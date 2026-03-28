"""
Tests for Audit Events

测试审计事件功能。
"""
import pytest
from datetime import datetime

from src.runtime_logging import TaskLogger, MemoryTaskLogStore
from src.runtime_logging.audit_events import (
    create_audit_event,
    feedback_submitted,
    task_rerun,
    task_viewed,
)
from src.contracts.base import ModuleName


class TestAuditEventTypes:
    """测试审计事件类型"""

    def test_create_audit_event(self):
        """创建基本审计事件"""
        event = create_audit_event(
            event_type="task_viewed",
            actor="user123",
            details={"task_id": "test-task"}
        )
        
        assert event.event_type == "task_viewed"
        assert event.actor == "user123"
        assert event.details["task_id"] == "test-task"
        assert event.timestamp is not None

    def test_feedback_submitted_event(self):
        """创建反馈提交事件"""
        event = feedback_submitted(
            task_id="task-123",
            rating=5,
            comment="非常好",
            actor="reviewer1"
        )
        
        assert event.event_type == "feedback_submitted"
        assert event.actor == "reviewer1"
        assert event.details["task_id"] == "task-123"
        assert event.details["rating"] == 5
        assert event.details["comment"] == "非常好"

    def test_task_rerun_event(self):
        """创建任务重跑事件"""
        event = task_rerun(
            original_task_id="task-1",
            new_task_id="task-2",
            actor="user1"
        )
        
        assert event.event_type == "task_rerun"
        assert event.details["original_task_id"] == "task-1"
        assert event.details["new_task_id"] == "task-2"

    def test_task_viewed_event(self):
        """创建任务查看事件"""
        event = task_viewed(task_id="task-123", actor="viewer1")
        
        assert event.event_type == "task_viewed"
        assert event.actor == "viewer1"
        assert event.details["task_id"] == "task-123"


class TestTaskLoggerAuditEvents:
    """测试 TaskLogger 的审计事件功能"""

    @pytest.fixture
    def logger(self):
        """创建测试用的 TaskLogger"""
        return TaskLogger(MemoryTaskLogStore())

    def test_save_audit_event(self, logger):
        """保存审计事件"""
        task_id = logger.start_task(module=ModuleName.OPINION)
        
        logger.save_audit_event(
            task_id=task_id,
            event_type="feedback_submitted",
            timestamp=datetime.now().isoformat(),
            actor="user1",
            details={"rating": 5}
        )
        
        events = logger.get_audit_events(task_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "feedback_submitted"
        assert events[0]["actor"] == "user1"

    def test_multiple_audit_events(self, logger):
        """保存多个审计事件"""
        task_id = logger.start_task(module=ModuleName.OPINION)
        
        logger.save_audit_event(
            task_id=task_id,
            event_type="task_viewed",
            timestamp=datetime.now().isoformat(),
            actor="user1"
        )
        
        logger.save_audit_event(
            task_id=task_id,
            event_type="feedback_submitted",
            timestamp=datetime.now().isoformat(),
            actor="user1",
            details={"rating": 4}
        )
        
        events = logger.get_audit_events(task_id)
        assert len(events) == 2

    def test_audit_events_nonexistent_task(self, logger):
        """获取不存在任务的审计事件"""
        events = logger.get_audit_events("nonexistent-task")
        assert events == []


class TestAuditEventsWithSQLite:
    """测试 SQLite 存储的审计事件"""

    @pytest.fixture
    def logger(self):
        """创建使用 SQLite 存储的 TaskLogger"""
        from src.runtime_logging import SQLiteTaskLogStore
        import tempfile
        import os
        
        # 使用临时文件
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_audit.db")
        
        store = SQLiteTaskLogStore(db_path)
        return TaskLogger(store)

    def test_save_and_get_audit_event_sqlite(self, logger):
        """SQLite 存储：保存和获取审计事件"""
        task_id = logger.start_task(module=ModuleName.OPINION)
        
        logger.save_audit_event(
            task_id=task_id,
            event_type="feedback_submitted",
            timestamp=datetime.now().isoformat(),
            actor="reviewer",
            details={"rating": 5, "comment": "excellent"}
        )
        
        events = logger.get_audit_events(task_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "feedback_submitted"
        assert events[0]["actor"] == "reviewer"
        assert events[0]["details"]["rating"] == 5