"""
Quality API Routes

质量审校 API 端点。
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.modules.quality.orchestrator import QualityOrchestrator
from src.modules.quality.models import QualityResult, GateStatus
from src.runtime_logging import TaskLogger
from src.contracts.base import ModuleName
from src.api.app import get_shared_task_logger


router = APIRouter(prefix="/v1/quality", tags=["quality"])


# ==================== Request/Response Models ====================

class QualityReviewRequest(BaseModel):
    """质量审核请求"""
    content: str = Field(..., description="待审核内容")
    enabled_gates: Optional[List[str]] = Field(None, description="启用的门禁列表")


class QualityResultResponse(BaseModel):
    """质量审核结果响应（包含 task_id）"""
    task_id: str = Field(..., description="任务ID")
    overall_status: str
    gates_passed: List[str] = Field(default_factory=list)
    warnings: List[Dict[str, str]] = Field(default_factory=list)
    errors: List[Dict[str, str]] = Field(default_factory=list)


class ContentQualityRequest(BaseModel):
    """内容质量检查请求"""
    content: str = Field(..., description="待检查内容")


# ==================== Service Instance ====================

_quality_orchestrator: Optional[QualityOrchestrator] = None


def get_quality_orchestrator() -> QualityOrchestrator:
    """获取 QualityOrchestrator 实例"""
    global _quality_orchestrator
    if _quality_orchestrator is None:
        _quality_orchestrator = QualityOrchestrator()
    return _quality_orchestrator


async def get_task_logger():
    """获取应用级共享的 TaskLogger 实例"""
    return get_shared_task_logger()


# ==================== Endpoints ====================

@router.post("/review", response_model=QualityResultResponse)
async def review_content(
    request: QualityReviewRequest,
    logger: TaskLogger = Depends(get_task_logger)
):
    """
    审核内容质量
    
    对内容运行质量门禁检查。
    
    Args:
        request: 质量审核请求
        
    Returns:
        QualityResult: 审核结果
    """
    orchestrator = get_quality_orchestrator()
    
    # 开始记录任务
    task_id = logger.start_task(
        module=ModuleName.QUALITY,
        input_data={
            "content_length": len(request.content),
            "enabled_gates": request.enabled_gates
        },
        metadata={"mode": "review"}
    )
    
    try:
        # 如果指定了门禁列表，使用传入的门禁配置
        if request.enabled_gates:
            result = orchestrator.run_gates_on_content(request.content, enabled_gates=request.enabled_gates)
        else:
            result = orchestrator.run_gates_on_content(request.content)
        
        # 完成任务记录
        logger.complete_task(
            task_id=task_id,
            output_data={
                "overall_status": result.overall_status.value,
                "gates_passed_count": len(result.gates_passed)
            }
        )
        
        return QualityResultResponse(
            task_id=task_id,
            overall_status=result.overall_status.value,
            gates_passed=result.gates_passed,
            warnings=result.warnings,
            errors=result.errors
        )
        
    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"质量审核失败: {str(e)}")


@router.post("/semantic-check")
async def semantic_check(
    request: ContentQualityRequest,
    logger: TaskLogger = Depends(get_task_logger)
):
    """
    语义检查
    
    对内容进行语义级别的检查。
    
    Args:
        request: 内容检查请求
        
    Returns:
        语义检查结果
    """
    orchestrator = get_quality_orchestrator()
    
    # 开始记录任务
    task_id = logger.start_task(
        module=ModuleName.QUALITY,
        input_data={
            "content_length": len(request.content)
        },
        metadata={"mode": "semantic_check"}
    )
    
    try:
        result = orchestrator.semantic_review_check(request.content)
        
        # 完成任务记录
        logger.complete_task(
            task_id=task_id,
            output_data={"status": "completed"}
        )
        
        return result
        
    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"语义检查失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "quality"}