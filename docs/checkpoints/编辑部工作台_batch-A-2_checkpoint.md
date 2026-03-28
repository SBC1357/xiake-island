# Batch A-2：后端任务历史/详情 API Checkpoint

> **日期**: 2026-03-16
> **阶段包**: Batch A-2 后端任务历史/详情 API
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 已实现功能

| API 端点 | 方法 | 功能 |
|---------|------|------|
| `/v1/tasks` | GET | 查询任务历史列表，支持按模块/状态过滤和分页 |
| `/v1/tasks/{task_id}` | GET | 获取任务详情，包含完整 input_data/output_data/child_task_ids |

### 1.2 涉及文件

| 文件 | 状态 | 说明 |
|------|------|------|
| `src/api/routes/tasks.py` | 新增 | 任务 API 路由实现 |
| `tests/api/test_tasks.py` | 新增 | API 测试用例（12 个） |

### 1.3 响应模型

**TaskListItemResponse**（列表项）：
- task_id, module, status, started_at, completed_at, duration_ms, error_message

**TaskDetailResponse**（详情）：
- 完整字段包括 input_data, output_data, child_task_ids, input_hash, audit_events

## 2. 未完成项

无

## 3. 失败项与是否既有失败

无 P1/P2 问题。

### 已清除的既有 P2（2026-03-17）
- **Empty dict serialization bug**: `sqlite_store.py` 中空字典 `{}` 被错误序列化为 `None`
  - 修复：改用 `is not None` 显式检查
  - 验证：22/22 测试通过
  - Checkpoint: `checkpoints/2026-03-17-empty-dict-serialization-fix.md`

### 既有问题（非本次引入，非阻塞）
- FastAPI `on_event` 弃用警告
- `SemanticReviewInput` 字段名 `register` 与父类属性冲突警告

## 4. 关键证据路径或命令

### 测试结果
```
pytest tests/api/test_tasks.py -v
# 12 passed in 0.48s

pytest tests -q
# 291 passed, 1 skipped, 5 warnings in 9.28s
```

### 手动验证
```bash
# 启动服务
XIAGEDAO_CONSUMER_ROOT="D:\汇度编辑部1\藏经阁\publish\current\consumers\xiakedao" \
XIAGEDAO_USE_MEMORY_STORE=true \
python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8001

# 创建任务
curl -X POST http://127.0.0.1:8001/v1/opinion/generate \
  -H "Content-Type: application/json" \
  -d '{"audience":"医学专业人士","evidence_bundle":{"items":[{"id":"e1","content":"测试"}]}}'

# 查询任务列表
curl http://127.0.0.1:8001/v1/tasks
# 返回: {"tasks":[{"task_id":"xxx",...}],"total":1}

# 查询任务详情
curl http://127.0.0.1:8001/v1/tasks/{task_id}
# 返回完整 input_data/output_data/child_task_ids
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| API 返回真实数据 | ✅ |
| 包含 input_data | ✅ |
| 包含 output_data | ✅ |
| 包含 child_task_ids | ✅ |

## 5. 双轮自审结果

### 第一轮：敏感信息暴露检查
- ✅ `_filter_sensitive_fields` 函数过滤敏感字段
- ✅ 敏感字段列表：api_key, api_secret, secret, password, token, access_token, refresh_token
- ✅ 过滤逻辑递归处理嵌套数据

### 第二轮：分页限制检查
- ✅ limit 参数约束：1 ≤ limit ≤ 200
- ✅ offset 参数约束：offset ≥ 0
- ✅ 默认 limit=50 合理

### 自审结论
无 P1/P2 问题，符合执行单要求。

## 6. 下一步动作

A-2 已完成，可以进入：
- **A-3** 前端任务历史面板（依赖 A-2）

## 7. 变更摘要

### 新增 API 端点
```
GET /v1/tasks              # 任务列表
GET /v1/tasks/{task_id}    # 任务详情
```

### 功能特性
1. 按模块过滤（opinion, semantic_review, orchestrator）
2. 按状态过滤（running, completed, failed）
3. 分页支持（limit 1-200，默认 50）
4. 敏感信息自动过滤
5. 审计事件关联查询

### 安全措施
- 敏感字段过滤（不暴露 api_key, password 等）
- 分页限制防止数据过载
- 无效参数返回 400 错误
- 不存在的任务返回 404 错误