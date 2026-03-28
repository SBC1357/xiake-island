# Batch A-6：审计事件链完整化与审查记录关联 Checkpoint

> **日期**: 2026-03-17
> **阶段包**: Batch A-6 审计事件链完整化与审查记录关联
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 修改文件

| 文件 | 变更 |
|------|------|
| `src/runtime_logging/audit_events.py` | 扩展审计事件类型，新增 feedback/task_rerun/task_viewed 等 |
| `src/runtime_logging/task_logger.py` | 添加 save_audit_event 方法，支持独立 audit_events 表 |
| `src/api/routes/tasks.py` | 新增 POST /v1/tasks/{task_id}/feedback 接口 |
| `src/api/routes/workflow.py` | 添加 workflow_requested/workflow_completed 审计事件记录 |

### 1.2 新增文件

| 文件 | 说明 |
|------|------|
| `tests/runtime_logging/test_audit_events.py` | 审计事件测试（8 个用例） |

### 1.3 功能特性

1. **扩展的审计事件类型**：
   - task_started, task_completed, task_failed
   - workflow_requested, workflow_completed, workflow_failed
   - feedback_submitted, task_rerun, task_viewed

2. **POST feedback 接口**：
   - 路径：`POST /v1/tasks/{task_id}/feedback`
   - 参数：rating (1-5), comment, tags
   - 审查反馈关联到原任务

3. **审计事件存储**：
   - 支持 SQLite 独立 audit_events 表
   - 支持回退到 metadata 存储

## 2. 未完成项

无

## 3. 失败项与是否既有失败

无 P1/P2 问题。

### 既有问题（非本次引入，非阻塞）
- 数据库数据积累可能导致 limit 相关测试失败（需清理或使用内存存储）

## 4. 关键证据路径或命令

### 后端测试
```
pytest tests/runtime_logging/test_audit_events.py -v
# 8 passed in 0.24s

pytest tests -q
# 301 passed, 1 skipped, 3 warnings in 7.90s
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| 审计事件写入独立 audit_events 表 | ✅ |
| POST feedback 接口可用 | ✅ |
| 审查结果关联到原任务 | ✅ |
| 不阻塞主流程 | ✅ 审计失败不影响任务执行 |
| 不在审计事件中存储完整输入输出 | ✅ 只存储摘要信息 |

## 5. 双轮自审结果

### 第一轮：主流程影响检查
- ✅ 审计事件保存使用 try/except，失败不影响主流程
- ✅ 审计事件表独立，不影响任务表性能

### 第二轮：敏感信息检查
- ✅ 审计事件 details 不包含完整输入输出
- ✅ workflow_requested 只存储 input_summary

### 自审结论
无 P1/P2 问题，符合执行单要求。

## 6. 下一步动作

A-6 已完成，可以进入：
- **A-7** 任务版本/回退 API（依赖 A-2）

## 7. 变更摘要

### 新增审计事件类型
```python
AuditEventType = Literal[
    "task_started",
    "task_completed",
    "task_failed",
    "workflow_requested",
    "workflow_completed",
    "workflow_failed",
    "feedback_submitted",
    "task_rerun",
    "task_viewed",
]
```

### 新增 API
```
POST /v1/tasks/{task_id}/feedback
{
  "rating": 1-5,
  "comment": "string",
  "tags": ["string"]
}
```

### 审计事件记录位置
- workflow.py：记录 workflow_requested, workflow_completed
- tasks.py：记录 feedback_submitted