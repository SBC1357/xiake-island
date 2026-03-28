from __future__ import annotations

from pathlib import Path

import pytest


def _should_force_fake_llm(request: pytest.FixtureRequest) -> bool:
    path = getattr(request.node, "path", None)
    if path is None:
        path = Path(str(request.node.fspath))

    if path.name == "test_orchestrator.py":
        return True

    return "integration" in path.parts or "api" in path.parts


@pytest.fixture(autouse=True)
def force_fake_llm_for_app_level_tests(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
):
    """
    将集成层和编排器测试固定到 fake provider，避免被 .env 或外部环境污染。
    """
    if not _should_force_fake_llm(request):
        return

    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_MODEL", "fake-model")
    monkeypatch.setenv("DRAFTING_MODE", "fake")
