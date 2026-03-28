"""
Writing Module

写作生成类能力，接入 V2 prompt/compiler。
"""
from .models import CompiledPrompt, CompiledPromptResponse
from .service import WritingService

__all__ = [
    "CompiledPrompt",
    "CompiledPromptResponse",
    "WritingService",
]