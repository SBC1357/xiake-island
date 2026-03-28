# Batch C-1：历史/反馈/回退 UI 统一收口 Checkpoint

> **日期**: 2026-03-17
> **阶段包**: Batch C-1 历史/反馈/回退 UI 统一收口
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 修改文件

| 文件 | 变更 |
|------|------|
| `frontend/src/api/tasks.ts` | 新增 rerunTask、getTaskVersions API |
| `frontend/src/components/HistoryPanel.tsx` | 新增重新执行功能 |
| `frontend/src/pages/TriggerPage.tsx` | 新增 handleRerun 回调 |

### 1.2 功能特性

1. **任务历史面板增强**：
   - 显示任务 ID 和输入哈希
   - 加载参数到表单
   - 重新执行任务（回退）

2. **回退功能**：
   - 确认对话框：提示用户将创建新任务
   - 执行状态显示
   - 成功后显示新任务 ID

3. **API 扩展**：
   - `rerunTask(taskId)`: 调用回退 API
   - `getTaskVersions(inputHash)`: 查询版本列表

## 2. 未完成项

- 版本查询 UI（P2 优先级，未在 C-1 范围）

## 3. 失败项与是否既有失败

无 P1/P2 问题。

## 4. 关键证据路径或命令

### 前端测试
```
npm run lint
# 无错误

npm run test:run
# 33 passed in 2.54s
```

### 后端测试
```
pytest tests -q
# 347 passed, 1 skipped, 4 warnings in 7.57s
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| 查看历史 | ✅ HistoryPanel 显示任务列表 |
| 加载参数 | ✅ 点击"加载参数到表单"填充表单 |
| 修改 | ✅ 基于 basedOnTaskId 标记 |
| 再执行 | ✅ 点击"重新执行"创建新任务 |
| 提交反馈 | ✅ FeedbackForm 已集成到 ResultActions |

## 5. 双轮自审结果

### 第一轮：编辑工作流检查
- ✅ 历史面板操作流程清晰
- ✅ 回退有确认提示
- ✅ 操作结果有反馈

### 第二轮：UI 一致性检查
- ✅ 按钮样式一致
- ✅ 状态提示清晰
- ✅ 错误处理完善

### 自审结论
无 P1/P2 问题，符合执行单要求。

## 6. 下一步动作

C-1 已完成，可以进入：
- **C-2** 新能力前端入口（依赖 C-0 ✅, B-2 ✅）