# Asset Bridge - 资产桥接器
"""
职责:
- 向核心模块提供统一资产读取接口
- 隔离外部目录结构
- 屏蔽历史系统差异

首批桥接资产类别:
- rules
- editorial
- evidence
- structured

注意: 资产路径不能硬编码进核心模块,必须通过配置层注入
"""

# 数据模型
from .models import AssetKind, AssetTextRecord

# 配置
from .config import AssetBridgeConfig

# 错误
from .errors import (
    AssetBridgeError,
    AssetKindNotConfiguredError,
    AssetRootNotFoundError,
    AssetNotFoundError,
    PathTraversalError,
    AssetReadError,
)

# 实现
from .filesystem import FilesystemAssetBridge

__all__ = [
    # 数据模型
    "AssetKind",
    "AssetTextRecord",
    # 配置
    "AssetBridgeConfig",
    # 错误
    "AssetBridgeError",
    "AssetKindNotConfiguredError",
    "AssetRootNotFoundError",
    "AssetNotFoundError",
    "PathTraversalError",
    "AssetReadError",
    # 实现
    "FilesystemAssetBridge",
]