"""
Rules Module - Data Models

SP-6 Batch 6B: Deterministic Rule Execution Engine

定义规则执行引擎的核心数据模型，支持:
- 规则定义与元数据
- 规则执行结果与追踪
- 规则族管理
"""
from typing import Optional, Literal, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone


class RuleStatus(str, Enum):
    """规则执行状态"""
    MATCHED = "matched"      # 规则匹配（命中）
    FAILED = "failed"        # 规则检查失败（违规）
    SKIPPED = "skipped"      # 规则被跳过（条件不满足）
    ERROR = "error"          # 执行出错


class RuleSeverity(str, Enum):
    """规则严重程度"""
    CRITICAL = "critical"    # 严重违规，阻断流程
    HIGH = "high"           # 高风险
    MEDIUM = "medium"       # 中等风险
    LOW = "low"             # 低风险
    INFO = "info"           # 仅提示


class RuleFamilyId(str, Enum):
    """规则族标识"""
    REGISTER_LEVELS = "register_levels"
    EXPRESSION_BASE = "expression_base"
    MEDICAL_SYNTAX_RULES = "medical_syntax_rules"
    THESIS_DERIVATION_RULES = "thesis_derivation_rules"
    M5_COMPLIANCE = "m5_compliance"
    CUSTOM_USER_RULES = "custom_user_rules"


# ==================== 规则定义 ====================

@dataclass
class Rule:
    """
    单条规则定义
    
    Attributes:
        rule_id: 规则唯一标识
        family: 规则族
        name: 规则名称
        description: 规则描述
        severity: 严重程度
        checker: 检查函数 (content -> bool) 
                 返回 True 表示匹配/通过，False 表示失败/违规
        condition: 前置条件函数 (content -> bool)
                   返回 True 才执行 checker，否则跳过
        on_match: 匹配时的消息模板
        on_fail: 失败时的消息模板
        suggestion: 修改建议
        enabled: 是否启用
    """
    rule_id: str
    family: RuleFamilyId
    name: str
    description: str
    severity: RuleSeverity = RuleSeverity.MEDIUM
    checker: Optional[Callable[[str], bool]] = None
    condition: Optional[Callable[[str], bool]] = None
    on_match: Optional[str] = None
    on_fail: Optional[str] = None
    suggestion: Optional[str] = None
    enabled: bool = True


# ==================== 规则执行结果 ====================

@dataclass
class RuleResult:
    """
    单条规则执行结果
    
    Attributes:
        rule_id: 规则ID
        status: 执行状态
        severity: 严重程度
        message: 结果消息
        reason: 状态原因（为什么是这个状态）
        suggestion: 修改建议
        matched_text: 匹配到的文本片段（可选）
        position: 文本位置 (start, end)
        duration_ms: 执行耗时（毫秒）
    """
    rule_id: str
    status: RuleStatus
    severity: RuleSeverity
    message: str
    reason: str = ""
    suggestion: Optional[str] = None
    matched_text: Optional[str] = None
    position: Optional[tuple[int, int]] = None
    duration_ms: int = 0


# ==================== 规则追踪 ====================

@dataclass
class RuleTrace:
    """
    规则执行追踪
    
    SP-6 Batch 6B 核心输出: rule-level trace
    
    Attributes:
        family: 规则族
        total_rules: 执行规则总数
        matched: 匹配的规则ID列表
        failed: 失败的规则ID列表
        skipped: 跳过的规则ID列表
        errors: 出错的规则ID列表
        results: 详细执行结果列表
        summary: 执行摘要
        duration_ms: 总执行耗时
        executed_at: 执行时间
    """
    family: RuleFamilyId
    total_rules: int = 0
    matched: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    results: list[RuleResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    executed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    
    def add_result(self, result: RuleResult) -> None:
        """添加执行结果"""
        self.results.append(result)
        self.total_rules += 1
        
        if result.status == RuleStatus.MATCHED:
            self.matched.append(result.rule_id)
        elif result.status == RuleStatus.FAILED:
            self.failed.append(result.rule_id)
        elif result.status == RuleStatus.SKIPPED:
            self.skipped.append(result.rule_id)
        elif result.status == RuleStatus.ERROR:
            self.errors.append(result.rule_id)
    
    @property
    def has_critical_failures(self) -> bool:
        """是否有严重失败"""
        return any(
            r.status == RuleStatus.FAILED and r.severity == RuleSeverity.CRITICAL
            for r in self.results
        )
    
    @property
    def passed(self) -> bool:
        """是否通过（无失败）"""
        return len(self.failed) == 0 and len(self.errors) == 0


# ==================== 规则族输出 ====================

@dataclass
class RuleFamilyOutput:
    """
    规则族执行输出
    
    包含单个规则族的完整执行结果
    """
    family: RuleFamilyId
    trace: RuleTrace
    source: str = "built-in"  # built-in | external | adapter


# ==================== 综合规则执行结果 ====================

class RuleLayerOutput(BaseModel):
    """
    规则层输出
    
    SP-6 Batch 6B: 语义审核中区分规则层与模型层
    
    Attributes:
        families_executed: 执行的规则族列表
        traces: 各规则族的执行追踪
        total_matched: 总匹配数
        total_failed: 总失败数
        total_skipped: 总跳过数
        total_errors: 总错误数
        has_critical_failures: 是否有严重失败
        overall_passed: 总体是否通过
        duration_ms: 总耗时
    """
    model_config = ConfigDict(extra="forbid")
    
    families_executed: list[str] = Field(
        default_factory=list,
        description="执行的规则族列表"
    )
    traces: dict[str, Any] = Field(
        default_factory=dict,
        description="各规则族的执行追踪"
    )
    total_matched: int = Field(default=0, description="总匹配数")
    total_failed: int = Field(default=0, description="总失败数")
    total_skipped: int = Field(default=0, description="总跳过数")
    total_errors: int = Field(default=0, description="总错误数")
    has_critical_failures: bool = Field(
        default=False,
        description="是否有严重失败"
    )
    overall_passed: bool = Field(default=True, description="总体是否通过")
    duration_ms: int = Field(default=0, description="总耗时")
    
    def add_family_output(self, output: RuleFamilyOutput) -> None:
        """添加规则族输出"""
        self.families_executed.append(output.family.value)
        self.traces[output.family.value] = {
            "matched": output.trace.matched,
            "failed": output.trace.failed,
            "skipped": output.trace.skipped,
            "errors": output.trace.errors,
            "passed": output.trace.passed,
            "has_critical_failures": output.trace.has_critical_failures,
            "duration_ms": output.trace.duration_ms,
        }
        
        self.total_matched += len(output.trace.matched)
        self.total_failed += len(output.trace.failed)
        self.total_skipped += len(output.trace.skipped)
        self.total_errors += len(output.trace.errors)
        
        if output.trace.has_critical_failures:
            self.has_critical_failures = True
        
        if not output.trace.passed:
            self.overall_passed = False
        
        self.duration_ms += output.trace.duration_ms


# ==================== 规则族定义协议 ====================

class RuleFamilyDefinition:
    """
    规则族定义基类
    
    子类需要实现:
    - get_rules(): 返回规则列表
    - get_family_id(): 返回规则族ID
    """
    
    def get_family_id(self) -> RuleFamilyId:
        """返回规则族ID"""
        raise NotImplementedError
    
    def get_rules(self) -> list[Rule]:
        """返回规则列表"""
        raise NotImplementedError
    
    def get_source(self) -> str:
        """返回规则来源"""
        return "built-in"


# ==================== 类型别名 ====================

RuleChecker = Callable[[str], bool]
RuleCondition = Callable[[str], bool]