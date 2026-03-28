"""
Opinion Module 错误定义

定义观点产出模块的异常类型。
"""
from typing import Optional


class OpinionModuleError(Exception):
    """
    Opinion Module 错误基类
    
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


class InsufficientEvidenceError(OpinionModuleError):
    """
    证据不足错误
    
    当提供的证据不足以形成观点时抛出。
    """
    pass


class ConfidenceTooLowError(OpinionModuleError):
    """
    置信度过低错误
    
    当生成的观点置信度低于阈值时抛出。
    """
    pass


class OpinionGenerationError(OpinionModuleError):
    """
    观点生成错误
    
    当观点生成过程失败时抛出。
    """
    pass