# Semantic Review Module - 中文语义审核模块
"""
输入最小集合:
- content
- prototype_hint
- register
- audience
- context_metadata

输出最小集合:
- passed
- severity_summary
- findings
- rewrite_target
- prototype_alignment

公开接口:
- SemanticReviewInput: 审核输入模型
- SemanticReviewOutput: 审核输出模型
- SemanticReviewer: 语义审核器
- SemanticReviewerConfig: 审核器配置
- 错误类型: SemanticReviewError, ContentTooShortError, ReviewGenerationError
"""

# 数据模型
from .models import (
    SemanticReviewInput,
    SemanticReviewOutput,
    FindingOutput,
    SeveritySummaryOutput,
    RewriteTargetOutput,
    PrototypeAlignmentOutput,
)

# 配置
from .config import SemanticReviewerConfig

# 错误
from .errors import (
    SemanticReviewError,
    ContentTooShortError,
    ReviewGenerationError,
)

# 审核器
from .reviewer import SemanticReviewer

__all__ = [
    # 数据模型
    "SemanticReviewInput",
    "SemanticReviewOutput",
    "FindingOutput",
    "SeveritySummaryOutput",
    "RewriteTargetOutput",
    "PrototypeAlignmentOutput",
    # 配置
    "SemanticReviewerConfig",
    # 错误
    "SemanticReviewError",
    "ContentTooShortError",
    "ReviewGenerationError",
    # 审核器
    "SemanticReviewer",
]