"""
侠客岛 - 统一 Web 入口

单进程同时提供 API 和前端静态页面，
既支持本地访问，也支持通过 Tailscale 共享。
"""
import os
import subprocess
from pathlib import Path

from src.env_utils import load_project_env, path_from_env


PROJECT_ROOT = Path(__file__).parent.parent
load_project_env(PROJECT_ROOT)

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.app import app


APP_STATE_CONFIGURED = "_xiakedao_frontend_configured"
APP_STATE_ENABLED = "_xiakedao_frontend_enabled"
XIAGEDAO_WEB_MODE = "XIAGEDAO_WEB_MODE"
XIAGEDAO_HOST = "XIAGEDAO_HOST"
XIAGEDAO_PORT = "XIAGEDAO_PORT"
XIAGEDAO_FRONTEND_DIST = "XIAGEDAO_FRONTEND_DIST"
WEB_MODE_API_ONLY = "api-only"
WEB_MODE_BUNDLED = "web-bundled"


def get_web_mode() -> str:
    raw_mode = os.environ.get(XIAGEDAO_WEB_MODE, WEB_MODE_BUNDLED).strip().lower()
    if raw_mode in {"", WEB_MODE_BUNDLED, "bundled"}:
        return WEB_MODE_BUNDLED
    if raw_mode == WEB_MODE_API_ONLY:
        return WEB_MODE_API_ONLY
    print(f"[WARN] Unknown {XIAGEDAO_WEB_MODE}={raw_mode!r}; fallback to {WEB_MODE_BUNDLED}.")
    return WEB_MODE_BUNDLED


def get_frontend_dist() -> Path:
    explicit = path_from_env(os.environ.get(XIAGEDAO_FRONTEND_DIST))
    if explicit is not None:
        return explicit
    return PROJECT_ROOT / "frontend" / "dist"


def setup_static_serving(
    target_app: FastAPI = app,
    frontend_dist: Path | None = None,
) -> bool:
    """Configure a FastAPI app to serve the built frontend once when enabled."""
    frontend_dist = frontend_dist or get_frontend_dist()

    if getattr(target_app.state, APP_STATE_CONFIGURED, False):
        return getattr(target_app.state, APP_STATE_ENABLED, False)

    setattr(target_app.state, APP_STATE_CONFIGURED, True)

    if get_web_mode() == WEB_MODE_API_ONLY:
        setattr(target_app.state, APP_STATE_ENABLED, False)
        print("[INFO] Web mode is api-only; skipping frontend static mount.")
        return False

    if not frontend_dist.exists():
        setattr(target_app.state, APP_STATE_ENABLED, False)
        print(f"[WARN] Frontend dist not found: {frontend_dist}")
        print("[WARN] Run: cd frontend && npm run build")
        return False

    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        target_app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @target_app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(frontend_dist / "index.html"))

    @target_app.get("/{path:path}", include_in_schema=False)
    async def serve_spa(path: str):
        # Preserve backend 404 semantics for unmatched API and docs paths.
        if path.startswith("v1/") or path in {"docs", "redoc", "openapi.json", "health"}:
            raise HTTPException(status_code=404)

        file_path = frontend_dist / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dist / "index.html"))

    setattr(target_app.state, APP_STATE_ENABLED, True)
    return True


def get_bind_host() -> str:
    return os.environ.get(XIAGEDAO_HOST, "0.0.0.0").strip() or "0.0.0.0"


def get_bind_port() -> int:
    raw_port = os.environ.get(XIAGEDAO_PORT, "8000").strip() or "8000"
    try:
        port = int(raw_port)
    except ValueError:
        print(f"[WARN] Invalid {XIAGEDAO_PORT}={raw_port!r}; fallback to 8000.")
        return 8000

    if not 1 <= port <= 65535:
        print(f"[WARN] Invalid {XIAGEDAO_PORT}={raw_port!r}; fallback to 8000.")
        return 8000
    return port


def get_tailscale_ip() -> str | None:
    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    ip = result.stdout.strip()
    return ip or None


def print_access_info(host: str, port: int, web_mode: str, frontend_enabled: bool) -> None:
    print("=" * 50)
    print("侠客岛 - 统一 Web 服务")
    print("=" * 50)
    print()
    print(f"[INFO] Binding to: {host}:{port}")
    print(f"[INFO] Web mode: {web_mode}")
    if frontend_enabled:
        print(f"[INFO] Local access: http://127.0.0.1:{port}")
    else:
        print(f"[INFO] API base: http://127.0.0.1:{port}")
    print(f"[INFO] API docs: http://127.0.0.1:{port}/docs")

    if host not in {"127.0.0.1", "localhost"}:
        ts_ip = get_tailscale_ip()
        if ts_ip:
            print(f"[INFO] Tailscale access: http://{ts_ip}:{port}")
        else:
            print("[INFO] Tailscale IP: (run 'tailscale ip -4' to get your IP)")

    print()


def main() -> None:
    """Start the unified web server."""
    host = get_bind_host()
    port = get_bind_port()

    web_mode = get_web_mode()
    frontend_enabled = setup_static_serving()
    print_access_info(host, port, web_mode, frontend_enabled)

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
