"""
Contract 导入测试

测试所有 contract 可导入。
"""
import pytest


def test_base_types_import():
    """测试基础类型可导入"""
    from src.contracts import (
        ContractBaseModel,
        ErrorSeverity,
        TaskStatus,
        ModuleName,
        ErrorCode,
        CONTRACT_VERSION,
    )
    
    assert CONTRACT_VERSION == "1.0.0"
    assert ErrorSeverity.LOW.value == "low"
    assert TaskStatus.RUNNING.value == "running"
    assert ModuleName.OPINION.value == "opinion"
    assert ErrorCode.INTERNAL_ERROR.value == "internal_error"


def test_registry_import():
    """测试注册表可导入"""
    from src.contracts import ContractRegistry, registry
    
    assert ContractRegistry is not None
    assert registry is not None


def test_schema_export_import():
    """测试 schema 导出函数可导入"""
    from src.contracts import (
        export_json_schema,
        export_json_schema_str,
        export_all_schemas,
    )
    
    assert callable(export_json_schema)
    assert callable(export_json_schema_str)
    assert callable(export_all_schemas)


def test_module_error_import():
    """测试 ModuleError 可导入"""
    from src.contracts import ModuleError
    
    assert ModuleError is not None


def test_task_trace_import():
    """测试 TaskTrace 可导入"""
    from src.contracts import TaskTrace
    
    assert TaskTrace is not None


def test_semantic_review_result_import():
    """测试 SemanticReviewResult 可导入"""
    from src.contracts import (
        SemanticReviewResult,
        FindingItem,
        SeveritySummary,
        PrototypeAlignment,
        RewriteTarget,
    )
    
    assert SemanticReviewResult is not None
    assert FindingItem is not None
    assert SeveritySummary is not None
    assert PrototypeAlignment is not None
    assert RewriteTarget is not None


def test_opinion_to_write_import():
    """测试 OpinionToWrite 可导入"""
    from src.contracts import OpinionToWrite, Thesis, SupportPoint
    
    assert OpinionToWrite is not None
    assert Thesis is not None
    assert SupportPoint is not None


def test_review_then_rewrite_import():
    """测试 ReviewThenRewrite 可导入"""
    from src.contracts import ReviewThenRewrite
    
    assert ReviewThenRewrite is not None