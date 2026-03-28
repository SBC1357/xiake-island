from pathlib import Path

from src import env_utils


def test_path_from_env_normalizes_wsl_path_on_windows(monkeypatch):
    monkeypatch.setattr(env_utils.os, "name", "nt")

    path = env_utils.path_from_env("/mnt/d/汇度编辑部1/侠客岛")

    assert path == Path(r"D:\汇度编辑部1\侠客岛")


def test_get_env_csv_ignores_empty_items(monkeypatch):
    monkeypatch.setenv("XIAGEDAO_CORS_ORIGINS", " http://a.test , , http://b.test ")

    assert env_utils.get_env_csv("XIAGEDAO_CORS_ORIGINS", ["http://fallback"]) == [
        "http://a.test",
        "http://b.test",
    ]


def test_load_project_env_prefers_explicit_env_file(monkeypatch, tmp_path):
    project_root = tmp_path / "repo"
    project_root.mkdir()
    explicit_env = tmp_path / "cloud.env"
    explicit_env.write_text("XIAGEDAO_SAMPLE_FLAG=enabled\n", encoding="utf-8")

    monkeypatch.delenv("XIAGEDAO_SAMPLE_FLAG", raising=False)
    monkeypatch.setenv(env_utils.XIAGEDAO_ENV_FILE, str(explicit_env))

    loaded = env_utils.load_project_env(project_root)

    assert loaded == explicit_env
    assert env_utils.resolve_env_file(project_root) == explicit_env
    assert env_utils.os.environ["XIAGEDAO_SAMPLE_FLAG"] == "enabled"
