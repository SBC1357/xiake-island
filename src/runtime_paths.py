"""
运行态路径配置

统一管理运行时数据目录，避免不同模块各自回写仓库工作区。
"""
from __future__ import annotations

import os
from pathlib import Path

from src.env_utils import path_from_env


XIAGEDAO_RUNTIME_ROOT = "XIAGEDAO_RUNTIME_ROOT"
XIAGEDAO_DATA_DIR = "XIAGEDAO_DATA_DIR"
XIAGEDAO_UPLOAD_ROOT = "XIAGEDAO_UPLOAD_ROOT"
LEGACY_XIAKEDAO_UPLOAD_ROOT = "XIAKEDAO_UPLOAD_ROOT"
# 兼容旧常量导入，避免现有测试或脚本在过渡期失效。
XIAKEDAO_UPLOAD_ROOT = LEGACY_XIAKEDAO_UPLOAD_ROOT

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_default_runtime_root() -> Path:
    """默认把运行态放到仓库同级目录，避免污染工作区。"""
    return PROJECT_ROOT.parent / f"{PROJECT_ROOT.name}-runtime"


def get_runtime_root() -> Path:
    return path_from_env(os.environ.get(XIAGEDAO_RUNTIME_ROOT)) or get_default_runtime_root()


def get_runtime_data_dir() -> Path:
    explicit = path_from_env(os.environ.get(XIAGEDAO_DATA_DIR))
    if explicit is not None:
        return explicit
    return get_runtime_root() / "data"


def get_task_db_path() -> Path:
    return get_runtime_data_dir() / "tasks.db"


def get_upload_root() -> Path:
    explicit = path_from_env(
        os.environ.get(XIAGEDAO_UPLOAD_ROOT)
        or os.environ.get(LEGACY_XIAKEDAO_UPLOAD_ROOT)
    )
    if explicit is not None:
        return explicit
    return get_runtime_root() / "uploads"
