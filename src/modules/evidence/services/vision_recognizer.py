"""
视觉识别与证据片段生成服务

消费图像化后的 PageImage，调用视觉模型提取结构化证据片段。
禁止 OCR 作为正式识别方案。
"""
import json
from typing import List, Optional

from src.adapters.llm_gateway import (
    VisionRequest,
    ImageContent,
    LLMGatewayConfig,
    LLMResponse,
    create_vision_provider_from_env,
)
from src.adapters.llm_gateway.provider import VisionProvider

from ..upload_models import (
    PageImage,
    EvidenceFragment,
    EvidenceFragmentType,
    generate_fragment_id,
)
from .image_converter import image_to_base64


VISION_SYSTEM_PROMPT = """你是一个医学内容证据提取助手。你的任务是从提供的文档页面图像中提取所有有价值的证据信息。

提取要求：
1. 提取所有文本内容、表格数据、图表描述
2. 保留原始结构和层次关系
3. 标注每个证据片段的类型（text/table/figure/mixed）
4. 如果是医学相关内容，保留专业术语的准确性

输出格式要求（JSON）：
{
  "fragments": [
    {
      "type": "text|table|figure|mixed",
      "content": "提取的内容",
      "confidence": 0.0-1.0,
      "location": "位置描述（如：页面顶部/中部/底部）"
    }
  ]
}

仅输出 JSON，不要包含其他内容。"""

VISION_PROMPT_TEMPLATE = "请从这张文档页面图像中提取所有证据信息。页码：第{page}页。"


class VisionRecognitionError(Exception):
    pass


class VisionRecognizer:
    """
    视觉识别器

    使用视觉模型（而非 OCR）从图像中提取结构化证据片段。
    """

    def __init__(
        self,
        vision_provider: Optional[VisionProvider] = None,
        vision_config: Optional[LLMGatewayConfig] = None,
    ):
        self._provider = vision_provider
        self._config = vision_config

    def _ensure_provider(self):
        """延迟初始化 vision provider"""
        if self._provider is None:
            self._provider, self._config = create_vision_provider_from_env()

    def recognize_page(
        self, page_image: PageImage, upload_id: str
    ) -> List[EvidenceFragment]:
        """
        对单个页面图像执行视觉识别

        Args:
            page_image: 页面图像对象
            upload_id: 关联的上传 ID

        Returns:
            识别出的证据片段列表
        """
        self._ensure_provider()

        # 将图像转换为 base64
        b64_data = image_to_base64(page_image.storage_path)

        request = VisionRequest(
            images=[
                ImageContent(
                    base64_data=b64_data,
                    media_type="image/png",
                    page_number=page_image.page_number,
                )
            ],
            prompt=VISION_PROMPT_TEMPLATE.format(page=page_image.page_number),
            system_prompt=VISION_SYSTEM_PROMPT,
            temperature=0.1,
            max_tokens=4096,
        )

        try:
            response = self._provider.recognize(request, self._config)
            return self._parse_fragments(response, page_image, upload_id)
        except Exception as e:
            raise VisionRecognitionError(
                f"Vision recognition failed for page {page_image.page_number}: {e}"
            ) from e

    def recognize_pages(
        self, page_images: List[PageImage], upload_id: str
    ) -> List[EvidenceFragment]:
        """
        对多个页面图像执行视觉识别

        逐页识别（避免单次请求过大）。
        """
        all_fragments = []
        for page_image in page_images:
            fragments = self.recognize_page(page_image, upload_id)
            all_fragments.extend(fragments)
        return all_fragments

    def _parse_fragments(
        self, response: LLMResponse, page_image: PageImage, upload_id: str
    ) -> List[EvidenceFragment]:
        """解析视觉模型返回的 JSON 为证据片段"""
        content = response.content.strip()

        # 处理 markdown 代码块
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # 如果解析失败，将整个返回内容作为单个文本片段
            return [
                EvidenceFragment(
                    fragment_id=generate_fragment_id(),
                    upload_id=upload_id,
                    image_id=page_image.image_id,
                    page_number=page_image.page_number,
                    fragment_type=EvidenceFragmentType.TEXT,
                    content=response.content,
                    confidence=0.5,
                    source_location=f"page {page_image.page_number}",
                )
            ]

        fragments = []
        for frag_data in data.get("fragments", []):
            frag_type_str = frag_data.get("type", "text")
            try:
                frag_type = EvidenceFragmentType(frag_type_str)
            except ValueError:
                frag_type = EvidenceFragmentType.TEXT

            fragments.append(
                EvidenceFragment(
                    fragment_id=generate_fragment_id(),
                    upload_id=upload_id,
                    image_id=page_image.image_id,
                    page_number=page_image.page_number,
                    fragment_type=frag_type,
                    content=frag_data.get("content", ""),
                    confidence=float(frag_data.get("confidence", 0.8)),
                    source_location=frag_data.get("location", f"page {page_image.page_number}"),
                )
            )

        return fragments
