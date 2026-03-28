"""
Opinion Module 配置

定义医学观点产出模块的配置结构。
"""
from pydantic import BaseModel, ConfigDict, Field


class OpinionGeneratorConfig(BaseModel):
    """
    Opinion Generator 配置
    
    配置严格模式，禁止额外字段。
    
    Attributes:
        min_confidence: 最小置信度阈值
        max_support_points: 最大支撑点数量
        require_evidence_mapping: 是否要求证据映射
    """
    model_config = ConfigDict(extra="forbid")
    
    min_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="最小置信度阈值"
    )
    max_support_points: int = Field(
        default=5,
        ge=1,
        le=10,
        description="最大支撑点数量"
    )
    require_evidence_mapping: bool = Field(
        default=True,
        description="是否要求证据映射"
    )