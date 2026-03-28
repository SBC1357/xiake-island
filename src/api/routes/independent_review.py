"""
Independent Review API Router

独立可触发的改稿审稿模块。
支持：
- 直接上传 DOCX 文档
- 直接粘贴文字
- 侠客岛默认规则审改
- 用户自定义规则审改

不依赖现有任务工作流的 taskId。
"""
from typing import Optional, Any, List
from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends

from src.modules.semantic_review import (
    SemanticReviewInput,
    SemanticReviewOutput,
    SemanticReviewer,
    SemanticReviewerConfig,
)
from src.adapters.llm_gateway import (
    LLMGateway,
    LLMGatewayConfig,
    create_llm_provider_from_env,
    create_llm_provider,
)
from src.rules import RuleEngine
from src.rules.families import (
    RegisterLevelsFamily,
    ExpressionBaseFamily,
    MedicalSyntaxRulesFamily,
    ThesisDerivationRulesFamily,
)
from src.rules.adapters import M5ComplianceAdapterFamily
from src.runtime_logging import TaskLogger
from src.contracts.base import ModuleName


router = APIRouter(prefix="/v1/review/independent", tags=["independent_review"])


# ==================== Request / Response Models ====================


class TextReviewRequest(BaseModel):
    """文本输入审改请求"""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    content: str = Field(..., min_length=10, description="待审改内容")
    audience: str = Field(default="医学专业人士", description="目标受众")
    rule_mode: str = Field(
        default="default",
        description="规则模式: 'default' (侠客岛默认规则) 或 'custom' (自定义规则)",
    )
    custom_rules: Optional[List[str]] = Field(
        default=None,
        description="自定义规则列表（仅 rule_mode='custom' 时生效）",
    )
    prototype_hint: Optional[str] = Field(default=None, description="原型提示")
    tone_register: Optional[str] = Field(
        default=None,
        alias="register",
        serialization_alias="register",
        description="语体要求",
    )

    @property
    def register(self) -> Optional[str]:
        return self.tone_register


class ReviewFinding(BaseModel):
    severity: str
    category: str
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


class ReviewRewriteTarget(BaseModel):
    original: str
    suggested: str
    reason: str
    priority: str = "medium"


class IndependentReviewResponse(BaseModel):
    """独立审改响应"""
    model_config = ConfigDict(extra="forbid")

    review_id: str = Field(..., description="审改 ID")
    input_mode: str = Field(..., description="输入模式: text / docx")
    rule_mode: str = Field(..., description="规则模式: default / custom")
    passed: bool = Field(..., description="是否通过审核")
    severity_summary: dict = Field(default_factory=dict)
    findings: List[ReviewFinding] = Field(default_factory=list)
    rewrite_targets: List[ReviewRewriteTarget] = Field(default_factory=list)
    rule_layer_output: Optional[dict] = Field(default=None, description="确定性规则层输出")
    model_review_output: Optional[dict] = Field(default=None, description="模型审校层输出")
    original_content: Optional[str] = Field(default=None, description="原始内容（截断）")
    debug_info: Optional[dict] = Field(default=None, description="调试信息")


# ==================== Dependencies ====================


from src.api.app import get_shared_task_logger


def _build_reviewer(rule_mode: str, custom_rules: Optional[List[str]] = None) -> SemanticReviewer:
    """构建审核器实例"""
    import os

    provider_name = os.environ.get("LLM_PROVIDER", "fake").lower()

    if provider_name == "openai":
        provider, gateway_config = create_llm_provider_from_env()
    else:
        fake_response = '{"passed":true,"severity_summary":{"low":0,"medium":0,"high":0,"critical":0},"findings":[],"rewrite_target":[],"prototype_alignment":{"score":90,"matched_rules":[],"unmatched_rules":[],"notes":"fake mode"}}'
        gateway_config = LLMGatewayConfig(provider_name="fake", model_name="fake-model")
        provider = create_llm_provider(gateway_config, fake_response_content=fake_response)

    gateway = LLMGateway(provider, gateway_config)

    # 构建规则引擎
    rule_engine = RuleEngine()
    if rule_mode == "default":
        rule_engine.register_family(RegisterLevelsFamily())
        rule_engine.register_family(ExpressionBaseFamily())
        rule_engine.register_family(MedicalSyntaxRulesFamily())
        rule_engine.register_family(ThesisDerivationRulesFamily())
        rule_engine.register_family(M5ComplianceAdapterFamily())
    elif rule_mode == "custom" and custom_rules:
        # 自定义规则：将用户规则文本转换为简单的包含检测规则
        from src.rules.models import Rule, RuleFamilyDefinition, RuleFamilyId, RuleSeverity
        from dataclasses import dataclass

        @dataclass
        class CustomRuleFamily(RuleFamilyDefinition):
            _rules: list

            def get_family_id(self):
                return RuleFamilyId("custom_user_rules")

            def get_rules(self):
                return self._rules

        custom_rule_objects = []
        for i, rule_text in enumerate(custom_rules):
            rule = Rule(
                rule_id=f"custom_{i+1}",
                family=RuleFamilyId.CUSTOM_USER_RULES,
                name=f"custom_rule_{i+1}",
                description=rule_text,
                severity=RuleSeverity.MEDIUM,
                checker=lambda content, rt=rule_text: rt.lower() in content.lower(),
                on_match=f"命中自定义规则: {rule_text}",
                on_fail=f"未命中自定义规则: {rule_text}",
                suggestion=f"请检查是否符合: {rule_text}",
            )
            custom_rule_objects.append(rule)

        if custom_rule_objects:
            rule_engine.register_family(CustomRuleFamily(_rules=custom_rule_objects))

    config = SemanticReviewerConfig(
        require_prototype_alignment=True,
        require_rewrite_targets=True,
    )

    return SemanticReviewer(gateway, config, rule_engine=rule_engine)


# ==================== Endpoints ====================


@router.post("/text", response_model=IndependentReviewResponse)
async def review_text(
    request: TextReviewRequest,
    logger: TaskLogger = Depends(get_shared_task_logger),
):
    """
    独立文本审改

    不依赖 taskId，直接输入文本进行审改。
    支持默认规则和自定义规则两种模式。
    """
    import uuid

    review_id = f"review_{uuid.uuid4().hex[:12]}"

    reviewer = _build_reviewer(request.rule_mode, request.custom_rules)

    # 记录任务
    task_id = logger.start_task(
        module=ModuleName.SEMANTIC_REVIEW,
        input_data={"content": request.content[:200], "mode": "independent_text"},
        metadata={"review_id": review_id, "rule_mode": request.rule_mode},
    )

    try:
        review_input = SemanticReviewInput(
            content=request.content,
            audience=request.audience,
            prototype_hint=request.prototype_hint,
            register=request.register,
        )

        output = reviewer.review(review_input)

        findings = [
            ReviewFinding(
                severity=f.severity,
                category=f.category,
                description=f.description,
                location=f.location,
                suggestion=f.suggestion,
            )
            for f in output.findings
        ]

        rewrite_targets = [
            ReviewRewriteTarget(
                original=rt.original,
                suggested=rt.suggested,
                reason=rt.reason,
                priority=rt.priority,
            )
            for rt in output.rewrite_target
        ]

        logger.complete_task(
            task_id=task_id,
            output_data={"passed": output.passed, "findings_count": len(findings)},
        )

        return IndependentReviewResponse(
            review_id=review_id,
            input_mode="text",
            rule_mode=request.rule_mode,
            passed=output.passed,
            severity_summary={
                "low": output.severity_summary.low,
                "medium": output.severity_summary.medium,
                "high": output.severity_summary.high,
                "critical": output.severity_summary.critical,
            },
            findings=findings,
            rewrite_targets=rewrite_targets,
            rule_layer_output=output.rule_layer_output,
            model_review_output=output.model_review_output,
            original_content=request.content[:1000],
            debug_info={
                "provider": reviewer.gateway.provider.name,
                "model": reviewer.gateway.config.model_name,
            },
        )

    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"审改失败: {e}")


@router.post("/docx", response_model=IndependentReviewResponse)
async def review_docx(
    file: UploadFile = File(...),
    audience: str = Form("医学专业人士"),
    rule_mode: str = Form("default"),
    custom_rules: Optional[str] = Form(None),
    prototype_hint: Optional[str] = Form(None),
    tone_register: Optional[str] = Form(None, alias="register"),
    logger: TaskLogger = Depends(get_shared_task_logger),
):
    """
    独立 DOCX 审改

    上传 DOCX 文件进行审改，不依赖 taskId。
    """
    import uuid

    # 验证文件格式
    if not file.filename or not file.filename.lower().endswith((".docx", ".doc")):
        raise HTTPException(status_code=400, detail="仅支持 .docx / .doc 文件")

    review_id = f"review_{uuid.uuid4().hex[:12]}"

    # 读取 DOCX 内容
    file_data = await file.read()
    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="上传文件为空")

    try:
        from docx import Document
        import io

        doc = Document(io.BytesIO(file_data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        content = "\n\n".join(paragraphs)

        if len(content.strip()) < 10:
            raise HTTPException(status_code=400, detail="DOCX 内容过短，至少需要10个字符")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOCX 解析失败: {e}")

    # 解析自定义规则
    parsed_custom_rules = None
    if custom_rules:
        parsed_custom_rules = [r.strip() for r in custom_rules.split(",") if r.strip()]

    reviewer = _build_reviewer(rule_mode, parsed_custom_rules)

    task_id = logger.start_task(
        module=ModuleName.SEMANTIC_REVIEW,
        input_data={"filename": file.filename, "mode": "independent_docx"},
        metadata={"review_id": review_id, "rule_mode": rule_mode},
    )

    try:
        review_input = SemanticReviewInput(
            content=content,
            audience=audience,
            prototype_hint=prototype_hint,
            register=tone_register,
        )

        output = reviewer.review(review_input)

        findings = [
            ReviewFinding(
                severity=f.severity,
                category=f.category,
                description=f.description,
                location=f.location,
                suggestion=f.suggestion,
            )
            for f in output.findings
        ]

        rewrite_targets = [
            ReviewRewriteTarget(
                original=rt.original,
                suggested=rt.suggested,
                reason=rt.reason,
                priority=rt.priority,
            )
            for rt in output.rewrite_target
        ]

        logger.complete_task(
            task_id=task_id,
            output_data={"passed": output.passed, "findings_count": len(findings)},
        )

        return IndependentReviewResponse(
            review_id=review_id,
            input_mode="docx",
            rule_mode=rule_mode,
            passed=output.passed,
            severity_summary={
                "low": output.severity_summary.low,
                "medium": output.severity_summary.medium,
                "high": output.severity_summary.high,
                "critical": output.severity_summary.critical,
            },
            findings=findings,
            rewrite_targets=rewrite_targets,
            rule_layer_output=output.rule_layer_output,
            model_review_output=output.model_review_output,
            original_content=content[:1000],
            debug_info={
                "provider": reviewer.gateway.provider.name,
                "model": reviewer.gateway.config.model_name,
                "source_file": file.filename,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"审改失败: {e}")
