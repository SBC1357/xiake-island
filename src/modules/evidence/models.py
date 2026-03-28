"""
Evidence Models

定义证据管理的数据模型，与 V2 契约兼容。
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """来源类型"""
    PDF = "pdf"
    PPTX = "pptx"
    WEB = "web"
    DATABASE = "database"
    MANUAL = "manual"


class AssetType(str, Enum):
    """资产类型"""
    DOCUMENT = "document"
    IMAGE = "image"
    TABLE = "table"
    CHART = "chart"
    SNAPSHOT = "snapshot"


class FactStatus(str, Enum):
    """事实状态"""
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    CONFLICTED = "conflicted"
    REVIEWED = "reviewed"
    DRAFT = "draft"


@dataclass
class SourceRecord:
    """
    来源记录
    
    与 V2 SourceRecord 契约兼容。
    """
    source_id: str
    source_type: SourceType
    title: str
    product_id: Optional[str] = None
    source_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AssetRecord:
    """
    资产记录
    
    与 V2 AssetRecord 契约兼容。
    """
    asset_id: str
    source_id: str
    asset_type: AssetType
    title: str
    storage_key: Optional[str] = None
    content_hash: Optional[str] = None
    page_range: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FactRecord:
    """
    事实记录
    
    与 V2 FactRecord 契约兼容。
    """
    fact_id: str
    product_id: str
    domain: str
    fact_key: str
    value: Any
    definition: Optional[str] = None
    definition_zh: Optional[str] = None
    unit: Optional[str] = None
    status: FactStatus = FactStatus.ACTIVE
    lineage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)