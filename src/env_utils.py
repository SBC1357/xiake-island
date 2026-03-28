"""
环境变量与路径解析工具。

统一处理布尔开关、逗号分隔配置、`.env` 文件加载，以及 WSL/Windows 路径兼容。
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv


XIAGEDAO_ENV_FILE = "XIAGEDAO_ENV_FILE"

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}
_WSL_PATH_RE = re.compile(r"^/mnt/([a-zA-Z])/(.*)")


def normalize_path_string(raw_value: str | None) -> str | None:
    """将环境变量中的路径标准化为当前平台可识别的形式。"""
    if not raw_value:
        return None

    if os.name == "nt":
        match = _WSL_PATH_RE.match(raw_value)
        if match:
            drive = match.group(1).upper()
            rest = match.group(2).replace("/", "\\")
            return f"{drive}:\\{rest}"

    return raw_value


def path_from_env(raw_value: str | None) -> Path | None:
    normalized = normalize_path_string(raw_value)
    if not normalized:
        return None
    return Path(normalized)


def get_env_flag(name: str, default: bool = False) -> bool:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return default


def get_env_csv(name: str, default: list[str]) -> list[str]:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return list(default)

    items = [item.strip() for item in raw_value.split(",") if item.strip()]
    return items or list(default)


def resolve_env_file(project_root: Path) -> Path | None:
    explicit = path_from_env(os.environ.get(XIAGEDAO_ENV_FILE))
    if explicit is not None:
        return explicit

    default_env_file = project_root / ".env"
    if default_env_file.exists():
        return default_env_file

    return None


def load_project_env(project_root: Path) -> Path | None:
    """按约定加载环境变量文件。"""
    env_file = resolve_env_file(project_root)
    if env_file is None or not env_file.exists():
        return None

    load_dotenv(env_file, override=False)
    return env_file
