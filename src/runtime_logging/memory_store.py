"""
内存任务日志存储

最小版实现，使用内存存储，不引入数据库。
"""
from typing import Dict, Optional, List
from threading import Lock

from .store import TaskLogStore
from .models import TaskLogEntry, TaskLogQuery


class MemoryTaskLogStore(TaskLogStore):
    """
    内存任务日志存储
    
    最小版实现，数据保存在内存中。
    适用于开发和测试环境，生产环境应使用持久化存储。
    
    Attributes:
        _logs: 任务日志字典，key 为 task_id
        _lock: 线程锁，保证线程安全
    """
    
    def __init__(self):
        """初始化内存存储"""
        self._logs: Dict[str, TaskLogEntry] = {}
        self._lock = Lock()
    
    def save(self, entry: TaskLogEntry) -> None:
        """
        保存任务日志条目
        
        Args:
            entry: 任务日志条目
        """
        with self._lock:
            self._logs[entry.task_id] = entry
    
    def get(self, task_id: str) -> Optional[TaskLogEntry]:
        """
        获取指定任务ID的日志条目
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务日志条目，不存在则返回 None
        """
        with self._lock:
            return self._logs.get(task_id)
    
    def query(self, query: TaskLogQuery) -> List[TaskLogEntry]:
        """
        查询任务日志
        
        Args:
            query: 查询条件
            
        Returns:
            任务日志条目列表
        """
        with self._lock:
            # 先收集所有符合条件的条目
            results = []
            
            for entry in self._logs.values():
                # 应用过滤条件
                if query.task_id and entry.task_id != query.task_id:
                    continue
                if query.module and entry.module != query.module:
                    continue
                if query.status and entry.status != query.status:
                    continue
                if query.parent_task_id and entry.parent_task_id != query.parent_task_id:
                    continue
                if query.input_hash and entry.input_hash != query.input_hash:
                    continue
                
                results.append(entry)
            
            # 按开始时间降序排序（最新的在前）
            results.sort(key=lambda x: x.started_at, reverse=True)
            
            # 应用 limit 限制
            return results[:query.limit]
    
    def clear(self) -> None:
        """清空所有日志"""
        with self._lock:
            self._logs.clear()
    
    def get_count(self) -> int:
        """
        获取日志数量
        
        Returns:
            日志条目数量
        """
        with self._lock:
            return len(self._logs)