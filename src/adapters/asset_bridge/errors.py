"""
Asset Bridge 错误定义

定义桥接层异常，不在桥接层直接做 API 响应。
"""
from typing import Optional

from .models import AssetKind


class AssetBridgeError(Exception):
    """
    Asset Bridge 错误基类
    
    桥接层统一异常，用于表达资产读取失败等错误。
    不在桥接层直接做 API 响应。
    
    Attributes:
        message: 错误消息
        kind: 资产类别 (可选)
        path: 相关路径 (可选)
    """
    
    def __init__(
        self,
        message: str,
        kind: Optional[AssetKind] = None,
        path: Optional[str] = None
    ):
        self.message = message
        self.kind = kind
        self.path = path
        super().__init__(self.message)
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.kind:
            parts.append(f"kind={self.kind.value}")
        if self.path:
            parts.append(f"path={self.path}")
        return " | ".join(parts)


class AssetKindNotConfiguredError(AssetBridgeError):
    """
    资产类别未配置错误
    
    当尝试访问未配置根目录的资产类别时抛出。
    """
    pass


class AssetRootNotFoundError(AssetBridgeError):
    """
    资产根目录不存在错误
    
    当配置的根目录路径不存在时抛出。
    这会把配置错误显式暴露出来，而不是静默返回空结果。
    """
    pass


class AssetNotFoundError(AssetBridgeError):
    """
    资产未找到错误
    
    当指定的资产文件不存在时抛出。
    """
    pass


class PathTraversalError(AssetBridgeError):
    """
    路径穿越错误
    
    当检测到路径穿越攻击 (如 ../ 或绝对路径逃逸) 时抛出。
    """
    pass


class AssetReadError(AssetBridgeError):
    """
    资产读取错误
    
    当读取文件内容失败时抛出。
    """
    pass