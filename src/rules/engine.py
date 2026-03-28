"""
Rules Engine - 规则执行引擎

SP-6 Batch 6B: 确定性规则执行引擎

核心功能:
- 加载和执行规则族
- 产出 rule-level trace (matched/failed/skipped/errors with reasons)
- 支持内置规则族和外部资产加载
"""
import time
import re
from typing import Optional, Callable
from dataclasses import dataclass, field

from .models import (
    Rule,
    RuleResult,
    RuleTrace,
    RuleFamilyOutput,
    RuleLayerOutput,
    RuleFamilyId,
    RuleFamilyDefinition,
    RuleStatus,
    RuleSeverity,
)


# ==================== 规则族注册表 ====================

@dataclass
class RuleFamilyRegistry:
    """
    规则族注册表
    
    管理所有可用的规则族定义。
    支持内置规则族和动态加载的外部规则族。
    """
    families: dict[RuleFamilyId, RuleFamilyDefinition] = field(default_factory=dict)
    
    def register(self, family: RuleFamilyDefinition) -> None:
        """注册规则族"""
        self.families[family.get_family_id()] = family
    
    def get(self, family_id: RuleFamilyId) -> Optional[RuleFamilyDefinition]:
        """获取规则族"""
        return self.families.get(family_id)
    
    def list_families(self) -> list[RuleFamilyId]:
        """列出所有注册的规则族"""
        return list(self.families.keys())


# ==================== 规则执行引擎 ====================

class RuleEngine:
    """
    规则执行引擎
    
    SP-6 Batch 6B 核心: 执行确定性规则并产出 rule-level trace。
    
    特性:
    - 执行指定的规则族
    - 记录 matched/failed/skipped/errors 状态及原因
    - 支持条件跳过规则
    - 记录执行耗时
    
    Usage:
        engine = RuleEngine()
        engine.register_family(RegisterLevelsFamily())
        
        output = engine.execute(
            content="待检查内容",
            families=[RuleFamilyId.REGISTER_LEVELS]
        )
    """
    
    def __init__(self):
        """初始化规则引擎"""
        self.registry = RuleFamilyRegistry()
        self._external_load_hook: Optional[Callable[[RuleFamilyId], Optional[RuleFamilyDefinition]]] = None
    
    def register_family(self, family: RuleFamilyDefinition) -> None:
        """注册规则族"""
        self.registry.register(family)
    
    def set_external_load_hook(
        self, 
        hook: Callable[[RuleFamilyId], Optional[RuleFamilyDefinition]]
    ) -> None:
        """
        设置外部资产加载钩子
        
        当内置规则族不存在时，调用此钩子尝试从外部加载。
        这允许未来从藏经阁或其他来源加载规则资产。
        
        Args:
            hook: 接受 RuleFamilyId，返回 RuleFamilyDefinition 或 None
        """
        self._external_load_hook = hook
    
    def _get_family(self, family_id: RuleFamilyId) -> Optional[RuleFamilyDefinition]:
        """获取规则族，支持外部加载"""
        # 先从注册表获取
        family = self.registry.get(family_id)
        if family:
            return family
        
        # 尝试从外部加载
        if self._external_load_hook:
            return self._external_load_hook(family_id)
        
        return None
    
    def execute_single_rule(
        self, 
        rule: Rule, 
        content: str
    ) -> RuleResult:
        """
        执行单条规则
        
        Args:
            rule: 规则定义
            content: 待检查内容
            
        Returns:
            规则执行结果
        """
        start_time = time.time()
        
        # 检查是否启用
        if not rule.enabled:
            return RuleResult(
                rule_id=rule.rule_id,
                status=RuleStatus.SKIPPED,
                severity=rule.severity,
                message=f"规则 {rule.rule_id} 已禁用",
                reason="disabled"
            )
        
        # 检查前置条件
        if rule.condition:
            try:
                if not rule.condition(content):
                    return RuleResult(
                        rule_id=rule.rule_id,
                        status=RuleStatus.SKIPPED,
                        severity=rule.severity,
                        message=f"规则 {rule.rule_id} 前置条件不满足",
                        reason="condition_not_met"
                    )
            except Exception as e:
                return RuleResult(
                    rule_id=rule.rule_id,
                    status=RuleStatus.ERROR,
                    severity=rule.severity,
                    message=f"前置条件检查出错: {str(e)}",
                    reason=f"condition_error: {str(e)}"
                )
        
        # 执行规则检查
        try:
            if rule.checker is None:
                return RuleResult(
                    rule_id=rule.rule_id,
                    status=RuleStatus.ERROR,
                    severity=rule.severity,
                    message="规则缺少检查函数",
                    reason="no_checker_defined"
                )
            
            check_result = rule.checker(content)
            duration_ms = int((time.time() - start_time) * 1000)
            
            if check_result:
                # 规则匹配（命中）
                return RuleResult(
                    rule_id=rule.rule_id,
                    status=RuleStatus.MATCHED,
                    severity=rule.severity,
                    message=rule.on_match or f"规则 {rule.rule_id} 匹配",
                    reason="pattern_matched",
                    suggestion=rule.suggestion,
                    duration_ms=duration_ms
                )
            else:
                # 规则不匹配（未命中，不是失败）
                return RuleResult(
                    rule_id=rule.rule_id,
                    status=RuleStatus.FAILED,
                    severity=rule.severity,
                    message=rule.on_fail or f"规则 {rule.rule_id} 检查未通过",
                    reason="check_failed",
                    suggestion=rule.suggestion,
                    duration_ms=duration_ms
                )
                
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return RuleResult(
                rule_id=rule.rule_id,
                status=RuleStatus.ERROR,
                severity=rule.severity,
                message=f"规则执行出错: {str(e)}",
                reason=f"execution_error: {str(e)}",
                duration_ms=duration_ms
            )
    
    def execute_family(
        self, 
        family_id: RuleFamilyId, 
        content: str
    ) -> Optional[RuleFamilyOutput]:
        """
        执行单个规则族
        
        Args:
            family_id: 规则族ID
            content: 待检查内容
            
        Returns:
            规则族输出，如果规则族不存在则返回 None
        """
        start_time = time.time()
        
        family = self._get_family(family_id)
        if not family:
            return None
        
        rules = family.get_rules()
        trace = RuleTrace(family=family_id)
        
        for rule in rules:
            result = self.execute_single_rule(rule, content)
            trace.add_result(result)
        
        trace.duration_ms = int((time.time() - start_time) * 1000)
        
        return RuleFamilyOutput(
            family=family_id,
            trace=trace,
            source=family.get_source()
        )
    
    def execute(
        self, 
        content: str, 
        families: Optional[list[RuleFamilyId]] = None
    ) -> RuleLayerOutput:
        """
        执行规则引擎
        
        Args:
            content: 待检查内容
            families: 要执行的规则族列表，如果为 None 则执行所有注册的规则族
            
        Returns:
            规则层输出
        """
        start_time = time.time()
        output = RuleLayerOutput()
        
        # 确定要执行的规则族
        families_to_run = families if families else self.registry.list_families()
        
        for family_id in families_to_run:
            family_output = self.execute_family(family_id, content)
            if family_output:
                output.add_family_output(family_output)
        
        output.duration_ms = int((time.time() - start_time) * 1000)
        
        return output


# ==================== 辅助函数 ====================

def create_pattern_checker(pattern: str, pattern_type: str = "keyword") -> Callable[[str], bool]:
    """
    创建模式检查器
    
    Args:
        pattern: 匹配模式
        pattern_type: 模式类型 (regex/keyword)
        
    Returns:
        检查函数，返回 True 表示模式匹配
    """
    if pattern_type == "regex":
        compiled = re.compile(pattern)
        return lambda content: bool(compiled.search(content))
    else:
        # keyword 模式：检查是否包含任一关键词
        keywords = pattern.split("|")
        return lambda content: any(kw in content for kw in keywords)


def create_pattern_checker_with_matches(
    pattern: str, 
    pattern_type: str = "keyword"
) -> tuple[Callable[[str], bool], Callable[[str], list[tuple[str, tuple[int, int]]]]]:
    """
    创建模式检查器（带匹配详情）
    
    Returns:
        (checker, matcher) 元组
        - checker: 检查函数，返回 True 表示匹配
        - matcher: 匹配函数，返回 [(matched_text, (start, end)), ...]
    """
    if pattern_type == "regex":
        compiled = re.compile(pattern)
        
        def regex_checker(content: str) -> bool:
            return bool(compiled.search(content))
        
        def regex_matcher(content: str) -> list[tuple[str, tuple[int, int]]]:
            matches = []
            for match in compiled.finditer(content):
                matches.append((match.group(), (match.start(), match.end())))
            return matches
        
        return regex_checker, regex_matcher
    else:
        keywords = pattern.split("|")
        
        def keyword_checker(content: str) -> bool:
            return any(kw in content for kw in keywords)
        
        def keyword_matcher(content: str) -> list[tuple[str, tuple[int, int]]]:
            matches = []
            for kw in keywords:
                start = 0
                while True:
                    pos = content.find(kw, start)
                    if pos == -1:
                        break
                    matches.append((kw, (pos, pos + len(kw))))
                    start = pos + 1
            return matches
        
        return keyword_checker, keyword_matcher