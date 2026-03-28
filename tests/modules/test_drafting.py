"""
Tests for Drafting Module

SP-7B: 测试独立成稿模块。
SP-7B FIX1: 补充 openai gateway 路径验证。
"""

from types import SimpleNamespace

import pytest

from src.adapters.llm_gateway import LLMResponse, LLMUsage
from src.modules.drafting import DraftingInput, DraftingResult, DraftingService, DraftingTrace


class TestDraftingTrace:
    """测试成稿追踪"""

    def test_drafting_trace_creation(self):
        trace = DraftingTrace(
            prompt_tokens=100,
            completion_tokens=500,
            model_used="fake-drafting",
            latency_ms=50,
            generation_mode="fake",
            deterministic_seed="abc123",
        )

        assert trace.prompt_tokens == 100
        assert trace.completion_tokens == 500
        assert trace.model_used == "fake-drafting"
        assert trace.generation_mode == "fake"
        assert trace.deterministic_seed == "abc123"

    def test_drafting_trace_to_dict(self):
        trace = DraftingTrace(
            prompt_tokens=50,
            completion_tokens=200,
            model_used="fake-drafting",
            generation_mode="fake",
        )

        result = trace.to_dict()

        assert "prompt_tokens" in result
        assert "completion_tokens" in result
        assert "model_used" in result
        assert "generation_mode" in result
        assert result["prompt_tokens"] == 50


class TestDraftingInput:
    """测试成稿输入"""

    def test_drafting_input_creation(self):
        input_data = DraftingInput(
            system_prompt="你是医学写作助手",
            user_prompt="请写一篇关于阿尔茨海默病的文章",
            target_word_count=1000,
        )

        assert input_data.system_prompt == "你是医学写作助手"
        assert input_data.user_prompt == "请写一篇关于阿尔茨海默病的文章"
        assert input_data.target_word_count == 1000

    def test_drafting_input_with_model_config(self):
        input_data = DraftingInput(
            system_prompt="系统指令",
            user_prompt="用户指令",
            model_config={"temperature": 0.5, "max_tokens": 3000},
            metadata={"play_id": "professional"},
        )

        assert input_data.model_config["temperature"] == 0.5
        assert input_data.metadata["play_id"] == "professional"


class TestDraftingResult:
    """测试成稿结果"""

    def test_drafting_result_creation(self):
        trace = DraftingTrace(generation_mode="fake")
        result = DraftingResult(
            content="这是生成的正文内容", word_count=100, trace=trace
        )

        assert result.content == "这是生成的正文内容"
        assert result.word_count == 100
        assert result.trace.generation_mode == "fake"


class TestDraftingService:
    """测试成稿服务"""

    @pytest.fixture
    def service(self):
        return DraftingService()

    def test_generate_basic(self, service):
        input_data = DraftingInput(
            system_prompt="你是医学写作助手",
            user_prompt="主题: 阿尔茨海默病治疗进展\n\n大纲:\n1. 引言\n2. 主要内容\n3. 结论",
        )

        result = service.generate(input_data)

        assert result.content is not None
        assert len(result.content) > 0
        assert result.word_count > 0
        assert result.trace.generation_mode == "fake"

    def test_generate_deterministic(self, service):
        input_data = DraftingInput(
            system_prompt="系统指令",
            user_prompt="主题: 测试主题\n\n大纲:\n1. 引言\n2. 结论",
        )

        result1 = service.generate(input_data)
        result2 = service.generate(input_data)

        assert result1.content == result2.content
        assert result1.trace.deterministic_seed == result2.trace.deterministic_seed

    def test_generate_with_thesis(self, service):
        input_data = DraftingInput(
            system_prompt="你是助手",
            user_prompt="主题: 阿尔茨海默病的最新治疗进展\n\n大纲:\n1. 引言\n2. 药物治疗\n3. 结论",
        )

        result = service.generate(input_data)

        assert "阿尔茨海默病" in result.content or "治疗进展" in result.content

    def test_generate_with_evidence(self, service):
        input_data = DraftingInput(
            system_prompt="你是助手",
            user_prompt="主题: 测试\n\n核心证据:\n- 证据1: 有效率85%\n- 证据2: 安全性良好",
        )

        result = service.generate(input_data)

        assert "证据" in result.content or "核心证据" in result.content

    def test_generate_with_target_word_count(self, service):
        input_data = DraftingInput(
            system_prompt="你是助手",
            user_prompt="主题: 测试主题",
            target_word_count=500,
        )

        result = service.generate(input_data)

        assert result.metadata["target_word_count"] == 500

    def test_word_count_calculation(self, service):
        input_data = DraftingInput(
            system_prompt="系统", user_prompt="主题: 中文测试主题"
        )

        result = service.generate(input_data)

        assert result.word_count > 0

    def test_trace_has_latency(self, service):
        input_data = DraftingInput(system_prompt="系统", user_prompt="主题: 测试")

        result = service.generate(input_data)

        assert result.trace.latency_ms >= 0


class DummyOpenAIGateway:
    """测试用 gateway，验证 openai 路径而不触发真实 API 调用。"""

    def __init__(self):
        self.config = SimpleNamespace(provider_name="openai", model_name="gpt-4.1")
        self.last_request = None

    def generate(self, request):
        self.last_request = request
        return LLMResponse(
            content="这是由 mock OpenAI gateway 生成的正文内容。",
            provider="openai",
            model="gpt-4.1",
            latency_ms=12,
            finish_reason="stop",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )


class TestDraftingOpenAIGatewayPath:
    """SP-7B FIX1: 测试 openai 路径显式使用 gateway。"""

    def test_generate_openai_mode_uses_gateway(self):
        gateway = DummyOpenAIGateway()
        service = DraftingService(llm_gateway=gateway, default_mode="openai")
        input_data = DraftingInput(
            system_prompt="系统指令",
            user_prompt="用户指令",
        )

        result = service.generate(input_data)

        assert result.trace.generation_mode == "openai"
        assert result.trace.model_used == "gpt-4.1"
        assert gateway.last_request.prompt == "用户指令"
        assert gateway.last_request.system_prompt == "系统指令"


class TestDraftingServiceHelpers:
    """测试成稿服务辅助方法"""

    @pytest.fixture
    def service(self):
        return DraftingService()

    def test_extract_thesis(self, service):
        user_prompt = "主题: 阿尔茨海默病治疗\n\n大纲:\n1. 引言"

        thesis = service._extract_thesis(user_prompt)

        assert "阿尔茨海默病" in thesis or thesis == "医学研究主题"

    def test_extract_outline(self, service):
        user_prompt = """主题: 测试

大纲:
1. 引言
2. 疗效分析(5条证据)
3. 结论"""

        outline = service._extract_outline(user_prompt)

        assert len(outline) >= 2
        titles = [item["title"] for item in outline]
        assert "引言" in titles or "疗效分析" in titles

    def test_extract_evidence(self, service):
        user_prompt = """主题: 测试

核心证据:
- 证据1: 有效率85%
- 证据2: 安全性5%"""

        evidence = service._extract_evidence(user_prompt)

        assert len(evidence) == 2
        assert "证据1" in evidence[0]

    def test_count_words_chinese(self, service):
        content = "这是一段中文测试内容"

        word_count = service._count_words(content)

        assert word_count >= 5

    def test_count_words_mixed(self, service):
        content = "这是中文 content with English 123"

        word_count = service._count_words(content)

        assert word_count > 0
