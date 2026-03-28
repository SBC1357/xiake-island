"""
Delivery API Routes

交付 API 端点。

SP-6 Batch 6D:
- output_path 指向 docx
- 添加 target_word_count 参数
- 响应包含 docx 元数据和字数门禁结果
"""
from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.modules.delivery.service import MarkdownWriter
from src.modules.delivery.models import DeliveryResult, WordCountGateError
from src.runtime_logging import TaskLogger
from src.contracts.base import ModuleName
from src.api.app import get_shared_task_logger


router = APIRouter(prefix="/v1/delivery", tags=["delivery"])


# ==================== Request/Response Models ====================

class DeliveryRequest(BaseModel):
    """
    交付请求
    
    SP-6 Batch 6D: 添加 target_word_count 参数
    """
    thesis: str = Field(..., description="核心论点")
    outline: List[Dict[str, Any]] = Field(default_factory=list, description="文章大纲")
    key_evidence: Optional[List[str]] = Field(None, description="核心证据")
    content: Optional[str] = Field(None, description="正文内容")
    target_audience: Optional[str] = Field(None, description="目标受众")
    play_id: Optional[str] = Field(None, description="写作策略ID")
    arc_id: Optional[str] = Field(None, description="叙事弧线ID")
    target_word_count: Optional[int] = Field(None, description="目标字数（用于门禁检查）")


class DeliveryResultResponse(BaseModel):
    """
    交付结果响应（包含 task_id）
    
    SP-6 Batch 6D: 包含 docx 元数据和字数门禁结果
    """
    task_id: str = Field(..., description="任务ID")
    output_path: str = Field(..., description="主输出文件路径 (docx)")
    summary: Dict[str, Any] = Field(default_factory=dict, description="交付摘要")
    artifacts: List[str] = Field(default_factory=list, description="所有生成产物的路径")
    
    # SP-6 Batch 6D: 新增字段
    markdown_preview_path: Optional[str] = Field(None, description="Markdown 预览文件路径")
    docx_path: Optional[str] = Field(None, description="Docx 输出文件路径")
    final_docx_word_count: Optional[int] = Field(None, description="Docx 正文词数")
    word_count_basis: str = Field(default="docx_body", description="词数统计基准")
    target_word_count: Optional[int] = Field(None, description="目标词数")
    word_count_gate_passed: bool = Field(default=True, description="词数门禁是否通过")


class DeliveryHistoryItem(BaseModel):
    """交付历史项"""
    filename: str
    path: str
    created_at: Optional[str] = None


class DeliveryHistoryResponse(BaseModel):
    """交付历史响应"""
    items: List[DeliveryHistoryItem]
    count: int


# ==================== Service Instance ====================

_markdown_writer: Optional[MarkdownWriter] = None


def get_markdown_writer() -> MarkdownWriter:
    """获取 MarkdownWriter 实例"""
    global _markdown_writer
    if _markdown_writer is None:
        _markdown_writer = MarkdownWriter()
    return _markdown_writer


async def get_task_logger():
    """获取应用级共享的 TaskLogger 实例"""
    return get_shared_task_logger()


# ==================== Endpoints ====================

@router.post("/deliver", response_model=DeliveryResultResponse)
async def deliver_content(
    request: DeliveryRequest,
    logger: TaskLogger = Depends(get_task_logger)
):
    """
    交付内容
    
    SP-6 Batch 6D: 
    - 生成 docx 作为正式输出
    - 生成 markdown 作为预览
    - 执行字数门禁检查
    
    Args:
        request: 交付请求
        
    Returns:
        DeliveryResult: 交付结果
        
    Raises:
        HTTPException: 当字数门禁检查失败时返回 400
    """
    writer = get_markdown_writer()
    
    # 开始记录任务
    task_id = logger.start_task(
        module=ModuleName.DELIVERY,
        input_data={
            "thesis": request.thesis[:50] if request.thesis else "",
            "outline_items": len(request.outline),
            "has_content": request.content is not None,
            "target_word_count": request.target_word_count
        },
        metadata={"play_id": request.play_id, "arc_id": request.arc_id}
    )
    
    try:
        result = writer.create_delivery_result(
            thesis=request.thesis,
            outline=request.outline,
            key_evidence=request.key_evidence,
            content=request.content,
            target_audience=request.target_audience,
            play_id=request.play_id,
            arc_id=request.arc_id,
            target_word_count=request.target_word_count
        )
        
        # 完成任务记录
        logger.complete_task(
            task_id=task_id,
            output_data={
                "output_path": str(result.output_path),
                "artifacts_count": len(result.artifacts),
                "docx_word_count": result.final_docx_word_count,
                "word_count_gate_passed": result.word_count_gate_passed
            }
        )
        
        return DeliveryResultResponse(
            task_id=task_id,
            output_path=str(result.output_path),
            summary=result.summary,
            artifacts=[str(a) for a in result.artifacts],
            markdown_preview_path=str(result.markdown_preview_path) if result.markdown_preview_path else None,
            docx_path=str(result.docx_path) if result.docx_path else None,
            final_docx_word_count=result.final_docx_word_count,
            word_count_basis=result.word_count_basis,
            target_word_count=result.target_word_count,
            word_count_gate_passed=result.word_count_gate_passed if result.word_count_gate_passed is not None else True if result.word_count_gate_passed is not None else True
        )
        
    except WordCountGateError as e:
        logger.fail_task(
            task_id=task_id,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "word_count_gate_failed",
                "message": str(e),
                "final_word_count": e.final_word_count,
                "target_word_count": e.target_word_count
            }
        )
        
    except Exception as e:
        logger.fail_task(task_id=task_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"交付失败: {str(e)}")


@router.get("/history", response_model=DeliveryHistoryResponse)
async def get_delivery_history():
    """
    获取交付历史
    
    列出 output 目录下的所有 Markdown 和 Docx 文件。
    
    Returns:
        交付历史列表
    """
    writer = get_markdown_writer()
    output_dir = writer.output_dir
    
    items = []
    if output_dir.exists():
        for file_path in output_dir.glob("*.*"):
            if file_path.suffix in [".md", ".docx"]:
                stat = file_path.stat()
                from datetime import datetime
                created_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
                items.append(DeliveryHistoryItem(
                    filename=file_path.name,
                    path=str(file_path),
                    created_at=created_at
                ))
    
    # 按修改时间倒序排列
    items.sort(key=lambda x: x.created_at or "", reverse=True)
    
    return DeliveryHistoryResponse(
        items=items,
        count=len(items)
    )


@router.get("/artifact/{filename}")
async def get_artifact(filename: str):
    """
    获取交付产物
    
    下载指定的 Markdown 或 Docx 文件。
    
    Args:
        filename: 文件名
        
    Returns:
        文件下载响应
    """
    writer = get_markdown_writer()
    output_dir = writer.output_dir
    
    # 安全检查：防止路径穿越
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # 根据扩展名设置 media_type
    if filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        media_type = "text/markdown"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "delivery"}