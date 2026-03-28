"""
Drafting Service

独立成稿服务，负责从编译后的 Prompt 生成正文内容。

SP-7B: 实现确定性 Fake 模式成稿 + OpenAI 真实成稿。
SP-7B FIX1: OpenAI 路径通过注入的 LLMGateway 显式接线，不再在 openai 模式下静默回退到 fake。
"""

import hashlib
import re
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

from .models import DraftingInput, DraftingResult, DraftingTrace

if TYPE_CHECKING:
    from src.adapters.llm_gateway import LLMGateway


@dataclass
class DraftingService:
    """
    成稿服务

    默认使用 Fake 模式生成确定性正文；当 default_mode="openai" 且注入了
    llm_gateway 时，走真实的 gateway 路径。
    """

    llm_gateway: Optional["LLMGateway"] = None
    default_mode: str = "fake"

    def generate(self, input_data: DraftingInput) -> DraftingResult:
        """
        生成正文

        Args:
            input_data: 成稿输入，包含 system_prompt 和 user_prompt

        Returns:
            DraftingResult: 成稿结果，包含 content 和 word_count
        """
        start_time = time.time()

        if self.default_mode == "openai":
            if self.llm_gateway is None:
                raise ValueError("DraftingService requires llm_gateway in openai mode")
            content, trace = self._generate_with_openai(input_data)
            
            # 方案五: 字数偏差重试（仅 openai 模式，最多 1 次）
            target_wc = input_data.target_word_count
            if target_wc and target_wc > 0:
                actual_wc = self._count_words(content)
                deviation = (actual_wc - target_wc) / target_wc
                if abs(deviation) > 0.20:
                    retry_content, retry_trace = self._retry_with_length_hint(
                        input_data, content, actual_wc, target_wc, deviation
                    )
                    if retry_content is not None:
                        content = retry_content
                        trace = retry_trace
                        trace.generation_mode = "openai_retry"
        else:
            content, trace = self._generate_with_fake(input_data)

        word_count = self._count_words(content)
        trace.latency_ms = int((time.time() - start_time) * 1000)
        
        # 字数偏差信息写入 metadata，供 Quality/Delivery 消费
        word_deviation_info = {}
        if input_data.target_word_count and input_data.target_word_count > 0:
            deviation_pct = round(
                (word_count - input_data.target_word_count) / input_data.target_word_count * 100, 1
            )
            word_deviation_info = {
                "word_deviation_pct": deviation_pct,
                "word_deviation_abs": word_count - input_data.target_word_count,
            }

        return DraftingResult(
            content=content,
            word_count=word_count,
            trace=trace,
            metadata={
                "target_word_count": input_data.target_word_count,
                "model_config": input_data.model_config,
                "provider_name": self.default_mode,
                **word_deviation_info,
                **input_data.metadata,
            },
        )

    def _generate_with_fake(
        self, input_data: DraftingInput
    ) -> tuple[str, DraftingTrace]:
        """
        Fake 模式：根据 prompt 结构生成确定性正文。
        """
        seed_input = input_data.user_prompt + input_data.system_prompt
        deterministic_seed = hashlib.md5(seed_input.encode("utf-8")).hexdigest()[:16]

        thesis = self._extract_thesis(input_data.user_prompt)
        outline = self._extract_outline(input_data.user_prompt)
        evidence = self._extract_evidence(input_data.user_prompt)

        content_parts: list[str] = []

        if thesis:
            content_parts.append(f"# {thesis}")
            content_parts.append("")

        content_parts.append("## 引言")
        content_parts.append("")
        content_parts.append(
            f"本文旨在探讨{thesis}。通过系统性分析，我们将从多个角度阐述这一主题。"
        )
        content_parts.append("")

        if outline:
            content_parts.append("## 主要内容")
            content_parts.append("")
            for i, item in enumerate(outline, 1):
                title = item.get("title", f"第{i}节")
                content_parts.append(f"### {title}")
                content_parts.append("")

                section_type = item.get("type", "section")
                if section_type == "domain_section":
                    domain = item.get("domain", title)
                    fact_count = item.get("fact_count", 0)
                    paragraph = (
                        f"在{domain}方面，本节基于{fact_count}条证据进行深入分析。"
                        "研究数据显示，该领域具有明确的实践意义。"
                    )
                elif section_type == "evidence":
                    paragraph = "本节聚焦于关键证据的深入分析，为论点提供有力支撑。"
                elif section_type == "intro":
                    paragraph = f"{title}部分为全文奠定基础，明确研究背景和意义。"
                elif section_type == "conclusion":
                    paragraph = f"{title}部分总结全文核心观点，并提出后续关注点。"
                else:
                    paragraph = f"本节讨论{title}相关内容，从专业角度进行分析阐述。"

                content_parts.append(paragraph)
                content_parts.append("")

        if evidence:
            content_parts.append("## 核心证据")
            content_parts.append("")
            for item in evidence[:5]:
                content_parts.append(f"- {item}")
            content_parts.append("")

        content_parts.append("## 结论")
        content_parts.append("")
        content_parts.append(
            f"综上所述，{thesis}。本文通过系统性分析，为相关决策提供了科学依据和实践参考。"
        )

        content = "\n".join(content_parts)

        # 根据 target_word_count 扩展 fake 内容，避免被 Delivery 门禁卡死
        if input_data.target_word_count and input_data.target_word_count > 0:
            current_wc = self._count_words(content)
            _FILLER_PARAGRAPHS = [
                "从机制层面来看，现有数据为该方向提供了初步支撑，后续仍需更大规模的验证研究予以确认。",
                "值得关注的是，不同亚组之间的表现存在一定异质性，这提示临床实践中应结合患者个体特征进行决策。",
                "安全性方面，已有证据未发现显著的不良信号，但长期随访数据仍然有限，需持续关注。",
                "从卫生经济学角度审视，该方案的成本效益比在现有评估框架下表现良好，但不同医疗体系间的适用性仍待验证。",
                "综合多维度证据，该领域的研究正从概念验证阶段向临床转化过渡，未来的关键在于高质量随机对照试验的开展。",
                "在研究方法学层面，当前证据主要来源于观察性研究和小规模试验，证据等级有待提升。",
                "此外，基于真实世界数据的分析为理解该方案在常规临床环境中的表现提供了有益补充。",
                "从患者报告结局来看，接受该方案治疗的患者在生活质量评分上呈现出积极趋势。",
            ]
            para_idx = 0
            while current_wc < input_data.target_word_count and para_idx < len(_FILLER_PARAGRAPHS) * 3:
                filler = _FILLER_PARAGRAPHS[para_idx % len(_FILLER_PARAGRAPHS)]
                content += f"\n\n{filler}"
                current_wc = self._count_words(content)
                para_idx += 1

        trace = DraftingTrace(
            prompt_tokens=len(input_data.user_prompt) // 2,
            completion_tokens=len(content) // 2,
            model_used="fake-drafting",
            generation_mode="fake",
            deterministic_seed=deterministic_seed,
        )
        return content, trace

    def _generate_with_openai(
        self, input_data: DraftingInput
    ) -> tuple[str, DraftingTrace]:
        """
        OpenAI 模式：通过注入的 gateway 执行真实生成路径。
        """
        from src.adapters.llm_gateway import LLMRequest

        # 根据目标字数动态调整 max_tokens（中文1字≈1.5token，留20%余量）
        target_wc = input_data.target_word_count
        if target_wc:
            dynamic_max_tokens = int(target_wc * 1.5 * 1.2)
        else:
            dynamic_max_tokens = input_data.model_config.get("max_tokens", 2000)

        request = LLMRequest(
            prompt=input_data.user_prompt or "请根据系统提示完成正文撰写。",
            system_prompt=input_data.system_prompt or None,
            temperature=input_data.model_config.get("temperature", 0.7),
            max_tokens=dynamic_max_tokens,
            metadata=input_data.metadata or None,
        )
        response = self.llm_gateway.generate(request)
        cleaned_content = self._clean_content(response.content)
        trace = DraftingTrace(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            model_used=response.model,
            generation_mode="openai",
        )
        return cleaned_content, trace

    def _retry_with_length_hint(
        self,
        input_data: DraftingInput,
        first_content: str,
        actual_wc: int,
        target_wc: int,
        deviation: float,
    ) -> tuple[Optional[str], DraftingTrace]:
        """
        字数偏差重试：给 LLM 追加长度修正指令，重新生成一次。

        - deviation > 0.20: 太长，追加压缩指令
        - deviation < -0.20: 太短，追加扩展指令
        - 最多重试 1 次；重试失败返回 (None, empty_trace)
        """
        from src.adapters.llm_gateway import LLMRequest

        if deviation > 0:
            hint = (
                f"\n\n【修正指令】上一稿{actual_wc}字，超出目标{target_wc}字。"
                f"请压缩至{target_wc}字左右（±10%），删除冗余表述和重复论证，保留核心证据和结论。"
            )
        else:
            hint = (
                f"\n\n【修正指令】上一稿{actual_wc}字，不足目标{target_wc}字。"
                f"请扩展至{target_wc}字左右（±10%），补充证据细节和分析深度，禁止泛化扩写和灌水。"
            )

        retry_prompt = (input_data.user_prompt or "") + hint
        dynamic_max_tokens = int(target_wc * 1.5 * 1.2)

        try:
            request = LLMRequest(
                prompt=retry_prompt,
                system_prompt=input_data.system_prompt or None,
                temperature=input_data.model_config.get("temperature", 0.7),
                max_tokens=dynamic_max_tokens,
                metadata=input_data.metadata or None,
            )
            response = self.llm_gateway.generate(request)
            cleaned = self._clean_content(response.content)
            trace = DraftingTrace(
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                model_used=response.model,
                generation_mode="openai_retry",
            )
            return cleaned, trace
        except Exception:
            # 重试失败，保留原始结果
            empty_trace = DraftingTrace(
                prompt_tokens=0,
                completion_tokens=0,
                model_used="retry_failed",
                generation_mode="openai_retry_failed",
            )
            return None, empty_trace

    def _extract_thesis(self, user_prompt: str) -> str:
        """从 user_prompt 提取主题。"""
        for line in user_prompt.split("\n"):
            if line.startswith("主题:"):
                return line.replace("主题:", "", 1).strip() or "医学研究主题"
            if line.startswith("# "):
                return line.replace("# ", "", 1).strip() or "医学研究主题"
        return "医学研究主题"

    def _extract_outline(self, user_prompt: str) -> list[dict[str, Any]]:
        """从 user_prompt 提取大纲。"""
        import re

        outline: list[dict[str, Any]] = []
        lines = user_prompt.split("\n")
        in_outline = False

        for line in lines:
            stripped = line.strip()
            if "大纲:" in stripped:
                in_outline = True
                continue
            if in_outline and stripped.startswith(
                ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")
            ):
                _, title = stripped.split(".", 1)
                title = title.strip()
                match = re.search(r"\((\d+)条证据\)", title)
                if match:
                    outline.append(
                        {
                            "title": title.split("(")[0].strip(),
                            "type": "domain_section",
                            "fact_count": int(match.group(1)),
                            "domain": title.split("(")[0].strip(),
                        }
                    )
                else:
                    outline.append({"title": title, "type": "section"})
            elif in_outline and stripped == "":
                break

        return outline

    def _extract_evidence(self, user_prompt: str) -> list[str]:
        """从 user_prompt 提取证据列表。"""
        evidence: list[str] = []
        lines = user_prompt.split("\n")
        in_evidence = False

        for line in lines:
            stripped = line.strip()
            if "核心证据:" in stripped or "证据详情:" in stripped:
                in_evidence = True
                continue
            if in_evidence and stripped.startswith("- "):
                evidence.append(stripped[2:])
            elif in_evidence and stripped == "" and evidence:
                break

        return evidence

    def _clean_content(self, content: str) -> str:
        """清洗推理泄露标记，防止 <think>、内部自述句进入正文"""
        # 移除 <think>...</think> 块（含换行）
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        # 过滤明显的推理自述行
        _INFERENCE_PREFIXES = (
            "The user wants", "Let me", "I need", "I will", "I should",
            "I'll", "Step ", "First,", "Next,", "Finally,",
            "Okay,", "Sure,", "Alright,",
        )
        lines = [
            line for line in content.splitlines()
            if not any(line.strip().startswith(p) for p in _INFERENCE_PREFIXES)
        ]
        return "\n".join(lines).strip()

    def _count_words(self, content: str) -> int:
        """
        计算正文字数

        中文字数按字符计，英文按单词计。
        """
        import re

        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", content))
        english_words = len(re.findall(r"[a-zA-Z]+", content))
        numbers = len(re.findall(r"\d+", content))
        return chinese_chars + english_words + numbers
