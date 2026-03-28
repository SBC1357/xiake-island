"""
Semantic Review API 测试

测试 POST /v1/review/semantic API。
"""
import pytest
from fastapi.testclient import TestClient

from src.api.app import app, get_shared_task_logger


# 创建测试客户端
client = TestClient(app)


class TestSemanticReviewAPI:
    """测试 Semantic Review API"""
    
    def test_review_semantic_success(self):
        """测试成功审核"""
        request_data = {
            "content": "这是一段需要审核的中文医学内容，语言通俗易懂。",
            "audience": "普通公众",
            "prototype_hint": "科普文章",
            "register": "通俗"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "passed" in data
        assert "severity_summary" in data
        assert "findings" in data
        assert "rewrite_target" in data
        assert "prototype_alignment" in data
        
        # 验证字段类型
        assert isinstance(data["task_id"], str)
        assert isinstance(data["passed"], bool)
        assert isinstance(data["severity_summary"], dict)
        assert isinstance(data["findings"], list)
    
    def test_review_returns_task_id(self):
        """测试返回 task_id"""
        request_data = {
            "content": "测试内容，长度足够长。",
            "audience": "测试受众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 task_id 格式（应该是 UUID）
        assert len(data["task_id"]) == 36
        assert data["task_id"].count("-") == 4
    
    def test_review_response_structure(self):
        """测试返回体包含所有必需字段"""
        request_data = {
            "content": "这是一段良好的医学科普内容，语言通俗易懂。",
            "audience": "普通公众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 severity_summary 结构
        severity = data["severity_summary"]
        assert "low" in severity
        assert "medium" in severity
        assert "high" in severity
        assert "critical" in severity
        
        # 验证 findings 结构
        if data["findings"]:
            finding = data["findings"][0]
            assert "severity" in finding
            assert "category" in finding
            assert "description" in finding
        
        # 验证 prototype_alignment 结构
        if data["prototype_alignment"]:
            alignment = data["prototype_alignment"]
            assert "score" in alignment
            assert "matched_rules" in alignment
            assert "unmatched_rules" in alignment
    
    def test_review_missing_content_fails(self):
        """测试缺少 content 返回 422"""
        request_data = {
            "audience": "测试受众"
            # 缺少 content
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 422
    
    def test_review_missing_audience_fails(self):
        """测试缺少 audience 返回 422"""
        request_data = {
            "content": "测试内容"
            # 缺少 audience
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 422
    
    def test_review_empty_content_fails(self):
        """测试空 content 返回 422"""
        request_data = {
            "content": "",
            "audience": "测试受众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 422
    
    def test_review_empty_audience_fails(self):
        """测试空 audience 返回 422"""
        request_data = {
            "content": "测试内容",
            "audience": ""
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 422
    
    def test_review_extra_field_rejected(self):
        """测试额外字段被拒绝"""
        request_data = {
            "content": "测试内容",
            "audience": "测试受众",
            "unknown_field": "value"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 422
    
    def test_review_task_id_traceable(self):
        """测试 task_id 可通过共享 logger 追踪"""
        request_data = {
            "content": "这是一段需要审核的医学内容，确保长度足够。",
            "audience": "医学专业人士"
        }
        
        # 调用 API
        response = client.post("/v1/review/semantic", json=request_data)
        
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
    
    def test_review_content_too_short(self):
        """测试内容过短返回 400"""
        request_data = {
            "content": "太短",
            "audience": "测试受众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 400
        assert "过短" in response.json()["detail"]


class TestSemanticReviewAPIIntegration:
    """测试 Semantic Review API 集成场景"""
    
    def test_multiple_reviews_share_store(self):
        """测试多次审核使用同一个共享 store"""
        request_data = {
            "content": "这是一段良好的医学科普内容，语言通俗易懂。",
            "audience": "普通公众"
        }
        
        # 连续调用多次
        task_ids = []
        for _ in range(3):
            response = client.post("/v1/review/semantic", json=request_data)
            assert response.status_code == 200
            task_ids.append(response.json()["task_id"])
        
        # 验证所有 task_id 都不同
        assert len(set(task_ids)) == 3
        
        # 验证所有 task 都可在共享 logger 中找到
        logger = get_shared_task_logger()
        for task_id in task_ids:
            task_entry = logger.get_task(task_id)
            assert task_entry is not None
            assert task_entry.status.value == "completed"


class TestSemanticReviewAPISP6Batch6CSliceB:
    """SP-6 Batch 6C Slice B 测试：三层输出和重跑范围 API"""
    
    def test_response_contains_rule_layer_output(self):
        """测试响应包含 rule_layer_output"""
        request_data = {
            "content": "这是一段需要审核的中文医学内容，语言通俗易懂。",
            "audience": "普通公众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 rule_layer_output 存在
        assert "rule_layer_output" in data
        assert data["rule_layer_output"] is not None
        assert "families_executed" in data["rule_layer_output"]
    
    def test_response_contains_model_review_output(self):
        """测试响应包含 model_review_output"""
        request_data = {
            "content": "这是一段需要审核的中文医学内容，语言通俗易懂。",
            "audience": "普通公众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 model_review_output 存在
        assert "model_review_output" in data
        assert data["model_review_output"] is not None
        assert "findings" in data["model_review_output"]
        assert "severity_summary" in data["model_review_output"]
    
    def test_response_contains_rewrite_layer_output(self):
        """测试响应包含 rewrite_layer_output"""
        request_data = {
            "content": "这是一段需要审核的中文医学内容，语言通俗易懂。",
            "audience": "普通公众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 rewrite_layer_output 存在
        assert "rewrite_layer_output" in data
        assert data["rewrite_layer_output"] is not None
        assert "rewrite_targets" in data["rewrite_layer_output"]
        assert "count" in data["rewrite_layer_output"]
    
    def test_response_contains_rerun_scope(self):
        """测试响应包含 rerun_scope"""
        request_data = {
            "content": "这是一段需要审核的中文医学内容，语言通俗易懂。",
            "audience": "普通公众"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 rerun_scope 存在且值有效
        assert "rerun_scope" in data
        assert data["rerun_scope"] in ["full_gate_rerun", "partial_gate_rerun"]
    
    def test_all_layer_outputs_together(self):
        """测试三层输出同时存在"""
        request_data = {
            "content": "这是一段需要审核的中文医学内容，语言通俗易懂。",
            "audience": "普通公众",
            "prototype_hint": "科普文章",
            "register": "通俗"
        }
        
        response = client.post("/v1/review/semantic", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证所有字段都存在
        assert "rule_layer_output" in data
        assert "model_review_output" in data
        assert "rewrite_layer_output" in data
        assert "rerun_scope" in data
        
        # 验证各字段结构
        assert isinstance(data["rule_layer_output"]["families_executed"], list)
        assert isinstance(data["model_review_output"]["findings"], list)
        assert isinstance(data["rewrite_layer_output"]["rewrite_targets"], list)
        assert data["rerun_scope"] in ["full_gate_rerun", "partial_gate_rerun"]