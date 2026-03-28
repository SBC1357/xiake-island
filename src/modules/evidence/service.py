"""
Evidence Service

证据管理服务，实现 V2 EvidenceResolver 逻辑。
从藏经阁消费者目录读取 L4 产品证据数据。

SP-6 Batch 6A: 新增 resolve_facts_with_trace() 支持显式检索追踪。
"""
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .models import SourceRecord, AssetRecord, FactRecord, SourceType, AssetType, FactStatus
from .retrieval_trace import (
    RetrievalTrace, QueryInput, FilterDecision, RankingDecision,
    DedupDecision, SelectionDecision, SufficiencyJudgment,
    FilterType, SelectionReason, EvidenceResultWithTrace
)
from src.adapters.asset_bridge import FilesystemAssetBridge, AssetKind


@dataclass
class EvidenceService:
    """
    证据管理服务
    
    实现与 V2 EvidenceResolver 兼容的证据解析逻辑。
    通过 AssetBridge 从藏经阁消费者目录读取证据数据。
    """
    
    asset_bridge: Optional[FilesystemAssetBridge] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后验证配置"""
        if self.asset_bridge is None:
            # 尝试从 assembly 获取共享实例
            try:
                from src.assembly import get_asset_bridge
                self.asset_bridge = get_asset_bridge()
            except Exception:
                pass  # 在测试环境中可能没有配置
    
    def _load_evidence_file(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        加载产品的证据文件
        
        Args:
            product_id: 产品 ID
            
        Returns:
            证据数据字典，如果文件不存在则返回 None
        """
        if self.asset_bridge is None:
            return None
        
        # 证据文件路径: staging/evidence/rebuilt/{product_id}_evidence_v2.json
        evidence_path = f"staging/evidence/rebuilt/{product_id}_evidence_v2.json"
        
        try:
            record = self.asset_bridge.read_text(AssetKind.CONSUMER, evidence_path)
            return json.loads(record.content)
        except Exception:
            pass  # 主文件不存在，尝试 _sample 版本
        
        # 尝试 _sample 版本（用于测试或部分产品）
        sample_path = f"staging/evidence/rebuilt/{product_id}_evidence_v2_sample.json"
        try:
            record = self.asset_bridge.read_text(AssetKind.CONSUMER, sample_path)
            return json.loads(record.content)
        except Exception:
            return None
    
    def resolve_sources(self, query: Dict[str, Any]) -> List[SourceRecord]:
        """
        解析来源
        
        Args:
            query: 查询条件 {product_id, source_type, source_keys, etc}
            
        Returns:
            匹配的 SourceRecord 列表
        """
        product_id = query.get("product_id")
        if not product_id:
            return []
        
        data = self._load_evidence_file(product_id)
        if not data:
            return []
        
        sources = data.get("v2_sources", [])
        result = []
        
        source_type_filter = query.get("source_type")
        source_keys_filter = query.get("source_keys", [])
        
        for src in sources:
            # 类型过滤
            if source_type_filter and src.get("source_type") != source_type_filter:
                continue
            
            # source_keys 过滤
            if source_keys_filter and src.get("source_key") not in source_keys_filter:
                continue
            
            # 转换为 SourceRecord
            source_type = self._map_source_type(src.get("source_type", "manual"))
            
            result.append(SourceRecord(
                source_id=src.get("source_id", ""),
                source_type=source_type,
                title=src.get("title", ""),
                product_id=product_id,
                source_keys=[src.get("source_key", "")] if src.get("source_key") else [],
                metadata=src.get("metadata", {})
            ))
        
        return result
    
    def resolve_assets(self, source_ids: List[str]) -> List[AssetRecord]:
        """
        解析资产
        
        Args:
            source_ids: 来源 ID 列表
            
        Returns:
            关联的 AssetRecord 列表
        """
        # 当前证据文件不包含独立的 assets 列表
        # 返回空列表，后续可扩展
        return []
    
    def resolve_facts(self, query: Dict[str, Any]) -> List[FactRecord]:
        """
        解析事实
        
        Args:
            query: 查询条件 {product_id, domain, fact_keys, etc}
            
        Returns:
            匹配的 FactRecord 列表
        """
        product_id = query.get("product_id")
        if not product_id:
            return []
        
        data = self._load_evidence_file(product_id)
        if not data:
            return []
        
        facts = data.get("v2_facts", [])
        result = []
        
        domain_filter = query.get("domain")
        fact_keys_filter = query.get("fact_keys", [])
        limit = query.get("limit", 100)
        
        for fact in facts:
            # domain 过滤
            if domain_filter and fact.get("domain") != domain_filter:
                continue
            
            # fact_keys 过滤
            if fact_keys_filter and fact.get("fact_key") not in fact_keys_filter:
                continue
            
            # 状态过滤（只返回 active 状态）
            if fact.get("status") != "active":
                continue
            
            # 转换为 FactRecord
            result.append(FactRecord(
                fact_id=fact.get("fact_id", ""),
                product_id=product_id,
                domain=fact.get("domain", ""),
                fact_key=fact.get("fact_key", ""),
                value=fact.get("value"),
                definition=fact.get("definition"),
                definition_zh=fact.get("definition_zh"),
                unit=fact.get("unit"),
                status=FactStatus.ACTIVE,
                lineage=fact.get("lineage", {}),
                metadata=fact.get("v1_mapping", {})
            ))
            
            if len(result) >= limit:
                break
        
        return result
    
    def query_facts_by_domain(
        self,
        product_id: str,
        domain: str,
        limit: int = 100
    ) -> List[FactRecord]:
        """
        按领域查询事实
        
        Args:
            product_id: 产品 ID
            domain: 领域（efficacy, safety, etc）
            limit: 返回数量限制
            
        Returns:
            FactRecord 列表
        """
        return self.resolve_facts({
            "product_id": product_id,
            "domain": domain,
            "limit": limit
        })
    
    def query_facts_by_keys(
        self,
        product_id: str,
        fact_keys: List[str]
    ) -> List[FactRecord]:
        """
        按事实键查询
        
        Args:
            product_id: 产品 ID
            fact_keys: 事实键列表
            
        Returns:
            FactRecord 列表
        """
        return self.resolve_facts({
            "product_id": product_id,
            "fact_keys": fact_keys
        })
    
    def get_fact_lineage(self, fact_id: str) -> Dict[str, Any]:
        """
        获取事实溯源信息
        
        Args:
            fact_id: 事实 ID
            
        Returns:
            溯源信息字典
        """
        # 从 fact_id 提取 product_id（格式：V2-FACT-{PRODUCT}-...）
        parts = fact_id.split("-")
        if len(parts) >= 4:
            # 尝试从 fact_id 推断 product_id
            product_hint = parts[2].lower()
            
            # 查找匹配的产品
            if self.asset_bridge:
                try:
                    # 列出 staging/evidence/rebuilt 目录下的文件
                    evidence_files = self.asset_bridge.list_assets(AssetKind.CONSUMER)
                    evidence_files = [f for f in evidence_files if "evidence/rebuilt" in f]
                    
                    for ef in evidence_files:
                        # 文件名格式: {product_id}_evidence_v2.json 或 {product_id}_evidence_v2_sample.json
                        filename = ef.split("/")[-1]
                        file_product = filename.replace("_evidence_v2_sample.json", "").replace("_evidence_v2.json", "")
                        
                        data = self._load_evidence_file(file_product)
                        if data:
                            for fact in data.get("v2_facts", []):
                                if fact.get("fact_id") == fact_id:
                                    return {
                                        "fact_id": fact_id,
                                        "product_id": file_product,
                                        "lineage": fact.get("lineage", {}),
                                        "sources": [fact.get("lineage", {}).get("source_key")] if fact.get("lineage", {}).get("source_key") else []
                                    }
                except Exception:
                    pass
        
        return {
            "fact_id": fact_id,
            "sources": [],
            "created_at": None,
            "updated_at": None
        }
    
    def list_available_products(self) -> List[str]:
        """
        列出所有可用的产品 ID
        
        Returns:
            产品 ID 列表
        """
        if self.asset_bridge is None:
            return []
        
        try:
            evidence_files = self.asset_bridge.list_assets(AssetKind.CONSUMER)
            evidence_files = [f for f in evidence_files if "evidence/rebuilt" in f and f.endswith(".json")]
            
            products = []
            for ef in evidence_files:
                # 文件名格式: {product_id}_evidence_v2.json 或 {product_id}_evidence_v2_sample.json
                filename = ef.split("/")[-1]
                # 移除 _evidence_v2.json 或 _evidence_v2_sample.json
                product_id = filename.replace("_evidence_v2_sample.json", "").replace("_evidence_v2.json", "")
                if product_id and product_id not in products:
                    products.append(product_id)
            
            return sorted(products)
        except Exception:
            return []
    
    def _map_source_type(self, source_type: str) -> SourceType:
        """
        映射来源类型字符串到枚举
        
        Args:
            source_type: 来源类型字符串
            
        Returns:
            SourceType 枚举值
        """
        mapping = {
            "journal_article": SourceType.PDF,
            "clinical_trial": SourceType.PDF,
            "guideline": SourceType.PDF,
            "web": SourceType.WEB,
            "database": SourceType.DATABASE,
            "manual": SourceType.MANUAL,
        }
        return mapping.get(source_type, SourceType.MANUAL)
    
    def create_source_record(
        self,
        source_type: SourceType,
        title: str,
        product_id: Optional[str] = None,
        source_keys: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SourceRecord:
        """
        创建来源记录
        
        Args:
            source_type: 来源类型
            title: 标题
            product_id: 产品 ID
            source_keys: 来源键列表
            metadata: 元数据
            
        Returns:
            SourceRecord
        """
        import uuid
        
        return SourceRecord(
            source_id=f"src_{uuid.uuid4().hex[:12]}",
            source_type=source_type,
            title=title,
            product_id=product_id,
            source_keys=source_keys or [],
            metadata=metadata or {}
        )
    
    def create_fact_record(
        self,
        product_id: str,
        domain: str,
        fact_key: str,
        value: Any,
        definition: Optional[str] = None,
        unit: Optional[str] = None
    ) -> FactRecord:
        """
        创建事实记录
        
        Args:
            product_id: 产品 ID
            domain: 领域
            fact_key: 事实键
            value: 值
            definition: 定义
            unit: 单位
            
        Returns:
            FactRecord
        """
        import uuid
        
        return FactRecord(
            fact_id=f"fact_{uuid.uuid4().hex[:12]}",
            product_id=product_id,
            domain=domain,
            fact_key=fact_key,
            value=value,
            definition=definition,
            unit=unit,
            status=FactStatus.ACTIVE
        )
    
    def resolve_facts_with_trace(
        self,
        query: Dict[str, Any]
    ) -> EvidenceResultWithTrace:
        """
        解析事实并返回完整检索追踪
        
        SP-6 Batch 6A: 显式取证追踪。
        将证据检索决策链显式化，使选择过程可回看、可审计。
        
        Args:
            query: 查询条件 {product_id, domain, fact_keys, audience, register, project_goal, deliverable_type, limit}
            
        Returns:
            EvidenceResultWithTrace: 包含事实列表和完整检索追踪
        """
        start_time = time.time()
        
        # 构建查询输入追踪
        query_input = QueryInput(
            product_id=query.get("product_id", ""),
            domain=query.get("domain"),
            fact_keys=query.get("fact_keys", []),
            audience=query.get("audience"),
            register=query.get("register"),
            project_goal=query.get("project_goal"),
            deliverable_type=query.get("deliverable_type"),
            limit=query.get("limit", 100)
        )
        
        # 初始化追踪记录
        trace = RetrievalTrace(
            query_input=query_input,
            trace_id=f"trace_{uuid.uuid4().hex[:12]}",
        )
        
        # 加载证据数据
        product_id = query.get("product_id")
        data = self._load_evidence_file(product_id) if product_id else None
        
        if not data:
            # 无数据，返回空结果
            trace.total_candidates = 0
            trace.candidates_after_filtering = 0
            trace.candidates_after_dedup = 0
            trace.final_selected = 0
            trace.sufficiency_judgment = SufficiencyJudgment(
                is_sufficient=False,
                criteria="至少存在一个匹配的事实",
                facts_count=0,
                domains_covered=[],
                gaps=["未找到证据数据文件"],
                recommendations=["请检查产品ID是否正确，或确认证据数据已加载"]
            )
            trace.duration_ms = int((time.time() - start_time) * 1000)
            
            return EvidenceResultWithTrace(facts=[], trace=trace)
        
        # 获取所有事实作为候选
        all_facts = data.get("v2_facts", [])
        trace.total_candidates = len(all_facts)
        
        # 准备过滤条件
        domain_filter = query.get("domain")
        fact_keys_filter = query.get("fact_keys", [])
        limit = query.get("limit", 100)
        
        # 阶段1: 状态过滤 (只保留 active)
        active_facts = [f for f in all_facts if f.get("status") == "active"]
        if len(active_facts) != len(all_facts):
            trace.filter_decisions.append(FilterDecision(
                filter_type=FilterType.STATUS,
                filter_value="active",
                candidates_before=len(all_facts),
                candidates_after=len(active_facts),
                reason="只保留有效状态的事实"
            ))
        
        # 阶段2: domain 过滤
        filtered_facts = active_facts
        if domain_filter:
            before_count = len(filtered_facts)
            filtered_facts = [f for f in filtered_facts if f.get("domain") == domain_filter]
            trace.filter_decisions.append(FilterDecision(
                filter_type=FilterType.DOMAIN,
                filter_value=domain_filter,
                candidates_before=before_count,
                candidates_after=len(filtered_facts),
                reason=f"按领域 '{domain_filter}' 过滤"
            ))
        
        # 阶段3: fact_keys 过滤
        if fact_keys_filter:
            before_count = len(filtered_facts)
            filtered_facts = [f for f in filtered_facts if f.get("fact_key") in fact_keys_filter]
            trace.filter_decisions.append(FilterDecision(
                filter_type=FilterType.FACT_KEYS,
                filter_value=fact_keys_filter,
                candidates_before=before_count,
                candidates_after=len(filtered_facts),
                reason=f"按事实键过滤: {fact_keys_filter}"
            ))
        
        trace.candidates_after_filtering = len(filtered_facts)
        
        # 去重（按 fact_id）
        seen_ids = set()
        deduped_facts = []
        for f in filtered_facts:
            fact_id = f.get("fact_id", "")
            if fact_id not in seen_ids:
                seen_ids.add(fact_id)
                deduped_facts.append(f)
        
        if len(deduped_facts) != len(filtered_facts):
            trace.dedup_decision = DedupDecision(
                dedup_rule="by_fact_id",
                dedup_field="fact_id",
                candidates_before=len(filtered_facts),
                candidates_after=len(deduped_facts),
                duplicates_removed=len(filtered_facts) - len(deduped_facts)
            )
        
        trace.candidates_after_dedup = len(deduped_facts)
        
        # 排序（按 domain, fact_key 排序以保持一致性）
        deduped_facts.sort(key=lambda f: (f.get("domain", ""), f.get("fact_key", "")))
        trace.ranking_decision = RankingDecision(
            ranking_rule="default_sort",
            ranking_field="domain, fact_key",
            ascending=True,
            description="按领域和事实键排序以保持一致性"
        )
        
        # 限制数量
        final_facts_data = deduped_facts[:limit]
        trace.final_selected = len(final_facts_data)
        
        # 转换为 FactRecord 并记录选择决策
        result_facts = []
        for fact_data in final_facts_data:
            result_facts.append(FactRecord(
                fact_id=fact_data.get("fact_id", ""),
                product_id=product_id or "",
                domain=fact_data.get("domain", ""),
                fact_key=fact_data.get("fact_key", ""),
                value=fact_data.get("value"),
                definition=fact_data.get("definition"),
                definition_zh=fact_data.get("definition_zh"),
                unit=fact_data.get("unit"),
                status=FactStatus.ACTIVE,
                lineage=fact_data.get("lineage", {}),
                metadata=fact_data.get("v1_mapping", {})
            ))
            
            # 记录选择决策
            trace.selection_decisions.append(SelectionDecision(
                fact_id=fact_data.get("fact_id", ""),
                reason=SelectionReason.DOMAIN_MATCH if fact_data.get("domain") == domain_filter else SelectionReason.KEY_MATCH,
                notes=f"领域: {fact_data.get('domain', 'unknown')}, 键: {fact_data.get('fact_key', 'unknown')}"
            ))
        
        # 证据充分性判断
        domains_covered = list(set(f.domain for f in result_facts)) if result_facts else []
        is_sufficient = len(result_facts) > 0
        
        trace.sufficiency_judgment = SufficiencyJudgment(
            is_sufficient=is_sufficient,
            criteria="至少存在一个匹配的事实",
            facts_count=len(result_facts),
            domains_covered=domains_covered,
            gaps=[] if is_sufficient else ["未找到匹配的事实"],
            recommendations=[] if is_sufficient else ["建议检查产品ID或领域参数是否正确"]
        )
        
        # 记录执行时间
        trace.duration_ms = int((time.time() - start_time) * 1000)
        
        return EvidenceResultWithTrace(facts=result_facts, trace=trace)