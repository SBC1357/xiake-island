"""
Hash Utilities

提供输入数据哈希计算函数，用于任务版本分组。
"""
import hashlib
import json
from typing import Any


def compute_input_hash(input_data: dict[str, Any]) -> str:
    """
    计算输入数据的哈希值
    
    使用 SHA256 算法计算输入数据的哈希值，用于版本分组。
    相同参数的任务归为同一"参数组"，每次执行产生一个新版本。
    
    Args:
        input_data: 输入数据字典
        
    Returns:
        16字符的哈希字符串
        
    Example:
        >>> compute_input_hash({"audience": "医生", "content": "test"})
        'a1b2c3d4e5f67890'
    """
    # 过滤敏感信息（如 API key）后再计算哈希
    filtered_data = _filter_sensitive_fields(input_data)
    
    # 使用 sort_keys=True 确保相同内容产生相同哈希
    # 使用 ensure_ascii=False 支持中文字符
    json_str = json.dumps(filtered_data, sort_keys=True, ensure_ascii=False)
    
    # 计算 SHA256 并取前 16 位
    hash_value = hashlib.sha256(json_str.encode('utf-8')).hexdigest()[:16]
    
    return hash_value


def compute_output_hash(output_data: dict[str, Any]) -> str:
    """
    计算输出数据的哈希值
    
    使用 SHA256 算法计算输出数据的哈希值，用于结果版本追踪。
    相同输出结果产生相同哈希，便于去重和缓存识别。
    
    Args:
        output_data: 输出数据字典
        
    Returns:
        16字符的哈希字符串
        
    Example:
        >>> compute_output_hash({"content": "生成的内容", "status": "completed"})
        'b2c3d4e5f6789012'
    """
    # 过滤敏感信息后再计算哈希
    filtered_data = _filter_sensitive_fields(output_data)
    
    # 使用 sort_keys=True 确保相同内容产生相同哈希
    # 使用 ensure_ascii=False 支持中文字符
    json_str = json.dumps(filtered_data, sort_keys=True, ensure_ascii=False)
    
    # 计算 SHA256 并取前 16 位
    hash_value = hashlib.sha256(json_str.encode('utf-8')).hexdigest()[:16]
    
    return hash_value


def _filter_sensitive_fields(data: dict[str, Any]) -> dict[str, Any]:
    """
    过滤敏感字段
    
    移除不应被存储或用于哈希计算的敏感字段。
    
    Args:
        data: 原始数据字典
        
    Returns:
        过滤后的数据字典
    """
    # 定义敏感字段列表
    SENSITIVE_FIELDS = {
        'api_key',
        'apikey',
        'api_secret',
        'secret',
        'password',
        'token',
        'access_token',
        'refresh_token',
        'authorization',
    }
    
    def _filter_recursive(obj: Any) -> Any:
        """递归过滤"""
        if isinstance(obj, dict):
            return {
                k: _filter_recursive(v)
                for k, v in obj.items()
                if k.lower() not in SENSITIVE_FIELDS
            }
        elif isinstance(obj, list):
            return [_filter_recursive(item) for item in obj]
        else:
            return obj
    
    return _filter_recursive(data)