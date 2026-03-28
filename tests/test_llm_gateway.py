"""
LLM Gateway 测试

使用 FakeLLMProvider 进行测试，不依赖真实外部模型服务。
"""
import pytest
from pydantic import ValidationError

from src.adapters.llm_gateway import (
    LLMRequest,
    LLMResponse,
    LLMUsage,
    LLMGatewayConfig,
    LLMProvider,
    FakeLLMProvider,
    LLMGateway,
    LLMTimeoutError,
    LLMProviderError,
    LLMRetryExceededError,
)


class TestLLMRequest:
    """测试 LLMRequest"""
    
    def test_request_with_required_fields(self):
        """测试 7: 请求模型基本校验 - 必填字段"""
        request = LLMRequest(prompt="Hello, world!")
        assert request.prompt == "Hello, world!"
        assert request.system_prompt is None
        assert request.temperature is None
        assert request.max_tokens is None
        assert request.metadata is None
    
    def test_request_with_all_fields(self):
        """测试请求模型 - 所有字段"""
        request = LLMRequest(
            prompt="Hello",
            system_prompt="You are helpful",
            temperature=0.7,
            max_tokens=100,
            metadata={"key": "value"}
        )
        assert request.prompt == "Hello"
        assert request.system_prompt == "You are helpful"
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.metadata == {"key": "value"}
    
    def test_request_empty_prompt_fails(self):
        """测试空提示词失败"""
        with pytest.raises(ValidationError):
            LLMRequest(prompt="")
    
    def test_request_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            LLMRequest(prompt="Hello", unknown_field="value")
    
    def test_request_invalid_temperature_fails(self):
        """测试无效温度失败"""
        with pytest.raises(ValidationError):
            LLMRequest(prompt="Hello", temperature=3.0)  # > 2.0


class TestLLMResponse:
    """测试 LLMResponse"""
    
    def test_response_with_required_fields(self):
        """测试 7: 响应模型基本校验 - 必填字段"""
        response = LLMResponse(
            content="Hello!",
            provider="fake",
            model="fake-model",
            latency_ms=10
        )
        assert response.content == "Hello!"
        assert response.provider == "fake"
        assert response.model == "fake-model"
        assert response.latency_ms == 10
        assert response.finish_reason is None
        assert response.usage is None
    
    def test_response_with_usage(self):
        """测试响应模型 - 包含使用统计"""
        usage = LLMUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        response = LLMResponse(
            content="Hello!",
            provider="fake",
            model="fake-model",
            latency_ms=10,
            usage=usage
        )
        assert response.usage is not None
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 20


class TestLLMGatewayConfig:
    """测试 LLMGatewayConfig"""
    
    def test_config_with_required_fields(self):
        """测试配置 - 必填字段"""
        config = LLMGatewayConfig(
            provider_name="fake",
            model_name="fake-model"
        )
        assert config.provider_name == "fake"
        assert config.model_name == "fake-model"
        assert config.timeout_seconds == 30.0
        assert config.max_retries == 3
    
    def test_config_custom_values(self):
        """测试配置 - 自定义值"""
        config = LLMGatewayConfig(
            provider_name="fake",
            model_name="fake-model",
            timeout_seconds=60.0,
            max_retries=5
        )
        assert config.timeout_seconds == 60.0
        assert config.max_retries == 5
    
    def test_config_typo_field_fails(self):
        """测试 6: 配置 typo 字段会报错"""
        with pytest.raises(ValidationError) as exc_info:
            LLMGatewayConfig(
                provider_name="fake",
                model_name="fake-model",
                timeout_secondss=30.0  # typo: extra 's'
            )
        assert "Extra inputs are not permitted" in str(exc_info.value) or "timeout_secondss" in str(exc_info.value)
    
    def test_config_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            LLMGatewayConfig(
                provider_name="fake",
                model_name="fake-model",
                unknown_option=True
            )


class TestFakeLLMProvider:
    """测试 FakeLLMProvider"""
    
    def test_fake_provider_success(self):
        """测试 1: fake provider 成功返回"""
        provider = FakeLLMProvider(
            name="test-fake",
            response_content="Test response",
            latency_ms=5
        )
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="test-fake",
            model_name="test-model"
        )
        
        response = provider.generate(request, config)
        
        assert response.content == "Test response"
        assert response.provider == "test-fake"
        assert response.model == "test-model"
        assert response.finish_reason == "stop"
        assert response.usage is not None
        assert response.usage.total_tokens == 30
    
    def test_fake_provider_timeout(self):
        """测试 fake provider 超时"""
        provider = FakeLLMProvider(should_timeout=True)
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="fake",
            model_name="fake-model"
        )
        
        with pytest.raises(LLMTimeoutError) as exc_info:
            provider.generate(request, config)
        
        assert "timeout" in str(exc_info.value).lower()
    
    def test_fake_provider_error(self):
        """测试 fake provider 错误"""
        provider = FakeLLMProvider(should_fail=True)
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="fake",
            model_name="fake-model"
        )
        
        with pytest.raises(LLMProviderError) as exc_info:
            provider.generate(request, config)
        
        assert "provider error" in str(exc_info.value).lower()


class TestLLMGateway:
    """测试 LLMGateway"""
    
    @pytest.fixture
    def gateway(self):
        """创建测试用 Gateway"""
        provider = FakeLLMProvider(
            name="test-fake",
            response_content="Gateway response",
            latency_ms=5
        )
        config = LLMGatewayConfig(
            provider_name="test-fake",
            model_name="test-model"
        )
        return LLMGateway(provider, config)
    
    def test_gateway_success(self, gateway):
        """测试 2: gateway 成功调用并返回结构化响应"""
        request = LLMRequest(prompt="Hello")
        response = gateway.generate(request)
        
        assert response.content == "Gateway response"
        assert response.provider == "test-fake"
        assert response.model == "test-model"
        assert response.latency_ms >= 0
        assert response.finish_reason == "stop"
    
    def test_gateway_timeout_error(self):
        """测试 3: timeout 错误映射正确"""
        provider = FakeLLMProvider(should_timeout=True)
        config = LLMGatewayConfig(
            provider_name="timeout-fake",
            model_name="test-model",
            max_retries=0  # 不重试，立即失败
        )
        gateway = LLMGateway(provider, config)
        
        request = LLMRequest(prompt="Hello")
        
        with pytest.raises(LLMRetryExceededError) as exc_info:
            gateway.generate(request)
        
        assert exc_info.value.attempts == 1
    
    def test_gateway_retry_transient_error(self):
        """测试 4: 可重试错误在限定次数内重试"""
        # 模拟前 2 次失败，第 3 次成功
        provider = FakeLLMProvider(
            should_fail=True,
            is_transient_error=True,
            fail_until_success=3
        )
        config = LLMGatewayConfig(
            provider_name="retry-fake",
            model_name="test-model",
            max_retries=5  # 允许足够重试
        )
        gateway = LLMGateway(provider, config)
        
        request = LLMRequest(prompt="Hello")
        response = gateway.generate(request)
        
        # 应该在第 3 次成功
        assert response.content == "This is a fake response."
    
    def test_gateway_retry_exceeded(self):
        """测试 5: 重试耗尽时抛出预期异常"""
        provider = FakeLLMProvider(
            should_fail=True,
            is_transient_error=True
        )
        config = LLMGatewayConfig(
            provider_name="retry-fake",
            model_name="test-model",
            max_retries=2
        )
        gateway = LLMGateway(provider, config)
        
        request = LLMRequest(prompt="Hello")
        
        with pytest.raises(LLMRetryExceededError) as exc_info:
            gateway.generate(request)
        
        # max_retries=2 意味着最多 3 次尝试 (1 次 + 2 次重试)
        assert exc_info.value.attempts == 3
        assert exc_info.value.provider == "retry-fake"
        assert exc_info.value.model == "test-model"
        assert exc_info.value.retryable is False
    
    def test_gateway_non_retryable_error_immediate_fail(self):
        """测试不可重试错误立即失败"""
        provider = FakeLLMProvider(
            should_fail=True,
            is_transient_error=False  # 不可重试
        )
        config = LLMGatewayConfig(
            provider_name="fail-fake",
            model_name="test-model",
            max_retries=5
        )
        gateway = LLMGateway(provider, config)
        
        request = LLMRequest(prompt="Hello")
        
        with pytest.raises(LLMProviderError) as exc_info:
            gateway.generate(request)
        
        # 不可重试错误不进行重试
        assert exc_info.value.retryable is False


class TestLLMGatewayErrorTypes:
    """测试错误类型"""
    
    def test_timeout_is_retryable(self):
        """测试超时错误可重试"""
        error = LLMTimeoutError(
            message="Timeout",
            provider="test",
            model="test-model"
        )
        assert error.retryable is True
    
    def test_provider_error_retryable_flag(self):
        """测试提供商错误可重试标志"""
        retryable_error = LLMProviderError(
            message="Transient error",
            provider="test",
            model="test-model",
            retryable=True
        )
        assert retryable_error.retryable is True
        
        non_retryable_error = LLMProviderError(
            message="Permanent error",
            provider="test",
            model="test-model",
            retryable=False
        )
        assert non_retryable_error.retryable is False
    
    def test_retry_exceeded_not_retryable(self):
        """测试重试耗尽错误不可重试"""
        error = LLMRetryExceededError(
            message="Exceeded",
            provider="test",
            model="test-model",
            attempts=5
        )
        assert error.retryable is False
        assert error.attempts == 5


class TestNativeExceptionNormalization:
    """测试原生异常归一化"""
    
    def test_native_timeout_error_normalized(self):
        """原生 TimeoutError 被归一化为 LLMTimeoutError"""
        from src.adapters.llm_gateway.provider import LLMProvider
        from src.adapters.llm_gateway.models import LLMRequest, LLMResponse
        from src.adapters.llm_gateway.config import LLMGatewayConfig
        
        # 创建抛出原生 TimeoutError 的 provider
        class NativeTimeoutProvider(LLMProvider):
            @property
            def name(self) -> str:
                return "native-timeout"
            
            def generate(self, request: LLMRequest, config: LLMGatewayConfig) -> LLMResponse:
                raise TimeoutError("socket timed out")
        
        provider = NativeTimeoutProvider()
        config = LLMGatewayConfig(
            provider_name="native-timeout",
            model_name="test-model",
            max_retries=0
        )
        gateway = LLMGateway(provider, config)
        
        request = LLMRequest(prompt="Hello")
        
        # max_retries=0 时，超时会抛出 LLMRetryExceededError
        # 其 cause 应该是归一化后的 LLMTimeoutError
        with pytest.raises(LLMRetryExceededError) as exc_info:
            gateway.generate(request)
        
        assert exc_info.value.provider == "native-timeout"
        assert exc_info.value.model == "test-model"
        # 验证 __cause__ 是 LLMTimeoutError（归一化后的原生 TimeoutError）
        assert isinstance(exc_info.value.__cause__, LLMTimeoutError)
        assert "socket timed out" in str(exc_info.value.__cause__)
    
    def test_native_runtime_error_normalized(self):
        """原生 RuntimeError 被归一化为 LLMProviderError"""
        from src.adapters.llm_gateway.provider import LLMProvider
        from src.adapters.llm_gateway.models import LLMRequest, LLMResponse
        from src.adapters.llm_gateway.config import LLMGatewayConfig
        
        # 创建抛出原生 RuntimeError 的 provider
        class NativeRuntimeErrorProvider(LLMProvider):
            @property
            def name(self) -> str:
                return "native-runtime"
            
            def generate(self, request: LLMRequest, config: LLMGatewayConfig) -> LLMResponse:
                raise RuntimeError("provider boom")
        
        provider = NativeRuntimeErrorProvider()
        config = LLMGatewayConfig(
            provider_name="native-runtime",
            model_name="test-model"
        )
        gateway = LLMGateway(provider, config)
        
        request = LLMRequest(prompt="Hello")
        
        # 应该抛出 LLMProviderError，而不是原生 RuntimeError
        with pytest.raises(LLMProviderError) as exc_info:
            gateway.generate(request)
        
        assert "provider boom" in str(exc_info.value)
        assert exc_info.value.provider == "native-runtime"
        assert exc_info.value.model == "test-model"
        assert exc_info.value.retryable is False  # 未知错误默认不可重试
        assert exc_info.value.original_error is not None
        assert isinstance(exc_info.value.original_error, RuntimeError)
    
    def test_native_timeout_retryable(self):
        """原生 TimeoutError 归一化后可重试"""
        from src.adapters.llm_gateway.provider import LLMProvider
        from src.adapters.llm_gateway.models import LLMRequest, LLMResponse
        from src.adapters.llm_gateway.config import LLMGatewayConfig
        
        call_count = 0
        
        class EventuallySucceedProvider(LLMProvider):
            @property
            def name(self) -> str:
                return "eventual-success"
            
            def generate(self, request: LLMRequest, config: LLMGatewayConfig) -> LLMResponse:
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise TimeoutError("socket timed out")
                return LLMResponse(
                    content="Success!",
                    provider="eventual-success",
                    model=config.model_name,
                    latency_ms=10
                )
        
        provider = EventuallySucceedProvider()
        config = LLMGatewayConfig(
            provider_name="eventual-success",
            model_name="test-model",
            max_retries=5
        )
        gateway = LLMGateway(provider, config)
        
        request = LLMRequest(prompt="Hello")
        response = gateway.generate(request)
        
        # 应该在第 3 次成功
        assert response.content == "Success!"
        assert call_count == 3