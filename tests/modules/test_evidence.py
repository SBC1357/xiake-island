"""
Tests for Evidence Module
"""
import pytest

from src.modules.evidence import (
    EvidenceService,
    SourceRecord,
    AssetRecord,
    FactRecord,
    SourceType,
    AssetType,
    FactStatus,
    # SP-6 Batch 6A: 检索追踪模型
    RetrievalTrace,
    QueryInput,
    FilterDecision,
    FilterType,
    SelectionReason,
    EvidenceResultWithTrace,
)


class TestSourceRecord:
    """测试来源记录"""
    
    def test_create_source_record(self):
        """创建来源记录"""
        source = SourceRecord(
            source_id="src_001",
            source_type=SourceType.PDF,
            title="Test Document"
        )
        
        assert source.source_id == "src_001"
        assert source.source_type == SourceType.PDF
        assert source.title == "Test Document"
    
    def test_source_with_product_id(self):
        """带产品 ID 的来源"""
        source = SourceRecord(
            source_id="src_002",
            source_type=SourceType.DATABASE,
            title="Clinical Trial Data",
            product_id="lecanemab"
        )
        
        assert source.product_id == "lecanemab"


class TestFactRecord:
    """测试事实记录"""
    
    def test_create_fact_record(self):
        """创建事实记录"""
        fact = FactRecord(
            fact_id="fact_001",
            product_id="test",
            domain="efficacy",
            fact_key="response_rate",
            value="85%"
        )
        
        assert fact.fact_id == "fact_001"
        assert fact.domain == "efficacy"
        assert fact.value == "85%"
        assert fact.status == FactStatus.ACTIVE
    
    def test_fact_with_unit(self):
        """带单位的事实"""
        fact = FactRecord(
            fact_id="fact_002",
            product_id="test",
            domain="safety",
            fact_key="ae_rate",
            value="5.2",
            unit="%"
        )
        
        assert fact.unit == "%"


class TestEvidenceService:
    """测试证据服务"""
    
    @pytest.fixture
    def service(self):
        return EvidenceService()
    
    def test_resolve_sources_empty(self, service):
        """解析来源返回空列表"""
        results = service.resolve_sources({"product_id": "test"})
        
        assert len(results) == 0
    
    def test_resolve_facts_empty(self, service):
        """解析事实返回空列表"""
        results = service.resolve_facts({"product_id": "test", "domain": "efficacy"})
        
        assert len(results) == 0
    
    def test_query_facts_by_domain(self, service):
        """按领域查询事实"""
        results = service.query_facts_by_domain("lecanemab", "efficacy")
        
        assert isinstance(results, list)
    
    def test_create_source_record(self, service):
        """创建来源记录"""
        source = service.create_source_record(
            source_type=SourceType.PDF,
            title="Test PDF",
            product_id="test"
        )
        
        assert source.source_type == SourceType.PDF
        assert source.title == "Test PDF"
        assert source.product_id == "test"
        assert source.source_id.startswith("src_")
    
    def test_create_fact_record(self, service):
        """创建事实记录"""
        fact = service.create_fact_record(
            product_id="test",
            domain="safety",
            fact_key="mortality_rate",
            value="2.3%",
            definition="Mortality rate in trial"
        )
        
        assert fact.product_id == "test"
        assert fact.domain == "safety"
        assert fact.fact_key == "mortality_rate"
        assert fact.value == "2.3%"
        assert fact.definition == "Mortality rate in trial"
    
    def test_get_fact_lineage(self, service):
        """获取事实溯源"""
        lineage = service.get_fact_lineage("fact_001")
        
        assert "fact_id" in lineage
        assert "sources" in lineage


# ============================================================================
# SP-6 Batch 6A: 检索追踪测试
# ============================================================================

class TestRetrievalTraceSP6Batch6A:
    """
    SP-6 Batch 6A: 显式取证追踪测试
    
    验证 retrieval_trace 功能：
    - 查询输入记录
    - 候选数量变化
    - 过滤决策链
    - 最终入选原因
    """
    
    @pytest.fixture
    def service(self):
        return EvidenceService()
    
    def test_resolve_facts_with_trace_returns_trace(self, service):
        """resolve_facts_with_trace 返回完整追踪"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        # 验证返回类型
        assert isinstance(result, EvidenceResultWithTrace)
        assert isinstance(result.facts, list)
        assert isinstance(result.trace, RetrievalTrace)
    
    def test_trace_records_query_input(self, service):
        """追踪记录查询输入"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy",
            "fact_keys": ["response_rate", "pfs"],
            "audience": "医学专业人士",
            "register": "R2",
            "project_goal": "评估疗效",
            "deliverable_type": "brief",
            "limit": 50
        })
        
        trace = result.trace
        assert isinstance(trace.query_input, QueryInput)
        assert trace.query_input.product_id == "test_product"
        assert trace.query_input.domain == "efficacy"
        assert trace.query_input.fact_keys == ["response_rate", "pfs"]
        assert trace.query_input.audience == "医学专业人士"
        assert trace.query_input.register == "R2"
        assert trace.query_input.project_goal == "评估疗效"
        assert trace.query_input.deliverable_type == "brief"
        assert trace.query_input.limit == 50
    
    def test_trace_records_candidate_counts(self, service):
        """追踪记录候选数量变化"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        trace = result.trace
        # 验证候选数量字段存在
        assert hasattr(trace, 'total_candidates')
        assert hasattr(trace, 'candidates_after_filtering')
        assert hasattr(trace, 'candidates_after_dedup')
        assert hasattr(trace, 'final_selected')
        
        # 验证数量关系
        assert trace.final_selected <= trace.candidates_after_dedup
        assert trace.candidates_after_dedup <= trace.candidates_after_filtering
        assert trace.candidates_after_filtering <= trace.total_candidates
    
    def test_trace_records_filter_decisions(self, service):
        """追踪记录过滤决策"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        trace = result.trace
        # 验证过滤决策列表
        assert isinstance(trace.filter_decisions, list)
        
        # 如果有过滤决策，验证结构
        if trace.filter_decisions:
            for fd in trace.filter_decisions:
                assert isinstance(fd, FilterDecision)
                assert isinstance(fd.filter_type, FilterType)
                assert fd.candidates_before >= fd.candidates_after
    
    def test_trace_records_selection_reasons(self, service):
        """追踪记录选择原因"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        trace = result.trace
        # 验证选择决策列表
        assert isinstance(trace.selection_decisions, list)
        
        # 如果有选择决策，验证结构
        if trace.selection_decisions:
            for sd in trace.selection_decisions:
                assert sd.fact_id is not None
                assert isinstance(sd.reason, SelectionReason)
    
    def test_trace_records_sufficiency_judgment(self, service):
        """追踪记录充分性判断"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        trace = result.trace
        # 验证充分性判断存在
        assert trace.sufficiency_judgment is not None
        assert trace.sufficiency_judgment.is_sufficient is not None
        assert trace.sufficiency_judgment.criteria is not None
        assert trace.sufficiency_judgment.facts_count >= 0
    
    def test_trace_has_trace_id(self, service):
        """追踪有唯一 trace_id"""
        result1 = service.resolve_facts_with_trace({"product_id": "test1"})
        result2 = service.resolve_facts_with_trace({"product_id": "test2"})
        
        assert result1.trace.trace_id is not None
        assert result1.trace.trace_id.startswith("trace_")
        # 不同查询应该有不同的 trace_id
        assert result1.trace.trace_id != result2.trace.trace_id
    
    def test_trace_to_dict(self, service):
        """追踪可以序列化为字典"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        trace_dict = result.trace.to_dict()
        
        # 验证字典结构
        assert isinstance(trace_dict, dict)
        assert "trace_id" in trace_dict
        assert "query_input" in trace_dict
        assert "total_candidates" in trace_dict
        assert "candidates_after_filtering" in trace_dict
        assert "final_selected" in trace_dict
        assert "filter_decisions" in trace_dict
        assert "selection_decisions" in trace_dict
        assert "sufficiency_judgment" in trace_dict
    
    def test_result_to_dict(self, service):
        """结果可以序列化为字典"""
        result = service.resolve_facts_with_trace({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        result_dict = result.to_dict()
        
        # 验证字典结构
        assert isinstance(result_dict, dict)
        assert "facts" in result_dict
        assert "trace" in result_dict
        assert isinstance(result_dict["facts"], list)
        assert isinstance(result_dict["trace"], dict)
    
    def test_resolve_facts_still_works(self, service):
        """resolve_facts 保持行为兼容"""
        # 原有方法应该仍然工作
        facts = service.resolve_facts({
            "product_id": "test_product",
            "domain": "efficacy"
        })
        
        assert isinstance(facts, list)
        # 返回的是 FactRecord 列表
        for fact in facts:
            assert isinstance(fact, FactRecord)
    
    def test_empty_query_returns_empty_trace(self, service):
        """空查询返回空结果但追踪完整"""
        result = service.resolve_facts_with_trace({
            "product_id": "nonexistent_product"
        })
        
        assert result.facts == []
        assert result.trace.total_candidates == 0
        assert result.trace.final_selected == 0
        assert result.trace.sufficiency_judgment is not None
        assert result.trace.sufficiency_judgment.is_sufficient == False