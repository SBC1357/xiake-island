"""
Task Log 模型

定义任务日志内部数据结构。
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field

from src.contracts.base import TaskStatus, ModuleName


class TaskLogEntry(BaseModel):
    """
    任务日志条目
    
    Attributes:
        task_id: 任务唯一标识
        status: 任务状态
        module: 执行模块
        input_hash: 输入哈希 (用于版本分组)
        output_hash: 输出哈希 (可选)
        input_data: 完整输入参数 (可重放)
        output_data: 完整输出结果 (可查看)
        parent_task_id: 父任务ID (可选)
        child_task_ids: 子任务ID列表 (工作流场景)
        started_at: 开始时间 (ISO 8601)
        completed_at: 完成时间 (ISO 8601) (可选)
        duration_ms: 执行耗时 (毫秒) (可选)
        metadata: 元数据 (可选)
        error_message: 错误消息 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    task_id: str = Field(..., description="任务唯一标识")
    status: TaskStatus = Field(..., description="任务状态")
    module: ModuleName = Field(..., description="执行模块")
    input_hash: Optional[str] = Field(default=None, description="输入哈希 (用于版本分组)")
    output_hash: Optional[str] = Field(default=None, description="输出哈希")
    input_data: Optional[dict[str, Any]] = Field(default=None, description="完整输入参数 (可重放)")
    output_data: Optional[dict[str, Any]] = Field(default=None, description="完整输出结果 (可查看)")
    parent_task_id: Optional[str] = Field(default=None, description="父任务ID")
    child_task_ids: list[str] = Field(default_factory=list, description="子任务ID列表")
    started_at: str = Field(..., description="开始时间 (ISO 8601)")
    completed_at: Optional[str] = Field(default=None, description="完成时间")
    duration_ms: Optional[int] = Field(default=None, ge=0, description="执行耗时")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="元数据")
    error_message: Optional[str] = Field(default=None, description="错误消息")


class TaskLogQuery(BaseModel):
    """
    任务日志查询条件
    
    Attributes:
        task_id: 按任务ID查询
        module: 按模块查询
        status: 按状态查询
        parent_task_id: 按父任务ID查询
        input_hash: 按输入哈希查询 (版本分组)
        limit: 返回数量限制
    """
    model_config = ConfigDict(extra="forbid")
    
    task_id: Optional[str] = Field(default=None, description="任务ID")
    module: Optional[ModuleName] = Field(default=None, description="模块")
    status: Optional[TaskStatus] = Field(default=None, description="状态")
    parent_task_id: Optional[str] = Field(default=None, description="父任务ID")
    input_hash: Optional[str] = Field(default=None, description="输入哈希 (版本分组)")
    limit: int = Field(default=100, ge=1, le=1000, description="返回数量限制")