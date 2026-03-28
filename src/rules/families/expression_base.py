"""
Expression Base Rule Family

SP-6 Batch 6B: 通用表达规则族

检查内容中的:
- 禁用表达（不当用语）
- 推荐表达替换
- 常见表达问题
"""
from ..models import (
    Rule,
    RuleFamilyId,
    RuleFamilyDefinition,
    RuleSeverity,
)
from ..engine import create_pattern_checker


# 内置禁用表达列表
BUILTIN_FORBIDDEN_EXPRESSIONS = [
    # 绝对化表达
    ("绝对|肯定|必定|一定|必然", "避免绝对化表达", "建议使用'可能''或许'等留有余地的表达"),
    # 主观判断
    ("我觉得|我认为|依我看|在我看来", "避免主观判断表达", "建议使用客观陈述或引用权威来源"),
    # 模糊表达
    ("有些东西|某些方面|各个方面", "避免模糊表达", "建议使用具体、明确的描述"),
    # 口语化连接词
    ("然后然后|就是就是|那个那个", "避免重复口语化连接词", "建议精简表达或使用书面连接词"),
    # 夸张表达
    ("极其|无比|超级超级|特别特别", "避免夸张表达", "建议使用更客观的程度描述"),
]

# 内置建议替换表达
BUILTIN_EXPRESSION_SUBSTITUTIONS = [
    ("很多的时候", "通常情况下", "表达更正式"),
    ("一般来说", "通常", "表达更简洁"),
    ("基本上", "总体上", "表达更准确"),
    ("差不多", "约", "表达更精确"),
]


class ExpressionBaseFamily(RuleFamilyDefinition):
    """
    通用表达规则族
    
    检查内容中不当的表达使用。
    """
    
    def get_family_id(self) -> RuleFamilyId:
        return RuleFamilyId.EXPRESSION_BASE
    
    def get_rules(self) -> list[Rule]:
        """返回规则列表"""
        rules: list[Rule] = []
        
        # 禁用表达规则
        for i, (pattern, description, suggestion) in enumerate(BUILTIN_FORBIDDEN_EXPRESSIONS):
            rule = Rule(
                rule_id=f"EXPR_FORBIDDEN_{i:03d}",
                family=RuleFamilyId.EXPRESSION_BASE,
                name=f"禁用表达检查: {description}",
                description=description,
                severity=RuleSeverity.MEDIUM,
                checker=create_pattern_checker(pattern, "regex"),
                on_match=f"发现禁用表达: {description}",
                on_fail="未发现该类禁用表达",
                suggestion=suggestion
            )
            rules.append(rule)
        
        # 建议替换规则（低严重度）
        for i, (original, suggested, reason) in enumerate(BUILTIN_EXPRESSION_SUBSTITUTIONS):
            def make_checker(orig: str):
                return lambda content: orig in content
            
            rule = Rule(
                rule_id=f"EXPR_SUGGEST_{i:03d}",
                family=RuleFamilyId.EXPRESSION_BASE,
                name=f"表达建议: '{original}' -> '{suggested}'",
                description=f"建议将 '{original}' 替换为 '{suggested}'",
                severity=RuleSeverity.LOW,
                checker=make_checker(original),
                on_match=f"发现可优化表达: '{original}'",
                on_fail="未发现该表达",
                suggestion=f"建议替换为 '{suggested}' ({reason})"
            )
            rules.append(rule)
        
        # 常见错误表达
        common_errors = [
            ("做出了贡献", "做出了贡献 -> 做出了贡献/贡献了", "语法优化"),
            ("进行了一次", "进行了一次 -> 进行了/做了", "冗余表达"),
            ("对此进行", "对此进行 -> 对此", "冗余表达"),
        ]
        
        for i, (pattern, description, reason) in enumerate(common_errors):
            rule = Rule(
                rule_id=f"EXPR_COMMON_ERROR_{i:03d}",
                family=RuleFamilyId.EXPRESSION_BASE,
                name=f"常见表达问题: {pattern}",
                description=description,
                severity=RuleSeverity.INFO,
                checker=lambda content, p=pattern: p in content,
                on_match=f"发现常见表达问题: {pattern}",
                on_fail="未发现该常见问题",
                suggestion=f"建议优化 ({reason})"
            )
            rules.append(rule)
        
        return rules


# 辅助函数
def get_expression_base_rules() -> list[Rule]:
    """获取通用表达规则列表"""
    family = ExpressionBaseFamily()
    return family.get_rules()


__all__ = [
    "ExpressionBaseFamily",
    "BUILTIN_FORBIDDEN_EXPRESSIONS",
    "BUILTIN_EXPRESSION_SUBSTITUTIONS",
    "get_expression_base_rules",
]