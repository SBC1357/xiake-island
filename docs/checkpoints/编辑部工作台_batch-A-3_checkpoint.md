# Batch A-3：前端任务历史面板 Checkpoint

> **日期**: 2026-03-17
> **阶段包**: Batch A-3 前端任务历史面板
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 新增文件

| 文件 | 说明 |
|------|------|
| `frontend/src/hooks/useTaskHistory.ts` | 任务历史查询 Hook，支持缓存 |
| `frontend/src/components/HistoryPanel.tsx` | 任务历史面板组件 |
| `frontend/src/test/useTaskHistory.test.ts` | Hook 测试（5 个用例） |
| `frontend/src/test/HistoryPanel.test.tsx` | 组件测试（4 个用例） |

### 1.2 修改文件

| 文件 | 变更 |
|------|------|
| `frontend/src/hooks/index.ts` | 导出 useTaskHistory |
| `frontend/src/api/index.ts` | 导出 tasks API |
| `frontend/src/pages/TriggerPage.tsx` | 集成 HistoryPanel |

### 1.3 功能特性

1. **任务列表显示**：显示历史任务，包含模块、状态、时间
2. **任务详情查看**：点击任务可查看详情
3. **参数加载**：点击"加载参数到表单"可填充对应表单
4. **自动缓存**：全局缓存 5 秒，详情缓存永不过期（组件生命周期内）
5. **刷新功能**：手动刷新按钮

## 2. 未完成项

无

## 3. 失败项与是否既有失败

无 P1/P2 问题。

### 既有问题（非本次引入，非阻塞）
- `SemanticReviewInput` 字段名 `register` 与父类属性冲突警告

## 4. 关键证据路径或命令

### 前端测试
```
npm run lint
# 无错误

npm run test:run
# 33 passed in 1.76s

npm run build
# built in 205ms
```

### 后端测试
```
pytest tests -q
# 293 passed, 1 skipped, 3 warnings in 7.90s
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| 前端能显示历史任务 | ✅ |
| 点击能填充表单 | ✅ |
| 不在每次渲染时重请求 | ✅ 全局缓存 5 秒 |
| 不暴露原始 JSON | ✅ 仅显示格式化信息 |
| 不阻塞主界面 | ✅ 异步加载 |

## 5. 双轮自审结果

### 第一轮：缓存合理性检查
- ✅ 全局任务列表缓存（5 秒 TTL）
- ✅ 任务详情缓存（Map 结构，组件生命周期内有效）
- ✅ 缓存命中时不发起请求

### 第二轮：原始 JSON 暴露检查
- ✅ 不直接暴露原始 JSON
- ✅ 显示格式化的模块名、状态标签
- ✅ 参数加载内部处理，用户看到的是填充后的表单

### 自审结论
无 P1/P2 问题，符合执行单要求。

## 6. 下一步动作

A-3 已完成，可以进入：
- **A-4** 前端结果查看器增强（无依赖，可并行）
- **A-5** 前端修改参数再生成（依赖 A-2, A-3）

## 7. 变更摘要

### 新增 Hook
```typescript
useTaskHistory(options?: {
  refreshInterval?: number;
  defaultParams?: TasksQueryParams;
  autoLoad?: boolean;
}): {
  tasks: TaskListItem[];
  total: number;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  getDetail: (taskId: string) => Promise<TaskDetail | null>;
  detailCache: Map<string, TaskDetail>;
  lastRefreshedAt: Date | null;
}
```

### 新增组件
```typescript
<HistoryPanel
  onLoadParams={(module, params) => void}
  maxHeight?: string
/>
```

### 集成点
- TriggerPage 右侧栏添加 HistoryPanel
- 点击任务加载参数时自动切换到对应目标并填充表单