"""
Task Log 测试

测试任务日志记录功能。
"""
import pytest
from pydantic import ValidationError

from src.runtime_logging import (
    TaskLogger,
    MemoryTaskLogStore,
    TaskLogEntry,
    TaskLogQuery,
)
from src.contracts.base import TaskStatus, ModuleName


class TestTaskLogEntry:
    """测试 TaskLogEntry"""
    
    def test_entry_with_required_fields(self):
        """测试条目 - 必填字段"""
        entry = TaskLogEntry(
            task_id="test-123",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:00:00+00:00"
        )
        assert entry.task_id == "test-123"
        assert entry.status == TaskStatus.RUNNING
        assert entry.module == ModuleName.OPINION
        assert entry.completed_at is None
    
    def test_entry_with_all_fields(self):
        """测试条目 - 所有字段"""
        entry = TaskLogEntry(
            task_id="test-456",
            status=TaskStatus.COMPLETED,
            module=ModuleName.SEMANTIC_REVIEW,
            input_hash="abc123",
            output_hash="def456",
            parent_task_id="parent-123",
            started_at="2026-03-13T10:00:00+00:00",
            completed_at="2026-03-13T10:01:00+00:00",
            duration_ms=60000,
            metadata={"key": "value"},
            error_message=None
        )
        assert entry.duration_ms == 60000
        assert entry.metadata == {"key": "value"}
    
    def test_entry_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            TaskLogEntry(
                task_id="test",
                status=TaskStatus.RUNNING,
                module=ModuleName.OPINION,
                started_at="2026-03-13T10:00:00+00:00",
                unknown_field="value"
            )


class TestMemoryTaskLogStore:
    """测试 MemoryTaskLogStore"""
    
    @pytest.fixture
    def store(self):
        """创建内存存储实例"""
        return MemoryTaskLogStore()
    
    def test_save_and_get(self, store):
        """测试保存和获取"""
        entry = TaskLogEntry(
            task_id="test-123",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:00:00+00:00"
        )
        
        store.save(entry)
        retrieved = store.get("test-123")
        
        assert retrieved is not None
        assert retrieved.task_id == "test-123"
        assert retrieved.module == ModuleName.OPINION
    
    def test_get_nonexistent(self, store):
        """测试获取不存在的条目"""
        result = store.get("nonexistent")
        assert result is None
    
    def test_query_by_module(self, store):
        """测试按模块查询"""
        # 保存多个条目
        store.save(TaskLogEntry(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:00:00+00:00"
        ))
        store.save(TaskLogEntry(
            task_id="task-2",
            status=TaskStatus.COMPLETED,
            module=ModuleName.SEMANTIC_REVIEW,
            started_at="2026-03-13T10:01:00+00:00"
        ))
        store.save(TaskLogEntry(
            task_id="task-3",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:02:00+00:00"
        ))
        
        results = store.query(TaskLogQuery(module=ModuleName.OPINION))
        
        assert len(results) == 2
        assert all(r.module == ModuleName.OPINION for r in results)
    
    def test_query_by_status(self, store):
        """测试按状态查询"""
        store.save(TaskLogEntry(
            task_id="task-1",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:00:00+00:00"
        ))
        store.save(TaskLogEntry(
            task_id="task-2",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:01:00+00:00"
        ))
        
        results = store.query(TaskLogQuery(status=TaskStatus.RUNNING))
        
        assert len(results) == 1
        assert results[0].task_id == "task-1"
    
    def test_query_limit(self, store):
        """测试查询数量限制"""
        for i in range(10):
            store.save(TaskLogEntry(
                task_id=f"task-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                started_at=f"2026-03-13T10:{i:02d}:00+00:00"
            ))
        
        results = store.query(TaskLogQuery(limit=5))
        
        assert len(results) == 5
    
    def test_query_sort_by_time(self, store):
        """测试按时间排序"""
        store.save(TaskLogEntry(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:00:00+00:00"
        ))
        store.save(TaskLogEntry(
            task_id="task-2",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:02:00+00:00"
        ))
        store.save(TaskLogEntry(
            task_id="task-3",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:01:00+00:00"
        ))
        
        results = store.query(TaskLogQuery())
        
        # 应该是降序排列（最新的在前）
        assert results[0].task_id == "task-2"
        assert results[1].task_id == "task-3"
        assert results[2].task_id == "task-1"
    
    def test_clear(self, store):
        """测试清空"""
        store.save(TaskLogEntry(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-13T10:00:00+00:00"
        ))
        
        assert store.get_count() == 1
        store.clear()
        assert store.get_count() == 0


class TestTaskLogger:
    """测试 TaskLogger"""
    
    @pytest.fixture
    def logger(self):
        """创建 TaskLogger 实例"""
        return TaskLogger()
    
    def test_start_task(self, logger):
        """测试开始任务"""
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_hash="abc123",
            metadata={"source": "test"}
        )
        
        assert task_id is not None
        assert len(task_id) > 0
        
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.status == TaskStatus.RUNNING
        assert entry.module == ModuleName.OPINION
        assert entry.input_hash == "abc123"
        assert entry.metadata == {"source": "test"}
    
    def test_complete_task(self, logger):
        """测试完成任务"""
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_hash="abc123"
        )
        
        logger.complete_task(
            task_id=task_id,
            output_hash="def456",
            duration_ms=5000,
            metadata={"result": "success"}
        )
        
        entry = logger.get_task(task_id)
        assert entry.status == TaskStatus.COMPLETED
        assert entry.output_hash == "def456"
        assert entry.duration_ms == 5000
        assert entry.completed_at is not None
        assert entry.metadata == {"result": "success"}
    
    def test_fail_task(self, logger):
        """测试任务失败"""
        task_id = logger.start_task(
            module=ModuleName.SEMANTIC_REVIEW,
            input_hash="abc123"
        )
        
        logger.fail_task(
            task_id=task_id,
            error_message="LLM 调用失败",
            duration_ms=3000,
            metadata={"retry_count": 3}
        )
        
        entry = logger.get_task(task_id)
        assert entry.status == TaskStatus.FAILED
        assert entry.error_message == "LLM 调用失败"
        assert entry.duration_ms == 3000
        assert entry.metadata == {"retry_count": 3}
    
    def test_complete_nonexistent_task(self, logger):
        """测试完成不存在的任务（不应抛异常）"""
        logger.complete_task("nonexistent", output_hash="abc")
        # 不应抛异常
    
    def test_get_tasks_by_module(self, logger):
        """测试按模块获取任务"""
        logger.start_task(module=ModuleName.OPINION)
        logger.start_task(module=ModuleName.SEMANTIC_REVIEW)
        logger.start_task(module=ModuleName.OPINION)
        
        results = logger.get_tasks_by_module(ModuleName.OPINION)
        
        assert len(results) == 2
        assert all(r.module == ModuleName.OPINION for r in results)


class TestTaskLoggerIntegration:
    """测试 TaskLogger 集成场景"""
    
    def test_full_task_lifecycle(self):
        """测试完整任务生命周期"""
        logger = TaskLogger()
        
        # 父任务
        parent_id = logger.start_task(
            module=ModuleName.ORCHESTRATOR,
            metadata={"workflow": "opinion_generation"}
        )
        
        # 子任务
        child_id = logger.start_task(
            module=ModuleName.OPINION,
            parent_task_id=parent_id,
            input_hash="input_hash"
        )
        
        # 完成子任务
        logger.complete_task(
            task_id=child_id,
            output_hash="output_hash",
            duration_ms=10000
        )
        
        # 完成父任务
        logger.complete_task(
            task_id=parent_id,
            duration_ms=12000
        )
        
        # 查询子任务
        child_results = logger.query_tasks(TaskLogQuery(parent_task_id=parent_id))
        assert len(child_results) == 1
        assert child_results[0].task_id == child_id
        
        # 验证状态
        parent_entry = logger.get_task(parent_id)
        child_entry = logger.get_task(child_id)
        
        assert parent_entry.status == TaskStatus.COMPLETED
        assert child_entry.status == TaskStatus.COMPLETED
        assert child_entry.parent_task_id == parent_id