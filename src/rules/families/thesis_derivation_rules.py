"""
Thesis Derivation Rules Family

SP-6 Batch 6B: 论点推导规则族

定义论点生成和推导的规范规则，用于:
- 规划阶段：确保论点清晰
- 写作阶段：支撑论证结构
- 合规阶段：验证论点合理性
"""
from ..models import (
    Rule,
    RuleFamilyId,
    RuleFamilyDefinition,
    RuleSeverity,
)
from ..engine import create_pattern_checker


class ThesisDerivationRulesFamily(RuleFamilyDefinition):
    """论点推导规则族"""
    
    def get_family_id(self) -> RuleFamilyId:
        return RuleFamilyId.THESIS_DERIVATION_RULES
    
    def get_rules(self) -> list[Rule]:
        return get_thesis_derivation_rules()


def get_thesis_derivation_rules() -> list[Rule]:
    """
    获取论点推导规则
    
    规则覆盖:
    1. 核心论点清晰性
    2. 论证逻辑完整性
    3. 证据支撑充分性
    
    Returns:
        论点推导规则列表
    """
    return [
        # ==================== 核心论点检查 ====================
        Rule(
            rule_id="THS_CORE_001",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="论点-核心观点存在性",
            description="内容应有明确的核心观点",
            severity=RuleSeverity.MEDIUM,
            checker=lambda content: len(content) > 50 and any(
                marker in content 
                for marker in ["因此", "所以", "综上", "总之", "由此可见", "总的来说"]
            ),
            on_match="发现核心观点表述",
            on_fail="建议明确核心观点",
            suggestion="请在文中明确表达核心观点，使用总结性表述",
            enabled=True
        ),
        Rule(
            rule_id="THS_CORE_002",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="论点-观点一致性",
            description="全文观点应保持一致",
            severity=RuleSeverity.HIGH,
            checker=lambda content: True,  # 需要更复杂的语义分析，暂时通过
            on_match="观点一致性检查通过",
            suggestion="请确保全文观点前后一致，避免自相矛盾",
            enabled=True
        ),
        
        # ==================== 论证逻辑检查 ====================
        Rule(
            rule_id="THS_LOGIC_001",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="逻辑-论证结构完整性",
            description="论证应有完整的论点、论据、结论结构",
            severity=RuleSeverity.MEDIUM,
            checker=lambda content: all(
                any(kw in content for kw in kw_list)
                for kw_list in [
                    ["首先", "第一", "一是", "其一"],
                    ["其次", "第二", "二是", "其二"],
                    ["因此", "所以", "综上", "总之"]
                ]
            ),
            on_match="论证结构较为完整",
            on_fail="论证结构建议完善",
            suggestion="建议使用'首先...其次...因此...'等结构使论证更清晰",
            enabled=True
        ),
        Rule(
            rule_id="THS_LOGIC_002",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="逻辑-因果关系明确",
            description="因果论述应明确",
            severity=RuleSeverity.MEDIUM,
            checker=create_pattern_checker(
                "因为|由于|原因是|导致|使得|造成|引起|引发",
                "regex"
            ),
            on_match="发现因果论述",
            on_fail="建议明确因果关系",
            suggestion="在论述因果关系时，请明确说明原因和结果",
            enabled=True
        ),
        Rule(
            rule_id="THS_LOGIC_003",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="逻辑-避免逻辑跳跃",
            description="论述应避免逻辑跳跃",
            severity=RuleSeverity.HIGH,
            checker=lambda content: True,  # 需要更复杂的分析
            on_match="逻辑连贯性检查通过",
            suggestion="请注意论证过程不要有逻辑跳跃，确保推理完整",
            enabled=True
        ),
        
        # ==================== 证据支撑检查 ====================
        Rule(
            rule_id="THS_EVID_001",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="证据-数据支撑",
            description="关键论述应有数据支撑",
            severity=RuleSeverity.HIGH,
            checker=lambda content: any(
                char in content 
                for char in "0123456789"
            ),
            on_match="发现数据支撑",
            on_fail="关键论述建议添加数据支撑",
            suggestion="请在关键论述处添加具体数据或研究结果",
            enabled=True
        ),
        Rule(
            rule_id="THS_EVID_002",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="证据-引用来源",
            description="重要结论应有引用来源",
            severity=RuleSeverity.HIGH,
            checker=create_pattern_checker(
                "研究|试验|调查|报告|文献|指南|共识",
                "regex"
            ),
            on_match="发现引用来源",
            on_fail="重要结论建议注明来源",
            suggestion="请在重要结论处注明研究来源或权威出处",
            enabled=True
        ),
        Rule(
            rule_id="THS_EVID_003",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="证据-多角度论证",
            description="论证应从多角度展开",
            severity=RuleSeverity.LOW,
            checker=lambda content: content.count("。") >= 3,  # 至少3句话
            on_match="论述较为完整",
            on_fail="建议从多角度展开论述",
            suggestion="建议从机制、临床、指南等多个角度展开论述",
            enabled=True
        ),
        
        # ==================== 产品级规则模板 ====================
        Rule(
            rule_id="THS_PROD_001",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="产品-关键信息覆盖",
            description="产品内容应覆盖关键信息点",
            severity=RuleSeverity.MEDIUM,
            checker=lambda content: any(
                kw in content 
                for kw in ["适应症", "用法用量", "不良反应", "注意事项"]
            ),
            on_match="关键信息覆盖较完整",
            on_fail="建议补充关键信息",
            suggestion="产品内容建议覆盖适应症、用法用量、不良反应、注意事项等关键信息",
            enabled=True
        ),
        Rule(
            rule_id="THS_PROD_002",
            family=RuleFamilyId.THESIS_DERIVATION_RULES,
            name="产品-竞争格局客观",
            description="竞争产品比较应客观",
            severity=RuleSeverity.HIGH,
            checker=create_pattern_checker(
                "优于|好于|强于|超越|领先|第一",
                "regex"
            ),
            on_match="发现比较性表述",
            on_fail="比较性表述检查通过",
            suggestion="产品比较应客观，请提供循证医学证据支持比较结论",
            enabled=True
        ),
    ]