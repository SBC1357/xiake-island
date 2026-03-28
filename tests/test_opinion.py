"""
Opinion Module 测试

使用 FakeLLMProvider 进行测试，不依赖真实外部模型服务。
"""
import pytest
import json
from pydantic import ValidationError

from src.modules.opinion import (
    EvidenceItem,
    EvidenceBundle,
    OpinionInput,
    ThesisOutput,
    SupportPointOutput,
    OpinionOutput,
    OpinionGeneratorConfig,
    OpinionGenerator,
    OpinionModuleError,
    ConfidenceTooLowError,
    OpinionGenerationError,
)
from src.adapters.llm_gateway import (
    FakeLLMProvider,
    LLMGateway,
    LLMGatewayConfig,
)


class TestEvidenceItem:
    """测试 EvidenceItem"""
    
    def test_evidence_item_with_required_fields(self):
        """测试证据项 - 必填字段"""
        item = EvidenceItem(id="e1", content="Test evidence")
        assert item.id == "e1"
        assert item.content == "Test evidence"
        assert item.source is None
        assert item.relevance is None
    
    def test_evidence_item_with_all_fields(self):
        """测试证据项 - 所有字段"""
        item = EvidenceItem(
            id="e1",
            content="Test evidence",
            source="PubMed",
            relevance=0.9
        )
        assert item.source == "PubMed"
        assert item.relevance == 0.9
    
    def test_evidence_item_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            EvidenceItem(id="e1", content="Test", unknown="field")


class TestOpinionInput:
    """测试 OpinionInput"""
    
    @pytest.fixture
    def valid_input(self):
        """创建有效输入"""
        return OpinionInput(
            evidence_bundle=EvidenceBundle(
                items=[
                    EvidenceItem(id="e1", content="Evidence 1"),
                    EvidenceItem(id="e2", content="Evidence 2"),
                ]
            ),
            audience="医学专业人士"
        )
    
    def test_input_with_required_fields(self, valid_input):
        """测试输入 - 必填字段"""
        assert len(valid_input.evidence_bundle.items) == 2
        assert valid_input.audience == "医学专业人士"
        assert valid_input.thesis_hint is None
        assert valid_input.context_metadata is None
    
    def test_input_with_all_fields(self):
        """测试输入 - 所有字段"""
        input_data = OpinionInput(
            evidence_bundle=EvidenceBundle(items=[]),
            audience="普通公众",
            thesis_hint="关注安全性",
            context_metadata={"source": "test"}
        )
        assert input_data.thesis_hint == "关注安全性"
        assert input_data.context_metadata == {"source": "test"}
    
    def test_input_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            OpinionInput(
                evidence_bundle=EvidenceBundle(items=[]),
                audience="test",
                unknown_field="value"
            )


class TestOpinionOutput:
    """测试 OpinionOutput"""
    
    def test_output_with_required_fields(self):
        """测试输出 - 必填字段"""
        thesis = ThesisOutput(statement="Test thesis", confidence=0.8)
        output = OpinionOutput(thesis=thesis)
        
        assert output.thesis.statement == "Test thesis"
        assert output.thesis.confidence == 0.8
        assert output.support_points == []
    
    def test_output_with_all_fields(self):
        """测试输出 - 所有字段"""
        thesis = ThesisOutput(
            statement="Test thesis",
            confidence=0.8,
            evidence_refs=["e1", "e2"]
        )
        support = SupportPointOutput(
            content="Support 1",
            strength="strong",
            evidence_id="e1"
        )
        
        output = OpinionOutput(
            thesis=thesis,
            support_points=[support],
            boundaries={"scope": "limited"},
            confidence_notes={
                "overall_confidence": 0.8,
                "limitations": ["Test limitation"],
                "assumptions": ["Test assumption"]
            }
        )
        
        assert len(output.support_points) == 1
        assert output.support_points[0].strength == "strong"
    
    def test_output_extra_field_fails(self):
        """测试额外字段失败"""
        thesis = ThesisOutput(statement="Test", confidence=0.5)
        with pytest.raises(ValidationError):
            OpinionOutput(thesis=thesis, unknown="field")


class TestOpinionGeneratorConfig:
    """测试 OpinionGeneratorConfig"""
    
    def test_config_default_values(self):
        """测试配置默认值"""
        config = OpinionGeneratorConfig()
        assert config.min_confidence == 0.5
        assert config.max_support_points == 5
        assert config.require_evidence_mapping is True
    
    def test_config_custom_values(self):
        """测试配置自定义值"""
        config = OpinionGeneratorConfig(
            min_confidence=0.7,
            max_support_points=3,
            require_evidence_mapping=False
        )
        assert config.min_confidence == 0.7
        assert config.max_support_points == 3
    
    def test_config_extra_field_fails(self):
        """测试额外字段失败"""
        with pytest.raises(ValidationError):
            OpinionGeneratorConfig(unknown_option=True)


class TestOpinionGenerator:
    """测试 OpinionGenerator"""
    
    @pytest.fixture
    def gateway_with_fake_provider(self):
        """创建使用 FakeLLMProvider 的 Gateway"""
        # 返回有效的 JSON 响应
        fake_response = json.dumps({
            "thesis": {
                "statement": "该药物在临床试验中显示出良好的疗效",
                "confidence": 0.85,
                "evidence_refs": ["e1", "e2"]
            },
            "support_points": [
                {
                    "content": "主要终点达到统计学显著性",
                    "strength": "strong",
                    "evidence_id": "e1"
                }
            ],
            "limitations": ["样本量有限"],
            "assumptions": ["患者依从性良好"]
        })
        
        provider = FakeLLMProvider(
            name="test-fake",
            response_content=fake_response,
            latency_ms=5
        )
        config = LLMGatewayConfig(
            provider_name="test-fake",
            model_name="test-model"
        )
        return LLMGateway(provider, config)
    
    @pytest.fixture
    def valid_input(self):
        """创建有效输入"""
        return OpinionInput(
            evidence_bundle=EvidenceBundle(
                items=[
                    EvidenceItem(id="e1", content="Clinical trial showed significant results"),
                    EvidenceItem(id="e2", content="Safety profile is acceptable"),
                ],
                summary="Positive clinical trial results"
            ),
            audience="医学专业人士",
            thesis_hint="关注疗效和安全性"
        )
    
    def test_generator_success(self, gateway_with_fake_provider, valid_input):
        """测试生成器成功生成观点"""
        generator = OpinionGenerator(gateway_with_fake_provider)
        output = generator.generate(valid_input)
        
        assert output.thesis.statement == "该药物在临床试验中显示出良好的疗效"
        assert output.thesis.confidence == 0.85
        assert len(output.support_points) == 1
        assert output.confidence_notes is not None
    
    def test_generator_respects_max_support_points(self, gateway_with_fake_provider, valid_input):
        """测试生成器遵守最大支撑点数限制"""
        config = OpinionGeneratorConfig(max_support_points=1)
        generator = OpinionGenerator(gateway_with_fake_provider, config)
        output = generator.generate(valid_input)
        
        assert len(output.support_points) <= 1
    
    def test_generator_confidence_too_low(self):
        """测试置信度过低抛出异常"""
        # 返回低置信度响应
        low_confidence_response = json.dumps({
            "thesis": {
                "statement": "证据不足",
                "confidence": 0.3,
                "evidence_refs": []
            },
            "support_points": [],
            "limitations": ["证据质量低"],
            "assumptions": []
        })
        
        provider = FakeLLMProvider(response_content=low_confidence_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="test",
            model_name="test"
        ))
        generator = OpinionGenerator(gateway, OpinionGeneratorConfig(min_confidence=0.5))
        
        input_data = OpinionInput(
            evidence_bundle=EvidenceBundle(items=[EvidenceItem(id="e1", content="test")]),
            audience="test"
        )
        
        with pytest.raises(ConfidenceTooLowError) as exc_info:
            generator.generate(input_data)
        
        assert "置信度" in str(exc_info.value)
    
    def test_generator_handles_markdown_json(self):
        """测试生成器处理 markdown 代码块中的 JSON"""
        markdown_response = """```json
{
  "thesis": {
    "statement": "Test thesis",
    "confidence": 0.8,
    "evidence_refs": []
  },
  "support_points": [],
  "limitations": [],
  "assumptions": []
}
```"""
        
        provider = FakeLLMProvider(response_content=markdown_response)
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="test",
            model_name="test"
        ))
        generator = OpinionGenerator(gateway)
        
        input_data = OpinionInput(
            evidence_bundle=EvidenceBundle(items=[EvidenceItem(id="e1", content="test")]),
            audience="test"
        )
        
        output = generator.generate(input_data)
        assert output.thesis.statement == "Test thesis"
    
    def test_generator_handles_llm_error(self):
        """测试生成器处理 LLM 错误"""
        provider = FakeLLMProvider(should_fail=True)
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="test",
            model_name="test",
            max_retries=0
        ))
        generator = OpinionGenerator(gateway)
        
        input_data = OpinionInput(
            evidence_bundle=EvidenceBundle(items=[EvidenceItem(id="e1", content="test")]),
            audience="test"
        )
        
        with pytest.raises(OpinionGenerationError):
            generator.generate(input_data)
    
    def test_generator_handles_invalid_json(self):
        """测试生成器处理无效 JSON"""
        provider = FakeLLMProvider(response_content="This is not valid JSON")
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="test",
            model_name="test"
        ))
        generator = OpinionGenerator(gateway)
        
        input_data = OpinionInput(
            evidence_bundle=EvidenceBundle(items=[EvidenceItem(id="e1", content="test")]),
            audience="test"
        )
        
        with pytest.raises(OpinionGenerationError) as exc_info:
            generator.generate(input_data)
        
        assert "解析" in str(exc_info.value)


class TestOpinionGeneratorIntegration:
    """测试 OpinionGenerator 与 LLM Gateway 集成"""
    
    def test_full_pipeline(self):
        """测试完整管道"""
        # 创建返回结构化响应的 fake provider
        response = json.dumps({
            "thesis": {
                "statement": "二甲双胍在2型糖尿病患者中具有良好的安全性和有效性",
                "confidence": 0.9,
                "evidence_refs": ["e1", "e2"]
            },
            "support_points": [
                {
                    "content": "多项大型临床试验证实其有效性",
                    "strength": "strong",
                    "evidence_id": "e1"
                },
                {
                    "content": "长期安全性数据充分",
                    "strength": "medium",
                    "evidence_id": "e2"
                }
            ],
            "limitations": ["缺乏头对头比较研究"],
            "assumptions": ["患者肾功能正常"]
        })
        
        provider = FakeLLMProvider(response_content=response)
        gateway = LLMGateway(provider, LLMGatewayConfig(
            provider_name="integration-test",
            model_name="test-model"
        ))
        generator = OpinionGenerator(gateway)
        
        input_data = OpinionInput(
            evidence_bundle=EvidenceBundle(
                items=[
                    EvidenceItem(
                        id="e1",
                        content="Meta分析显示二甲双胍降低HbA1c 1.5%",
                        source="Cochrane Review"
                    ),
                    EvidenceItem(
                        id="e2",
                        content="UKPDS研究证实长期安全性",
                        source="UKPDS"
                    ),
                ],
                summary="二甲双胍循证证据充分"
            ),
            audience="内分泌科医生",
            thesis_hint="重点关注疗效和安全性"
        )
        
        output = generator.generate(input_data)
        
        # 验证输出结构
        assert output.thesis.confidence >= 0.8
        assert len(output.support_points) >= 1
        assert output.evidence_mapping is not None
        assert output.confidence_notes is not None
        assert len(output.confidence_notes.limitations) >= 1