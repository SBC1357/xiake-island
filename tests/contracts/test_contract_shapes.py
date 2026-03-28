"""
Contract 结构测试

测试 contract 的结构形状和基本实例化。
"""
import pytest
from src.contracts import (
    registry,
    ModuleError,
    TaskTrace,
    SemanticReviewResult,
    FindingItem,
    SeveritySummary,
    PrototypeAlignment,
    RewriteTarget,
    OpinionToWrite,
    Thesis,
    SupportPoint,
    ReviewThenRewrite,
    ErrorSeverity,
    TaskStatus,
    ModuleName,
    ErrorCode,
)


class TestModuleError:
    """ModuleError contract 测试"""
    
    def test_module_error_instantiation(self):
        """测试 ModuleError 可实例化"""
        error = ModuleError(
            code=ErrorCode.INTERNAL_ERROR,
            message="测试错误",
            module=ModuleName.OPINION
        )
        
        assert error.code == ErrorCode.INTERNAL_ERROR
        assert error.message == "测试错误"
        assert error.module == ModuleName.OPINION
        assert error.recoverable is False
        assert error.retry_count == 0
    
    def test_module_error_with_details(self):
        """测试 ModuleError 可带详情"""
        error = ModuleError(
            code=ErrorCode.LLM_ERROR,
            message="LLM 调用失败",
            module=ModuleName.SEMANTIC_REVIEW,
            details={"reason": "timeout"},
            recoverable=True,
            retry_count=2
        )
        
        assert error.details == {"reason": "timeout"}
        assert error.recoverable is True
        assert error.retry_count == 2


class TestTaskTrace:
    """TaskTrace contract 测试"""
    
    def test_task_trace_instantiation(self):
        """测试 TaskTrace 可实例化"""
        trace = TaskTrace(
            task_id="task-001",
            status=TaskStatus.RUNNING,
            module=ModuleName.OPINION
        )
        
        assert trace.task_id == "task-001"
        assert trace.status == TaskStatus.RUNNING
        assert trace.module == ModuleName.OPINION
    
    def test_task_trace_with_parent(self):
        """测试 TaskTrace 可带父任务"""
        trace = TaskTrace(
            task_id="task-002",
            status=TaskStatus.COMPLETED,
            module=ModuleName.ORCHESTRATOR,
            parent_task_id="task-001",
            duration_ms=1500
        )
        
        assert trace.parent_task_id == "task-001"
        assert trace.duration_ms == 1500


class TestSemanticReviewResult:
    """SemanticReviewResult contract 测试"""
    
    def test_semantic_review_result_passed(self):
        """测试 SemanticReviewResult 通过场景"""
        result = SemanticReviewResult(passed=True)
        
        assert result.passed is True
        assert len(result.findings) == 0
    
    def test_semantic_review_result_with_findings(self):
        """测试 SemanticReviewResult 带发现项"""
        finding = FindingItem(
            severity=ErrorSeverity.HIGH,
            category="consistency",
            description="内容不一致",
            location="第3段",
            suggestion="请核实数据"
        )
        
        summary = SeveritySummary(low=0, medium=0, high=1, critical=0)
        
        result = SemanticReviewResult(
            passed=False,
            severity_summary=summary,
            findings=[finding]
        )
        
        assert result.passed is False
        assert result.severity_summary.high == 1
        assert len(result.findings) == 1
        assert result.findings[0].severity == ErrorSeverity.HIGH
    
    def test_semantic_review_result_with_prototype_alignment(self):
        """测试 SemanticReviewResult 带原型对齐"""
        alignment = PrototypeAlignment(
            score=85,
            matched_rules=["rule-1", "rule-2"],
            unmatched_rules=["rule-3"],
            notes="基本符合原型要求"
        )
        
        result = SemanticReviewResult(
            passed=True,
            prototype_alignment=alignment
        )
        
        assert result.prototype_alignment.score == 85
        assert len(result.prototype_alignment.matched_rules) == 2


class TestOpinionToWrite:
    """OpinionToWrite contract 测试"""
    
    def test_opinion_to_write_instantiation(self):
        """测试 OpinionToWrite 可实例化"""
        thesis = Thesis(
            statement="该药物对目标人群有效",
            confidence=0.85,
            evidence_refs=["evidence-001"]
        )
        
        handoff = OpinionToWrite(
            thesis=thesis,
            audience="医生",
            style_hint="专业严谨"
        )
        
        assert handoff.thesis.statement == "该药物对目标人群有效"
        assert handoff.thesis.confidence == 0.85
        assert handoff.audience == "医生"
    
    def test_opinion_to_write_with_support_points(self):
        """测试 OpinionToWrite 带支撑点"""
        thesis = Thesis(
            statement="观点陈述",
            confidence=0.9
        )
        
        support = SupportPoint(
            content="支撑论据1",
            strength="strong",
            evidence_id="ev-001"
        )
        
        handoff = OpinionToWrite(
            thesis=thesis,
            support_points=[support],
            audience="患者"
        )
        
        assert len(handoff.support_points) == 1
        assert handoff.support_points[0].strength == "strong"


class TestReviewThenRewrite:
    """ReviewThenRewrite contract 测试"""
    
    def test_review_then_rewrite_instantiation(self):
        """测试 ReviewThenRewrite 可实例化"""
        handoff = ReviewThenRewrite(
            original_content="原始内容",
            passed=False
        )
        
        assert handoff.original_content == "原始内容"
        assert handoff.passed is False
    
    def test_review_then_rewrite_with_targets(self):
        """测试 ReviewThenRewrite 带改写目标"""
        target = RewriteTarget(
            original="原始句子",
            suggested="修改后的句子",
            reason="表述不准确",
            priority=ErrorSeverity.HIGH
        )
        
        handoff = ReviewThenRewrite(
            original_content="原始内容",
            rewrite_targets=[target],
            passed=False
        )
        
        assert len(handoff.rewrite_targets) == 1
        assert handoff.rewrite_targets[0].priority == ErrorSeverity.HIGH


class TestRegistry:
    """Registry 测试"""
    
    def test_registry_has_all_contracts(self):
        """测试注册表包含所有首批 contract"""
        expected = [
            "module_error",
            "task_trace",
            "semantic_review_result",
            "opinion_to_write",
            "review_then_rewrite",
        ]
        
        for name in expected:
            assert registry.is_registered(name), f"Contract {name} not registered"
    
    def test_registry_get_by_name(self):
        """测试注册表可按名称获取模型"""
        model = registry.get("module_error")
        assert model is ModuleError
        
        model = registry.get("semantic_review_result")
        assert model is SemanticReviewResult
    
    def test_registry_get_version(self):
        """测试注册表可获取版本"""
        version = registry.get_version("module_error")
        assert version == "1.0.0"


class TestStrictMode:
    """Strict 模式测试 - 验证类型约束不被静默转换"""
    
    def test_module_error_rejects_string_bool(self):
        """测试 ModuleError 拒绝字符串类型的 bool"""
        with pytest.raises(Exception):
            ModuleError(
                code=ErrorCode.INTERNAL_ERROR,
                message="测试错误",
                module=ModuleName.OPINION,
                recoverable="false"  # 字符串，应被拒绝
            )
    
    def test_module_error_rejects_string_int(self):
        """测试 ModuleError 拒绝字符串类型的 int"""
        with pytest.raises(Exception):
            ModuleError(
                code=ErrorCode.INTERNAL_ERROR,
                message="测试错误",
                module=ModuleName.OPINION,
                retry_count="2"  # 字符串，应被拒绝
            )
    
    def test_task_trace_rejects_string_int(self):
        """测试 TaskTrace 拒绝字符串类型的 int"""
        with pytest.raises(Exception):
            TaskTrace(
                task_id="task-001",
                status=TaskStatus.RUNNING,
                module=ModuleName.OPINION,
                duration_ms="10"  # 字符串，应被拒绝
            )
    
    def test_thesis_rejects_string_float(self):
        """测试 Thesis 拒绝字符串类型的 float"""
        with pytest.raises(Exception):
            Thesis(
                statement="测试观点",
                confidence="0.9"  # 字符串，应被拒绝
            )


class TestSupportPointStrengthLiteral:
    """SupportPoint.strength Literal 约束测试"""
    
    def test_support_point_accepts_valid_strengths(self):
        """测试 SupportPoint 接受有效的 strength 值"""
        for strength in ["weak", "medium", "strong"]:
            sp = SupportPoint(content="测试内容", strength=strength)
            assert sp.strength == strength
    
    def test_support_point_rejects_invalid_strength(self):
        """测试 SupportPoint 拒绝无效的 strength 值"""
        with pytest.raises(Exception):
            SupportPoint(
                content="测试内容",
                strength="banana"  # 无效值，应被拒绝
            )
    
    def test_support_point_rejects_numeric_strength(self):
        """测试 SupportPoint 拒绝数字类型的 strength"""
        with pytest.raises(Exception):
            SupportPoint(
                content="测试内容",
                strength=1  # 数字，应被拒绝
            )
    
    def test_support_point_default_is_medium(self):
        """测试 SupportPoint 默认 strength 为 medium"""
        sp = SupportPoint(content="测试内容")
        assert sp.strength == "medium"
        """测试注册表可获取版本"""
        version = registry.get_version("module_error")
        assert version == "1.0.0"