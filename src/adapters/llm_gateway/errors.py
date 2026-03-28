"""
LLM Gateway 错误定义

定义 Gateway 层统一异常，不在 Gateway 层直接做 API 响应。
"""
from typing import Optional


class LLMGatewayError(Exception):
    """
    LLM Gateway 错误基类
    
    Gateway 层统一异常，用于表达模型调用失败等错误。
    不在 Gateway 层直接做 API 响应。
    
    Attributes:
        message: 错误消息
        provider: 提供商名称 (可选)
        model: 模型名称 (可选)
        retryable: 是否可重试
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        retryable: bool = False
    ):
        self.message = message
        self.provider = provider
        self.model = model
        self.retryable = retryable
        super().__init__(self.message)
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.provider:
            parts.append(f"provider={self.provider}")
        if self.model:
            parts.append(f"model={self.model}")
        if self.retryable:
            parts.append("retryable=True")
        return " | ".join(parts)


class LLMTimeoutError(LLMGatewayError):
    """
    LLM 超时错误
    
    当模型调用超时时抛出。
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(
            message=message,
            provider=provider,
            model=model,
            retryable=True  # 超时通常可重试
        )


class LLMProviderError(LLMGatewayError):
    """
    LLM 提供商错误
    
    当提供商返回错误时抛出。
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        retryable: bool = False,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            provider=provider,
            model=model,
            retryable=retryable
        )
        self.original_error = original_error


class LLMRetryExceededError(LLMGatewayError):
    """
    LLM 重试耗尽错误
    
    当重试次数耗尽仍失败时抛出。
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        attempts: int = 0
    ):
        super().__init__(
            message=message,
            provider=provider,
            model=model,
            retryable=False  # 已重试耗尽
        )
        self.attempts = attempts