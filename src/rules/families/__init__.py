"""
Rules Families Package

SP-6 Batch 6B: 内置规则族
"""
from .register_levels import (
    RegisterLevelsFamily,
    RegisterLevel,
    BUILTIN_REGISTER_LEVELS,
)
from .expression_base import (
    ExpressionBaseFamily,
    get_expression_base_rules,
)
from .medical_syntax_rules import (
    MedicalSyntaxRulesFamily,
    get_medical_syntax_rules,
)
from .thesis_derivation_rules import (
    ThesisDerivationRulesFamily,
    get_thesis_derivation_rules,
)


def get_register_level_rules():
    """获取语体级别规则列表"""
    family = RegisterLevelsFamily()
    return family.get_rules()


__all__ = [
    # 规则族类
    "RegisterLevelsFamily",
    "ExpressionBaseFamily",
    "MedicalSyntaxRulesFamily",
    "ThesisDerivationRulesFamily",
    # 获取规则函数
    "get_register_level_rules",
    "get_expression_base_rules",
    "get_medical_syntax_rules",
    "get_thesis_derivation_rules",
    # 其他导出
    "RegisterLevel",
    "BUILTIN_REGISTER_LEVELS",
]