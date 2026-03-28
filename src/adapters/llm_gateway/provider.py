"""
LLM Provider 协议

定义 LLM Provider 的统一接口。
支持文本生成和视觉识别两种模式。
"""
from abc import ABC, abstractmethod

from .models import LLMRequest, LLMResponse, VisionRequest
from .config import LLMGatewayConfig


class LLMProvider(ABC):
    """
    LLM Provider 抽象基类
    
    定义所有 LLM Provider 必须实现的接口。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Provider 名称
        
        Returns:
            Provider 名称字符串
        """
        pass
    
    @abstractmethod
    def generate(
        self,
        request: LLMRequest,
        config: LLMGatewayConfig
    ) -> LLMResponse:
        """
        生成 LLM 响应
        
        Args:
            request: LLM 请求
            config: Gateway 配置
            
        Returns:
            LLM 响应
            
        Raises:
            LLMTimeoutError: 调用超时
            LLMProviderError: 提供商错误
        """
        pass


class VisionProvider(ABC):
    """
    视觉模型 Provider 抽象基类

    独立于文本 LLMProvider，避免影响现有文本调用链。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def recognize(
        self,
        request: VisionRequest,
        config: LLMGatewayConfig
    ) -> LLMResponse:
        """
        视觉识别

        Args:
            request: 视觉请求（含图像 + 提示词）
            config: Gateway 配置

        Returns:
            LLM 响应（content 为识别结果的结构化文本）
        """
        pass