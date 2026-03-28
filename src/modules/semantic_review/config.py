"""
Semantic Review Module 配置

定义语义审核模块的配置结构。
"""
from pydantic import BaseModel, ConfigDict, Field


class SemanticReviewerConfig(BaseModel):
    """
    语义审核器配置
    
    配置严格模式，禁止额外字段。
    
    Attributes:
        max_findings: 最大发现问题数量
        auto_pass_threshold: 自动通过阈值 (无 critical/high 问题)
        require_rewrite_targets: 是否要求改写目标
        require_prototype_alignment: 是否要求原型对齐
    """
    model_config = ConfigDict(extra="forbid")
    
    max_findings: int = Field(
        default=10,
        ge=1,
        le=50,
        description="最大发现问题数量"
    )
    auto_pass_threshold: bool = Field(
        default=True,
        description="自动通过阈值 (无 critical/high 问题时自动通过)"
    )
    require_rewrite_targets: bool = Field(
        default=True,
        description="是否要求改写目标"
    )
    require_prototype_alignment: bool = Field(
        default=False,
        description="是否要求原型对齐"
    )