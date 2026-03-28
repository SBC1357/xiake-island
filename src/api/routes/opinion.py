"""
Opinion API Router

实现观点生成相关 API 路由。
"""
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, HTTPException, Depends

from src.modules.opinion import (
    OpinionInput,
    OpinionOutput,
    EvidenceBundle,
    EvidenceItem,
    OpinionGenerator,
    OpinionGeneratorConfig,
    OpinionModuleError,
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
router = APIRouter(prefix="/v1/opinion", tags=["opinion"])


# 导入共享的 task logger
from src.api.app import get_shared_task_logger


# 请求/响应模型
class EvidenceItemRequest(BaseModel):
    """证据项请求"""
    model_config = ConfigDict(extra="forbid")
    
    id: str = Field(..., description="证据ID")
    content: str = Field(..., description="证据内容")
    source: Optional[str] = Field(default=None, description="证据来源")
    relevance: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="相关性")


class EvidenceBundleRequest(BaseModel):
    """证据包请求"""
    model_config = ConfigDict(extra="forbid")
    
    items: list[EvidenceItemRequest] = Field(default_factory=list, description="证据项列表")
    summary: Optional[str] = Field(default=None, description="证据摘要")


class OpinionGenerateRequest(BaseModel):
    """
    观点生成请求
    
    Attributes:
        evidence_bundle: 证据包
        audience: 目标受众
        thesis_hint: 观点提示 (可选)
        context_metadata: 上下文元数据 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    evidence_bundle: EvidenceBundleRequest = Field(..., description="证据包")
    audience: str = Field(..., min_length=1, description="目标受众")
    thesis_hint: Optional[str] = Field(default=None, description="观点提示")
    context_metadata: Optional[dict[str, Any]] = Field(default=None, description="上下文元数据")


class SupportPointResponse(BaseModel):
    """支撑点响应"""
    model_config = ConfigDict(extra="forbid")
    
    content: str = Field(..., description="支撑内容")
    strength: str = Field(..., description="支撑强度")
    evidence_id: Optional[str] = Field(default=None, description="关联证据ID")


class ThesisResponse(BaseModel):
    """论题响应"""
    model_config = ConfigDict(extra="forbid")
    
    statement: str = Field(..., description="观点陈述")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    evidence_refs: list[str] = Field(default_factory=list, description="证据引用列表")


class ConfidenceNotesResponse(BaseModel):
    """置信度说明响应"""
    model_config = ConfigDict(extra="forbid")
    
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="整体置信度")
    limitations: list[str] = Field(default_factory=list, description="局限性说明")
    assumptions: list[str] = Field(default_factory=list, description="假设条件")


class OpinionGenerateResponse(BaseModel):
    """
    观点生成响应
    
    Attributes:
        task_id: 任务ID
        thesis: 核心观点
        support_points: 支撑点列表
        confidence_notes: 置信度说明
    """
    model_config = ConfigDict(extra="forbid")
    
    task_id: str = Field(..., description="任务ID")
    thesis: ThesisResponse = Field(..., description="核心观点")
    support_points: list[SupportPointResponse] = Field(default_factory=list, description="支撑点列表")
    confidence_notes: Optional[ConfidenceNotesResponse] = Field(default=None, description="置信度说明")


# 依赖注入
async def get_opinion_generator():
    """获取 OpinionGenerator 实例"""
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
  "thesis": {
    "statement": "根据提供的证据，该治疗方案具有良好的疗效和安全性。",
    "confidence": 0.85,
    "evidence_refs": ["e1", "e2"]
  },
  "support_points": [
    {
      "content": "临床试验显示显著疗效",
      "strength": "strong",
      "evidence_id": "e1"
    },
    {
      "content": "安全性数据充分",
      "strength": "medium",
      "evidence_id": "e2"
    }
  ],
  "limitations": ["样本量有限", "随访时间较短"],
  "assumptions": ["患者依从性良好"]
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
    return OpinionGenerator(gateway)


async def get_task_logger():
    """获取应用级共享的 TaskLogger 实例"""
    return get_shared_task_logger()


@router.post("/generate", response_model=OpinionGenerateResponse)
async def generate_opinion(
    request: OpinionGenerateRequest,
    generator: OpinionGenerator = Depends(get_opinion_generator),
    logger: TaskLogger = Depends(get_task_logger)
):
    """
    生成医学观点
    
    根据提供的证据材料生成结构化的医学观点。
    
    Args:
        request: 观点生成请求
        
    Returns:
        观点生成响应
    """
    # 开始记录任务
    # 构建输入数据用于日志记录
    input_data = {
        "audience": request.audience,
        "thesis_hint": request.thesis_hint,
        "evidence_bundle": {
            "items": [
                {"id": item.id, "content": item.content, "source": item.source, "relevance": item.relevance}
                for item in request.evidence_bundle.items
            ],
            "summary": request.evidence_bundle.summary
        },
        "context_metadata": request.context_metadata
    }
    
    task_id = logger.start_task(
        module=ModuleName.OPINION,
        input_data=input_data,
        metadata={
            "audience": request.audience,
            "evidence_count": len(request.evidence_bundle.items)
        }
    )
    
    try:
        # 构建 OpinionInput
        evidence_items = [
            EvidenceItem(
                id=item.id,
                content=item.content,
                source=item.source,
                relevance=item.relevance
            )
            for item in request.evidence_bundle.items
        ]
        
        opinion_input = OpinionInput(
            evidence_bundle=EvidenceBundle(
                items=evidence_items,
                summary=request.evidence_bundle.summary
            ),
            audience=request.audience,
            thesis_hint=request.thesis_hint,
            context_metadata=request.context_metadata
        )
        
        # 生成观点
        output = generator.generate(opinion_input)
        
        # 构建输出数据用于日志记录
        output_data = {
            "thesis": {
                "statement": output.thesis.statement,
                "confidence": output.thesis.confidence,
                "evidence_refs": output.thesis.evidence_refs
            },
            "support_points": [
                {
                    "content": sp.content,
                    "strength": sp.strength,
                    "evidence_id": sp.evidence_id
                }
                for sp in output.support_points
            ],
            "confidence_notes": {
                "overall_confidence": output.confidence_notes.overall_confidence if output.confidence_notes else None,
                "limitations": output.confidence_notes.limitations if output.confidence_notes else [],
                "assumptions": output.confidence_notes.assumptions if output.confidence_notes else []
            } if output.confidence_notes else None
        }
        
        # 记录任务完成
        logger.complete_task(
            task_id=task_id,
            output_data=output_data,
            metadata={
                "confidence": output.thesis.confidence,
                "support_points_count": len(output.support_points)
            }
        )
        
        # 构建响应
        return OpinionGenerateResponse(
            task_id=task_id,
            thesis=ThesisResponse(
                statement=output.thesis.statement,
                confidence=output.thesis.confidence,
                evidence_refs=output.thesis.evidence_refs
            ),
            support_points=[
                SupportPointResponse(
                    content=sp.content,
                    strength=sp.strength,
                    evidence_id=sp.evidence_id
                )
                for sp in output.support_points
            ],
            confidence_notes=ConfidenceNotesResponse(
                overall_confidence=output.confidence_notes.overall_confidence,
                limitations=output.confidence_notes.limitations,
                assumptions=output.confidence_notes.assumptions
            ) if output.confidence_notes else None
        )
        
    except OpinionModuleError as e:
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