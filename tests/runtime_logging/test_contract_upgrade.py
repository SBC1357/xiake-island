"""
契约升级验证测试

验证 2B-0 日志契约升级的完整性：
1. TaskLogEntry 新增字段正确
2. input_hash 自动计算
3. input_data/output_data 完整存储
4. child_task_ids 正确记录
"""
import pytest
from src.runtime_logging import (
    TaskLogger,
    TaskLogEntry,
    TaskLogQuery,
    MemoryTaskLogStore,
    compute_input_hash,
)
from src.runtime_logging.hash_utils import _filter_sensitive_fields
from src.contracts.base import TaskStatus, ModuleName


class TestHashUtils:
    """测试哈希工具函数"""
    
    def test_compute_input_hash_deterministic(self):
        """相同输入产生相同哈希"""
        input_data = {"audience": "医生", "content": "测试内容"}
        hash1 = compute_input_hash(input_data)
        hash2 = compute_input_hash(input_data)
        assert hash1 == hash2
        assert len(hash1) == 16
    
    def test_compute_input_hash_different_for_different_input(self):
        """不同输入产生不同哈希"""
        input1 = {"audience": "医生", "content": "测试内容1"}
        input2 = {"audience": "医生", "content": "测试内容2"}
        hash1 = compute_input_hash(input1)
        hash2 = compute_input_hash(input2)
        assert hash1 != hash2
    
    def test_compute_input_hash_key_order_independent(self):
        """键顺序不影响哈希"""
        input1 = {"a": 1, "b": 2}
        input2 = {"b": 2, "a": 1}
        assert compute_input_hash(input1) == compute_input_hash(input2)
    
    def test_filter_sensitive_fields(self):
        """过滤敏感字段"""
        data = {
            "audience": "医生",
            "api_key": "secret-key",
            "password": "secret-pass",
            "content": "正常内容"
        }
        filtered = _filter_sensitive_fields(data)
        assert "api_key" not in filtered
        assert "password" not in filtered
        assert filtered["audience"] == "医生"
        assert filtered["content"] == "正常内容"
    
    def test_compute_input_hash_filters_sensitive(self):
        """哈希计算会过滤敏感字段"""
        data1 = {"content": "测试", "api_key": "key1"}
        data2 = {"content": "测试", "api_key": "key2"}
        # 敏感字段被过滤，所以哈希应该相同
        assert compute_input_hash(data1) == compute_input_hash(data2)


class TestTaskLogEntryUpgrade:
    """测试 TaskLogEntry 模型升级"""
    
    def test_task_log_entry_has_input_data(self):
        """TaskLogEntry 有 input_data 字段"""
        entry = TaskLogEntry(
            task_id="test-123",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            input_data={"audience": "医生"},
            started_at="2026-03-16T00:00:00Z"
        )
        assert entry.input_data == {"audience": "医生"}
    
    def test_task_log_entry_has_output_data(self):
        """TaskLogEntry 有 output_data 字段"""
        entry = TaskLogEntry(
            task_id="test-123",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            output_data={"thesis": {"statement": "测试"}},
            started_at="2026-03-16T00:00:00Z",
            completed_at="2026-03-16T00:00:01Z"
        )
        assert entry.output_data == {"thesis": {"statement": "测试"}}
    
    def test_task_log_entry_has_child_task_ids(self):
        """TaskLogEntry 有 child_task_ids 字段"""
        entry = TaskLogEntry(
            task_id="parent-123",
            status=TaskStatus.COMPLETED,
            module=ModuleName.ORCHESTRATOR,
            child_task_ids=["child-1", "child-2"],
            started_at="2026-03-16T00:00:00Z",
            completed_at="2026-03-16T00:00:01Z"
        )
        assert entry.child_task_ids == ["child-1", "child-2"]
    
    def test_task_log_entry_child_task_ids_default_empty(self):
        """child_task_ids 默认为空列表"""
        entry = TaskLogEntry(
            task_id="test-123",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            started_at="2026-03-16T00:00:00Z"
        )
        assert entry.child_task_ids == []
    
    def test_task_log_entry_backward_compatible(self):
        """向后兼容：不传新字段也能正常工作"""
        # 模拟旧代码的调用方式
        entry = TaskLogEntry(
            task_id="test-123",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            input_hash="abc123",
            started_at="2026-03-16T00:00:00Z"
        )
        assert entry.task_id == "test-123"
        assert entry.input_hash == "abc123"
        assert entry.input_data is None
        assert entry.output_data is None
        assert entry.child_task_ids == []


class TestTaskLoggerUpgrade:
    """测试 TaskLogger 接口升级"""
    
    def test_start_task_with_input_data_auto_compute_hash(self):
        """start_task 传入 input_data 时自动计算 input_hash"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        input_data = {"audience": "医生", "content": "测试"}
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data
        )
        
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.input_data == input_data
        assert entry.input_hash is not None
        assert len(entry.input_hash) == 16
    
    def test_start_task_without_input_data_no_hash(self):
        """start_task 不传 input_data 时 input_hash 为 None"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        task_id = logger.start_task(module=ModuleName.OPINION)
        
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.input_data is None
        assert entry.input_hash is None
    
    def test_complete_task_with_output_data(self):
        """complete_task 传入 output_data 被正确存储"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        task_id = logger.start_task(module=ModuleName.OPINION)
        
        output_data = {"thesis": {"statement": "测试观点"}}
        logger.complete_task(task_id, output_data=output_data)
        
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.output_data == output_data
        assert entry.status == TaskStatus.COMPLETED
    
    def test_complete_task_with_child_task_ids(self):
        """complete_task 传入 child_task_ids 被正确存储"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        task_id = logger.start_task(module=ModuleName.ORCHESTRATOR)
        
        child_ids = ["child-1", "child-2"]
        logger.complete_task(task_id, child_task_ids=child_ids)
        
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.child_task_ids == child_ids
    
    def test_get_tasks_by_input_hash(self):
        """可以按 input_hash 查询任务"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        input_data = {"audience": "医生", "content": "测试"}
        
        # 创建多个相同参数的任务
        task_id1 = logger.start_task(module=ModuleName.OPINION, input_data=input_data)
        logger.complete_task(task_id1)
        
        task_id2 = logger.start_task(module=ModuleName.OPINION, input_data=input_data)
        logger.complete_task(task_id2)
        
        # 创建不同参数的任务
        task_id3 = logger.start_task(
            module=ModuleName.OPINION,
            input_data={"audience": "患者", "content": "测试"}
        )
        logger.complete_task(task_id3)
        
        # 按哈希查询
        hash_value = compute_input_hash(input_data)
        results = logger.get_tasks_by_input_hash(hash_value)
        
        assert len(results) == 2
        task_ids = [r.task_id for r in results]
        assert task_id1 in task_ids
        assert task_id2 in task_ids
        assert task_id3 not in task_ids


class TestIntegration:
    """集成测试：验证完整流程"""
    
    def test_full_opinion_task_lifecycle(self):
        """完整的 opinion 任务生命周期"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        # 开始任务
        input_data = {
            "audience": "医学专业人士",
            "evidence_bundle": {
                "items": [{"id": "e1", "content": "证据内容"}],
                "summary": "证据摘要"
            }
        }
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data
        )
        
        # 验证开始状态
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.status == TaskStatus.RUNNING
        assert entry.input_data == input_data
        assert entry.input_hash is not None
        
        # 完成任务
        output_data = {
            "thesis": {"statement": "测试观点", "confidence": 0.85},
            "support_points": [{"content": "支撑点1", "strength": "strong"}]
        }
        logger.complete_task(task_id, output_data=output_data)
        
        # 验证完成状态
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.status == TaskStatus.COMPLETED
        assert entry.output_data == output_data
    
    def test_workflow_with_child_tasks(self):
        """工作流场景：父任务记录子任务ID"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        # 开始父任务
        parent_id = logger.start_task(
            module=ModuleName.ORCHESTRATOR,
            input_data={"mode": "workflow", "workflow_name": "article"}
        )
        
        # 创建子任务
        opinion_input = {"audience": "医生"}
        opinion_task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data=opinion_input,
            parent_task_id=parent_id
        )
        logger.complete_task(opinion_task_id, output_data={"thesis": {}})
        
        review_input = {"content": "审核内容"}
        review_task_id = logger.start_task(
            module=ModuleName.SEMANTIC_REVIEW,
            input_data=review_input,
            parent_task_id=parent_id
        )
        logger.complete_task(review_task_id, output_data={"passed": True})
        
        # 完成父任务
        logger.complete_task(
            parent_id,
            child_task_ids=[opinion_task_id, review_task_id]
        )
        
        # 验证父任务
        parent_entry = logger.get_task(parent_id)
        assert parent_entry is not None
        assert parent_entry.child_task_ids == [opinion_task_id, review_task_id]
        
        # 验证子任务的 parent_task_id
        opinion_entry = logger.get_task(opinion_task_id)
        assert opinion_entry is not None
        assert opinion_entry.parent_task_id == parent_id
    
    def test_query_by_input_hash_returns_versions(self):
        """按 input_hash 查询返回同一参数的多个版本"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        input_data = {"audience": "医生", "content": "测试"}
        
        # 执行3次相同参数的任务
        task_ids = []
        for i in range(3):
            task_id = logger.start_task(
                module=ModuleName.OPINION,
                input_data=input_data
            )
            logger.complete_task(task_id, output_data={"version": i})
            task_ids.append(task_id)
        
        # 按哈希查询
        hash_value = compute_input_hash(input_data)
        results = logger.get_tasks_by_input_hash(hash_value)
        
        assert len(results) == 3
        # 按时间倒序
        result_ids = [r.task_id for r in results]
        assert result_ids == list(reversed(task_ids))


class TestBackwardCompatibility:
    """向后兼容性测试"""
    
    def test_old_start_task_signature_still_works(self):
        """旧的 start_task 签名仍然可用"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        # 旧签名：不传 input_data
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_hash="manual-hash",
            metadata={"key": "value"}
        )
        
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.input_hash == "manual-hash"
        assert entry.metadata == {"key": "value"}
    
    def test_old_complete_task_signature_still_works(self):
        """旧的 complete_task 签名仍然可用"""
        store = MemoryTaskLogStore()
        logger = TaskLogger(store)
        
        task_id = logger.start_task(module=ModuleName.OPINION)
        
        # 旧签名：不传 output_data, child_task_ids
        logger.complete_task(
            task_id=task_id,
            metadata={"confidence": 0.85}
        )
        
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.status == TaskStatus.COMPLETED
        assert entry.output_data is None
        assert entry.child_task_ids == []