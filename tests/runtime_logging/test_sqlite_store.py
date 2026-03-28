"""
SQLite 任务日志存储测试

验证 SQLiteTaskLogStore 的正确性：
1. 任务持久化存储
2. 服务重启后数据不丢失
3. 审计事件独立存储
"""
import os
import tempfile
import pytest
from pathlib import Path

from src.runtime_logging.sqlite_store import SQLiteTaskLogStore
from src.runtime_logging import TaskLogger, TaskLogEntry, TaskLogQuery
from src.contracts.base import TaskStatus, ModuleName


class TestSQLiteTaskLogStore:
    """测试 SQLiteTaskLogStore"""
    
    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield str(Path(tmpdir) / "test_tasks.db")
    
    @pytest.fixture
    def store(self, temp_db_path):
        """创建存储实例"""
        store = SQLiteTaskLogStore(temp_db_path)
        yield store
        store.close()
    
    def test_init_creates_tables(self, temp_db_path):
        """初始化时创建表"""
        store = SQLiteTaskLogStore(temp_db_path)
        
        # 检查表是否存在
        import sqlite3
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        assert cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_events'")
        assert cursor.fetchone() is not None
        
        conn.close()
        store.close()
    
    def test_save_and_get(self, store):
        """保存和获取任务"""
        entry = TaskLogEntry(
            task_id="test-123",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            input_hash="abc123",
            input_data={"audience": "医生"},
            started_at="2026-03-16T00:00:00Z"
        )
        
        store.save(entry)
        
        result = store.get("test-123")
        assert result is not None
        assert result.task_id == "test-123"
        assert result.status == TaskStatus.RUNNING
        assert result.module == ModuleName.OPINION
        assert result.input_hash == "abc123"
        assert result.input_data == {"audience": "医生"}
    
    def test_get_nonexistent(self, store):
        """获取不存在的任务返回 None"""
        result = store.get("nonexistent")
        assert result is None
    
    def test_save_with_all_fields(self, store):
        """保存包含所有字段的任务"""
        entry = TaskLogEntry(
            task_id="full-task",
            status=TaskStatus.COMPLETED,
            module=ModuleName.ORCHESTRATOR,
            input_hash="hash123",
            input_data={"key": "value"},
            output_data={"result": "success"},
            parent_task_id="parent-123",
            child_task_ids=["child-1", "child-2"],
            started_at="2026-03-16T00:00:00Z",
            completed_at="2026-03-16T00:00:01Z",
            duration_ms=1000,
            metadata={"meta_key": "meta_value"},
            error_message=None
        )
        
        store.save(entry)
        
        result = store.get("full-task")
        assert result is not None
        assert result.output_data == {"result": "success"}
        assert result.child_task_ids == ["child-1", "child-2"]
        assert result.parent_task_id == "parent-123"
        assert result.duration_ms == 1000
        assert result.metadata == {"meta_key": "meta_value"}
    
    def test_update_task(self, store):
        """更新任务状态"""
        # 创建初始任务
        entry = TaskLogEntry(
            task_id="update-test",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION,
            input_data={"audience": "医生"},
            started_at="2026-03-16T00:00:00Z"
        )
        store.save(entry)
        
        # 更新任务
        updated_entry = TaskLogEntry(
            task_id="update-test",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            input_data={"audience": "医生"},
            output_data={"thesis": {"statement": "观点"}},
            started_at="2026-03-16T00:00:00Z",
            completed_at="2026-03-16T00:00:01Z",
            duration_ms=1000
        )
        store.save(updated_entry)
        
        result = store.get("update-test")
        assert result is not None
        assert result.status == TaskStatus.COMPLETED
        assert result.output_data == {"thesis": {"statement": "观点"}}
    
    def test_query_by_module(self, store):
        """按模块查询"""
        # 创建多个任务
        for i in range(3):
            entry = TaskLogEntry(
                task_id=f"opinion-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                started_at=f"2026-03-16T00:00:0{i}Z"
            )
            store.save(entry)
        
        for i in range(2):
            entry = TaskLogEntry(
                task_id=f"review-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.SEMANTIC_REVIEW,
                started_at=f"2026-03-16T00:00:1{i}Z"
            )
            store.save(entry)
        
        # 查询 opinion 模块
        results = store.query(TaskLogQuery(module=ModuleName.OPINION))
        assert len(results) == 3
        
        # 查询 semantic_review 模块
        results = store.query(TaskLogQuery(module=ModuleName.SEMANTIC_REVIEW))
        assert len(results) == 2
    
    def test_query_by_status(self, store):
        """按状态查询"""
        for i in range(3):
            entry = TaskLogEntry(
                task_id=f"task-{i}",
                status=TaskStatus.COMPLETED if i < 2 else TaskStatus.FAILED,
                module=ModuleName.OPINION,
                started_at=f"2026-03-16T00:00:0{i}Z"
            )
            store.save(entry)
        
        results = store.query(TaskLogQuery(status=TaskStatus.COMPLETED))
        assert len(results) == 2
        
        results = store.query(TaskLogQuery(status=TaskStatus.FAILED))
        assert len(results) == 1
    
    def test_query_by_parent_task_id(self, store):
        """按父任务ID查询"""
        # 创建父任务
        parent = TaskLogEntry(
            task_id="parent-1",
            status=TaskStatus.COMPLETED,
            module=ModuleName.ORCHESTRATOR,
            started_at="2026-03-16T00:00:00Z"
        )
        store.save(parent)
        
        # 创建子任务
        for i in range(2):
            child = TaskLogEntry(
                task_id=f"child-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                parent_task_id="parent-1",
                started_at=f"2026-03-16T00:00:0{i}Z"
            )
            store.save(child)
        
        results = store.query(TaskLogQuery(parent_task_id="parent-1"))
        assert len(results) == 2
    
    def test_query_by_input_hash(self, store):
        """按 input_hash 查询"""
        for i in range(3):
            entry = TaskLogEntry(
                task_id=f"hash-task-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                input_hash="same-hash" if i < 2 else "different-hash",
                started_at=f"2026-03-16T00:00:0{i}Z"
            )
            store.save(entry)
        
        results = store.query(TaskLogQuery(input_hash="same-hash"))
        assert len(results) == 2
    
    def test_query_limit(self, store):
        """查询限制数量"""
        for i in range(10):
            entry = TaskLogEntry(
                task_id=f"limit-task-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                started_at=f"2026-03-16T00:00:{i:02d}Z"
            )
            store.save(entry)
        
        results = store.query(TaskLogQuery(limit=5))
        assert len(results) == 5
    
    def test_query_sort_by_time_desc(self, store):
        """查询结果按时间降序"""
        for i in range(3):
            entry = TaskLogEntry(
                task_id=f"sort-task-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                started_at=f"2026-03-16T00:00:0{i}Z"
            )
            store.save(entry)
        
        results = store.query(TaskLogQuery())
        assert results[0].task_id == "sort-task-2"
        assert results[1].task_id == "sort-task-1"
        assert results[2].task_id == "sort-task-0"
    
    def test_clear(self, store):
        """清空日志"""
        entry = TaskLogEntry(
            task_id="clear-test",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            started_at="2026-03-16T00:00:00Z"
        )
        store.save(entry)
        
        assert store.get_count() == 1
        
        store.clear()
        
        assert store.get_count() == 0
    
    def test_get_count(self, store):
        """获取日志数量"""
        assert store.get_count() == 0
        
        for i in range(5):
            entry = TaskLogEntry(
                task_id=f"count-task-{i}",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                started_at=f"2026-03-16T00:00:0{i}Z"
            )
            store.save(entry)
        
        assert store.get_count() == 5
    
    def test_empty_dict_round_trip(self, store):
        """空字典 {} 在保存和读取后保持为 {} 而非 None"""
        # 测试 input_data={} 和 output_data={}
        entry = TaskLogEntry(
            task_id="empty-dict-test",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            input_data={},
            output_data={},
            started_at="2026-03-16T00:00:00Z"
        )
        
        store.save(entry)
        result = store.get("empty-dict-test")
        
        assert result is not None
        assert result.input_data == {}, f"Expected {{}} but got {result.input_data}"
        assert result.output_data == {}, f"Expected {{}} but got {result.output_data}"
    
    def test_none_vs_empty_dict_distinction(self, store):
        """区分 None 和 {} 是不同的值"""
        # None 值
        entry_none = TaskLogEntry(
            task_id="none-test",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            input_data=None,
            output_data=None,
            started_at="2026-03-16T00:00:00Z"
        )
        store.save(entry_none)
        
        # 空字典
        entry_empty = TaskLogEntry(
            task_id="empty-test",
            status=TaskStatus.COMPLETED,
            module=ModuleName.OPINION,
            input_data={},
            output_data={},
            started_at="2026-03-16T00:00:01Z"
        )
        store.save(entry_empty)
        
        result_none = store.get("none-test")
        result_empty = store.get("empty-test")
        
        assert result_none.input_data is None
        assert result_none.output_data is None
        assert result_empty.input_data == {}
        assert result_empty.output_data == {}


class TestSQLiteAuditEvents:
    """测试审计事件存储"""
    
    @pytest.fixture
    def store(self):
        """创建存储实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test_audit.db")
            store = SQLiteTaskLogStore(db_path)
            yield store
            store.close()
    
    def test_save_and_get_audit_event(self, store):
        """保存和获取审计事件"""
        # 创建任务
        entry = TaskLogEntry(
            task_id="audit-task",
            status=TaskStatus.COMPLETED,
            module=ModuleName.ORCHESTRATOR,
            started_at="2026-03-16T00:00:00Z"
        )
        store.save(entry)
        
        # 保存审计事件
        store.save_audit_event(
            task_id="audit-task",
            event_type="workflow_completed",
            timestamp="2026-03-16T00:00:01Z",
            details={"workflow_name": "article", "passed": True}
        )
        
        # 获取审计事件
        events = store.get_audit_events("audit-task")
        assert len(events) == 1
        assert events[0]["event_type"] == "workflow_completed"
        assert events[0]["details"]["workflow_name"] == "article"
    
    def test_multiple_audit_events(self, store):
        """多个审计事件"""
        entry = TaskLogEntry(
            task_id="multi-audit",
            status=TaskStatus.COMPLETED,
            module=ModuleName.ORCHESTRATOR,
            started_at="2026-03-16T00:00:00Z"
        )
        store.save(entry)
        
        # 保存多个事件
        store.save_audit_event(
            task_id="multi-audit",
            event_type="workflow_requested",
            timestamp="2026-03-16T00:00:00Z"
        )
        store.save_audit_event(
            task_id="multi-audit",
            event_type="workflow_completed",
            timestamp="2026-03-16T00:00:02Z"
        )
        
        events = store.get_audit_events("multi-audit")
        assert len(events) == 2


class TestSQLitePersistence:
    """测试持久化特性"""
    
    def test_data_survives_reconnect(self):
        """数据在重新连接后仍然存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "persist.db")
            
            # 第一次连接：保存数据
            store1 = SQLiteTaskLogStore(db_path)
            entry = TaskLogEntry(
                task_id="persist-test",
                status=TaskStatus.COMPLETED,
                module=ModuleName.OPINION,
                input_data={"key": "value"},
                output_data={"result": "success"},
                started_at="2026-03-16T00:00:00Z",
                completed_at="2026-03-16T00:00:01Z"
            )
            store1.save(entry)
            store1.close()
            
            # 第二次连接：验证数据
            store2 = SQLiteTaskLogStore(db_path)
            result = store2.get("persist-test")
            assert result is not None
            assert result.input_data == {"key": "value"}
            assert result.output_data == {"result": "success"}
            store2.close()
    
    def test_environment_variable_config(self):
        """环境变量配置数据目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 设置环境变量
            old_env = os.environ.get("XIAGEDAO_DATA_DIR")
            os.environ["XIAGEDAO_DATA_DIR"] = tmpdir
            
            try:
                store = SQLiteTaskLogStore()  # 使用默认路径
                
                entry = TaskLogEntry(
                    task_id="env-test",
                    status=TaskStatus.COMPLETED,
                    module=ModuleName.OPINION,
                    started_at="2026-03-16T00:00:00Z"
                )
                store.save(entry)
                
                # 验证数据库文件在指定目录
                db_file = Path(tmpdir) / "tasks.db"
                assert db_file.exists()
                
                store.close()
            finally:
                if old_env is not None:
                    os.environ["XIAGEDAO_DATA_DIR"] = old_env
                else:
                    os.environ.pop("XIAGEDAO_DATA_DIR", None)

    def test_runtime_root_environment_config(self):
        """环境变量配置运行态根目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_runtime_root = os.environ.get("XIAGEDAO_RUNTIME_ROOT")
            old_data_dir = os.environ.get("XIAGEDAO_DATA_DIR")
            os.environ["XIAGEDAO_RUNTIME_ROOT"] = tmpdir
            os.environ.pop("XIAGEDAO_DATA_DIR", None)

            try:
                store = SQLiteTaskLogStore()

                entry = TaskLogEntry(
                    task_id="runtime-root-test",
                    status=TaskStatus.COMPLETED,
                    module=ModuleName.OPINION,
                    started_at="2026-03-16T00:00:00Z"
                )
                store.save(entry)

                db_file = Path(tmpdir) / "data" / "tasks.db"
                assert db_file.exists()

                store.close()
            finally:
                if old_runtime_root is not None:
                    os.environ["XIAGEDAO_RUNTIME_ROOT"] = old_runtime_root
                else:
                    os.environ.pop("XIAGEDAO_RUNTIME_ROOT", None)

                if old_data_dir is not None:
                    os.environ["XIAGEDAO_DATA_DIR"] = old_data_dir
                else:
                    os.environ.pop("XIAGEDAO_DATA_DIR", None)


class TestTaskLoggerWithSQLite:
    """测试 TaskLogger 与 SQLiteTaskLogStore 集成"""
    
    @pytest.fixture
    def logger(self):
        """创建使用 SQLite 存储的 TaskLogger"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "integration.db")
            store = SQLiteTaskLogStore(db_path)
            logger = TaskLogger(store)
            yield logger
            store.close()
    
    def test_full_lifecycle_with_sqlite(self, logger):
        """完整的任务生命周期"""
        # 开始任务
        input_data = {"audience": "医生", "content": "测试"}
        task_id = logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data
        )
        
        # 验证开始状态
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.status == TaskStatus.RUNNING
        assert entry.input_data == input_data
        
        # 完成任务
        output_data = {"thesis": {"statement": "观点"}}
        logger.complete_task(task_id, output_data=output_data)
        
        # 验证完成状态
        entry = logger.get_task(task_id)
        assert entry is not None
        assert entry.status == TaskStatus.COMPLETED
        assert entry.output_data == output_data
    
    def test_query_tasks_with_sqlite(self, logger):
        """查询任务"""
        # 创建多个任务
        for i in range(5):
            task_id = logger.start_task(
                module=ModuleName.OPINION,
                input_data={"index": i}
            )
            logger.complete_task(task_id)
        
        # 查询
        results = logger.query_tasks(TaskLogQuery(module=ModuleName.OPINION))
        assert len(results) == 5
    
    def test_get_tasks_by_input_hash_with_sqlite(self, logger):
        """按 input_hash 查询"""
        input_data = {"audience": "医生"}
        
        # 创建相同参数的多个任务
        for _ in range(3):
            task_id = logger.start_task(
                module=ModuleName.OPINION,
                input_data=input_data
            )
            logger.complete_task(task_id)
        
        # 按 hash 查询
        from src.runtime_logging import compute_input_hash
        hash_value = compute_input_hash(input_data)
        results = logger.get_tasks_by_input_hash(hash_value)
        
        assert len(results) == 3
