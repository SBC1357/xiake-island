"""
侠客岛 Asset Bridge 样例配置

展示如何配置藏经阁发布物消费路径。

重要：所有路径应通过环境变量或配置文件注入，不硬编码路径。
"""
from pathlib import Path
from src.adapters.asset_bridge import AssetBridgeConfig, FilesystemAssetBridge, AssetKind


# ==================== 配置方式 1: 环境变量（推荐） ====================

def create_bridge_from_env() -> FilesystemAssetBridge:
    """
    从环境变量读取配置（推荐方式）
    
    环境变量:
        XIAGEDAO_CONSUMER_ROOT: 藏经阁发布物消费目录
        XIAGEDAO_RULES_ROOT: 规则目录
        XIAGEDAO_EDITORIAL_ROOT: 编辑规范目录
        XIAGEDAO_EVIDENCE_ROOT: 证据目录
        XIAGEDAO_STRUCTURED_ROOT: 结构化目录
    """
    import os
    
    # 环境变量返回 str | None，需要转换为 Path | None
    def to_path(v: str | None) -> Path | None:
        return Path(v) if v else None
    
    config = AssetBridgeConfig(
        consumer_root=to_path(os.environ.get("XIAGEDAO_CONSUMER_ROOT")),
        rules_root=to_path(os.environ.get("XIAGEDAO_RULES_ROOT")),
        editorial_root=to_path(os.environ.get("XIAGEDAO_EDITORIAL_ROOT")),
        evidence_root=to_path(os.environ.get("XIAGEDAO_EVIDENCE_ROOT")),
        structured_root=to_path(os.environ.get("XIAGEDAO_STRUCTURED_ROOT")),
    )
    
    return FilesystemAssetBridge(config)


# ==================== 配置方式 2: 配置文件 ====================

def create_bridge_from_config_file(config_path: str = "config/asset_bridge.yaml") -> FilesystemAssetBridge:
    """
    从 YAML 配置文件读取配置
    
    配置文件示例（路径通过配置注入，不硬编码）:
    ```yaml
    asset_bridge:
      consumer_root: "${CANGJINGGE_ROOT}/publish/current/consumers/xiakedao"
      # 或使用绝对路径（由运维人员配置）
    ```
    """
    import yaml
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    bridge_config = data.get('asset_bridge', {})
    
    # 配置文件返回 str | None，需要转换为 Path | None
    def to_path(v: str | None) -> Path | None:
        return Path(v) if v else None
    
    config = AssetBridgeConfig(
        consumer_root=to_path(bridge_config.get('consumer_root')),
        rules_root=to_path(bridge_config.get('rules_root')),
        editorial_root=to_path(bridge_config.get('editorial_root')),
        evidence_root=to_path(bridge_config.get('evidence_root')),
        structured_root=to_path(bridge_config.get('structured_root')),
    )
    
    return FilesystemAssetBridge(config)


# ==================== 配置方式 3: 显式参数（用于测试） ====================

def create_bridge_with_config(consumer_root: Path | None = None, **kwargs) -> FilesystemAssetBridge:
    """
    使用显式参数创建桥接实例（主要用于测试）
    
    Args:
        consumer_root: 藏经阁发布物消费目录
        **kwargs: 其他根目录配置
    """
    config = AssetBridgeConfig(
        consumer_root=consumer_root,
        rules_root=kwargs.get('rules_root'),
        editorial_root=kwargs.get('editorial_root'),
        evidence_root=kwargs.get('evidence_root'),
        structured_root=kwargs.get('structured_root'),
    )
    
    return FilesystemAssetBridge(config)


# ==================== 使用示例 ====================

def example_usage():
    """
    使用示例
    
    注意：实际使用时应通过环境变量或配置文件注入路径，
    不应在代码中硬编码路径。
    """
    bridge = create_bridge_from_env()
    
    # 列出消费目录中的所有资产
    try:
        assets = bridge.list_assets(AssetKind.CONSUMER)
        print(f"Found {len(assets)} assets in consumer directory")
        
        # 读取特定资产
        if assets:
            record = bridge.read_text(AssetKind.CONSUMER, assets[0])
            print(f"Read: {record.relative_path}")
            print(f"Content length: {len(record.content)} chars")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_usage()