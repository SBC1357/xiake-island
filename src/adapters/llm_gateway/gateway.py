"""
LLM Gateway

统一模型调用入口，管理重试和错误归一化。
"""
import time
from typing import Optional

from .models import LLMRequest, LLMResponse
from .config import LLMGatewayConfig
from .provider import LLMProvider
from .errors import (
    LLMGatewayError,
    LLMTimeoutError,
    LLMProviderError,
    LLMRetryExceededError,
)


class LLMGateway:
    """
    LLM Gateway
    
    统一模型调用入口，提供：
    - 统一的 provider 调用接口
    - 有限重试支持
    - 错误归一化
    - 基础元数据记录 (provider、model、latency)
    
    不在这一层直接做 FastAPI 响应。
    
    Attributes:
        provider: LLM Provider 实例
        config: Gateway 配置
    """
    
    def __init__(self, provider: LLMProvider, config: LLMGatewayConfig):
        """
        初始化 LLM Gateway
        
        Args:
            provider: LLM Provider 实例
            config: Gateway 配置
        """
        self.provider = provider
        self.config = config
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        生成 LLM 响应
        
        统一调用入口，支持有限重试。
        
        Args:
            request: LLM 请求
            
        Returns:
            LLM 响应
            
        Raises:
            LLMRetryExceededError: 重试耗尽
            LLMProviderError: 不可重试的提供商错误
            LLMTimeoutError: 超时（重试后仍超时）
        """
        attempts = 0
        last_error: Optional[LLMGatewayError] = None
        
        while attempts <= self.config.max_retries:
            attempts += 1
            start_time = time.time()
            
            try:
                response = self.provider.generate(request, self.config)
                
                # 更新延迟为实际耗时
                elapsed_ms = int((time.time() - start_time) * 1000)
                response.latency_ms = elapsed_ms
                
                return response
                
            except LLMTimeoutError as e:
                last_error = e
                # 超时可重试
                if attempts <= self.config.max_retries:
                    continue
                # 否则退出循环，抛出 RetryExceededError
                    
            except LLMProviderError as e:
                last_error = e
                # 只有可重试的错误才继续
                if e.retryable:
                    # 如果还有重试机会，继续
                    if attempts <= self.config.max_retries:
                        continue
                    # 否则退出循环，抛出 RetryExceededError
                else:
                    # 不可重试的错误直接抛出
                    raise
                
            except LLMGatewayError as e:
                # 其他 Gateway 错误直接抛出
                raise
            
            # 归一化原生异常
            except TimeoutError as e:
                # 原生 Python TimeoutError 包装成 LLMTimeoutError
                last_error = LLMTimeoutError(
                    message=str(e),
                    provider=self.config.provider_name,
                    model=self.config.model_name
                )
                # 超时可重试
                if attempts <= self.config.max_retries:
                    continue
            
            except Exception as e:
                # 其他未归一化异常包装成 LLMProviderError
                last_error = LLMProviderError(
                    message=str(e),
                    provider=self.config.provider_name,
                    model=self.config.model_name,
                    retryable=False,  # 未知错误默认不可重试
                    original_error=e
                )
                # 不可重试，直接抛出
                raise last_error from e
        
        # 重试耗尽
        raise LLMRetryExceededError(
            message=f"Retry attempts exceeded ({attempts} attempts)",
            provider=self.config.provider_name,
            model=self.config.model_name,
            attempts=attempts
        ) from last_error