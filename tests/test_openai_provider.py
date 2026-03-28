"""
OpenAI Provider 测试

测试 OpenAIProvider 的核心功能。
使用 mock HTTP 客户端，不要求真实联网。
"""
import json
import pytest
from unittest.mock import Mock, MagicMock

import httpx

from src.adapters.llm_gateway import (
    LLMRequest,
    LLMGatewayConfig,
    LLMTimeoutError,
    LLMProviderError,
)
from src.adapters.llm_gateway.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    """测试 OpenAIProvider"""
    
    def test_openai_provider_name(self):
        """测试 provider 名称"""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.name == "openai"
    
    def test_openai_provider_missing_api_key(self):
        """测试缺少 API Key 时抛出错误"""
        provider = OpenAIProvider(api_key=None)
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo"
        )
        
        with pytest.raises(LLMProviderError) as exc_info:
            provider.generate(request, config)
        
        assert "API key not configured" in str(exc_info.value)
        assert exc_info.value.retryable is False
    
    def test_openai_provider_success(self):
        """测试成功的 API 调用"""
        # 创建 mock HTTP client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {"content": "This is a test response."},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        
        provider = OpenAIProvider(
            api_key="test-key",
            http_client=mock_client
        )
        
        request = LLMRequest(
            prompt="Hello",
            system_prompt="You are helpful"
        )
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo",
            timeout_seconds=30.0
        )
        
        response = provider.generate(request, config)
        
        # 验证响应
        assert response.content == "This is a test response."
        assert response.provider == "openai"
        assert response.model == "gpt-3.5-turbo"
        assert response.finish_reason == "stop"
        assert response.usage is not None
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 20
        assert response.usage.total_tokens == 30
        
        # 验证 HTTP 调用
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.openai.com/v1/chat/completions"
        assert call_args[1]["json"]["model"] == "gpt-3.5-turbo"
        assert call_args[1]["json"]["messages"][0]["role"] == "system"
        assert call_args[1]["json"]["messages"][1]["role"] == "user"
    
    def test_openai_provider_timeout(self):
        """测试超时处理"""
        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.TimeoutException("Connection timeout")
        
        provider = OpenAIProvider(
            api_key="test-key",
            http_client=mock_client
        )
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo"
        )
        
        with pytest.raises(LLMTimeoutError) as exc_info:
            provider.generate(request, config)
        
        assert "timeout" in str(exc_info.value).lower()
    
    def test_openai_provider_http_error_429(self):
        """测试 429 限流错误（可重试）"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        
        http_error = httpx.HTTPStatusError(
            "Rate limit",
            request=MagicMock(),
            response=mock_response
        )
        mock_client.post.side_effect = http_error
        
        provider = OpenAIProvider(
            api_key="test-key",
            http_client=mock_client
        )
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo"
        )
        
        with pytest.raises(LLMProviderError) as exc_info:
            provider.generate(request, config)
        
        assert exc_info.value.retryable is True
    
    def test_openai_provider_http_error_400(self):
        """测试 400 错误（不可重试）"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        
        http_error = httpx.HTTPStatusError(
            "Bad request",
            request=MagicMock(),
            response=mock_response
        )
        mock_client.post.side_effect = http_error
        
        provider = OpenAIProvider(
            api_key="test-key",
            http_client=mock_client
        )
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo"
        )
        
        with pytest.raises(LLMProviderError) as exc_info:
            provider.generate(request, config)
        
        assert exc_info.value.retryable is False
    
    def test_openai_provider_with_base_url(self):
        """测试自定义 Base URL"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hi"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        
        provider = OpenAIProvider(
            api_key="test-key",
            base_url="https://custom.openai.com/v1",
            http_client=mock_client
        )
        
        request = LLMRequest(prompt="Hello")
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo"
        )
        
        provider.generate(request, config)
        
        # 验证使用了自定义 URL
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://custom.openai.com/v1/chat/completions"
    
    def test_openai_provider_no_system_prompt(self):
        """测试不带 system prompt 的请求"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        
        provider = OpenAIProvider(
            api_key="test-key",
            http_client=mock_client
        )
        
        request = LLMRequest(prompt="Hello")  # 没有 system_prompt
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo"
        )
        
        provider.generate(request, config)
        
        # 验证消息结构
        call_args = mock_client.post.call_args
        messages = call_args[1]["json"]["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"

    def test_openai_provider_defaults_to_not_trusting_env(self, monkeypatch):
        """测试默认不继承系统代理环境变量"""
        captured = {}

        class DummyClient:
            def close(self):
                return None

        def fake_client(*args, **kwargs):
            captured.update(kwargs)
            return DummyClient()

        monkeypatch.delenv("OPENAI_TRUST_ENV", raising=False)
        monkeypatch.setattr(httpx, "Client", fake_client)

        provider = OpenAIProvider(api_key="test-key")
        provider._get_client()

        assert captured["trust_env"] is False

    def test_openai_provider_can_enable_trust_env(self, monkeypatch):
        """测试可通过环境变量开启 trust_env"""
        captured = {}

        class DummyClient:
            def close(self):
                return None

        def fake_client(*args, **kwargs):
            captured.update(kwargs)
            return DummyClient()

        monkeypatch.setenv("OPENAI_TRUST_ENV", "true")
        monkeypatch.setattr(httpx, "Client", fake_client)

        provider = OpenAIProvider(api_key="test-key")
        provider._get_client()

        assert captured["trust_env"] is True
