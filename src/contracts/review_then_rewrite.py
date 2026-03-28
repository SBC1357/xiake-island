"""
Review then Rewrite Contract

Handoff 类 contract，用于从 semantic_review 模块传递到 writing 模块。
先按 handoff contract 处理，保持最小但清晰。

命名约定: {source}_to_{target} 风格 (handoff 类)
"""
from typing import Optional
from pydantic import Field
from .base import ContractBaseModel
from .semantic_review_result import RewriteTarget, SeveritySummary


class ReviewThenRewrite(ContractBaseModel):
    """
    审核后改写的 handoff 结构
    
    用于从 semantic_review 模块传递结果到 writing 模块。
    保持最小但清晰，待业务实现阶段细化。
    
    Attributes:
        original_content: 原始内容
        rewrite_targets: 改写目标列表
        severity_summary: 严重性摘要
        passed: 是否通过审核
        review_notes: 审核说明
        preserve_sections: 需要保留的段落标记
    """
    
    original_content: str = Field(
        ...,
        description="原始内容"
    )
    rewrite_targets: list[RewriteTarget] = Field(
        default_factory=list,
        description="改写目标列表"
    )
    severity_summary: SeveritySummary = Field(
        default_factory=SeveritySummary,
        description="严重性摘要"
    )
    passed: bool = Field(
        ...,
        description="是否通过审核"
    )
    review_notes: Optional[str] = Field(
        default=None,
        description="审核说明"
    )
    preserve_sections: list[str] = Field(
        default_factory=list,
        description="需要保留的段落标记"
    )