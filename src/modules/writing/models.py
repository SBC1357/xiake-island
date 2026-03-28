"""
Writing Models

定义写作模块的数据模型，与 V2 契约兼容。

SP-6 Batch 6C 新增:
- WritingTrace: 写作追踪，记录规划约束、证据锚点、应用的规则/风格
- CompiledPromptWithTrace: 带追踪的编译结果
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ==================== SP-6 Batch 6C: Writing Trace ====================

@dataclass
class PlanningConstraintsTrace:
    """
    规划约束追踪
    
    记录从规划阶段传入的约束信息。
    """
    thesis: Optional[str] = None
    outline: List[Dict[str, Any]] = field(default_factory=list)
    register: Optional[str] = None
    audience: Optional[str] = None
    style_notes: Dict[str, Any] = field(default_factory=dict)
    target_word_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "thesis": self.thesis,
            "outline": self.outline,
            "register": self.register,
            "audience": self.audience,
            "style_notes": self.style_notes,
            "target_word_count": self.target_word_count,
        }


@dataclass
class EvidenceAnchor:
    """
    证据锚点
    
    记录段落或章节引用的证据。
    """
    section_title: str
    section_index: int
    fact_ids: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_title": self.section_title,
            "section_index": self.section_index,
            "fact_ids": self.fact_ids,
            "domains": self.domains,
        }


@dataclass
class WritingTrace:
    """
    写作追踪
    
    SP-6 Batch 6C: 显式追踪写作输出的生成过程。
    
    Attributes:
        planning_constraints: 规划阶段传入的约束
        evidence_anchors: 各章节/段落的证据锚点
        applied_rule_ids: 应用的规则ID列表
        applied_style_ids: 应用的风格ID列表
        hard_constraints: 硬性约束（必须满足）
        advisory_constraints: 建议性约束（推荐满足）
    """
    planning_constraints: PlanningConstraintsTrace = field(default_factory=PlanningConstraintsTrace)
    evidence_anchors: List[EvidenceAnchor] = field(default_factory=list)
    applied_rule_ids: List[str] = field(default_factory=list)
    applied_style_ids: List[str] = field(default_factory=list)
    hard_constraints: List[str] = field(default_factory=list)
    advisory_constraints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "planning_constraints": self.planning_constraints.to_dict(),
            "evidence_anchors": [ea.to_dict() for ea in self.evidence_anchors],
            "applied_rule_ids": self.applied_rule_ids,
            "applied_style_ids": self.applied_style_ids,
            "hard_constraints": self.hard_constraints,
            "advisory_constraints": self.advisory_constraints,
        }


@dataclass
class CompiledPromptWithTrace:
    """
    带追踪的编译结果
    
    SP-6 Batch 6C: 返回编译后的 Prompt 及其追踪信息。
    """
    prompt: "CompiledPrompt"
    trace: WritingTrace


# ==================== Pydantic 模型 (用于 API) ====================

class ModelConfigResponse(BaseModel):
    """模型配置响应"""
    model_config = ConfigDict(extra="forbid")
    
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")


class CompiledPromptResponse(BaseModel):
    """编译后的Prompt响应"""
    model_config = ConfigDict(extra="forbid")
    
    system_prompt: str = Field(..., description="系统级指令")
    user_prompt: str = Field(..., description="用户级指令")
    model_config_data: ModelConfigResponse = Field(
        default_factory=ModelConfigResponse,
        description="模型配置"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="编译元数据")


class CompileRequest(BaseModel):
    """编译请求"""
    model_config = ConfigDict(extra="forbid")
    
    thesis: str = Field(..., description="核心论点")
    outline: List[Dict[str, Any]] = Field(default_factory=list, description="文章大纲")
    play_id: Optional[str] = Field(default=None, description="写作策略ID")
    arc_id: Optional[str] = Field(default=None, description="叙事弧线ID")
    target_audience: Optional[str] = Field(default=None, description="目标受众")
    key_evidence: List[str] = Field(default_factory=list, description="核心证据")
    style_notes: Dict[str, Any] = Field(default_factory=dict, description="风格注释")


# ==================== 内部数据类 (用于服务层) ====================

@dataclass
class CompiledPrompt:
    """
    编译后的Prompt
    
    与 V2 CompiledPrompt 契约兼容。
    """
    system_prompt: str
    user_prompt: str
    model_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_messages(self) -> list:
        """转换为OpenAI风格的messages格式"""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt}
        ]