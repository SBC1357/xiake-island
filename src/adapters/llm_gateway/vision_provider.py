"""
OpenAI Vision Provider

实现 OpenAI-compatible 视觉模型 Provider，用于多模态证据识别。
独立于文本 OpenAIProvider，使用独立的模型配置。
"""
import os
from typing import Optional

import httpx

from .models import VisionRequest, LLMResponse, LLMUsage, ImageContent
from .config import LLMGatewayConfig
from .provider import VisionProvider
from .errors import LLMTimeoutError, LLMProviderError


class OpenAIVisionProvider(VisionProvider):
    """
    OpenAI-compatible 视觉模型 Provider

    调用 OpenAI Vision API（或兼容接口）进行图像识别。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
    ):
        self._api_key = api_key or os.environ.get("VISION_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self._base_url = (
            base_url
            or os.environ.get("VISION_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self._base_url = self._base_url.rstrip("/")
        self._http_client = http_client

    @property
    def name(self) -> str:
        return "openai_vision"

    def _get_client(self) -> httpx.Client:
        if self._http_client is not None:
            return self._http_client
        return httpx.Client()

    def _build_image_content(self, image: ImageContent) -> dict:
        """构建 OpenAI Vision API 的图像内容块"""
        if image.base64_data:
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image.media_type};base64,{image.base64_data}"
                },
            }
        elif image.image_url:
            return {
                "type": "image_url",
                "image_url": {"url": image.image_url},
            }
        else:
            raise LLMProviderError(
                message="ImageContent must have either base64_data or image_url",
                provider=self.name,
                model="",
                retryable=False,
            )

    def recognize(
        self,
        request: VisionRequest,
        config: LLMGatewayConfig,
    ) -> LLMResponse:
        """
        执行视觉识别

        将图像和提示词发送到 Vision API，返回结构化识别结果。
        """
        if not self._api_key:
            raise LLMProviderError(
                message="Vision API key not configured. Set VISION_API_KEY or OPENAI_API_KEY.",
                provider=self.name,
                model=config.model_name,
                retryable=False,
            )

        # 构建 content 数组：先放图像，后放文本提示
        content_parts = []
        for img in request.images:
            content_parts.append(self._build_image_content(img))
        content_parts.append({"type": "text", "text": request.prompt})

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": content_parts})

        request_body = {
            "model": config.model_name,
            "messages": messages,
        }
        if request.temperature is not None:
            request_body["temperature"] = request.temperature
        if request.max_tokens is not None:
            request_body["max_tokens"] = request.max_tokens

        client = self._get_client()
        try:
            response = client.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
                timeout=max(config.timeout_seconds, 120.0),  # 视觉识别需要更长超时
            )
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            message = choice["message"]
            usage_data = data.get("usage", {})
            usage = LLMUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

            return LLMResponse(
                content=message.get("content", ""),
                provider=self.name,
                model=config.model_name,
                latency_ms=0,
                finish_reason=choice.get("finish_reason"),
                usage=usage,
            )

        except httpx.TimeoutException as e:
            raise LLMTimeoutError(
                message=f"Vision API timeout: {e}",
                provider=self.name,
                model=config.model_name,
            ) from e
        except httpx.HTTPStatusError as e:
            error_msg = f"Vision API error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg = f"Vision API error: {error_data['error'].get('message', str(e))}"
            except Exception:
                pass
            retryable = e.response.status_code in [429, 500, 502, 503, 504]
            raise LLMProviderError(
                message=error_msg,
                provider=self.name,
                model=config.model_name,
                retryable=retryable,
            ) from e
        except httpx.RequestError as e:
            raise LLMProviderError(
                message=f"Vision API request failed: {e}",
                provider=self.name,
                model=config.model_name,
                retryable=True,
            ) from e
        finally:
            if self._http_client is None:
                client.close()
