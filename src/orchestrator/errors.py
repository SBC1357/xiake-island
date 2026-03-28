"""
Orchestrator 错误定义

定义编排层的异常类型。
"""
from typing import Optional


class OrchestratorError(Exception):
    """
    Orchestrator 错误基类
    
    Attributes:
        message: 错误消息
        details: 错误详情 (可选)
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


class UnsupportedModuleError(OrchestratorError):
    """
    不支持的模块错误
    
    当请求的模块不被支持时抛出。
    """
    pass


class UnsupportedWorkflowError(OrchestratorError):
    """
    不支持的工作流错误
    
    当请求的工作流不被支持时抛出。
    """
    pass


class WorkflowExecutionError(OrchestratorError):
    """
    工作流执行错误
    
    当工作流执行过程中失败时抛出。
    """
    pass