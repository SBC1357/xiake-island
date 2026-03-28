"""
Opinion API 测试

测试 POST /v1/opinion/generate API。
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.api.app import app
from src.runtime_logging import TaskLogger, MemoryTaskLogStore


# 创建测试客户端
client = TestClient(app)


@pytest.fixture
def isolated_task_logger():
    """
    为测试提供隔离的 TaskLogger
    
    使用 MemoryTaskLogStore 替代共享的 SQLiteTaskLogStore，
    确保测试间完全隔离，不受其他进程或测试的干扰。
    """
    isolated = TaskLogger(MemoryTaskLogStore())
    with patch('src.api.app._shared_task_logger', isolated):
        yield isolated


class TestOpinionAPI:
    """测试 Opinion API"""
    
    def test_generate_opinion_success(self):
        """测试成功生成观点"""
        request_data = {
            "evidence_bundle": {
                "items": [
                    {
                        "id": "e1",
                        "content": "Clinical trial showed significant results",
                        "source": "PubMed",
                        "relevance": 0.9
                    },
                    {
                        "id": "e2",
                        "content": "Safety profile is acceptable"
                    }
                ],
                "summary": "Positive clinical trial results"
            },
            "audience": "医学专业人士",
            "thesis_hint": "关注疗效和安全性"
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "thesis" in data
        assert "support_points" in data
        assert "confidence_notes" in data
        
        # 验证论题结构
        thesis = data["thesis"]
        assert "statement" in thesis
        assert "confidence" in thesis
        assert 0 <= thesis["confidence"] <= 1
        
        # 验证置信度说明
        confidence_notes = data["confidence_notes"]
        assert "overall_confidence" in confidence_notes
        assert "limitations" in confidence_notes
        assert "assumptions" in confidence_notes
    
    def test_generate_opinion_minimal_request(self):
        """测试最小请求"""
        request_data = {
            "evidence_bundle": {
                "items": [
                    {"id": "e1", "content": "Test evidence"}
                ]
            },
            "audience": "普通公众"
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] is not None
    
    def test_generate_opinion_missing_required_field(self):
        """测试缺少必填字段"""
        request_data = {
            "evidence_bundle": {
                "items": []
            }
            # 缺少 audience
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_opinion_empty_audience(self):
        """测试空受众"""
        request_data = {
            "evidence_bundle": {
                "items": [{"id": "e1", "content": "test"}]
            },
            "audience": ""
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_opinion_extra_field_rejected(self):
        """测试额外字段被拒绝"""
        request_data = {
            "evidence_bundle": {
                "items": [{"id": "e1", "content": "test"}]
            },
            "audience": "test",
            "unknown_field": "value"
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_opinion_evidence_item_extra_field(self):
        """测试证据项额外字段被拒绝"""
        request_data = {
            "evidence_bundle": {
                "items": [
                    {
                        "id": "e1",
                        "content": "test",
                        "unknown": "field"
                    }
                ]
            },
            "audience": "test"
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_opinion_invalid_relevance(self):
        """测试无效相关性值"""
        request_data = {
            "evidence_bundle": {
                "items": [
                    {
                        "id": "e1",
                        "content": "test",
                        "relevance": 1.5  # 超出范围
                    }
                ]
            },
            "audience": "test"
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_returns_task_id(self):
        """测试返回任务ID用于追踪"""
        request_data = {
            "evidence_bundle": {
                "items": [{"id": "e1", "content": "test"}]
            },
            "audience": "test"
        }
        
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 task_id 格式（应该是 UUID）
        assert len(data["task_id"]) == 36
        assert data["task_id"].count("-") == 4


class TestHealthEndpoint:
    """测试健康检查端点"""
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "xiakedao"


class TestTaskLogTraceability:
    """测试任务日志可追踪性"""
    
    def test_task_id_is_traceable(self, isolated_task_logger):
        """
        测试 task_id 可被追踪
        
        验证 POST /v1/opinion/generate 返回的 task_id
        可以在应用级共享的 task logger 中查询到
        """
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "evidence_bundle": {
                "items": [{"id": "e1", "content": "Test evidence"}]
            },
            "audience": "test"
        }
        
        # 调用 API 生成观点
        response = client.post("/v1/opinion/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        
        # 通过共享的 task logger 查询该 task_id
        logger = get_shared_task_logger()
        task_entry = logger.get_task(task_id)
        
        # 验证 task 存在且状态为已完成
        assert task_entry is not None
        assert task_entry.task_id == task_id
        assert task_entry.status.value == "completed"
    
    def test_task_id_persists_across_requests(self, isolated_task_logger):
        """
        测试 task_id 在多次请求间可追踪
        
        验证多次调用使用同一个共享 store
        """
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "evidence_bundle": {
                "items": [{"id": "e1", "content": "Test"}]
            },
            "audience": "test"
        }
        
        # 第一次调用
        response1 = client.post("/v1/opinion/generate", json=request_data)
        assert response1.status_code == 200
        task_id_1 = response1.json()["task_id"]
        
        # 第二次调用
        response2 = client.post("/v1/opinion/generate", json=request_data)
        assert response2.status_code == 200
        task_id_2 = response2.json()["task_id"]
        
        # 验证两个 task_id 不同
        assert task_id_1 != task_id_2
        
        # 通过同一个 logger 查询两个 task
        logger = get_shared_task_logger()
        task_1 = logger.get_task(task_id_1)
        task_2 = logger.get_task(task_id_2)
        
        # 两个 task 都应该存在
        assert task_1 is not None
        assert task_2 is not None
        assert task_1.task_id == task_id_1
        assert task_2.task_id == task_id_2
    
    def test_query_returns_latest_tasks(self, isolated_task_logger):
        """
        测试查询返回最新任务
        
        验证 query(limit=N) 返回的是最新的 N 条任务
        """
        from src.api.app import get_shared_task_logger
        from src.runtime_logging import TaskLogQuery
        from src.contracts.base import ModuleName
        
        # 使用隔离的 logger（由 fixture 提供，已 patch）
        logger = get_shared_task_logger()
        
        request_data = {
            "evidence_bundle": {
                "items": [{"id": "e1", "content": "Test"}]
            },
            "audience": "test"
        }
        
        # 连续调用多次
        task_ids = []
        for i in range(5):
            response = client.post("/v1/opinion/generate", json=request_data)
            assert response.status_code == 200
            task_ids.append(response.json()["task_id"])
        
        # 查询最近的 3 条
        results = logger.query_tasks(TaskLogQuery(limit=3))
        
        # 应该返回最新的 3 条
        assert len(results) == 3
        
        # 验证是最新的（最后创建的）
        # 最新的 task_ids 在最后，所以 results[0] 应该对应 task_ids[-1]
        assert results[0].task_id == task_ids[-1]
        assert results[1].task_id == task_ids[-2]
        assert results[2].task_id == task_ids[-3]