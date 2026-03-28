"""
Quality Orchestrator 

质量编排器，实现 V2 quality/orchestrator 逻辑。

SP-6 Batch 6B: 集成规则执行引擎，产出 rule-level trace。
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .models import QualityResult, GateStatus
from src.modules.writing import CompiledPrompt
from src.contracts.m5_compliance_schema import ComplianceChecker, ComplianceResult


# 关键门禁列表：失败时阻断流程
CRITICAL_GATES = {"basic", "compliance", "inference_clean"}


@dataclass
class QualityOrchestrator:
    """
    质量编排器
    
    负责协调多个质量门禁的运行。
    与 V2 QualityOrchestrator 兼容。
    
    SP-6 Batch 6B 新增:
    - rule_trace: 规则执行追踪
    - run_rules: 执行规则引擎
    """
    
    enabled_gates: List[str] = field(default_factory=lambda: ["basic", "schema"])
    config: Dict[str, Any] = field(default_factory=dict)
    compliance_checker: Optional[ComplianceChecker] = field(default=None)
    rule_engine: Optional[Any] = field(default=None, repr=False)  # RuleEngine
    _last_rule_trace: Optional[Dict[str, Any]] = field(default=None, repr=False)
    
    def __post_init__(self):
        """初始化合规检查器和规则引擎"""
        if self.compliance_checker is None:
            self.compliance_checker = ComplianceChecker()
    
    @property
    def rule_trace(self) -> Optional[Dict[str, Any]]:
        """
        获取最近一次规则执行的追踪结果
        
        SP-6 Batch 6B: 暴露 rule-level trace 到程序输出
        """
        return self._last_rule_trace
    
    def run_gates(self, prompt: CompiledPrompt) -> QualityResult:
        """
        运行所有启用的门禁
        
        Args:
            prompt: 编译后的 prompt
            
        Returns:
            QualityResult: 门禁检查结果
        """
        result = QualityResult()
        
        for gate in self.enabled_gates:
            try:
                gate_result = self._run_single_gate(gate, prompt)
                if gate_result:
                    result.gates_passed.append(gate)
                else:
                    # 区分关键门禁和非关键门禁
                    if gate in CRITICAL_GATES:
                        # 关键门禁失败：添加错误，阻断流程
                        result.add_error(gate, f"{gate} gate failed - critical check failed")
                    else:
                        # 非关键门禁失败：只添加警告
                        result.add_warning(gate, f"{gate} gate returned warnings")
            except Exception as e:
                result.add_error(gate, str(e))
        
        return result
    
    def run_gates_on_content(self, content: str, enabled_gates: Optional[List[str]] = None) -> QualityResult:
        """
        对内容运行门禁检查
        
        Args:
            content: 待检查的内容
            enabled_gates: 可选的门禁列表，如未指定则使用 self.enabled_gates
            
        Returns:
            QualityResult: 门禁检查结果
        """
        result = QualityResult()
        
        # 使用传入的 enabled_gates 或默认的 self.enabled_gates
        gates_to_run = enabled_gates if enabled_gates is not None else self.enabled_gates
        
        # 基础检查（内容门禁）
        if self._check_basic_content(content):
            result.gates_passed.append("basic")
        else:
            result.add_error("basic", "内容基础检查失败")

        # 推理泄露检查（CRITICAL: 命中则阻断交付）
        if self._check_inference_leak(content):
            result.gates_passed.append("inference_clean")
        else:
            result.add_error("inference_clean", "检测到推理泄露标记（<think> 或内部推理句式），阻断交付")
            
        # 边界越界检查（CRITICAL: 命中则阻断交付）
        boundary_violations = self._check_boundary_violations(content)
        if not boundary_violations:
            result.gates_passed.append("boundary_clean")
        else:
            for violation in boundary_violations:
                result.add_error("boundary_clean", f"边界越界检测拦截: {violation}")
        
        # 长度检查（内容门禁 - 总是运行）
        if len(content) >= 10:
            result.gates_passed.append("length")
        else:
            result.add_warning("length", f"内容长度不足: {len(content)} < 10")
        
        # 合规检查（红线门禁 - 总是运行）
        compliance_result = self.compliance_check(content)
        if compliance_result.passed:
            result.gates_passed.append("compliance")
        else:
            # 合规检查失败
            if compliance_result.has_critical_violations:
                result.add_error("compliance", f"合规红线检查失败: 发现 {compliance_result.violation_count} 个严重违规")
            else:
                result.add_warning("compliance", f"合规检查警告: 发现 {compliance_result.warning_count} 个警告项")
        
        return result
    
    def _run_single_gate(self, gate_name: str, prompt: CompiledPrompt) -> bool:
        """运行单个门禁"""
        if gate_name == "basic":
            # 基础检查：prompt 非空 - 关键门禁
            if not prompt.system_prompt:
                return False
            if not prompt.user_prompt:
                return False
            return True
        elif gate_name == "schema":
            # schema 检查：配置存在 - 非关键门禁
            return bool(self.config)
        return True
    
    def _check_inference_leak(self, content: str) -> bool:
        """检查是否存在推理泄露（<think> 标记或内部推理句式）"""
        import re
        if re.search(r'<think>', content, re.IGNORECASE):
            return False
        _INFERENCE_PREFIXES = (
            "The user wants", "Let me think", "I need to",
        )
        lines = content.splitlines()
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(p) for p in _INFERENCE_PREFIXES):
                return False
        return True

    def _check_boundary_violations(self, content: str) -> List[str]:
        """检查是否存在写作边界越界，拦截 4 类典型越界表述"""
        import re
        violations = []
        
        # 1. 动物→人体
        if re.search(r'(小鼠|大鼠|动物模型|体外实验).*?(临床显效|治愈患者|在人体内证实|显著改善患者)', content, re.DOTALL | re.IGNORECASE):
            violations.append("动物/体外实验直接推导人体临床获益 (动物→人体越界)")
            
        # 2. 方法学→临床价值
        if re.search(r'(检测法|试剂盒|测序法|染色法|方法学研究).*?(能够治疗|完全缓解病患|改善生存期|替代临床治疗)', content, re.DOTALL | re.IGNORECASE):
            violations.append("方法学研究硬关联直接临床疗效 (方法学→临床价值越界)")
            
        # 3. 相关性→因果
        if re.search(r'(相关性|有关联|可能相关).*?(导致了|决定了|绝对原因是)', content, re.DOTALL | re.IGNORECASE):
            violations.append("从相关性研究跳跃得出确定的因果推论 (相关性→因果越界)")
            
        # 4. 海报→定论
        if re.search(r'(海报|初步数据|中期分析|初步观察).*?(已确立|成为标准治疗|证实了绝对优势|毋庸置疑)', content, re.DOTALL | re.IGNORECASE):
            violations.append("从初步数据或海报直接宣布临床定论 (海报→定论越界)")
            
        return violations

    def _check_basic_content(self, content: str) -> bool:
        """检查基础内容"""
        if not content:
            return False
        if len(content.strip()) < 10:
            return False
        return True
    
    def compliance_check(self, content: str) -> ComplianceResult:
        """
        执行合规检查
        
        Args:
            content: 待检查的内容
            
        Returns:
            ComplianceResult: 合规检查结果
        """
        # compliance_checker 在 __post_init__ 中初始化，但类型检查器不知道这一点
        if self.compliance_checker is None:
            self.compliance_checker = ComplianceChecker()
        return self.compliance_checker.check(content)
    
    def semantic_review_check(self, content: str) -> Dict[str, Any]:
        """
        语义审查检查
        
        Args:
            content: 待审查内容
            
        Returns:
            审查结果
        """
        issues = []
        suggestions = []
        
        # 基础语义检查
        if len(content) < 50:
            suggestions.append("内容较短，建议补充更多细节")
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "passed": len(issues) == 0
        }
    
    def run_rules(
        self, 
        content: str, 
        families: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        执行规则引擎
        
        SP-6 Batch 6B: 执行确定性规则并产出 rule-level trace
        
        Args:
            content: 待检查内容
            families: 要执行的规则族列表（可选）
            
        Returns:
            规则执行结果，包含 rule-level trace
        """
        from src.rules import RuleEngine, RuleFamilyId
        from src.rules.families import (
            RegisterLevelsFamily,
            ExpressionBaseFamily,
            MedicalSyntaxRulesFamily,
            ThesisDerivationRulesFamily,
        )
        from src.rules.adapters import M5ComplianceAdapterFamily
        
        # 创建或复用规则引擎
        if self.rule_engine is None:
            self.rule_engine = RuleEngine()
            # 注册内置规则族
            self.rule_engine.register_family(RegisterLevelsFamily())
            self.rule_engine.register_family(ExpressionBaseFamily())
            self.rule_engine.register_family(MedicalSyntaxRulesFamily())
            self.rule_engine.register_family(ThesisDerivationRulesFamily())
            # 注册适配器
            self.rule_engine.register_family(M5ComplianceAdapterFamily())
        
        # 转换规则族名称
        family_ids = None
        if families:
            family_map = {
                "register_levels": RuleFamilyId.REGISTER_LEVELS,
                "expression_base": RuleFamilyId.EXPRESSION_BASE,
                "medical_syntax_rules": RuleFamilyId.MEDICAL_SYNTAX_RULES,
                "thesis_derivation_rules": RuleFamilyId.THESIS_DERIVATION_RULES,
                "m5_compliance": RuleFamilyId.M5_COMPLIANCE,
            }
            family_ids = [family_map[f] for f in families if f in family_map]
        
        # 执行规则
        output = self.rule_engine.execute(content, family_ids)
        
        # 保存追踪结果
        self._last_rule_trace = {
            "families_executed": output.families_executed,
            "total_matched": output.total_matched,
            "total_failed": output.total_failed,
            "total_skipped": output.total_skipped,
            "total_errors": output.total_errors,
            "has_critical_failures": output.has_critical_failures,
            "overall_passed": output.overall_passed,
            "duration_ms": output.duration_ms,
            "traces": output.traces,
        }
        
        return self._last_rule_trace
    
    def run_gates_with_rules(
        self, 
        content: str, 
        enabled_gates: Optional[List[str]] = None
    ) -> QualityResult:
        """
        运行门禁检查（包含规则引擎）
        
        SP-6 Batch 6B: 扩展 run_gates_on_content 以包含规则执行
        
        Args:
            content: 待检查内容
            enabled_gates: 门禁列表
            
        Returns:
            QualityResult: 包含规则追踪的质量结果
        """
        # 执行原有门禁
        result = self.run_gates_on_content(content, enabled_gates)
        
        # 执行规则引擎
        rule_trace = self.run_rules(content)
        
        # 将规则追踪添加到结果中
        result.metadata["rule_trace"] = rule_trace
        
        # 如果规则检查发现严重问题，添加到错误中
        if rule_trace.get("has_critical_failures"):
            result.add_error("rules", "规则检查发现严重问题")
        elif not rule_trace.get("overall_passed", True):
            result.add_warning("rules", "规则检查发现问题")
        else:
            result.gates_passed.append("rules")
        
        return result