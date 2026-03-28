"""
API Layer - FastAPI 应用
职责: 暴露统一 HTTP 接口
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 应用级共享实例
from src.runtime_logging import TaskLogger, SQLiteTaskLogStore, MemoryTaskLogStore
from src.assembly import get_asset_bridge, validate_consumer_config
from src.env_utils import get_env_csv, get_env_flag


_shared_task_logger: TaskLogger | None = None
XIAGEDAO_USE_MEMORY_STORE = "XIAGEDAO_USE_MEMORY_STORE"
XIAGEDAO_CORS_ORIGINS = "XIAGEDAO_CORS_ORIGINS"
XIAGEDAO_FRONTEND_HOST = "XIAGEDAO_FRONTEND_HOST"
XIAGEDAO_FRONTEND_PORT = "XIAGEDAO_FRONTEND_PORT"
_DEFAULT_FRONTEND_HOST = "localhost"
_DEFAULT_FRONTEND_PORT = "5173"


def _create_shared_task_logger() -> TaskLogger:
    """按当前环境配置创建共享 TaskLogger。"""
    use_memory = get_env_flag(XIAGEDAO_USE_MEMORY_STORE, default=False)
    store = MemoryTaskLogStore() if use_memory else SQLiteTaskLogStore()
    return TaskLogger(store)


def get_shared_task_logger():
    """
    获取应用级共享的 TaskLogger 实例

    Returns:
        TaskLogger: 共享的任务日志记录器
    """
    global _shared_task_logger
    if _shared_task_logger is None:
        _shared_task_logger = _create_shared_task_logger()
    return _shared_task_logger


def get_default_cors_origins() -> list[str]:
    frontend_host = os.environ.get(XIAGEDAO_FRONTEND_HOST, _DEFAULT_FRONTEND_HOST).strip() or _DEFAULT_FRONTEND_HOST
    frontend_port = os.environ.get(XIAGEDAO_FRONTEND_PORT, _DEFAULT_FRONTEND_PORT).strip() or _DEFAULT_FRONTEND_PORT

    origins = {f"http://{frontend_host}:{frontend_port}"}
    if frontend_host == "localhost":
        origins.add(f"http://127.0.0.1:{frontend_port}")
    elif frontend_host == "127.0.0.1":
        origins.add(f"http://localhost:{frontend_port}")

    return sorted(origins)


def get_cors_origins() -> list[str]:
    return get_env_csv(XIAGEDAO_CORS_ORIGINS, get_default_cors_origins())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 启动时验证配置"""
    # Startup
    strict_mode = get_env_flag("XIAGEDAO_STRICT_MODE", default=True)

    is_valid, message = validate_consumer_config()

    if not is_valid:
        if strict_mode:
            # 严格模式：启动失败
            raise RuntimeError(
                f"Xiakedao consumer config invalid (strict mode): {message}"
            )
        else:
            # 非严格模式：仅警告
            print(f"警告 (非严格模式): {message}")
    else:
        print(f"配置验证通过: {message}")

    yield
    # Shutdown (如有需要可在此添加清理逻辑)


# 创建 FastAPI 应用实例
app = FastAPI(
    title="侠客岛 - 中文医疗内容能力平台",
    description="模块化内容能力底座 + 主编排器",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件 - 允许本地前端开发访问
cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials="*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 导入路由
from src.api.routes import (
    opinion,
    semantic_review,
    workflow,
    tasks,
    evidence,
    planning,
    writing,
    quality,
    delivery,
    drafting,
)
from src.api.routes import upload, independent_review

# 注册路由
app.include_router(opinion.router)
app.include_router(semantic_review.router)
app.include_router(workflow.router)
app.include_router(tasks.router)
app.include_router(evidence.router)
app.include_router(planning.router)
app.include_router(writing.router)
app.include_router(quality.router)
app.include_router(delivery.router)
app.include_router(drafting.router)  # SP-7B: 独立成稿模块
app.include_router(upload.router)  # 多模态证据上传
app.include_router(independent_review.router)  # 独立改稿审稿模块


@app.get("/health")
async def health_check():
    """
    健康检查接口

    Returns:
        dict: 服务状态信息
    """
    return {"status": "ok", "service": "xiakedao"}
