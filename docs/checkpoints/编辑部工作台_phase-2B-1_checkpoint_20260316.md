# 2B-1 日志持久化存储 Checkpoint

> **日期**: 2026-03-16
> **阶段包**: 2B-1 日志持久化存储
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 新增文件
- `src/runtime_logging/sqlite_store.py` — SQLite 持久化存储实现
- `tests/runtime_logging/test_sqlite_store.py` — SQLite 存储测试（20 个测试用例）

### 1.2 修改文件
- `src/runtime_logging/__init__.py` — 导出 SQLiteTaskLogStore
- `src/api/app.py` — 使用 SQLiteTaskLogStore 替代 MemoryTaskLogStore

## 2. 未完成项

无

## 3. 失败项与是否既有失败

### 修复的 P1 问题
- **SQLite 线程安全问题**：FastAPI 异步场景下 SQLite 连接跨线程使用报错
  - 解决方案：添加 `check_same_thread=False` 参数

### 既有问题（非本次引入）
- LSP 类型警告（既存）
- 前端 React key 警告（既存）

## 4. 关键证据路径或命令

### 测试结果
```
pytest tests/runtime_logging/test_sqlite_store.py -v
# 20 passed in 2.63s

pytest tests -q
# 279 passed, 1 skipped, 5 warnings in 9.07s
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| 任务日志持久化到 SQLite | ✅ |
| 服务重启后仍可查询历史任务 | ✅ 测试覆盖 |
| 独立 audit_events 表 | ✅ |
| 环境变量可配置数据目录 | ✅ |

## 5. 下一步动作

2B-1 已完成，可以进入后续阶段包：
- **2A-1** 后端任务历史 API（依赖 2B-1）
- **2A-2** 后端任务详情 API（依赖 2B-1）
- **2B-2** 审计事件链完整化（依赖 2B-1）

## 6. 变更摘要

### SQLite 表结构
```sql
-- tasks 表
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    module TEXT NOT NULL,
    input_hash TEXT,
    input_data TEXT,      -- JSON
    output_data TEXT,     -- JSON
    parent_task_id TEXT,
    child_task_ids TEXT,  -- JSON 数组
    started_at TEXT NOT NULL,
    completed_at TEXT,
    duration_ms INTEGER,
    metadata TEXT,        -- JSON
    error_message TEXT
);

-- audit_events 表（独立）
CREATE TABLE audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    actor TEXT,
    details TEXT,         -- JSON
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);
```

### 环境变量
- `XIAGEDAO_DATA_DIR`: 数据目录（默认 `./data`）
- `XIAGEDAO_USE_MEMORY_STORE`: 使用内存存储（开发/测试用）

### 线程安全
- SQLite 连接使用 `check_same_thread=False` 支持异步场景