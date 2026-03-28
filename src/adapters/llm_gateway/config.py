"""
LLM Gateway 配置

定义 LLM Gateway 的配置结构。
单 provider、单主模型策略。
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LLMGatewayConfig(BaseModel):
    """
    LLM Gateway 配置
    
    首阶段采用单 provider、单主模型策略。
    配置严格模式，禁止额外字段，避免拼写错误被静默忽略。
    
    Attributes:
        provider_name: 提供商名称 ("fake" 或 "openai")
        model_name: 模型名称
        api_key: API Key (可选，也可从环境变量读取)
        base_url: API Base URL (可选)
        timeout_seconds: 超时时间 (秒)
        max_retries: 最大重试次数
    """
    model_config = ConfigDict(
        extra="forbid",  # 禁止额外字段，拼写错误会立即报错
    )
    
    provider_name: str = Field(
        ...,
        min_length=1,
        description="提供商名称"
    )
    model_name: str = Field(
        ...,
        min_length=1,
        description="模型名称"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API Key (可选，也可从环境变量读取)"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="API Base URL (可选)"
    )
    timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        description="超时时间 (秒)"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="最大重试次数"
    )