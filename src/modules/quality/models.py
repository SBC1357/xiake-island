"""
Quality Models

定义质量模块的数据模型，与 V2 契约兼容。
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class GateStatus(str, Enum):
    """门禁状态"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


# ==================== Pydantic 模型 (用于 API) ====================

class GateResultResponse(BaseModel):
    """门禁结果响应"""
    model_config = ConfigDict(extra="forbid")
    
    gate: str = Field(..., description="门禁名称")
    status: GateStatus = Field(..., description="门禁状态")
    message: Optional[str] = Field(default=None, description="消息")


class QualityResultResponse(BaseModel):
    """质量检查结果响应"""
    model_config = ConfigDict(extra="forbid")
    
    overall_status: GateStatus = Field(..., description="总体状态")
    gates_passed: List[str] = Field(default_factory=list, description="通过的门禁")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="警告列表")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    is_passed: bool = Field(..., description="是否通过")


# ==================== 内部数据类 (用于服务层) ====================

@dataclass
class QualityResult:
    """
    质量检查结果
    
    与 V2 QualityResult 契约兼容。
    """
    overall_status: GateStatus = GateStatus.PASSED
    gates_passed: List[str] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_passed(self) -> bool:
        """检查是否通过所有门禁"""
        return self.overall_status in [GateStatus.PASSED, GateStatus.WARNING]
    
    def add_warning(self, gate: str, message: str):
        """添加警告"""
        self.warnings.append({"gate": gate, "message": message})
        if self.overall_status == GateStatus.PASSED:
            self.overall_status = GateStatus.WARNING
    
    def add_error(self, gate: str, message: str):
        """添加错误"""
        self.errors.append({"gate": gate, "message": message})
        self.overall_status = GateStatus.FAILED