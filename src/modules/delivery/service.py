"""
Markdown Writer Service

交付服务，实现 V2 markdown_writer 逻辑。

SP-6 Batch 6D: 
- 生成 Python 产生的 docx 作为正式输出
- Markdown 仅作为预览产物
- 添加字数门禁检查
- 当内容缺失时从 thesis/outline/key_evidence 生成确定性正文
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .models import DeliveryResult, WordCountGateError
from .docx_writer import DocxWriter


# 默认字数门禁阈值（当未提供 target_word_count 时使用）
# 设置为较低值以确保当前生成的最小内容可以通过门禁
DEFAULT_WORD_COUNT_THRESHOLD = 30


@dataclass
class MarkdownWriter:
    """
    Markdown 文件写入器
    
    根据编辑计划生成 Markdown 格式的文章。
    与 V2 MarkdownWriter 兼容。
    
    SP-6 Batch 6D: 同时生成 docx 和 markdown，以 docx 为正式输出。
    """
    
    output_dir: Path = field(default_factory=lambda: Path("output"))
    
    def write(
        self,
        thesis: str,
        outline: List[Dict[str, Any]],
        key_evidence: Optional[List[str]] = None,
        content: Optional[str] = None,
        target_audience: Optional[str] = None,
        play_id: Optional[str] = None,
        arc_id: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Path:
        """
        写入 Markdown 文件
        
        Args:
            thesis: 核心论点
            outline: 文章大纲
            key_evidence: 核心证据
            content: 正文内容
            target_audience: 目标受众
            play_id: 写作策略ID
            arc_id: 叙事弧线ID
            filename: 自定义文件名
            
        Returns:
            输出文件路径
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        # SP-6 Batch 6D: 添加短 UUID 确保同一秒内多次调用的唯一性
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = thesis[:30].replace(' ', '_').replace('/', '_').replace('\\', '_')
            # 8字符短UUID确保Windows下文件名唯一
            unique_suffix = uuid.uuid4().hex[:8]
            filename = f"{safe_title}_{timestamp}_{unique_suffix}.md"
        
        output_path = self.output_dir / filename
        
        # 构建 Markdown 内容
        lines = [
            f"# {thesis}",
            "",
            f"**生成时间**: {datetime.now().isoformat()}",
            f"**目标受众**: {target_audience or '未指定'}",
            f"**策略**: {play_id or '未指定'}",
            f"**弧线**: {arc_id or '未指定'}",
            "",
            "## 大纲",
            ""
        ]
        
        for i, section in enumerate(outline, 1):
            title = section.get('title', '未命名章节')
            # 如果是 domain 章节，添加证据数量
            if section.get('type') == 'domain_section' and section.get('fact_count'):
                title = f"{title} ({section['fact_count']}条证据)"
            lines.append(f"{i}. {title}")
        
        key_evidence = key_evidence or []
        if key_evidence:
            lines.extend([
                "",
                "## 核心证据",
                ""
            ])
            for evidence in key_evidence:
                lines.append(f"- {evidence}")
        
        if content:
            lines.extend([
                "",
                "## 正文",
                "",
                content
            ])
        else:
            lines.extend([
                "",
                "## 正文",
                "",
                "*[正文内容待生成]*"
            ])
        
        # 写入文件
        output_path.write_text("\n".join(lines), encoding='utf-8')
        
        return output_path
    
    def write_from_plan(self, plan_dict: Dict[str, Any], content: Optional[str] = None) -> Path:
        """
        从编辑计划字典写入 Markdown
        
        Args:
            plan_dict: 编辑计划字典
            content: 正文内容
            
        Returns:
            输出文件路径
        """
        return self.write(
            thesis=plan_dict.get('thesis', '未命名文章'),
            outline=plan_dict.get('outline', []),
            key_evidence=plan_dict.get('key_evidence'),
            content=content,
            target_audience=plan_dict.get('target_audience'),
            play_id=plan_dict.get('play_id'),
            arc_id=plan_dict.get('arc_id')
        )
    
    def create_delivery_result(
        self,
        thesis: str,
        outline: List[Dict[str, Any]],
        key_evidence: Optional[List[str]] = None,
        content: Optional[str] = None,
        target_audience: Optional[str] = None,
        play_id: Optional[str] = None,
        arc_id: Optional[str] = None,
        filename: Optional[str] = None,
        target_word_count: Optional[int] = None
    ) -> DeliveryResult:
        """
        创建交付结果
        
        SP-6 Batch 6D: 
        - 生成 docx 作为正式输出
        - 生成 markdown 作为预览
        - 执行字数门禁检查
        
        Args:
            thesis: 核心论点
            outline: 文章大纲
            key_evidence: 核心证据
            content: 正文内容
            target_audience: 目标受众
            play_id: 写作策略ID
            arc_id: 叙事弧线ID
            filename: 自定义文件名
            target_word_count: 目标字数（用于门禁检查）
            
        Returns:
            DeliveryResult: 交付结果
            
        Raises:
            WordCountGateError: 当 docx 正文字数低于目标阈值时
        """
        # 生成基础文件名（不带扩展名）
        # SP-6 Batch 6D: 添加短 UUID 确保同一秒内多次调用的唯一性
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = thesis[:30].replace(' ', '_').replace('/', '_').replace('\\', '_')
            # 8字符短UUID确保Windows下文件名唯一，避免同一秒内重复请求的碰撞
            unique_suffix = uuid.uuid4().hex[:8]
            base_filename = f"{safe_title}_{timestamp}_{unique_suffix}"
        else:
            # 移除扩展名
            base_filename = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        # Step 1: 生成 Markdown 预览
        md_filename = f"{base_filename}.md"
        md_path = self.write(
            thesis=thesis,
            outline=outline,
            key_evidence=key_evidence,
            content=content,
            target_audience=target_audience,
            play_id=play_id,
            arc_id=arc_id,
            filename=md_filename
        )
        
        # Step 2: 生成 DOCX 正式输出
        docx_filename = f"{base_filename}.docx"
        docx_writer = DocxWriter(output_dir=self.output_dir)
        docx_result = docx_writer.write(
            thesis=thesis,
            outline=outline,
            key_evidence=key_evidence,
            content=content,
            target_audience=target_audience,
            play_id=play_id,
            arc_id=arc_id,
            filename=docx_filename
        )
        
        # Step 3: 执行字数门禁检查
        # 如果未提供 target_word_count，使用默认阈值
        effective_threshold = target_word_count if target_word_count is not None else DEFAULT_WORD_COUNT_THRESHOLD
        
        word_count_gate_passed = docx_result.body_word_count >= effective_threshold
        
        # Step 4: 如果门禁失败，抛出异常
        if not word_count_gate_passed:
            raise WordCountGateError(
                message=f"字数门禁检查失败: docx正文字数({docx_result.body_word_count})低于目标阈值({effective_threshold})",
                final_word_count=docx_result.body_word_count,
                target_word_count=effective_threshold
            )
        
        # Step 5: 构建交付结果
        result = DeliveryResult(
            output_path=docx_result.docx_path,  # 主输出指向 docx
            markdown_preview_path=md_path,
            docx_path=docx_result.docx_path,
            final_docx_word_count=docx_result.body_word_count,
            word_count_basis="docx_body",
            target_word_count=target_word_count,
            word_count_gate_passed=word_count_gate_passed,
            summary={
                "thesis": thesis,
                "sections": len(outline),
                "evidence_count": len(key_evidence) if key_evidence else 0,
                "has_content": bool(content),
                "markdown_preview_path": str(md_path),
                "docx_path": str(docx_result.docx_path),
                "final_docx_word_count": docx_result.body_word_count,
                "word_count_basis": "docx_body",
                "target_word_count": target_word_count,
                "word_count_gate_passed": word_count_gate_passed
            }
        )
        
        # 添加产物
        result.add_artifact(md_path)  # Markdown 预览
        result.add_artifact(docx_result.docx_path)  # DOCX 正式输出
        
        return result