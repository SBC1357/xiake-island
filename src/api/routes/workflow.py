"""
Workflow API Router

实现工作流编排相关 API 路由。
"""

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, HTTPException, Depends

from src.orchestrator import OrchestratorService, WorkflowTask
from src.orchestrator.errors import (
    OrchestratorError,
    UnsupportedWorkflowError,
    WorkflowExecutionError,
)
from src.runtime_logging import TaskLogger
from src.contracts.base import TaskStatus
from src.assembly import get_asset_bridge
from src.adapters.asset_bridge import AssetKind


# 创建 Router
router = APIRouter(prefix="/v1/workflow", tags=["workflow"])


# 导入共享的 task logger
from src.api.app import get_shared_task_logger


# 请求/响应模型
class ArticleWorkflowOpinionInput(BaseModel):
    """文章工作流 - Opinion 输入"""

    model_config = ConfigDict(extra="forbid")

    evidence_bundle: dict[str, Any] = Field(
        ..., description="证据包 (包含 items 和可选 summary)"
    )
    audience: str = Field(default="医学专业人士", description="目标受众")
    thesis_hint: Optional[str] = Field(default=None, description="观点提示")
    context_metadata: Optional[dict[str, Any]] = Field(
        default=None, description="上下文元数据"
    )


class ArticleWorkflowReviewInput(BaseModel):
    """文章工作流 - Semantic Review 输入"""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    audience: str = Field(default="医学专业人士", description="目标受众")
    prototype_hint: Optional[str] = Field(default=None, description="原型提示")
    tone_register: Optional[str] = Field(
        default=None,
        alias="register",
        serialization_alias="register",
        description="语体要求",
    )
    context_metadata: Optional[dict[str, Any]] = Field(
        default=None, description="上下文元数据"
    )

    @property
    def register(self) -> Optional[str]:
        return self.tone_register


class ArticleWorkflowInputData(BaseModel):
    """
    文章工作流输入数据

    包含 opinion 和 semantic_review 子字段的类型化结构。

    Attributes:
        opinion: Opinion 模块输入
        semantic_review: Semantic Review 模块输入
    """

    model_config = ConfigDict(extra="forbid")

    opinion: ArticleWorkflowOpinionInput = Field(..., description="Opinion 模块输入")
    semantic_review: ArticleWorkflowReviewInput = Field(
        default_factory=ArticleWorkflowReviewInput,
        description="Semantic Review 模块输入",
    )


class ArticleWorkflowRequest(BaseModel):
    """
    文章工作流请求

    Attributes:
        input_data: 包含 opinion 和 semantic_review 输入 (类型化验证)
        metadata: 工作流元数据 (可选)
    """

    model_config = ConfigDict(extra="forbid")

    input_data: ArticleWorkflowInputData = Field(
        ..., description="工作流输入数据 (包含 opinion 和 semantic_review 子字段)"
    )
    metadata: Optional[dict[str, Any]] = Field(default=None, description="工作流元数据")


class ChildTaskResultResponse(BaseModel):
    """子任务结果响应"""

    model_config = ConfigDict(extra="forbid")

    module_name: str = Field(..., description="模块名称")
    task_id: str = Field(..., description="子任务ID")
    status: str = Field(..., description="执行状态")
    result: Optional[dict[str, Any]] = Field(default=None, description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")


class PrototypeAlignmentResponse(BaseModel):
    """原型对齐情况响应"""

    model_config = ConfigDict(extra="forbid")

    score: int = Field(..., ge=0, le=100, description="对齐分数 (0-100)")
    matched_rules: list[str] = Field(default_factory=list, description="匹配的规则列表")
    unmatched_rules: list[str] = Field(
        default_factory=list, description="未匹配的规则列表"
    )
    notes: Optional[str] = Field(default=None, description="对齐说明")


class ArticleWorkflowResponse(BaseModel):
    """
    文章工作流响应

    SP-6 Batch 6C: 新增三层输出字段和重跑范围。

    Attributes:
        task_id: 父任务ID
        child_task_ids: 子任务ID列表
        status: 执行状态
        result: 工作流结果
        child_results: 子任务结果列表
        prototype_alignment: 原型对齐情况 (从 semantic_review 输出提取)
        rule_layer_output: 规则层输出（确定性规则执行结果）
        model_review_output: 模型审校层输出（LLM 审核结果）
        rewrite_layer_output: 改写建议层输出
        rerun_scope: 重跑范围分类 (full_gate_rerun / partial_gate_rerun)
        errors: 错误列表
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(..., description="父任务ID")
    child_task_ids: list[str] = Field(default_factory=list, description="子任务ID列表")
    status: str = Field(..., description="执行状态")
    result: Optional[dict[str, Any]] = Field(default=None, description="工作流结果")
    child_results: list[ChildTaskResultResponse] = Field(
        default_factory=list, description="子任务结果列表"
    )
    prototype_alignment: Optional[PrototypeAlignmentResponse] = Field(
        default=None, description="原型对齐情况"
    )
    # SP-6 Batch 6C: 三层输出和重跑范围
    rule_layer_output: Optional[dict[str, Any]] = Field(
        default=None, description="规则层输出（确定性规则执行结果）"
    )
    model_review_output: Optional[dict[str, Any]] = Field(
        default=None, description="模型审校层输出（LLM 审核结果）"
    )
    rewrite_layer_output: Optional[dict[str, Any]] = Field(
        default=None, description="改写建议层输出"
    )
    rerun_scope: Optional[str] = Field(
        default=None, description="重跑范围分类 (full_gate_rerun / partial_gate_rerun)"
    )
    errors: list[str] = Field(default_factory=list, description="错误列表")


# ==================== Standard Chain Workflow API ====================


class StandardChainWorkflowRequest(BaseModel):
    """
    标准六段链工作流请求

    SP-7C: 执行 Evidence -> Planning -> Writing -> Drafting -> Quality -> Delivery 全链路。

    Attributes:
        product_id: 产品ID (必需)
        domain: 领域过滤 (可选，如 efficacy, safety)
        register: 语体要求 (可选，默认 R2)
        audience: 目标受众 (可选，默认 医学专业人士)
        project_name: 项目名称 (可选)
        metadata: 工作流元数据 (可选)
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    product_id: str = Field(..., description="产品ID")
    domain: Optional[str] = Field(
        default=None, description="领域过滤 (如 efficacy, safety)"
    )
    tone_register: Optional[str] = Field(
        default="R2",
        alias="register",
        serialization_alias="register",
        description="语体要求",
    )
    audience: Optional[str] = Field(default="医学专业人士", description="目标受众")
    project_name: Optional[str] = Field(default=None, description="项目名称")
    target_word_count: Optional[int] = Field(default=None, ge=1, description="目标字数（前置约束，最小为1）")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="工作流元数据")

    @property
    def register(self) -> Optional[str]:
        return self.tone_register


class StandardChainWorkflowResponse(BaseModel):
    """
    标准六段链工作流响应

    SP-7C: 六段链，Drafting 在 Writing 和 Quality 之间。

    Attributes:
        task_id: 父任务ID
        child_task_ids: 子任务ID列表 (6个子任务)
        status: 执行状态
        result: 各阶段结果汇总
        child_results: 各阶段子任务结果
        errors: 错误列表
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(..., description="父任务ID")
    child_task_ids: list[str] = Field(
        default_factory=list,
        description="子任务ID列表 (Evidence, Planning, Writing, Drafting, Quality, Delivery)",
    )
    status: str = Field(..., description="执行状态")
    result: Optional[dict[str, Any]] = Field(default=None, description="各阶段结果汇总")
    child_results: list[ChildTaskResultResponse] = Field(
        default_factory=list, description="各阶段子任务结果"
    )
    errors: list[str] = Field(default_factory=list, description="错误列表")


# 依赖注入
async def get_orchestrator_service(
    logger: TaskLogger = Depends(get_shared_task_logger),
):
    """获取 OrchestratorService 实例"""
    return OrchestratorService(task_logger=logger)


@router.post("/article", response_model=ArticleWorkflowResponse)
async def execute_article_workflow(
    request: ArticleWorkflowRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    """
    执行文章工作流

    执行 opinion -> semantic_review 工作流链路。

    Args:
        request: 文章工作流请求

    Returns:
        文章工作流响应，包含 task_id、child_task_ids、结果和原型对齐信息

    Raises:
        HTTPException 422: 参数校验失败
        HTTPException 400: 不支持的工作流
        HTTPException 500: 工作流执行失败
    """
    # 构建 WorkflowTask - 将类型化输入转换为 dict
    try:
        # 转换类型化输入为 dict，保持 Orchestrator 接口兼容
        input_data_dict = {
            "opinion": request.input_data.opinion.model_dump(),
            "semantic_review": request.input_data.semantic_review.model_dump(),
        }

        workflow_task = WorkflowTask(
            workflow_name="article",
            input_data=input_data_dict,
            metadata=request.metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"参数校验失败: {str(e)}")

    try:
        # 执行工作流
        result = orchestrator.execute(workflow_task)

        # 从 result 的顶层提取 prototype_alignment（Orchestrator 现在会包含它）
        prototype_alignment = None
        if result.result and "prototype_alignment" in result.result:
            pa_data = result.result["prototype_alignment"]
            if pa_data:
                prototype_alignment = PrototypeAlignmentResponse(
                    score=pa_data.get("score", 0),
                    matched_rules=pa_data.get("matched_rules", []),
                    unmatched_rules=pa_data.get("unmatched_rules", []),
                    notes=pa_data.get("notes"),
                )

        # SP-6 Batch 6C: 提取三层输出和重跑范围
        rule_layer_output = (
            result.result.get("rule_layer_output") if result.result else None
        )
        model_review_output = (
            result.result.get("model_review_output") if result.result else None
        )
        rewrite_layer_output = (
            result.result.get("rewrite_layer_output") if result.result else None
        )
        rerun_scope = result.result.get("rerun_scope") if result.result else None

        # 构建响应
        return ArticleWorkflowResponse(
            task_id=result.task_id,
            child_task_ids=result.child_task_ids,
            status=result.status.value,
            result=result.result,
            child_results=[
                ChildTaskResultResponse(
                    module_name=cr.module_name,
                    task_id=cr.task_id,
                    status=cr.status.value,
                    result=cr.result,
                    error=cr.error,
                )
                for cr in result.child_results
            ],
            prototype_alignment=prototype_alignment,
            # SP-6 Batch 6C: 三层输出和重跑范围
            rule_layer_output=rule_layer_output,
            model_review_output=model_review_output,
            rewrite_layer_output=rewrite_layer_output,
            rerun_scope=rerun_scope,
            errors=result.errors,
        )

    except UnsupportedWorkflowError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except WorkflowExecutionError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except OrchestratorError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工作流执行失败: {str(e)}")


@router.post("/standard-chain", response_model=StandardChainWorkflowResponse)
async def execute_standard_chain_workflow(
    request: StandardChainWorkflowRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    """
    执行标准六段链工作流

    SP-7C: 执行 Evidence -> Planning -> Writing -> Drafting -> Quality -> Delivery 完整链路。
    Drafting 生成正文，Quality 审查正文而非 prompts，Delivery 接收正文内容。

    Args:
        request: 标准六段链工作流请求

    Returns:
        标准六段链工作流响应，包含 task_id、child_task_ids、各阶段结果

    Raises:
        HTTPException 422: 参数校验失败
        HTTPException 400: 不支持的工作流
        HTTPException 500: 工作流执行失败（包括质量门禁检查失败）
    """
    # 构建 WorkflowTask
    try:
        input_data_dict = {
            "product_id": request.product_id,
            "domain": request.domain,
            "register": request.register,
            "audience": request.audience,
            "project_name": request.project_name,
            "target_word_count": request.target_word_count,
        }

        workflow_task = WorkflowTask(
            workflow_name="standard_chain",
            input_data=input_data_dict,
            metadata=request.metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"参数校验失败: {str(e)}")

    try:
        # 执行工作流
        result = orchestrator.execute(workflow_task)

        # 构建响应
        return StandardChainWorkflowResponse(
            task_id=result.task_id,
            child_task_ids=result.child_task_ids,
            status=result.status.value,
            result=result.result,
            child_results=[
                ChildTaskResultResponse(
                    module_name=cr.module_name,
                    task_id=cr.task_id,
                    status=cr.status.value,
                    result=cr.result,
                    error=cr.error,
                )
                for cr in result.child_results
            ],
            errors=result.errors,
        )

    except UnsupportedWorkflowError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except WorkflowExecutionError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except OrchestratorError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"标准六段链执行失败: {str(e)}")


# ==================== Knowledge Assets API ====================


class KnowledgeAssetsResponse(BaseModel):
    """知识资产响应"""

    model_config = ConfigDict(extra="forbid")

    consumer_assets_count: int = Field(..., description="消费者资产数量")
    rules_assets_count: int = Field(..., description="规则资产数量")
    consumer_root: Optional[str] = Field(default=None, description="消费者根路径")
    has_l2: bool = Field(default=False, description="是否存在 L2 层资产")
    l2_files: list[str] = Field(default_factory=list, description="L2 文件列表")


@router.get("/knowledge-assets", response_model=KnowledgeAssetsResponse)
async def get_knowledge_assets():
    """
    获取知识资产状态

    证明 asset_bridge 被真实请求链使用，且依赖 publish/current/consumers/xiakedao。

    Returns:
        知识资产统计信息，包括 L2 层存在性验证
    """
    try:
        bridge = get_asset_bridge()

        # 获取消费者资产 - 证明依赖 publish/current/consumers/xiakedao
        consumer_assets = []
        rules_assets = []

        try:
            consumer_assets = bridge.list_assets(AssetKind.CONSUMER)
        except Exception:
            pass  # consumer 未配置时返回空列表

        try:
            rules_assets = bridge.list_assets(AssetKind.RULES)
        except Exception:
            pass  # rules 未配置时返回空列表

        # 检查 L2 层资产
        has_l2 = False
        l2_files = []

        if bridge.config.consumer_root:
            from pathlib import Path

            l2_path = bridge.config.consumer_root / "l2"
            if l2_path.exists():
                has_l2 = True
                l2_files = [f.name for f in l2_path.rglob("*.json")][
                    :10
                ]  # 最多返回10个文件名

        return KnowledgeAssetsResponse(
            consumer_assets_count=len(consumer_assets),
            rules_assets_count=len(rules_assets),
            consumer_root=str(bridge.config.consumer_root)
            if bridge.config.consumer_root
            else None,
            has_l2=has_l2,
            l2_files=l2_files,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识资产失败: {str(e)}")
