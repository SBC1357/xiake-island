"""
Smoke Test - 验证应用可导入且 /health 返回 200
"""
import pytest
from fastapi.testclient import TestClient
from src.api.app import app


client = TestClient(app)


def test_app_can_import():
    """测试应用可导入"""
    from src.api.app import app
    assert app is not None


def test_health_check_returns_200():
    """测试健康检查接口返回 200"""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_correct_json():
    """测试健康检查接口返回正确的 JSON"""
    response = client.get("/health")
    assert response.json() == {"status": "ok", "service": "xiakedao"}