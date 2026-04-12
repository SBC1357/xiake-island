# IID 8公式缺位矩阵

状态：已填写 / 首轮审计版  
日期：2026-04-06  
用途：`IID` 正式执行资产；逐位记录 `8` 公式 `15` 个公式位在白盒管线 `4` 层中的编码状态，并把 `IIE` 的首批施工包压成可执行缺口。

## 证据摘要

- 已直接核对 [ii_candidate_pool.json](../../../侠客岛白盒编排器/config/ii_candidate_pool.json)，当前候选池稳定存在的写作字段只有 `audience / target_word_count / purpose / genre / core_data_points / required_structure`，没有 `persona / range / content_combo / logic_combo / effective_outline` 等公式位。
- 已直接核对 [run_ii_whitebox_orchestrator.ps1](../../../侠客岛白盒编排器/run_ii_whitebox_orchestrator.ps1)，当前 `whitebox_contract` 真正落盘的核心字段是 `purpose / target_word_count / must_include_facts / required_structure / route_profile / pseudo_load_bearing_points`。
- 已直接核对 [run_ii_whitebox_materials.ps1](../../../侠客岛白盒编排器/run_ii_whitebox_materials.ps1)、[run_ii_whitebox_draft.ps1](../../../侠客岛白盒编排器/run_ii_whitebox_draft.ps1)、[run_ii_whitebox_score.ps1](../../../侠客岛白盒编排器/run_ii_whitebox_score.ps1)，确认材料层只做原文抽取，出稿层只消费 `purpose / must_include_facts / required_structure` 及少量硬规则，评分层没有公式合规维度和 `formula_trace` 闸门。

## 审计口径

1. 本表按 [藏经阁假设建设逻辑.md](../../00_实验总纲/藏经阁假设建设逻辑.md) 的严格 `15` 公式位审计。
2. 状态只用三档：`已编码` / `部分编码` / `缺失`。
3. 当前活跃口径里常说的“`2/15` 已编码”，其中第二个位实际上是通过 `required_structure` 这条**非公式代理约束**把“文章大纲”半手工写进管线；它不是公式 `7 -> 8` 已真正打通。

## 缺位矩阵

| 公式位 | contract 层 | materials 层 | draft_prompt 层 | scoring 层 | 当前判定 | 当前证据 | 代码/文件落点 | 下一步进入哪层 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `写作目标` | 部分编码 | 缺失 | 部分编码 | 缺失 | 部分编码 | 当前只有 `target_word_count` 这个长度代理，没有独立的 `write_target` 机器位，也没有把“这篇稿到底要完成什么任务”写成公式输入。 | `ii_candidate_pool.json:11-23,57-67`；`run_ii_whitebox_orchestrator.ps1:179-185`；`run_ii_whitebox_draft.ps1:75-77` | 先补 `contract`，再补 `draft_prompt` 和 `scoring` |
| `排列规则` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 候选池、合同、prompt、评分都没有对应字段或推导链。 | `ii_candidate_pool.json` 无该字段；`run_ii_whitebox_orchestrator.ps1:175-195`；`run_ii_whitebox_draft.ps1:69-98`；`run_ii_whitebox_score.ps1:50-95` | 先补 `contract`，再补 `draft_prompt` |
| `写作目的` | 已编码 | 缺失 | 已编码 | 部分编码 | 已编码 | `purpose` 已从候选池进入合同，并直接写进出稿 prompt；评分 prompt 也会读到它，但没有公式合规评分。 | `ii_candidate_pool.json:13,59,113,167,201`；`run_ii_whitebox_orchestrator.ps1:179-185`；`run_ii_whitebox_draft.ps1:72-78`；`run_ii_whitebox_score.ps1:53-58` | 继续补 `scoring` 的公式合规检查 |
| `人格` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 当前只有 `audience / genre`，没有单独的 `persona` 输入，也没有“人格如何改写表达策略”的消费链。 | `ii_candidate_pool.json` 无 `persona`；`run_ii_whitebox_orchestrator.ps1:179-185` 仅写 `audience / genre` | 先补 `contract`，再补 `draft_prompt` 和 `scoring` |
| `写作范围` | 部分编码 | 缺失 | 缺失 | 缺失 | 部分编码 | 只有 `route_profile / case_type` 这类残余代理，没有把 `purpose * persona` 推成 `range` 的显式公式位。 | `run_ii_whitebox_orchestrator.ps1:170,191-193`；`run_ii_whitebox_draft.ps1:73-77` 仅消费题型/目的，不消费 `range` | 先补 `contract`，再补 `draft_prompt` |
| `最小内容单元` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 材料层只抽全文和 preview，没有把内容拆成可审计的最小单元。 | `run_ii_whitebox_materials.ps1:29-87` | 先补 `materials` |
| `最小逻辑单元` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 当前没有任何地方把 `ARCH-04 / 人物线主从 / 人群分流` 这类逻辑位写成机器输入。 | `run_ii_whitebox_orchestrator.ps1:191-193` 只有 `route_profile / pseudo_load_bearing_points` 代理 | 先补 `contract` |
| `最小有效内容单元` | 部分编码 | 缺失 | 部分编码 | 部分编码 | 部分编码 | `must_include_facts` 能代理一部分“必须吃住的内容”，但它不是从公式位推导出来，也没有结构化映射到材料层。评分只用 `key_facts` 维度粗评。 | `ii_candidate_pool.json:15-22`；`run_ii_whitebox_orchestrator.ps1:184`；`run_ii_whitebox_draft.ps1:51-55,80,90`；`run_ii_whitebox_score.ps1:76-81` | 先补 `materials`，再补 `contract / draft_prompt / scoring` |
| `最小有效逻辑单元` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 当前没有把“哪些逻辑位在本题必须生效”写成合同对象，也没有在评分里校验。 | `run_ii_whitebox_orchestrator.ps1:191-193` 仅代理式路由，不是最小有效逻辑单元 | 先补 `contract`，再补 `scoring` |
| `内容单元组合规则` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 没有“哪些内容单元怎样组合才能成这类稿”的机器规则。 | `ii_candidate_pool.json`、`orchestrator/draft/score` 均无对应字段 | 先补 `contract` |
| `逻辑组合规则` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 没有“逻辑单元如何组装成主承重”的机器规则。 | 同上 | 先补 `contract` |
| `内容组合` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 现有白盒没有把“本题应采用哪一种内容组合”写成可消费对象。 | 同上 | 先补 `contract` |
| `逻辑组合` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 现有白盒没有把“本题应采用哪一种逻辑组合”写成可消费对象。 | 同上 | 先补 `contract` |
| `文章大纲` | 已编码 | 缺失 | 已编码 | 部分编码 | 已编码 | 当前通过 `required_structure` 这条**代理约束**把大纲直接手填进候选池、合同和 prompt；评分也有 `structure` 维度，但没有检查大纲推导链。 | `ii_candidate_pool.json:23-29,67-72,123-129,174-180`；`run_ii_whitebox_orchestrator.ps1:185`；`run_ii_whitebox_draft.ps1:57-61,82`；`run_ii_whitebox_score.ps1:76-81` | 保留现代理约束，同时在 `contract` 补公式来源，在 `scoring` 补链路检查 |
| `有效大纲` | 缺失 | 缺失 | 缺失 | 缺失 | 缺失 | 现有系统没有把“范围 × 文章大纲”之后得到的有效大纲写成独立对象，也没有消费或校验。 | `ii_candidate_pool.json`、`orchestrator/draft/score` 均无对应字段 | 先补 `contract`，再补 `draft_prompt / scoring` |

## 汇总统计

### 严格 `15` 位统计

| 状态 | 数量 | 公式位 |
| --- | --- | --- |
| 已编码 | `2/15` | `写作目的`、`文章大纲`（通过 `required_structure` 代理写入） |
| 部分编码 | `3/15` | `写作目标`、`写作范围`、`最小有效内容单元` |
| 缺失 | `10/15` | `排列规则`、`人格`、`最小内容单元`、`最小逻辑单元`、`最小有效逻辑单元`、`内容单元组合规则`、`逻辑组合规则`、`内容组合`、`逻辑组合`、`有效大纲` |

### 当前最先该进 `IIE` 的施工包

1. `contract` 首包：补 `persona / range / 有效大纲 / 内容组合 / 逻辑组合` 的机器可读字段。
2. `materials` 首包：补 `最小内容单元 / 最小有效内容单元` 的结构化抽取，尤其是图表 exact value 与来源锚点同步入链。
3. `draft_prompt` 首包：把 `range / persona / 组合规则 / 有效大纲` 从合同层真正展开成 prompt 约束，而不是继续只吃 `purpose + required_structure + must_include_facts`。
4. `scoring` 首包：补 `formula_trace` 闸门和公式合规评分，避免只拿参考答案对照分冒充“公式被正确调用”。

## 当前结论

1. 当前白盒不是“完全没接 `8` 公式”，但也远不是“公式驱动 + LLM”。
2. 真实状态是：`写作目的` 已直接打通，`文章大纲` 只靠 `required_structure` 代理写入，`写作目标 / 写作范围 / 最小有效内容单元` 有残余代理，其余 `10` 位当前完全没进管线。
3. 因此 `IIE` 第一优先级不是继续跑题，而是先把首批缺位写进 `contract / materials / draft_prompt / scoring`。
