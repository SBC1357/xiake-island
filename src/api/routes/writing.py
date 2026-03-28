"""
Writing API Routes

写作生成 API 端点。

SP-6 Batch 6C: 新增 /draft-with-trace 端点，暴露 writing_trace。
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.modules.writing.service import WritingService
from src.modules.writing.models import CompiledPrompt, CompiledPromptWithTrace
from src.runtime_logging import TaskLogger
from src.contracts.base import ModuleName
from src.api.app import get_shared_task_logger


router = APIRouter(prefix="/v1/writing", tags=["writing"])


# ==================== Request/Response Models ====================

class WritingRequest(BaseModel):
    """写作请求"""
    thesis: str = Field(..., description="核心论点")
    outline: List[Dict[str, Any]] = Field(default_factory=list, description="文章大纲")
    play_id: Optional[str] = Field(None, description="写作策略ID")
    arc_id: Optional[str] = Field(None, description="叙事弧线ID")
    target_audience: Optional[str] = Field(None, description="目标受众")
    key_evidence: Optional[List[str]] = Field(None, description="核心证据")
    style_notes: Optional[Dict[str, Any]] = Field(None, description="风格注释")


class WritingWithEvidenceRequest(BaseModel):
    """带证据的写作请求"""
    thesis: str = Field(..., description="核心论点")
    outline: List[Dict[str, Any]] = Field(default_factory=list, description="文章大纲")
    evidence_facts: List[Dict[str, Any]] = Field(default_factory=list, description="证据事实列表")
    play_id: Optional[str] = Field(None, description="写作策略ID")
    arc_id: Optional[str] = Field(None, description="叙事弧线ID")
    target_audience: Optional[str] = Field(None, description="目标受众")
    style_notes: Optional[Dict[str, Any]] = Field(None, description="风格注释")


class WritingWithTraceRequest(BaseModel):
    """带追踪的写作请求 - SP-6 Batch 6C"""
    thesis: str = Field(..., description="核心论点")
    outline: List[Dict[str, Any]] = Field(default_factory=list, description="文章大纲")
    evidence_facts: List[Dict[str, Any]] = Field(default_factory=list, description="证据事实列表")
    play_id: Optional[str] = Field(None, description="写作策略ID")
    arc_id: Optional[str] = Field(None, description="叙事弧线ID")
    target_audience: Optional[str] = Field(None, description="目标受众")
    style_notes: Optional[Dict[str, Any]] = Field(None, description="风格注释")
    target_word_count: Optional[int] = Field(None, description="目标字数")


class CompiledPromptResponse(BaseModel):
    """编译后 Prompt 响应（包含 task_id）"""
    task_id: str = Field(..., description="任务ID")
    system_prompt: str
    user_prompt: str
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="LLM 配置")
    extra_info: Dict[str, Any] = Field(default_factory=dict, description="额外信息")


# ==================== Service Instance ====================

_writing_service: Optional[WritingService] = None


def get_writing_service() -> WritingService:
    """获取 WritingService 实例"""
    global _writing_service
    if _writing_service is None:
        _writing_service = WritingService()
    return _writing_service


async def get_task_logger():
    """获取应用级共享的 TaskLogger 实例"""
    return get_shared_task_logger()


# ==================== Endpoints ====================

@router.post("/draft", response_model=CompiledPromptResponse)
async def compile_draft(
    request: WritingRequest,
    logger: TaskLogger = Depends(get_task_logger)
):
    """
    编译写作草稿 Prompt
    
    基于论点、大纲和可选证据生成编译后的 Prompt。
    
    Args:
        request: 写作请求
        
    Returns:
        CompiledPrompt: 编译后的 prompt
    """
    service = get_writing_service()
    
    # 开始记录任务
    task_id = logger.start_task(
        module=ModuleName.WRITING,
        input_data={
            "thesis": request.thesis[:50] if request.thesis else "",
            "outline_items": len(request.outline),
            "play_id": request.play_id
        },
        metadata={"arc_id": request.arc_id}
    )
    
    try:
        prompt = service.compile(
            thesis=request.thesis,
            outline=request.outline,
            play_id=request.play_id,
            arc_id=request.arc_id,
            target_audience=request.target_audience,
            key_evidence=request.key_evidence,
            style_notes=request.style_notes
        )
        
        # 完成任务记录
        logger.complete_task(
            task_id=task_id,
            output_data={
                "system_prompt_length": len(prompt.system_prompt),
                "user_prompt_length": len(prompt.user_prompt)
            }
        )
        
        return CompiledPromptResponse(
            task_id=task_id,
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
            llm_config=prompt.model_config,
            extra_info=prompt.metadata
        )
        
    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"Prompt 编译失败: {str(e)}")


@router.post("/draft-with-evidence", response_model=CompiledPromptResponse)
async def compile_draft_with_evidence(
    request: WritingWithEvidenceRequest,
    logger: TaskLogger = Depends(get_task_logger)
):
    """
    编译带详细证据的写作草稿 Prompt
    
    SP-6 Batch 6C: 使用 compile_with_trace 暴露 writing_trace
    
    Args:
        request: 带证据的写作请求
        
    Returns:
        CompiledPrompt: 编译后的 prompt，extra_info 包含 writing_trace
    """
    service = get_writing_service()
    
    # 开始记录任务
    task_id = logger.start_task(
        module=ModuleName.WRITING,
        input_data={
            "thesis": request.thesis[:50] if request.thesis else "",
            "outline_items": len(request.outline),
            "evidence_facts_count": len(request.evidence_facts),
            "play_id": request.play_id
        },
        metadata={"arc_id": request.arc_id, "mode": "with_evidence"}
    )
    
    try:
        # SP-6 Batch 6C: 使用 compile_with_trace 获取追踪信息
        result = service.compile_with_trace(
            thesis=request.thesis,
            outline=request.outline,
            evidence_facts=request.evidence_facts,
            play_id=request.play_id,
            arc_id=request.arc_id,
            target_audience=request.target_audience,
            style_notes=request.style_notes
        )
        
        prompt = result.prompt
        trace = result.trace
        
        # 完成任务记录
        logger.complete_task(
            task_id=task_id,
            output_data={
                "system_prompt_length": len(prompt.system_prompt),
                "user_prompt_length": len(prompt.user_prompt)
            }
        )
        
        # SP-6 Batch 6C: 在 extra_info 中暴露 writing_trace
        extra_info = dict(prompt.metadata)
        extra_info["writing_trace"] = trace.to_dict()
        
        return CompiledPromptResponse(
            task_id=task_id,
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
            llm_config=prompt.model_config,
            extra_info=extra_info
        )
        
    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"Prompt 编译失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "writing"}