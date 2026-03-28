"""
Fake LLM Provider

用于测试的假 LLM Provider，返回可预测、稳定的响应。
可通过参数模拟 timeout / provider error / transient error。
"""
import time
from typing import Optional, Callable

from .models import LLMRequest, LLMResponse, LLMUsage
from .config import LLMGatewayConfig
from .provider import LLMProvider
from .errors import LLMTimeoutError, LLMProviderError


class FakeLLMProvider(LLMProvider):
    """
    假 LLM Provider
    
    用于测试，返回可预测的响应。
    
    Attributes:
        _name: Provider 名称
        _response_content: 固定返回的内容
        _latency_ms: 模拟延迟 (毫秒)
        _should_timeout: 是否模拟超时
        _should_fail: 是否模拟失败
        _is_transient_error: 失败是否为瞬时错误 (可重试)
        _fail_count: 失败计数
        _fail_until_success: 在多少次失败后成功 (用于测试重试)
    """
    
    def __init__(
        self,
        name: str = "fake",
        response_content: str = "This is a fake response.",
        latency_ms: int = 10,
        should_timeout: bool = False,
        should_fail: bool = False,
        is_transient_error: bool = False,
        fail_until_success: int = 0
    ):
        """
        初始化 Fake LLM Provider
        
        Args:
            name: Provider 名称
            response_content: 固定返回的内容
            latency_ms: 模拟延迟 (毫秒)
            should_timeout: 是否模拟超时
            should_fail: 是否模拟失败
            is_transient_error: 失败是否为瞬时错误 (可重试)
            fail_until_success: 在多少次失败后成功 (0 = 总是失败)
        """
        self._name = name
        self._response_content = response_content
        self._latency_ms = latency_ms
        self._should_timeout = should_timeout
        self._should_fail = should_fail
        self._is_transient_error = is_transient_error
        self._fail_until_success = fail_until_success
        self._fail_count = 0
    
    @property
    def name(self) -> str:
        return self._name
    
    def generate(
        self,
        request: LLMRequest,
        config: LLMGatewayConfig
    ) -> LLMResponse:
        """
        生成假响应
        
        Args:
            request: LLM 请求
            config: Gateway 配置
            
        Returns:
            假 LLM 响应
            
        Raises:
            LLMTimeoutError: 如果 should_timeout=True
            LLMProviderError: 如果 should_fail=True
        """
        # 模拟延迟
        if self._latency_ms > 0:
            time.sleep(self._latency_ms / 1000.0)
        
        # 模拟超时
        if self._should_timeout:
            raise LLMTimeoutError(
                message="Simulated timeout",
                provider=self._name,
                model=config.model_name
            )
        
        # 模拟失败
        if self._should_fail:
            self._fail_count += 1
            
            # 如果设置了 fail_until_success，检查是否应该成功
            if self._fail_until_success > 0 and self._fail_count >= self._fail_until_success:
                # 达到指定次数后成功
                pass
            else:
                raise LLMProviderError(
                    message="Simulated provider error",
                    provider=self._name,
                    model=config.model_name,
                    retryable=self._is_transient_error
                )
        
        # 返回成功响应
        return LLMResponse(
            content=self._response_content,
            provider=self._name,
            model=config.model_name,
            latency_ms=self._latency_ms,
            finish_reason="stop",
            usage=LLMUsage(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=30
            )
        )
    
    def reset(self):
        """重置失败计数"""
        self._fail_count = 0