"""
Semantic Review Module 数据模型

定义中文语义审核模块的输入输出数据结构。

SP-6 Batch 6B 新增:
- RuleLayerOutput: 规则层输出，区分规则层与模型层
- SemanticReviewOutput.rule_layer_output: 规则层执行结果
"""
from typing import Optional, Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class SemanticReviewInput(BaseModel):
    """
    语义审核输入
    
    Attributes:
        content: 待审核内容
        prototype_hint: 原型提示 (可选)
        register: 语体要求 (可选)
        audience: 目标受众
        context_metadata: 上下文元数据 (可选)
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    content: str = Field(
        ...,
        min_length=1,
        description="待审核内容"
    )
    prototype_hint: Optional[str] = Field(
        default=None,
        description="原型提示"
    )
    tone_register: Optional[str] = Field(
        default=None,
        alias="register",
        serialization_alias="register",
        description="语体要求"
    )
    audience: str = Field(
        ...,
        min_length=1,
        description="目标受众"
    )
    context_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="上下文元数据"
    )

    @property
    def register(self) -> Optional[str]:
        return self.tone_register


class FindingOutput(BaseModel):
    """
    审核发现项输出
    
    Attributes:
        severity: 严重级别 (low/medium/high/critical)
        category: 问题类别
        description: 问题描述
        location: 问题位置 (可选)
        suggestion: 修改建议 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ...,
        description="严重级别"
    )
    category: str = Field(..., description="问题类别")
    description: str = Field(..., description="问题描述")
    location: Optional[str] = Field(default=None, description="问题位置")
    suggestion: Optional[str] = Field(default=None, description="修改建议")


class SeveritySummaryOutput(BaseModel):
    """
    严重性摘要输出
    
    Attributes:
        low: 低严重性问题数量
        medium: 中严重性问题数量
        high: 高严重性问题数量
        critical: 严重问题数量
    """
    model_config = ConfigDict(extra="forbid")
    
    low: int = Field(default=0, ge=0, description="低严重性问题数量")
    medium: int = Field(default=0, ge=0, description="中严重性问题数量")
    high: int = Field(default=0, ge=0, description="高严重性问题数量")
    critical: int = Field(default=0, ge=0, description="严重问题数量")


class RewriteTargetOutput(BaseModel):
    """
    改写目标输出
    
    Attributes:
        original: 原始内容
        suggested: 建议改写内容
        reason: 改写原因
        priority: 改写优先级
    """
    model_config = ConfigDict(extra="forbid")
    
    original: str = Field(..., description="原始内容")
    suggested: str = Field(..., description="建议改写内容")
    reason: str = Field(..., description="改写原因")
    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="改写优先级"
    )


class PrototypeAlignmentOutput(BaseModel):
    """
    原型对齐情况输出
    
    Attributes:
        score: 对齐分数 (0-100)
        matched_rules: 匹配的规则列表
        unmatched_rules: 未匹配的规则列表
        notes: 对齐说明 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    score: int = Field(..., ge=0, le=100, description="对齐分数 (0-100)")
    matched_rules: list[str] = Field(
        default_factory=list,
        description="匹配的规则列表"
    )
    unmatched_rules: list[str] = Field(
        default_factory=list,
        description="未匹配的规则列表"
    )
    notes: Optional[str] = Field(default=None, description="对齐说明")


class SemanticReviewOutput(BaseModel):
    """
    语义审核输出
    
    SP-6 Batch 6B: 新增 rule_layer_output 字段，区分规则层与模型层。
    SP-6 Batch 6C: 新增 model_review_output, rewrite_layer_output, rerun_scope 字段，
                   显式暴露分层输出。
    
    Attributes:
        passed: 是否通过审核
        severity_summary: 严重性摘要
        findings: 审核发现的问题列表
        rewrite_target: 改写目标列表
        prototype_alignment: 原型对齐情况
        rule_layer_output: 规则层输出（确定性规则执行结果）
        model_review_output: 模型审校层输出（LLM 审核结果）
        rewrite_layer_output: 改写建议层输出
        rerun_scope: 重跑范围分类 (full_gate_rerun / partial_gate_rerun)
    """
    model_config = ConfigDict(extra="forbid")
    
    passed: bool = Field(..., description="是否通过审核")
    severity_summary: SeveritySummaryOutput = Field(
        default_factory=SeveritySummaryOutput,
        description="严重性摘要"
    )
    findings: list[FindingOutput] = Field(
        default_factory=list,
        description="审核发现的问题列表"
    )
    rewrite_target: list[RewriteTargetOutput] = Field(
        default_factory=list,
        description="改写目标列表"
    )
    prototype_alignment: Optional[PrototypeAlignmentOutput] = Field(
        default=None,
        description="原型对齐情况"
    )
    # SP-6 Batch 6B: 规则层输出
    rule_layer_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="规则层输出（确定性规则执行结果）"
    )
    # SP-6 Batch 6C: 模型审校层输出
    model_review_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="模型审校层输出（LLM 审核结果，包含 findings 和 severity_summary）"
    )
    # SP-6 Batch 6C: 改写建议层输出
    rewrite_layer_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="改写建议层输出（rewrite_target 的结构化表示）"
    )
    # SP-6 Batch 6C: 重跑范围分类
    rerun_scope: Optional[Literal["full_gate_rerun", "partial_gate_rerun"]] = Field(
        default=None,
        description="重跑范围分类"
    )
