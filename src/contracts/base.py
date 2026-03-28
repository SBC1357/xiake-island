"""
Contract 基础模型和枚举

提供所有 contract 共享的基础类型定义。
"""

from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict


class ContractBaseModel(BaseModel):
    """
    所有 contract 的基类

    配置:
        - strict: 启用严格模式验证
        - extra: 禁止额外字段
    """

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class ErrorSeverity(str, Enum):
    """错误严重级别"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """任务状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModuleName(str, Enum):
    """模块名称"""

    OPINION = "opinion"
    SEMANTIC_REVIEW = "semantic_review"
    WRITING = "writing"
    ORCHESTRATOR = "orchestrator"
    PLANNING = "planning"
    EVIDENCE = "evidence"
    QUALITY = "quality"
    DELIVERY = "delivery"
    DRAFTING = "drafting"  # SP-7B: 独立成稿模块


class ErrorCode(str, Enum):
    """错误代码枚举"""

    # 基础设施错误
    INTERNAL_ERROR = "internal_error"
    TIMEOUT = "timeout"
    RESOURCE_UNAVAILABLE = "resource_unavailable"

    # 业务错误
    CONTRACT_VALIDATION_FAILED = "contract_validation_failed"
    MODULE_EXECUTION_FAILED = "module_execution_failed"

    # 外部依赖错误
    LLM_ERROR = "llm_error"
    ASSET_UNAVAILABLE = "asset_unavailable"
    SOURCE_UNAVAILABLE = "source_unavailable"


# 合约版本常量
CONTRACT_VERSION = "1.0.0"
