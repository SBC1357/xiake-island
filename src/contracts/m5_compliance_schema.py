"""
M5 Compliance Schema

合规红线检查模型，定义合规检查规则和结果结构。
用于 SP-4 合规红线检查增强。
"""
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
import re


# ==================== 合规规则定义 ====================

class ComplianceRule(BaseModel):
    """
    合规规则
    
    定义单个合规检查规则，包括模式匹配和响应动作。
    
    Attributes:
        rule_id: 规则唯一标识
        name: 规则名称
        description: 规则描述
        pattern: 匹配模式（正则表达式或关键词列表）
        pattern_type: 模式类型 (regex/keyword)
        severity: 严重程度 (critical/warning/info)
        action: 触发时的动作 (block/flag/log)
        category: 规则类别
    """
    model_config = ConfigDict(extra="forbid")
    
    rule_id: str = Field(..., description="规则唯一标识")
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    pattern: str = Field(..., description="匹配模式")
    pattern_type: Literal["regex", "keyword"] = Field(
        default="keyword",
        description="模式类型"
    )
    severity: Literal["critical", "warning", "info"] = Field(
        default="warning",
        description="严重程度"
    )
    action: Literal["block", "flag", "log"] = Field(
        default="flag",
        description="触发动作"
    )
    category: str = Field(
        default="general",
        description="规则类别"
    )


class ComplianceViolation(BaseModel):
    """
    合规违规项
    
    记录单次合规检查中发现的违规内容。
    
    Attributes:
        rule_id: 触发的规则ID
        rule_name: 规则名称
        matched_text: 匹配到的文本片段
        position: 文本位置 (start, end)
        severity: 严重程度
        suggestion: 建议修改
    """
    model_config = ConfigDict(extra="forbid")
    
    rule_id: str = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    matched_text: str = Field(..., description="匹配文本")
    position: tuple[int, int] = Field(..., description="位置 (start, end)")
    severity: str = Field(..., description="严重程度")
    suggestion: Optional[str] = Field(default=None, description="修改建议")


class ComplianceResult(BaseModel):
    """
    合规检查结果
    
    Attributes:
        passed: 是否通过检查
        violations: 违规项列表
        warnings: 警告项列表
        checked_at: 检查时间 (ISO 8601)
        content_hash: 内容哈希（用于缓存）
    """
    model_config = ConfigDict(extra="forbid")
    
    passed: bool = Field(..., description="是否通过")
    violations: list[ComplianceViolation] = Field(
        default_factory=list,
        description="违规项"
    )
    warnings: list[ComplianceViolation] = Field(
        default_factory=list,
        description="警告项"
    )
    checked_at: str = Field(..., description="检查时间")
    content_hash: Optional[str] = Field(
        default=None,
        description="内容哈希"
    )
    
    @property
    def has_critical_violations(self) -> bool:
        """是否存在严重违规"""
        return any(v.severity == "critical" for v in self.violations)
    
    @property
    def violation_count(self) -> int:
        """违规总数"""
        return len(self.violations)
    
    @property
    def warning_count(self) -> int:
        """警告总数"""
        return len(self.warnings)


# ==================== 默认规则集 ====================

# 医疗内容敏感词（示例）
DEFAULT_BANNED_WORDS = [
    # 疗效绝对化表述
    "根治", "百分之百", "100%治愈", "无效退款", "包治百病",
    # 未经批准的宣称
    "最新发现", "突破性进展", "革命性突破", "世界首创",
    # 恐吓性表述
    "不治之症", "绝症", "必死无疑",
]

# 合规红线规则
DEFAULT_REDLINED_RULES: list[ComplianceRule] = [
    ComplianceRule(
        rule_id="REDLINE_001",
        name="绝对化疗效宣称",
        description="禁止使用绝对化疗效宣称用语",
        pattern="根治|百分之百|100%治愈|无效退款|包治百病|彻底治愈",
        pattern_type="regex",
        severity="critical",
        action="block",
        category="efficacy_claim"
    ),
    ComplianceRule(
        rule_id="REDLINE_002",
        name="未经批准宣称",
        description="禁止使用未经审批宣称用语",
        pattern="最新发现|突破性进展|革命性突破|世界首创|首创|独家秘方",
        pattern_type="regex",
        severity="warning",
        action="flag",
        category="unapproved_claim"
    ),
    ComplianceRule(
        rule_id="REDLINE_003",
        name="恐吓性表述",
        description="禁止使用恐吓性表述诱导患者",
        pattern="不治之症|绝症|必死无疑|错过后悔|再不治就",
        pattern_type="regex",
        severity="warning",
        action="flag",
        category="fear_tactic"
    ),
    ComplianceRule(
        rule_id="REDLINE_004",
        name="处方药直接面向患者宣传",
        description="处方药不得直接面向患者宣传疗效",
        pattern="处方药.*疗效|特效药|神药|灵丹妙药",
        pattern_type="regex",
        severity="critical",
        action="block",
        category="prescription_promotion"
    ),
    ComplianceRule(
        rule_id="REDLINE_005",
        name="虚假对比",
        description="禁止与其他产品进行不实对比",
        pattern="比.*强.*倍|远超.*疗效|秒杀.*产品",
        pattern_type="regex",
        severity="warning",
        action="flag",
        category="false_comparison"
    ),
]


# ==================== 合规检查器 ====================

class ComplianceChecker:
    """
    合规检查器
    
    对内容进行合规红线检查，支持自定义规则扩展。
    """
    
    def __init__(self, rules: Optional[list[ComplianceRule]] = None):
        """
        初始化合规检查器
        
        Args:
            rules: 自定义规则列表，如未提供则使用默认规则
        """
        self.rules = rules or DEFAULT_REDLINED_RULES
        self._compiled_patterns: dict[str, re.Pattern] = {}
        
        # 预编译正则表达式
        for rule in self.rules:
            if rule.pattern_type == "regex":
                try:
                    self._compiled_patterns[rule.rule_id] = re.compile(rule.pattern)
                except re.error:
                    # 正则编译失败时回退到关键词匹配
                    pass
    
    def check(self, content: str, strict_mode: bool = True) -> ComplianceResult:
        """
        执行合规检查
        
        Args:
            content: 待检查的内容
            strict_mode: 严格模式（critical违规直接block）
            
        Returns:
            合规检查结果
        """
        from datetime import datetime, timezone
        from src.runtime_logging.hash_utils import compute_input_hash
        
        violations: list[ComplianceViolation] = []
        warnings: list[ComplianceViolation] = []
        
        for rule in self.rules:
            matches = self._find_matches(content, rule)
            
            for match_text, position in matches:
                violation = ComplianceViolation(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    matched_text=match_text,
                    position=position,
                    severity=rule.severity,
                    suggestion=self._get_suggestion(rule)
                )
                
                if rule.severity == "critical":
                    violations.append(violation)
                else:
                    warnings.append(violation)
        
        # 判断是否通过
        passed = not violations
        if strict_mode:
            passed = not violations and not any(
                w.severity == "critical" for w in warnings
            )
        
        return ComplianceResult(
            passed=passed,
            violations=violations,
            warnings=warnings,
            checked_at=datetime.now(timezone.utc).isoformat(),
            content_hash=compute_input_hash({"content": content})[:16]
        )
    
    def _find_matches(
        self, 
        content: str, 
        rule: ComplianceRule
    ) -> list[tuple[str, tuple[int, int]]]:
        """查找规则匹配"""
        matches: list[tuple[str, tuple[int, int]]] = []
        
        if rule.pattern_type == "regex":
            # 使用预编译的正则表达式
            pattern = self._compiled_patterns.get(rule.rule_id)
            if pattern:
                for match in pattern.finditer(content):
                    matches.append((
                        match.group(),
                        (match.start(), match.end())
                    ))
        else:
            # 关键词匹配
            keywords = rule.pattern.split("|")
            for keyword in keywords:
                start = 0
                while True:
                    pos = content.find(keyword, start)
                    if pos == -1:
                        break
                    matches.append((
                        keyword,
                        (pos, pos + len(keyword))
                    ))
                    start = pos + 1
        
        return matches
    
    def _get_suggestion(self, rule: ComplianceRule) -> str:
        """获取修改建议"""
        suggestions = {
            "REDLINE_001": "请使用客观描述替代绝对化表述，如'显著改善'、'有效缓解'",
            "REDLINE_002": "请提供权威出处或删除未经批准的宣称",
            "REDLINE_003": "请避免使用恐吓性表述，采用客观、温和的表述方式",
            "REDLINE_004": "处方药宣传请遵守相关法规要求",
            "REDLINE_005": "请提供循证医学证据支持对比声明",
        }
        return suggestions.get(rule.rule_id, f"请检查内容是否符合合规要求: {rule.description}")
    
    def add_rule(self, rule: ComplianceRule) -> None:
        """添加自定义规则"""
        self.rules.append(rule)
        if rule.pattern_type == "regex":
            try:
                self._compiled_patterns[rule.rule_id] = re.compile(rule.pattern)
            except re.error:
                pass