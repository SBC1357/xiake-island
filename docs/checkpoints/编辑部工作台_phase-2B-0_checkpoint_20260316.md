# 2B-0 日志契约升级 Checkpoint

> **日期**: 2026-03-16
> **阶段包**: 2B-0 日志契约升级（强制前置）
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 新增文件
- `src/runtime_logging/hash_utils.py` — input_hash 计算函数
- `tests/runtime_logging/test_contract_upgrade.py` — 契约升级验证测试（20 个测试用例）

### 1.2 修改文件
- `src/runtime_logging/models.py` — TaskLogEntry 新增 input_data, output_data, child_task_ids 字段
- `src/runtime_logging/task_logger.py` — 接口升级，支持新参数
- `src/runtime_logging/memory_store.py` — 支持 input_hash 查询
- `src/runtime_logging/__init__.py` — 导出 compute_input_hash
- `src/api/routes/opinion.py` — 传入完整 input_data/output_data
- `src/api/routes/semantic_review.py` — 传入完整 input_data/output_data
- `src/orchestrator/service.py` — 传入完整 input_data/output_data/child_task_ids

## 2. 未完成项

无

## 3. 失败项与是否既有失败

无 P1/P2 问题。既有 LSP 警告（非本次引入）：
- `orchestrator/service.py` 类型注解问题（既存）
- `frontend` React key 警告（既存）

## 4. 关键证据路径或命令

### 测试结果
```
pytest tests/runtime_logging/test_contract_upgrade.py -v
# 20 passed in 0.21s

pytest tests -q
# 259 passed, 1 skipped, 5 warnings in 2.36s
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| 执行一次 opinion 生成后，能通过 TaskLogger.get_task(task_id) 取回完整 input_data 和 output_data | ✅ 测试覆盖 |
| input_hash 被正确计算并存入 | ✅ 测试覆盖 |
| orchestrator 执行 workflow 后，父任务的 child_task_ids 包含子任务 ID | ✅ 测试覆盖 |

## 5. 下一步动作

2B-0 已完成，可以进入后续阶段包：
- **2B-1** 日志持久化存储（依赖 2B-0）
- **2A-1** 后端任务历史 API（依赖 2B-1）

## 6. 变更摘要

### TaskLogEntry 新增字段
```python
input_data: Optional[dict[str, Any]]  # 完整输入参数（可重放）
output_data: Optional[dict[str, Any]]  # 完整输出结果（可查看）
child_task_ids: list[str]  # 子任务ID列表（默认空列表）
```

### TaskLogger 接口升级
```python
def start_task(
    self,
    module: ModuleName,
    input_data: Optional[dict[str, Any]] = None,  # 新增
    input_hash: Optional[str] = None,
    parent_task_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None
) -> str

def complete_task(
    self,
    task_id: str,
    output_data: Optional[dict[str, Any]] = None,  # 新增
    output_hash: Optional[str] = None,
    duration_ms: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
    child_task_ids: Optional[list[str]] = None  # 新增
) -> None
```

### input_hash 计算规则
```python
# 使用 SHA256，取前 16 位
hash_value = hashlib.sha256(json.dumps(input_data, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()[:16]
```

### 向后兼容性
- input_data/output_data 为 Optional，旧调用点不传不会报错
- child_task_ids 默认为空列表
- 既有测试全部通过