"""
Task Logger

任务日志记录器，提供统一的任务追踪接口。
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Any

from src.contracts.base import TaskStatus, ModuleName

from .store import TaskLogStore
from .memory_store import MemoryTaskLogStore
from .models import TaskLogEntry, TaskLogQuery
from .audit_events import AuditEvent
from .hash_utils import compute_input_hash, compute_output_hash


class TaskLogger:
    """
    任务日志记录器
    
    提供统一的任务追踪接口，支持：
    - 任务开始记录
    - 任务完成记录
    - 任务失败记录
    - 任务查询
    
    Attributes:
        store: 任务日志存储
    """
    
    def __init__(self, store: Optional[TaskLogStore] = None):
        """
        初始化任务日志记录器
        
        Args:
            store: 任务日志存储，默认使用 MemoryTaskLogStore
        """
        self.store = store or MemoryTaskLogStore()
    
    def start_task(
        self,
        module: ModuleName,
        input_data: Optional[dict[str, Any]] = None,
        input_hash: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> str:
        """
        开始记录任务
        
        Args:
            module: 执行模块
            input_data: 完整输入参数 (可选，用于重放和版本分组)
            input_hash: 输入哈希 (可选，如未提供且 input_data 存在则自动计算)
            parent_task_id: 父任务ID (可选)
            metadata: 元数据 (可选)
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()
        
        # 如果提供了 input_data 但未提供 input_hash，自动计算
        if input_data is not None and input_hash is None:
            input_hash = compute_input_hash(input_data)
        
        entry = TaskLogEntry(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            module=module,
            input_hash=input_hash,
            input_data=input_data,
            parent_task_id=parent_task_id,
            child_task_ids=[],  # 初始化为空列表
            started_at=started_at,
            metadata=metadata
        )
        
        self.store.save(entry)
        return task_id
    
    def complete_task(
        self,
        task_id: str,
        output_data: Optional[dict[str, Any]] = None,
        output_hash: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
        child_task_ids: Optional[list[str]] = None
    ) -> None:
        """
        完成任务记录
        
        Args:
            task_id: 任务ID
            output_data: 完整输出结果 (可选，用于查看历史结果)
            output_hash: 输出哈希 (可选)
            duration_ms: 执行耗时 (毫秒) (可选)
            metadata: 额外元数据 (可选，会合并到已有元数据)
            child_task_ids: 子任务ID列表 (可选，工作流场景)
        """
        entry = self.store.get(task_id)
        if entry is None:
            return
        
        completed_at = datetime.now(timezone.utc).isoformat()
        
        # 如果提供了 output_data 但未提供 output_hash，自动计算
        if output_data is not None and output_hash is None:
            output_hash = compute_output_hash(output_data)
        
        # 合并元数据
        merged_metadata = entry.metadata or {}
        if metadata:
            merged_metadata.update(metadata)
        
        # 合并 child_task_ids
        final_child_task_ids = entry.child_task_ids or []
        if child_task_ids:
            # 追加新的子任务ID，避免重复
            for cid in child_task_ids:
                if cid not in final_child_task_ids:
                    final_child_task_ids.append(cid)
        
        updated_entry = TaskLogEntry(
            task_id=entry.task_id,
            status=TaskStatus.COMPLETED,
            module=entry.module,
            input_hash=entry.input_hash,
            output_hash=output_hash,
            input_data=entry.input_data,
            output_data=output_data,
            parent_task_id=entry.parent_task_id,
            child_task_ids=final_child_task_ids,
            started_at=entry.started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            metadata=merged_metadata if merged_metadata else None
        )
        
        self.store.save(updated_entry)
    
    def fail_task(
        self,
        task_id: str,
        error_message: str,
        duration_ms: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        记录任务失败
        
        Args:
            task_id: 任务ID
            error_message: 错误消息
            duration_ms: 执行耗时 (毫秒) (可选)
            metadata: 额外元数据 (可选)
        """
        entry = self.store.get(task_id)
        if entry is None:
            return
        
        completed_at = datetime.now(timezone.utc).isoformat()
        
        # 合并元数据
        merged_metadata = entry.metadata or {}
        if metadata:
            merged_metadata.update(metadata)
        
        updated_entry = TaskLogEntry(
            task_id=entry.task_id,
            status=TaskStatus.FAILED,
            module=entry.module,
            input_hash=entry.input_hash,
            input_data=entry.input_data,
            parent_task_id=entry.parent_task_id,
            child_task_ids=entry.child_task_ids or [],
            started_at=entry.started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            metadata=merged_metadata if merged_metadata else None,
            error_message=error_message
        )
        
        self.store.save(updated_entry)
    
    def get_task(self, task_id: str) -> Optional[TaskLogEntry]:
        """
        获取任务日志
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务日志条目
        """
        return self.store.get(task_id)
    
    def query_tasks(self, query: TaskLogQuery) -> list[TaskLogEntry]:
        """
        查询任务日志
        
        Args:
            query: 查询条件
            
        Returns:
            任务日志条目列表
        """
        return self.store.query(query)
    
    def get_tasks_by_module(self, module: ModuleName, limit: int = 100) -> list[TaskLogEntry]:
        """
        按模块查询任务
        
        Args:
            module: 模块名称
            limit: 返回数量限制
            
        Returns:
            任务日志条目列表
        """
        return self.store.query(TaskLogQuery(module=module, limit=limit))
    
    def get_tasks_by_input_hash(self, input_hash: str, limit: int = 100) -> list[TaskLogEntry]:
        """
        按输入哈希查询任务 (用于版本分组)
        
        Args:
            input_hash: 输入哈希
            limit: 返回数量限制
            
        Returns:
            任务日志条目列表
        """
        return self.store.query(TaskLogQuery(input_hash=input_hash, limit=limit))
    
    def record_audit_event(
        self,
        task_id: str,
        event: AuditEvent
    ) -> None:
        """
        记录审计事件
        
        将审计事件追加到任务的 metadata["audit"] 列表中。
        
        Args:
            task_id: 任务ID
            event: 审计事件
        """
        entry = self.store.get(task_id)
        if entry is None:
            return
        
        # 获取或创建 audit 列表
        merged_metadata = entry.metadata or {}
        audit_list = merged_metadata.get("audit", [])
        
        # 追加新事件
        audit_list.append(event.model_dump())
        merged_metadata["audit"] = audit_list
        
        # 更新 entry
        updated_entry = TaskLogEntry(
            task_id=entry.task_id,
            status=entry.status,
            module=entry.module,
            input_hash=entry.input_hash,
            output_hash=entry.output_hash,
            input_data=entry.input_data,
            output_data=entry.output_data,
            parent_task_id=entry.parent_task_id,
            child_task_ids=entry.child_task_ids or [],
            started_at=entry.started_at,
            completed_at=entry.completed_at,
            duration_ms=entry.duration_ms,
            metadata=merged_metadata if merged_metadata else None,
            error_message=entry.error_message
        )
        
        self.store.save(updated_entry)
    
    def get_audit_events(self, task_id: str) -> list[dict]:
        """
        获取任务的审计事件列表
        
        Args:
            task_id: 任务ID
            
        Returns:
            审计事件列表
        """
        # 优先使用 store 的独立 audit_events 表
        if hasattr(self.store, 'get_audit_events'):
            return self.store.get_audit_events(task_id)
        
        # 回退到 metadata 中的 audit 列表
        entry = self.store.get(task_id)
        if entry is None or entry.metadata is None:
            return []
        
        return entry.metadata.get("audit", [])
    
    def save_audit_event(
        self,
        task_id: str,
        event_type: str,
        timestamp: str,
        actor: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """
        保存审计事件到独立的 audit_events 表
        
        Args:
            task_id: 任务ID
            event_type: 事件类型
            timestamp: 事件时间戳
            actor: 执行者（可选）
            details: 事件详情（可选）
        """
        if hasattr(self.store, 'save_audit_event'):
            self.store.save_audit_event(
                task_id=task_id,
                event_type=event_type,
                timestamp=timestamp,
                actor=actor,
                details=details
            )
        else:
            # 回退：存储到 metadata
            from .audit_events import create_audit_event
            event = create_audit_event(
                event_type=event_type,
                actor=actor,
                details=details
            )
            event.timestamp = timestamp  # 使用传入的时间戳
            self.record_audit_event(task_id, event)