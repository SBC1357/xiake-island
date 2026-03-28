# 写作质量交付闭环 Stage Package 2 Checkpoint

> **日期**: 2026-03-18
> **阶段包**: Stage Package 2 - 写作 + 质量 + 交付 + 标准链闭环
> **状态**: ✅ 2026-03-19 补充复核后，SP-2 尾项已闭合
> **修订**: v1.3 - 补录 `test_query_returns_latest_tasks` 尾项闭合证据

---

## 0. 2026-03-19 补充闭合记录

### 0.1 本次闭合对象

- `tests/integration/test_opinion_api.py::TestTaskLogTraceability::test_query_returns_latest_tasks`

### 0.2 定性

- 本轮按实测定性为：`测试隔离 / 共享状态问题`
- 当前没有硬证据要求修改生产逻辑；修复落在测试侧隔离
- 具体修复不改应用运行逻辑，只隔离测试使用的共享 task logger

### 0.3 修复内容

- 修改文件：`tests/integration/test_opinion_api.py`
- 新增 `isolated_task_logger` fixture
- 使用 `TaskLogger(MemoryTaskLogStore())` + `patch('src.api.app._shared_task_logger', isolated)`，让 `TestTaskLogTraceability` 3 个用例在进程内使用同一个隔离 logger
- `test_query_returns_latest_tasks` 不再依赖共享 SQLite 任务库

### 0.4 串行验收结果

```bash
python -m pytest tests/modules/test_quality.py -q
# 10 passed in 0.11s

python -m pytest tests/integration/test_opinion_api.py::TestTaskLogTraceability::test_query_returns_latest_tasks -q
# 1 passed, 5 warnings in 0.67s

python -m pytest tests -q
# 387 passed, 1 skipped, 5 warnings in 12.43s
```

### 0.5 验收结论

- 该尾项已按“修复并重测”路径闭合
- 就本次执行边界而言，`SP-2` 不再被该项阻断
- 本文档只记录 `SP-2` 收口，不在此处自动启动 `SP-3`

### 0.6 Evidence Summary

1. `ses_2fe1dd9c4ffexRBDDx1ZEL2orx` 导出显示：修复机制为 `TaskLogger(MemoryTaskLogStore())` + patch `src.api.app._shared_task_logger`。
2. `python -m pytest tests/integration/test_opinion_api.py::TestTaskLogTraceability::test_query_returns_latest_tasks -q`：`1 passed, 5 warnings in 0.67s`。
3. `python -m pytest tests -q`：`387 passed, 1 skipped, 5 warnings in 12.43s`。

---

## 1. 完成项

### 1.1 新增文件

| 文件 | 说明 |
|------|------|
| `src/api/routes/writing.py` | 写作生成 API 路由 |
| `src/api/routes/quality.py` | 质量审校 API 路由 |
| `src/api/routes/delivery.py` | 交付 API 路由 |

### 1.2 修改文件

| 文件 | 说明 |
|------|------|
| `src/api/app.py` | 注册新路由 |
| `src/orchestrator/service.py` | 扩展支持标准五段链 |
| `src/orchestrator/models.py` | 支持 standard_chain 工作流 |
| `src/api/routes/workflow.py` | **新增** POST /v1/workflow/standard-chain 路由 |

### 1.3 功能特性

#### Writing API 端点
- `POST /v1/writing/draft`: 编译写作草稿 Prompt ✅
- `POST /v1/writing/draft-with-evidence`: 编译带证据的草稿 ✅
- `GET /v1/writing/health`: 健康检查 ✅

#### Quality API 端点
- `POST /v1/quality/review`: 审核内容质量 ✅
- `POST /v1/quality/semantic-check`: 语义检查 ✅
- `GET /v1/quality/health`: 健康检查 ✅

#### Delivery API 端点
- `POST /v1/delivery/deliver`: 交付内容生成 Markdown ✅
- `GET /v1/delivery/history`: 获取交付历史 ✅
- `GET /v1/delivery/artifact/{filename}`: 下载交付产物 ✅
- `GET /v1/delivery/health`: 健康检查 ✅

#### Standard Chain 工作流 API
- `POST /v1/workflow/standard-chain`: 执行标准五段链 ✅ **[P1 修复后新增]**

### 1.4 标准五段链工作流

**工作流名称**: `standard_chain`

**执行步骤**:
1. **Evidence** - 查询证据：从藏经阁读取产品证据
2. **Planning** - 生成编辑计划：基于证据生成论点和大纲
3. **Writing** - 编译 Prompt：将计划编译为 LLM 可执行的 prompt
4. **Quality** - 质量门禁：运行质量检查，失败时阻断交付
5. **Delivery** - 交付：生成 Markdown 文件

**触发方式**:
```json
POST /v1/workflow/standard-chain
{
  "product_id": "lecanemab",
  "domain": "efficacy",
  "register": "R2",
  "audience": "医学专业人士"
}
```

### 1.5 模块接入方式

| 模块 | 现有代码 | 接入方式 |
|------|----------|----------|
| Writing | WritingService 已实现 | 复用，创建 API 路由 |
| Quality | QualityOrchestrator 已实现 | 复用，创建 API 路由 |
| Delivery | MarkdownWriter 已实现 | 复用，创建 API 路由 |
| Orchestrator | 扩展支持 standard_chain | 新增工作流路由 |

---

## 2. 发现与修复的问题

### P1: standard_chain 未暴露为公开 API

**问题描述**:
- `standard_chain` 仅在 `OrchestratorService._execute_standard_chain()` 内部实现
- `src/api/routes/workflow.py` 只有 `/v1/workflow/article` 和 `/v1/workflow/knowledge-assets`
- `POST /v1/workflow/standard-chain` 返回 404

**修复内容** (`src/api/routes/workflow.py`):
1. 新增 `StandardChainWorkflowRequest` 请求模型 (行 145-170)
2. 新增 `StandardChainWorkflowResponse` 响应模型 (行 173-198)
3. 新增 `POST /v1/workflow/standard-chain` 端点 (行 329-430)

**验证结果**:
```
POST /v1/workflow/standard-chain
Status: 200
task_id: f99ef1ae-73d0-4015-92e2-2c2cb7cb92ce
status: completed
child_task_ids count: 5
```

---

## 3. 未完成项

| 项目 | 说明 | 优先级 |
|------|------|--------|
| 新模块 API 接入编排器统一任务日志 | writing/quality/delivery API 直接调 service，未走 orchestrator 跟踪 | P2 |
| 集成测试覆盖 | 新增 API 和 standard_chain 缺少集成测试 | P2 |
| _execute_module 扩展 | 只支持 opinion/semantic_review，模型声明 6 模块 | P2 |

---

## 4. 关键证据路径或命令

### 后端测试
```
pytest tests -q
# 358 passed, 1 skipped, 5 warnings in 8.50s
```

### 前端测试
```
npm run test:run
# 33 passed (5 test files)

npm run build
# built in 176ms
```

### API 路由验证
```
Writing API:
  /v1/writing/draft
  /v1/writing/draft-with-evidence
  /v1/writing/health

Quality API:
  /v1/quality/review
  /v1/quality/semantic-check
  /v1/quality/health

Delivery API:
  /v1/delivery/deliver
  /v1/delivery/history
  /v1/delivery/artifact/{filename}
  /v1/delivery/health

Workflow API:
  /v1/workflow/article
  /v1/workflow/standard-chain  # 新增
  /v1/workflow/knowledge-assets
```

### 支持的工作流
```
article: opinion -> semantic_review
standard_chain: Evidence -> Planning -> Writing -> Quality -> Delivery
```

---

## 5. 自审结果

### 已验证项

| 检查项 | 结果 |
|--------|------|
| Writing API 可用 | ✅ POST /v1/writing/draft |
| Quality API 可用 | ✅ POST /v1/quality/review |
| Delivery API 可用 | ✅ POST /v1/delivery/deliver |
| standard_chain 公开 API | ✅ POST /v1/workflow/standard-chain 返回 200 |
| 标准五段链执行成功 | ✅ 5 个 child_task_ids |
| 模块复用而非重写 | ✅ |
| 无新路径硬编码 | ✅ |

### 待改进项

| 检查项 | 当前状态 |
|--------|----------|
| 新模块 API 走 orchestrator 跟踪 | ❌ 直接调 service |
| 集成测试覆盖 | ❌ 缺失 |
| _execute_module 支持 6 模块 | ❌ 只支持 2 模块 |

---

## 6. SP-2 退出门禁检查

| 门禁条件 | 状态 |
|----------|------|
| Writing API 可用 | ✅ |
| Quality API 可用 | ✅ |
| Delivery API 可用 | ✅ |
| standard_chain 公开 API | ✅ P1 已修复 |
| 后端测试通过 | ✅ 358 passed |
| P1 问题已修复 | ✅ |
| 剩余 P2 已记录 | ✅ API 跟踪、测试覆盖、模块扩展 |

---

## 7. 下一步动作

**从本 checkpoint 的已执行门禁看，SP-2 已无当前已知阻断项；是否进入 SP-3，需以下一轮调度为准。**

### SP-3 任务预览
1. 证据查询面板（EvidenceQueryPanel）
2. 规划配置表单（PlanningConfigForm）
3. 写作进度视图（WritingProgressView）
4. 质量报告视图（QualityReportView）
5. 交付物下载面板（DeliveryPanel）

### 残留 P2 建议处理顺序
1. 集成测试覆盖（建议 SP-3 之前或并行）
2. 新模块 API 接入 orchestrator 跟踪
3. _execute_module 扩展支持 6 模块

---

> **文档版本**: v1.3
> **创建日期**: 2026-03-18
> **修订日期**: 2026-03-19
> **编写者**: Sisyphus Agent
> **修订说明**: 补录 `test_query_returns_latest_tasks` 尾项闭合证据，记录测试隔离修复与串行验收结果
