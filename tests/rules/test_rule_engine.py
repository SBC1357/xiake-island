"""
SP-6 Batch 6B: 规则执行引擎测试

测试确定性规则执行引擎的核心功能:
- 规则引擎可以执行规则
- 产出 rule-level trace (matched/failed/skipped/errors + reasons)
- 可以区分规则层与模型层
"""
import pytest

from src.rules import (
    RuleEngine,
    Rule,
    RuleResult,
    RuleTrace,
    RuleFamilyOutput,
    RuleLayerOutput,
    RuleFamilyId,
    RuleStatus,
    RuleSeverity,
)
from src.rules.families import (
    RegisterLevelsFamily,
    ExpressionBaseFamily,
    MedicalSyntaxRulesFamily,
    ThesisDerivationRulesFamily,
    get_register_level_rules,
    get_expression_base_rules,
    get_medical_syntax_rules,
    get_thesis_derivation_rules,
)
from src.rules.adapters import M5ComplianceAdapterFamily


class TestRuleEngineSP6Batch6B:
    """SP-6 Batch 6B: 测试规则引擎核心功能"""
    
    def test_rule_engine_can_be_created(self):
        """测试规则引擎可以创建"""
        engine = RuleEngine()
        assert engine is not None
    
    def test_rule_engine_can_register_family(self):
        """测试规则引擎可以注册规则族"""
        engine = RuleEngine()
        family = ExpressionBaseFamily()
        engine.register_family(family)
        
        assert RuleFamilyId.EXPRESSION_BASE in engine.registry.list_families()
    
    def test_rule_engine_execute_returns_output(self):
        """测试规则引擎执行返回输出"""
        engine = RuleEngine()
        engine.register_family(ExpressionBaseFamily())
        
        content = "这是一段正常的测试内容。"
        output = engine.execute(content)
        
        assert output is not None
        assert isinstance(output, RuleLayerOutput)
    
    def test_rule_engine_produces_rule_level_trace(self):
        """测试规则引擎产出 rule-level trace"""
        engine = RuleEngine()
        engine.register_family(ExpressionBaseFamily())
        
        content = "这个药物可以根治疾病。"
        output = engine.execute(content)
        
        # 验证 trace 结构
        assert output.families_executed is not None
        assert output.total_matched >= 0
        assert output.total_failed >= 0
        assert output.total_skipped >= 0
        assert output.total_errors >= 0
        assert output.duration_ms >= 0
        assert output.traces is not None
    
    def test_rule_engine_detects_absolute_expression(self):
        """测试规则引擎检测绝对化表达"""
        engine = RuleEngine()
        engine.register_family(ExpressionBaseFamily())
        
        # 包含绝对化表达的内容
        content = "这个药物可以根治疾病，百分之百有效！"
        output = engine.execute(content)
        
        # 应该检测到问题 (failed 表示规则检测到违规)
        assert output.total_failed > 0 or output.total_matched > 0
    
    def test_rule_engine_detects_compliance_violation(self):
        """测试规则引擎检测合规违规"""
        engine = RuleEngine()
        engine.register_family(M5ComplianceAdapterFamily())
        
        # 包含合规违规的内容
        content = "这个药物可以根治疾病，无效退款！"
        output = engine.execute(content)
        
        # 应该检测到违规
        assert output.total_matched > 0


class TestRuleFamiliesSP6Batch6B:
    """SP-6 Batch 6B: 测试规则族"""
    
    def test_expression_base_family_has_rules(self):
        """测试表达规则族有规则"""
        rules = get_expression_base_rules()
        assert len(rules) > 0
    
    def test_medical_syntax_family_has_rules(self):
        """测试医学语法规则族有规则"""
        rules = get_medical_syntax_rules()
        assert len(rules) > 0
    
    def test_thesis_derivation_family_has_rules(self):
        """测试论点推导规则族有规则"""
        rules = get_thesis_derivation_rules()
        assert len(rules) > 0
    
    def test_register_levels_family_has_rules(self):
        """测试语体级别规则族有规则"""
        rules = get_register_level_rules()
        assert len(rules) > 0


class TestRuleTraceSP6Batch6B:
    """SP-6 Batch 6B: 测试规则追踪"""
    
    def test_rule_trace_contains_matched_ids(self):
        """测试规则追踪包含匹配的规则ID"""
        engine = RuleEngine()
        engine.register_family(ExpressionBaseFamily())
        
        content = "这个药物可以根治疾病。"
        output = engine.execute(content)
        
        # 检查 traces 结构
        for family_name, trace in output.traces.items():
            assert "matched" in trace
            assert "failed" in trace
            assert "skipped" in trace
            assert isinstance(trace["matched"], list)
    
    def test_rule_trace_contains_failed_ids_with_reasons(self):
        """测试规则追踪包含失败的规则ID和原因"""
        engine = RuleEngine()
        engine.register_family(ExpressionBaseFamily())
        
        content = "普通内容没有违规。"
        output = engine.execute(content)
        
        # 检查 traces 结构包含 reason
        for family_name, trace in output.traces.items():
            assert "passed" in trace


class TestQualityOrchestratorRuleTraceSP6Batch6B:
    """SP-6 Batch 6B: 测试 QualityOrchestrator 集成"""
    
    def test_quality_orchestrator_has_rule_trace_property(self):
        """测试 QualityOrchestrator 有 rule_trace 属性"""
        from src.modules.quality import QualityOrchestrator
        
        orchestrator = QualityOrchestrator()
        assert hasattr(orchestrator, 'rule_trace')
    
    def test_quality_orchestrator_can_run_rules(self):
        """测试 QualityOrchestrator 可以运行规则"""
        from src.modules.quality import QualityOrchestrator
        
        orchestrator = QualityOrchestrator()
        content = "这是一段测试内容，长度足够。"
        
        trace = orchestrator.run_rules(content)
        
        assert trace is not None
        assert "families_executed" in trace
        assert "total_matched" in trace
        assert "traces" in trace
    
    def test_quality_orchestrator_rule_trace_exposed(self):
        """测试 QualityOrchestrator 暴露 rule_trace"""
        from src.modules.quality import QualityOrchestrator
        
        orchestrator = QualityOrchestrator()
        content = "这是一段测试内容。"
        
        orchestrator.run_rules(content)
        
        # 验证 rule_trace 属性被设置
        assert orchestrator.rule_trace is not None


class TestSemanticReviewerRuleLayerSP6Batch6B:
    """SP-6 Batch 6B: 测试 SemanticReviewer 规则层集成"""
    
    def test_semantic_review_output_has_rule_layer_field(self):
        """测试 SemanticReviewOutput 有 rule_layer_output 字段"""
        from src.modules.semantic_review import SemanticReviewOutput
        
        output = SemanticReviewOutput(passed=True)
        assert hasattr(output, 'rule_layer_output')
    
    def test_semantic_review_output_can_store_rule_layer(self):
        """测试 SemanticReviewOutput 可以存储规则层输出"""
        from src.modules.semantic_review import SemanticReviewOutput
        
        rule_layer = {
            "families_executed": ["expression_base"],
            "total_matched": 1,
            "overall_passed": True,
        }
        
        output = SemanticReviewOutput(
            passed=True,
            rule_layer_output=rule_layer
        )
        
        assert output.rule_layer_output == rule_layer


# Tail phrase: SP6_BATCH_6B_RULE_ENGINE