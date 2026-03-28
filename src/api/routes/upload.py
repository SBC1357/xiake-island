"""
Evidence Upload API Routes

多模态证据文件上传与处理 API 端点。
支持 PDF / DOC / DOCX / PPT / PPTX / JPG / JPEG / PNG。
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from src.modules.evidence.services.upload_service import UploadService, UploadError
from src.modules.evidence.upload_models import (
    UploadStatus,
    MAX_FILE_SIZE_BYTES,
    EXTENSION_TO_TYPE,
)


router = APIRouter(prefix="/v1/evidence/upload", tags=["evidence_upload"])


# ==================== 应用级单例 ====================

_upload_service: Optional[UploadService] = None


def get_upload_service() -> UploadService:
    global _upload_service
    if _upload_service is None:
        _upload_service = UploadService()
    return _upload_service


# ==================== Response Models ====================


class TracebackInfo(BaseModel):
    original_file: dict = Field(default_factory=dict)
    page_image: dict = Field(default_factory=dict)
    fragment: dict = Field(default_factory=dict)


class TraceableEvidenceResponse(BaseModel):
    evidence_id: str
    upload_id: str
    content: str
    source_file: str
    source_pages: List[int]
    evidence_type: str
    confidence: Optional[float] = None
    status: str
    traceback: dict = Field(default_factory=dict)


class PageImageResponse(BaseModel):
    image_id: str
    page_number: int
    width: int
    height: int
    format: str


class EvidenceFragmentResponse(BaseModel):
    fragment_id: str
    page_number: int
    fragment_type: str
    content: str
    confidence: float
    source_location: Optional[str] = None


class UploadResponse(BaseModel):
    upload_id: str
    original_filename: str
    file_type: str
    status: str
    error_message: Optional[str] = None
    page_count: int = 0
    fragment_count: int = 0
    evidence_count: int = 0
    evidences: List[TraceableEvidenceResponse] = Field(default_factory=list)


class UploadStatusResponse(BaseModel):
    upload_id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    status: str
    task_id: Optional[str] = None
    error_message: Optional[str] = None
    page_images: List[PageImageResponse] = Field(default_factory=list)
    fragments: List[EvidenceFragmentResponse] = Field(default_factory=list)
    evidences: List[TraceableEvidenceResponse] = Field(default_factory=list)


class UploadListResponse(BaseModel):
    uploads: List[UploadResponse]
    total: int


class UploadDeleteResponse(BaseModel):
    upload_id: str
    removed_files: int
    removed_directories: int


# ==================== Endpoints ====================


@router.post("/file", response_model=UploadResponse)
async def upload_evidence_file(
    file: UploadFile = File(...),
    task_id: Optional[str] = Form(None),
):
    """
    上传多模态证据文件

    支持 PDF / DOC / DOCX / PPT / PPTX / JPG / JPEG / PNG。
    上传后自动执行：存储 -> 图像化 -> 视觉识别 -> 证据生成。

    Args:
        file: 上传的文件
        task_id: 可选的关联任务 ID

    Returns:
        上传处理结果，包含可回溯证据对象
    """
    service = get_upload_service()

    # 读取文件数据
    file_data = await file.read()

    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="上传文件为空")

    if len(file_data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大，最大允许 {MAX_FILE_SIZE_BYTES // (1024*1024)} MB",
        )

    try:
        result = service.process_upload(
            filename=file.filename or "unknown",
            file_data=file_data,
            task_id=task_id,
        )
    except UploadError as e:
        raise HTTPException(status_code=400, detail=str(e))

    evidences = [
        TraceableEvidenceResponse(
            evidence_id=ev.evidence_id,
            upload_id=ev.upload_id,
            content=ev.content[:500],  # 截断以减小响应体
            source_file=ev.source_file,
            source_pages=ev.source_pages,
            evidence_type=ev.evidence_type,
            confidence=ev.confidence,
            status=ev.status.value,
            traceback=ev.traceback,
        )
        for ev in result.traceable_evidences
    ]

    return UploadResponse(
        upload_id=result.upload_id,
        original_filename=result.uploaded_file.original_filename if result.uploaded_file else "unknown",
        file_type=result.uploaded_file.file_type.value if result.uploaded_file else "unknown",
        status=result.status.value,
        error_message=result.error_message,
        page_count=len(result.page_images),
        fragment_count=len(result.fragments),
        evidence_count=len(result.traceable_evidences),
        evidences=evidences,
    )


@router.get("/status/{upload_id}", response_model=UploadStatusResponse)
async def get_upload_status(upload_id: str):
    """
    获取上传处理状态与详情

    包含完整的回溯信息：原始文件 -> 页面图像 -> 证据片段 -> 可回溯证据。
    """
    service = get_upload_service()
    uploaded_file = service.get_upload(upload_id)

    if not uploaded_file:
        raise HTTPException(status_code=404, detail=f"Upload not found: {upload_id}")

    page_images = service._page_images.get(upload_id, [])
    fragments = service._fragments.get(upload_id, [])
    evidences = service._evidences.get(upload_id, [])

    return UploadStatusResponse(
        upload_id=uploaded_file.upload_id,
        original_filename=uploaded_file.original_filename,
        file_type=uploaded_file.file_type.value,
        file_size_bytes=uploaded_file.file_size_bytes,
        status=uploaded_file.status.value,
        task_id=uploaded_file.task_id,
        error_message=uploaded_file.error_message,
        page_images=[
            PageImageResponse(
                image_id=img.image_id,
                page_number=img.page_number,
                width=img.width,
                height=img.height,
                format=img.format,
            )
            for img in page_images
        ],
        fragments=[
            EvidenceFragmentResponse(
                fragment_id=frag.fragment_id,
                page_number=frag.page_number,
                fragment_type=frag.fragment_type.value,
                content=frag.content[:500],
                confidence=frag.confidence,
                source_location=frag.source_location,
            )
            for frag in fragments
        ],
        evidences=[
            TraceableEvidenceResponse(
                evidence_id=ev.evidence_id,
                upload_id=ev.upload_id,
                content=ev.content[:500],
                source_file=ev.source_file,
                source_pages=ev.source_pages,
                evidence_type=ev.evidence_type,
                confidence=ev.confidence,
                status=ev.status.value,
                traceback=ev.traceback,
            )
            for ev in evidences
        ],
    )


@router.get("/list", response_model=UploadListResponse)
async def list_uploads(task_id: Optional[str] = None):
    """
    列出上传记录

    Args:
        task_id: 可选的任务 ID 过滤

    Returns:
        上传记录列表
    """
    service = get_upload_service()
    uploads = service.list_uploads(task_id=task_id)

    return UploadListResponse(
        uploads=[
            UploadResponse(
                upload_id=u.upload_id,
                original_filename=u.original_filename,
                file_type=u.file_type.value,
                status=u.status.value,
                error_message=u.error_message,
                page_count=len(service._page_images.get(u.upload_id, [])),
                fragment_count=len(service._fragments.get(u.upload_id, [])),
                evidence_count=len(service._evidences.get(u.upload_id, [])),
            )
            for u in uploads
        ],
        total=len(uploads),
    )


@router.get("/evidences/{upload_id}", response_model=List[TraceableEvidenceResponse])
async def get_upload_evidences(upload_id: str):
    """
    获取上传文件生成的所有可回溯证据

    Args:
        upload_id: 上传 ID

    Returns:
        可回溯证据列表
    """
    service = get_upload_service()
    evidences = service.get_evidences(upload_id)

    if not evidences and not service.get_upload(upload_id):
        raise HTTPException(status_code=404, detail=f"Upload not found: {upload_id}")

    return [
        TraceableEvidenceResponse(
            evidence_id=ev.evidence_id,
            upload_id=ev.upload_id,
            content=ev.content,
            source_file=ev.source_file,
            source_pages=ev.source_pages,
            evidence_type=ev.evidence_type,
            confidence=ev.confidence,
            status=ev.status.value,
            traceback=ev.traceback,
        )
        for ev in evidences
    ]


@router.get("/task/{task_id}/evidences", response_model=List[TraceableEvidenceResponse])
async def get_task_evidences(task_id: str):
    """
    获取指定任务关联的所有可回溯证据

    Args:
        task_id: 任务 ID

    Returns:
        该任务的所有可回溯证据
    """
    service = get_upload_service()
    evidences = service.get_all_evidences_for_task(task_id)

    return [
        TraceableEvidenceResponse(
            evidence_id=ev.evidence_id,
            upload_id=ev.upload_id,
            content=ev.content,
            source_file=ev.source_file,
            source_pages=ev.source_pages,
            evidence_type=ev.evidence_type,
            confidence=ev.confidence,
            status=ev.status.value,
            traceback=ev.traceback,
        )
        for ev in evidences
    ]


@router.delete("/{upload_id}", response_model=UploadDeleteResponse)
async def delete_upload(upload_id: str):
    """
    删除单个上传的运行态文件与索引。

    用于扩展开发和回归测试后的运行态清理，不影响仓库源码。
    """
    service = get_upload_service()

    try:
        result = service.delete_upload(upload_id)
    except UploadError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return UploadDeleteResponse(
        upload_id=upload_id,
        removed_files=int(result["removed_files"]),
        removed_directories=int(result["removed_directories"]),
    )
