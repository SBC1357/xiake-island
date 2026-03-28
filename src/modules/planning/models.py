"""
Planning Models

定义规划模块的数据模型，与 V2 契约兼容。
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class VoiceStyle(str, Enum):
    """声音风格"""
    PUNCHY = "punchy"
    ANALYTICAL = "analytical"
    COMPASSIONATE = "compassionate"
    CRITICAL = "critical"
    PREDICTIVE = "predictive"
    DRAMATIC = "dramatic"
    DATA_DRIVEN = "data_driven"
    CYNICAL = "cynical"


class EmotionalTemperature(str, Enum):
    """情感温度"""
    DRAMATIC_PROVOCATIVE = "dramatic_provocative"
    COMPASSIONATE_RATIONAL = "compassionate_rational"
    NEUTRAL_OBJECTIVE = "neutral_objective"
    WARM_EDUCATIONAL = "warm_educational"


# ==================== Pydantic 模型 (用于 API) ====================

class RouteContextRequest(BaseModel):
    """路由上下文请求"""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    product_id: str = Field(..., description="产品标识符")
    tone_register: str = Field(
        default="R2",
        alias="register",
        serialization_alias="register",
        description="语体等级 (R1-R5)",
    )
    audience: Optional[str] = Field(default=None, description="目标受众")
    project_name: Optional[str] = Field(default=None, description="项目名称")
    deliverable_type: Optional[str] = Field(default=None, description="交付物类型")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    @property
    def register(self) -> str:
        return self.tone_register


class OutlineItemResponse(BaseModel):
    """大纲项响应"""
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(..., description="章节标题")
    type: str = Field(..., description="章节类型")
    domain: Optional[str] = Field(default=None, description="领域 (domain_section 类型)")
    fact_count: Optional[int] = Field(default=None, description="证据数量")
    fact_id: Optional[str] = Field(default=None, description="证据ID (evidence 类型)")


class EditorialPlanResponse(BaseModel):
    """
    编辑计划响应
    
    SP-6 Batch 6C: 新增 target_word_count 可选字段。
    """
    model_config = ConfigDict(extra="forbid")
    
    thesis: str = Field(..., description="核心论点")
    outline: List[OutlineItemResponse] = Field(default_factory=list, description="文章大纲")
    play_id: Optional[str] = Field(default=None, description="写作策略ID")
    arc_id: Optional[str] = Field(default=None, description="叙事弧线ID")
    target_audience: Optional[str] = Field(default=None, description="目标受众")
    key_evidence: List[str] = Field(default_factory=list, description="核心证据")
    style_notes: Dict[str, Any] = Field(default_factory=dict, description="风格注释")
    target_word_count: Optional[int] = Field(default=None, description="目标字数")
    section_word_budget: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="章节篇幅分配，每项含 section_title、target_words、ratio"
    )


class PersonaProfileResponse(BaseModel):
    """人格画像响应"""
    model_config = ConfigDict(extra="forbid")
    
    profile_id: str = Field(..., description="画像ID")
    author_id: str = Field(..., description="作者ID")
    author_name: str = Field(..., description="作者名称")
    domain: str = Field(..., description="领域")
    tone: str = Field(..., description="基调")
    voice_styles: List[str] = Field(default_factory=list, description="声音风格")
    signature_phrases: List[str] = Field(default_factory=list, description="签名短语")


# ==================== 内部数据类 (用于服务层) ====================

@dataclass
class RouteContext:
    """
    路由上下文 - 任务启动参数
    
    与 V2 RouteContext 契约兼容。
    """
    product_id: str
    register: str = "R2"
    audience: Optional[str] = None
    task_id: str = field(default_factory=lambda: f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    project_name: Optional[str] = None
    deliverable_type: Optional[str] = None
    task_category: str = "project"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """验证register值"""
        valid_registers = ['R1', 'R2', 'R3', 'R4', 'R5']
        if self.register not in valid_registers:
            raise ValueError(f"register必须是 {valid_registers} 之一，当前: {self.register}")


@dataclass
class EditorialPlan:
    """
    编辑计划
    
    与 V2 EditorialPlan 契约兼容。
    
    SP-6 Batch 6C: 新增 target_word_count 可选字段。
    """
    thesis: str
    outline: List[Dict[str, Any]] = field(default_factory=list)
    play_id: Optional[str] = None
    arc_id: Optional[str] = None
    target_audience: Optional[str] = None
    key_evidence: List[str] = field(default_factory=list)
    style_notes: Dict[str, Any] = field(default_factory=dict)
    target_word_count: Optional[int] = None
    section_word_budget: Optional[List[Dict[str, Any]]] = None


@dataclass
class PersonaProfile:
    """
    人格画像
    
    与 V2 PersonaProfile 契约兼容。
    """
    profile_id: str
    author_id: str
    author_name: str
    domain: str
    tone: str = "professional"
    voice_styles: List[VoiceStyle] = field(default_factory=list)
    signature_phrases: List[str] = field(default_factory=list)
    vocabulary_bias: List[str] = field(default_factory=list)
