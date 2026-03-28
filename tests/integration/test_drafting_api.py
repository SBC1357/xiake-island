"""
Tests for Drafting API

SP-7B: 测试独立成稿 API 端点。
SP-7B FIX1: 补充 strict request contract 和 openai gateway 路径验证。
"""

import os

import pytest
from fastapi.testclient import TestClient

from src.adapters.llm_gateway import FakeLLMProvider, LLMGatewayConfig
from src.api.app import app


client = TestClient(app)


class TestDraftingAPI:
    """测试成稿 API"""

    def test_generate_content_basic(self):
        response = client.post(
            "/v1/drafting/generate",
            json={
                "system_prompt": "你是医学写作助手",
                "user_prompt": "主题: 阿尔茨海默病治疗进展\n\n大纲:\n1. 引言\n2. 结论",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "task_id" in data
        assert "content" in data
        assert "word_count" in data
        assert len(data["content"]) > 0
        assert data["word_count"] > 0

    def test_generate_content_with_target_word_count(self):
        response = client.post(
            "/v1/drafting/generate",
            json={
                "system_prompt": "系统指令",
                "user_prompt": "主题: 测试主题",
                "target_word_count": 500,
            },
        )

        assert response.status_code == 200
        assert response.json()["metadata"]["target_word_count"] == 500

    def test_generate_content_with_model_config(self):
        response = client.post(
            "/v1/drafting/generate",
            json={
                "system_prompt": "系统指令",
                "user_prompt": "主题: 测试",
                "model_config_data": {"temperature": 0.5, "max_tokens": 3000},
            },
        )

        assert response.status_code == 200
        assert response.json()["trace"]["generation_mode"] == "fake"

    def test_generate_content_returns_task_id(self):
        response = client.post(
            "/v1/drafting/generate",
            json={"system_prompt": "系统", "user_prompt": "主题: 测试"},
        )

        assert response.status_code == 200
        assert len(response.json()["task_id"]) > 0

    def test_generate_content_trace_includes_mode(self):
        response = client.post(
            "/v1/drafting/generate",
            json={"system_prompt": "系统", "user_prompt": "主题: 测试"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "generation_mode" in data["trace"]
        assert data["trace"]["generation_mode"] == "fake"

    def test_generate_content_trace_includes_latency(self):
        response = client.post(
            "/v1/drafting/generate",
            json={"system_prompt": "系统", "user_prompt": "主题: 测试"},
        )

        assert response.status_code == 200
        assert response.json()["trace"]["latency_ms"] >= 0

    def test_generate_content_deterministic(self):
        request_body = {
            "system_prompt": "系统指令",
            "user_prompt": "主题: 测试主题\n\n大纲:\n1. 引言\n2. 结论",
        }

        response1 = client.post("/v1/drafting/generate", json=request_body)
        response2 = client.post("/v1/drafting/generate", json=request_body)

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        assert data1["content"] == data2["content"]
        assert (
            data1["trace"]["deterministic_seed"] == data2["trace"]["deterministic_seed"]
        )

    def test_health_check(self):
        response = client.get("/v1/drafting/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["module"] == "drafting"


class TestDraftingAPIValidation:
    """测试成稿 API 参数验证"""

    def test_missing_system_prompt(self):
        response = client.post(
            "/v1/drafting/generate", json={"user_prompt": "用户指令"}
        )

        assert response.status_code == 422

    def test_missing_user_prompt(self):
        response = client.post(
            "/v1/drafting/generate", json={"system_prompt": "系统指令"}
        )

        assert response.status_code == 422

    def test_empty_prompts(self):
        response = client.post(
            "/v1/drafting/generate", json={"system_prompt": "", "user_prompt": ""}
        )

        assert response.status_code == 200

    def test_extra_field_rejected(self):
        response = client.post(
            "/v1/drafting/generate",
            json={
                "system_prompt": "系统指令",
                "user_prompt": "用户指令",
                "unexpected": "x",
            },
        )

        assert response.status_code == 422


class TestDraftingOpenAIGatewayPath:
    """SP-7B FIX1: 验证 API openai 路径通过 gateway，而不依赖真实 OpenAI 调用。"""

    def test_openai_mode_uses_gateway_path(self, monkeypatch):
        from src.api.routes import drafting as drafting_route

        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("LLM_MODEL", "gpt-4.1")

        def fake_provider_factory():
            config = LLMGatewayConfig(provider_name="openai", model_name="gpt-4.1")
            provider = FakeLLMProvider(
                name="mock-openai",
                response_content="这是由 mock OpenAI provider 生成的正文内容。",
            )
            return provider, config

        monkeypatch.setattr(
            drafting_route, "create_llm_provider_from_env", fake_provider_factory
        )

        response = client.post(
            "/v1/drafting/generate",
            json={"system_prompt": "系统指令", "user_prompt": "用户指令"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["trace"]["generation_mode"] == "openai"
        assert data["trace"]["model_used"] == "gpt-4.1"
        assert "mock OpenAI" in data["content"]

        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.delenv("LLM_MODEL", raising=False)
