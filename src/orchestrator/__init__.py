# Orchestrator - 主编排器
"""
职责:
- 接收标准化任务
- 判断是单模块调用还是工作流调用
- 组织模块顺序
- 传递 payload
- 汇总结果、状态与日志

公开接口:
- OrchestratorService: 编排服务
- ModuleTask: 模块任务
- WorkflowTask: 工作流任务
- OrchestratorExecutionResult: 执行结果
- ModuleExecutionResult: 模块执行结果
- 错误类型: OrchestratorError, UnsupportedModuleError, UnsupportedWorkflowError, WorkflowExecutionError
"""

# 数据模型
from .models import (
    ModuleTask,
    WorkflowTask,
    ModuleExecutionResult,
    OrchestratorExecutionResult,
)

# 错误
from .errors import (
    OrchestratorError,
    UnsupportedModuleError,
    UnsupportedWorkflowError,
    WorkflowExecutionError,
)

# 服务
from .service import OrchestratorService

__all__ = [
    # 数据模型
    "ModuleTask",
    "WorkflowTask",
    "ModuleExecutionResult",
    "OrchestratorExecutionResult",
    # 错误
    "OrchestratorError",
    "UnsupportedModuleError",
    "UnsupportedWorkflowError",
    "WorkflowExecutionError",
    # 服务
    "OrchestratorService",
]