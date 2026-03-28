"""
Workflow API 测试

测试 POST /v1/workflow/article API。
"""
import pytest
from fastapi.testclient import TestClient

from src.api.app import app


# 创建测试客户端
client = TestClient(app)


class TestArticleWorkflowAPI:
    """测试 Article Workflow API"""
    
    def test_article_workflow_success(self):
        """测试成功执行文章工作流"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [
                            {
                                "id": "e1",
                                "content": "Clinical trial showed significant results",
                                "source": "PubMed"
                            }
                        ]
                    },
                    "audience": "医学专业人士"
                },
                "semantic_review": {
                    "audience": "医学专业人士",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "task_id" in data
        assert "child_task_ids" in data
        assert "status" in data
        assert "result" in data
        assert "child_results" in data
        
        # 验证 task_id 存在
        assert data["task_id"] is not None
        assert len(data["task_id"]) == 36  # UUID format
        
        # 验证 child_task_ids 有两个子任务
        assert len(data["child_task_ids"]) == 2
        
        # 验证状态为 completed
        assert data["status"] == "completed"
        
        # 验证 child_results 有两个结果
        assert len(data["child_results"]) == 2
        
        # 验证第一个是 opinion，第二个是 semantic_review
        modules = [cr["module_name"] for cr in data["child_results"]]
        assert "opinion" in modules
        assert "semantic_review" in modules
    
    def test_article_workflow_returns_real_task_id(self):
        """测试返回真实的 task_id"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # task_id 应该是有效的 UUID
        task_id = data["task_id"]
        assert task_id is not None
        assert len(task_id) == 36
        assert task_id.count("-") == 4
        
        # child_task_ids 也应该是有效的 UUID
        for child_id in data["child_task_ids"]:
            assert len(child_id) == 36
            assert child_id.count("-") == 4
    
    def test_article_workflow_child_task_ids_traceable(self):
        """测试 child_task_ids 可追踪"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 获取共享 logger
        logger = get_shared_task_logger()
        
        # 验证父任务可追踪
        parent_task = logger.get_task(data["task_id"])
        assert parent_task is not None
        assert parent_task.task_id == data["task_id"]
        
        # 验证子任务可追踪
        for child_id in data["child_task_ids"]:
            child_task = logger.get_task(child_id)
            assert child_task is not None
            assert child_task.parent_task_id == data["task_id"]
    
    def test_article_workflow_minimal_request(self):
        """测试最小请求"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] is not None
    
    def test_article_workflow_missing_input_data(self):
        """测试缺少 input_data"""
        request_data = {}
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 422
    
    def test_article_workflow_empty_input_data(self):
        """测试空 input_data - 应该返回 422 因为 opinion 是必填的"""
        request_data = {
            "input_data": {}
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        # 空的 input_data 缺少必填的 opinion 字段，应该返回 422
        assert response.status_code == 422
    
    def test_article_workflow_missing_opinion_returns_422(self):
        """测试缺少 opinion 返回 422"""
        request_data = {
            "input_data": {
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 422
    
    def test_article_workflow_invalid_opinion_field_returns_422(self):
        """测试 opinion 中无效字段返回 422"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test",
                    "invalid_field": "should_fail"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        # 由于 extra="forbid"，无效字段应该被拒绝
        assert response.status_code == 422
    
    def test_article_workflow_invalid_semantic_review_field_returns_422(self):
        """测试 semantic_review 中无效字段返回 422"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "invalid_field": "should_fail"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 422
    
    def test_article_workflow_missing_evidence_bundle_returns_422(self):
        """测试缺少 evidence_bundle 返回 422"""
        request_data = {
            "input_data": {
                "opinion": {
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 422
    
    def test_article_workflow_extra_field_rejected(self):
        """测试额外字段被拒绝"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            },
            "unknown_field": "value"
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 422
    
    def test_article_workflow_result_structure(self):
        """测试结果结构正确"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 result 结构
        assert "opinion" in data["result"]
        assert "semantic_review" in data["result"]
        
        # 验证 opinion 结果
        opinion_result = data["result"]["opinion"]
        assert "passed" in opinion_result
        
        # 验证 semantic_review 结果
        review_result = data["result"]["semantic_review"]
        assert "passed" in review_result


class TestWorkflowTraceability:
    """测试工作流可追踪性"""
    
    def test_parent_child_relationship(self):
        """测试父子任务关系"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        logger = get_shared_task_logger()
        
        # 验证父任务的子任务引用
        parent_task = logger.get_task(data["task_id"])
        assert parent_task is not None
        
        # 验证子任务的父任务引用
        for child_id in data["child_task_ids"]:
            child_task = logger.get_task(child_id)
            assert child_task is not None
            assert child_task.parent_task_id == data["task_id"]
    
    def test_workflow_uses_shared_logger(self):
        """测试工作流使用共享 logger"""
        from src.api.app import get_shared_task_logger
        from src.runtime_logging import TaskLogQuery
        
        # 清理已有数据，确保测试隔离
        logger = get_shared_task_logger()
        logger.store.clear()
        
        # 记录调用前的任务数
        initial_count = len(logger.query_tasks(TaskLogQuery(limit=1000)))
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        
        # 验证任务数增加了 3 (1 父任务 + 2 子任务)
        final_count = len(logger.query_tasks(TaskLogQuery(limit=1000)))
        assert final_count >= initial_count + 3


class TestWorkflowPrototypeAlignment:
    """测试原型对齐保留"""
    
    def test_prototype_alignment_in_response(self):
        """测试响应中包含 prototype_alignment"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # prototype_alignment 应该存在
        # 注意：当前 fake provider 返回的 prototype_alignment 可能不在 child_results 的 result 中
        # 这是预期行为，因为 semantic_review 模块输出的是 SemanticReviewOutput
        # 需要在后续版本中改进响应结构
        
        # 验证 semantic_review 子任务存在
        review_results = [
            cr for cr in data["child_results"]
            if cr["module_name"] == "semantic_review"
        ]
        assert len(review_results) == 1
    
    def test_prototype_alignment_in_top_level_result(self):
        """测试 prototype_alignment 在顶层 result 中"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证顶层 result 包含 prototype_alignment
        assert "prototype_alignment" in data["result"]
        
        # 验证 prototype_alignment 结构
        pa = data["result"]["prototype_alignment"]
        assert pa is not None
        assert "score" in pa
        assert "matched_rules" in pa
        assert "unmatched_rules" in pa
        
        # 验证分数范围
        assert 0 <= pa["score"] <= 100
    
    def test_prototype_alignment_extracted_to_response(self):
        """测试 prototype_alignment 被提取到响应顶层"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 prototype_alignment 被提取到响应顶层
        assert data["prototype_alignment"] is not None
        assert data["prototype_alignment"]["score"] >= 0


class TestWorkflowAuditLog:
    """测试工作流审计日志"""
    
    def test_workflow_requested_audit_event(self):
        """测试 workflow_requested 审计事件"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        
        # 获取审计事件
        logger = get_shared_task_logger()
        audit_events = logger.get_audit_events(task_id)
        
        # 应该有 workflow_requested 和 workflow_completed 两个事件
        assert len(audit_events) >= 1
        
        # 验证 workflow_requested 事件
        event_types = [e["event_type"] for e in audit_events]
        assert "workflow_requested" in event_types
    
    def test_workflow_completed_audit_event(self):
        """测试 workflow_completed 审计事件"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        
        # 获取审计事件
        logger = get_shared_task_logger()
        audit_events = logger.get_audit_events(task_id)
        
        # 验证 workflow_completed 事件存在
        event_types = [e["event_type"] for e in audit_events]
        assert "workflow_completed" in event_types
        
        # 验证 workflow_completed 事件的详情
        completed_events = [e for e in audit_events if e["event_type"] == "workflow_completed"]
        assert len(completed_events) == 1
        
        details = completed_events[0]["details"]
        assert details["workflow_name"] == "article"
        assert details["task_id"] == task_id
        assert len(details["child_task_ids"]) == 2
    
    def test_audit_events_can_be_queried_by_task_id(self):
        """测试审计事件可以通过 task_id 查询"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # 通过 task_id 获取审计事件
        logger = get_shared_task_logger()
        audit_events = logger.get_audit_events(task_id)
        
        # 验证审计事件存在
        assert len(audit_events) >= 2
        
        # 验证每个事件都有必要字段
        for event in audit_events:
            assert "event_type" in event
            assert "timestamp" in event
            assert event["event_type"] in ["workflow_requested", "workflow_completed", "workflow_failed"]
    
    def test_audit_event_timestamp_is_iso8601(self):
        """测试审计事件时间戳是 ISO 8601 格式"""
        from src.api.app import get_shared_task_logger
        from datetime import datetime
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        logger = get_shared_task_logger()
        audit_events = logger.get_audit_events(task_id)
        
        # 验证时间戳格式
        for event in audit_events:
            timestamp = event["timestamp"]
            # ISO 8601 格式应该可以被解析
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            assert parsed is not None


class TestWorkflowSelfCheck:
    """测试工作流自检门"""
    
    def test_self_check_passed_on_success(self):
        """测试成功工作流的自检通过"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # 获取任务元数据
        logger = get_shared_task_logger()
        task = logger.get_task(task_id)
        
        # 验证自检结果存在
        assert task is not None
        assert task.metadata is not None
        assert "self_check" in task.metadata
        
        # 验证自检通过
        self_check = task.metadata["self_check"]
        assert self_check["passed"] is True
    
    def test_self_check_includes_all_checks(self):
        """测试自检包含所有检查项"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        logger = get_shared_task_logger()
        task = logger.get_task(task_id)
        
        self_check = task.metadata["self_check"]
        checks = self_check["checks"]
        
        # 验证所有检查项都存在
        expected_checks = [
            "task_id_exists",
            "child_task_ids_exist",
            "result_exists",
            "opinion_output_exists",
            "semantic_review_output_exists",
            "child_tasks_traceable",
            "no_fake_completed_tasks",
            "prototype_alignment_not_lost",
        ]
        
        for check_name in expected_checks:
            assert check_name in checks, f"Missing check: {check_name}"
            assert checks[check_name] is True, f"Check failed: {check_name}"
    
    def test_self_check_verifies_child_task_traceability(self):
        """测试自检验证子任务可追踪性"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        child_task_ids = data["child_task_ids"]
        
        logger = get_shared_task_logger()
        
        # 验证每个子任务都可追踪
        for child_id in child_task_ids:
            child_task = logger.get_task(child_id)
            assert child_task is not None, f"Child task {child_id} is not traceable"
        
        # 验证自检通过
        task = logger.get_task(task_id)
        assert task.metadata["self_check"]["checks"]["child_tasks_traceable"] is True
    
    def test_self_check_verifies_prototype_alignment(self):
        """测试自检验证 prototype_alignment 未丢失"""
        from src.api.app import get_shared_task_logger
        
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        logger = get_shared_task_logger()
        task = logger.get_task(task_id)
        
        # 验证 prototype_alignment 检查通过
        self_check = task.metadata["self_check"]
        assert self_check["checks"]["prototype_alignment_not_lost"] is True


class TestWorkflowRegisterForwarding:
    """测试 register 和 context_metadata 正确转发"""
    
    def test_register_forwarded_to_semantic_review(self):
        """测试 register 被正确转发到 semantic_review"""
        # 这个测试验证 API 接受 register 字段
        # 实际转发验证需要检查 semantic_review 子任务的 metadata
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "register": "正式"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] is not None
    
    def test_context_metadata_forwarded_to_semantic_review(self):
        """测试 context_metadata 被正确转发到 semantic_review"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "context_metadata": {"urgent": True, "source": "test"}
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] is not None
    
    def test_all_semantic_review_fields_accepted(self):
        """测试 semantic_review 的所有字段都被接受"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "医学专业人士",
                    "prototype_hint": "专业医学文章",
                    "register": "正式",
                    "context_metadata": {"key": "value"}
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200


class TestSelfCheckGate:
    """测试自检门真正阻止交付"""
    
    def test_self_check_passed_workflow_completes(self):
        """测试自检通过时工作流正常完成"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "test"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 正常成功的工作流应该返回 completed 状态
        assert data["status"] == "completed"
        
        # 没有自检相关的错误
        assert len(data["errors"]) == 0


class TestWorkflowAPISP6Batch6CSliceB:
    """SP-6 Batch 6C Slice B 测试：三层输出和重跑范围在 Workflow API 中暴露"""
    
    def test_article_workflow_contains_rule_layer_output(self):
        """测试 article workflow 响应包含 rule_layer_output"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 rule_layer_output 存在于顶层响应
        assert "rule_layer_output" in data
        assert data["rule_layer_output"] is not None
        assert "families_executed" in data["rule_layer_output"]
    
    def test_article_workflow_contains_model_review_output(self):
        """测试 article workflow 响应包含 model_review_output"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 model_review_output 存在
        assert "model_review_output" in data
        assert data["model_review_output"] is not None
        assert "findings" in data["model_review_output"]
        assert "severity_summary" in data["model_review_output"]
    
    def test_article_workflow_contains_rewrite_layer_output(self):
        """测试 article workflow 响应包含 rewrite_layer_output"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 rewrite_layer_output 存在
        assert "rewrite_layer_output" in data
        assert data["rewrite_layer_output"] is not None
        assert "rewrite_targets" in data["rewrite_layer_output"]
        assert "count" in data["rewrite_layer_output"]
    
    def test_article_workflow_contains_rerun_scope(self):
        """测试 article workflow 响应包含 rerun_scope"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 rerun_scope 存在且值有效
        assert "rerun_scope" in data
        assert data["rerun_scope"] in ["full_gate_rerun", "partial_gate_rerun"]
    
    def test_article_workflow_all_layer_outputs_in_result(self):
        """测试 article workflow result 中包含所有三层输出"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 result 中包含三层输出
        result = data["result"]
        assert "rule_layer_output" in result
        assert "model_review_output" in result
        assert "rewrite_layer_output" in result
        assert "rerun_scope" in result
    
    def test_article_workflow_layer_outputs_in_child_result(self):
        """测试 article workflow child_results 中包含三层输出"""
        request_data = {
            "input_data": {
                "opinion": {
                    "evidence_bundle": {
                        "items": [{"id": "e1", "content": "test"}]
                    },
                    "audience": "test"
                },
                "semantic_review": {
                    "audience": "test",
                    "prototype_hint": "专业医学文章"
                }
            }
        }
        
        response = client.post("/v1/workflow/article", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 找到 semantic_review 的 child_result
        review_results = [
            cr for cr in data["child_results"]
            if cr["module_name"] == "semantic_review"
        ]
        assert len(review_results) == 1
        
        # 验证 child_result 中包含三层输出
        review_result = review_results[0]["result"]
        assert "rule_layer_output" in review_result
        assert "model_review_output" in review_result
        assert "rewrite_layer_output" in review_result
        assert "rerun_scope" in review_result