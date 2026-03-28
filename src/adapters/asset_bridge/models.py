"""
Asset Bridge 数据模型

定义资产类别枚举和资产记录数据结构。
只做文本读取，不涉及业务语义解析。
"""
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import Field

from src.contracts.base import ContractBaseModel


class AssetKind(str, Enum):
    """
    资产类别枚举
    
    首批桥接资产类别:
    - rules: 规则资产
    - editorial: 编辑规范资产
    - evidence: 证据资产
    - structured: 结构化资产
    
    Phase 3 新增（藏经阁发布物消费）:
    - consumer: 藏经阁发布物消费目录
    """
    RULES = "rules"
    EDITORIAL = "editorial"
    EVIDENCE = "evidence"
    STRUCTURED = "structured"
    CONSUMER = "consumer"


class AssetTextRecord(ContractBaseModel):
    """
    资产文本记录
    
    表示从文件系统读取的文本资产记录。
    
    Attributes:
        kind: 资产类别
        relative_path: 相对于根目录的相对路径
        absolute_path: 文件的绝对路径
        content: 文件内容 (UTF-8 编码)
    """
    kind: AssetKind = Field(
        ...,
        description="资产类别"
    )
    relative_path: str = Field(
        ...,
        description="相对于根目录的相对路径"
    )
    absolute_path: str = Field(
        ...,
        description="文件的绝对路径"
    )
    content: str = Field(
        ...,
        description="文件内容 (UTF-8 编码)"
    )