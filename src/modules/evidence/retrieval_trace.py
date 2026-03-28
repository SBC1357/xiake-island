"""
Retrieval Trace Models

SP-6 Batch 6A: 显式取证 / 数据编排去黑箱

定义证据检索决策链的追踪模型，使证据选择过程可回看、可审计。
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class FilterType(str, Enum):
    """过滤类型"""
    DOMAIN = "domain"
    FACT_KEYS = "fact_keys"
    STATUS = "status"
    CUSTOM = "custom"


class SelectionReason(str, Enum):
    """选择原因"""
    DOMAIN_MATCH = "domain_match"
    KEY_MATCH = "key_match"
    RELEVANCE = "relevance"
    RECENCY = "recency"
    COVERAGE = "coverage"
    MANUAL = "manual"


@dataclass
class QueryInput:
    """
    查询输入
    
    记录证据查询的原始输入参数。
    """
    product_id: str
    domain: Optional[str] = None
    fact_keys: List[str] = field(default_factory=list)
    audience: Optional[str] = None
    register: Optional[str] = None
    project_goal: Optional[str] = None
    deliverable_type: Optional[str] = None
    limit: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "domain": self.domain,
            "fact_keys": self.fact_keys,
            "audience": self.audience,
            "register": self.register,
            "project_goal": self.project_goal,
            "deliverable_type": self.deliverable_type,
            "limit": self.limit,
        }


@dataclass
class FilterDecision:
    """
    过滤决策
    
    记录单次过滤操作的详情。
    """
    filter_type: FilterType
    filter_value: Any
    candidates_before: int
    candidates_after: int
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "filter_type": self.filter_type.value,
            "filter_value": self.filter_value,
            "candidates_before": self.candidates_before,
            "candidates_after": self.candidates_after,
            "reason": self.reason,
        }


@dataclass
class RankingDecision:
    """
    排序决策
    
    记录候选事实的排序规则和结果。
    """
    ranking_rule: str
    ranking_field: str
    ascending: bool = False
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ranking_rule": self.ranking_rule,
            "ranking_field": self.ranking_field,
            "ascending": self.ascending,
            "description": self.description,
        }


@dataclass
class DedupDecision:
    """
    去重决策
    
    记录去重规则和处理结果。
    """
    dedup_rule: str
    dedup_field: str
    candidates_before: int
    candidates_after: int
    duplicates_removed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dedup_rule": self.dedup_rule,
            "dedup_field": self.dedup_field,
            "candidates_before": self.candidates_before,
            "candidates_after": self.candidates_after,
            "duplicates_removed": self.duplicates_removed,
        }


@dataclass
class SelectionDecision:
    """
    选择决策
    
    记录最终入选的事实及其原因。
    """
    fact_id: str
    reason: SelectionReason
    score: Optional[float] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "reason": self.reason.value,
            "score": self.score,
            "notes": self.notes,
        }


@dataclass
class SufficiencyJudgment:
    """
    充分性判断
    
    评估证据是否足以支撑当前任务。
    """
    is_sufficient: bool
    criteria: str
    facts_count: int
    domains_covered: List[str]
    gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_sufficient": self.is_sufficient,
            "criteria": self.criteria,
            "facts_count": self.facts_count,
            "domains_covered": self.domains_covered,
            "gaps": self.gaps,
            "recommendations": self.recommendations,
        }


@dataclass
class RetrievalTrace:
    """
    检索追踪
    
    完整记录证据检索的决策链，使选择过程可回看、可审计。
    
    SP-6 Batch 6A 核心输出。
    """
    # 查询输入
    query_input: QueryInput
    
    # 候选统计
    total_candidates: int = 0
    candidates_after_filtering: int = 0
    candidates_after_dedup: int = 0
    final_selected: int = 0
    
    # 决策链
    filter_decisions: List[FilterDecision] = field(default_factory=list)
    ranking_decision: Optional[RankingDecision] = None
    dedup_decision: Optional[DedupDecision] = None
    selection_decisions: List[SelectionDecision] = field(default_factory=list)
    sufficiency_judgment: Optional[SufficiencyJudgment] = None
    
    # 元数据
    trace_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "created_at": self.created_at.isoformat(),
            "duration_ms": self.duration_ms,
            "query_input": self.query_input.to_dict(),
            "total_candidates": self.total_candidates,
            "candidates_after_filtering": self.candidates_after_filtering,
            "candidates_after_dedup": self.candidates_after_dedup,
            "final_selected": self.final_selected,
            "filter_decisions": [fd.to_dict() for fd in self.filter_decisions],
            "ranking_decision": self.ranking_decision.to_dict() if self.ranking_decision else None,
            "dedup_decision": self.dedup_decision.to_dict() if self.dedup_decision else None,
            "selection_decisions": [sd.to_dict() for sd in self.selection_decisions],
            "sufficiency_judgment": self.sufficiency_judgment.to_dict() if self.sufficiency_judgment else None,
        }
    
    def summarize(self) -> str:
        """生成简短的摘要"""
        return (
            f"RetrievalTrace[{self.trace_id}]: "
            f"{self.total_candidates} candidates → "
            f"{self.candidates_after_filtering} after filter → "
            f"{self.final_selected} selected. "
            f"Sufficient: {self.sufficiency_judgment.is_sufficient if self.sufficiency_judgment else 'N/A'}"
        )


@dataclass
class EvidenceResultWithTrace:
    """
    带追踪的证据结果
    
    将事实列表和检索追踪打包返回，使调用方能同时获取数据和决策过程。
    """
    facts: List[Any]  # List[FactRecord]
    trace: RetrievalTrace
    
    def to_dict(self) -> Dict[str, Any]:
        from .models import FactRecord
        return {
            "facts": [
                {
                    "fact_id": f.fact_id,
                    "product_id": f.product_id,
                    "domain": f.domain,
                    "fact_key": f.fact_key,
                    "value": str(f.value) if f.value is not None else "",
                    "definition": f.definition,
                    "definition_zh": f.definition_zh,
                    "unit": f.unit,
                    "status": f.status.value,
                    "lineage": f.lineage,
                }
                for f in self.facts
            ],
            "trace": self.trace.to_dict(),
        }