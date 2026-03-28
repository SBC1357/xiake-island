# Opinion Module - 医学观点产出模块
"""
输入最小集合:
- source_packet 或 evidence_bundle
- audience
- thesis_hint
- context_metadata

输出最小集合:
- thesis
- support_points
- boundaries
- evidence_mapping
- confidence_notes

公开接口:
- OpinionInput: 观点输入模型
- OpinionOutput: 观点输出模型
- EvidenceBundle: 证据包
- EvidenceItem: 证据项
- OpinionGenerator: 观点生成器
- OpinionGeneratorConfig: 生成器配置
- 错误类型: OpinionModuleError, InsufficientEvidenceError, ConfidenceTooLowError, OpinionGenerationError
"""

# 数据模型
from .models import (
    EvidenceItem,
    EvidenceBundle,
    OpinionInput,
    ThesisOutput,
    SupportPointOutput,
    EvidenceMapping,
    ConfidenceNotes,
    OpinionOutput,
)

# 配置
from .config import OpinionGeneratorConfig

# 错误
from .errors import (
    OpinionModuleError,
    InsufficientEvidenceError,
    ConfidenceTooLowError,
    OpinionGenerationError,
)

# 生成器
from .generator import OpinionGenerator

__all__ = [
    # 数据模型
    "EvidenceItem",
    "EvidenceBundle",
    "OpinionInput",
    "ThesisOutput",
    "SupportPointOutput",
    "EvidenceMapping",
    "ConfidenceNotes",
    "OpinionOutput",
    # 配置
    "OpinionGeneratorConfig",
    # 错误
    "OpinionModuleError",
    "InsufficientEvidenceError",
    "ConfidenceTooLowError",
    "OpinionGenerationError",
    # 生成器
    "OpinionGenerator",
]