"""
Medical Syntax Rules Family

SP-6 Batch 6B: 医学语法规则族

检查医学内容中的:
- 医学术语使用规范
- 具名归因要求
- 临床落地的表达要求
"""
from ..models import (
    Rule,
    RuleFamilyId,
    RuleFamilyDefinition,
    RuleSeverity,
)
from ..engine import create_pattern_checker


# 医学术语规范
MEDICAL_TERMINOLOGY_RULES = [
    # 术语准确性
    ("高血压病|糖尿病病", "避免重复'病'字", "建议使用'高血压'或'糖尿病'"),
    ("抗菌素", "术语更新", "建议使用'抗生素'"),
    ("抗菌药|抗细菌药", "术语规范", "建议使用'抗菌药物'"),
]

# 具名归因规则
NAMED_ATTRIBUTION_RULES = [
    # 需要引用来源的表达
    ("研究表明|研究显示|研究发现", "需要具名归因", "请标注具体研究来源"),
    ("专家指出|专家认为|专家建议", "需要具名归因", "请标注具体专家姓名和单位"),
    ("据统计|数据显示", "需要具名归因", "请标注具体数据来源"),
]

# 临床落地表达
CLINICAL_LANDING_RULES = [
    # 患者指导应具体可操作
    ("定期复查|定期随访|定期检查", "临床落地", "建议明确具体时间间隔，如'每3个月复查一次'"),
    ("适量运动|适度运动|适当运动", "临床落地", "建议明确具体运动类型和时长"),
    ("注意饮食|合理饮食|健康饮食", "临床落地", "建议明确具体饮食建议"),
]

# 禁用表达
FORBIDDEN_MEDICAL_EXPRESSIONS = [
    # 疗效保证
    ("保证治愈|保证有效|包治", "严重", "禁止疗效保证"),
    # 夸大宣传
    ("最新突破|革命性|颠覆性|奇迹", "严重", "禁止夸大宣传"),
    # 不实对比
    ("远胜于|秒杀|完胜|吊打", "严重", "禁止不实对比"),
]


class MedicalSyntaxRulesFamily(RuleFamilyDefinition):
    """
    医学语法规则族
    
    SP-6 Batch 6B 必须规则族:
    检查医学内容的术语规范、归因要求和临床落地表达。
    """
    
    def get_family_id(self) -> RuleFamilyId:
        return RuleFamilyId.MEDICAL_SYNTAX_RULES
    
    def get_rules(self) -> list[Rule]:
        """返回规则列表"""
        rules: list[Rule] = []
        
        # 医学术语规范规则
        for i, (pattern, description, suggestion) in enumerate(MEDICAL_TERMINOLOGY_RULES):
            rule = Rule(
                rule_id=f"MED_TERM_{i:03d}",
                family=RuleFamilyId.MEDICAL_SYNTAX_RULES,
                name=f"医学术语规范: {description}",
                description=description,
                severity=RuleSeverity.LOW,
                checker=create_pattern_checker(pattern, "regex"),
                on_match=f"发现术语问题: {description}",
                on_fail="术语使用规范",
                suggestion=suggestion
            )
            rules.append(rule)
        
        # 具名归因规则
        for i, (pattern, description, suggestion) in enumerate(NAMED_ATTRIBUTION_RULES):
            rule = Rule(
                rule_id=f"MED_ATTR_{i:03d}",
                family=RuleFamilyId.MEDICAL_SYNTAX_RULES,
                name=f"具名归因检查: {description}",
                description=description,
                severity=RuleSeverity.MEDIUM,
                checker=create_pattern_checker(pattern, "regex"),
                on_match=f"发现需要归因的表达: {description}",
                on_fail="归因完整",
                suggestion=suggestion
            )
            rules.append(rule)
        
        # 临床落地规则
        for i, (pattern, description, suggestion) in enumerate(CLINICAL_LANDING_RULES):
            rule = Rule(
                rule_id=f"MED_CLINICAL_{i:03d}",
                family=RuleFamilyId.MEDICAL_SYNTAX_RULES,
                name=f"临床落地检查: {description}",
                description=description,
                severity=RuleSeverity.MEDIUM,
                checker=create_pattern_checker(pattern, "regex"),
                on_match=f"发现模糊表达: {description}",
                on_fail="表达具体可操作",
                suggestion=suggestion
            )
            rules.append(rule)
        
        # 禁用表达规则（高严重度）
        for i, (pattern, severity, description) in enumerate(FORBIDDEN_MEDICAL_EXPRESSIONS):
            severity_level = RuleSeverity.CRITICAL if severity == "严重" else RuleSeverity.HIGH
            rule = Rule(
                rule_id=f"MED_FORBIDDEN_{i:03d}",
                family=RuleFamilyId.MEDICAL_SYNTAX_RULES,
                name=f"禁用表达: {description}",
                description=description,
                severity=severity_level,
                checker=create_pattern_checker(pattern, "regex"),
                on_match=f"发现禁用表达: {description}",
                on_fail="未发现禁用表达",
                suggestion=f"请删除或修改该表达: {description}"
            )
            rules.append(rule)
        
        return rules


# 辅助函数
def get_medical_syntax_rules() -> list[Rule]:
    """获取医学语法规则列表"""
    family = MedicalSyntaxRulesFamily()
    return family.get_rules()


__all__ = [
    "MedicalSyntaxRulesFamily",
    "MEDICAL_TERMINOLOGY_RULES",
    "NAMED_ATTRIBUTION_RULES",
    "CLINICAL_LANDING_RULES",
    "FORBIDDEN_MEDICAL_EXPRESSIONS",
    "get_medical_syntax_rules",
]