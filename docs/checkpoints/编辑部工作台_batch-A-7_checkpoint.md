# Batch A-7：任务版本/回退 API Checkpoint

> **日期**: 2026-03-17
> **阶段包**: Batch A-7 任务版本/回退 API
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 修改文件

| 文件 | 变更 |
|------|------|
| `src/api/routes/tasks.py` | 新增版本查询和回退接口 |
| `tests/api/test_tasks.py` | 新增版本/回退测试用例（4 个） |

### 1.2 功能特性

1. **版本查询接口**：
   - 路径：`GET /v1/tasks/versions/{input_hash}`
   - 返回具有相同 input_hash 的所有任务版本

2. **回退接口**：
   - 路径：`POST /v1/tasks/{task_id}/rerun`
   - 基于历史任务的输入参数创建新任务
   - 记录审计事件关联原任务和新任务

## 2. 未完成项

无

## 3. 失败项与是否既有失败

无 P1/P2 问题。

## 4. 关键证据路径或命令

### 后端测试
```
pytest tests/api/test_tasks.py -v
# 16 passed in 0.83s

pytest tests -q
# 305 passed, 1 skipped, 3 warnings in 7.44s
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| 能按 input_hash 查询版本 | ✅ |
| 回退创建新任务 | ✅ |
| 不删除历史 | ✅ |

## 5. 双轮自审结果

### 第一轮：回退行为检查
- ✅ 回退创建新任务，保留原任务
- ✅ 新任务 metadata 记录 rerun_from
- ✅ 审计事件记录关联

### 第二轮：版本查询检查
- ✅ 按 input_hash 查询
- ✅ 返回所有匹配版本
- ✅ 不暴露敏感信息

### 自审结论
无 P1/P2 问题，符合执行单要求。

## 6. 下一步动作

A-7 已完成，可以进入：
- **A-8** 前端审查反馈入口（依赖 A-6）

## 7. 变更摘要

### 新增 API
```
GET /v1/tasks/versions/{input_hash}  # 查询版本
POST /v1/tasks/{task_id}/rerun       # 回退（创建新任务）
```

### 回退行为
- 新任务继承原任务的 input_data 和 input_hash
- 新任务 metadata 记录 `rerun_from` 指向原任务
- 审计事件记录 `task_rerun` 类型