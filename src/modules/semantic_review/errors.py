"""
Semantic Review Module 错误定义

定义语义审核模块的异常类型。
"""
from typing import Optional


class SemanticReviewError(Exception):
    """
    语义审核错误基类
    
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


class ContentTooShortError(SemanticReviewError):
    """
    内容过短错误
    
    当审核内容过短时抛出。
    """
    pass


class ReviewGenerationError(SemanticReviewError):
    """
    审核生成错误
    
    当审核生成过程失败时抛出。
    """
    pass