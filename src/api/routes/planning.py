"""
Planning API Routes

规划生成 API 端点。
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.modules.planning.service import PlanningService
from src.modules.planning.models import (
    RouteContext,
    EditorialPlan,
    RouteContextRequest,
    EditorialPlanResponse,
    OutlineItemResponse,
    PersonaProfileResponse
)
from src.runtime_logging import TaskLogger
from src.contracts.base import ModuleName
from src.api.app import get_shared_task_logger


router = APIRouter(prefix="/v1/planning", tags=["planning"])


# ==================== Request/Response Models ====================

class PlanningRequest(BaseModel):
    """规划请求"""
    context: RouteContextRequest = Field(..., description="路由上下文")
    evidence_facts: Optional[List[Dict[str, Any]]] = Field(None, description="证据事实列表")
    selected_facts: Optional[List[str]] = Field(None, description="选中的证据ID列表")


class PlanningPlanResponse(BaseModel):
    """规划响应（包含 task_id）"""
    task_id: str = Field(..., description="任务ID")
    thesis: Optional[str] = Field(None, description="核心论点")
    outline: List[OutlineItemResponse] = Field(default_factory=list, description="文章大纲")
    play_id: Optional[str] = Field(None, description="写作策略ID")
    arc_id: Optional[str] = Field(None, description="叙事弧线ID")
    target_audience: Optional[str] = Field(None, description="目标受众")
    key_evidence: Optional[List[str]] = Field(None, description="核心证据")
    style_notes: Optional[Dict[str, Any]] = Field(None, description="风格注释")


class PersonaRequest(BaseModel):
    """人格画像请求"""
    profile_id: str = Field(..., description="画像ID")


# ==================== Service Instance ====================

_planning_service: Optional[PlanningService] = None


def get_planning_service() -> PlanningService:
    """获取 PlanningService 实例"""
    global _planning_service
    if _planning_service is None:
        _planning_service = PlanningService()
    return _planning_service


async def get_task_logger():
    """获取应用级共享的 TaskLogger 实例"""
    return get_shared_task_logger()


# ==================== Endpoints ====================

@router.post("/plan", response_model=PlanningPlanResponse)
async def generate_plan(
    request: PlanningRequest,
    logger: TaskLogger = Depends(get_task_logger)
):
    """
    生成编辑计划
    
    基于路由上下文和可选的证据事实生成编辑计划。
    
    Args:
        request: 规划请求
        
    Returns:
        EditorialPlan: 编辑计划
    """
    service = get_planning_service()
    
    # 开始记录任务
    input_data = {
        "product_id": request.context.product_id,
        "register": request.context.register,
        "audience": request.context.audience,
        "evidence_facts_count": len(request.evidence_facts) if request.evidence_facts else 0
    }
    
    task_id = logger.start_task(
        module=ModuleName.PLANNING,
        input_data=input_data,
        metadata={"context": request.context.model_dump(by_alias=True)}
    )
    
    try:
        # 构建 RouteContext
        context = RouteContext(
            product_id=request.context.product_id,
            register=request.context.register,
            audience=request.context.audience,
            project_name=request.context.project_name,
            deliverable_type=request.context.deliverable_type,
            metadata=request.context.metadata
        )
        
        # 生成计划
        plan = service.plan(
            context=context,
            evidence_facts=request.evidence_facts,
            selected_facts=request.selected_facts
        )
        
        # 转换为响应格式
        outline_response = [
            OutlineItemResponse(
                title=item.get("title", ""),
                type=item.get("type", ""),
                domain=item.get("domain"),
                fact_count=item.get("fact_count"),
                fact_id=item.get("fact_id")
            )
            for item in plan.outline
        ]
        
        # 完成任务记录
        logger.complete_task(
            task_id=task_id,
            output_data={
                "thesis": plan.thesis[:50] if plan.thesis else "",
                "outline_items": len(plan.outline)
            }
        )
        
        return PlanningPlanResponse(
            task_id=task_id,
            thesis=plan.thesis,
            outline=outline_response,
            play_id=plan.play_id,
            arc_id=plan.arc_id,
            target_audience=plan.target_audience,
            key_evidence=plan.key_evidence,
            style_notes=plan.style_notes
        )
        
    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"规划生成失败: {str(e)}")


@router.post("/persona", response_model=Optional[PersonaProfileResponse])
async def get_persona(request: PersonaRequest):
    """
    获取人格画像
    
    Args:
        request: 人格画像请求
        
    Returns:
        PersonaProfile 或 None
    """
    service = get_planning_service()
    
    persona = service.get_persona(request.profile_id)
    
    if persona is None:
        return None
    
    return PersonaProfileResponse(
        profile_id=persona.profile_id,
        author_id=persona.author_id,
        author_name=persona.author_name,
        domain=persona.domain,
        tone=persona.tone,
        voice_styles=[vs.value for vs in persona.voice_styles] if persona.voice_styles else [],
        signature_phrases=persona.signature_phrases
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "planning"}
