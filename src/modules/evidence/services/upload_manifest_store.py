"""
上传链持久化存储

将每个 upload 的元数据与状态写入对应目录下的 manifest.json，
让文件和索引保持同一持久化边界。
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..upload_models import (
    EvidenceFragment,
    EvidenceFragmentType,
    PageImage,
    TraceableEvidence,
    UploadedFile,
    UploadStatus,
    UploadFileType,
)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


def _parse_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    return datetime.fromisoformat(raw)


class UploadManifestStore:
    MANIFEST_NAME = "manifest.json"

    def __init__(self, upload_root: Path):
        self.upload_root = upload_root

    def save(
        self,
        uploaded_file: UploadedFile,
        page_images: list[PageImage],
        fragments: list[EvidenceFragment],
        evidences: list[TraceableEvidence],
    ) -> None:
        manifest_path = self._manifest_path(uploaded_file.upload_id)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "uploaded_file": _serialize_value(asdict(uploaded_file)),
            "page_images": _serialize_value([asdict(item) for item in page_images]),
            "fragments": _serialize_value([asdict(item) for item in fragments]),
            "evidences": _serialize_value([asdict(item) for item in evidences]),
        }
        manifest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_all(
        self,
    ) -> list[tuple[UploadedFile, list[PageImage], list[EvidenceFragment], list[TraceableEvidence]]]:
        snapshots = []
        for manifest_path in sorted(self.upload_root.glob(f"*/{self.MANIFEST_NAME}")):
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            uploaded_file = self._load_uploaded_file(payload["uploaded_file"])
            page_images = [self._load_page_image(item) for item in payload.get("page_images", [])]
            fragments = [self._load_fragment(item) for item in payload.get("fragments", [])]
            evidences = [self._load_evidence(item) for item in payload.get("evidences", [])]
            snapshots.append((uploaded_file, page_images, fragments, evidences))
        return snapshots

    def _manifest_path(self, upload_id: str) -> Path:
        return self.upload_root / upload_id / self.MANIFEST_NAME

    def _load_uploaded_file(self, data: dict[str, Any]) -> UploadedFile:
        return UploadedFile(
            upload_id=data["upload_id"],
            original_filename=data["original_filename"],
            file_type=UploadFileType(data["file_type"]),
            file_size_bytes=data["file_size_bytes"],
            storage_path=data["storage_path"],
            content_hash=data["content_hash"],
            task_id=data.get("task_id"),
            status=UploadStatus(data["status"]),
            error_message=data.get("error_message"),
            created_at=_parse_datetime(data.get("created_at")) or datetime.now(),
            metadata=data.get("metadata", {}),
        )

    def _load_page_image(self, data: dict[str, Any]) -> PageImage:
        return PageImage(
            image_id=data["image_id"],
            upload_id=data["upload_id"],
            page_number=data["page_number"],
            storage_path=data["storage_path"],
            width=data["width"],
            height=data["height"],
            format=data.get("format", "png"),
            created_at=_parse_datetime(data.get("created_at")) or datetime.now(),
        )

    def _load_fragment(self, data: dict[str, Any]) -> EvidenceFragment:
        return EvidenceFragment(
            fragment_id=data["fragment_id"],
            upload_id=data["upload_id"],
            image_id=data["image_id"],
            page_number=data["page_number"],
            fragment_type=EvidenceFragmentType(data["fragment_type"]),
            content=data["content"],
            confidence=data.get("confidence", 0.0),
            source_location=data.get("source_location"),
            metadata=data.get("metadata", {}),
            created_at=_parse_datetime(data.get("created_at")) or datetime.now(),
        )

    def _load_evidence(self, data: dict[str, Any]) -> TraceableEvidence:
        return TraceableEvidence(
            evidence_id=data["evidence_id"],
            upload_id=data["upload_id"],
            fragment_ids=data.get("fragment_ids", []),
            content=data["content"],
            source_file=data["source_file"],
            source_pages=data.get("source_pages", []),
            evidence_type=data.get("evidence_type", "file"),
            confidence=data.get("confidence"),
            status=UploadStatus(data.get("status", UploadStatus.COMPLETED.value)),
            traceback=data.get("traceback", {}),
            created_at=_parse_datetime(data.get("created_at")) or datetime.now(),
        )
