"""
Asset Bridge 配置

通过配置注入四类根目录，不硬编码 V2 路径。
"""
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import AssetKind


class AssetBridgeConfig(BaseModel):
    """
    Asset Bridge 配置
    
    通过构造参数注入四类根目录路径。
    不硬编码 `medical_kb_system_v2` 目录到实现中。
    
    配置严格模式，禁止额外字段，避免拼写错误被静默忽略。
    
    Attributes:
        rules_root: 规则资产根目录 (可选)
        editorial_root: 编辑规范资产根目录 (可选)
        evidence_root: 证据资产根目录 (可选)
        structured_root: 结构化资产根目录 (可选)
    """
    model_config = ConfigDict(
        extra="forbid",  # 禁止额外字段，拼写错误会立即报错
    )
    
    rules_root: Optional[Path] = Field(
        default=None,
        description="规则资产根目录"
    )
    editorial_root: Optional[Path] = Field(
        default=None,
        description="编辑规范资产根目录"
    )
    evidence_root: Optional[Path] = Field(
        default=None,
        description="证据资产根目录"
    )
    structured_root: Optional[Path] = Field(
        default=None,
        description="结构化资产根目录"
    )
    consumer_root: Optional[Path] = Field(
        default=None,
        description="藏经阁发布物消费根目录 (publish/current/consumers/xiakedao/)"
    )
    
    @field_validator('rules_root', 'editorial_root', 'evidence_root', 'structured_root', 'consumer_root', mode='before')
    @classmethod
    def convert_to_path(cls, v):
        """将字符串路径转换为 Path 对象"""
        if v is None:
            return None
        if isinstance(v, str):
            return Path(v)
        return v
    
    def get_root(self, kind: AssetKind) -> Optional[Path]:
        """
        获取指定类别的根目录
        
        Args:
            kind: 资产类别
            
        Returns:
            根目录 Path，如果未配置则返回 None
        """
        mapping = {
            AssetKind.RULES: self.rules_root,
            AssetKind.EDITORIAL: self.editorial_root,
            AssetKind.EVIDENCE: self.evidence_root,
            AssetKind.STRUCTURED: self.structured_root,
            AssetKind.CONSUMER: self.consumer_root,
        }
        return mapping.get(kind)