"""
Tests for Planning Module
"""
import pytest
from datetime import datetime

from src.modules.planning import PlanningService, RouteContext, EditorialPlan


class TestRouteContext:
    """测试路由上下文"""
    
    def test_create_route_context(self):
        """创建路由上下文"""
        context = RouteContext(
            product_id="lecanemab",
            register="R2",
            audience="医学专业人士"
        )
        
        assert context.product_id == "lecanemab"
        assert context.register == "R2"
        assert context.audience == "医学专业人士"
        assert context.task_id.startswith("task_")
    
    def test_invalid_register(self):
        """无效的 register 值"""
        with pytest.raises(ValueError):
            RouteContext(
                product_id="test",
                register="R6"  # 无效值
            )
    
    def test_default_values(self):
        """默认值"""
        context = RouteContext(product_id="test")
        
        assert context.register == "R2"
        assert context.audience is None
        assert context.task_category == "project"


class TestPlanningService:
    """测试规划服务"""
    
    @pytest.fixture
    def service(self):
        return PlanningService()
    
    def test_plan_basic(self, service):
        """基本规划"""
        context = RouteContext(
            product_id="lecanemab",
            register="R2",
            audience="医生"
        )
        
        plan = service.plan(context)
        
        assert plan.thesis is not None
        assert len(plan.outline) >= 2  # 至少有引言和结论
        assert plan.play_id == "professional"
        assert plan.arc_id == "evidence_driven"
    
    def test_plan_with_evidence(self, service):
        """带证据的规划"""
        context = RouteContext(
            product_id="lecanemab",
            register="R2"
        )
        
        evidence_facts = [
            {"domain": "efficacy", "content": "疗效证据1"},
            {"domain": "efficacy", "content": "疗效证据2"},
            {"domain": "safety", "content": "安全性证据1"},
        ]
        
        plan = service.plan(context, evidence_facts=evidence_facts)
        
        assert "efficacy" in plan.thesis or "safety" in plan.thesis or "lecanemab" in plan.thesis
        # 应该有疗效分析和章节
        section_titles = [item["title"] for item in plan.outline]
        assert any("疗效" in title for title in section_titles)
    
    def test_plan_with_selected_facts(self, service):
        """带选中事实的规划"""
        context = RouteContext(
            product_id="test",
            register="R1"
        )
        
        plan = service.plan(context, selected_facts=["fact1", "fact2", "fact3", "fact4", "fact5", "fact6"])
        
        assert len(plan.key_evidence) == 5  # 最多5个核心证据
        assert plan.play_id == "academic"
    
    def test_domain_to_title(self, service):
        """domain 转标题"""
        assert service._domain_to_title("efficacy") == "疗效分析"
        assert service._domain_to_title("safety") == "安全性评估"
        assert service._domain_to_title("unknown") == "Unknown"
    
    def test_register_to_formality(self, service):
        """语体等级转正式程度"""
        assert service._register_to_formality("R1") == "highly_formal"
        assert service._register_to_formality("R2") == "formal"
        assert service._register_to_formality("R5") == "casual"


class TestEditorialPlan:
    """测试编辑计划"""
    
    def test_create_plan(self):
        """创建编辑计划"""
        plan = EditorialPlan(
            thesis="核心论点",
            outline=[{"title": "引言", "type": "intro"}],
            play_id="professional",
            target_audience="医生"
        )
        
        assert plan.thesis == "核心论点"
        assert len(plan.outline) == 1
        assert plan.play_id == "professional"


class TestPersonaProfile:
    """测试人格画像"""
    
    def test_get_persona(self):
        """获取人格画像"""
        service = PlanningService()
        
        persona = service.get_persona("medical_expert")
        
        assert persona is not None
        assert persona.profile_id == "medical_expert"
        assert persona.author_name == "医学专家"
    
    def test_get_nonexistent_persona(self):
        """获取不存在的人格画像"""
        service = PlanningService()
        
        persona = service.get_persona("nonexistent")
        
        assert persona is None