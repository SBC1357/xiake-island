"""
Tests for Quality Module
"""
import pytest

from src.modules.quality import QualityOrchestrator, QualityResult, GateStatus
from src.modules.writing import CompiledPrompt


class TestQualityResult:
    """测试质量检查结果"""
    
    def test_create_result(self):
        """创建质量检查结果"""
        result = QualityResult()
        
        assert result.overall_status == GateStatus.PASSED
        assert len(result.gates_passed) == 0
        assert result.is_passed is True
    
    def test_add_warning(self):
        """添加警告"""
        result = QualityResult()
        result.add_warning("test_gate", "test warning")
        
        assert len(result.warnings) == 1
        assert result.overall_status == GateStatus.WARNING
        assert result.is_passed is True
    
    def test_add_error(self):
        """添加错误"""
        result = QualityResult()
        result.add_error("test_gate", "test error")
        
        assert len(result.errors) == 1
        assert result.overall_status == GateStatus.FAILED
        assert result.is_passed is False


class TestQualityOrchestrator:
    """测试质量编排器"""
    
    @pytest.fixture
    def orchestrator(self):
        return QualityOrchestrator()
    
    def test_run_gates_success(self, orchestrator):
        """门禁通过"""
        prompt = CompiledPrompt(
            system_prompt="系统指令",
            user_prompt="用户指令"
        )
        
        result = orchestrator.run_gates(prompt)
        
        assert result.is_passed is True
        assert "basic" in result.gates_passed
    
    def test_run_gates_empty_prompt(self, orchestrator):
        """空 prompt 失败"""
        prompt = CompiledPrompt(
            system_prompt="",
            user_prompt=""
        )
        
        result = orchestrator.run_gates(prompt)
        
        assert result.is_passed is False
        assert len(result.errors) > 0
    
    def test_run_gates_on_content(self, orchestrator):
        """对内容运行门禁"""
        result = orchestrator.run_gates_on_content("这是一段测试内容，长度足够。")
        
        assert result.is_passed is True
        assert "basic" in result.gates_passed
        assert "length" in result.gates_passed
    
    def test_run_gates_on_short_content(self, orchestrator):
        """短内容检查"""
        result = orchestrator.run_gates_on_content("短")
        
        assert result.is_passed is False
    
    def test_custom_enabled_gates(self):
        """自定义启用的门禁"""
        orchestrator = QualityOrchestrator(enabled_gates=["basic"])
        
        prompt = CompiledPrompt(
            system_prompt="系统",
            user_prompt="用户"
        )
        
        result = orchestrator.run_gates(prompt)
        
        assert "basic" in result.gates_passed
        assert "schema" not in result.gates_passed  # 未启用
    
    def test_semantic_review_check(self, orchestrator):
        """语义审查检查"""
        result = orchestrator.semantic_review_check("这是一段测试内容")
        
        assert "issues" in result
        assert "suggestions" in result
        assert result["passed"] is True
    
    def test_critical_gate_failure(self):
        """关键门禁失败"""
        orchestrator = QualityOrchestrator(enabled_gates=["basic", "custom"])
        
        # 空 prompt 会导致 basic 门禁失败
        prompt = CompiledPrompt(system_prompt="", user_prompt="")
        
        result = orchestrator.run_gates(prompt)
        
        assert result.overall_status == GateStatus.FAILED
        assert any(e["gate"] == "basic" for e in result.errors)

    def test_boundary_violations_animal_to_human(self, orchestrator):
        """测试越界拦截：动物到人体"""
        content = "该小鼠动物模型在实验中表现优异，这直接治愈患者并在人体内证实了极大的临床获益，可作为新标准。"
        result = orchestrator.run_gates_on_content(content)
        
        assert result.is_passed is False
        assert any(e["gate"] == "boundary_clean" for e in result.errors)
        
    def test_boundary_violations_method_to_clinical(self, orchestrator):
        """测试越界拦截：方法学到临床价值"""
        content = "基于这种最新染色法，表明可以对患者改善生存期。"
        result = orchestrator.run_gates_on_content(content)
        
        assert result.is_passed is False
        assert any(e["gate"] == "boundary_clean" for e in result.errors)

    def test_boundary_violations_pass(self, orchestrator):
        """测试不越界的正常表达应予以放行"""
        content = "该动物模型在实验中表现优异，这为进一步的针对该靶点的临床探索提供了机制信号。"
        result = orchestrator.run_gates_on_content(content)
        
        assert "boundary_clean" in result.gates_passed