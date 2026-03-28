"""
SQLite 任务日志存储

持久化任务日志存储实现，使用 SQLite 数据库。
"""
import json
import sqlite3
from threading import Lock
from typing import Optional, List

from .store import TaskLogStore
from .models import TaskLogEntry, TaskLogQuery
from src.contracts.base import TaskStatus
from src.runtime_paths import get_runtime_data_dir, get_task_db_path


class SQLiteTaskLogStore(TaskLogStore):
    """
    SQLite 任务日志存储
    
    持久化任务日志，支持：
    - 任务主记录存储 (tasks 表)
    - 审计事件存储 (audit_events 表)
    - 服务重启后数据不丢失
    
    Attributes:
        db_path: 数据库文件路径
        _conn: 数据库连接
        _lock: 线程锁
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化 SQLite 存储
        
        Args:
            db_path: 数据库文件路径，默认使用运行态目录下的 tasks.db
                     可通过环境变量 XIAGEDAO_DATA_DIR 配置目录
        """
        if db_path is None:
            data_dir = get_runtime_data_dir()
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(get_task_db_path())
        
        self.db_path = db_path
        self._lock = Lock()
        self._conn = self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        # check_same_thread=False 允许跨线程使用（FastAPI 异步场景需要）
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def _init_db(self) -> sqlite3.Connection:
        """
        初始化数据库表结构
        
        Returns:
            数据库连接
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 创建 tasks 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                module TEXT NOT NULL,
                input_hash TEXT,
                input_data TEXT,
                output_data TEXT,
                parent_task_id TEXT,
                child_task_ids TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms INTEGER,
                metadata TEXT,
                error_message TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_module ON tasks(module)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_input_hash ON tasks(input_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_started_at ON tasks(started_at)")
        
        # 创建 audit_events 表（独立存储）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                actor TEXT,
                details TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
        """)
        
        # 创建审计事件索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_task_id ON audit_events(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp)")
        
        conn.commit()
        return conn
    
    def save(self, entry: TaskLogEntry) -> None:
        """
        保存任务日志条目
        
        Args:
            entry: 任务日志条目
        """
        with self._lock:
            cursor = self._conn.cursor()
            
            # 序列化 JSON 字段（使用 is not None 检查，保留空字典 {}）
            input_data_json = json.dumps(entry.input_data, ensure_ascii=False) if entry.input_data is not None else None
            output_data_json = json.dumps(entry.output_data, ensure_ascii=False) if entry.output_data is not None else None
            child_task_ids_json = json.dumps(entry.child_task_ids, ensure_ascii=False) if entry.child_task_ids else "[]"
            metadata_json = json.dumps(entry.metadata, ensure_ascii=False) if entry.metadata else None
            
            # 使用 UPSERT（INSERT OR REPLACE）
            cursor.execute("""
                INSERT OR REPLACE INTO tasks (
                    task_id, status, module, input_hash, input_data, output_data,
                    parent_task_id, child_task_ids, started_at, completed_at,
                    duration_ms, metadata, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.task_id,
                entry.status.value,
                entry.module.value,
                entry.input_hash,
                input_data_json,
                output_data_json,
                entry.parent_task_id,
                child_task_ids_json,
                entry.started_at,
                entry.completed_at,
                entry.duration_ms,
                metadata_json,
                entry.error_message
            ))
            
            self._conn.commit()
    
    def get(self, task_id: str) -> Optional[TaskLogEntry]:
        """
        获取指定任务ID的日志条目
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务日志条目，不存在则返回 None
        """
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_entry(row)
    
    def query(self, query: TaskLogQuery) -> List[TaskLogEntry]:
        """
        查询任务日志
        
        Args:
            query: 查询条件
            
        Returns:
            任务日志条目列表
        """
        with self._lock:
            cursor = self._conn.cursor()
            
            # 构建查询条件
            conditions = []
            params = []
            
            if query.task_id:
                conditions.append("task_id = ?")
                params.append(query.task_id)
            if query.module:
                conditions.append("module = ?")
                params.append(query.module.value)
            if query.status:
                conditions.append("status = ?")
                params.append(query.status.value)
            if query.parent_task_id:
                conditions.append("parent_task_id = ?")
                params.append(query.parent_task_id)
            if query.input_hash:
                conditions.append("input_hash = ?")
                params.append(query.input_hash)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            sql = f"""
                SELECT * FROM tasks 
                WHERE {where_clause}
                ORDER BY started_at DESC
                LIMIT ?
            """
            params.append(query.limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._row_to_entry(row) for row in rows]
    
    def clear(self) -> None:
        """清空所有日志（主要用于测试）"""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM audit_events")
            cursor.execute("DELETE FROM tasks")
            self._conn.commit()
    
    def close(self) -> None:
        """关闭数据库连接"""
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None
    
    def get_audit_events(self, task_id: str) -> List[dict]:
        """
        获取任务的审计事件列表
        
        Args:
            task_id: 任务ID
            
        Returns:
            审计事件列表
        """
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                "SELECT event_type, timestamp, actor, details FROM audit_events WHERE task_id = ? ORDER BY timestamp",
                (task_id,)
            )
            rows = cursor.fetchall()
            
            return [
                {
                    "event_type": row[0],
                    "timestamp": row[1],
                    "actor": row[2],
                    "details": json.loads(row[3]) if row[3] else None
                }
                for row in rows
            ]
    
    def save_audit_event(
        self,
        task_id: str,
        event_type: str,
        timestamp: str,
        actor: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        """
        保存审计事件
        
        Args:
            task_id: 任务ID
            event_type: 事件类型
            timestamp: 事件时间戳
            actor: 执行者（可选）
            details: 事件详情（可选）
        """
        with self._lock:
            cursor = self._conn.cursor()
            details_json = json.dumps(details, ensure_ascii=False) if details else None
            
            cursor.execute("""
                INSERT INTO audit_events (task_id, event_type, timestamp, actor, details)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, event_type, timestamp, actor, details_json))
            
            self._conn.commit()
    
    def _row_to_entry(self, row: tuple) -> TaskLogEntry:
        """
        将数据库行转换为 TaskLogEntry
        
        Args:
            row: 数据库行
            
        Returns:
            TaskLogEntry 实例
        """
        return TaskLogEntry(
            task_id=row[0],
            status=TaskStatus(row[1]),
            module=row[2],
            input_hash=row[3],
            # 反序列化时使用 is not None 检查，保留空字典 {}
            input_data=json.loads(row[4]) if row[4] is not None else None,
            output_data=json.loads(row[5]) if row[5] is not None else None,
            parent_task_id=row[6],
            child_task_ids=json.loads(row[7]) if row[7] else [],
            started_at=row[8],
            completed_at=row[9],
            duration_ms=row[10],
            metadata=json.loads(row[11]) if row[11] else None,
            error_message=row[12]
        )
    
    def get_count(self) -> int:
        """
        获取日志数量
        
        Returns:
            日志条目数量
        """
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks")
            return cursor.fetchone()[0]
