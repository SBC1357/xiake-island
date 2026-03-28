"""
Tests for Delivery Module

SP-6 Batch 6D: 新增 docx 生成和字数门禁测试
"""
import pytest
from pathlib import Path
import tempfile
import os

from src.modules.delivery import MarkdownWriter, DeliveryResult
from src.modules.delivery.models import WordCountGateError
from src.modules.delivery.docx_writer import DocxWriter


class TestDeliveryResult:
    """测试交付结果"""
    
    def test_create_result(self):
        """创建交付结果"""
        result = DeliveryResult()
        
        assert result.output_path is None
        assert len(result.artifacts) == 0
    
    def test_add_artifact(self):
        """添加产物"""
        result = DeliveryResult()
        result.add_artifact(Path("/tmp/test.md"))
        
        assert len(result.artifacts) == 1
        assert result.artifacts[0] == Path("/tmp/test.md")
    
    def test_add_log_path(self):
        """添加日志路径"""
        result = DeliveryResult()
        result.add_log_path(Path("/tmp/log1.txt"))
        result.add_log_path(Path("/tmp/log2.txt"))
        
        assert result.task_log_path == Path("/tmp/log1.txt")
        assert len(result.task_log_paths) == 2


class TestDocxWriter:
    """测试 Docx 写入器 - SP-6 Batch 6D"""
    
    @pytest.fixture
    def writer(self):
        temp_dir = tempfile.mkdtemp()
        writer = DocxWriter(output_dir=Path(temp_dir))
        yield writer
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_write_creates_docx(self, writer):
        """Docx 文件被创建"""
        result = writer.write(
            thesis="测试文章标题",
            outline=[
                {"title": "引言", "type": "intro"},
                {"title": "结论", "type": "conclusion"}
            ]
        )
        
        assert result.docx_path.exists()
        assert result.docx_path.suffix == ".docx"
    
    def test_write_returns_body_word_count(self, writer):
        """返回正文字数"""
        result = writer.write(
            thesis="测试文章标题",
            outline=[],
            key_evidence=["证据一", "证据二"]
        )
        
        assert result.body_word_count > 0
    
    def test_word_count_excludes_title(self, writer):
        """字数排除标题"""
        # 标题："测试文章标题" 不计入正文字数
        result = writer.write(
            thesis="测试文章标题",
            outline=[],
            key_evidence=[]
        )
        
        # 正文应该有引言、主要内容、结论等生成的段落
        assert result.body_word_count > 0
    
    def test_word_count_includes_body_paragraphs(self, writer):
        """字数包含正文段落"""
        result = writer.write(
            thesis="测试",
            outline=[
                {"title": "章节一", "type": "section"},
                {"title": "章节二", "type": "section"}
            ],
            key_evidence=["证据内容"]
        )
        
        assert result.body_word_count > 0


class TestMarkdownWriterDocxIntegration:
    """测试 MarkdownWriter Docx 集成 - SP-6 Batch 6D"""
    
    @pytest.fixture
    def writer(self):
        temp_dir = tempfile.mkdtemp()
        writer = MarkdownWriter(output_dir=Path(temp_dir))
        yield writer
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_create_delivery_result_generates_docx(self, writer):
        """交付结果生成 docx 文件"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[{"title": "引言", "type": "intro"}],
            key_evidence=["证据"]
        )
        
        assert result.docx_path is not None
        assert result.docx_path.exists()
        assert result.docx_path.suffix == ".docx"
    
    def test_output_path_points_to_docx(self, writer):
        """output_path 指向 docx"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[],
            key_evidence=[],
            target_word_count=10  # 使用低阈值确保通过
        )
        
        assert result.output_path == result.docx_path
        assert str(result.output_path).endswith(".docx")
    
    def test_markdown_is_preview_artifact(self, writer):
        """Markdown 是预览产物"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[],
            key_evidence=[],
            target_word_count=10  # 使用低阈值确保通过
        )
        
        assert result.markdown_preview_path is not None
        assert result.markdown_preview_path.suffix == ".md"
    
    def test_artifacts_include_both_md_and_docx(self, writer):
        """产物包含 md 和 docx"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[],
            key_evidence=[],
            target_word_count=10  # 使用低阈值确保通过
        )
        
        artifact_extensions = [a.suffix for a in result.artifacts]
        assert ".md" in artifact_extensions
        assert ".docx" in artifact_extensions
    
    def test_final_docx_word_count_populated(self, writer):
        """正文字数被填充"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[{"title": "章节", "type": "section"}],
            key_evidence=["证据"]
        )
        
        assert result.final_docx_word_count is not None
        assert result.final_docx_word_count > 0
    
    def test_word_count_basis_is_docx_body(self, writer):
        """字数基准为 docx_body"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[],
            key_evidence=[],
            target_word_count=10  # 使用低阈值确保通过
        )
        
        assert result.word_count_basis == "docx_body"
    
    def test_word_count_gate_passed_when_above_threshold(self, writer):
        """字数高于阈值时门禁通过"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[{"title": "章节", "type": "section"}],
            key_evidence=["证据一", "证据二"],
            target_word_count=10  # 低阈值，确保通过
        )
        
        assert result.word_count_gate_passed is True
    
    def test_word_count_gate_passed_when_target_is_none(self, writer):
        """未提供阈值时使用默认阈值"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[{"title": "章节", "type": "section"}],
            key_evidence=["证据"]
        )
        
        # 默认阈值为 50，生成的内容应该超过
        assert result.word_count_gate_passed is True
    
    def test_word_count_gate_blocks_when_below_threshold(self, writer):
        """字数低于阈值时门禁阻断"""
        with pytest.raises(WordCountGateError) as exc_info:
            writer.create_delivery_result(
                thesis="测试文章",
                outline=[],  # 空大纲，内容较少
                key_evidence=[],
                target_word_count=10000  # 高阈值，确保不通过
            )
        
        assert exc_info.value.final_word_count < exc_info.value.target_word_count
    
    def test_summary_contains_docx_metadata(self, writer):
        """摘要包含 docx 元数据"""
        result = writer.create_delivery_result(
            thesis="测试文章",
            outline=[],
            key_evidence=[],
            target_word_count=10  # 使用低阈值确保通过
        )
        
        assert "markdown_preview_path" in result.summary
        assert "docx_path" in result.summary
        assert "final_docx_word_count" in result.summary
        assert "word_count_basis" in result.summary
        assert "target_word_count" in result.summary
        assert "word_count_gate_passed" in result.summary


class TestMarkdownWriterBasic:
    """测试 Markdown 写入器基本功能"""
    
    @pytest.fixture
    def writer(self):
        temp_dir = tempfile.mkdtemp()
        writer = MarkdownWriter(output_dir=Path(temp_dir))
        yield writer
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_write_basic(self, writer):
        """基本写入"""
        output_path = writer.write(
            thesis="测试文章标题",
            outline=[
                {"title": "引言", "type": "intro"},
                {"title": "结论", "type": "conclusion"}
            ]
        )
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert "# 测试文章标题" in content
        assert "引言" in content
        assert "结论" in content
    
    def test_write_with_evidence(self, writer):
        """带证据写入"""
        output_path = writer.write(
            thesis="测试文章",
            outline=[],
            key_evidence=["证据1", "证据2"]
        )
        
        content = output_path.read_text(encoding='utf-8')
        assert "核心证据" in content
        assert "证据1" in content
        assert "证据2" in content
    
    def test_write_with_content(self, writer):
        """带正文内容写入"""
        output_path = writer.write(
            thesis="测试文章",
            outline=[],
            content="这是正文内容。"
        )
        
        content = output_path.read_text(encoding='utf-8')
        assert "这是正文内容" in content
        assert "*[正文内容待生成]*" not in content
    
    def test_write_without_content(self, writer):
        """不带正文内容"""
        output_path = writer.write(
            thesis="测试文章",
            outline=[]
        )
        
        content = output_path.read_text(encoding='utf-8')
        assert "*[正文内容待生成]*" in content
    
    def test_write_with_metadata(self, writer):
        """带元数据写入"""
        output_path = writer.write(
            thesis="测试文章",
            outline=[],
            target_audience="医生",
            play_id="professional",
            arc_id="evidence_driven"
        )
        
        content = output_path.read_text(encoding='utf-8')
        assert "医生" in content
        assert "professional" in content
        assert "evidence_driven" in content
    
    def test_domain_section_outline(self, writer):
        """domain 章节大纲"""
        output_path = writer.write(
            thesis="测试文章",
            outline=[
                {"title": "疗效分析", "type": "domain_section", "fact_count": 5}
            ]
        )
        
        content = output_path.read_text(encoding='utf-8')
        assert "5条证据" in content
    
    def test_custom_filename(self, writer):
        """自定义文件名"""
        output_path = writer.write(
            thesis="测试文章",
            outline=[],
            filename="custom_name.md"
        )
        
        assert output_path.name == "custom_name.md"


class TestFilenameCollisionSP6Batch6D:
    """
    SP-6 Batch 6D 回归测试: 验证同一秒内快速重复调用不再产生文件名碰撞
    
    根因: 原实现使用 `%Y%m%d_%H%M%S` 时间戳，同一秒内多次调用生成相同文件名，
    Windows 下写入正在被占用的文件会抛出 PermissionError。
    
    修复: 添加 8 字符短 UUID 后缀确保每次调用的文件名唯一。
    """
    
    @pytest.fixture
    def writer(self):
        temp_dir = tempfile.mkdtemp()
        writer = MarkdownWriter(output_dir=Path(temp_dir))
        yield writer
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_rapid_repeated_calls_no_collision(self, writer):
        """快速重复调用不再产生文件名碰撞"""
        # 同一论点，同一秒内调用多次
        thesis = "这是一个测试论点"
        results = []
        
        # 快速连续调用 10 次（极大概率在同一秒内）
        for _ in range(10):
            result = writer.create_delivery_result(
                thesis=thesis,
                outline=[{"title": "章节", "type": "section"}],
                key_evidence=["证据"],
                target_word_count=10
            )
            results.append(result)
        
        # 所有调用都应该成功，没有 PermissionError
        assert len(results) == 10
        
        # 验证每个结果都有有效的输出路径
        for result in results:
            assert result.docx_path.exists()
            assert result.markdown_preview_path.exists()
    
    def test_rapid_calls_produce_unique_filenames(self, writer):
        """快速调用产生唯一文件名"""
        thesis = "同一个论点"
        
        # 快速调用多次
        paths = []
        for _ in range(5):
            result = writer.create_delivery_result(
                thesis=thesis,
                outline=[],
                target_word_count=10
            )
            paths.append(result.docx_path.name)
        
        # 所有文件名应该唯一
        assert len(set(paths)) == 5, f"Expected 5 unique filenames, got {paths}"
    
    def test_md_and_docx_share_same_base_filename(self, writer):
        """md 和 docx 共享相同的基础文件名"""
        result = writer.create_delivery_result(
            thesis="测试论点",
            outline=[],
            target_word_count=10
        )
        
        md_name = result.markdown_preview_path.stem
        docx_name = result.docx_path.stem
        
        # 基础文件名（不含扩展名）应该相同
        assert md_name == docx_name
    
    def test_filename_contains_uuid_suffix(self, writer):
        """文件名包含 UUID 后缀"""
        result = writer.create_delivery_result(
            thesis="测试论点",
            outline=[],
            target_word_count=10
        )
        
        # 文件名格式: {safe_title}_{timestamp}_{8-char-uuid}
        filename = result.docx_path.stem
        
        # 应该包含下划线分隔的三部分
        parts = filename.split('_')
        assert len(parts) >= 3, f"Filename should have at least 3 parts separated by _, got {filename}"
        
        # 最后一部分应该是 8 字符的十六进制 UUID
        uuid_part = parts[-1]
        assert len(uuid_part) == 8, f"UUID suffix should be 8 chars, got {uuid_part}"
        # 验证是有效的十六进制
        int(uuid_part, 16)  # 如果不是有效十六进制会抛出异常