"""
多模态证据上传对象模型

阶段1产物：定义上传对象、图像化对象、证据片段、前端引用对象。
明确"文件对象 / 图像对象 / 证据片段 / 前端引用对象"的字段边界。
禁止 OCR 正式路径。
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class UploadFileType(str, Enum):
    """支持的上传文件类型"""
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    PPT = "ppt"
    PPTX = "pptx"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"


class UploadStatus(str, Enum):
    """上传处理状态"""
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    CONVERTING = "converting"
    CONVERTED = "converted"
    RECOGNIZING = "recognizing"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceFragmentType(str, Enum):
    """证据片段类型"""
    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"
    MIXED = "mixed"


# 允许的 MIME 类型白名单
ALLOWED_MIME_TYPES = {
    "application/pdf": UploadFileType.PDF,
    "application/msword": UploadFileType.DOC,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": UploadFileType.DOCX,
    "application/vnd.ms-powerpoint": UploadFileType.PPT,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": UploadFileType.PPTX,
    "image/jpeg": UploadFileType.JPG,
    "image/png": UploadFileType.PNG,
}

# 基于后缀的类型映射
EXTENSION_TO_TYPE = {
    ".pdf": UploadFileType.PDF,
    ".doc": UploadFileType.DOC,
    ".docx": UploadFileType.DOCX,
    ".ppt": UploadFileType.PPT,
    ".pptx": UploadFileType.PPTX,
    ".jpg": UploadFileType.JPG,
    ".jpeg": UploadFileType.JPEG,
    ".png": UploadFileType.PNG,
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB


def generate_upload_id() -> str:
    return f"upload_{uuid.uuid4().hex[:12]}"


def generate_image_id() -> str:
    return f"img_{uuid.uuid4().hex[:12]}"


def generate_fragment_id() -> str:
    return f"frag_{uuid.uuid4().hex[:12]}"


@dataclass
class UploadedFile:
    """
    上传文件对象 — 回溯层1：原始文件

    记录用户上传的原始文件信息与存储位置。
    """
    upload_id: str
    original_filename: str
    file_type: UploadFileType
    file_size_bytes: int
    storage_path: str
    content_hash: str
    task_id: Optional[str] = None
    status: UploadStatus = UploadStatus.PENDING
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class PageImage:
    """
    页面图像对象 — 回溯层2：中间图像

    文档页面或原始图像的标准化图像。
    每个文档页面对应一个 PageImage。
    每个原始图像文件对应一个 PageImage。
    """
    image_id: str
    upload_id: str
    page_number: int
    storage_path: str
    width: int
    height: int
    format: str = "png"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvidenceFragment:
    """
    证据片段 — 回溯层3：识别产物

    视觉识别从图像中提取的结构化证据片段。
    可回指具体的原始文件和页面图像。
    """
    fragment_id: str
    upload_id: str
    image_id: str
    page_number: int
    fragment_type: EvidenceFragmentType
    content: str
    confidence: float = 0.0
    source_location: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TraceableEvidence:
    """
    可回溯证据对象 — 回溯层4：前端引用对象

    供前端展示和后续调用链消费的最终证据对象。
    包含完整的回溯链信息。
    """
    evidence_id: str
    upload_id: str
    fragment_ids: List[str]
    content: str
    source_file: str
    source_pages: List[int]
    evidence_type: str = "file"
    confidence: Optional[float] = None
    status: UploadStatus = UploadStatus.COMPLETED
    traceback: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class UploadProcessingResult:
    """上传处理结果"""
    upload_id: str
    status: UploadStatus
    uploaded_file: Optional[UploadedFile] = None
    page_images: List[PageImage] = field(default_factory=list)
    fragments: List[EvidenceFragment] = field(default_factory=list)
    traceable_evidences: List[TraceableEvidence] = field(default_factory=list)
    error_message: Optional[str] = None
