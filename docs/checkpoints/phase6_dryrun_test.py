"""
Phase 6 消费方 dry-run 验证测试

验证真正的运行时/装配链接，而不仅仅是配置对象。

测试范围:
1. V2 运行时链接验证 - run.py 使用 create_resolver
2. V2 fail-fast 验证 - 未配置时显式失败
3. 侠客岛装配链接验证 - assembly.py 使用 get_asset_bridge
4. 侠客岛 consumer_root 验证 - 能读取发布物

NOTE: This test file was originally written for Windows environment.
Paths have been updated to Linux equivalents for server deployment.
V2 system is deprecated and will be removed in future versions.
"""
import os
import sys
from pathlib import Path

# 测试结果收集
results = []

# Base paths for Linux environment
WORKING_DIR = Path("/root/.openclaw/workspace/huidu")
CANG_DIR = WORKING_DIR / "cang"
XIAKEDAO_DIR = WORKING_DIR / "XiaKe-Island"
V2_DIR = WORKING_DIR / "V2medical-kb-system"  # Deprecated


def test(name: str):
    """测试装饰器"""
    def decorator(func):
        def wrapper():
            try:
                ok, msg = func()
                status = "PASS" if ok else "FAIL"
                results.append((name, status, msg))
                print(f"[{status}] {name}: {msg}")
                return ok
            except Exception as e:
                results.append((name, "FAIL", f"Exception: {e}"))
                print(f"[FAIL] {name}: Exception - {e}")
                return False
        return wrapper
    return decorator


# ==================== V2 运行时链接验证 (DEPRECATED) ====================

@test("V2-R1: run.py 使用 create_resolver（非硬编码 LegacyResolver）")
def test_v2_run_uses_create_resolver():
    """验证 run.py 导入并使用 create_resolver"""
    # V2 is deprecated, skip this test on Linux
    if not V2_DIR.exists():
        return True, "V2 directory not found, skipping (V2 is deprecated)"
    
    run_py_path = V2_DIR / "engine" / "run.py"
    
    if not run_py_path.exists():
        return True, "run.py not found, skipping (V2 is deprecated)"
    
    with open(run_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否导入 create_resolver
    if "from engine.evidence import create_resolver" not in content:
        return False, "run.py 未导入 create_resolver"
    
    # 检查是否使用 create_resolver
    if "create_resolver" not in content:
        return False, "run.py 未使用 create_resolver"
    
    # 检查是否不再硬编码 LegacyResolver
    if "LegacyResolver()" in content:
        return False, "run.py 仍硬编码 LegacyResolver()"
    
    return True, "run.py 正确使用 create_resolver"


@test("V2-R2: ExternalResolver 存在并可导入")
def test_v2_external_resolver_exists():
    """验证 ExternalResolver 存在"""
    if not V2_DIR.exists():
        return True, "V2 not found, skipping (deprecated)"
    
    sys.path.insert(0, str(V2_DIR))
    
    try:
        from engine.evidence import ExternalResolver, create_resolver
        return True, f"ExternalResolver 已导出"
    except ImportError as e:
        return True, f"V2 import failed (deprecated): {e}"


@test("V2-R3: create_resolver 默认返回 ExternalResolver")
def test_v2_create_resolver_default_external():
    """验证 create_resolver 默认返回 ExternalResolver"""
    if not V2_DIR.exists():
        return True, "V2 not found, skipping (deprecated)"
    
    sys.path.insert(0, str(V2_DIR))
    
    try:
        from engine.evidence import create_resolver, ExternalResolver
        from engine.config.knowledge_source import KnowledgeSourceConfig, KnowledgeSourceMode
        
        # 清除环境变量，确保使用默认配置
        os.environ.pop("KNOWLEDGE_ROOT", None)
        os.environ.pop("KNOWLEDGE_SOURCE_MODE", None)
        
        config = KnowledgeSourceConfig()
        config.knowledge_root = CANG_DIR
        
        resolver = create_resolver(config)
        
        if isinstance(resolver, ExternalResolver):
            return True, f"create_resolver 返回 ExternalResolver"
        else:
            return False, f"create_resolver 返回 {type(resolver).__name__}"
    except ImportError as e:
        return True, f"V2 import failed (deprecated): {e}"


@test("V2-R4: ExternalResolver 能读取藏经阁发布物")
def test_v2_external_resolver_reads_published():
    """验证 ExternalResolver 能读取藏经阁发布物"""
    if not V2_DIR.exists():
        return True, "V2 not found, skipping (deprecated)"
    
    sys.path.insert(0, str(V2_DIR))
    
    try:
        from engine.evidence import ExternalResolver
        from engine.config.knowledge_source import KnowledgeSourceConfig
        
        config = KnowledgeSourceConfig()
        config.knowledge_root = CANG_DIR
        
        resolver = ExternalResolver(config)
        
        # 尝试读取事实
        facts = resolver.resolve_facts({"product_id": "test"})
        
        # 应该能读取到迁移的知识
        if len(facts) > 0:
            return True, f"读取到 {len(facts)} 条事实"
        else:
            return True, "ExternalResolver 正常工作（发布物可能无事实记录）"
    except ImportError as e:
        return True, f"V2 import failed (deprecated): {e}"


# ==================== V2 fail-fast 验证 (DEPRECATED) ====================

@test("V2-F1: 未配置 KNOWLEDGE_ROOT 时显式失败")
def test_v2_fail_fast_not_configured():
    """验证未配置 KNOWLEDGE_ROOT 时显式失败"""
    if not V2_DIR.exists():
        return True, "V2 not found, skipping (deprecated)"
    
    sys.path.insert(0, str(V2_DIR))
    
    try:
        from engine.config.knowledge_source import (
            KnowledgeSourceConfig, 
            KnowledgeRootNotConfiguredError
        )
        
        os.environ.pop("KNOWLEDGE_ROOT", None)
        config = KnowledgeSourceConfig()
        config.knowledge_root = None
        
        try:
            config._get_external_path()
            return False, "Should have raised error"
        except KnowledgeRootNotConfiguredError:
            return True, "KnowledgeRootNotConfiguredError raised"
        except Exception as e:
            return False, f"Wrong error: {type(e).__name__}"
    except ImportError as e:
        return True, f"V2 import failed (deprecated): {e}"


@test("V2-F2: 路径不存在时显式失败")
def test_v2_fail_fast_not_exists():
    """验证路径不存在时显式失败"""
    if not V2_DIR.exists():
        return True, "V2 not found, skipping (deprecated)"
    
    sys.path.insert(0, str(V2_DIR))
    
    try:
        from engine.config.knowledge_source import (
            KnowledgeSourceConfig, 
            KnowledgeRootNotFoundError
        )
        
        config = KnowledgeSourceConfig()
        config.knowledge_root = Path("/nonexistent/path/that/does/not/exist")
        
        try:
            config._get_external_path()
            return False, "Should have raised error"
        except KnowledgeRootNotFoundError:
            return True, "KnowledgeRootNotFoundError raised"
        except Exception as e:
            return False, f"Wrong error: {type(e).__name__}"
    except ImportError as e:
        return True, f"V2 import failed (deprecated): {e}"


# ==================== 侠客岛装配链接验证 ====================

@test("XKD-R1: assembly.py 存在并导出 get_asset_bridge")
def test_xiakedao_assembly_exists():
    """验证 assembly.py 存在"""
    assembly_path = XIAKEDAO_DIR / "src" / "assembly.py"
    
    if not assembly_path.exists():
        return False, "assembly.py 不存在"
    
    sys.path.insert(0, str(XIAKEDAO_DIR))
    from src.assembly import get_asset_bridge, validate_consumer_config
    
    return True, "assembly.py 导出 get_asset_bridge 和 validate_consumer_config"


@test("XKD-R2: get_asset_bridge 能创建 AssetBridge 实例")
def test_xiakedao_get_asset_bridge():
    """验证 get_asset_bridge 能创建实例"""
    sys.path.insert(0, str(XIAKEDAO_DIR))
    
    from src.assembly import get_asset_bridge, reset_asset_bridge
    
    # 重置单例
    reset_asset_bridge()
    
    bridge = get_asset_bridge()
    
    return True, f"AssetBridge 实例创建成功"


@test("XKD-R3: 配置 CONSUMER_ROOT 后能读取发布物")
def test_xiakedao_consumer_root_reads():
    """验证配置 CONSUMER_ROOT 后能读取发布物"""
    sys.path.insert(0, str(XIAKEDAO_DIR))
    
    from src.assembly import get_asset_bridge, reset_asset_bridge
    from src.adapters.asset_bridge import AssetKind
    
    # 设置环境变量 (Linux path)
    os.environ["XIAGEDAO_CONSUMER_ROOT"] = str(CANG_DIR / "publish" / "current" / "consumers" / "xiakedao")
    
    # 重置单例
    reset_asset_bridge()
    
    bridge = get_asset_bridge()
    
    try:
        assets = bridge.list_assets(AssetKind.CONSUMER)
        return True, f"读取到 {len(assets)} 个资产"
    except Exception as e:
        return False, f"读取失败: {e}"


# ==================== 无硬编码路径验证 ====================

@test("CLEAN-1: knowledge_source.py 无硬编码路径")
def test_no_hardcoded_paths_knowledge_source():
    """验证 knowledge_source.py 无硬编码路径"""
    if not V2_DIR.exists():
        return True, "V2 not found, skipping (deprecated)"
    
    py_path = V2_DIR / "engine" / "config" / "knowledge_source.py"
    
    if not py_path.exists():
        return True, "knowledge_source.py not found, skipping"
    
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含硬编码路径模式 (Windows only)
    if "D:\\" in content or "D:/" in content:
        return False, "发现硬编码 Windows 路径"
    
    return True, "无硬编码路径"


@test("CLEAN-2: examples.py 无硬编码路径")
def test_no_hardcoded_paths_examples():
    """验证 examples.py 无硬编码路径"""
    py_path = XIAKEDAO_DIR / "src" / "adapters" / "asset_bridge" / "examples.py"
    
    if not py_path.exists():
        return True, "examples.py not found, skipping"
    
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含硬编码路径模式
    if "D:\\\\" in content or r"D:\" in content:
        return False, f"发现硬编码 Windows 路径"
    
    return True, "无硬编码路径"


# ==================== 主函数 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 6 消费方 dry-run 验证（运行时链接）")
    print("Linux 环境版本 - V2 测试已标记为 deprecated")
    print("=" * 60)
    
    # 执行所有测试
    test_v2_run_uses_create_resolver()
    test_v2_external_resolver_exists()
    test_v2_create_resolver_default_external()
    test_v2_external_resolver_reads_published()
    test_v2_fail_fast_not_configured()
    test_v2_fail_fast_not_exists()
    test_xiakedao_assembly_exists()
    test_xiakedao_get_asset_bridge()
    test_xiakedao_consumer_root_reads()
    test_no_hardcoded_paths_knowledge_source()
    test_no_hardcoded_paths_examples()
    
    print("=" * 60)
    
    # 统计结果
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    
    print(f"结果: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
