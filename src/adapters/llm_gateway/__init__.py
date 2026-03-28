# LLM Gateway - LLM 网关
"""
职责:
- 统一封装模型调用
- 管理模型配置
- 管理超时、重试、错误归因
- 为不同模块提供一致的模型执行接口
- 支持文本和视觉(多模态)两种调用路径

首阶段策略:
1. 默认采用单 provider、单主模型策略
2. 所有 prompt 模板与模型参数必须版本化
3. 必须记录模型名、耗时、失败原因和基础成本信息
4. 复杂多模型路由与回退策略后移到独立 ADR
5. 视觉模型独立于文本模型，使用独立配置槽位

公开接口:
- LLMRequest: LLM 请求模型
- LLMResponse: LLM 响应模型
- LLMUsage: 使用统计
- ImageContent: 图像内容（视觉模型）
- VisionRequest: 视觉模型请求
- LLMGatewayConfig: Gateway 配置
- LLMProvider: Provider 协议
- VisionProvider: 视觉 Provider 协议
- FakeLLMProvider: 假 Provider (用于测试)
- OpenAIProvider: OpenAI Provider (真实调用)
- OpenAIVisionProvider: 视觉模型 Provider
- LLMGateway: Gateway 入口
- create_llm_provider: Provider 工厂函数
- create_llm_provider_from_env: 从环境变量创建 Provider
- create_vision_provider_from_env: 从环境变量创建视觉 Provider
- 错误类型: LLMGatewayError, LLMTimeoutError, LLMProviderError, LLMRetryExceededError
"""

# 数据模型
from .models import LLMRequest, LLMResponse, LLMUsage, ImageContent, VisionRequest

# 配置
from .config import LLMGatewayConfig

# 错误
from .errors import (
    LLMGatewayError,
    LLMTimeoutError,
    LLMProviderError,
    LLMRetryExceededError,
)

# Provider 协议和实现
from .provider import LLMProvider, VisionProvider
from .fake_provider import FakeLLMProvider
from .openai_provider import OpenAIProvider
from .vision_provider import OpenAIVisionProvider

# Provider 工厂
from .provider_factory import (
    create_llm_provider,
    create_llm_provider_from_env,
    create_vision_provider_from_env,
)

# Gateway
from .gateway import LLMGateway

__all__ = [
    # 数据模型
    "LLMRequest",
    "LLMResponse",
    "LLMUsage",
    # 配置
    "LLMGatewayConfig",
    # 错误
    "LLMGatewayError",
    "LLMTimeoutError",
    "LLMProviderError",
    "LLMRetryExceededError",
    # Provider
    "LLMProvider",
    "FakeLLMProvider",
    "OpenAIProvider",
    # Provider 工厂
    "create_llm_provider",
    "create_llm_provider_from_env",
    # Gateway
    "LLMGateway",
]