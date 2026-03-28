"""
Semantic Review API Router

实现中文语义审核相关 API 路由。
"""
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, HTTPException, Depends

from src.modules.semantic_review import (
    SemanticReviewInput,
    SemanticReviewOutput,
    SemanticReviewer,
    SemanticReviewerConfig,
    SemanticReviewError,
    ContentTooShortError,
    ReviewGenerationError,
)
from src.adapters.llm_gateway import (
    LLMGateway,
    LLMGatewayConfig,
    FakeLLMProvider,
    create_llm_provider_from_env,
    create_llm_provider,
)
from src.runtime_logging import TaskLogger
from src.contracts.base import ModuleName


# 创建 Router
router = APIRouter(prefix="/v1/review", tags=["semantic_review"])


# 请求/响应模型
class SemanticReviewRequest(BaseModel):
    """
    语义审核请求
    
    Attributes:
        content: 待审核内容
        audience: 目标受众
        prototype_hint: 原型提示 (可选)
        register: 语体要求 (可选)
        context_metadata: 上下文元数据 (可选)
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    content: str = Field(..., min_length=1, description="待审核内容")
    audience: str = Field(..., min_length=1, description="目标受众")
    prototype_hint: Optional[str] = Field(default=None, description="原型提示")
    tone_register: Optional[str] = Field(
        default=None,
        alias="register",
        serialization_alias="register",
        description="语体要求",
    )
    context_metadata: Optional[dict[str, Any]] = Field(default=None, description="上下文元数据")

    @property
    def register(self) -> Optional[str]:
        return self.tone_register


class SeveritySummaryResponse(BaseModel):
    """严重性摘要响应"""
    model_config = ConfigDict(extra="forbid")
    
    low: int = Field(default=0, description="低严重性问题数量")
    medium: int = Field(default=0, description="中严重性问题数量")
    high: int = Field(default=0, description="高严重性问题数量")
    critical: int = Field(default=0, description="严重问题数量")


class FindingResponse(BaseModel):
    """审核发现项响应"""
    model_config = ConfigDict(extra="forbid")
    
    severity: str = Field(..., description="严重级别")
    category: str = Field(..., description="问题类别")
    description: str = Field(..., description="问题描述")
    location: Optional[str] = Field(default=None, description="问题位置")
    suggestion: Optional[str] = Field(default=None, description="修改建议")


class RewriteTargetResponse(BaseModel):
    """改写目标响应"""
    model_config = ConfigDict(extra="forbid")
    
    original: str = Field(..., description="原始内容")
    suggested: str = Field(..., description="建议改写内容")
    reason: str = Field(..., description="改写原因")
    priority: str = Field(default="medium", description="改写优先级")


class PrototypeAlignmentResponse(BaseModel):
    """原型对齐情况响应"""
    model_config = ConfigDict(extra="forbid")
    
    score: int = Field(..., ge=0, le=100, description="对齐分数 (0-100)")
    matched_rules: list[str] = Field(default_factory=list, description="匹配的规则列表")
    unmatched_rules: list[str] = Field(default_factory=list, description="未匹配的规则列表")
    notes: Optional[str] = Field(default=None, description="对齐说明")


class SemanticReviewResponse(BaseModel):
    """
    语义审核响应
    
    SP-6 Batch 6C: 新增三层输出字段和重跑范围。
    
    Attributes:
        task_id: 任务ID
        passed: 是否通过审核
        severity_summary: 严重性摘要
        findings: 审核发现的问题列表
        rewrite_target: 改写目标列表
        prototype_alignment: 原型对齐情况
        rule_layer_output: 规则层输出（确定性规则执行结果）
        model_review_output: 模型审校层输出（LLM 审核结果）
        rewrite_layer_output: 改写建议层输出
        rerun_scope: 重跑范围分类 (full_gate_rerun / partial_gate_rerun)
    """
    model_config = ConfigDict(extra="forbid")
    
    task_id: str = Field(..., description="任务ID")
    passed: bool = Field(..., description="是否通过审核")
    severity_summary: SeveritySummaryResponse = Field(..., description="严重性摘要")
    findings: list[FindingResponse] = Field(default_factory=list, description="审核发现的问题列表")
    rewrite_target: list[RewriteTargetResponse] = Field(default_factory=list, description="改写目标列表")
    prototype_alignment: Optional[PrototypeAlignmentResponse] = Field(default=None, description="原型对齐情况")
    # SP-6 Batch 6C: 三层输出和重跑范围
    rule_layer_output: Optional[dict[str, Any]] = Field(default=None, description="规则层输出（确定性规则执行结果）")
    model_review_output: Optional[dict[str, Any]] = Field(default=None, description="模型审校层输出（LLM 审核结果）")
    rewrite_layer_output: Optional[dict[str, Any]] = Field(default=None, description="改写建议层输出")
    rerun_scope: Optional[str] = Field(default=None, description="重跑范围分类 (full_gate_rerun / partial_gate_rerun)")


# 依赖注入
async def get_semantic_reviewer():
    """获取 SemanticReviewer 实例"""
    import os
    
    # 从环境变量读取 provider 类型
    provider_name = os.environ.get("LLM_PROVIDER", "fake").lower()
    model_name = os.environ.get("LLM_MODEL", "fake-model")
    
    if provider_name == "openai":
        # 使用真实 OpenAI provider
        # 验证模型名称不是默认值
        if model_name == "fake-model":
            raise ValueError(
                "LLM_MODEL must be set to a valid OpenAI model name "
                "(e.g., 'gpt-3.5-turbo', 'gpt-4') when using OpenAI provider. "
                "Current value is the default 'fake-model'."
            )
        provider, gateway_config = create_llm_provider_from_env()
    elif provider_name == "fake":
        # 使用 fake provider，返回有效的 JSON 响应
        fake_response = """{
  "passed": true,
  "severity_summary": {
    "low": 1,
    "medium": 0,
    "high": 0,
    "critical": 0
  },
  "findings": [
    {
      "severity": "low",
      "category": "标点",
      "description": "标点符号使用建议优化",
      "suggestion": "使用更规范的标点"
    }
  ],
  "rewrite_target": [],
  "prototype_alignment": {
    "score": 85,
    "matched_rules": ["通俗易懂"],
    "unmatched_rules": [],
    "notes": "整体符合要求"
  }
}"""
        
        gateway_config = LLMGatewayConfig(
            provider_name="fake",
            model_name=model_name
        )
        provider = create_llm_provider(
            gateway_config,
            fake_response_content=fake_response
        )
    else:
        # 未知的 provider，快速失败
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider_name}'. "
            f"Supported values: 'fake', 'openai'."
        )
    
    gateway = LLMGateway(provider, gateway_config)
    config = SemanticReviewerConfig(require_prototype_alignment=True)
    return SemanticReviewer(gateway, config)


# 导入共享的 task logger
from src.api.app import get_shared_task_logger


@router.post("/semantic", response_model=SemanticReviewResponse)
async def review_semantic(
    request: SemanticReviewRequest,
    reviewer: SemanticReviewer = Depends(get_semantic_reviewer),
    logger: TaskLogger = Depends(get_shared_task_logger)
):
    """
    执行中文语义审核
    
    对提供的中文内容进行语义审核，识别语法错误、表达不当、逻辑问题等。
    
    Args:
        request: 语义审核请求
        
    Returns:
        语义审核响应
    """
    # 开始记录任务
    # 构建输入数据用于日志记录
    input_data = {
        "content": request.content,
        "audience": request.audience,
        "prototype_hint": request.prototype_hint,
        "register": request.register,
        "context_metadata": request.context_metadata
    }
    
    task_id = logger.start_task(
        module=ModuleName.SEMANTIC_REVIEW,
        input_data=input_data,
        metadata={
            "audience": request.audience,
            "content_length": len(request.content)
        }
    )
    
    try:
        # 构建 SemanticReviewInput
        review_input = SemanticReviewInput(
            content=request.content,
            audience=request.audience,
            prototype_hint=request.prototype_hint,
            register=request.register,
            context_metadata=request.context_metadata
        )
        
        # 执行审核
        output = reviewer.review(review_input)
        
        # 构建输出数据用于日志记录
        output_data = {
            "passed": output.passed,
            "severity_summary": {
                "low": output.severity_summary.low,
                "medium": output.severity_summary.medium,
                "high": output.severity_summary.high,
                "critical": output.severity_summary.critical
            },
            "findings": [
                {
                    "severity": f.severity,
                    "category": f.category,
                    "description": f.description,
                    "location": f.location,
                    "suggestion": f.suggestion
                }
                for f in output.findings
            ],
            "rewrite_target": [
                {
                    "original": rt.original,
                    "suggested": rt.suggested,
                    "reason": rt.reason,
                    "priority": rt.priority
                }
                for rt in output.rewrite_target
            ],
            "prototype_alignment": {
                "score": output.prototype_alignment.score,
                "matched_rules": output.prototype_alignment.matched_rules,
                "unmatched_rules": output.prototype_alignment.unmatched_rules,
                "notes": output.prototype_alignment.notes
            } if output.prototype_alignment else None,
            # SP-6 Batch 6C: 三层输出和重跑范围
            "rule_layer_output": output.rule_layer_output,
            "model_review_output": output.model_review_output,
            "rewrite_layer_output": output.rewrite_layer_output,
            "rerun_scope": output.rerun_scope
        }
        
        # 记录任务完成
        logger.complete_task(
            task_id=task_id,
            output_data=output_data,
            metadata={
                "passed": output.passed,
                "findings_count": len(output.findings)
            }
        )
        
        # 构建响应
        return SemanticReviewResponse(
            task_id=task_id,
            passed=output.passed,
            severity_summary=SeveritySummaryResponse(
                low=output.severity_summary.low,
                medium=output.severity_summary.medium,
                high=output.severity_summary.high,
                critical=output.severity_summary.critical
            ),
            findings=[
                FindingResponse(
                    severity=f.severity,
                    category=f.category,
                    description=f.description,
                    location=f.location,
                    suggestion=f.suggestion
                )
                for f in output.findings
            ],
            rewrite_target=[
                RewriteTargetResponse(
                    original=rt.original,
                    suggested=rt.suggested,
                    reason=rt.reason,
                    priority=rt.priority
                )
                for rt in output.rewrite_target
            ],
            prototype_alignment=PrototypeAlignmentResponse(
                score=output.prototype_alignment.score,
                matched_rules=output.prototype_alignment.matched_rules,
                unmatched_rules=output.prototype_alignment.unmatched_rules,
                notes=output.prototype_alignment.notes
            ) if output.prototype_alignment else None,
            # SP-6 Batch 6C: 三层输出和重跑范围
            rule_layer_output=output.rule_layer_output,
            model_review_output=output.model_review_output,
            rewrite_layer_output=output.rewrite_layer_output,
            rerun_scope=output.rerun_scope
        )
        
    except (SemanticReviewError, ContentTooShortError) as e:
        # 记录任务失败
        logger.fail_task(
            task_id=task_id,
            error_message=e.message
        )
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        # 记录任务失败
        logger.fail_task(
            task_id=task_id,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))
