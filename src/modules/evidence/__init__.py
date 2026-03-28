"""
Evidence Module

证据管理能力，接入 V2 evidence/resolver。

SP-6 Batch 6A: 新增检索追踪模型支持显式取证决策链。
"""
from .models import SourceRecord, AssetRecord, FactRecord, SourceType, AssetType, FactStatus
from .service import EvidenceService
from .retrieval_trace import (
    RetrievalTrace,
    QueryInput,
    FilterDecision,
    RankingDecision,
    DedupDecision,
    SelectionDecision,
    SufficiencyJudgment,
    FilterType,
    SelectionReason,
    EvidenceResultWithTrace,
)

__all__ = [
    # 原有导出
    "SourceRecord",
    "AssetRecord",
    "FactRecord",
    "SourceType",
    "AssetType",
    "FactStatus",
    "EvidenceService",
    # SP-6 Batch 6A: 检索追踪模型
    "RetrievalTrace",
    "QueryInput",
    "FilterDecision",
    "RankingDecision",
    "DedupDecision",
    "SelectionDecision",
    "SufficiencyJudgment",
    "FilterType",
    "SelectionReason",
    "EvidenceResultWithTrace",
]