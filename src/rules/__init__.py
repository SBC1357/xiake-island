# Rules Module - 规则执行引擎
"""
SP-6 Batch 6B: 确定性规则执行引擎

职责:
- 加载和执行规则族
- 产出 rule-level trace (matched/failed/skipped/errors + reasons)
- 支持内置规则族和外部资产加载

核心规则族:
- register_levels: 语体级别规则
- expression_base: 通用表达规则
- medical_syntax_rules: 医学语法规则
- thesis_derivation_rules: 论点推导规则
- m5_compliance: 合规检查（适配器）

公开接口:
- RuleEngine: 规则执行引擎
- Rule, RuleResult, RuleTrace: 数据模型
- RuleLayerOutput: 规则层输出（用于区分规则层与模型层）
- RuleFamilyDefinition: 规则族定义基类

使用示例:
    from src.rules import RuleEngine, RuleFamilyId
    from src.rules.families import RegisterLevelsFamily
    
    engine = RuleEngine()
    engine.register_family(RegisterLevelsFamily())
    
    output = engine.execute(
        content="待检查内容",
        families=[RuleFamilyId.REGISTER_LEVELS]
    )
"""

# 数据模型
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

# 引擎
from .engine import (
    RuleEngine,
    RuleFamilyRegistry,
    create_pattern_checker,
    create_pattern_checker_with_matches,
)

# 内置规则族
from .families import (
    RegisterLevelsFamily,
    ExpressionBaseFamily,
    MedicalSyntaxRulesFamily,
    ThesisDerivationRulesFamily,
    get_register_level_rules,
    get_expression_base_rules,
    get_medical_syntax_rules,
    get_thesis_derivation_rules,
)

# 适配器
from .adapters import (
    M5ComplianceAdapterFamily,
    get_m5_compliance_rules,
)

__all__ = [
    # 数据模型
    "Rule",
    "RuleResult",
    "RuleTrace",
    "RuleFamilyOutput",
    "RuleLayerOutput",
    "RuleFamilyId",
    "RuleFamilyDefinition",
    "RuleStatus",
    "RuleSeverity",
    # 引擎
    "RuleEngine",
    "RuleFamilyRegistry",
    "create_pattern_checker",
    "create_pattern_checker_with_matches",
    # 内置规则族
    "RegisterLevelsFamily",
    "ExpressionBaseFamily",
    "MedicalSyntaxRulesFamily",
    "ThesisDerivationRulesFamily",
    "get_register_level_rules",
    "get_expression_base_rules",
    "get_medical_syntax_rules",
    "get_thesis_derivation_rules",
    # 适配器
    "M5ComplianceAdapterFamily",
    "get_m5_compliance_rules",
]