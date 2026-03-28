"""
Semantic Review Module 测试

使用 FakeLLMProvider 进行测试，不依赖真实外部模型服务。
"""
import pytest
import json
from pydantic import ValidationError

from src.modules.semantic_review import (
    SemanticReviewInput,
    SemanticReviewOutput,
    FindingOutput,
    SeveritySummaryOutput,
    RewriteTargetOutput,
    PrototypeAlignmentOutput,
    SemanticReviewerConfig,
    SemanticReviewer,
    SemanticReviewError,
    ContentTooShortError,
    ReviewGenerationError,
)
from src.adapters.llm_gateway import (
    FakeLLMProvider,
    LLMGateway,
    LLMGatewayConfig,
)


class TestSemanticReviewInput:
    """测试 SemanticReviewInput"""
    
    def test_input_with_required_fields(self):
        """测试输入 - 必填字段"""
        input_data = SemanticReviewInput(
            content="这是一段需要审核的中文内容。",
            audience="医学专业人士"
        )
        assert input_data.content == "这是一段需要审核的中文内容。"
        assert input_data.audience == "医学专业人士"
        assert input_data.prototype_hint is None
        assert input_data.register is None
    
    def test_input_with_all_fields(self):
        """测试输入 - 所有字段"""
        input_data = SemanticReviewInput(
            content="测试内容",
            audience="普通公众",
            prototype_hint="科普文章",
            register="通俗",
            context_metadata={"source": "test"}
        )
        assert input_data.prototype_hint == "科普文章"
        assert input_data.register == "通俗"
    
    def test_input_empty_content_fails(self):
        """测试空内容失败"""
        with pytest.raises(ValidationError):
            SemanticReviewInput(content="", audience="test")
    
    def test_input_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            SemanticReviewInput(
                content="test",
                audience="test",
                unknown_field="value"
            )


class TestSemanticReviewOutput:
    """测试 SemanticReviewOutput"""
    
    def test_output_with_required_fields(self):
        """测试输出 - 必填字段"""
        output = SemanticReviewOutput(passed=True)
        assert output.passed is True
        assert output.findings == []
        assert output.rewrite_target == []
    
    def test_output_with_findings(self):
        """测试输出 - 包含发现项"""
        finding = FindingOutput(
            severity="medium",
            category="语法",
            description="句子结构不完整"
        )
        output = SemanticReviewOutput(
            passed=False,
            findings=[finding]
        )
        assert len(output.findings) == 1
        assert output.findings[0].severity == "medium"


class TestSemanticReviewerConfig:
    """测试 SemanticReviewerConfig"""
    
    def test_config_default_values(self):
        """测试配置默认值"""
        config = SemanticReviewerConfig()
        assert config.max_findings == 10
        assert config.auto_pass_threshold is True
        assert config.require_rewrite_targets is True
        assert config.require_prototype_alignment is False
    
    def test_config_custom_values(self):
        """测试配置自定义值"""
        config = SemanticReviewerConfig(
            max_findings=5,
            auto_pass_threshold=False,
            require_prototype_alignment=True
        )
        assert config.max_findings == 5
        assert config.auto_pass_threshold is False
    
    def test_config_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            SemanticReviewerConfig(unknown_option=True)


class TestSemanticReviewer:
    """测试 SemanticReviewer"""
    
    @pytest.fixture
    def gateway_with_pass_response(self):
        """创建返回通过结果的 Gateway"""
        fake_response = json.dumps({
            "passed": True,
            "severity_summary": {
                "low": 1,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "findings": [
                {
                    "severity": "low",
                    "category": "标点",
                    "description": "标点使用建议",
                    "suggestion": "使用更规范的标点"
                }
            ],
            "rewrite_target": [],
            "prototype_alignment": {
                "score": 85,
                "matched_rules": ["通俗易懂"],
                "unmatched_rules": [],
                "notes": "整体符合要求"
            }
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway_config = LLMGatewayConfig(
            provider_name="fake",
            model_name="test-model"
        )
        return LLMGateway(provider, gateway_config)
    
    @pytest.fixture
    def gateway_with_fail_response(self):
        """创建返回失败结果的 Gateway"""
        fake_response = json.dumps({
            "passed": False,
            "severity_summary": {
                "low": 0,
                "medium": 1,
                "high": 1,
                "critical": 0
            },
            "findings": [
                {
                    "severity": "high",
                    "category": "准确性",
                    "description": "医学术语使用不当",
                    "suggestion": "请核实专业术语"
                },
                {
                    "severity": "medium",
                    "category": "表达",
                    "description": "句子结构问题"
                }
            ],
            "rewrite_target": [
                {
                    "original": "原句",
                    "suggested": "修改后",
                    "reason": "更准确",
                    "priority": "high"
                }
            ],
            "prototype_alignment": {
                "score": 60,
                "matched_rules": [],
                "unmatched_rules": ["专业性"],
                "notes": "需要改进"
            }
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway_config = LLMGatewayConfig(
            provider_name="fake",
            model_name="test-model"
        )
        return LLMGateway(provider, gateway_config)
    
    def test_review_success_passed(self, gateway_with_pass_response):
        """测试审核通过"""
        reviewer = SemanticReviewer(gateway_with_pass_response)
        
        input_data = SemanticReviewInput(
            content="这是一段良好的医学科普内容，语言通俗易懂。",
            audience="普通公众"
        )
        
        output = reviewer.review(input_data)
        
        assert output.passed is True
        assert len(output.findings) == 1
        assert output.findings[0].severity == "low"
        assert output.severity_summary.low == 1
        assert output.severity_summary.critical == 0
    
    def test_review_success_failed(self, gateway_with_fail_response):
        """测试审核不通过"""
        reviewer = SemanticReviewer(gateway_with_fail_response)
        
        input_data = SemanticReviewInput(
            content="这段内容存在医学术语使用问题。",
            audience="医学专业人士",
            prototype_hint="专业文章"
        )
        
        output = reviewer.review(input_data)
        
        assert output.passed is False
        assert len(output.findings) == 2
        assert output.severity_summary.high == 1
        assert len(output.rewrite_target) == 1
    
    def test_review_content_too_short(self):
        """测试内容过短"""
        provider = FakeLLMProvider()
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="fake",
            model_name="test"
        ))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="太短",
            audience="test"
        )
        
        with pytest.raises(ContentTooShortError) as exc_info:
            reviewer.review(input_data)
        
        assert "过短" in str(exc_info.value)
    
    def test_review_auto_pass_threshold(self, gateway_with_fail_response):
        """测试自动通过阈值"""
        config = SemanticReviewerConfig(auto_pass_threshold=True)
        reviewer = SemanticReviewer(gateway_with_fail_response, config)
        
        input_data = SemanticReviewInput(
            content="这段内容存在医学术语使用问题，需要仔细审核。",
            audience="test"
        )
        
        output = reviewer.review(input_data)
        
        # 有 high 问题，应该不通过
        assert output.passed is False
    
    def test_review_handles_llm_error(self):
        """测试处理 LLM 错误"""
        provider = FakeLLMProvider(should_fail=True)
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="fake",
            model_name="test",
            max_retries=0
        ))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="这是一段需要审核的内容，长度足够长。",
            audience="test"
        )
        
        with pytest.raises(ReviewGenerationError) as exc_info:
            reviewer.review(input_data)
        
        assert "LLM" in str(exc_info.value) or "审核生成失败" in str(exc_info.value)
    
    def test_review_handles_invalid_json(self):
        """测试处理无效 JSON"""
        provider = FakeLLMProvider(response_content="This is not JSON")
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="fake",
            model_name="test"
        ))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="这是一段需要审核的内容，长度足够长。",
            audience="test"
        )
        
        with pytest.raises(ReviewGenerationError) as exc_info:
            reviewer.review(input_data)
        
        assert "解析" in str(exc_info.value)

    def test_review_parses_json_wrapped_by_reasoning_text(self):
        """测试兼容 JSON 前后的说明性文本"""
        wrapped_response = """<think>先思考一下</think>
审核结果如下：
```json
{
  "passed": true,
  "severity_summary": {
    "low": 0,
    "medium": 0,
    "high": 0,
    "critical": 0
  },
  "findings": [],
  "rewrite_target": [],
  "prototype_alignment": {
    "score": 92,
    "matched_rules": ["结构清晰"],
    "unmatched_rules": [],
    "notes": "整体良好"
  }
}
```
请查收。"""

        provider = FakeLLMProvider(response_content=wrapped_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="fake",
            model_name="test"
        ))
        reviewer = SemanticReviewer(
            gateway,
            SemanticReviewerConfig(require_prototype_alignment=True)
        )

        input_data = SemanticReviewInput(
            content="这是一段需要审核的内容，长度足够长。",
            audience="test"
        )

        output = reviewer.review(input_data)

        assert output.passed is True
        assert output.prototype_alignment is not None
        assert output.prototype_alignment.score == 92


class TestSemanticReviewerIntegration:
    """测试 SemanticReviewer 集成场景"""
    
    def test_full_review_pipeline(self):
        """测试完整审核管道"""
        fake_response = json.dumps({
            "passed": True,
            "severity_summary": {
                "low": 2,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "findings": [
                {
                    "severity": "low",
                    "category": "标点",
                    "description": "标点符号使用建议优化",
                    "location": "第2段",
                    "suggestion": "使用更规范的逗号"
                },
                {
                    "severity": "low",
                    "category": "表达",
                    "description": "可以更简洁",
                    "suggestion": "精简句子"
                }
            ],
            "rewrite_target": [
                {
                    "original": "原表达方式",
                    "suggested": "优化后的表达",
                    "reason": "更简洁明了",
                    "priority": "low"
                }
            ],
            "prototype_alignment": {
                "score": 90,
                "matched_rules": ["通俗易懂", "结构清晰"],
                "unmatched_rules": [],
                "notes": "符合科普文章要求"
            }
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="integration-test",
            model_name="test-model"
        ))
        config = SemanticReviewerConfig(require_prototype_alignment=True)
        reviewer = SemanticReviewer(gateway, config)
        
        input_data = SemanticReviewInput(
            content="""二甲双胍是一种常用的口服降糖药物，主要用于治疗2型糖尿病。
            它通过抑制肝脏葡萄糖的产生和提高外周组织对胰岛素的敏感性来降低血糖。
            常见的不良反应包括胃肠道不适，如恶心、腹泻等。""",
            audience="糖尿病患者",
            prototype_hint="科普文章",
            register="通俗"
        )
        
        output = reviewer.review(input_data)
        
        # 验证输出结构
        assert output.passed is True
        assert len(output.findings) == 2
        assert output.severity_summary.critical == 0
        assert output.severity_summary.high == 0
        assert output.prototype_alignment is not None
        assert output.prototype_alignment.score == 90
        assert len(output.rewrite_target) >= 1


class TestSemanticReviewerSP6Batch6CSliceB:
    """SP-6 Batch 6C Slice B 测试：三层输出和重跑范围"""
    
    @pytest.fixture
    def gateway_with_high_severity(self):
        """创建返回 high 严重性问题的 Gateway"""
        fake_response = json.dumps({
            "passed": False,
            "severity_summary": {
                "low": 0,
                "medium": 0,
                "high": 1,
                "critical": 0
            },
            "findings": [
                {
                    "severity": "high",
                    "category": "准确性",
                    "description": "医学术语使用不当",
                    "suggestion": "请核实专业术语"
                }
            ],
            "rewrite_target": [
                {
                    "original": "原表达",
                    "suggested": "修改后",
                    "reason": "更准确",
                    "priority": "high"
                }
            ],
            "prototype_alignment": {
                "score": 60,
                "matched_rules": [],
                "unmatched_rules": ["专业性"],
                "notes": "需要改进"
            }
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway_config = LLMGatewayConfig(
            provider_name="fake",
            model_name="test-model"
        )
        return LLMGateway(provider, gateway_config)
    
    @pytest.fixture
    def gateway_with_low_severity(self):
        """创建返回 low 严重性问题的 Gateway"""
        fake_response = json.dumps({
            "passed": True,
            "severity_summary": {
                "low": 1,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "findings": [
                {
                    "severity": "low",
                    "category": "标点",
                    "description": "标点建议",
                    "suggestion": "使用更规范标点"
                }
            ],
            "rewrite_target": [],
            "prototype_alignment": {
                "score": 95,
                "matched_rules": ["通俗易懂"],
                "unmatched_rules": [],
                "notes": "良好"
            }
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway_config = LLMGatewayConfig(
            provider_name="fake",
            model_name="test-model"
        )
        return LLMGateway(provider, gateway_config)
    
    def test_rule_layer_output_present(self):
        """测试 rule_layer_output 存在"""
        fake_response = json.dumps({
            "passed": True,
            "severity_summary": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "findings": [],
            "rewrite_target": [],
            "prototype_alignment": {"score": 90, "matched_rules": [], "unmatched_rules": [], "notes": ""}
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(provider_name="fake", model_name="test"))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="这是一段需要审核的中文医学内容，语言通俗易懂。",
            audience="普通公众"
        )
        
        output = reviewer.review(input_data)
        
        # 验证 rule_layer_output 存在
        assert output.rule_layer_output is not None
        assert "families_executed" in output.rule_layer_output
        assert "duration_ms" in output.rule_layer_output
    
    def test_model_review_output_present(self):
        """测试 model_review_output 存在且包含 findings 和 severity_summary"""
        fake_response = json.dumps({
            "passed": True,
            "severity_summary": {"low": 1, "medium": 0, "high": 0, "critical": 0},
            "findings": [{"severity": "low", "category": "标点", "description": "标点建议"}],
            "rewrite_target": [],
            "prototype_alignment": {"score": 90, "matched_rules": [], "unmatched_rules": [], "notes": ""}
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(provider_name="fake", model_name="test"))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="这是一段需要审核的中文医学内容，语言通俗易懂。",
            audience="普通公众"
        )
        
        output = reviewer.review(input_data)
        
        # 验证 model_review_output 存在且结构正确
        assert output.model_review_output is not None
        assert "findings" in output.model_review_output
        assert "severity_summary" in output.model_review_output
        assert len(output.model_review_output["findings"]) == 1
        assert output.model_review_output["severity_summary"]["low"] == 1
    
    def test_rewrite_layer_output_present(self):
        """测试 rewrite_layer_output 存在且包含 rewrite_targets"""
        fake_response = json.dumps({
            "passed": False,
            "severity_summary": {"low": 0, "medium": 1, "high": 0, "critical": 0},
            "findings": [],
            "rewrite_target": [
                {"original": "原句", "suggested": "新句", "reason": "更准确", "priority": "medium"}
            ],
            "prototype_alignment": {"score": 80, "matched_rules": [], "unmatched_rules": [], "notes": ""}
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(provider_name="fake", model_name="test"))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="这是一段需要审核的中文医学内容，需要改写部分内容。",
            audience="普通公众"
        )
        
        output = reviewer.review(input_data)
        
        # 验证 rewrite_layer_output 存在且结构正确
        assert output.rewrite_layer_output is not None
        assert "rewrite_targets" in output.rewrite_layer_output
        assert "count" in output.rewrite_layer_output
        assert output.rewrite_layer_output["count"] == 1
        assert len(output.rewrite_layer_output["rewrite_targets"]) == 1
    
    def test_rerun_scope_full_gate_for_high_severity(self, gateway_with_high_severity):
        """测试 high 严重性问题触发 full_gate_rerun"""
        reviewer = SemanticReviewer(gateway_with_high_severity)
        
        input_data = SemanticReviewInput(
            content="这段内容存在医学术语使用问题，需要仔细审核。",
            audience="医学专业人士"
        )
        
        output = reviewer.review(input_data)
        
        # 验证 rerun_scope 为 full_gate_rerun
        assert output.rerun_scope == "full_gate_rerun"
    
    def test_rerun_scope_partial_gate_for_low_severity(self, gateway_with_low_severity):
        """测试 low 严重性问题触发 partial_gate_rerun"""
        reviewer = SemanticReviewer(gateway_with_low_severity)
        
        input_data = SemanticReviewInput(
            content="这是一段良好的医学科普内容，语言通俗易懂。",
            audience="普通公众"
        )
        
        output = reviewer.review(input_data)
        
        # 验证 rerun_scope 为 partial_gate_rerun
        assert output.rerun_scope == "partial_gate_rerun"
    
    def test_rerun_scope_full_gate_for_critical_severity(self):
        """测试 critical 严重性问题触发 full_gate_rerun"""
        fake_response = json.dumps({
            "passed": False,
            "severity_summary": {"low": 0, "medium": 0, "high": 0, "critical": 1},
            "findings": [{"severity": "critical", "category": "合规", "description": "严重合规问题"}],
            "rewrite_target": [],
            "prototype_alignment": {"score": 30, "matched_rules": [], "unmatched_rules": [], "notes": ""}
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(provider_name="fake", model_name="test"))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="这段内容存在严重合规问题。",
            audience="医学专业人士"
        )
        
        output = reviewer.review(input_data)
        
        # 验证 rerun_scope 为 full_gate_rerun
        assert output.rerun_scope == "full_gate_rerun"
    
    def test_all_layer_outputs_together(self):
        """测试三层输出同时存在"""
        fake_response = json.dumps({
            "passed": False,
            "severity_summary": {"low": 1, "medium": 1, "high": 1, "critical": 0},
            "findings": [
                {"severity": "high", "category": "准确性", "description": "术语问题"},
                {"severity": "medium", "category": "表达", "description": "表达问题"},
                {"severity": "low", "category": "标点", "description": "标点建议"}
            ],
            "rewrite_target": [
                {"original": "原句", "suggested": "新句", "reason": "更准确", "priority": "high"}
            ],
            "prototype_alignment": {"score": 60, "matched_rules": [], "unmatched_rules": [], "notes": ""}
        })
        
        provider = FakeLLMProvider(response_content=fake_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(provider_name="fake", model_name="test"))
        reviewer = SemanticReviewer(gateway)
        
        input_data = SemanticReviewInput(
            content="这是一段需要审核的中文医学内容，存在多个问题。",
            audience="医学专业人士"
        )
        
        output = reviewer.review(input_data)
        
        # 验证所有三层输出都存在
        assert output.rule_layer_output is not None
        assert output.model_review_output is not None
        assert output.rewrite_layer_output is not None
        assert output.rerun_scope == "full_gate_rerun"  # 因为有 high 问题
        
        # 验证 model_review_output 包含所有 findings
        assert len(output.model_review_output["findings"]) == 3
        
        # 验证 rewrite_layer_output 包含 rewrite_target
        assert output.rewrite_layer_output["count"] == 1
