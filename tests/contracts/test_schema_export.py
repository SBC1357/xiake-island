"""
Contract Schema 导出测试

测试每个 contract 都能导出 JSON Schema。
"""
import pytest
from src.contracts import (
    registry,
    export_json_schema,
    export_json_schema_str,
    ModuleError,
    TaskTrace,
    SemanticReviewResult,
    OpinionToWrite,
    ReviewThenRewrite,
)


def test_module_error_schema_export():
    """测试 ModuleError 可导出 JSON Schema"""
    schema = export_json_schema(ModuleError)
    
    assert "properties" in schema
    assert "code" in schema["properties"]
    assert "message" in schema["properties"]
    assert "module" in schema["properties"]


def test_task_trace_schema_export():
    """测试 TaskTrace 可导出 JSON Schema"""
    schema = export_json_schema(TaskTrace)
    
    assert "properties" in schema
    assert "task_id" in schema["properties"]
    assert "status" in schema["properties"]
    assert "module" in schema["properties"]


def test_semantic_review_result_schema_export():
    """测试 SemanticReviewResult 可导出 JSON Schema"""
    schema = export_json_schema(SemanticReviewResult)
    
    assert "properties" in schema
    # 验证关键字段存在
    assert "passed" in schema["properties"]
    assert "severity_summary" in schema["properties"]
    assert "findings" in schema["properties"]
    assert "rewrite_target" in schema["properties"]
    assert "prototype_alignment" in schema["properties"]


def test_opinion_to_write_schema_export():
    """测试 OpinionToWrite 可导出 JSON Schema"""
    schema = export_json_schema(OpinionToWrite)
    
    assert "properties" in schema
    assert "thesis" in schema["properties"]
    assert "support_points" in schema["properties"]
    assert "audience" in schema["properties"]


def test_review_then_rewrite_schema_export():
    """测试 ReviewThenRewrite 可导出 JSON Schema"""
    schema = export_json_schema(ReviewThenRewrite)
    
    assert "properties" in schema
    assert "original_content" in schema["properties"]
    assert "rewrite_targets" in schema["properties"]
    assert "passed" in schema["properties"]


def test_schema_export_to_string():
    """测试 JSON Schema 可导出为字符串"""
    schema_str = export_json_schema_str(ModuleError)
    
    assert isinstance(schema_str, str)
    assert '"code"' in schema_str
    assert '"message"' in schema_str


def test_all_registered_contracts_have_schema():
    """测试所有已注册的 contract 都能导出 schema"""
    for name in registry.list_contracts():
        model = registry.get(name)
        assert model is not None, f"Contract {name} not found in registry"
        
        schema = export_json_schema(model)
        assert "properties" in schema, f"Contract {name} schema has no properties"