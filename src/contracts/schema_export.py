"""
JSON Schema 导出工具

提供将 Pydantic 模型导出为 JSON Schema 的能力。
"""
import json
from typing import Type, Dict, Any
from pydantic import BaseModel


def export_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    将 Pydantic 模型导出为 JSON Schema
    
    Args:
        model: Pydantic 模型类
        
    Returns:
        JSON Schema 字典
    """
    return model.model_json_schema()


def export_json_schema_str(model: Type[BaseModel], indent: int = 2) -> str:
    """
    将 Pydantic 模型导出为 JSON Schema 字符串
    
    Args:
        model: Pydantic 模型类
        indent: 缩进空格数
        
    Returns:
        JSON Schema 字符串
    """
    schema = export_json_schema(model)
    return json.dumps(schema, indent=indent, ensure_ascii=False)


def export_all_schemas(models: Dict[str, Type[BaseModel]]) -> Dict[str, Dict[str, Any]]:
    """
    批量导出多个模型的 JSON Schema
    
    Args:
        models: 模型名称到模型类的映射
        
    Returns:
        模型名称到 JSON Schema 的映射
    """
    return {
        name: export_json_schema(model) 
        for name, model in models.items()
    }