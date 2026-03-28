"""
Opinion to Write Contract

Handoff 类 contract，用于从 opinion 模块传递到 writing 模块。
先按 handoff contract 处理，保持最小但清晰。

命名约定: {source}_to_{target} 风格 (handoff 类)
"""
from typing import Optional, Any, Literal
from pydantic import Field
from .base import ContractBaseModel


class Thesis(ContractBaseModel):
    """
    观点论题
    
    表达核心观点和论据结构。
    
    Attributes:
        statement: 观点陈述
        confidence: 置信度 (0-1)
        evidence_refs: 证据引用列表
    """
    
    statement: str = Field(..., description="观点陈述")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="置信度 (0-1)"
    )
    evidence_refs: list[str] = Field(
        default_factory=list,
        description="证据引用列表"
    )


class SupportPoint(ContractBaseModel):
    """
    支撑点
    
    表达支撑观点的论据。
    
    Attributes:
        content: 支撑内容
        strength: 支撑强度 (weak/medium/strong)
        evidence_id: 关联证据ID
    """
    
    content: str = Field(..., description="支撑内容")
    strength: Literal["weak", "medium", "strong"] = Field(
        default="medium",
        description="支撑强度"
    )
    evidence_id: Optional[str] = Field(
        default=None,
        description="关联证据ID"
    )


class OpinionToWrite(ContractBaseModel):
    """
    观点到写作的 handoff 结构
    
    用于从 opinion 模块传递结果到 writing 模块。
    保持最小但清晰，待业务实现阶段细化。
    
    Attributes:
        thesis: 核心观点
        support_points: 支撑点列表
        audience: 目标受众
        style_hint: 风格提示
        boundaries: 边界限制
        context: 上下文信息
    """
    
    thesis: Thesis = Field(
        ...,
        description="核心观点"
    )
    support_points: list[SupportPoint] = Field(
        default_factory=list,
        description="支撑点列表"
    )
    audience: str = Field(
        ...,
        description="目标受众"
    )
    style_hint: Optional[str] = Field(
        default=None,
        description="风格提示"
    )
    boundaries: Optional[dict[str, Any]] = Field(
        default=None,
        description="边界限制，待业务实现阶段细化"
    )
    context: Optional[dict[str, Any]] = Field(
        default=None,
        description="上下文信息，待业务实现阶段细化"
    )