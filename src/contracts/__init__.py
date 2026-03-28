# Contracts Registry - 模块输入输出 schema 注册中心
"""
职责:
- 管理模块输入输出 schema
- 管理 handoff 结构
- 管理 contract 版本
- 为测试和校验提供统一真相源

首批 contract:
- opinion_to_write: 观点到写作的 handoff
- review_then_rewrite: 审核后改写的 handoff
- semantic_review_result: 语义审核结果
- module_error: 模块错误结构
- task_trace: 任务追踪结构
"""

# 基础类型
from .base import (
    ContractBaseModel,
    ErrorSeverity,
    TaskStatus,
    ModuleName,
    ErrorCode,
    CONTRACT_VERSION,
)

# 注册表
from .registry import ContractRegistry, registry

# Schema 导出
from .schema_export import (
    export_json_schema,
    export_json_schema_str,
    export_all_schemas,
)

# Contract 模型
from .module_error import ModuleError
from .task_trace import TaskTrace
from .semantic_review_result import (
    SemanticReviewResult,
    FindingItem,
    SeveritySummary,
    PrototypeAlignment,
    RewriteTarget,
)
from .opinion_to_write import (
    OpinionToWrite,
    Thesis,
    SupportPoint,
)
from .review_then_rewrite import ReviewThenRewrite

# 注册首批 contract
registry.register("module_error", ModuleError, CONTRACT_VERSION)
registry.register("task_trace", TaskTrace, CONTRACT_VERSION)
registry.register("semantic_review_result", SemanticReviewResult, CONTRACT_VERSION)
registry.register("opinion_to_write", OpinionToWrite, CONTRACT_VERSION)
registry.register("review_then_rewrite", ReviewThenRewrite, CONTRACT_VERSION)

__all__ = [
    # 基础类型
    "ContractBaseModel",
    "ErrorSeverity",
    "TaskStatus",
    "ModuleName",
    "ErrorCode",
    "CONTRACT_VERSION",
    # 注册表
    "ContractRegistry",
    "registry",
    # Schema 导出
    "export_json_schema",
    "export_json_schema_str",
    "export_all_schemas",
    # Contract 模型
    "ModuleError",
    "TaskTrace",
    "SemanticReviewResult",
    "FindingItem",
    "SeveritySummary",
    "PrototypeAlignment",
    "RewriteTarget",
    "OpinionToWrite",
    "Thesis",
    "SupportPoint",
    "ReviewThenRewrite",
]