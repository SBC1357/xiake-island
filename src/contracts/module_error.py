"""
Module Error Contract

基础设施类 contract，用于统一表达模块执行错误。
所有失败都必须返回统一 `module_error` 结构，并落任务日志。

命名约定: {domain}_{artifact} 风格 (基础设施类)
"""
from typing import Optional, Any
from pydantic import Field
from .base import ContractBaseModel, ErrorCode, ModuleName


class ModuleError(ContractBaseModel):
    """
    模块错误结构
    
    用于统一表达模块执行过程中的各类错误。
    可被基础设施复用。
    
    Attributes:
        code: 错误代码
        message: 人类可读的错误消息
        module: 产生错误的模块名称
        details: 错误详情 (可选，待业务实现阶段细化)
        recoverable: 是否可恢复
        retry_count: 已重试次数
        timestamp: 错误发生时间 (ISO 8601 格式)
    """
    
    code: ErrorCode = Field(
        ...,
        description="错误代码"
    )
    message: str = Field(
        ...,
        description="人类可读的错误消息"
    )
    module: ModuleName = Field(
        ...,
        description="产生错误的模块名称"
    )
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="错误详情，待业务实现阶段细化"
    )
    recoverable: bool = Field(
        default=False,
        description="是否可恢复"
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="已重试次数"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="错误发生时间 (ISO 8601 格式)"
    )