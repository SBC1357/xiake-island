import src.assembly as assembly


def test_validate_consumer_config_uses_normalized_path(monkeypatch, tmp_path):
    raw_path = "/mnt/d/汇度编辑部1/藏经阁/publish/current/consumers/xiakedao"
    seen = {}

    def fake_to_path(value: str | None):
        seen["value"] = value
        return tmp_path

    monkeypatch.setenv(assembly.XIAGEDAO_CONSUMER_ROOT, raw_path)
    monkeypatch.setattr(assembly, "_to_path", fake_to_path)

    is_valid, message = assembly.validate_consumer_config()

    assert seen["value"] == raw_path
    assert is_valid is True
    assert str(tmp_path) in message


def test_validate_consumer_config_reports_missing_normalized_path(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing-consumer-root"

    monkeypatch.setenv(assembly.XIAGEDAO_CONSUMER_ROOT, "/mnt/d/missing")
    monkeypatch.setattr(assembly, "_to_path", lambda value: missing_path)

    is_valid, message = assembly.validate_consumer_config()

    assert is_valid is False
    assert str(missing_path) in message
