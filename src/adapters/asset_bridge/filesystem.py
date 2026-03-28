"""
Filesystem Asset Bridge

实现本地文件系统资产桥接，只支持文本读取。
"""
from pathlib import Path
from typing import List

from .config import AssetBridgeConfig
from .models import AssetKind, AssetTextRecord
from .errors import (
    AssetKindNotConfiguredError,
    AssetRootNotFoundError,
    AssetNotFoundError,
    PathTraversalError,
    AssetReadError,
)


class FilesystemAssetBridge:
    """
    文件系统资产桥接
    
    向核心模块提供统一资产读取接口，只支持本地文件系统。
    只做文本读取，默认 UTF-8 编码。
    
    不实现:
    - 缓存
    - 远程存储
    - 文件监听
    - 索引构建
    - 全文搜索
    - 业务级规则解析
    
    Attributes:
        config: 桥接配置，包含四类资产根目录
    """
    
    def __init__(self, config: AssetBridgeConfig):
        """
        初始化文件系统资产桥接
        
        Args:
            config: 桥接配置，注入四类根目录
        """
        self.config = config
    
    def _validate_path(self, kind: AssetKind, relative_path: str) -> Path:
        """
        验证并解析路径，阻止路径穿越
        
        Args:
            kind: 资产类别
            relative_path: 相对路径
            
        Returns:
            验证后的绝对路径
            
        Raises:
            AssetKindNotConfiguredError: 资产类别未配置
            AssetRootNotFoundError: 配置的根目录不存在
            PathTraversalError: 检测到路径穿越
        """
        # 检查类别是否配置
        root = self.config.get_root(kind)
        if root is None:
            raise AssetKindNotConfiguredError(
                f"资产类别 '{kind.value}' 未配置根目录",
                kind=kind
            )
        
        # 检查根目录是否存在
        if not root.exists():
            raise AssetRootNotFoundError(
                f"资产根目录不存在: {root}",
                kind=kind,
                path=str(root)
            )
        
        # 标准化相对路径，移除开头的斜杠
        normalized_relative = relative_path.lstrip('/\\')
        
        # 检查路径穿越模式
        if '..' in relative_path:
            raise PathTraversalError(
                "检测到路径穿越: 路径包含 '..'",
                kind=kind,
                path=relative_path
            )
        
        # 检查绝对路径逃逸
        if Path(relative_path).is_absolute():
            raise PathTraversalError(
                "检测到路径穿越: 不允许使用绝对路径",
                kind=kind,
                path=relative_path
            )
        
        # 构建完整路径
        full_path = root / normalized_relative
        
        # 解析为绝对路径并验证在根目录内
        # 使用 relative_to 而非 startswith，避免同前缀路径绕过
        # 例如 D:\tmp\ruleset 会匹配 D:\tmp\rules 的前缀
        try:
            resolved_path = full_path.resolve()
            resolved_root = root.resolve()
            
            # 尝试计算相对路径，如果不在根目录内会抛出 ValueError
            resolved_path.relative_to(resolved_root)
        except ValueError:
            # relative_to 失败意味着路径逃逸出根目录
            raise PathTraversalError(
                "检测到路径穿越: 路径逃逸出根目录",
                kind=kind,
                path=relative_path
            )
        except Exception as e:
            if isinstance(e, PathTraversalError):
                raise
            # 其他解析错误也视为路径问题
            raise PathTraversalError(
                f"路径解析失败: {e}",
                kind=kind,
                path=relative_path
            )
        
        return resolved_path
    
    def list_assets(self, kind: AssetKind) -> List[str]:
        """
        列出指定类别的所有资产文件
        
        Args:
            kind: 资产类别
            
        Returns:
            相对路径列表
            
        Raises:
            AssetKindNotConfiguredError: 资产类别未配置
            AssetRootNotFoundError: 配置的根目录不存在
        """
        root = self.config.get_root(kind)
        if root is None:
            raise AssetKindNotConfiguredError(
                f"资产类别 '{kind.value}' 未配置根目录",
                kind=kind
            )
        
        if not root.exists():
            raise AssetRootNotFoundError(
                f"资产根目录不存在: {root}",
                kind=kind,
                path=str(root)
            )
        
        # 递归查找所有文件
        assets = []
        for file_path in root.rglob('*'):
            if file_path.is_file():
                relative = file_path.relative_to(root)
                assets.append(str(relative).replace('\\', '/'))
        
        return sorted(assets)
    
    def read_text(self, kind: AssetKind, relative_path: str) -> AssetTextRecord:
        """
        读取文本资产
        
        Args:
            kind: 资产类别
            relative_path: 相对于根目录的路径
            
        Returns:
            资产文本记录
            
        Raises:
            AssetKindNotConfiguredError: 资产类别未配置
            PathTraversalError: 检测到路径穿越
            AssetNotFoundError: 文件不存在
            AssetReadError: 读取失败
        """
        # 验证并解析路径
        full_path = self._validate_path(kind, relative_path)
        
        # 检查文件是否存在
        if not full_path.exists():
            raise AssetNotFoundError(
                f"资产文件不存在: {relative_path}",
                kind=kind,
                path=relative_path
            )
        
        # 检查是否为文件
        if not full_path.is_file():
            raise AssetNotFoundError(
                f"路径不是文件: {relative_path}",
                kind=kind,
                path=relative_path
            )
        
        # 读取文件内容 (UTF-8)
        try:
            content = full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            raise AssetReadError(
                f"文件编码错误 (需要 UTF-8): {e}",
                kind=kind,
                path=relative_path
            )
        except Exception as e:
            raise AssetReadError(
                f"读取文件失败: {e}",
                kind=kind,
                path=relative_path
            )
        
        # 返回资产记录
        return AssetTextRecord(
            kind=kind,
            relative_path=relative_path.replace('\\', '/'),
            absolute_path=str(full_path),
            content=content
        )
    
    def exists(self, kind: AssetKind, relative_path: str) -> bool:
        """
        检查资产是否存在
        
        Args:
            kind: 资产类别
            relative_path: 相对于根目录的路径
            
        Returns:
            是否存在
            
        Note:
            此方法不抛出异常，对路径穿越等情况返回 False
        """
        try:
            full_path = self._validate_path(kind, relative_path)
            return full_path.exists() and full_path.is_file()
        except Exception:
            return False