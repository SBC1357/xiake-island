from fastapi.testclient import TestClient

from src.api.app import app
from src.api.routes import upload as upload_routes
from src.modules.evidence.services.upload_service import UploadService
from tests.modules.test_upload_persistence import StubImageConverter, StubVisionRecognizer


def test_delete_upload_endpoint_removes_runtime_artifacts(tmp_path, monkeypatch):
    service = UploadService(
        upload_root=tmp_path,
        image_converter=StubImageConverter(tmp_path),
        vision_recognizer=StubVisionRecognizer(),
    )
    monkeypatch.setattr(upload_routes, "_upload_service", service)

    with TestClient(app) as client:
        response = client.post(
            "/v1/evidence/upload/file",
            files={"file": ("evidence.png", b"fake-image-bytes", "image/png")},
            data={"task_id": "task-42"},
        )
        assert response.status_code == 200
        upload_id = response.json()["upload_id"]

        upload_dir = tmp_path / upload_id
        assert upload_dir.exists()

        delete_response = client.delete(f"/v1/evidence/upload/{upload_id}")
        assert delete_response.status_code == 200
        body = delete_response.json()
        assert body["upload_id"] == upload_id
        assert body["removed_files"] >= 2
        assert body["removed_directories"] >= 2
        assert not upload_dir.exists()

        missing_response = client.delete(f"/v1/evidence/upload/{upload_id}")
        assert missing_response.status_code == 404
