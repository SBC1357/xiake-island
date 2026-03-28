# Runtime Logging - 运行时日志模块
"""
职责:
- 统一日志记录
- 任务追踪
- 审计日志

首阶段最小版:
- TaskLogger: 任务日志记录器
- MemoryTaskLogStore: 内存存储 (开发和测试)
- SQLiteTaskLogStore: SQLite 持久化存储 (生产)
- TaskLogEntry: 任务日志条目模型
- AuditEvent: 审计事件模型

公开接口:
- TaskLogger: 任务日志记录器
- TaskLogStore: 存储接口 (可扩展)
- MemoryTaskLogStore: 内存存储实现
- SQLiteTaskLogStore: SQLite 持久化存储实现
- TaskLogEntry: 任务日志条目
- TaskLogQuery: 查询条件
- AuditEvent: 审计事件
- create_audit_event: 创建审计事件
- workflow_requested, workflow_completed, workflow_failed: 便捷函数
- compute_input_hash: 计算输入哈希
"""

# 数据模型
from .models import TaskLogEntry, TaskLogQuery

# 存储
from .store import TaskLogStore
from .memory_store import MemoryTaskLogStore
from .sqlite_store import SQLiteTaskLogStore

# 记录器
from .task_logger import TaskLogger

# 审计事件
from .audit_events import (
    AuditEvent,
    AuditEventType,
    create_audit_event,
    workflow_requested,
    workflow_completed,
    workflow_failed,
)

# 哈希工具
from .hash_utils import compute_input_hash, compute_output_hash

__all__ = [
    # 数据模型
    "TaskLogEntry",
    "TaskLogQuery",
    # 存储
    "TaskLogStore",
    "MemoryTaskLogStore",
    "SQLiteTaskLogStore",
    # 记录器
    "TaskLogger",
    # 审计事件
    "AuditEvent",
    "AuditEventType",
    "create_audit_event",
    "workflow_requested",
    "workflow_completed",
    "workflow_failed",
    # 哈希工具
    "compute_input_hash",
    "compute_output_hash",
]