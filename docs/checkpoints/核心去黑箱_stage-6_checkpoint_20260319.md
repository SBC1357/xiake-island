# 核心去黑箱 Stage Package 6 Checkpoint

> 日期：2026-03-19
> 阶段包：Stage Package 6 - 核心去黑箱与正式交付
> 状态：✅ 已闭合（Batch 6A、6B、6C、6D 已实现并验证）
> 修订：v1.2

---

## 0. 本次 checkpoint 范围

本 checkpoint 当前覆盖：

- `SP-6 Batch 6A：显式取证 / 数据编排去黑箱`
- `SP-6 Batch 6B：规则执行引擎落地`
- `SP-6 Batch 6C：写作 / 审核主链去黑箱`
- `SP-6 Batch 6D：docx 正式交付与终版字数门禁`

本 checkpoint 当前宣称范围仅限 `SP-6` 本阶段，不外推到后续未定义阶段。

## 1. 已实现内容

### 1.1 retrieval/query trace 模型已落地

已新增 `src/modules/evidence/retrieval_trace.py`，包含：

- `QueryInput`
- `FilterDecision`
- `RankingDecision`
- `DedupDecision`
- `SelectionDecision`
- `SufficiencyJudgment`
- `RetrievalTrace`
- `EvidenceResultWithTrace`

### 1.2 EvidenceService 已能返回显式检索追踪

`src/modules/evidence/service.py` 已新增 `resolve_facts_with_trace()`，当前可显式记录：

- 查询输入
- 候选数量
- 过滤前后变化
- 去重与排序决策
- 最终入选条数与选择原因
- `sufficiency_judgment`
- `duration_ms`

同时保留原有 `resolve_facts()` 行为，不以本批次直接替换旧接口返回类型。

### 1.3 standard_chain 已暴露 retrieval_trace

`src/orchestrator/service.py` 的 `standard_chain` Evidence 步骤已改为调用 `resolve_facts_with_trace()`。

当前 retrieval trace 已能在以下位置回读：

- `child_results` 中的 evidence 子任务结果
- `result.evidence` 最终结果

### 1.4 focused tests 已补齐

已补 focused tests：

- `tests/modules/test_evidence.py`
- `tests/integration/test_standard_chain_api.py`

当前覆盖到：

- trace 查询输入
- 候选数量字段
- 过滤决策字段
- 选择决策字段
- `sufficiency_judgment`
- `standard_chain` 最终结果 / 子任务结果中的 retrieval trace

### 1.5 规则执行引擎已落地

已新增 `src/rules/` 模块，当前包含：

- `src/rules/models.py`
- `src/rules/engine.py`
- `src/rules/families/register_levels.py`
- `src/rules/families/expression_base.py`
- `src/rules/families/medical_syntax_rules.py`
- `src/rules/families/thesis_derivation_rules.py`
- `src/rules/adapters/m5_compliance_adapter.py`
- `src/rules/__init__.py`

当前规则执行引擎可产出 rule-level trace，至少包含：

- `matched`
- `failed`
- `skipped`
- `errors`
- `reason`
- `duration_ms`

### 1.6 QualityOrchestrator 已暴露 rule_trace

`src/modules/quality/orchestrator.py` 已新增：

- `rule_trace` 属性
- `run_rules()`
- `run_gates_with_rules()`

当前规则执行结果已可落入程序输出 / 结果 metadata，不再只存在模型口头描述。

### 1.7 SemanticReviewer 已区分规则层与模型层

`src/modules/semantic_review/reviewer.py` 当前会先执行确定性规则层，再进入 LLM 审校层。

`src/modules/semantic_review/models.py` 已新增：

- `SemanticReviewOutput.rule_layer_output`

当前至少能区分：

- 规则层输出
- 模型层输出

### 1.8 Batch 6B focused tests 已补齐

已新增：

- `tests/rules/test_rule_engine.py`

并通过现有质量 / 审核 / 集成链路复验，确保 `6B` 不是只在孤立单测里通过。

### 1.9 WritingTrace 与 `compile_with_trace()` 已落地

`src/modules/writing/models.py` 当前已显式定义：

- `PlanningConstraintsTrace`
- `EvidenceAnchor`
- `WritingTrace`
- `CompiledPromptWithTrace`

`src/modules/writing/service.py` 当前已新增 `compile_with_trace()`，会把以下信息显式写入程序输出：

- 规划约束
- 证据锚点
- 已应用规则 ID
- 已应用风格 ID
- 硬性约束
- 建议性约束

### 1.10 standard_chain 已暴露 `writing_trace`

`src/orchestrator/service.py` 的 `standard_chain` Writing 步骤当前已改为调用 `compile_with_trace()`。

当前 `writing_trace` 已可在以下位置回读：

- `child_results` 中的 writing 子任务结果
- `result.writing` 最终结果

### 1.11 SemanticReviewer 已显式暴露审核三层输出

`src/modules/semantic_review/reviewer.py` 当前除规则层输出外，还会显式写出：

- `model_review_output`
- `rewrite_layer_output`
- `rerun_scope`

当前审核链已可区分：

- 确定性规则层输出
- 模型审校层输出
- 改写建议层输出
- 改写后应重跑的 gate 范围

### 1.12 `semantic_review` / `workflow` API 已透出审核分层结果

当前以下 API 路径都已把三层输出与重跑范围暴露到响应：

- `src/api/routes/semantic_review.py`
- `src/api/routes/workflow.py`

当前 `article workflow` 响应已可在以下层级回读：

- 顶层响应字段
- `result`
- `child_results[].result` 中的 `semantic_review` 子结果

### 1.13 Batch 6C focused + 集成验收已补齐

当前 `Batch 6C` 已直接覆盖到：

- `tests/modules/test_planning.py`
- `tests/modules/test_writing.py`
- `tests/integration/test_standard_chain_api.py`
- `tests/test_semantic_review.py`
- `tests/integration/test_semantic_review_api.py`
- `tests/integration/test_workflow_api.py`

当前验收已覆盖：

- `writing_trace` 结构
- 规划约束与证据锚点
- `standard_chain` 中的 writing 子结果暴露
- 语义审核三层输出
- `article workflow` 顶层 / result / child result 的审核分层输出
- `rerun_scope`

### 1.14 `docx` 正式交付与终版字数门禁已落地

当前 `src/modules/delivery/service.py` 已把交付主路径改为：

- Markdown 仅作为预览产物
- Python 生成的 `docx` 作为正式输出
- `output_path` 指向 `docx`
- `artifacts` 同时保留 `.md` 与 `.docx`

当前以下字段已进入程序输出与 API / 工作流结果：

- `markdown_preview_path`
- `docx_path`
- `final_docx_word_count`
- `word_count_basis`
- `target_word_count`
- `word_count_gate_passed`

当前 `docx` 正文字数门禁已以后置 `docx_body` 口径执行；低于阈值时，`delivery` API 会返回 `word_count_gate_failed`。

为解决 Windows 下同一秒内重复交付请求的文件名碰撞，当前交付文件名已增加短 UUID 后缀；同一请求内的 `.md` 与 `.docx` 仍共用同一基础文件名。

当前已补回归测试到 `tests/modules/test_delivery.py`，覆盖：

- 快速重复调用不再碰撞
- 文件名唯一性
- `.md` / `.docx` 共用基础文件名
- 文件名包含 UUID 后缀

## 2. 本轮发现与 fix batch

### Finding 1：空结果路径缺失 `sufficiency_judgment`

第一轮 focused 验收时，`resolve_facts_with_trace()` 在“无证据文件 / 零命中”路径没有写入 `trace.sufficiency_judgment`。

实际表现：

- `tests/modules/test_evidence.py::TestRetrievalTraceSP6Batch6A` 首轮失败 2 个
- `tests/integration/test_standard_chain_api.py::TestStandardChainRetrievalTraceSP6Batch6A` 首轮失败 1 个

处理方式：

- 通过窄 fix batch 回写，仅要求补齐空结果路径的 `sufficiency_judgment`
- 修复后重跑 focused tests

当前该项已验证闭合。

### Finding 2：原 Opencode session 触发上下文长度上限

原监督 session `ses_2fe1dd9c4ffexRBDDx1ZEL2orx` 在继续 `SP-6` 时返回：

- `InvalidParameter`
- `Range of input length should be [1, 202752]`

本轮处理：

- 不再向原 session 继续堆叠 `SP-6` 上下文
- 新建 recovery session `ses_2fd8c899dffePN5RUUi63jcMLX`
- 只承接 `Batch 6A`，按窄范围恢复执行

本次恢复只说明监督链已恢复，不说明原 session 已恢复。

### Finding 3：Batch 6B 初始实现误用 bash 风格 shell 语法

`SP-6 Batch 6B` recovery session 起步时，worker 在 Windows / PowerShell 环境里误用了：

- `mkdir -p`
- `cd ... && ...`
- `||`

这不是业务实现缺陷，而是 worker shell 兼容问题。

处理方式：

- 回写窄 fix batch，只要求改用 PowerShell 兼容命令或直接使用 Write / Edit 工具
- 不扩大到业务逻辑重写

修复后，`src/rules/` 模块开始正常落盘，`Batch 6B` 得以继续推进。

### Finding 4：Batch 6C Slice B 首轮独立验收暴露测试断言错误

Codex 本地首轮执行：

- `"/mnt/c/Users/96138/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_semantic_review.py tests/integration/test_semantic_review_api.py tests/integration/test_workflow_api.py -q`

实际结果：

- 首轮失败 1 个
- 失败点为 `tests/integration/test_semantic_review_api.py::TestSemanticReviewAPISP6Batch6CSliceB::test_all_layer_outputs_together`
- 失败原因不是业务实现缺陷，而是测试仍按数值比较 `rule_layer_output["families_executed"]`
- 该字段的真实返回类型为 `list`

处理方式：

- 通过窄 fix batch 回写，只修测试断言并补 `workflow API` 顶层 / 结果层覆盖
- 不扩大到业务逻辑重写

修复后，`Batch 6C` focused 验收与合并验收均已通过。

### Finding 5：Batch 6C recovery session 再次暴露 PowerShell/bash 壳层兼容问题

`Batch 6C` 的轻量 recovery session `ses_2fbfcc4c4ffevxHo1dHz2KIw29` 在尝试重跑 pytest 时，worker 又一次在 Windows / PowerShell 环境里误用了 bash 风格命令拼接。

本轮处理：

- 不把该命令失败当作任何“已验收”证据
- 只以前述文件读回、代码路径确认和 Codex 本地 pytest 结果作为 `Batch 6C` 验收依据

该问题属于监督链 / 壳层兼容问题，不属于当前已证实的业务实现阻塞。

### Finding 6：Batch 6D 合并回归暴露同秒文件名碰撞

Codex 本地在 `SP-6` 合并回归里首轮执行：

- `"/mnt/c/Users/96138/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/modules/test_evidence.py tests/rules/test_rule_engine.py tests/modules/test_planning.py tests/modules/test_writing.py tests/modules/test_quality.py tests/test_semantic_review.py tests/modules/test_delivery.py tests/integration/test_standard_chain_api.py tests/integration/test_semantic_review_api.py tests/integration/test_workflow_api.py tests/integration/test_direct_api.py -q`

实际结果：

- 首轮失败 1 个
- 失败点位于 `tests/integration/test_direct_api.py` 的 `delivery` 路径
- `data/tasks.db` 直接读回最近失败记录，错误为 `Permission denied: output\\这是一个测试论点_20260319_112951.md`

定性：

- 这是实现缺陷，不是测试断言缺陷
- 根因是交付文件名只使用到秒级时间戳；同一秒内重复请求会复用同名文件，Windows 下可能抛出 `PermissionError`

处理方式：

- 新建轻量 fix session `ses_2fbd9b6d9ffeXUHM7Rno5N04hp`
- 只修 `Batch 6D` 文件名碰撞，不回退 `6A / 6B / 6C`
- 追加 `tests/modules/test_delivery.py` 回归测试，覆盖快速重复调用与唯一文件名
- worker 首轮 pytest 又触发一次 PowerShell 兼容问题；通过窄壳层纠偏后重跑 focused tests

修复后，该项已通过 worker focused 验收与 Codex 本地复验。

## 3. 验收结论

当前可证实结论：

- `Batch 6A` 已实现并通过 focused 验收
- `Batch 6B` 已实现并通过 focused + 集成验收
- `Batch 6C` 已实现并通过 focused + 合并验收
- `Batch 6D` 已实现并通过 focused + 合并验收
- `SP-6` 已在当前计划范围内闭合

当前闭合口径仅限：

- 显式取证 / 数据编排去黑箱
- 规则执行引擎落地
- 写作 / 审核主链去黑箱
- `docx` 正式交付与终版字数门禁

## 4. 当前残留风险

当前未发现 `SP-6` 范围内未处理的 P1 / P2。

仍需保留的事实：

- 原长 session `ses_2fe1dd9c4ffexRBDDx1ZEL2orx` 没有恢复为可继续承载 `SP-6` 的主 session；本阶段是通过轻量 recovery / fix session 闭合
- `SP-3` 仍保持“部分完成但不阻塞主线”的历史口径，不被本 checkpoint 改写

## 5. 下一步

`SP-6` 已闭合。

若长线程继续推进，下一 session 应先读取新的阶段计划或用户新范围；没有新的硬证据前，不要重新打开 `SP-6` 已闭合项。

## Evidence Summary

1. `opencode export ses_2fbd9b6d9ffeXUHM7Rno5N04hp` 可回读 `Batch 6D` 文件名碰撞 fix batch 与壳层纠偏均已送达；同一 export 已回读 worker focused pytest 结果：`88 passed, 5 warnings in 18.90s`。
2. Codex 本地复验：`"/mnt/c/Users/96138/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/modules/test_delivery.py tests/integration/test_direct_api.py tests/integration/test_standard_chain_api.py -q`：`88 passed, 5 warnings in 11.75s`；`... -m pytest tests/modules/test_evidence.py tests/rules/test_rule_engine.py tests/modules/test_planning.py tests/modules/test_writing.py tests/modules/test_quality.py tests/test_semantic_review.py tests/modules/test_delivery.py tests/integration/test_standard_chain_api.py tests/integration/test_semantic_review_api.py tests/integration/test_workflow_api.py tests/integration/test_direct_api.py -q`：`242 passed, 5 warnings in 16.07s`。
3. 已直接读回 `src/modules/delivery/service.py` 与 `tests/modules/test_delivery.py`，确认交付文件名已增加短 UUID 后缀，且新增了“快速重复调用不碰撞 / 文件名唯一 / md 与 docx 共用基础文件名”的回归测试；同时用 TestClient 连续调用 `/v1/delivery/deliver` 20 次，得到 `STATUSES 20`、`UNIQUE_PATHS 20`。
