"""
应用装配模块

提供应用级的依赖注入和配置管理。

重要：所有外部路径通过环境变量注入，不硬编码。
"""
import os
from pathlib import Path
from typing import Optional

from src.adapters.asset_bridge import AssetBridgeConfig, FilesystemAssetBridge, AssetKind
from src.env_utils import get_env_flag, path_from_env


# ==================== 配置环境变量 ====================

# 藏经阁消费者根目录
XIAGEDAO_CONSUMER_ROOT = "XIAGEDAO_CONSUMER_ROOT"

# 严格模式开关（生产环境默认启用）
XIAGEDAO_STRICT_MODE = "XIAGEDAO_STRICT_MODE"

# 其他可选目录
XIAGEDAO_RULES_ROOT = "XIAGEDAO_RULES_ROOT"
XIAGEDAO_EDITORIAL_ROOT = "XIAGEDAO_EDITORIAL_ROOT"
XIAGEDAO_EVIDENCE_ROOT = "XIAGEDAO_EVIDENCE_ROOT"
XIAGEDAO_STRUCTURED_ROOT = "XIAGEDAO_STRUCTURED_ROOT"


def _to_path(v: str | None) -> Path | None:
    """兼容旧调用点，统一委托给共享路径解析工具。"""
    return path_from_env(v)


# ==================== 应用级单例 ====================

_shared_asset_bridge: Optional[FilesystemAssetBridge] = None


def get_asset_bridge() -> FilesystemAssetBridge:
    """
    获取应用级共享的 AssetBridge 实例
    
    配置来源（按优先级）：
    1. 环境变量 XIAGEDAO_CONSUMER_ROOT
    2. 其他可选环境变量（rules, editorial, evidence, structured）
    
    严格模式（XIAGEDAO_STRICT_MODE=true，默认）：
        - 强制要求 consumer_root 必须配置且有效
        - 启动时调用 validate_consumer_config 验证
        - 验证失败会抛出 ValueError
    
    非严格模式（XIAGEDAO_STRICT_MODE=false，用于开发/测试）：
        - 允许 consumer_root 未配置
        - 仅打印警告信息，继续启动
    
    Returns:
        FilesystemAssetBridge: 共享的资产桥接实例
        
    Raises:
        ValueError: 如果 consumer_root 未配置或无效（严格模式下）
    """
    global _shared_asset_bridge
    
    if _shared_asset_bridge is not None:
        return _shared_asset_bridge
    
    # 读取严格模式配置（默认 true）
    strict_mode = get_env_flag(XIAGEDAO_STRICT_MODE, default=True)
    
    # 从环境变量读取配置
    consumer_root = _to_path(os.environ.get(XIAGEDAO_CONSUMER_ROOT))
    
    # 严格模式下验证消费者配置
    if strict_mode:
        is_valid, message = validate_consumer_config()
        if not is_valid:
            raise ValueError(f"消费者配置无效: {message}")
    else:
        # 非严格模式下，仅警告不阻止
        if consumer_root is None:
            print(f"警告: {XIAGEDAO_CONSUMER_ROOT} 未配置，asset_bridge 将无法访问消费者目录")
    
    config = AssetBridgeConfig(
        consumer_root=consumer_root,
        rules_root=_to_path(os.environ.get(XIAGEDAO_RULES_ROOT)),
        editorial_root=_to_path(os.environ.get(XIAGEDAO_EDITORIAL_ROOT)),
        evidence_root=_to_path(os.environ.get(XIAGEDAO_EVIDENCE_ROOT)),
        structured_root=_to_path(os.environ.get(XIAGEDAO_STRUCTURED_ROOT)),
    )
    
    _shared_asset_bridge = FilesystemAssetBridge(config)
    return _shared_asset_bridge


def reset_asset_bridge() -> None:
    """重置共享的 AssetBridge 实例（主要用于测试）"""
    global _shared_asset_bridge
    _shared_asset_bridge = None


def validate_consumer_config() -> tuple[bool, str]:
    """
    验证消费者配置是否有效
    
    Returns:
        (is_valid, message)
    """
    raw_consumer_root = os.environ.get(XIAGEDAO_CONSUMER_ROOT)
    consumer_root = _to_path(raw_consumer_root)

    if consumer_root is None:
        return False, f"{XIAGEDAO_CONSUMER_ROOT} 未配置"

    if not consumer_root.exists():
        return False, f"消费者目录不存在: {consumer_root}"

    if not os.access(consumer_root, os.R_OK):
        return False, f"消费者目录不可读: {consumer_root}"

    return True, f"消费者配置有效: {consumer_root}"


# ==================== EvidenceService 单例 ====================

_shared_evidence_service: Optional["EvidenceService"] = None


def get_evidence_service() -> "EvidenceService":
    """
    获取应用级共享的 EvidenceService 实例
    
    Returns:
        EvidenceService: 共享的证据服务实例
    """
    global _shared_evidence_service
    
    if _shared_evidence_service is not None:
        return _shared_evidence_service
    
    from src.modules.evidence.service import EvidenceService
    
    bridge = get_asset_bridge()
    _shared_evidence_service = EvidenceService(asset_bridge=bridge)
    return _shared_evidence_service


def reset_evidence_service() -> None:
    """重置共享的 EvidenceService 实例（主要用于测试）"""
    global _shared_evidence_service
    _shared_evidence_service = None
