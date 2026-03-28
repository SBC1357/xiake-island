"""
Planning Service

选题/规划服务，实现 V2 EditorialPlanner 逻辑。
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .models import RouteContext, EditorialPlan, PersonaProfile


@dataclass
class PlanningService:
    """
    规划服务
    
    实现与 V2 EditorialPlanner 兼容的规划逻辑。
    """
    config: Dict[str, Any] = field(default_factory=dict)
    
    def plan(
        self,
        context: RouteContext,
        evidence_facts: Optional[List[Dict[str, Any]]] = None,
        selected_facts: Optional[List[str]] = None
    ) -> EditorialPlan:
        """
        生成编辑计划
        
        Args:
            context: 路由上下文
            evidence_facts: 证据事实列表 (V2 fact_records 格式)
            selected_facts: 选中的证据ID列表
            
        Returns:
            EditorialPlan: 编辑计划
        """
        thesis = self._build_thesis(context, evidence_facts)
        outline = self._build_outline(context, evidence_facts, selected_facts)
        play_id = self._select_play(context)
        arc_id = self._select_arc(context, evidence_facts)
        
        key_evidence = selected_facts[:5] if selected_facts else []
        
        # SP-6 Batch 6C: 从 context.metadata 获取 target_word_count
        target_word_count = context.metadata.get("target_word_count") if context.metadata else None
        
        # 方案六: 章节篇幅分配
        section_word_budget = self._allocate_word_budget(outline, target_word_count)
        
        return EditorialPlan(
            thesis=thesis,
            outline=outline,
            play_id=play_id,
            arc_id=arc_id,
            target_audience=context.audience,
            key_evidence=key_evidence,
            style_notes=self._build_style_notes(context),
            target_word_count=target_word_count,
            section_word_budget=section_word_budget,
        )
    
    def _build_thesis(
        self,
        context: RouteContext,
        evidence_facts: Optional[List[Dict[str, Any]]]
    ) -> str:
        """构建核心论点"""
        if evidence_facts:
            domains = set(f.get("domain") for f in evidence_facts if f.get("domain"))
            if domains:
                domain_str = "、".join(list(domains)[:2])
                return f"关于{context.product_id}的{domain_str}分析"
        
        return f"关于{context.product_id}的医学写作"
    
    def _build_outline(
        self,
        context: RouteContext,
        evidence_facts: Optional[List[Dict[str, Any]]],
        selected_facts: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """构建文章大纲"""
        outline = [{"title": "引言", "type": "intro"}]
        
        if evidence_facts:
            # 按 domain 分组
            by_domain: Dict[str, List[Any]] = {}
            for fact in evidence_facts:
                domain = fact.get("domain")
                if domain:
                    if domain not in by_domain:
                        by_domain[domain] = []
                    by_domain[domain].append(fact)
            
            # 为每个 domain 创建章节
            for domain, facts in by_domain.items():
                outline.append({
                    "title": self._domain_to_title(domain),
                    "type": "domain_section",
                    "domain": domain,
                    "fact_count": len(facts)
                })
        elif selected_facts:
            # 降级：使用 selected_facts
            for fact_id in selected_facts[:3]:
                outline.append({
                    "title": f"章节: {fact_id}",
                    "type": "evidence",
                    "fact_id": fact_id
                })
        
        outline.append({"title": "结论", "type": "conclusion"})
        
        return outline
    
    def _domain_to_title(self, domain: str) -> str:
        """将 domain 转换为中文标题"""
        domain_titles = {
            "efficacy": "疗效分析",
            "safety": "安全性评估",
            "biomarker": "生物标志物",
            "moa": "作用机制",
            "trial_design": "试验设计",
            "competitor": "竞品对比"
        }
        return domain_titles.get(domain, domain.title())
    
    def _select_play(self, context: RouteContext) -> str:
        """选择写作策略"""
        play_map = {
            "R1": "academic",
            "R2": "professional",
            "R3": "clinical",
            "R4": "patient",
            "R5": "casual"
        }
        return play_map.get(context.register, "standard")
    
    def _select_arc(
        self,
        context: RouteContext,
        evidence_facts: Optional[List[Dict[str, Any]]]
    ) -> str:
        """选择叙事弧线"""
        if evidence_facts and len(evidence_facts) > 5:
            return "evidence_rich"
        return "evidence_driven"
    
    def _build_style_notes(self, context: RouteContext) -> Dict[str, Any]:
        """构建风格注释"""
        return {
            "register": context.register,
            "formality": self._register_to_formality(context.register)
        }
    
    def _register_to_formality(self, register: str) -> str:
        """语体等级转正式程度"""
        mapping = {
            "R1": "highly_formal",
            "R2": "formal",
            "R3": "semi_formal",
            "R4": "informal",
            "R5": "casual"
        }
        return mapping.get(register, "neutral")
    
    def _allocate_word_budget(
        self,
        outline: List[Dict[str, Any]],
        target_word_count: Optional[int],
    ) -> Optional[List[Dict[str, Any]]]:
        """
        根据大纲结构分配章节篇幅。
        
        分配策略：
        - 引言: 10%
        - 结论: 10%
        - 主体章节: 平分剩余 80%，按证据数量加权
        
        Returns:
            篇幅分配列表，每项含 section_title、target_words、ratio；无目标字数时返回 None
        """
        if not target_word_count or not outline:
            return None
        
        budget: List[Dict[str, Any]] = []
        body_sections = []
        
        for section in outline:
            sec_type = section.get("type", "section")
            if sec_type == "intro":
                ratio = 0.10
                budget.append({
                    "section_title": section.get("title", "引言"),
                    "target_words": int(target_word_count * ratio),
                    "ratio": ratio,
                })
            elif sec_type == "conclusion":
                ratio = 0.10
                budget.append({
                    "section_title": section.get("title", "结论"),
                    "target_words": int(target_word_count * ratio),
                    "ratio": ratio,
                })
            else:
                body_sections.append(section)
        
        # 主体部分占 80%，按 fact_count 加权
        body_total = int(target_word_count * 0.80)
        if body_sections:
            weights = [max(s.get("fact_count", 1), 1) for s in body_sections]
            weight_sum = sum(weights)
            for section, weight in zip(body_sections, weights):
                ratio = round(0.80 * weight / weight_sum, 3)
                budget.append({
                    "section_title": section.get("title", "章节"),
                    "target_words": int(body_total * weight / weight_sum),
                    "ratio": ratio,
                })
        
        return budget if budget else None
    
    def get_persona(self, profile_id: str) -> Optional[PersonaProfile]:
        """
        获取人格画像
        
        Args:
            profile_id: 画像ID
            
        Returns:
            PersonaProfile 或 None
        """
        # 预定义画像
        personas = {
            "medical_expert": PersonaProfile(
                profile_id="medical_expert",
                author_id="expert_001",
                author_name="医学专家",
                domain="general",
                tone="analytical",
                signature_phrases=["研究表明", "临床证据显示", "根据指南推荐"]
            ),
            "clinical_writer": PersonaProfile(
                profile_id="clinical_writer",
                author_id="writer_001",
                author_name="临床写作者",
                domain="clinical",
                tone="professional",
                signature_phrases=["在临床实践中", "基于循证医学", "值得关注的是"]
            )
        }
        
        return personas.get(profile_id)