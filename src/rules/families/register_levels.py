"""
Register Levels Rule Family

SP-6 Batch 6B: 语体级别规则族

根据不同的 register（语体级别）检查内容是否符合相应的语体约束。
- academic: 学术语体，严谨、正式
- professional: 专业语体，专业但通俗
- popular: 科普语体，通俗易懂
- patient: 患者语体，亲切、温和
"""
from typing import Optional
from dataclasses import dataclass

from ..models import (
    Rule,
    RuleFamilyId,
    RuleFamilyDefinition,
    RuleSeverity,
)
from ..engine import create_pattern_checker


@dataclass
class RegisterLevel:
    """语体级别定义"""
    name: str
    description: str
    forbidden_patterns: list[str]  # 禁止使用的表达
    required_patterns: list[str]   # 建议使用的表达
    tone_hints: list[str]          # 语调提示


# 内置语体级别定义
BUILTIN_REGISTER_LEVELS: dict[str, RegisterLevel] = {
    "academic": RegisterLevel(
        name="学术语体",
        description="适用于学术论文、研究报告，严谨正式",
        forbidden_patterns=[
            "你|您|咱们",  # 避免第一/第二人称
            "非常|特别|超级",  # 避免口语化程度副词
            "真的|确实|实在",  # 避免主观强调
        ],
        required_patterns=[],
        tone_hints=["客观", "严谨", "正式", "引用文献"]
    ),
    "professional": RegisterLevel(
        name="专业语体",
        description="适用于专业文章，专业但相对通俗",
        forbidden_patterns=[
            "超级|特别特别|巨",  # 避免过度口语化
            "神|绝了|牛",  # 避免网络用语
        ],
        required_patterns=[],
        tone_hints=["专业", "准确", "适度通俗"]
    ),
    "popular": RegisterLevel(
        name="科普语体",
        description="适用于科普文章，通俗易懂",
        forbidden_patterns=[
            "众所周知",  # 避免假设读者已知
        ],
        required_patterns=[],
        tone_hints=["通俗", "生动", "有趣", "类比"]
    ),
    "patient": RegisterLevel(
        name="患者语体",
        description="适用于患者教育材料，亲切温和",
        forbidden_patterns=[
            "必须|一定|千万",  # 避免命令式
            "否则后果自负",  # 避免恐吓
        ],
        required_patterns=[],
        tone_hints=["亲切", "温和", "鼓励", "安慰"]
    ),
}


class RegisterLevelsFamily(RuleFamilyDefinition):
    """
    语体级别规则族
    
    检查内容是否符合指定语体的约束。
    """
    
    def __init__(self):
        self._context_register: Optional[str] = None
    
    def get_family_id(self) -> RuleFamilyId:
        return RuleFamilyId.REGISTER_LEVELS
    
    def set_register(self, register: str) -> None:
        """设置当前语体上下文"""
        self._context_register = register
    
    def get_rules(self) -> list[Rule]:
        """返回规则列表"""
        rules: list[Rule] = []
        
        # 规则：检查禁止表达
        for register_name, register_level in BUILTIN_REGISTER_LEVELS.items():
            for i, pattern in enumerate(register_level.forbidden_patterns):
                checker = create_pattern_checker(pattern, "regex")
                
                def make_condition(reg_name: str):
                    def condition(content: str) -> bool:
                        return self._context_register == reg_name
                    return condition
                
                rule = Rule(
                    rule_id=f"REG_{register_name.upper()}_FORBIDDEN_{i:02d}",
                    family=RuleFamilyId.REGISTER_LEVELS,
                    name=f"{register_level.name}禁止表达检查",
                    description=f"检查 {register_level.name} 是否使用了禁止表达: {pattern}",
                    severity=RuleSeverity.MEDIUM,
                    checker=checker,
                    condition=make_condition(register_name),
                    on_match=f"发现 {register_level.name} 禁止使用的表达",
                    on_fail="未发现禁止表达",
                    suggestion=f"建议修改以符合 {register_level.name} 的语体要求"
                )
                rules.append(rule)
        
        # 通用规则：检查口语化程度
        colloquial_patterns = "超级|特别特别|巨|贼|那叫一个"
        rules.append(Rule(
            rule_id="REG_COLLOQUIAL_CHECK",
            family=RuleFamilyId.REGISTER_LEVELS,
            name="口语化程度检查",
            description="检查内容是否过度口语化",
            severity=RuleSeverity.LOW,
            checker=create_pattern_checker(colloquial_patterns, "regex"),
            on_match="发现过度口语化表达",
            on_fail="口语化程度适当",
            suggestion="建议使用更正式的表达方式"
        ))
        
        return rules


# 辅助函数
def get_register_level_rules() -> list[Rule]:
    """获取语体级别规则列表"""
    family = RegisterLevelsFamily()
    return family.get_rules()


# 导出
__all__ = [
    "RegisterLevelsFamily",
    "RegisterLevel",
    "BUILTIN_REGISTER_LEVELS",
    "get_register_level_rules",
]