"""
LLM Provider 工厂

根据配置创建对应的 LLM Provider 实例。
支持文本 Provider 和视觉 Provider 两种创建路径。
"""
import os
from typing import Optional

from .config import LLMGatewayConfig
from .provider import LLMProvider, VisionProvider
from .fake_provider import FakeLLMProvider
from .openai_provider import OpenAIProvider
from .vision_provider import OpenAIVisionProvider


def create_llm_provider(
    config: LLMGatewayConfig,
    fake_response_content: Optional[str] = None
) -> LLMProvider:
    """
    创建 LLM Provider 实例
    
    根据配置的 provider_name 创建对应的 Provider。
    
    Args:
        config: LLM Gateway 配置
        fake_response_content: Fake Provider 的响应内容（仅当 provider_name="fake" 时使用）
        
    Returns:
        LLM Provider 实例
        
    Raises:
        ValueError: 未知的 provider_name
    """
    provider_name = config.provider_name.lower()
    
    if provider_name == "fake":
        # Fake Provider 用于开发和测试
        return FakeLLMProvider(
            name="fake",
            response_content=fake_response_content or "This is a fake response."
        )
    
    elif provider_name == "openai":
        # OpenAI Provider 用于真实调用
        return OpenAIProvider(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    else:
        raise ValueError(
            f"Unknown provider: {config.provider_name}. "
            f"Supported providers: 'fake', 'openai'"
        )


def create_llm_provider_from_env(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None
) -> tuple[LLMProvider, LLMGatewayConfig]:
    """
    从环境变量创建 LLM Provider 和配置
    
    优先从环境变量读取配置，未设置时使用默认值。
    
    Args:
        provider_name: 提供商名称 (可选，默认从环境变量或 "fake")
        model_name: 模型名称 (可选，默认从环境变量读取)
        
    Returns:
        (Provider 实例, Gateway 配置) 元组
        
    Raises:
        ValueError: OpenAI 模式下未设置 LLM_MODEL
    """
    import os
    
    # 从环境变量读取 provider
    _provider_name = provider_name or os.environ.get("LLM_PROVIDER", "fake")
    _provider_name = _provider_name.lower()
    
    # 从环境变量读取 model_name，openai 模式下无默认值
    if model_name:
        _model_name = model_name
    elif os.environ.get("LLM_MODEL"):
        _model_name = os.environ.get("LLM_MODEL")
    elif _provider_name == "openai":
        # OpenAI 模式下必须显式设置模型名
        raise ValueError(
            "LLM_MODEL environment variable must be set when using OpenAI provider. "
            "Example: export LLM_MODEL=gpt-3.5-turbo"
        )
    else:
        # Fake 模式下使用默认值
        _model_name = "fake-model"
    
    # 创建配置
    config = LLMGatewayConfig(
        provider_name=_provider_name,
        model_name=_model_name,
        api_key=os.environ.get("OPENAI_API_KEY") if _provider_name == "openai" else None,
        base_url=os.environ.get("OPENAI_BASE_URL") if _provider_name == "openai" else None,
        timeout_seconds=float(os.environ.get("LLM_TIMEOUT_SECONDS", "30.0")),
        max_retries=int(os.environ.get("LLM_MAX_RETRIES", "3"))
    )
    
    # 创建 Provider
    provider = create_llm_provider(config)
    
    return provider, config


def create_vision_provider_from_env() -> tuple[VisionProvider, LLMGatewayConfig]:
    """
    从环境变量创建 Vision Provider 和配置

    独立于文本模型，使用 VISION_MODEL / VISION_API_KEY / VISION_BASE_URL。
    如果未设置 VISION_* 前缀的变量，回退到 OPENAI_* 变量。

    Returns:
        (VisionProvider 实例, Gateway 配置) 元组
    """
    vision_model = os.environ.get("VISION_MODEL", "")
    if not vision_model:
        raise ValueError(
            "VISION_MODEL environment variable must be set for vision recognition. "
            "Example: VISION_MODEL=gpt-4o"
        )

    api_key = os.environ.get("VISION_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("VISION_BASE_URL") or os.environ.get("OPENAI_BASE_URL")

    config = LLMGatewayConfig(
        provider_name="openai_vision",
        model_name=vision_model,
        api_key=api_key,
        base_url=base_url,
        timeout_seconds=float(os.environ.get("VISION_TIMEOUT_SECONDS", "120.0")),
        max_retries=int(os.environ.get("VISION_MAX_RETRIES", "2")),
    )

    provider = OpenAIVisionProvider(
        api_key=api_key,
        base_url=base_url,
    )

    return provider, config