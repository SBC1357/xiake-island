from src.api import app as app_module


def test_default_cors_origins_follow_frontend_host_and_port(monkeypatch):
    monkeypatch.delenv(app_module.XIAGEDAO_CORS_ORIGINS, raising=False)
    monkeypatch.setenv(app_module.XIAGEDAO_FRONTEND_HOST, "127.0.0.1")
    monkeypatch.setenv(app_module.XIAGEDAO_FRONTEND_PORT, "4173")

    assert app_module.get_default_cors_origins() == [
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ]


def test_explicit_cors_origins_override_defaults(monkeypatch):
    monkeypatch.setenv(
        app_module.XIAGEDAO_CORS_ORIGINS,
        "https://editor.example.com, https://preview.example.com",
    )

    assert app_module.get_cors_origins() == [
        "https://editor.example.com",
        "https://preview.example.com",
    ]
