from pathlib import Path

from src.modules.evidence.services.upload_service import UploadService
from src.modules.evidence.upload_models import (
    EvidenceFragment,
    EvidenceFragmentType,
    PageImage,
    UploadStatus,
)


class StubImageConverter:
    def __init__(self, upload_root: Path):
        self.upload_root = upload_root

    def convert(self, uploaded_file):
        images_dir = self.upload_root / uploaded_file.upload_id / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        image_path = images_dir / "page_1.png"
        image_path.write_bytes(b"stub-image")
        return [
            PageImage(
                image_id="img_stub_1",
                upload_id=uploaded_file.upload_id,
                page_number=1,
                storage_path=str(image_path),
                width=640,
                height=480,
                format="png",
            )
        ]


class StubVisionRecognizer:
    def recognize_pages(self, page_images, upload_id):
        page_image = page_images[0]
        return [
            EvidenceFragment(
                fragment_id="frag_stub_1",
                upload_id=upload_id,
                image_id=page_image.image_id,
                page_number=page_image.page_number,
                fragment_type=EvidenceFragmentType.TEXT,
                content="提取到的证据内容",
                confidence=0.92,
                source_location="page_1",
            )
        ]


class FailingImageConverter:
    def __init__(self, upload_root: Path):
        self.upload_root = upload_root

    def convert(self, uploaded_file):
        raise RuntimeError("image conversion exploded")


def test_upload_state_restored_after_service_restart(tmp_path):
    service = UploadService(
        upload_root=tmp_path,
        image_converter=StubImageConverter(tmp_path),
        vision_recognizer=StubVisionRecognizer(),
    )

    result = service.process_upload(
        filename="evidence.png",
        file_data=b"fake-image-bytes",
        task_id="task-123",
    )

    manifest_path = tmp_path / result.upload_id / "manifest.json"
    assert result.status == UploadStatus.COMPLETED
    assert manifest_path.exists()

    restored = UploadService(
        upload_root=tmp_path,
        image_converter=StubImageConverter(tmp_path),
        vision_recognizer=StubVisionRecognizer(),
    )

    upload = restored.get_upload(result.upload_id)
    assert upload is not None
    assert upload.status == UploadStatus.COMPLETED
    assert upload.task_id == "task-123"
    assert len(restored.list_uploads(task_id="task-123")) == 1
    assert len(restored._page_images[result.upload_id]) == 1
    assert len(restored._fragments[result.upload_id]) == 1
    assert len(restored.get_evidences(result.upload_id)) == 1
    assert restored.get_evidences(result.upload_id)[0].content == "提取到的证据内容"


def test_failed_upload_state_restored_after_service_restart(tmp_path):
    service = UploadService(
        upload_root=tmp_path,
        image_converter=FailingImageConverter(tmp_path),
        vision_recognizer=StubVisionRecognizer(),
    )

    result = service.process_upload(
        filename="broken.png",
        file_data=b"fake-image-bytes",
        task_id="task-err",
    )

    assert result.status == UploadStatus.FAILED
    assert result.uploaded_file is not None

    restored = UploadService(
        upload_root=tmp_path,
        image_converter=StubImageConverter(tmp_path),
        vision_recognizer=StubVisionRecognizer(),
    )

    upload = restored.get_upload(result.upload_id)
    assert upload is not None
    assert upload.status == UploadStatus.FAILED
    assert upload.task_id == "task-err"
    assert "image conversion exploded" in (upload.error_message or "")
    assert restored._page_images.get(result.upload_id, []) == []
    assert len(restored.list_uploads(task_id="task-err")) == 1


def test_delete_upload_removes_manifest_and_runtime_files(tmp_path):
    service = UploadService(
        upload_root=tmp_path,
        image_converter=StubImageConverter(tmp_path),
        vision_recognizer=StubVisionRecognizer(),
    )

    result = service.process_upload(
        filename="to-delete.png",
        file_data=b"fake-image-bytes",
        task_id="task-delete",
    )

    upload_dir = tmp_path / result.upload_id
    assert upload_dir.exists()

    delete_result = service.delete_upload(result.upload_id)

    assert delete_result["upload_id"] == result.upload_id
    assert int(delete_result["removed_files"]) >= 2
    assert int(delete_result["removed_directories"]) >= 2
    assert not upload_dir.exists()
    assert service.get_upload(result.upload_id) is None

    restored = UploadService(
        upload_root=tmp_path,
        image_converter=StubImageConverter(tmp_path),
        vision_recognizer=StubVisionRecognizer(),
    )
    assert restored.get_upload(result.upload_id) is None
