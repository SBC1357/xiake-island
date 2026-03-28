"""
Orchestrator 数据模型

定义任务编排的数据结构。
"""

from typing import Optional, Any, Literal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

from src.contracts.base import TaskStatus


class ExecutionMode(str, Enum):
    """
    执行模式

    - module: 单模块调用
    - workflow: 工作流调用
    """

    MODULE = "module"
    WORKFLOW = "workflow"


class ModuleTask(BaseModel):
    """
    模块任务

    单模块调用任务。

    Attributes:
        mode: 执行模式 (固定为 "module")
        module_name: 模块名称 (opinion / semantic_review)
        input_data: 模块输入数据
        metadata: 任务元数据 (可选)
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["module"] = Field(default="module", description="执行模式")
    module_name: Literal[
        "opinion",
        "semantic_review",
        "planning",
        "evidence",
        "quality",
        "delivery",
        "drafting",
    ] = Field(..., description="模块名称")
    input_data: dict[str, Any] = Field(..., description="模块输入数据")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="任务元数据")


class WorkflowTask(BaseModel):
    """
    工作流任务

    工作流调用任务。

    支持的工作流：
    - article: opinion -> semantic_review
    - standard_chain: Evidence -> Planning -> Writing -> Quality -> Delivery

    Attributes:
        mode: 执行模式 (固定为 "workflow")
        workflow_name: 工作流名称 (article / standard_chain)
        input_data: 工作流输入数据
        metadata: 任务元数据 (可选)
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["workflow"] = Field(default="workflow", description="执行模式")
    workflow_name: Literal["article", "standard_chain"] = Field(
        ..., description="工作流名称"
    )
    input_data: dict[str, Any] = Field(..., description="工作流输入数据")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="任务元数据")


class ModuleExecutionResult(BaseModel):
    """
    模块执行结果

    Attributes:
        module_name: 模块名称
        task_id: 子任务ID
        status: 执行状态
        result: 执行结果数据
        error: 错误信息 (可选)
    """

    model_config = ConfigDict(extra="forbid")

    module_name: str = Field(..., description="模块名称")
    task_id: str = Field(..., description="子任务ID")
    status: TaskStatus = Field(..., description="执行状态")
    result: Optional[dict[str, Any]] = Field(default=None, description="执行结果数据")
    error: Optional[str] = Field(default=None, description="错误信息")


class OrchestratorExecutionResult(BaseModel):
    """
    Orchestrator 执行结果

    统一执行结果结构。

    Attributes:
        task_id: 父任务ID
        mode: 执行模式
        status: 执行状态
        module_name: 模块名称 (单模块模式)
        workflow_name: 工作流名称 (工作流模式)
        result: 最终结果数据
        child_task_ids: 子任务ID列表
        child_results: 子任务结果列表
        errors: 错误列表
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(..., description="父任务ID")
    mode: str = Field(..., description="执行模式")
    status: TaskStatus = Field(..., description="执行状态")
    module_name: Optional[str] = Field(default=None, description="模块名称")
    workflow_name: Optional[str] = Field(default=None, description="工作流名称")
    result: Optional[dict[str, Any]] = Field(default=None, description="最终结果数据")
    child_task_ids: list[str] = Field(default_factory=list, description="子任务ID列表")
    child_results: list[ModuleExecutionResult] = Field(
        default_factory=list, description="子任务结果列表"
    )
    errors: list[str] = Field(default_factory=list, description="错误列表")
