"""
LLM Gateway 数据模型

定义 LLM 请求和响应的数据结构。
支持纯文本和多模态(视觉)两种请求模式。
"""
from typing import Optional, Any, List
from pydantic import BaseModel, ConfigDict, Field


class LLMUsage(BaseModel):
    """
    LLM 使用统计
    
    记录 token 使用量等成本相关信息。
    
    Attributes:
        prompt_tokens: 提示词 token 数量
        completion_tokens: 完成 token 数量
        total_tokens: 总 token 数量
    """
    model_config = ConfigDict(extra="forbid")
    
    prompt_tokens: int = Field(
        default=0,
        ge=0,
        description="提示词 token 数量"
    )
    completion_tokens: int = Field(
        default=0,
        ge=0,
        description="完成 token 数量"
    )
    total_tokens: int = Field(
        default=0,
        ge=0,
        description="总 token 数量"
    )


class LLMRequest(BaseModel):
    """
    LLM 请求
    
    统一的 LLM 请求结构。
    
    Attributes:
        prompt: 用户提示词
        system_prompt: 系统提示词 (可选)
        temperature: 温度参数 (可选)
        max_tokens: 最大生成 token 数 (可选)
        metadata: 请求元数据 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    prompt: str = Field(
        ...,
        min_length=1,
        description="用户提示词"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="系统提示词"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="温度参数"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="最大生成 token 数"
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="请求元数据"
    )


class LLMResponse(BaseModel):
    """
    LLM 响应
    
    统一的 LLM 响应结构。
    
    Attributes:
        content: 生成的文本内容
        provider: 提供商名称
        model: 模型名称
        latency_ms: 响应延迟 (毫秒)
        finish_reason: 完成原因 (可选)
        usage: 使用统计 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    content: str = Field(
        ...,
        description="生成的文本内容"
    )
    provider: str = Field(
        ...,
        description="提供商名称"
    )
    model: str = Field(
        ...,
        description="模型名称"
    )
    latency_ms: int = Field(
        ...,
        ge=0,
        description="响应延迟 (毫秒)"
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description="完成原因"
    )
    usage: Optional[LLMUsage] = Field(
        default=None,
        description="使用统计"
    )


# ==================== 多模态/视觉模型扩展 ====================


class ImageContent(BaseModel):
    """
    图像内容 — 用于视觉模型调用

    支持 base64 编码的图像数据，或图像 URL。
    """
    model_config = ConfigDict(extra="forbid")

    base64_data: Optional[str] = Field(
        default=None,
        description="Base64 编码的图像数据"
    )
    image_url: Optional[str] = Field(
        default=None,
        description="图像 URL（仅限内部存储路径）"
    )
    media_type: str = Field(
        default="image/png",
        description="图像 MIME 类型 (image/png, image/jpeg)"
    )
    page_number: Optional[int] = Field(
        default=None,
        description="所属页码（文档转换时自动设置）"
    )


class VisionRequest(BaseModel):
    """
    视觉模型请求

    独立于文本 LLMRequest 的多模态请求结构。
    支持图像输入 + 文本提示词的组合。
    """
    model_config = ConfigDict(extra="forbid")

    images: List[ImageContent] = Field(
        ...,
        min_length=1,
        description="待识别的图像列表"
    )
    prompt: str = Field(
        default="请识别并提取这些图像中的所有文本内容、表格数据和关键信息，以结构化 JSON 格式返回。",
        min_length=1,
        description="识别提示词"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="系统提示词"
    )
    temperature: Optional[float] = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="温度参数（视觉识别建议低温）"
    )
    max_tokens: Optional[int] = Field(
        default=4096,
        ge=1,
        description="最大生成 token 数"
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="请求元数据"
    )