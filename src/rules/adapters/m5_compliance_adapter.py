"""
M5 Compliance Schema Adapter

SP-6 Batch 6B: 将 m5_compliance_schema 适配到规则引擎

将现有的 ComplianceChecker 包装为规则族，实现:
- 复用已有的合规检查逻辑
- 产出 rule-level trace
- 与其他规则族统一执行
"""
from typing import Optional
from dataclasses import dataclass

from ..models import (
    Rule,
    RuleResult,
    RuleTrace,
    RuleFamilyId,
    RuleFamilyDefinition,
    RuleFamilyOutput,
    RuleSeverity,
    RuleStatus,
)


def _get_suggestion_safe(checker, rule_id: str) -> Optional[str]:
    """安全获取规则建议"""
    if not checker or not checker.rules:
        return None
    rule = next((r for r in checker.rules if r.rule_id == rule_id), None)
    if rule:
        return checker._get_suggestion(rule)
    return None


class M5ComplianceAdapterFamily(RuleFamilyDefinition):
    """
    M5 合规检查适配器
    
    将 src.contracts.m5_compliance_schema.ComplianceChecker 
    包装为规则引擎可执行的规则族。
    """
    
    def __init__(self):
        """初始化适配器"""
        self._checker = None
        self._rules: Optional[list[Rule]] = None
    
    def _get_checker(self):
        """延迟加载 ComplianceChecker"""
        if self._checker is None:
            from src.contracts.m5_compliance_schema import ComplianceChecker
            self._checker = ComplianceChecker()
        return self._checker
    
    def get_family_id(self) -> RuleFamilyId:
        return RuleFamilyId.M5_COMPLIANCE
    
    def get_source(self) -> str:
        """来源是适配器"""
        return "adapter"
    
    def get_rules(self) -> list[Rule]:
        """将 ComplianceChecker 的规则转换为 Rule 对象"""
        if self._rules is not None:
            return self._rules
        
        checker = self._get_checker()
        self._rules = []
        
        # 将 ComplianceChecker 的规则转换为 Rule 对象
        for compliance_rule in checker.rules:
            # 创建检查函数
            def make_checker(rule_id: str):
                def checker_func(content: str) -> bool:
                    # 使用 ComplianceChecker 检查
                    checker = self._get_checker()
                    for rule in checker.rules:
                        if rule.rule_id == rule_id:
                            matches = checker._find_matches(content, rule)
                            return len(matches) > 0
                    return False
                return checker_func
            
            # 映射严重程度
            severity_map = {
                "critical": RuleSeverity.CRITICAL,
                "warning": RuleSeverity.HIGH,
                "info": RuleSeverity.LOW,
            }
            severity = severity_map.get(
                compliance_rule.severity, 
                RuleSeverity.MEDIUM
            )
            
            rule = Rule(
                rule_id=f"M5_{compliance_rule.rule_id}",
                family=RuleFamilyId.M5_COMPLIANCE,
                name=compliance_rule.name,
                description=compliance_rule.description,
                severity=severity,
                checker=make_checker(compliance_rule.rule_id),
                on_match=f"合规检查发现: {compliance_rule.name}",
                on_fail=f"合规检查通过: {compliance_rule.name}",
                suggestion=compliance_rule.description,
                enabled=compliance_rule.action != "log"
            )
            self._rules.append(rule)
        
        return self._rules
    
    def execute_with_details(self, content: str) -> RuleFamilyOutput:
        """
        执行合规检查并返回详细结果
        
        使用 ComplianceChecker.check() 获取详细的违规信息，
        然后转换为 RuleFamilyOutput 格式。
        """
        import time
        
        start_time = time.time()
        
        # 使用 ComplianceChecker 执行检查
        checker = self._get_checker()
        compliance_result = checker.check(content)
        
        # 构建规则追踪
        trace = RuleTrace(family=RuleFamilyId.M5_COMPLIANCE)
        
        # 将违规转换为规则结果
        for violation in compliance_result.violations:
            result = RuleResult(
                rule_id=f"M5_{violation.rule_id}",
                status=RuleStatus.MATCHED,
                severity=RuleSeverity.CRITICAL if violation.severity == "critical" else RuleSeverity.HIGH,
                message=f"合规违规: {violation.rule_name}",
                reason=violation.matched_text,
                suggestion=_get_suggestion_safe(
                    checker, violation.rule_id
                ),
                matched_text=violation.matched_text,
                position=violation.position
            )
            trace.add_result(result)
        
        # 将警告转换为规则结果
        for warning in compliance_result.warnings:
            result = RuleResult(
                rule_id=f"M5_{warning.rule_id}",
                status=RuleStatus.MATCHED,
                severity=RuleSeverity.MEDIUM,
                message=f"合规警告: {warning.rule_name}",
                reason=warning.matched_text,
                matched_text=warning.matched_text,
                position=warning.position
            )
            trace.add_result(result)
        
        trace.duration_ms = int((time.time() - start_time) * 1000)
        
        return RuleFamilyOutput(
            family=RuleFamilyId.M5_COMPLIANCE,
            trace=trace,
            source="adapter"
        )


# 便捷函数
def get_m5_compliance_rules() -> list[Rule]:
    """获取 M5 合规规则列表"""
    family = M5ComplianceAdapterFamily()
    return family.get_rules()


__all__ = [
    "M5ComplianceAdapterFamily",
    "get_m5_compliance_rules",
]