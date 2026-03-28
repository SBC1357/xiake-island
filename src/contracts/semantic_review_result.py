"""
Semantic Review Result Contract

模块结果类 contract，用于表达中文语义审核结果。

根据施工图纸，输出最小集合:
- passed: 是否通过审核
- severity_summary: 严重性摘要
- findings: 审核发现的问题列表
- rewrite_target: 改写目标
- prototype_alignment: 原型对齐情况

命名约定: {module}_{result} 风格 (模块结果类)
"""
from typing import Optional, Any
from pydantic import Field
from .base import ContractBaseModel, ErrorSeverity


class FindingItem(ContractBaseModel):
    """
    审核发现项
    
    表达单个审核发现的问题。
    
    Attributes:
        severity: 严重级别
        category: 问题类别
        description: 问题描述
        location: 问题位置 (行号、段落等)
        suggestion: 修改建议
    """
    
    severity: ErrorSeverity = Field(
        ...,
        description="严重级别"
    )
    category: str = Field(
        ...,
        description="问题类别"
    )
    description: str = Field(
        ...,
        description="问题描述"
    )
    location: Optional[str] = Field(
        default=None,
        description="问题位置 (行号、段落等)"
    )
    suggestion: Optional[str] = Field(
        default=None,
        description="修改建议"
    )


class SeveritySummary(ContractBaseModel):
    """
    严重性摘要
    
    汇总各级别问题的数量。
    
    Attributes:
        low: 低严重性问题数量
        medium: 中严重性问题数量
        high: 高严重性问题数量
        critical: 严重问题数量
    """
    
    low: int = Field(default=0, ge=0, description="低严重性问题数量")
    medium: int = Field(default=0, ge=0, description="中严重性问题数量")
    high: int = Field(default=0, ge=0, description="高严重性问题数量")
    critical: int = Field(default=0, ge=0, description="严重问题数量")


class PrototypeAlignment(ContractBaseModel):
    """
    原型对齐情况
    
    表达内容与原型的对齐程度。
    
    Attributes:
        score: 对齐分数 (0-100)
        matched_rules: 匹配的规则列表
        unmatched_rules: 未匹配的规则列表
        notes: 对齐说明
    """
    
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="对齐分数 (0-100)"
    )
    matched_rules: list[str] = Field(
        default_factory=list,
        description="匹配的规则列表"
    )
    unmatched_rules: list[str] = Field(
        default_factory=list,
        description="未匹配的规则列表"
    )
    notes: Optional[str] = Field(
        default=None,
        description="对齐说明"
    )


class RewriteTarget(ContractBaseModel):
    """
    改写目标
    
    表达需要改写的目标内容。
    
    Attributes:
        original: 原始内容
        suggested: 建议改写内容
        reason: 改写原因
        priority: 改写优先级
    """
    
    original: str = Field(..., description="原始内容")
    suggested: str = Field(..., description="建议改写内容")
    reason: str = Field(..., description="改写原因")
    priority: ErrorSeverity = Field(
        default=ErrorSeverity.MEDIUM,
        description="改写优先级"
    )


class SemanticReviewResult(ContractBaseModel):
    """
    语义审核结果
    
    用于表达中文语义审核的完整结果。
    
    Attributes:
        passed: 是否通过审核
        severity_summary: 严重性摘要
        findings: 审核发现的问题列表
        rewrite_target: 改写目标列表
        prototype_alignment: 原型对齐情况
    """
    
    passed: bool = Field(
        ...,
        description="是否通过审核"
    )
    severity_summary: SeveritySummary = Field(
        default_factory=SeveritySummary,
        description="严重性摘要"
    )
    findings: list[FindingItem] = Field(
        default_factory=list,
        description="审核发现的问题列表"
    )
    rewrite_target: list[RewriteTarget] = Field(
        default_factory=list,
        description="改写目标列表"
    )
    prototype_alignment: Optional[PrototypeAlignment] = Field(
        default=None,
        description="原型对齐情况"
    )