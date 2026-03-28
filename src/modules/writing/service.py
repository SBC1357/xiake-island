"""
Writing Service

写作生成服务，实现 V2 PromptCompiler 逻辑。

SP-6 Batch 6C: 新增 compile_with_trace 方法，返回带追踪的编译结果。
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .models import CompiledPrompt, WritingTrace, PlanningConstraintsTrace, EvidenceAnchor, CompiledPromptWithTrace


@dataclass
class WritingService:
    """
    写作服务
    
    实现与 V2 PromptCompiler 兼容的编译逻辑。
    """
    base_system_prompt: str = "你是一个医学写作助手。"
    
    def compile(
        self,
        thesis: str,
        outline: List[Dict[str, Any]],
        play_id: Optional[str] = None,
        arc_id: Optional[str] = None,
        target_audience: Optional[str] = None,
        key_evidence: Optional[List[str]] = None,
        style_notes: Optional[Dict[str, Any]] = None
    ) -> CompiledPrompt:
        """
        编译 prompt
        
        Args:
            thesis: 核心论点
            outline: 文章大纲
            play_id: 写作策略ID
            arc_id: 叙事弧线ID
            target_audience: 目标受众
            key_evidence: 核心证据
            style_notes: 风格注释
            
        Returns:
            CompiledPrompt: 编译后的 prompt
        """
        # 构建编辑计划风格的参数
        plan_dict = {
            "thesis": thesis,
            "outline": outline,
            "play_id": play_id,
            "arc_id": arc_id,
            "target_audience": target_audience,
            "key_evidence": key_evidence or [],
            "style_notes": style_notes or {}
        }
        
        system_prompt = self._build_system_prompt(plan_dict)
        user_prompt = self._build_user_prompt(plan_dict)
        
        return CompiledPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_config=self._build_model_config(plan_dict),
            metadata={
                "play_id": play_id,
                "arc_id": arc_id,
                "thesis": thesis
            }
        )
    
    def compile_with_evidence(
        self,
        thesis: str,
        outline: List[Dict[str, Any]],
        evidence_facts: List[Dict[str, Any]],
        play_id: Optional[str] = None,
        arc_id: Optional[str] = None,
        target_audience: Optional[str] = None,
        style_notes: Optional[Dict[str, Any]] = None,
        target_word_count: Optional[int] = None
    ) -> CompiledPrompt:
        """
        编译带详细证据的 prompt
        """
        plan_dict = {
            "thesis": thesis,
            "outline": outline,
            "play_id": play_id,
            "arc_id": arc_id,
            "target_audience": target_audience,
            "style_notes": style_notes or {},
            "target_word_count": target_word_count,
        }
        
        system_prompt = self._build_system_prompt(plan_dict)
        user_prompt = self._build_user_prompt_with_evidence(plan_dict, evidence_facts)
        
        return CompiledPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_config=self._build_model_config(plan_dict),
            metadata={
                "play_id": play_id,
                "arc_id": arc_id,
                "thesis": thesis,
                "fact_count": len(evidence_facts)
            }
        )
    
    def compile_with_trace(
        self,
        thesis: str,
        outline: List[Dict[str, Any]],
        evidence_facts: List[Dict[str, Any]],
        play_id: Optional[str] = None,
        arc_id: Optional[str] = None,
        target_audience: Optional[str] = None,
        style_notes: Optional[Dict[str, Any]] = None,
        target_word_count: Optional[int] = None
    ) -> CompiledPromptWithTrace:
        """
        编译带追踪的 prompt
        
        SP-6 Batch 6C: 返回编译结果和写作追踪信息。
        
        Args:
            thesis: 核心论点
            outline: 文章大纲
            evidence_facts: 证据事实列表
            play_id: 写作策略ID
            arc_id: 叙事弧线ID
            target_audience: 目标受众
            style_notes: 风格注释
            target_word_count: 目标字数
            
        Returns:
            CompiledPromptWithTrace: 带追踪的编译结果
        """
        # 先编译 prompt
        prompt = self.compile_with_evidence(
            thesis=thesis,
            outline=outline,
            evidence_facts=evidence_facts,
            play_id=play_id,
            arc_id=arc_id,
            target_audience=target_audience,
            style_notes=style_notes,
            target_word_count=target_word_count,
        )
        
        # 构建规划约束追踪
        planning_constraints = PlanningConstraintsTrace(
            thesis=thesis,
            outline=outline,
            register=style_notes.get("register") if style_notes else None,
            audience=target_audience,
            style_notes=style_notes or {},
            target_word_count=target_word_count
        )
        
        # 构建证据锚点
        evidence_anchors = self._build_evidence_anchors(outline, evidence_facts)
        
        # 构写作追踪
        trace = WritingTrace(
            planning_constraints=planning_constraints,
            evidence_anchors=evidence_anchors,
            applied_rule_ids=self._get_applied_rule_ids(play_id, arc_id),
            applied_style_ids=self._get_applied_style_ids(style_notes),
            hard_constraints=self._get_hard_constraints(style_notes),
            advisory_constraints=self._get_advisory_constraints(style_notes)
        )
        
        return CompiledPromptWithTrace(prompt=prompt, trace=trace)
    
    def _build_evidence_anchors(
        self,
        outline: List[Dict[str, Any]],
        evidence_facts: List[Dict[str, Any]]
    ) -> List[EvidenceAnchor]:
        """构建证据锚点列表"""
        anchors = []
        
        # 按 domain 分组证据
        by_domain: Dict[str, List[Dict[str, Any]]] = {}
        for fact in evidence_facts:
            domain = fact.get('domain', 'unknown')
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(fact)
        
        # 为大纲中的 domain_section 创建锚点
        for idx, section in enumerate(outline):
            if section.get('type') == 'domain_section':
                domain = section.get('domain')
                if domain and domain in by_domain:
                    facts = by_domain[domain]
                    anchors.append(EvidenceAnchor(
                        section_index=idx,
                        section_title=section.get('title', ''),
                        fact_ids=[f.get('fact_id', '') for f in facts],
                        domains=[domain]
                    ))
        
        return anchors
    
    def _get_applied_rule_ids(self, play_id: Optional[str], arc_id: Optional[str]) -> List[str]:
        """获取应用的规则ID"""
        rule_ids = []
        if play_id:
            rule_ids.append(f"play:{play_id}")
        if arc_id:
            rule_ids.append(f"arc:{arc_id}")
        return rule_ids
    
    def _get_applied_style_ids(self, style_notes: Optional[Dict[str, Any]]) -> List[str]:
        """获取应用的风格ID"""
        style_ids = []
        if style_notes:
            if style_notes.get('register'):
                style_ids.append(f"register:{style_notes['register']}")
            if style_notes.get('formality'):
                style_ids.append(f"formality:{style_notes['formality']}")
        return style_ids
    
    def _get_hard_constraints(self, style_notes: Optional[Dict[str, Any]]) -> List[str]:
        """获取硬性约束"""
        constraints = []
        if style_notes:
            register = style_notes.get('register', '')
            if register in ['R1', 'R2']:
                constraints.append("formal_language_required")
                constraints.append("no_colloquialisms")
        return constraints
    
    def _get_advisory_constraints(self, style_notes: Optional[Dict[str, Any]]) -> List[str]:
        """获取建议性约束"""
        constraints = []
        if style_notes:
            register = style_notes.get('register', '')
            if register in ['R3', 'R4']:
                constraints.append("accessible_language_preferred")
        return constraints
    
    def _build_system_prompt(self, plan: Dict[str, Any]) -> str:
        """构建系统 prompt"""
        target_wc = plan.get("target_word_count")
        word_count_line = (
            f"目标篇幅: {target_wc} 字（允许浮动 ±10%，结构须与篇幅匹配，证据不足时收缩结构而非泛化扩写）"
            if target_wc else ""
        )
        lines = [
            self.base_system_prompt,
            "",
            f"写作策略: {plan.get('play_id') or '未指定'}",
            f"叙事弧线: {plan.get('arc_id') or '未指定'}",
            f"目标受众: {plan.get('target_audience') or '未指定'}",
        ]
        if word_count_line:
            lines.append(word_count_line)
        
        style_notes = plan.get('style_notes', {})
        if style_notes:
            lines.extend([
                "",
                "风格要求:",
                f"- 语体等级: {style_notes.get('register', '未指定')}",
                f"- 正式程度: {style_notes.get('formality', '未指定')}",
            ])
        
        return "\n".join(lines)
    
    def _build_user_prompt(self, plan: Dict[str, Any]) -> str:
        """构建用户 prompt"""
        lines = [
            f"主题: {plan.get('thesis', '未指定')}",
            "",
            "大纲:",
        ]
        
        outline = plan.get('outline', [])
        for i, section in enumerate(outline, 1):
            title = section.get('title', '未命名章节')
            if section.get('type') == 'domain_section':
                title = f"{title} ({section.get('fact_count', 0)}条证据)"
            lines.append(f"{i}. {title}")
        
        key_evidence = plan.get('key_evidence', [])
        if key_evidence:
            lines.extend([
                "",
                "核心证据:",
            ])
            for evidence in key_evidence:
                lines.append(f"- {evidence}")
        
        lines.extend([
            "",
            "请根据以上信息生成文章。"
        ])
        
        return "\n".join(lines)
    
    def _build_user_prompt_with_evidence(
        self,
        plan: Dict[str, Any],
        evidence_facts: List[Dict[str, Any]]
    ) -> str:
        """构建包含详细证据的用户 prompt"""
        lines = [
            f"主题: {plan.get('thesis', '未指定')}",
            "",
            "大纲:",
        ]
        
        outline = plan.get('outline', [])
        for i, section in enumerate(outline, 1):
            lines.append(f"{i}. {section.get('title', '未命名章节')}")
        
        if evidence_facts:
            lines.extend([
                "",
                "证据详情:",
                ""
            ])
            
            # 按 domain 分组
            by_domain: Dict[str, List[Any]] = {}
            for fact in evidence_facts:
                domain = fact.get('domain', 'unknown')
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(fact)
            
            for domain, facts in by_domain.items():
                lines.append(f"【{domain}】")
                for fact in facts[:3]:  # 每个 domain 最多3条
                    value_str = f"{fact.get('value', '')} {fact.get('unit', '')}".strip()
                    definition = fact.get('definition') or fact.get('definition_zh') or fact.get('fact_key', '')
                    lines.append(f"- {definition}: {value_str}")
                lines.append("")
                
            # 注入写作边界约束
            ceilings = set()
            for fact in evidence_facts:
                bt = fact.get("boundary_tags", {})
                cc = bt.get("claim_ceiling")
                if cc:
                    ceilings.add(cc)
            
            if ceilings:
                lines.extend(["", "【写作边界约束】"])
                if "method_only" in ceilings:
                    lines.append("- 本文献涉及方法学事实：仅支持方法学结论描述，不得出现临床获益/疗效表述")
                if "mechanistic_signal" in ceilings:
                    lines.append("- 本文献涉及相关机制的探讨：仅支持机制信号描述，不得外推至人体临床结论")
                if "clinical_association" in ceilings:
                    lines.append("- 本文献涉及相关性研究：仅支持相关性表述，不得使用因果/获益措辞")
                if "clinical_outcome" in ceilings:
                    lines.append("- 本文献涉及临床结局：允许正常写疗效")
                if "guideline_recommendation" in ceilings:
                    lines.append("- 本文献涉及指南推荐：允许引用指南推荐级别")
                lines.append("")
        
        target_wc = plan.get("target_word_count")
        if target_wc:
            lines.extend([
                f"请根据以上信息生成文章，目标字数约 {target_wc} 字（±10%），"
                "结构须与篇幅相匹配，避免泛化扩写。"
            ])
        else:
            lines.extend([
                "请根据以上信息生成文章。"
            ])
        
        return "\n".join(lines)
    
    def _build_model_config(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """构建模型配置"""
        base_config = {
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        style_notes = plan.get('style_notes', {})
        if style_notes:
            register = style_notes.get('register', '')
            if register in ['R1', 'R2']:
                base_config['temperature'] = 0.5
            elif register in ['R4', 'R5']:
                base_config['temperature'] = 0.8
        
        return base_config