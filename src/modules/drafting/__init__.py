"""
Drafting Module

独立成稿模块，负责从编译后的 Prompt 生成正文内容。

SP-7B: 新增模块，实现确定性 Fake 模式成稿 + OpenAI 真实成稿。
"""

from .models import DraftingInput, DraftingResult, DraftingTrace
from .service import DraftingService

__all__ = [
    "DraftingInput",
    "DraftingResult",
    "DraftingTrace",
    "DraftingService",
]
