"""
Delivery Models

定义交付模块的数据模型，与 V2 契约兼容。

SP-6 Batch 6D: 新增 docx 输出元数据和字数门禁字段。
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


# ==================== Pydantic 模型 (用于 API) ====================

class DeliveryResultResponse(BaseModel):
    """
    交付结果响应
    
    SP-6 Batch 6D: 新增 docx 相关字段和字数门禁字段。
    """
    model_config = ConfigDict(extra="forbid")
    
    task_id: Optional[str] = Field(default=None, description="任务ID")
    output_path: Optional[str] = Field(default=None, description="主输出文件路径 (docx)")
    artifacts: List[str] = Field(default_factory=list, description="所有生成产物的路径")
    summary: Dict[str, Any] = Field(default_factory=dict, description="交付摘要")
    completed_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="完成时间")
    
    # SP-6 Batch 6D: 新增字段
    markdown_preview_path: Optional[str] = Field(default=None, description="Markdown 预览文件路径")
    docx_path: Optional[str] = Field(default=None, description="DOCX 正式输出路径")
    final_docx_word_count: Optional[int] = Field(default=None, description="DOCX 正文字数")
    word_count_basis: str = Field(default="docx_body", description="字数计算基准")
    target_word_count: Optional[int] = Field(default=None, description="目标字数")
    word_count_gate_passed: Optional[bool] = Field(default=None, description="字数门禁是否通过")


# ==================== 内部数据类 (用于服务层) ====================

@dataclass
class DeliveryResult:
    """
    交付结果
    
    与 V2 DeliveryResult 契约兼容。
    
    SP-6 Batch 6D: 新增 docx 输出元数据和字数门禁字段。
    """
    output_path: Optional[Path] = None
    task_log_path: Optional[Path] = None
    task_log_paths: List[Path] = field(default_factory=list)
    artifacts: List[Path] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)
    
    # SP-6 Batch 6D: 新增字段
    markdown_preview_path: Optional[Path] = None
    docx_path: Optional[Path] = None
    final_docx_word_count: Optional[int] = None
    word_count_basis: str = "docx_body"
    target_word_count: Optional[int] = None
    word_count_gate_passed: Optional[bool] = None
    
    def add_artifact(self, path: Path):
        """添加产物路径"""
        self.artifacts.append(path)
    
    def add_log_path(self, path: Path):
        """添加日志路径"""
        self.task_log_paths.append(path)
        if self.task_log_path is None:
            self.task_log_path = path


class WordCountGateError(Exception):
    """
    字数门禁错误
    
    当 docx 正文字数低于目标阈值时抛出。
    """
    def __init__(
        self,
        message: str,
        final_word_count: int,
        target_word_count: int
    ):
        super().__init__(message)
        self.final_word_count = final_word_count
        self.target_word_count = target_word_count