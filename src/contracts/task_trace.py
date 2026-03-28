"""
Task Trace Contract

基础设施类 contract，用于追踪任务执行链路。
每次调用都应生成可追踪的任务记录。

命名约定: {domain}_{artifact} 风格 (基础设施类)
"""
from typing import Optional, Any
from pydantic import Field
from .base import ContractBaseModel, TaskStatus, ModuleName


class TaskTrace(ContractBaseModel):
    """
    任务追踪结构
    
    用于追踪任务执行链路，支持可审计性要求。
    可被基础设施复用。
    
    Attributes:
        task_id: 任务唯一标识
        status: 任务当前状态
        module: 执行模块名称
        input_hash: 输入数据哈希 (可选，用于去重和缓存)
        output_hash: 输出数据哈希 (可选)
        parent_task_id: 父任务ID (用于工作流追踪)
        started_at: 任务开始时间 (ISO 8601)
        completed_at: 任务完成时间 (ISO 8601)
        duration_ms: 执行耗时 (毫秒)
        metadata: 任务元数据 (待业务实现阶段细化)
    """
    
    task_id: str = Field(
        ...,
        description="任务唯一标识"
    )
    status: TaskStatus = Field(
        ...,
        description="任务当前状态"
    )
    module: ModuleName = Field(
        ...,
        description="执行模块名称"
    )
    input_hash: Optional[str] = Field(
        default=None,
        description="输入数据哈希，用于去重和缓存"
    )
    output_hash: Optional[str] = Field(
        default=None,
        description="输出数据哈希"
    )
    parent_task_id: Optional[str] = Field(
        default=None,
        description="父任务ID，用于工作流追踪"
    )
    started_at: Optional[str] = Field(
        default=None,
        description="任务开始时间 (ISO 8601)"
    )
    completed_at: Optional[str] = Field(
        default=None,
        description="任务完成时间 (ISO 8601)"
    )
    duration_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="执行耗时 (毫秒)"
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="任务元数据，待业务实现阶段细化"
    )