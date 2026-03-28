"""
Semantic Reviewer

中文语义审核器，通过 LLM Gateway 生成结构化审核结果。

SP-6 Batch 6B: 增加确定性规则层，规则层先于 LLM 执行。
"""
import json
from typing import Optional

from src.adapters.llm_gateway import (
    LLMGateway,
    LLMRequest,
    LLMResponse,
    LLMGatewayError,
)

from .models import (
    SemanticReviewInput,
    SemanticReviewOutput,
    FindingOutput,
    SeveritySummaryOutput,
    RewriteTargetOutput,
    PrototypeAlignmentOutput,
)
from .config import SemanticReviewerConfig
from .errors import (
    SemanticReviewError,
    ReviewGenerationError,
    ContentTooShortError,
)


class SemanticReviewer:
    """
    中文语义审核器
    
    SP-6 Batch 6B: 审核链分为三层：
    1. 确定性规则层：执行可程序化的语法、风格、合规规则
    2. 模型审校层：发现规则层难以完全覆盖的问题
    3. 改写建议层：提出修订目标和修订方向
    
    Attributes:
        gateway: LLM Gateway 实例
        config: 审核器配置
        rule_engine: 规则引擎实例（可选）
    """
    
    def __init__(
        self,
        gateway: LLMGateway,
        config: Optional[SemanticReviewerConfig] = None,
        rule_engine: Optional[object] = None,
    ):
        """
        初始化语义审核器
        
        Args:
            gateway: LLM Gateway 实例
            config: 审核器配置 (可选)
            rule_engine: 规则引擎实例 (可选)
        """
        self.gateway = gateway
        self.config = config or SemanticReviewerConfig()
        self._rule_engine = rule_engine
    
    def _get_rule_engine(self):
        """延迟初始化规则引擎"""
        if self._rule_engine is None:
            from src.rules import RuleEngine
            from src.rules.families import (
                RegisterLevelsFamily,
                ExpressionBaseFamily,
                MedicalSyntaxRulesFamily,
                ThesisDerivationRulesFamily,
            )
            from src.rules.adapters import M5ComplianceAdapterFamily
            
            self._rule_engine = RuleEngine()
            self._rule_engine.register_family(RegisterLevelsFamily())
            self._rule_engine.register_family(ExpressionBaseFamily())
            self._rule_engine.register_family(MedicalSyntaxRulesFamily())
            self._rule_engine.register_family(ThesisDerivationRulesFamily())
            self._rule_engine.register_family(M5ComplianceAdapterFamily())
        
        return self._rule_engine
    
    def _run_rule_layer(self, content: str) -> dict:
        """
        执行确定性规则层
        
        SP-6 Batch 6B: 规则层先于 LLM 执行。
        
        Args:
            content: 待审核内容
            
        Returns:
            规则层输出字典
        """
        engine = self._get_rule_engine()
        output = engine.execute(content)
        
        return {
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
    
    def _determine_rerun_scope(self, severity_summary: SeveritySummaryOutput) -> str:
        """
        SP-6 Batch 6C: 根据问题严重程度确定重跑范围
        
        规则：
        - critical 或 high 问题 -> full_gate_rerun (需重跑所有门禁)
        - medium 或 low 问题 -> partial_gate_rerun (只需局部重跑)
        
        Args:
            severity_summary: 严重性摘要
            
        Returns:
            "full_gate_rerun" 或 "partial_gate_rerun"
        """
        if severity_summary.critical > 0 or severity_summary.high > 0:
            return "full_gate_rerun"
        return "partial_gate_rerun"
    
    def review(self, input_data: SemanticReviewInput) -> SemanticReviewOutput:
        """
        执行语义审核
        
        SP-6 Batch 6B: 先执行确定性规则层，再执行模型层。
        SP-6 Batch 6C: 显式暴露三层输出和重跑范围。
        
        Args:
            input_data: 审核输入数据
            
        Returns:
            审核输出结果
            
        Raises:
            ReviewGenerationError: 审核生成失败
            ContentTooShortError: 内容过短
        """
        # 验证内容长度
        if len(input_data.content.strip()) < 10:
            raise ContentTooShortError(
                message="审核内容过短，至少需要10个字符",
                details={"content_length": len(input_data.content)}
            )
        
        # SP-6 Batch 6B: 执行确定性规则层
        rule_layer_output = self._run_rule_layer(input_data.content)
        
        try:
            # 构建提示词
            prompt = self._build_prompt(input_data)
            
            # 调用 LLM
            request = LLMRequest(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                temperature=0.3,  # 审核需要较低温度，更稳定
            )
            
            response = self.gateway.generate(request)
            
            # 解析响应
            output = self._parse_response(response)
            
            # SP-6 Batch 6B: 添加规则层输出
            output.rule_layer_output = rule_layer_output
            
            # SP-6 Batch 6C: 显式暴露模型审校层输出
            output.model_review_output = {
                "findings": [
                    {
                        "severity": f.severity,
                        "category": f.category,
                        "description": f.description,
                        "location": f.location,
                        "suggestion": f.suggestion
                    }
                    for f in output.findings
                ],
                "severity_summary": {
                    "low": output.severity_summary.low,
                    "medium": output.severity_summary.medium,
                    "high": output.severity_summary.high,
                    "critical": output.severity_summary.critical
                }
            }
            
            # SP-6 Batch 6C: 显式暴露改写建议层输出
            output.rewrite_layer_output = {
                "rewrite_targets": [
                    {
                        "original": rt.original,
                        "suggested": rt.suggested,
                        "reason": rt.reason,
                        "priority": rt.priority
                    }
                    for rt in output.rewrite_target
                ],
                "count": len(output.rewrite_target)
            }
            
            # SP-6 Batch 6C: 确定重跑范围
            output.rerun_scope = self._determine_rerun_scope(output.severity_summary)
            
            # 应用自动通过阈值
            if self.config.auto_pass_threshold:
                output.passed = (
                    output.severity_summary.critical == 0 and
                    output.severity_summary.high == 0
                )
            
            return output
            
        except LLMGatewayError as e:
            raise ReviewGenerationError(
                message=f"LLM 调用失败: {e.message}",
                details={"provider": e.provider, "model": e.model}
            ) from e
        except SemanticReviewError:
            raise
        except Exception as e:
            raise ReviewGenerationError(
                message=f"审核生成失败: {str(e)}"
            ) from e
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的中文语义审核助手。你的任务是对提供的中文内容进行语义审核，识别语法错误、表达不当、逻辑问题等。

不要输出思考过程，不要输出解释性文字，不要输出 Markdown 代码块。
只输出一个可被 json.loads 直接解析的 JSON 对象。

输出要求：
1. 识别内容中的语法、语义、逻辑问题
2. 按严重程度分类：critical(严重)、high(高)、medium(中)、low(低)
3. 提供具体的修改建议
4. 计算与原型的对齐分数
5. 生成改写目标（如有需要）

请以 JSON 格式输出，包含以下字段：
{
  "passed": true/false,
  "severity_summary": {
    "low": 0,
    "medium": 0,
    "high": 0,
    "critical": 0
  },
  "findings": [
    {
      "severity": "low/medium/high/critical",
      "category": "问题类别",
      "description": "问题描述",
      "location": "问题位置",
      "suggestion": "修改建议"
    }
  ],
  "rewrite_target": [
    {
      "original": "原始内容",
      "suggested": "建议改写",
      "reason": "改写原因",
      "priority": "low/medium/high/critical"
    }
  ],
  "prototype_alignment": {
    "score": 0-100,
    "matched_rules": ["匹配的规则"],
    "unmatched_rules": ["未匹配的规则"],
    "notes": "对齐说明"
  }
}"""
    
    def _build_prompt(self, input_data: SemanticReviewInput) -> str:
        """构建提示词"""
        parts = []
        
        # 添加待审核内容
        parts.append("## 待审核内容\n")
        parts.append(input_data.content)
        parts.append("\n")
        
        # 添加目标受众
        parts.append(f"\n## 目标受众\n{input_data.audience}\n")
        
        # 添加原型提示（如果有）
        if input_data.prototype_hint:
            parts.append(f"\n## 原型提示\n{input_data.prototype_hint}\n")
        
        # 添加语体要求（如果有）
        if input_data.register:
            parts.append(f"\n## 语体要求\n{input_data.register}\n")
        
        parts.append("\n请对以上内容进行语义审核，返回结构化的审核结果。")
        
        return "".join(parts)
    
    def _parse_response(self, response: LLMResponse) -> SemanticReviewOutput:
        """解析 LLM 响应"""
        try:
            # 尝试解析 JSON
            content = response.content.strip()
            
            # 移除 <think>...</think> 推理标签（部分模型会输出）
            import re
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            
            # 提取 JSON 部分（处理 markdown 代码块）
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()

            # 兼容 JSON 前后存在说明性文本的情况
            json_start = content.find("{")
            json_end = content.rfind("}")
            if json_start != -1 and json_end != -1 and json_start < json_end:
                content = content[json_start:json_end + 1]
            
            data = json.loads(content)
            
            # 构建严重性摘要
            severity_data = data.get("severity_summary", {})
            severity_summary = SeveritySummaryOutput(
                low=severity_data.get("low", 0),
                medium=severity_data.get("medium", 0),
                high=severity_data.get("high", 0),
                critical=severity_data.get("critical", 0)
            )
            
            # 构建发现项列表
            findings = []
            for f_data in data.get("findings", [])[:self.config.max_findings]:
                findings.append(FindingOutput(
                    severity=f_data.get("severity", "medium"),
                    category=f_data.get("category", "一般"),
                    description=f_data.get("description", ""),
                    location=f_data.get("location"),
                    suggestion=f_data.get("suggestion")
                ))
            
            # 构建改写目标列表
            rewrite_targets = []
            if self.config.require_rewrite_targets:
                for rt_data in data.get("rewrite_target", []):
                    rewrite_targets.append(RewriteTargetOutput(
                        original=rt_data.get("original", ""),
                        suggested=rt_data.get("suggested", ""),
                        reason=rt_data.get("reason", ""),
                        priority=rt_data.get("priority", "medium")
                    ))
            
            # 构建原型对齐
            prototype_alignment = None
            if self.config.require_prototype_alignment:
                pa_data = data.get("prototype_alignment", {})
                if pa_data:
                    prototype_alignment = PrototypeAlignmentOutput(
                        score=pa_data.get("score", 0),
                        matched_rules=pa_data.get("matched_rules", []),
                        unmatched_rules=pa_data.get("unmatched_rules", []),
                        notes=pa_data.get("notes")
                    )
            
            return SemanticReviewOutput(
                passed=data.get("passed", severity_summary.critical == 0 and severity_summary.high == 0),
                severity_summary=severity_summary,
                findings=findings,
                rewrite_target=rewrite_targets,
                prototype_alignment=prototype_alignment
            )
            
        except json.JSONDecodeError as e:
            raise ReviewGenerationError(
                message=f"解析 LLM 响应失败: {str(e)}",
                details={"response_content": response.content[:500]}
            ) from e
