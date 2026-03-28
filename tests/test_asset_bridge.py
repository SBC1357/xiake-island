"""
Asset Bridge 测试

使用 tmp_path 创建临时目录和样例文件，不依赖真实 V2 路径。
"""
import pytest
from pathlib import Path

from src.adapters.asset_bridge import (
    AssetKind,
    AssetBridgeConfig,
    FilesystemAssetBridge,
    AssetKindNotConfiguredError,
    AssetRootNotFoundError,
    AssetNotFoundError,
    PathTraversalError,
    AssetReadError,
)


class TestAssetKind:
    """测试 AssetKind 枚举"""
    
    def test_asset_kind_values(self):
        """测试资产类别枚举值"""
        assert AssetKind.RULES.value == "rules"
        assert AssetKind.EDITORIAL.value == "editorial"
        assert AssetKind.EVIDENCE.value == "evidence"
        assert AssetKind.STRUCTURED.value == "structured"


class TestAssetBridgeConfig:
    """测试 AssetBridgeConfig"""
    
    def test_config_with_string_paths(self):
        """测试使用字符串路径初始化配置"""
        config = AssetBridgeConfig(
            rules_root="/tmp/rules",
            editorial_root="/tmp/editorial",
        )
        assert config.rules_root == Path("/tmp/rules")
        assert config.editorial_root == Path("/tmp/editorial")
        assert config.evidence_root is None
        assert config.structured_root is None
    
    def test_config_with_path_objects(self):
        """测试使用 Path 对象初始化配置"""
        config = AssetBridgeConfig(
            rules_root=Path("/tmp/rules"),
        )
        assert config.rules_root == Path("/tmp/rules")
    
    def test_get_root_for_configured_kind(self):
        """测试获取已配置类别的根目录"""
        config = AssetBridgeConfig(
            rules_root="/tmp/rules",
        )
        assert config.get_root(AssetKind.RULES) == Path("/tmp/rules")
    
    def test_get_root_for_unconfigured_kind(self):
        """测试获取未配置类别的根目录"""
        config = AssetBridgeConfig()
        assert config.get_root(AssetKind.RULES) is None
    
    def test_typoed_field_raises_error(self):
        """测试拼写错误的字段抛出异常
        
        配置对象应禁止额外字段，避免拼写错误被静默忽略。
        例如 evidence_rooot (多了一个 o) 应该立即报错。
        """
        from pydantic import ValidationError
        
        # 正确拼写
        config_ok = AssetBridgeConfig(rules_root="/tmp/rules")
        assert config_ok.rules_root == Path("/tmp/rules")
        
        # 拼写错误应该抛出 ValidationError
        with pytest.raises(ValidationError) as exc_info:
            AssetBridgeConfig(rules_root="/tmp/rules", evidence_rooot="/tmp/evidence")  # typo: evidence_rooot
        
        # 验证错误信息包含未识别的字段
        error_str = str(exc_info.value)
        assert "evidence_rooot" in error_str or "Extra inputs are not permitted" in error_str


class TestFilesystemAssetBridge:
    """测试 FilesystemAssetBridge"""
    
    @pytest.fixture
    def bridge_with_sample_data(self, tmp_path):
        """创建包含样例数据的桥接实例"""
        # 创建测试目录结构
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        
        # 创建测试文件
        (rules_dir / "rule1.md").write_text("# Rule 1\n这是规则1的内容", encoding='utf-8')
        (rules_dir / "rule2.md").write_text("# Rule 2\n这是规则2的内容", encoding='utf-8')
        
        # 创建子目录
        sub_dir = rules_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "rule3.md").write_text("# Rule 3\n这是规则3的内容", encoding='utf-8')
        
        editorial_dir = tmp_path / "editorial"
        editorial_dir.mkdir()
        (editorial_dir / "guide.txt").write_text("编辑指南内容", encoding='utf-8')
        
        # 创建配置
        config = AssetBridgeConfig(
            rules_root=rules_dir,
            editorial_root=editorial_dir,
        )
        
        return FilesystemAssetBridge(config)
    
    def test_list_assets_success(self, bridge_with_sample_data):
        """测试 1: 可列出某类资产"""
        assets = bridge_with_sample_data.list_assets(AssetKind.RULES)
        
        assert len(assets) == 3
        assert "rule1.md" in assets
        assert "rule2.md" in assets
        assert "subdir/rule3.md" in assets
        
        # 验证排序
        assert assets == sorted(assets)
    
    def test_read_text_success(self, bridge_with_sample_data):
        """测试 2: 可读取文本文件"""
        record = bridge_with_sample_data.read_text(AssetKind.RULES, "rule1.md")
        
        assert record.kind == AssetKind.RULES
        assert record.relative_path == "rule1.md"
        assert "Rule 1" in record.content
        assert "这是规则1的内容" in record.content
        assert Path(record.absolute_path).exists()
    
    def test_read_text_with_subdirectory(self, bridge_with_sample_data):
        """测试读取子目录中的文件"""
        record = bridge_with_sample_data.read_text(AssetKind.RULES, "subdir/rule3.md")
        
        assert record.kind == AssetKind.RULES
        assert record.relative_path == "subdir/rule3.md"
        assert "Rule 3" in record.content
    
    def test_exists_returns_true_for_existing_file(self, bridge_with_sample_data):
        """测试 3: exists 返回正确结果 - 文件存在"""
        assert bridge_with_sample_data.exists(AssetKind.RULES, "rule1.md") is True
        assert bridge_with_sample_data.exists(AssetKind.RULES, "subdir/rule3.md") is True
    
    def test_exists_returns_false_for_nonexistent_file(self, bridge_with_sample_data):
        """测试 3: exists 返回正确结果 - 文件不存在"""
        assert bridge_with_sample_data.exists(AssetKind.RULES, "nonexistent.md") is False
    
    def test_unconfigured_kind_raises_error(self, bridge_with_sample_data):
        """测试 4: 未配置类别时抛出预期异常"""
        with pytest.raises(AssetKindNotConfiguredError) as exc_info:
            bridge_with_sample_data.list_assets(AssetKind.EVIDENCE)
        
        assert "evidence" in str(exc_info.value)
        assert exc_info.value.kind == AssetKind.EVIDENCE
    
    def test_nonexistent_file_raises_error(self, bridge_with_sample_data):
        """测试 4: 文件不存在时抛出预期异常"""
        with pytest.raises(AssetNotFoundError) as exc_info:
            bridge_with_sample_data.read_text(AssetKind.RULES, "nonexistent.md")
        
        assert "nonexistent.md" in str(exc_info.value)
        assert exc_info.value.kind == AssetKind.RULES
    
    def test_path_traversal_with_double_dot(self, bridge_with_sample_data, tmp_path):
        """测试 5: ../ 路径穿越被拒绝"""
        # 创建一个外部文件
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("外部文件", encoding='utf-8')
        
        # 尝试通过 ../ 访问
        with pytest.raises(PathTraversalError) as exc_info:
            bridge_with_sample_data.read_text(AssetKind.RULES, "../outside.txt")
        
        assert "路径穿越" in str(exc_info.value)
    
    def test_path_traversal_with_absolute_path(self, bridge_with_sample_data, tmp_path):
        """测试 5: 绝对路径逃逸被拒绝"""
        # 创建外部文件
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("外部文件", encoding='utf-8')
        
        # 尝试使用绝对路径
        with pytest.raises(PathTraversalError) as exc_info:
            bridge_with_sample_data.read_text(AssetKind.RULES, str(outside_file))
        
        assert "绝对路径" in str(exc_info.value) or "路径穿越" in str(exc_info.value)
    
    def test_exists_returns_false_for_path_traversal(self, bridge_with_sample_data):
        """测试 exists 对路径穿越返回 False 而不抛异常"""
        assert bridge_with_sample_data.exists(AssetKind.RULES, "../outside.txt") is False
    
    def test_list_assets_empty_directory(self, tmp_path):
        """测试列出空目录"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        config = AssetBridgeConfig(rules_root=empty_dir)
        bridge = FilesystemAssetBridge(config)
        
        assets = bridge.list_assets(AssetKind.RULES)
        assert assets == []
    
    def test_list_assets_nonexistent_directory_raises_error(self, tmp_path):
        """测试列出不存在的目录时抛出配置错误"""
        from src.adapters.asset_bridge import AssetRootNotFoundError
        
        nonexistent_dir = tmp_path / "nonexistent"
        
        config = AssetBridgeConfig(rules_root=nonexistent_dir)
        bridge = FilesystemAssetBridge(config)
        
        # 根目录不存在时应抛出异常，而不是静默返回空列表
        with pytest.raises(AssetRootNotFoundError) as exc_info:
            bridge.list_assets(AssetKind.RULES)
        
        assert "根目录不存在" in str(exc_info.value)
        assert exc_info.value.kind == AssetKind.RULES
    
    def test_read_text_directory_not_file(self, bridge_with_sample_data):
        """测试读取目录（非文件）时抛出异常"""
        with pytest.raises(AssetNotFoundError):
            bridge_with_sample_data.read_text(AssetKind.RULES, "subdir")
    
    def test_read_text_with_backslash_path(self, bridge_with_sample_data):
        """测试使用反斜杠路径也能正常工作"""
        # Windows 风格路径
        record = bridge_with_sample_data.read_text(AssetKind.RULES, "subdir\\rule3.md")
        assert record.kind == AssetKind.RULES
        # 应该统一转换为正斜杠
        assert "/" in record.relative_path


class TestAssetTextRecord:
    """测试 AssetTextRecord"""
    
    def test_record_creation(self):
        """测试创建资产记录"""
        from src.adapters.asset_bridge import AssetTextRecord
        
        record = AssetTextRecord(
            kind=AssetKind.RULES,
            relative_path="test.md",
            absolute_path="/tmp/test.md",
            content="# Test"
        )
        
        assert record.kind == AssetKind.RULES
        assert record.relative_path == "test.md"
        assert record.absolute_path == "/tmp/test.md"
        assert record.content == "# Test"


class TestPathTraversalSecurity:
    """测试路径穿越安全性"""
    
    def test_same_prefix_path_blocked(self, tmp_path):
        """测试同前缀路径绕过防护
        
        验证 D:\\tmp\\ruleset 不能绕过 D:\\tmp\\rules 的限制
        使用 relative_to 而非 startswith 判断路径包含
        """
        # 创建 rules 目录
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "rule1.md").write_text("规则内容", encoding='utf-8')
        
        # 创建 ruleset 目录（同前缀）
        ruleset_dir = tmp_path / "ruleset"
        ruleset_dir.mkdir()
        (ruleset_dir / "other.md").write_text("其他内容", encoding='utf-8')
        
        # 配置 rules 为根目录
        config = AssetBridgeConfig(rules_root=rules_dir)
        bridge = FilesystemAssetBridge(config)
        
        # 尝试通过同前缀路径访问 ruleset 目录中的文件
        # 这应该被阻止，而不是因为字符串前缀匹配而放行
        with pytest.raises(PathTraversalError):
            bridge.read_text(AssetKind.RULES, "../ruleset/other.md")
    
    def test_symlink_escape_blocked(self, tmp_path):
        """测试符号链接逃逸被阻止
        
        如果根目录内存在指向外部的符号链接，应该被阻止
        """
        # 创建内部目录和外部目录
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        (outside_dir / "secret.md").write_text("秘密内容", encoding='utf-8')
        
        # 在 rules 内创建指向外部的符号链接
        try:
            (rules_dir / "escape").symlink_to(outside_dir)
            
            config = AssetBridgeConfig(rules_root=rules_dir)
            bridge = FilesystemAssetBridge(config)
            
            # 尝试通过符号链接访问外部文件
            # resolve() 会解析符号链接的真实路径
            # relative_to 检查会发现真实路径不在根目录内
            with pytest.raises(PathTraversalError):
                bridge.read_text(AssetKind.RULES, "escape/secret.md")
        except OSError:
            # Windows 可能需要管理员权限创建符号链接，跳过此测试
            pytest.skip("无法创建符号链接（可能需要管理员权限）")
    
    def test_missing_root_raises_config_error(self, tmp_path):
        """测试缺失的根目录抛出配置错误而非静默返回空"""
        from src.adapters.asset_bridge import AssetRootNotFoundError
        
        missing_dir = tmp_path / "this_does_not_exist"
        
        config = AssetBridgeConfig(rules_root=missing_dir)
        bridge = FilesystemAssetBridge(config)
        
        # 应该抛出配置错误，而不是返回空列表
        with pytest.raises(AssetRootNotFoundError) as exc_info:
            bridge.list_assets(AssetKind.RULES)
        
        assert "根目录不存在" in str(exc_info.value)
        
        # read_text 也应该失败
        with pytest.raises(AssetRootNotFoundError):
            bridge.read_text(AssetKind.RULES, "any_file.md")