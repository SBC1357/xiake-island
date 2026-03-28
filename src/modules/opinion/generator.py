"""
Opinion Generator

医学观点生成器，通过 LLM Gateway 生成结构化观点。
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
    OpinionInput,
    OpinionOutput,
    ThesisOutput,
    SupportPointOutput,
    EvidenceMapping,
    ConfidenceNotes,
)
from .config import OpinionGeneratorConfig
from .errors import (
    OpinionModuleError,
    OpinionGenerationError,
    ConfidenceTooLowError,
)


class OpinionGenerator:
    """
    医学观点生成器
    
    通过 LLM Gateway 生成结构化医学观点。
    
    Attributes:
        gateway: LLM Gateway 实例
        config: 生成器配置
    """
    
    def __init__(self, gateway: LLMGateway, config: Optional[OpinionGeneratorConfig] = None):
        """
        初始化观点生成器
        
        Args:
            gateway: LLM Gateway 实例
            config: 生成器配置 (可选)
        """
        self.gateway = gateway
        self.config = config or OpinionGeneratorConfig()
    
    def generate(self, input_data: OpinionInput) -> OpinionOutput:
        """
        生成医学观点
        
        Args:
            input_data: 观点输入数据
            
        Returns:
            观点输出
            
        Raises:
            OpinionGenerationError: 生成失败
            ConfidenceTooLowError: 置信度过低
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(input_data)
            
            # 调用 LLM
            request = LLMRequest(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                temperature=0.7,
            )
            
            response = self.gateway.generate(request)
            
            # 解析响应
            output = self._parse_response(response, input_data)
            
            # 验证置信度
            if output.thesis.confidence < self.config.min_confidence:
                raise ConfidenceTooLowError(
                    message=f"置信度 {output.thesis.confidence} 低于阈值 {self.config.min_confidence}",
                    details={"confidence": output.thesis.confidence}
                )
            
            return output
            
        except LLMGatewayError as e:
            raise OpinionGenerationError(
                message=f"LLM 调用失败: {e.message}",
                details={"provider": e.provider, "model": e.model}
            ) from e
        except OpinionModuleError:
            raise
        except Exception as e:
            raise OpinionGenerationError(
                message=f"观点生成失败: {str(e)}"
            ) from e
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的医学观点分析助手。你的任务是根据提供的证据材料，形成结构化的医学观点。

输出要求：
1. 观点陈述应清晰、准确、有据可依
2. 置信度应根据证据质量和一致性合理评估
3. 支撑点应与证据明确关联
4. 指出观点的局限性和假设条件

请以 JSON 格式输出，包含以下字段：
{
  "thesis": {
    "statement": "观点陈述",
    "confidence": 0.0-1.0,
    "evidence_refs": ["证据ID列表"]
  },
  "support_points": [
    {
      "content": "支撑内容",
      "strength": "weak/medium/strong",
      "evidence_id": "关联证据ID"
    }
  ],
  "limitations": ["局限性说明"],
  "assumptions": ["假设条件"]
}"""
    
    def _build_prompt(self, input_data: OpinionInput) -> str:
        """构建提示词"""
        parts = []
        
        # 添加证据信息
        parts.append("## 证据材料\n")
        for item in input_data.evidence_bundle.items:
            source_info = f" (来源: {item.source})" if item.source else ""
            parts.append(f"[{item.id}]{source_info}: {item.content}\n")
        
        if input_data.evidence_bundle.summary:
            parts.append(f"\n证据摘要: {input_data.evidence_bundle.summary}\n")
        
        # 添加目标受众
        parts.append(f"\n## 目标受众\n{input_data.audience}\n")
        
        # 添加观点提示（如果有）
        if input_data.thesis_hint:
            parts.append(f"\n## 观点提示\n{input_data.thesis_hint}\n")
        
        parts.append("\n请根据以上证据材料，形成结构化的医学观点。")
        
        return "".join(parts)
    
    def _parse_response(self, response: LLMResponse, input_data: OpinionInput) -> OpinionOutput:
        """解析 LLM 响应"""
        try:
            # 尝试解析 JSON
            content = response.content.strip()
            
            # 提取 JSON 部分（处理 markdown 代码块）
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            data = json.loads(content)
            
            # 构建论题
            thesis_data = data.get("thesis", {})
            thesis = ThesisOutput(
                statement=thesis_data.get("statement", ""),
                confidence=thesis_data.get("confidence", 0.5),
                evidence_refs=thesis_data.get("evidence_refs", [])
            )
            
            # 构建支撑点
            support_points = []
            for sp_data in data.get("support_points", [])[:self.config.max_support_points]:
                support_points.append(SupportPointOutput(
                    content=sp_data.get("content", ""),
                    strength=sp_data.get("strength", "medium"),
                    evidence_id=sp_data.get("evidence_id")
                ))
            
            # 构建证据映射
            evidence_mapping = None
            if self.config.require_evidence_mapping:
                evidence_mapping = EvidenceMapping(
                    thesis_evidence=thesis.evidence_refs,
                    support_evidence={
                        str(i): [sp.evidence_id] if sp.evidence_id else []
                        for i, sp in enumerate(support_points)
                        if sp.evidence_id
                    }
                )
            
            # 构建置信度说明
            confidence_notes = ConfidenceNotes(
                overall_confidence=thesis.confidence,
                limitations=data.get("limitations", []),
                assumptions=data.get("assumptions", [])
            )
            
            return OpinionOutput(
                thesis=thesis,
                support_points=support_points,
                evidence_mapping=evidence_mapping,
                confidence_notes=confidence_notes
            )
            
        except json.JSONDecodeError as e:
            raise OpinionGenerationError(
                message=f"解析 LLM 响应失败: {str(e)}",
                details={"response_content": response.content[:500]}
            ) from e