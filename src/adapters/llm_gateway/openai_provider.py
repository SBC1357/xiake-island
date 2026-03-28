"""
OpenAI LLM Provider

实现 OpenAI API 的真实 LLM Provider。
"""
import os
from typing import Optional

import httpx

from .models import LLMRequest, LLMResponse, LLMUsage
from .config import LLMGatewayConfig
from .provider import LLMProvider
from .errors import LLMTimeoutError, LLMProviderError


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM Provider
    
    调用 OpenAI API 进行真实模型推理。
    
    Attributes:
        _api_key: OpenAI API Key
        _base_url: API Base URL (可选，默认 https://api.openai.com/v1)
        _http_client: HTTP 客户端
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
        trust_env: Optional[bool] = None,
    ):
        """
        初始化 OpenAI Provider
        
        Args:
            api_key: OpenAI API Key，默认从环境变量 OPENAI_API_KEY 读取
            base_url: API Base URL，默认从环境变量 OPENAI_BASE_URL 或官方地址
            http_client: 可选的 HTTP 客户端（用于测试）
            trust_env: 是否继承系统代理环境变量；默认从 OPENAI_TRUST_ENV 读取
        """
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._trust_env = trust_env if trust_env is not None else self._read_trust_env()
        
        # 移除末尾的 /，统一处理
        self._base_url = self._base_url.rstrip("/")
        
        self._http_client = http_client

    def _read_trust_env(self) -> bool:
        """
        是否继承系统代理环境变量。

        默认关闭，避免桌面代理或抓包代理影响模型调用稳定性。
        """
        raw = os.environ.get("OPENAI_TRUST_ENV", "false").strip().lower()
        return raw in {"1", "true", "yes", "on"}
    
    @property
    def name(self) -> str:
        return "openai"
    
    def _get_client(self) -> httpx.Client:
        """获取 HTTP 客户端"""
        if self._http_client is not None:
            return self._http_client
        return httpx.Client(trust_env=self._trust_env)
    
    def generate(
        self,
        request: LLMRequest,
        config: LLMGatewayConfig
    ) -> LLMResponse:
        """
        生成 LLM 响应
        
        调用 OpenAI Chat Completions API。
        
        Args:
            request: LLM 请求
            config: Gateway 配置
            
        Returns:
            LLM 响应
            
        Raises:
            LLMTimeoutError: 调用超时
            LLMProviderError: API 错误
        """
        # 检查 API Key
        if not self._api_key:
            raise LLMProviderError(
                message="OpenAI API key not configured. Set OPENAI_API_KEY environment variable.",
                provider=self.name,
                model=config.model_name,
                retryable=False
            )
        
        # 构建消息
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        # 构建请求体
        request_body = {
            "model": config.model_name,
            "messages": messages,
        }
        
        if request.temperature is not None:
            request_body["temperature"] = request.temperature
        if request.max_tokens is not None:
            request_body["max_tokens"] = request.max_tokens
        
        # 发送请求
        client = self._get_client()
        
        try:
            response = client.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
                timeout=config.timeout_seconds
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 解析响应
            choice = data["choices"][0]
            message = choice["message"]
            
            # 解析 usage
            usage_data = data.get("usage", {})
            usage = LLMUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return LLMResponse(
                content=message.get("content", ""),
                provider=self.name,
                model=config.model_name,
                latency_ms=0,  # Gateway 层会更新
                finish_reason=choice.get("finish_reason"),
                usage=usage
            )
            
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(
                message=f"OpenAI API timeout: {str(e)}",
                provider=self.name,
                model=config.model_name
            ) from e
        except httpx.HTTPStatusError as e:
            # HTTP 错误
            error_msg = f"OpenAI API error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg = f"OpenAI API error: {error_data['error'].get('message', str(e))}"
            except:
                pass
            
            # 判断是否可重试
            # 429 (rate limit), 500, 502, 503, 504 可重试
            retryable = e.response.status_code in [429, 500, 502, 503, 504]
            
            raise LLMProviderError(
                message=error_msg,
                provider=self.name,
                model=config.model_name,
                retryable=retryable
            ) from e
        except httpx.RequestError as e:
            # 网络错误
            raise LLMProviderError(
                message=f"OpenAI API request failed: {str(e)}",
                provider=self.name,
                model=config.model_name,
                retryable=True
            ) from e
        except Exception as e:
            # 其他错误
            raise LLMProviderError(
                message=f"Unexpected error: {str(e)}",
                provider=self.name,
                model=config.model_name,
                retryable=False,
                original_error=e
            ) from e
        finally:
            # 如果不是外部传入的 client，需要关闭
            if self._http_client is None:
                client.close()
