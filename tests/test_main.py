from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.main import (
    XIAGEDAO_FRONTEND_DIST,
    XIAGEDAO_PORT,
    get_bind_port,
    setup_static_serving,
)


def test_unified_root_serves_frontend(monkeypatch):
    monkeypatch.delenv("XIAGEDAO_WEB_MODE", raising=False)
    test_app = FastAPI()
    assert setup_static_serving(target_app=test_app) is True

    client = TestClient(test_app)
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_unknown_api_path_still_returns_404(monkeypatch):
    monkeypatch.delenv("XIAGEDAO_WEB_MODE", raising=False)
    test_app = FastAPI()
    assert setup_static_serving(target_app=test_app) is True

    client = TestClient(test_app)
    response = client.get("/v1/not-found")

    assert response.status_code == 404


def test_api_only_mode_skips_frontend_mount(monkeypatch):
    monkeypatch.setenv("XIAGEDAO_WEB_MODE", "api-only")
    test_app = FastAPI()

    assert setup_static_serving(target_app=test_app) is False

    client = TestClient(test_app)
    response = client.get("/")

    assert response.status_code == 404


def test_custom_frontend_dist_env_is_used(monkeypatch, tmp_path):
    frontend_dist = tmp_path / "custom-dist"
    frontend_dist.mkdir()
    (frontend_dist / "index.html").write_text("<html>custom</html>", encoding="utf-8")

    monkeypatch.delenv("XIAGEDAO_WEB_MODE", raising=False)
    monkeypatch.setenv(XIAGEDAO_FRONTEND_DIST, str(frontend_dist))
    test_app = FastAPI()

    assert setup_static_serving(target_app=test_app) is True

    client = TestClient(test_app)
    response = client.get("/")

    assert response.status_code == 200
    assert "custom" in response.text


def test_invalid_port_falls_back_to_default(monkeypatch):
    monkeypatch.setenv(XIAGEDAO_PORT, "invalid-port")

    assert get_bind_port() == 8000
