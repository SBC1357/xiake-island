"""
Task Log 存储接口

定义任务日志存储的抽象接口。
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from .models import TaskLogEntry, TaskLogQuery


class TaskLogStore(ABC):
    """
    任务日志存储抽象基类
    
    定义所有任务日志存储必须实现的接口。
    """
    
    @abstractmethod
    def save(self, entry: TaskLogEntry) -> None:
        """
        保存任务日志条目
        
        Args:
            entry: 任务日志条目
        """
        pass
    
    @abstractmethod
    def get(self, task_id: str) -> Optional[TaskLogEntry]:
        """
        获取指定任务ID的日志条目
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务日志条目，不存在则返回 None
        """
        pass
    
    @abstractmethod
    def query(self, query: TaskLogQuery) -> List[TaskLogEntry]:
        """
        查询任务日志
        
        Args:
            query: 查询条件
            
        Returns:
            任务日志条目列表
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """清空所有日志 (主要用于测试)"""
        pass