"""
Opinion Module 数据模型

定义医学观点产出模块的输入输出数据结构。
"""
from typing import Optional, Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    """
    证据项
    
    单条证据的基本结构。
    
    Attributes:
        id: 证据唯一标识
        content: 证据内容
        source: 证据来源
        relevance: 相关性评分 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    id: str = Field(..., description="证据唯一标识")
    content: str = Field(..., description="证据内容")
    source: Optional[str] = Field(default=None, description="证据来源")
    relevance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="相关性评分"
    )


class EvidenceBundle(BaseModel):
    """
    证据包
    
    包含多条相关证据的集合。
    
    Attributes:
        items: 证据项列表
        summary: 证据摘要 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    items: list[EvidenceItem] = Field(
        default_factory=list,
        description="证据项列表"
    )
    summary: Optional[str] = Field(default=None, description="证据摘要")


class OpinionInput(BaseModel):
    """
    Opinion Module 输入
    
    Attributes:
        evidence_bundle: 证据包
        audience: 目标受众
        thesis_hint: 观点提示 (可选)
        context_metadata: 上下文元数据 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    evidence_bundle: EvidenceBundle = Field(
        ...,
        description="证据包"
    )
    audience: str = Field(
        ...,
        min_length=1,
        description="目标受众"
    )
    thesis_hint: Optional[str] = Field(
        default=None,
        description="观点提示"
    )
    context_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="上下文元数据"
    )


class ThesisOutput(BaseModel):
    """
    观点论题输出
    
    Attributes:
        statement: 观点陈述
        confidence: 置信度 (0-1)
        evidence_refs: 证据引用列表
    """
    model_config = ConfigDict(extra="forbid")
    
    statement: str = Field(..., description="观点陈述")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="置信度"
    )
    evidence_refs: list[str] = Field(
        default_factory=list,
        description="证据引用列表"
    )


class SupportPointOutput(BaseModel):
    """
    支撑点输出
    
    Attributes:
        content: 支撑内容
        strength: 支撑强度
        evidence_id: 关联证据ID
    """
    model_config = ConfigDict(extra="forbid")
    
    content: str = Field(..., description="支撑内容")
    strength: Literal["weak", "medium", "strong"] = Field(
        default="medium",
        description="支撑强度"
    )
    evidence_id: Optional[str] = Field(
        default=None,
        description="关联证据ID"
    )


class EvidenceMapping(BaseModel):
    """
    证据映射
    
    记录观点各部分与原始证据的对应关系。
    
    Attributes:
        thesis_evidence: 论题引用的证据ID列表
        support_evidence: 各支撑点引用的证据ID
    """
    model_config = ConfigDict(extra="forbid")
    
    thesis_evidence: list[str] = Field(
        default_factory=list,
        description="论题引用的证据ID列表"
    )
    support_evidence: dict[str, list[str]] = Field(
        default_factory=dict,
        description="各支撑点引用的证据ID"
    )


class ConfidenceNotes(BaseModel):
    """
    置信度说明
    
    解释置信度评估的依据和限制。
    
    Attributes:
        overall_confidence: 整体置信度
        limitations: 局限性说明
        assumptions: 假设条件
    """
    model_config = ConfigDict(extra="forbid")
    
    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="整体置信度"
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="局限性说明"
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="假设条件"
    )


class OpinionOutput(BaseModel):
    """
    Opinion Module 输出
    
    Attributes:
        thesis: 核心观点
        support_points: 支撑点列表
        boundaries: 边界限制
        evidence_mapping: 证据映射
        confidence_notes: 置信度说明
    """
    model_config = ConfigDict(extra="forbid")
    
    thesis: ThesisOutput = Field(..., description="核心观点")
    support_points: list[SupportPointOutput] = Field(
        default_factory=list,
        description="支撑点列表"
    )
    boundaries: Optional[dict[str, Any]] = Field(
        default=None,
        description="边界限制"
    )
    evidence_mapping: Optional[EvidenceMapping] = Field(
        default=None,
        description="证据映射"
    )
    confidence_notes: Optional[ConfidenceNotes] = Field(
        default=None,
        description="置信度说明"
    )