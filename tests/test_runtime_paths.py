from src.runtime_paths import (
    LEGACY_XIAKEDAO_UPLOAD_ROOT,
    PROJECT_ROOT,
    XIAGEDAO_DATA_DIR,
    XIAGEDAO_RUNTIME_ROOT,
    XIAGEDAO_UPLOAD_ROOT,
    XIAKEDAO_UPLOAD_ROOT,
    get_default_runtime_root,
    get_runtime_data_dir,
    get_runtime_root,
    get_task_db_path,
    get_upload_root,
)


def test_default_runtime_root_is_repo_sibling():
    expected = PROJECT_ROOT.parent / f"{PROJECT_ROOT.name}-runtime"

    assert get_default_runtime_root() == expected
    assert get_default_runtime_root() != PROJECT_ROOT
    assert get_default_runtime_root().parent == PROJECT_ROOT.parent


def test_runtime_root_env_drives_default_data_and_upload_paths(monkeypatch, tmp_path):
    runtime_root = tmp_path / "runtime-root"

    monkeypatch.setenv(XIAGEDAO_RUNTIME_ROOT, str(runtime_root))
    monkeypatch.delenv(XIAGEDAO_DATA_DIR, raising=False)
    monkeypatch.delenv(XIAGEDAO_UPLOAD_ROOT, raising=False)
    monkeypatch.delenv(LEGACY_XIAKEDAO_UPLOAD_ROOT, raising=False)

    assert get_runtime_root() == runtime_root
    assert get_runtime_data_dir() == runtime_root / "data"
    assert get_task_db_path() == runtime_root / "data" / "tasks.db"
    assert get_upload_root() == runtime_root / "uploads"


def test_explicit_data_and_upload_roots_override_runtime_root(monkeypatch, tmp_path):
    runtime_root = tmp_path / "runtime-root"
    data_root = tmp_path / "custom-data"
    upload_root = tmp_path / "custom-uploads"

    monkeypatch.setenv(XIAGEDAO_RUNTIME_ROOT, str(runtime_root))
    monkeypatch.setenv(XIAGEDAO_DATA_DIR, str(data_root))
    monkeypatch.setenv(XIAGEDAO_UPLOAD_ROOT, str(upload_root))

    assert get_runtime_root() == runtime_root
    assert get_runtime_data_dir() == data_root
    assert get_task_db_path() == data_root / "tasks.db"
    assert get_upload_root() == upload_root


def test_legacy_upload_root_env_still_supported(monkeypatch, tmp_path):
    legacy_upload_root = tmp_path / "legacy-uploads"

    monkeypatch.delenv(XIAGEDAO_UPLOAD_ROOT, raising=False)
    monkeypatch.setenv(XIAKEDAO_UPLOAD_ROOT, str(legacy_upload_root))

    assert get_upload_root() == legacy_upload_root
