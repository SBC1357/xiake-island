"""
多模态证据上传处理服务

完整链路：文件上传 -> 存储 -> 图像化 -> 视觉识别 -> 证据片段 -> 可回溯证据
禁止 OCR 作为正式识别方案。
"""
import hashlib
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from ..upload_models import (
    UploadedFile,
    PageImage,
    EvidenceFragment,
    TraceableEvidence,
    UploadProcessingResult,
    UploadFileType,
    UploadStatus,
    ALLOWED_MIME_TYPES,
    EXTENSION_TO_TYPE,
    MAX_FILE_SIZE_BYTES,
    generate_upload_id,
)
from .image_converter import ImageConverter
from .upload_manifest_store import UploadManifestStore
from .vision_recognizer import VisionRecognizer
from src.runtime_paths import get_upload_root


class UploadError(Exception):
    pass


class UploadService:
    """
    多模态证据上传处理服务

    负责：
    1. 文件接收与验证
    2. 安全存储
    3. 调用图像转换服务
    4. 调用视觉识别服务
    5. 生成可回溯证据对象
    6. 维护上传记录
    """

    def __init__(
        self,
        upload_root: Optional[Path] = None,
        image_converter: Optional[ImageConverter] = None,
        vision_recognizer: Optional[VisionRecognizer] = None,
    ):
        self.upload_root = upload_root or get_upload_root()
        self.upload_root.mkdir(parents=True, exist_ok=True)
        self._converter = image_converter or ImageConverter(self.upload_root)
        self._recognizer = vision_recognizer or VisionRecognizer()
        self._manifest_store = UploadManifestStore(self.upload_root)

        # 内存中的上传记录（后续可持久化到 SQLite）
        self._uploads: Dict[str, UploadedFile] = {}
        self._page_images: Dict[str, List[PageImage]] = {}
        self._fragments: Dict[str, List[EvidenceFragment]] = {}
        self._evidences: Dict[str, List[TraceableEvidence]] = {}
        self._load_persisted_uploads()

    def _load_persisted_uploads(self) -> None:
        for uploaded_file, page_images, fragments, evidences in self._manifest_store.load_all():
            upload_id = uploaded_file.upload_id
            self._uploads[upload_id] = uploaded_file
            self._page_images[upload_id] = page_images
            self._fragments[upload_id] = fragments
            self._evidences[upload_id] = evidences

    def _persist_upload_state(self, upload_id: str) -> None:
        uploaded_file = self._uploads.get(upload_id)
        if uploaded_file is None:
            return

        self._manifest_store.save(
            uploaded_file=uploaded_file,
            page_images=self._page_images.get(upload_id, []),
            fragments=self._fragments.get(upload_id, []),
            evidences=self._evidences.get(upload_id, []),
        )

    def validate_file(
        self, filename: str, file_size: int, content_type: Optional[str] = None
    ) -> UploadFileType:
        """
        验证上传文件

        Args:
            filename: 原始文件名
            file_size: 文件大小（字节）
            content_type: MIME 类型

        Returns:
            文件类型

        Raises:
            UploadError: 验证失败
        """
        if file_size > MAX_FILE_SIZE_BYTES:
            raise UploadError(
                f"文件过大: {file_size} bytes，最大允许 {MAX_FILE_SIZE_BYTES} bytes"
            )

        # 基于文件后缀判断类型
        ext = Path(filename).suffix.lower()
        file_type = EXTENSION_TO_TYPE.get(ext)

        if file_type is None:
            raise UploadError(
                f"不支持的文件格式: {ext}。"
                f"支持的格式: {', '.join(EXTENSION_TO_TYPE.keys())}"
            )

        # 如果有 content_type，交叉验证
        if content_type and content_type in ALLOWED_MIME_TYPES:
            mime_type = ALLOWED_MIME_TYPES[content_type]
            # JPEG/JPG 等价
            if mime_type.value not in (file_type.value, "jpeg", "jpg"):
                if not (
                    {mime_type.value, file_type.value} <= {"jpg", "jpeg"}
                ):
                    raise UploadError(
                        f"文件后缀 ({ext}) 与 MIME 类型 ({content_type}) 不匹配"
                    )

        return file_type

    def store_file(
        self,
        filename: str,
        file_data: bytes,
        task_id: Optional[str] = None,
    ) -> UploadedFile:
        """
        存储上传文件

        Args:
            filename: 原始文件名
            file_data: 文件二进制数据
            task_id: 关联的任务 ID

        Returns:
            UploadedFile 记录
        """
        file_type = self.validate_file(filename, len(file_data))

        upload_id = generate_upload_id()
        content_hash = hashlib.sha256(file_data).hexdigest()

        # 创建存储目录
        upload_dir = self.upload_root / upload_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 安全化文件名：只保留基础名和后缀
        safe_filename = f"original{Path(filename).suffix.lower()}"
        storage_path = upload_dir / safe_filename

        with open(storage_path, "wb") as f:
            f.write(file_data)

        uploaded_file = UploadedFile(
            upload_id=upload_id,
            original_filename=filename,
            file_type=file_type,
            file_size_bytes=len(file_data),
            storage_path=str(storage_path),
            content_hash=content_hash,
            task_id=task_id,
            status=UploadStatus.UPLOADED,
        )

        self._uploads[upload_id] = uploaded_file
        self._persist_upload_state(upload_id)
        return uploaded_file

    def convert_to_images(self, upload_id: str) -> List[PageImage]:
        """
        将上传文件转换为页面图像

        Args:
            upload_id: 上传 ID

        Returns:
            PageImage 列表
        """
        uploaded_file = self._uploads.get(upload_id)
        if not uploaded_file:
            raise UploadError(f"Upload not found: {upload_id}")

        uploaded_file.status = UploadStatus.CONVERTING
        self._persist_upload_state(upload_id)
        try:
            page_images = self._converter.convert(uploaded_file)
            self._page_images[upload_id] = page_images
            uploaded_file.status = UploadStatus.CONVERTED
            uploaded_file.error_message = None
            self._persist_upload_state(upload_id)
            return page_images
        except Exception as e:
            uploaded_file.status = UploadStatus.FAILED
            uploaded_file.error_message = str(e)
            self._persist_upload_state(upload_id)
            raise UploadError(f"Image conversion failed: {e}") from e

    def recognize_images(self, upload_id: str) -> List[EvidenceFragment]:
        """
        对页面图像执行视觉识别

        Args:
            upload_id: 上传 ID

        Returns:
            EvidenceFragment 列表
        """
        uploaded_file = self._uploads.get(upload_id)
        if not uploaded_file:
            raise UploadError(f"Upload not found: {upload_id}")

        page_images = self._page_images.get(upload_id, [])
        if not page_images:
            raise UploadError(f"No images found for upload: {upload_id}")

        uploaded_file.status = UploadStatus.RECOGNIZING
        self._persist_upload_state(upload_id)
        try:
            fragments = self._recognizer.recognize_pages(page_images, upload_id)
            self._fragments[upload_id] = fragments
            uploaded_file.error_message = None
            self._persist_upload_state(upload_id)
            return fragments
        except Exception as e:
            uploaded_file.status = UploadStatus.FAILED
            uploaded_file.error_message = str(e)
            self._persist_upload_state(upload_id)
            raise UploadError(f"Vision recognition failed: {e}") from e

    def build_traceable_evidences(
        self, upload_id: str
    ) -> List[TraceableEvidence]:
        """
        将识别出的证据片段构建为可回溯证据对象

        Args:
            upload_id: 上传 ID

        Returns:
            TraceableEvidence 列表
        """
        uploaded_file = self._uploads.get(upload_id)
        if not uploaded_file:
            raise UploadError(f"Upload not found: {upload_id}")

        fragments = self._fragments.get(upload_id, [])
        page_images = self._page_images.get(upload_id, [])

        # 构建页码到图像的映射
        page_to_image = {img.page_number: img for img in page_images}

        evidences = []
        for fragment in fragments:
            evidence_id = f"ev_{uuid.uuid4().hex[:12]}"
            source_image = page_to_image.get(fragment.page_number)

            evidence = TraceableEvidence(
                evidence_id=evidence_id,
                upload_id=upload_id,
                fragment_ids=[fragment.fragment_id],
                content=fragment.content,
                source_file=uploaded_file.original_filename,
                source_pages=[fragment.page_number],
                evidence_type="file",
                status=UploadStatus.COMPLETED,
                traceback={
                    "original_file": {
                        "upload_id": upload_id,
                        "filename": uploaded_file.original_filename,
                        "file_type": uploaded_file.file_type.value,
                        "content_hash": uploaded_file.content_hash,
                    },
                    "page_image": {
                        "image_id": source_image.image_id if source_image else None,
                        "page_number": fragment.page_number,
                        "image_path": source_image.storage_path if source_image else None,
                    },
                    "fragment": {
                        "fragment_id": fragment.fragment_id,
                        "fragment_type": fragment.fragment_type.value,
                        "confidence": fragment.confidence,
                    },
                },
            )
            evidences.append(evidence)

        uploaded_file.status = UploadStatus.COMPLETED
        self._evidences[upload_id] = evidences
        uploaded_file.error_message = None
        self._persist_upload_state(upload_id)
        return evidences

    def process_upload(
        self,
        filename: str,
        file_data: bytes,
        task_id: Optional[str] = None,
    ) -> UploadProcessingResult:
        """
        完整处理链路：上传 -> 存储 -> 图像化 -> 视觉识别 -> 证据生成

        Args:
            filename: 原始文件名
            file_data: 文件数据
            task_id: 关联任务 ID

        Returns:
            UploadProcessingResult 处理结果
        """
        upload_id = None
        try:
            # 1. 存储文件
            uploaded_file = self.store_file(filename, file_data, task_id)
            upload_id = uploaded_file.upload_id

            # 2. 图像化转换
            page_images = self.convert_to_images(upload_id)

            # 3. 视觉识别
            fragments = self.recognize_images(upload_id)

            # 4. 构建可回溯证据
            evidences = self.build_traceable_evidences(upload_id)

            return UploadProcessingResult(
                upload_id=upload_id,
                status=UploadStatus.COMPLETED,
                uploaded_file=uploaded_file,
                page_images=page_images,
                fragments=fragments,
                traceable_evidences=evidences,
            )

        except Exception as e:
            return UploadProcessingResult(
                upload_id=upload_id or "unknown",
                status=UploadStatus.FAILED,
                uploaded_file=self._uploads.get(upload_id) if upload_id else None,
                error_message=str(e),
            )

    def get_upload(self, upload_id: str) -> Optional[UploadedFile]:
        return self._uploads.get(upload_id)

    def get_evidences(self, upload_id: str) -> List[TraceableEvidence]:
        return self._evidences.get(upload_id, [])

    def delete_upload(self, upload_id: str) -> dict[str, int | str]:
        """删除单个上传链路的运行态文件与内存索引。"""
        upload_dir = self.upload_root / upload_id
        if upload_id not in self._uploads and not upload_dir.exists():
            raise UploadError(f"Upload not found: {upload_id}")

        removed_files = 0
        removed_directories = 0

        if upload_dir.exists():
            removed_files = sum(1 for path in upload_dir.rglob("*") if path.is_file())
            removed_directories = sum(1 for path in upload_dir.rglob("*") if path.is_dir()) + 1
            shutil.rmtree(upload_dir)

        self._uploads.pop(upload_id, None)
        self._page_images.pop(upload_id, None)
        self._fragments.pop(upload_id, None)
        self._evidences.pop(upload_id, None)

        return {
            "upload_id": upload_id,
            "removed_files": removed_files,
            "removed_directories": removed_directories,
        }

    def get_all_evidences_for_task(self, task_id: str) -> List[TraceableEvidence]:
        """获取指定任务关联的所有可回溯证据"""
        result = []
        for upload_id, uploaded_file in self._uploads.items():
            if uploaded_file.task_id == task_id:
                result.extend(self._evidences.get(upload_id, []))
        return result

    def list_uploads(
        self, task_id: Optional[str] = None
    ) -> List[UploadedFile]:
        """列出上传记录"""
        if task_id:
            return [
                f for f in self._uploads.values() if f.task_id == task_id
            ]
        return list(self._uploads.values())
