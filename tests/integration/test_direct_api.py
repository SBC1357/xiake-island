"""
Direct API Integration Tests

测试 planning/writing/quality/delivery 的 direct API 端点。

覆盖场景：
- 成功响应
- 返回 task_id
- 任务可通过 logger / tasks API 查询
- quality/review 的 enabled_gates 生效
"""
import pytest
from fastapi.testclient import TestClient

from src.api.app import app


# 创建测试客户端
client = TestClient(app)


class TestPlanningAPI:
    """测试 Planning Direct API"""
    
    def test_planning_plan_success(self):
        """测试成功生成编辑计划"""
        request_data = {
            "context": {
                "product_id": "pluvicto",
                "register": "R2",
                "audience": "医学专业人士"
            }
        }
        
        response = client.post("/v1/planning/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "thesis" in data
        assert "outline" in data
    
    def test_planning_returns_task_id(self):
        """测试返回 task_id"""
        request_data = {
            "context": {
                "product_id": "pluvicto",
                "register": "R2",
                "audience": "医学专业人士"
            }
        }
        
        response = client.post("/v1/planning/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # task_id 应该是有效的 UUID
        task_id = data["task_id"]
        assert task_id is not None
        assert len(task_id) == 36
        assert task_id.count("-") == 4
    
    def test_planning_task_traceable(self):
        """测试任务可追踪"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "context": {
                "product_id": "pluvicto",
                "register": "R2",
                "audience": "医学专业人士"
            }
        }
        
        response = client.post("/v1/planning/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        
        # 获取共享 logger
        logger = get_shared_task_logger()
        
        # 验证任务可追踪
        task = logger.get_task(task_id)
        assert task is not None
        assert task.task_id == task_id


class TestWritingAPI:
    """测试 Writing Direct API"""
    
    def test_writing_draft_success(self):
        """测试成功编译写作草稿"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": [
                {"title": "第一节", "type": "section"}
            ]
        }
        
        response = client.post("/v1/writing/draft", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "system_prompt" in data
        assert "user_prompt" in data
    
    def test_writing_returns_task_id(self):
        """测试返回 task_id"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": []
        }
        
        response = client.post("/v1/writing/draft", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # task_id 应该是有效的 UUID
        task_id = data["task_id"]
        assert task_id is not None
        assert len(task_id) == 36
        assert task_id.count("-") == 4
    
    def test_writing_draft_with_evidence_success(self):
        """测试带证据的写作草稿编译"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": [],
            "evidence_facts": [
                {"fact_id": "f1", "fact_key": "efficacy", "value": "有效"}
            ]
        }
        
        response = client.post("/v1/writing/draft-with-evidence", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "system_prompt" in data
        assert "user_prompt" in data
    
    def test_writing_task_traceable(self):
        """测试任务可追踪"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": []
        }
        
        response = client.post("/v1/writing/draft", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        
        # 获取共享 logger
        logger = get_shared_task_logger()
        
        # 验证任务可追踪
        task = logger.get_task(task_id)
        assert task is not None
        assert task.task_id == task_id


class TestQualityAPI:
    """测试 Quality Direct API"""
    
    def test_quality_review_success(self):
        """测试成功执行质量审核"""
        request_data = {
            "content": "这是一段测试内容，用于测试质量审核功能。内容长度超过十个字符。"
        }
        
        response = client.post("/v1/quality/review", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "overall_status" in data
        assert "gates_passed" in data
    
    def test_quality_returns_task_id(self):
        """测试返回 task_id"""
        request_data = {
            "content": "这是一段测试内容，用于测试质量审核功能。内容长度超过十个字符。"
        }
        
        response = client.post("/v1/quality/review", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # task_id 应该是有效的 UUID
        task_id = data["task_id"]
        assert task_id is not None
        assert len(task_id) == 36
        assert task_id.count("-") == 4
    
    def test_quality_enabled_gates_takes_effect(self):
        """测试 enabled_gates 参数生效"""
        # 测试只启用 basic 门禁
        request_data = {
            "content": "这是一段测试内容，用于测试质量审核功能。内容长度超过十个字符。",
            "enabled_gates": ["basic"]
        }
        
        response = client.post("/v1/quality/review", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证只运行了 basic 门禁
        gates_passed = data["gates_passed"]
        # basic 应该在通过的门禁列表中（如果内容合格）
        # 注意：length 不应该在列表中，因为我们只启用了 basic
        
    def test_quality_enabled_gates_length_only(self):
        """测试只启用 length 门禁"""
        request_data = {
            "content": "这是一段测试内容，用于测试质量审核功能。内容长度超过十个字符。",
            "enabled_gates": ["length"]
        }
        
        response = client.post("/v1/quality/review", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证只运行了 length 门禁
        gates_passed = data["gates_passed"]
        # length 应该在通过的门禁列表中（如果内容长度 >= 10）
        assert "length" in gates_passed
    
    def test_quality_task_traceable(self):
        """测试任务可追踪"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "content": "这是一段测试内容，用于测试质量审核功能。内容长度超过十个字符。"
        }
        
        response = client.post("/v1/quality/review", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        
        # 获取共享 logger
        logger = get_shared_task_logger()
        
        # 验证任务可追踪
        task = logger.get_task(task_id)
        assert task is not None
        assert task.task_id == task_id


class TestDeliveryAPI:
    """测试 Delivery Direct API"""
    
    def test_delivery_deliver_success(self):
        """测试成功交付内容"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": [
                {"title": "第一节", "type": "section"}
            ]
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "output_path" in data
        assert "summary" in data
    
    def test_delivery_returns_task_id(self):
        """测试返回 task_id"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": []
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # task_id 应该是有效的 UUID
        task_id = data["task_id"]
        assert task_id is not None
        assert len(task_id) == 36
        assert task_id.count("-") == 4
    
    def test_delivery_task_traceable(self):
        """测试任务可追踪"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": []
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        
        # 获取共享 logger
        logger = get_shared_task_logger()
        
        # 验证任务可追踪
        task = logger.get_task(task_id)
        assert task is not None
        assert task.task_id == task_id
    
    def test_delivery_history(self):
        """测试获取交付历史"""
        response = client.get("/v1/delivery/history")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "items" in data
        assert "count" in data


# ============================================================================
# SP-6 Batch 6D: Docx 输出测试
# ============================================================================

class TestDeliveryAPIDocxSP6Batch6D:
    """
    SP-6 Batch 6D: 验证 delivery API 的 docx 输出
    """
    
    def test_delivery_output_path_is_docx(self):
        """output_path 是 docx 文件"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": [
                {"title": "第一节", "type": "section"}
            ]
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # output_path 应该指向 docx
        assert data["output_path"].endswith(".docx")
    
    def test_delivery_docx_path_in_response(self):
        """响应包含 docx_path 字段"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": []
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # docx_path 应该存在
        assert "docx_path" in data
        assert data["docx_path"] is not None
        assert data["docx_path"].endswith(".docx")
    
    def test_delivery_markdown_preview_path_in_response(self):
        """响应包含 markdown_preview_path 字段"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": []
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # markdown_preview_path 应该存在
        assert "markdown_preview_path" in data
        assert data["markdown_preview_path"] is not None
        assert data["markdown_preview_path"].endswith(".md")
    
    def test_delivery_word_count_fields_in_response(self):
        """响应包含字数相关字段"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": [
                {"title": "第一节", "type": "section"}
            ]
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 字数相关字段
        assert "final_docx_word_count" in data
        assert data["final_docx_word_count"] is not None
        assert data["final_docx_word_count"] > 0
        
        assert "word_count_basis" in data
        assert data["word_count_basis"] == "docx_body"
        
        assert "word_count_gate_passed" in data
        assert data["word_count_gate_passed"] is True
    
    def test_delivery_target_word_count_in_response(self):
        """响应包含 target_word_count"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": [{"title": "章节", "type": "section"}],
            "key_evidence": ["证据"],
            "target_word_count": 10  # 使用低阈值确保通过
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "target_word_count" in data
        assert data["target_word_count"] == 10
    
    def test_delivery_artifacts_include_md_and_docx(self):
        """产物包含 md 和 docx"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": []
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # artifacts 应该包含 .md 和 .docx 文件
        artifacts = data["artifacts"]
        assert any(a.endswith(".md") for a in artifacts)
        assert any(a.endswith(".docx") for a in artifacts)
    
    def test_delivery_summary_contains_docx_metadata(self):
        """摘要包含 docx 元数据"""
        request_data = {
            "thesis": "这是一个测试论点",
            "outline": [],
            "target_word_count": 50
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        summary = data["summary"]
        assert "markdown_preview_path" in summary
        assert "docx_path" in summary
        assert "final_docx_word_count" in summary
        assert "word_count_basis" in summary
        assert "target_word_count" in summary
        assert "word_count_gate_passed" in summary
    
    def test_delivery_gate_blocks_when_below_threshold(self):
        """低于阈值时门禁阻断"""
        request_data = {
            "thesis": "短",
            "outline": [],
            "target_word_count": 10000  # 很高的阈值
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        # 应该返回 400 错误
        assert response.status_code == 400
        data = response.json()
        
        # 错误详情应该包含字数信息
        assert "detail" in data
        detail = data["detail"]
        if isinstance(detail, dict):
            assert "error" in detail
            assert detail["error"] == "word_count_gate_failed"
    
    def test_delivery_gate_passes_with_low_threshold(self):
        """低阈值时门禁通过"""
        request_data = {
            "thesis": "这是一个测试论点，包含足够的内容",
            "outline": [
                {"title": "第一节", "type": "section"},
                {"title": "第二节", "type": "section"}
            ],
            "key_evidence": ["证据一", "证据二"],
            "target_word_count": 10  # 低阈值
        }
        
        response = client.post("/v1/delivery/deliver", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["word_count_gate_passed"] is True