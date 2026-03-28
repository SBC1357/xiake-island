"""
Tests for Tasks API

测试任务历史查询 API 端点。
"""
import pytest
from fastapi.testclient import TestClient

from src.api.app import app, get_shared_task_logger
from src.runtime_logging import TaskLogger, MemoryTaskLogStore, TaskLogQuery
from src.contracts.base import TaskStatus, ModuleName


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_logger():
    """创建测试用的 TaskLogger"""
    store = MemoryTaskLogStore()
    return TaskLogger(store)


class TestListTasks:
    """测试 GET /v1/tasks 端点"""
    
    def test_list_tasks_empty(self, client):
        """空列表场景"""
        response = client.get("/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert isinstance(data["tasks"], list)
    
    def test_list_tasks_with_data(self, client):
        """有数据场景"""
        # 先创建一个任务
        logger = get_shared_task_logger()
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data={"test": "data"}
        )
        logger.complete_task(
            task_id=task_id,
            output_data={"result": "success"}
        )
        
        response = client.get("/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        # 检查返回的字段
        task = data["tasks"][0]
        assert "task_id" in task
        assert "module" in task
        assert "status" in task
        assert "started_at" in task
    
    def test_list_tasks_filter_by_module(self, client):
        """按模块过滤"""
        response = client.get("/v1/tasks?module=opinion")
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["module"] == "opinion"
    
    def test_list_tasks_filter_by_status(self, client):
        """按状态过滤"""
        response = client.get("/v1/tasks?status=completed")
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "completed"
    
    def test_list_tasks_pagination(self, client):
        """分页测试"""
        response = client.get("/v1/tasks?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] <= 10
    
    def test_list_tasks_invalid_module(self, client):
        """无效模块名称返回 400 错误"""
        response = client.get("/v1/tasks?module=invalid_module")
        assert response.status_code == 400
        assert "无效的模块名称" in response.json()["detail"]
    
    def test_list_tasks_invalid_status(self, client):
        """无效状态返回 400 错误"""
        response = client.get("/v1/tasks?status=invalid_status")
        assert response.status_code == 400
        assert "无效的状态" in response.json()["detail"]


class TestGetTaskDetail:
    """测试 GET /v1/tasks/{task_id} 端点"""
    
    def test_get_task_not_found(self, client):
        """任务不存在"""
        response = client.get("/v1/tasks/nonexistent-task-id")
        assert response.status_code == 404
    
    def test_get_task_detail_success(self, client):
        """成功获取任务详情"""
        # 先创建一个任务
        logger = get_shared_task_logger()
        input_data = {
            "audience": "医学专业人士",
            "evidence_bundle": {"items": [{"id": "e1", "content": "test"}]}
        }
        output_data = {
            "thesis": {"statement": "测试观点", "confidence": 0.85}
        }
        
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data
        )
        logger.complete_task(
            task_id=task_id,
            output_data=output_data
        )
        
        response = client.get(f"/v1/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_id"] == task_id
        assert data["module"] == "opinion"
        assert data["status"] == "completed"
        
        # 验证 input_data 和 output_data
        assert data["input_data"] is not None
        assert data["input_data"]["audience"] == "医学专业人士"
        assert data["output_data"] is not None
        assert data["output_data"]["thesis"]["statement"] == "测试观点"
    
    def test_get_task_detail_with_child_tasks(self, client):
        """获取包含子任务的工作流任务详情"""
        logger = get_shared_task_logger()
        
        # 创建父任务
        parent_id = logger.start_task(
            module=ModuleName.ORCHESTRATOR,
            input_data={"workflow": "article"}
        )
        
        # 创建子任务
        child_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data={"audience": "医生"},
            parent_task_id=parent_id
        )
        logger.complete_task(child_id, output_data={"thesis": {}})
        
        # 完成父任务
        logger.complete_task(
            parent_id,
            child_task_ids=[child_id]
        )
        
        response = client.get(f"/v1/tasks/{parent_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert child_id in data["child_task_ids"]
    
    def test_get_task_detail_includes_input_hash(self, client):
        """详情包含 input_hash"""
        logger = get_shared_task_logger()
        
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data={"test": "hash_test"}
        )
        logger.complete_task(task_id)
        
        response = client.get(f"/v1/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["input_hash"] is not None
        assert len(data["input_hash"]) == 16  # SHA256 前16位


class TestTaskAPIIntegration:
    """API 集成测试"""
    
    def test_task_workflow_create_and_retrieve(self, client):
        """创建任务并通过 API 检索"""
        logger = get_shared_task_logger()
        
        # 创建任务
        task_id = logger.start_task(
            module=ModuleName.SEMANTIC_REVIEW,
            input_data={"content": "测试内容"}
        )
        logger.complete_task(
            task_id,
            output_data={"passed": True, "findings": []}
        )
        
        # 通过列表 API 查找
        response = client.get("/v1/tasks?module=semantic_review")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        # 通过详情 API 获取
        response = client.get(f"/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["output_data"]["passed"] == True


class TestTaskVersions:
    """测试版本查询和回退 API"""

    def test_get_task_versions(self, client):
        """按 input_hash 查询版本"""
        logger = get_shared_task_logger()
        
        # 创建两个相同输入的任务
        input_data = {"test": "version_test"}
        
        task_id_1 = logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data
        )
        logger.complete_task(task_id_1, output_data={"result": 1})
        
        task_id_2 = logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data
        )
        logger.complete_task(task_id_2, output_data={"result": 2})
        
        # 获取 input_hash
        detail = logger.get_task(task_id_1)
        input_hash = detail.input_hash
        
        # 查询版本
        response = client.get(f"/v1/tasks/versions/{input_hash}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["input_hash"] == input_hash
        assert data["total"] >= 2

    def test_copy_task(self, client):
        """复制任务创建新任务记录"""
        logger = get_shared_task_logger()
        
        # 创建原任务
        input_data = {"audience": "医生", "test": "copy"}
        
        original_task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data
        )
        logger.complete_task(original_task_id, output_data={"result": "original"})
        
        # 复制
        response = client.post(f"/v1/tasks/{original_task_id}/copy")
        assert response.status_code == 200
        
        data = response.json()
        assert data["original_task_id"] == original_task_id
        assert data["new_task_id"] != original_task_id
        assert "未执行" in data["message"]
        
        # 验证新任务已创建
        new_task = logger.get_task(data["new_task_id"])
        assert new_task is not None
        assert new_task.metadata["copied_from"] == original_task_id

    def test_copy_nonexistent_task(self, client):
        """复制不存在的任务"""
        response = client.post("/v1/tasks/nonexistent/copy")
        assert response.status_code == 404

    def test_copy_task_without_input(self, client):
        """复制无输入数据的任务"""
        logger = get_shared_task_logger()
        
        # 创建无输入数据的任务
        task_id = logger.start_task(module=ModuleName.OPINION)
        logger.complete_task(task_id)
        
        response = client.post(f"/v1/tasks/{task_id}/copy")
        assert response.status_code == 400
    
    def test_task_detail_preserves_empty_objects(self, client):
        """任务详情应保留空对象 {} 而非转为 null"""
        logger = get_shared_task_logger()
        
        # 创建带空对象的任务
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data={},  # 空对象
        )
        logger.complete_task(task_id, output_data={})  # 空对象
        
        response = client.get(f"/v1/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        # 空对象应保留为 {} 而非 null
        assert data["input_data"] == {}
        assert data["output_data"] == {}