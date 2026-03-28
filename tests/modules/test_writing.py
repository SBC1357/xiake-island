"""
Tests for Writing Module

SP-6 Batch 6C: 新增 WritingTrace 和 compile_with_trace 测试。
"""
import pytest

from src.modules.writing import WritingService, CompiledPrompt
from src.modules.writing.models import (
    WritingTrace,
    PlanningConstraintsTrace,
    EvidenceAnchor,
    CompiledPromptWithTrace,
)


class TestCompiledPrompt:
    """测试编译后的 Prompt"""
    
    def test_create_compiled_prompt(self):
        """创建编译后的 Prompt"""
        prompt = CompiledPrompt(
            system_prompt="你是助手",
            user_prompt="请写文章"
        )
        
        assert prompt.system_prompt == "你是助手"
        assert prompt.user_prompt == "请写文章"
    
    def test_to_messages(self):
        """转换为 messages 格式"""
        prompt = CompiledPrompt(
            system_prompt="系统指令",
            user_prompt="用户指令"
        )
        
        messages = prompt.to_messages()
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


class TestWritingTrace:
    """测试写作追踪 - SP-6 Batch 6C"""
    
    def test_planning_constraints_trace_creation(self):
        """测试规划约束追踪创建"""
        constraints = PlanningConstraintsTrace(
            thesis="测试论点",
            outline=[{"title": "引言", "type": "intro"}],
            register="R2",
            audience="医学专业人士",
            style_notes={"formality": "formal"},
            target_word_count=1000
        )
        
        assert constraints.thesis == "测试论点"
        assert constraints.target_word_count == 1000
        assert constraints.register == "R2"
    
    def test_planning_constraints_trace_to_dict(self):
        """测试规划约束追踪序列化"""
        constraints = PlanningConstraintsTrace(
            thesis="测试论点",
            outline=[],
            target_word_count=500
        )
        
        result = constraints.to_dict()
        
        assert "thesis" in result
        assert "target_word_count" in result
        assert result["target_word_count"] == 500
    
    def test_evidence_anchor_creation(self):
        """测试证据锚点创建"""
        anchor = EvidenceAnchor(
            section_index=1,
            section_title="疗效分析",
            fact_ids=["fact_1", "fact_2"],
            domains=["efficacy"]
        )
        
        assert anchor.section_index == 1
        assert len(anchor.fact_ids) == 2
    
    def test_evidence_anchor_to_dict(self):
        """测试证据锚点序列化"""
        anchor = EvidenceAnchor(
            section_index=0,
            section_title="引言",
            fact_ids=["f1"]
        )
        
        result = anchor.to_dict()
        
        assert "section_index" in result
        assert "fact_ids" in result
    
    def test_writing_trace_creation(self):
        """测试写作追踪创建"""
        constraints = PlanningConstraintsTrace(thesis="测试")
        trace = WritingTrace(
            planning_constraints=constraints,
            evidence_anchors=[],
            applied_rule_ids=["play:academic"],
            applied_style_ids=["register:R2"],
            hard_constraints=["thesis_required"],
            advisory_constraints=["target_word_count:1000"]
        )
        
        assert len(trace.applied_rule_ids) == 1
        assert len(trace.hard_constraints) == 1
    
    def test_writing_trace_to_dict(self):
        """测试写作追踪序列化"""
        constraints = PlanningConstraintsTrace(thesis="测试")
        trace = WritingTrace(planning_constraints=constraints)
        
        result = trace.to_dict()
        
        assert "planning_constraints" in result
        assert "evidence_anchors" in result
        assert "applied_rule_ids" in result
        assert "hard_constraints" in result


class TestCompiledPromptWithTrace:
    """测试带追踪的编译结果 - SP-6 Batch 6C"""
    
    @pytest.fixture
    def service(self):
        return WritingService()
    
    def test_compile_with_trace_returns_trace(self, service):
        """compile_with_trace 返回带追踪的结果"""
        evidence_facts = [
            {"fact_id": "f1", "domain": "efficacy", "value": "85%", "definition": "有效率"}
        ]
        
        result = service.compile_with_trace(
            thesis="测试论点",
            outline=[
                {"title": "引言", "type": "intro"},
                {"title": "疗效分析", "type": "domain_section", "domain": "efficacy"},
                {"title": "结论", "type": "conclusion"}
            ],
            evidence_facts=evidence_facts,
            play_id="professional",
            arc_id="evidence_driven",
            target_audience="医学专业人士",
            style_notes={"register": "R2", "formality": "formal"},
            target_word_count=1000
        )
        
        assert result.prompt is not None
        assert result.trace is not None
    
    def test_compile_with_trace_has_planning_constraints(self, service):
        """compile_with_trace 包含规划约束"""
        result = service.compile_with_trace(
            thesis="测试论点",
            outline=[],
            evidence_facts=[],
            target_word_count=800
        )
        
        pc = result.trace.planning_constraints
        assert pc.thesis == "测试论点"
        assert pc.target_word_count == 800
    
    def test_compile_with_trace_has_evidence_anchors(self, service):
        """compile_with_trace 包含证据锚点"""
        evidence_facts = [
            {"fact_id": "f1", "domain": "efficacy", "value": "85%"},
            {"fact_id": "f2", "domain": "safety", "value": "5%"}
        ]
        
        result = service.compile_with_trace(
            thesis="测试",
            outline=[
                {"title": "引言", "type": "intro"},
                {"title": "疗效分析", "type": "domain_section", "domain": "efficacy"},
                {"title": "结论", "type": "conclusion"}
            ],
            evidence_facts=evidence_facts
        )
        
        anchors = result.trace.evidence_anchors
        assert len(anchors) >= 1
        # 疗效分析章节应该有锚点
        efficacy_anchors = [a for a in anchors if "efficacy" in a.domains]
        assert len(efficacy_anchors) == 1
    
    def test_compile_with_trace_has_constraints(self, service):
        """compile_with_trace 包含硬性约束和建议性约束"""
        # R2 应该有硬性约束
        result_r2 = service.compile_with_trace(
            thesis="测试",
            outline=[],
            evidence_facts=[],
            style_notes={"register": "R2"}
        )
        
        assert len(result_r2.trace.hard_constraints) >= 1
        
        # R3/R4 应该有建议性约束
        result_r3 = service.compile_with_trace(
            thesis="测试",
            outline=[],
            evidence_facts=[],
            style_notes={"register": "R3"}
        )
        
        assert len(result_r3.trace.advisory_constraints) >= 1
    
    def test_compile_with_trace_to_dict(self, service):
        """compile_with_trace 可以序列化"""
        result = service.compile_with_trace(
            thesis="测试",
            outline=[],
            evidence_facts=[]
        )
        
        trace_dict = result.trace.to_dict()
        
        assert "planning_constraints" in trace_dict
        assert "evidence_anchors" in trace_dict


class TestWritingService:
    """测试写作服务"""
    
    @pytest.fixture
    def service(self):
        return WritingService()
    
    def test_compile_basic(self, service):
        """基本编译"""
        prompt = service.compile(
            thesis="关于阿尔茨海默病的治疗进展",
            outline=[
                {"title": "引言", "type": "intro"},
                {"title": "结论", "type": "conclusion"}
            ],
            play_id="professional",
            arc_id="evidence_driven"
        )
        
        assert prompt.system_prompt is not None
        assert prompt.user_prompt is not None
        assert "阿尔茨海默病" in prompt.user_prompt
        assert "professional" in prompt.system_prompt
    
    def test_compile_with_key_evidence(self, service):
        """带核心证据的编译"""
        prompt = service.compile(
            thesis="测试论点",
            outline=[{"title": "引言", "type": "intro"}],
            key_evidence=["证据1", "证据2", "证据3"]
        )
        
        assert "核心证据" in prompt.user_prompt
        assert "证据1" in prompt.user_prompt
    
    def test_compile_with_style_notes(self, service):
        """带风格注释的编译"""
        prompt = service.compile(
            thesis="测试论点",
            outline=[],
            style_notes={"register": "R2", "formality": "formal"}
        )
        
        assert "语体等级" in prompt.system_prompt
        assert "R2" in prompt.system_prompt
    
    def test_compile_with_evidence(self, service):
        """带详细证据的编译"""
        evidence_facts = [
            {"domain": "efficacy", "value": "85%", "definition": "有效率"},
            {"domain": "safety", "value": "5%", "definition": "不良事件率"},
        ]
        
        prompt = service.compile_with_evidence(
            thesis="测试论点",
            outline=[{"title": "引言", "type": "intro"}],
            evidence_facts=evidence_facts
        )
        
        assert "证据详情" in prompt.user_prompt
        assert "efficacy" in prompt.user_prompt
        assert prompt.metadata["fact_count"] == 2
    
    def test_model_config_r1(self, service):
        """R1 语体的模型配置"""
        prompt = service.compile(
            thesis="测试",
            outline=[],
            style_notes={"register": "R1"}
        )
        
        assert prompt.model_config["temperature"] == 0.5
    
    def test_model_config_r5(self, service):
        """R5 语体的模型配置"""
        prompt = service.compile(
            thesis="测试",
            outline=[],
            style_notes={"register": "R5"}
        )
        
        assert prompt.model_config["temperature"] == 0.8
    
    def test_model_config_default(self, service):
        """默认模型配置"""
        prompt = service.compile(
            thesis="测试",
            outline=[]
        )
        
        assert prompt.model_config["temperature"] == 0.7
        assert prompt.model_config["max_tokens"] == 2000
    
    def test_domain_section_outline(self, service):
        """domain 章节大纲"""
        prompt = service.compile(
            thesis="测试",
            outline=[
                {"title": "疗效分析", "type": "domain_section", "fact_count": 5}
            ]
        )
        
        assert "5条证据" in prompt.user_prompt