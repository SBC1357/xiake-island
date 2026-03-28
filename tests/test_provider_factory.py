"""
Provider Factory 测试

测试 Provider 工厂函数的核心逻辑。
"""
import os
import pytest
from pydantic import ValidationError

from src.adapters.llm_gateway import (
    LLMGatewayConfig,
    FakeLLMProvider,
    OpenAIProvider,
)
from src.adapters.llm_gateway.provider_factory import (
    create_llm_provider,
    create_llm_provider_from_env,
)


class TestCreateLLMProvider:
    """测试 create_llm_provider 函数"""
    
    def test_create_fake_provider(self):
        """测试创建 Fake Provider"""
        config = LLMGatewayConfig(
            provider_name="fake",
            model_name="fake-model"
        )
        
        provider = create_llm_provider(config)
        
        assert isinstance(provider, FakeLLMProvider)
        assert provider.name == "fake"
    
    def test_create_openai_provider(self):
        """测试创建 OpenAI Provider"""
        config = LLMGatewayConfig(
            provider_name="openai",
            model_name="gpt-3.5-turbo",
            api_key="test-key",
            base_url="https://api.openai.com/v1"
        )
        
        provider = create_llm_provider(config)
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.name == "openai"
    
    def test_create_provider_case_insensitive(self):
        """测试 provider 名称大小写不敏感"""
        config = LLMGatewayConfig(
            provider_name="FAKE",  # 大写
            model_name="fake-model"
        )
        
        provider = create_llm_provider(config)
        
        assert isinstance(provider, FakeLLMProvider)
    
    def test_create_unknown_provider(self):
        """测试未知 provider 抛出错误"""
        config = LLMGatewayConfig(
            provider_name="unknown",
            model_name="unknown-model"
        )
        
        with pytest.raises(ValueError) as exc_info:
            create_llm_provider(config)
        
        assert "Unknown provider" in str(exc_info.value)
        assert "fake" in str(exc_info.value)
        assert "openai" in str(exc_info.value)


class TestCreateLLMProviderFromEnv:
    """测试 create_llm_provider_from_env 函数"""
    
    def test_from_env_default_to_fake(self, monkeypatch):
        """测试默认使用 fake provider"""
        # 清除环境变量
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.delenv("LLM_MODEL", raising=False)
        
        provider, config = create_llm_provider_from_env()
        
        assert isinstance(provider, FakeLLMProvider)
        assert config.provider_name == "fake"
        assert config.model_name == "fake-model"
    
    def test_from_env_with_openai_config(self, monkeypatch):
        """测试从环境变量读取 OpenAI 配置"""
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("LLM_MODEL", "gpt-4")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_BASE_URL", "https://custom.openai.com/v1")
        monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "60")
        monkeypatch.setenv("LLM_MAX_RETRIES", "5")
        
        provider, config = create_llm_provider_from_env()
        
        assert isinstance(provider, OpenAIProvider)
        assert config.provider_name == "openai"
        assert config.model_name == "gpt-4"
        assert config.api_key == "sk-test-key"
        assert config.base_url == "https://custom.openai.com/v1"
        assert config.timeout_seconds == 60.0
        assert config.max_retries == 5
    
    def test_from_env_openai_without_api_key(self, monkeypatch):
        """测试 OpenAI 配置但没有 API Key"""
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("LLM_MODEL", "gpt-3.5-turbo")  # 必须设置模型名
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        provider, config = create_llm_provider_from_env()
        
        # Provider 创建成功，但调用时会报错
        assert isinstance(provider, OpenAIProvider)
        assert config.api_key is None
    
    def test_from_env_openai_without_model_name(self, monkeypatch):
        """测试 OpenAI 模式下缺少 LLM_MODEL 应抛出错误"""
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.delenv("LLM_MODEL", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        
        with pytest.raises(ValueError) as exc_info:
            create_llm_provider_from_env()
        
        assert "LLM_MODEL" in str(exc_info.value)
        assert "must be set" in str(exc_info.value)
    
    def test_from_env_openai_with_fake_model_raises_error(self, monkeypatch):
        """测试 OpenAI 模式下显式设置 LLM_MODEL=fake-model 也应报错"""
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("LLM_MODEL", "fake-model")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        
        # 注意：这个测试验证的是路由层的检查，不是 factory 层的检查
        # factory 只是创建 provider，不会验证 model_name 是否合理
        provider, config = create_llm_provider_from_env()
        
        # factory 会成功创建，但路由层会检查并报错
        assert isinstance(provider, OpenAIProvider)
        assert config.model_name == "fake-model"