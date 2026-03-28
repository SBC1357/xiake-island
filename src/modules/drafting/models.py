"""
Drafting Models

定义独立成稿模块的数据模型。

SP-7B: 新增 DraftingInput, DraftingResult, DraftingTrace。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ==================== SP-7B: Drafting Trace ====================


@dataclass
class DraftingTrace:
    """
    成稿追踪

    SP-7B: 记录成稿过程的元数据。

    Attributes:
        prompt_tokens: 输入 token 数
        completion_tokens: 输出 token 数
        model_used: 使用的模型名称
        latency_ms: 生成耗时（毫秒）
        generation_mode: 生成模式 (fake / openai)
        deterministic_seed: 确定性种子（Fake 模式）
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    model_used: str = "unknown"
    latency_ms: int = 0
    generation_mode: str = "fake"
    deterministic_seed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "model_used": self.model_used,
            "latency_ms": self.latency_ms,
            "generation_mode": self.generation_mode,
            "deterministic_seed": self.deterministic_seed,
        }


# ==================== 内部数据类 (用于服务层) ====================


@dataclass
class DraftingInput:
    """
    成稿输入

    SP-7B: 从 Writing 模块接收编译后的 Prompt。

    Attributes:
        system_prompt: 系统级指令
        user_prompt: 用户级指令
        model_config: 模型配置（温度、最大 token 等）
        target_word_count: 目标字数（可选）
        metadata: 元数据（play_id, arc_id 等）
    """

    system_prompt: str
    user_prompt: str
    model_config: Dict[str, Any] = field(default_factory=dict)
    target_word_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DraftingResult:
    """
    成稿结果

    SP-7B: 返回生成的正文内容。

    Attributes:
        content: 生成的正文内容
        word_count: 正文字数
        trace: 成稿追踪
        metadata: 元数据
    """

    content: str
    word_count: int = 0
    trace: DraftingTrace = field(default_factory=DraftingTrace)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ==================== Pydantic 模型 (用于 API) ====================


class DraftingRequest(BaseModel):
    """
    成稿请求

    SP-7B: API 请求模型。
    """

    model_config = ConfigDict(extra="forbid")

    system_prompt: str = Field(..., description="系统级指令")
    user_prompt: str = Field(..., description="用户级指令")
    model_config_data: Dict[str, Any] = Field(
        default_factory=dict, description="模型配置"
    )
    target_word_count: Optional[int] = Field(default=None, description="目标字数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class DraftingResponse(BaseModel):
    """
    成稿响应

    SP-7B: API 响应模型，包含 task_id。
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(..., description="任务ID")
    content: str = Field(..., description="生成的正文内容")
    word_count: int = Field(..., description="正文字数")
    trace: Dict[str, Any] = Field(default_factory=dict, description="成稿追踪")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
