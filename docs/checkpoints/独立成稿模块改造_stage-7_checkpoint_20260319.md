# 独立成稿模块改造 Stage Package 7 Checkpoint

> 日期：2026-03-19
> 阶段包：Stage Package 7 - 独立成稿模块改造
> 当前阶段：SP-7E - 总体验收、fix batch、文档收口
> 状态：✅ SP-7E 已闭合（前后端验收 + fix batch + 文档收口已完成）
> 修订：v1.6 (SP-7E Closure)

---

## 0. SP-7A 范围与目标

SP-7A 是独立成稿模块改造的第一阶段，目标是：

1. 用硬证据复核当前主链真实边界
2. 明确新模块命名、输入输出契约、插入点、主链改造方案
3. 识别受影响文件与测试面
4. 冻结设计，为 SP-7B 实现阶段提供明确蓝图

**门禁**：在"当前现状"和"目标链路"都写清楚前，不得进入实现。必须先给出 P1/P2 风险定性。

---

## 1. 当前标准链真实边界（代码证据）

### 1.1 当前标准链流程

**来源**：`src/orchestrator/service.py` 第 976-1250 行 `_execute_standard_chain()`

```
Evidence → Planning → Writing → Quality → Delivery
```

**各步骤产出（代码证据）**：

| 步骤 | 函数/行号 | 输出字段 | 是否包含 content |
|------|-----------|----------|------------------|
| **Evidence** | `_execute_standard_chain()` 1016-1071 | `fact_count`, `retrieval_trace` | ❌ 无 |
| **Planning** | `_execute_standard_chain()` 1073-1116 | `thesis`, `outline`, `play_id`, `arc_id`, `key_evidence` | ❌ 无 |
| **Writing** | `_execute_standard_chain()` 1118-1160 | `prompt_length`, `writing_trace` | ❌ 无（只有 prompts） |
| **Quality** | `_execute_standard_chain()` 1162-1193 | `overall_status` | ❌ 审的是 prompt |
| **Delivery** | `_execute_standard_chain()` 1195-1227 | `output_path`, `docx_path`, `final_docx_word_count` | ⚠️ **会生成 content** |

### 1.2 Writing 模块是 Prompt 编译器，不是成稿器

**证据**：`src/modules/writing/service.py`

**主入口函数**：
- `compile()` (第 23-71 行)
- `compile_with_evidence()` (第 73-108 行)
- `compile_with_trace()` (第 110-173 行)

**返回类型**：`CompiledPrompt`

```python
# src/modules/writing/models.py 第 145-162 行
@dataclass
class CompiledPrompt:
    system_prompt: str      # ← 系统指令字符串
    user_prompt: str        # ← 用户指令字符串
    model_config: Dict[str, Any]
    metadata: Dict[str, Any]
    # ❌ 没有 content 字段！
```

**结论**：Writing 只产出 `system_prompt` + `user_prompt`，不产出正文内容。

### 1.3 Delivery 模块兼任成稿

**证据**：`src/modules/delivery/docx_writer.py`

**触发条件**（第 105-114 行）：
```python
if content:
    # 使用提供的内容
    body_paragraphs = self._parse_content_to_paragraphs(doc, content)
else:
    # 从 thesis/outline/key_evidence 生成正文
    generated_paragraphs = self._generate_body_from_inputs(
        doc, thesis, outline, key_evidence
    )
```

**成稿函数**：`_generate_body_from_inputs()` (第 187-261 行)

该函数从 `thesis / outline / key_evidence` 生成确定性正文，包括：
- 引言
- 主要内容（按 outline 章节迭代）
- 核心证据列表
- 结论

**结论**：Delivery 在缺少 `content` 时会自动生成正文，这是成稿逻辑，不属于交付职责。

### 1.4 Quality 模块当前审的是 Prompt，不是正文

**证据**：`src/modules/quality/orchestrator.py`

**关键函数**：`run_gates()` (第 53-81 行)

```python
def run_gates(self, prompt: CompiledPrompt) -> QualityResult:
    # ...
    for gate in self.enabled_gates:
        gate_result = self._run_single_gate(gate, prompt)  # ← 传入 CompiledPrompt
```

**标准链中的调用**：`src/orchestrator/service.py` 第 1171 行

```python
quality_result = self.quality_orchestrator.run_gates(compiled_prompt)
```

**结论**：Quality 当前检查的是 `CompiledPrompt`（即 system_prompt + user_prompt），不是最终正文内容。

### 1.5 前端标准链页面没有 Drafting 步骤

**证据**：`frontend/src/components/forms/StandardChainConfigForm.tsx`

**当前步骤定义**（第 21 行）：
```typescript
type ChainStep = 'evidence' | 'planning' | 'writing' | 'quality' | 'delivery';
```

**步骤流转**（第 80 行）：
```typescript
const steps: ChainStep[] = ['evidence', 'planning', 'writing', 'quality', 'delivery'];
```

**Writing 步骤展示的内容**（第 191-204 行）：
```tsx
<WritingProgressView
  result={writingResult || undefined}  // ← CompiledPromptResponse
  plan={plan || undefined}
  onWriteComplete={handleWritingComplete}
/>
```

**结论**：前端没有 "Drafting" 步骤，Writing 展示的是 prompts（system_prompt + user_prompt），不是正文。

---

## 2. 目标链路设计

### 2.1 目标标准链

```
Evidence → Planning → Writing(编译) → Drafting(成稿) → Quality(审正文) → Delivery(交付)
```

### 2.2 新增 Drafting 模块设计

**模块名称**：`DraftingModule` / `DraftingService`

**位置**：`src/modules/drafting/`

**输入契约**：
```python
@dataclass
class DraftingInput:
    compiled_prompt: CompiledPrompt   # 来自 Writing
    writing_trace: WritingTrace       # 来自 Writing（可选）
    target_word_count: Optional[int]  # 目标字数（可选）
```

**输出契约**：
```python
@dataclass
class DraftingResult:
    content: str                      # ← 核心：生成的正文内容
    word_count: int                   # 正文字数
    generation_trace: Dict[str, Any]  # 生成追踪（可选）
    metadata: Dict[str, Any]          # 元数据
```

**插入点**：`src/orchestrator/service.py` `_execute_standard_chain()` 中，在 Writing 和 Quality 之间

### 2.3 Quality 改造设计

**变更**：从检查 `CompiledPrompt` 改为检查正文 `content`

**新输入契约**：
```python
def run_gates_on_content(self, content: str, ...) -> QualityResult:
    # 检查正文内容
```

**在标准链中的调用改为**：
```python
# 旧：quality_result = self.quality_orchestrator.run_gates(compiled_prompt)
# 新：quality_result = self.quality_orchestrator.run_gates_on_content(drafting_result.content)
```

### 2.4 Delivery 改造设计

**变更**：标准链主路径移除 `_generate_body_from_inputs()` 成稿职责，只保留交付职责

**新输入契约**：
```python
def create_delivery_result(
    self,
    thesis: str,
    outline: List[Dict[str, Any]],
    key_evidence: Optional[List[str]] = None,
    content: str,  # ← 必须提供，不再自动生成
    ...
) -> DeliveryResult:
```

**冻结口径**：
- 标准链主路径：`content` 视为必填，必须来自 `DraftingResult.content`
- direct `delivery` API：可在过渡期保留 `content` 为 Optional 以兼容旧调用，但缺少 `content` 的 fallback 仅限兼容路径，不再属于标准链设计

---

## 3. 受影响文件清单（精确清单）

### 3.1 后端 - 新增文件

| 文件路径 | 用途 | 行数估计 |
|----------|------|----------|
| `src/modules/drafting/__init__.py` | 模块入口，导出 DraftingService, DraftingInput, DraftingResult | ~10 |
| `src/modules/drafting/service.py` | DraftingService 实现：FakeLLM 确定性成稿 + OpenAI 真实成稿 | ~150 |
| `src/modules/drafting/models.py` | DraftingInput, DraftingResult, DraftingTrace 模型定义 | ~80 |
| `src/api/routes/drafting.py` | `/v1/drafting/generate` API 端点，含 TaskLogger 集成 | ~120 |
| `tests/modules/test_drafting.py` | Drafting 模块单元测试：Fake 模式确定性验证 | ~200 |
| `tests/integration/test_drafting_api.py` | Drafting API 集成测试：task_id 返回、错误处理 | ~150 |

### 3.2 后端 - 修改文件（精确行号引用）

| 文件路径 | 变更内容 | 关键行号 |
|----------|----------|----------|
| `src/contracts/base.py` | 添加 `ModuleName.DRAFTING = "drafting"` 枚举值 | 第 43-52 行 ModuleName 枚举 |
| `src/orchestrator/models.py` | ModuleTask.module_name Literal 添加 "drafting" | 第 39 行 Literal 类型 |
| `src/orchestrator/service.py` | 标准 Chain 插入 Drafting 步骤，修改 Quality/Delivery 调用；新增 `_execute_drafting()` 方法 | 第 976-1304 行 `_execute_standard_chain()` |
| `src/modules/quality/orchestrator.py` | 标准链中改用 `run_gates_on_content(content)` | 第 53-81 行 `run_gates()`、第 83-122 行 `run_gates_on_content()` |
| `src/modules/delivery/service.py` | 移除自动生成逻辑，content 参数逻辑调整 | 第 151-268 行 `create_delivery_result()` |
| `src/modules/delivery/docx_writer.py` | 移除 `_generate_body_from_inputs()` 或改为可选 fallback | 第 105-114 行、第 187-261 行 |
| `src/api/app.py` | 添加 drafting router 注册 | 第 78 行 import、第 89 行后 include_router |
| `src/api/routes/workflow.py` | StandardChainWorkflowResponse 添加 drafting 段；child_task_ids 从 5 个改为 6 个 | 第 184-209 行响应模型、第 315-388 行端点 |
| `tests/integration/test_standard_chain_api.py` | 添加 drafting 步骤断言；child_task_ids 长度断言改为 6 | 全文件 |
| `tests/modules/test_quality.py` | 更新测试用例：`run_gates_on_content` vs `run_gates` | 全文件 |
| `tests/modules/test_delivery.py` | 更新测试用例：content 必填化验证 | 全文件 |

### 3.3 前端 - 新增文件

| 文件路径 | 用途 |
|----------|------|
| `frontend/src/components/DraftingPanel.tsx` | 展示成稿结果的组件：content 预览、字数、继续按钮 |
| `frontend/src/api/drafting.ts` | Drafting API 客户端：`executeDrafting()` 函数 |

### 3.4 前端 - 修改文件（精确行号引用）

| 文件路径 | 变更内容 | 关键行号 |
|----------|----------|----------|
| `frontend/src/components/forms/StandardChainConfigForm.tsx` | ChainStep 类型添加 'drafting'；步骤流转数组添加 drafting；新增 draftingResult 状态；插入 DraftingPanel 组件 | 第 21 行 ChainStep、第 80 行 steps 数组、第 28 行状态定义、第 191-230 步骤渲染 |
| `frontend/src/components/WritingProgressView.tsx` | 组件职责明确：展示 prompts；在只有 plan 时显式提供“生成写作指令”入口 | 第 103 行后 onWriteComplete 按钮 |
| `frontend/src/components/DeliveryPanel.tsx` | content 参数来源改为 draftingResult.content；移除 user_prompt 作为 content 的 fallback | 第 59 行 content 使用、第 227 行传参 |
| `frontend/src/components/QualityReportView.tsx` | content 参数来源改为 draftingResult.content；审的是正文而非 prompts | 第 100-106 行内容预览 |
| `frontend/src/api/index.ts` | 添加 `export * from './drafting';` | 第 14 行后添加 |
| `frontend/src/test/SP3E2EAcceptance.test.ts` | 六段链 API 调用顺序从 5 步升级为 6 步，并补 drafting API 覆盖 | Standard Chain Flow Simulation 段 |
| `frontend/src/test/StandardChainConfigForm.test.tsx` | 新增组件级边界测试，锁定 Writing / Drafting / Quality / Delivery 的正文传递关系 | 全文件 |
| `frontend/src/types/extended.ts` | 添加 DraftingResponse 类型定义；WORKFLOW_ROUTES 更新模块列表 | 第 182 行后添加类型、第 160-182 行 WORKFLOW_ROUTES |

### 3.5 测试/契约/运行时日志 - 修改文件

| 文件路径 | 变更内容 | 关键行号 |
|----------|----------|----------|
| `tests/contracts/test_contract_shapes.py` | TestTaskTrace 使用 ModuleName.DRAFTING 验证新枚举值可用 | 第 60-86 行 TestTaskTrace |
| `tests/runtime_logging/test_contract_upgrade.py` | 测试 ModuleName.DRAFTING 在 TaskLogger.start_task 中可用 | 第 134-225 行 TestTaskLoggerUpgrade |

---

## 4. 风险清单（P1/P2 - 已精化）

### P1 风险（阻塞，必须解决）

| ID | 风险描述 | 影响 | 缓解措施 |
|----|----------|------|----------|
| **P1-1** | **Fake 模式确定性成稿**：DraftingService 需在 Fake 模式下返回确定性、可验证的正文内容，而非随机或空内容 | 后端测试套件无法验证 Drafting 输出 | DraftingService 支持 `FakeDraftingProvider`：根据 CompiledPrompt.user_prompt 生成确定性正文（如提取关键词 + 模板），确保每次调用相同输入返回相同输出 |
| **P1-2** | **Contract-TaskLog 传播**：新增 `ModuleName.DRAFTING` 枚举值需在 `src/contracts/base.py`、`src/orchestrator/models.py`、TaskLogger 调用链中保持一致 | 任务日志记录失败或类型错误 | 在 `src/contracts/base.py` 第 52 行添加 `DRAFTING = "drafting"`；在 `src/orchestrator/models.py` 第 39 行 Literal 添加 `"drafting"`；在 `_execute_standard_chain()` 中使用 `ModuleName.DRAFTING` |
| **P1-3** | **Quality 测试用例调整**：`tests/modules/test_quality.py` 需区分 `run_gates(prompt)` 和 `run_gates_on_content(content)` 两种调用路径 | 测试失败 | 保持两套测试：`test_run_gates_on_compiled_prompt` 和 `test_run_gates_on_content`，分别验证两种输入类型 |
| **P1-4** | **Delivery 契约双轨并存**：标准链要求 `content` 必填，但 direct `delivery` API 若保留兼容 fallback，必须明确与主路径隔离 | 实现边界漂移，SP-7B/7C 易回到 Delivery 兼任成稿 | 冻结为“标准链必传 `content`，direct API fallback 仅兼容旧调用且不得被标准链复用”；在实现与测试中分别覆盖两条路径 |

### P2 风险（重要，建议解决）

| ID | 风险描述 | 影响 | 缓解措施 |
|----|----------|------|----------|
| **P2-1** | **前端状态管理复杂度**：步骤增加后（5→6），StandardChainConfigForm 状态管理复杂度提升 | 前端维护 | 可考虑 useReducer 或状态机；当前 useState 可接受 |
| **P2-2** | **Drafting 生成时间**：真实 LLM 调用可能耗时较长（5-30秒），需考虑超时和用户体验 | 用户体验 | API 支持异步模式或增加超时配置；前端显示加载动画 |
| **P2-3** | **标准链 API 响应结构变化**：child_task_ids 从 5 个变为 6 个，可能影响下游消费者 | API 兼容性 | 文档说明响应结构变化；version bump |
| **P2-4** | **文档更新**：`写作系统全讲解.md`、`docs/archive/root-historical/长线程续接交接_20260318.md` 需同步修订 | 文档一致性 | SP-7E 阶段统一更新 |

---

## 5. 设计冻结确认

### 5.1 当前现状（已确认）

| 维度 | 当前状态 | 代码证据 |
|------|----------|----------|
| Writing 产出 | prompts (system_prompt + user_prompt) | `writing/models.py` CompiledPrompt 无 content 字段 |
| Quality 审查对象 | CompiledPrompt | `orchestrator.py` run_gates(prompt) |
| Delivery 职责 | 交付 + 成稿（兼任） | `docx_writer.py` _generate_body_from_inputs() |
| 前端步骤 | 5步（无 Drafting） | `StandardChainConfigForm.tsx` ChainStep 类型 |

### 5.2 目标链路（已冻结）

```
Evidence → Planning → Writing(编译) → Drafting(成稿) → Quality(审正文) → Delivery(交付)
```

### 5.3 契约冻结

**Drafting 模块契约**：
- 输入：`DraftingInput(compiled_prompt, writing_trace?, target_word_count?)`
- 输出：`DraftingResult(content, word_count, generation_trace?, metadata)`

**Quality 改造**：标准链中改用 `run_gates_on_content(drafting_result.content)`

**Delivery 改造**：标准链主路径必须传入 `content`；direct `delivery` API 是否保留 Optional fallback 仅作为兼容策略，不改变主路径冻结边界

### 5.4 Enum 冻结

```python
# src/contracts/base.py
class ModuleName(str, Enum):
    OPINION = "opinion"
    SEMANTIC_REVIEW = "semantic_review"
    WRITING = "writing"
    ORCHESTRATOR = "orchestrator"
    PLANNING = "planning"
    EVIDENCE = "evidence"
    QUALITY = "quality"
    DELIVERY = "delivery"
    DRAFTING = "drafting"  # ← 新增
```

---

## 6. 阶段闭合结论

Stage Package 7 已按执行单闭合，当前状态区分如下：

- `Implemented`：独立 Drafting 模块、标准六段链、前端成稿步骤、相关 API / 测试 / 文档都已落盘
- `Verified`：后端 focused suite、标准链 API 探针、前端 vitest、前端 build 都已直接重跑
- `Closed`：SP-7A ~ SP-7E 无未处理 P1/P2；checkpoint、handoff、`写作系统全讲解.md` 已同步回写

---

## Evidence Summary

1. `cmd.exe /c py -m pytest "D:\汇度编辑部1\侠客岛\tests\modules\test_drafting.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_drafting_api.py" -q` -> `31 passed, 5 warnings in 0.92s`
2. 进程内设置 `LLM_PROVIDER=openai` / `LLM_MODEL=gpt-4.1` 并 monkeypatch `create_llm_provider_from_env()` 后，`POST /v1/drafting/generate` 返回 `200 / openai / gpt-4.1 / mock openai content`
3. 直接探针 `POST /v1/drafting/generate` 携带未声明字段 `unexpected` 返回 `422 extra_forbidden`

---

## 状态

- [x] SP-7A：现状复核与设计冻结 ✅ **已完成**
- [x] SP-7A FIX1：精确文件清单、精化 P1/P2 风险 ✅ **已完成**
- [x] SP-7B：后端独立成稿模块与 API ✅ **已完成**
- [x] SP-7B FIX1：OpenAI gateway 路径 + strict request contract ✅ **已完成**
- [x] SP-7C：标准主编排链边界纠正 ✅ **已完成**
- [x] SP-7D：前端标准链页面改造 ✅ **已完成**
- [x] SP-7E：总体验收、fix batch、文档收口 ✅ **已完成**

**SP-7E 已闭合，stage_package_7_closed**

---

## SP-7C 实现记录

### 实现内容

SP-7C 将 Drafting 模块集成到标准六段链中，实现完整的 Evidence → Planning → Writing → Drafting → Quality → Delivery 链路。

**关键变更**：
1. **Drafting 集成**：在 Writing 和 Quality 之间插入 Drafting 子任务
2. **Quality 改造**：改用 `run_gates_on_content(drafting_result.content)` 审查正文，而非 prompts
3. **Delivery 改造**：标准链主路径接收 `content=drafting_result.content`，不再自动生成正文
4. **结果结构**：final_result 新增 drafting 段，child_task_ids 从 5 个变为 6 个

### 已修改文件

**后端修改文件**：
- `src/orchestrator/service.py` — 新增 `drafting_service` 初始化；`_execute_standard_chain()` 插入 Drafting 步骤；Quality 改用 `run_gates_on_content()`；Delivery 接收 `drafting_result.content`；新增 `_execute_drafting()` 方法
- `src/api/routes/workflow.py` — 更新请求/响应模型注释（五段链→六段链）

**测试修改文件**：
- `tests/integration/test_standard_chain_api.py` — 更新断言（5→6）；新增 `TestStandardChainDraftingSP7C` 测试类

### SP-7C 验收结果

```bash
cmd.exe /c py -m pytest "D:\汇度编辑部1\侠客岛\tests\modules\test_writing.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_quality.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_delivery.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_standard_chain_api.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_workflow_api.py" -q
# 135 passed, 5 warnings in 15.26s
```

### 关键实现验证

1. **标准链返回 drafting 段**：API 直接探针返回 `200`，`child_task_ids` 长度为 `6`，模块顺序为 `Evidence → Planning → Writing → Drafting → Quality → Delivery`
2. **drafting 结果独立暴露**：API 直接探针回读 `data["result"]["drafting"]` 键为 `content_length / trace / word_count`
3. **Quality 审查正文**：`src/orchestrator/service.py` 调用 `run_gates_on_content(drafting_result.content)` 而非 `run_gates(compiled_prompt)`
4. **Delivery 接收正文**：`src/orchestrator/service.py` 调用 `create_delivery_result(..., content=drafting_result.content)`

### Evidence Summary

1. `cmd.exe /c py -m pytest "D:\汇度编辑部1\侠客岛\tests\modules\test_writing.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_quality.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_delivery.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_standard_chain_api.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_workflow_api.py" -q` -> `135 passed, 5 warnings in 15.26s`
2. `cmd.exe /c py -c "from fastapi.testclient import TestClient; from src.api.app import app; ..."` -> `200 / 6 / ['evidence', 'planning', 'writing', 'drafting', 'quality', 'delivery'] / ['content_length', 'trace', 'word_count'] / passed / docx_body`
3. 代码读回确认 `src/orchestrator/service.py` 走 `run_gates_on_content(drafting_result.content)` 与 `create_delivery_result(..., content=drafting_result.content)`

### SP-7C Fix Batch

**清理残留文本**：
- `tests/integration/test_standard_chain_api.py` — 更新类 docstring（TestStandardChainWithLecanemab: 五段链→六段链）；更新测试注释（Writing -> Quality → Writing -> Drafting -> Quality）
- `src/orchestrator/service.py` — 更新模块 docstring（五段链→六段链）
- `src/api/routes/workflow.py` — 更新错误消息（五段链→六段链）

**验收结果**：
```bash
cmd.exe /c py -m pytest "D:\汇度编辑部1\侠客岛\tests\modules\test_writing.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_quality.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_delivery.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_standard_chain_api.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_workflow_api.py" -q
# 135 passed, 5 warnings in 15.26s
```

---

## SP-7D 实现记录

### 实现内容

SP-7D 将前端标准链页面升级为真实六段链，并在 Codex 独立 review 后补了一轮 fix batch，修正前端链路里的两个真实问题：

1. `WritingProgressView` 在只有 `plan` 时没有触发写作编译的入口，页面会卡在写作步骤
2. `StandardChainConfigForm` 在成稿完成后未持久化 `draftingResult`，导致 Quality / Delivery 拿不到正文内容

### 已修改文件

- `frontend/src/components/forms/StandardChainConfigForm.tsx` — 六段链步骤、`draftingResult` 状态持久化、Quality/Delivery 统一消费 `draftingResult.content`
- `frontend/src/components/WritingProgressView.tsx` — 明确“生成写作指令”按钮语义，避免把 Prompt 编译误写成正文生成
- `frontend/src/components/DraftingPanel.tsx` — 统一“成稿”术语，保留 `/v1/drafting/generate` 契约
- `frontend/src/components/QualityReportView.tsx` — 待执行文案改为“请先完成成稿”
- `frontend/src/test/SP3E2EAcceptance.test.ts` — 六段链 API 调用顺序改为 6 步，并补 `/v1/drafting/generate`
- `frontend/src/test/StandardChainConfigForm.test.tsx` — 新增组件级边界测试，锁定正文从 Drafting 流向 Quality/Delivery

### SP-7D 验收结果

```bash
cd frontend
npm run test:run -- src/test/SP3E2EAcceptance.test.ts src/test/StandardChainConfigForm.test.tsx
# 2 passed files, 10 passed tests

npm run test:run
# 7 passed files, 43 passed tests

npm run build
# vite build success
```

### Evidence Summary

1. `npm run test:run -- src/test/SP3E2EAcceptance.test.ts src/test/StandardChainConfigForm.test.tsx` -> `2 passed files / 10 passed tests`
2. `npm run test:run` -> `7 passed files / 43 passed tests`；`npm run build` -> `vite build success`
3. 代码读回确认 `frontend/src/components/forms/StandardChainConfigForm.tsx` 现在持久化 `draftingResult`，并把 `draftingResult.content` 传给 `QualityReportView` 与 `DeliveryPanel`

---

## SP-7E 总体验收与文档收口

### 两轮 review 结论

**Round 1: 代码级 review**

- 发现并修复 `WritingProgressView` 缺失写作触发入口
- 发现并修复 `StandardChainConfigForm` 未写回 `draftingResult` 的正文丢失问题
- 补齐前端 API / 组件边界测试

**Round 2: 集成 review**

- 后端 focused suite 复验通过
- 标准链 API 探针确认仍为 `Evidence → Planning → Writing → Drafting → Quality → Delivery`
- 前端 vitest/build 通过，且 `写作系统全讲解.md`、`docs/archive/root-historical/长线程续接交接_20260318.md`、本 checkpoint 已同步回写

### SP-7E 闭合判断

- 无未处理 P1/P2
- 前端不再把 Prompt 伪装成正文传给 Quality / Delivery
- 文档口径不再把 Delivery 描述成标准主线中的成稿环节

### Evidence Summary

1. `cmd.exe /c py -m pytest "D:\汇度编辑部1\侠客岛\tests\modules\test_writing.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_quality.py" "D:\汇度编辑部1\侠客岛\tests\modules\test_delivery.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_standard_chain_api.py" "D:\汇度编辑部1\侠客岛\tests\integration\test_workflow_api.py" -q` -> `135 passed, 5 warnings in 14.51s`
2. `cmd.exe /c py -c "from fastapi.testclient import TestClient; from src.api.app import app; ..."` -> `200 / 6 / ['evidence', 'planning', 'writing', 'drafting', 'quality', 'delivery'] / ['content_length', 'trace', 'word_count'] / passed / docx_body`
3. `cd frontend && npm run test:run && npm run build` -> `7 passed files / 43 passed tests` 且 `vite build` 成功；相关文档已读回确认更新到“标准六段链”真实口径

---

## SP-7B 实现记录

### 已实现文件

**后端新增文件**：
- `src/modules/drafting/__init__.py` — 模块入口，导出 DraftingService, DraftingInput, DraftingResult, DraftingTrace
- `src/modules/drafting/models.py` — DraftingInput, DraftingResult, DraftingTrace 数据模型
- `src/modules/drafting/service.py` — DraftingService 实现：Fake 模式确定性成稿 + OpenAI 真实成稿
- `src/api/routes/drafting.py` — `/v1/drafting/generate` API 端点，含 TaskLogger 集成

**后端修改文件**：
- `src/contracts/base.py` — 添加 `ModuleName.DRAFTING = "drafting"` 枚举值
- `src/orchestrator/models.py` — ModuleTask.module_name Literal 添加 "drafting"
- `src/api/app.py` — 添加 drafting router 注册

**测试新增文件**：
- `tests/modules/test_drafting.py` — Drafting 模块单元测试（17 tests）
- `tests/integration/test_drafting_api.py` — Drafting API 集成测试（11 tests）

### SP-7B 验收结果

```
tests/modules/test_drafting.py: 17 passed in 0.17s
tests/integration/test_drafting_api.py: 11 passed, 5 warnings in 1.52s
tests/contracts/test_contract_shapes.py::TestTaskTrace: 2 passed
tests/runtime_logging/test_contract_upgrade.py: 20 passed in 0.15s

SP-7B focused total: 28 passed, 5 warnings in 0.82s
```

### 关键实现验证

1. **Fake 模式确定性成稿**：DraftingService 在 Fake 模式下返回确定性正文，相同输入产生相同输出
2. **Contract-TaskLog 传播**：`ModuleName.DRAFTING` 枚举值可在 TaskLogger.start_task 中使用
3. **API 端点功能**：`/v1/drafting/generate` 返回 task_id、content、word_count、trace
4. **向后兼容**：standard_chain、Quality、Delivery 主路径行为未改变

### SP-7B 门禁验证

- [x] `tests/modules/test_drafting.py` 通过
- [x] `tests/integration/test_drafting_api.py` 通过
- [x] `src/contracts/base.py` ModuleName.DRAFTING 枚举值存在
- [x] API 契约可读："这是成稿结果"（content 字段明确）

---

## SP-7B FIX1 实现记录

### 修复内容

**问题 1：`/v1/drafting/generate` 在 LLM_PROVIDER=openai 时静默返回 fake 成稿**

**修复**：
- `src/api/routes/drafting.py` 在 `openai` 模式下显式通过 `create_llm_provider_from_env()` 创建 gateway，并注入 `DraftingService(llm_gateway=..., default_mode="openai")`
- `src/modules/drafting/service.py` 保留 `_generate_with_fake()` 确定性本地成稿逻辑
- `src/modules/drafting/service.py` 新增显式 `_generate_with_openai()` gateway 路径；只有 `default_mode="openai"` 才会调用该路径

**证据**：
- 进程内设置 `LLM_PROVIDER=openai` / `LLM_MODEL=gpt-4.1` 并 monkeypatch `create_llm_provider_from_env()` 后，`POST /v1/drafting/generate` 返回 `generation_mode=openai`
- fake 默认路径下，相同输入仍返回相同正文和相同 `deterministic_seed`

**问题 2：Drafting 请求契约未拒绝未声明字段**

**修复**：
- API route 改为复用 `src/modules/drafting/models.py` 中已声明 `extra="forbid"` 的 `DraftingRequest`
- 未声明字段现在直接返回 `422 extra_forbidden`

**证据**：
- 直接探针 `POST /v1/drafting/generate` 携带 `unexpected` 字段返回 `422 extra_forbidden`
- `tests/integration/test_drafting_api.py` 已补充 strict request contract 覆盖

### SP-7B FIX1 新增测试

**tests/modules/test_drafting.py**：
- `TestDraftingOpenAIGatewayPath` - 验证 openai 模式使用 gateway，且不依赖真实 OpenAI 调用
- 保留原有 Fake 模式确定性成稿与 helper 覆盖

**tests/integration/test_drafting_api.py**：
- `TestDraftingAPIValidation.test_extra_field_rejected` - 验证 extra-field rejection
- `TestDraftingOpenAIGatewayPath` - 验证 API openai gateway 路径（mock provider）

### SP-7B FIX1 验收结果

```bash
tests/modules/test_drafting.py + tests/integration/test_drafting_api.py
31 passed, 5 warnings in 0.92s

python probe (LLM_PROVIDER=openai, mock provider): 200 / openai / gpt-4.1 / mock openai content
python probe (extra field): 422 extra_forbidden
```

### 关键验证（基于实测，无过度声明）

1. **OpenAI gateway 路径验证**：openai 模式下返回 `generation_mode=openai`，不再静默回落到 fake
2. **Strict request contract**：未声明字段返回 `422 extra_forbidden`
3. **确定性成稿保持不变**：Fake 模式下相同输入仍产生相同正文和相同 `deterministic_seed`

### 不宣称事项

- 未宣称进行了真实 OpenAI API 调用
- 未宣称验证了 OpenAI API 密钥有效性
- 未宣称在生产环境测试了 openai 模式
