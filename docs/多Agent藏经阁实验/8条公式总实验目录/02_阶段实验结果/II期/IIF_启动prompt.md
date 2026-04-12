# IIF 全量执行启动 Prompt

> 本 prompt 供执行 Agent 一次性跑完 IIF 全部 17 次管线。  
> 状态：ready_to_execute  
> 日期：2026-04-08

---

## 你的身份与任务

你是侠客岛白盒管线的执行 Agent。你的唯一任务是：**按照 IIF 实验方案，依次执行 17 次管线调用，产出全部稿件、评分和 revise 记录，并整理成全貌文件。**

不要自作主张修改任何脚本。不要跳步。不要省略任何一次管线执行。每次执行后确认产物完整再进入下一次。

---

## 关键路径

- **脚本目录**：`D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\侠客岛白盒编排器\`
- **运行时产物落点**：`D:\汇度编辑部1\侠客岛-runtime\ii_whitebox\`（仓库外，随便写）
- **候选池**：`config\ii_candidate_pool.json`（10个候选全部 ready）
- **成果整理目录**：`D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\8条公式总实验目录\02_阶段实验结果\II期\IIF成果整理\`（不存在则先创建）

---

## 管线 4 步调用模板

每次管线执行的命令模板如下。**所有命令在脚本目录下执行。**

```powershell
# 设置工作目录
Set-Location "D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\侠客岛白盒编排器"

# Step 1: orchestrator → 产出 contract + summary + manifest
.\run_ii_whitebox_orchestrator.ps1 -CandidateId "{CANDIDATE_ID}" {EXTRA_FLAGS}
# 记录输出的 run_directory 路径（下面步骤需要）

# Step 2: materials → 编译原材料
.\run_ii_whitebox_materials.ps1 -CandidateId "{CANDIDATE_ID}" -RunDirectory "{RUN_DIR}"

# Step 3: draft → 出稿
.\run_ii_whitebox_draft.ps1 -CandidateId "{CANDIDATE_ID}" -RunDirectory "{RUN_DIR}"

# Step 4: score → 评分
.\run_ii_whitebox_score.ps1 -CandidateId "{CANDIDATE_ID}" -RunDirectory "{RUN_DIR}"
```

需要 revise loop 时追加第 5 步：

```powershell
# Step 5: revise → score→revise 循环（最多6轮，≥85分或连续2轮不提分退出）
.\run_ii_whitebox_revise.ps1 -CandidateId "{CANDIDATE_ID}" -RunDirectory "{RUN_DIR}"
```

### 关键 flag 说明

| Flag | 含义 | 何时使用 |
|------|------|----------|
| `-EnableReferenceSample` | 在 orchestrator 上放开样稿 | IIF-2、IIF-3、IIF-4 的 B 臂 |
| （无额外 flag 时） | 默认无样稿 | IIF-1 两臂、IIF-2 基准 |

### formula_positions 控制

- **A 臂（无公式）**：在 `ii_candidate_pool.json` 中临时清空该候选的 `formula_positions` 字段（设为 `null`），跑完后恢复。
- **B 臂（有公式）**：直接跑，`formula_positions` 已预填。

---

## 全部 17 次执行序列

### 第一批：IIF-1 公式因果性（6 次）

IIF-1 A/B 两臂各跑 3 题。**A 臂无公式无样稿无 revise，B 臂有公式无样稿无 revise。**

| 序号 | 候选ID | 臂 | 公式 | 样稿 | revise | 操作要点 |
|:----:|--------|:--:|:----:|:----:|:------:|----------|
| 1 | compassion15_os_c | A | ✗ | ✗ | ✗ | **先**把 `formula_positions` 设为 `null` → 跑 4 步 → 记录 run_dir |
| 2 | zolbetuximab_safety_d | A | ✗ | ✗ | ✗ | 同上 |
| 3 | sindi_gastric_esmo_c | A | ✗ | ✗ | ✗ | 同上 |
| 4 | compassion15_os_c | B | ✓ | ✗ | ✗ | **恢复** `formula_positions` → 跑 4 步 |
| 5 | zolbetuximab_safety_d | B | ✓ | ✗ | ✗ | 同上 |
| 6 | sindi_gastric_esmo_c | B | ✓ | ✗ | ✗ | 同上 |

**A 臂公式清空/恢复方法**：

```powershell
# 读取候选池
$poolPath = "config\ii_candidate_pool.json"
$pool = Get-Content $poolPath -Raw | ConvertFrom-Json

# 找到目标候选
$candidate = $pool.candidates | Where-Object { $_.id -eq "{CANDIDATE_ID}" }

# 备份 formula_positions（内存中保留）
$backup = $candidate.formula_positions

# 清空
$candidate.formula_positions = $null
$pool | ConvertTo-Json -Depth 100 | Set-Content $poolPath -Encoding UTF8

# ... 跑完 A 臂管线后恢复 ...
$candidate.formula_positions = $backup
$pool | ConvertTo-Json -Depth 100 | Set-Content $poolPath -Encoding UTF8
```

> ⚠️ 重要：3 题 A 臂可以先批量清空跑完，再批量恢复跑 B 臂，但每次清空/恢复后都要验证 JSON 结构完整。

### 第二批：IIF-2 样稿增益（4 次）

IIF-2 需要基准（有公式无样稿）和实验（有公式有样稿）各跑 2 题。

| 序号 | 候选ID | 组别 | 公式 | 样稿 | revise | 操作要点 |
|:----:|--------|:----:|:----:|:----:|:------:|----------|
| 7 | ctad_lb13_c | 基准 | ✓ | ✗ | ✗ | 跑 4 步，无额外 flag |
| 8 | ctad_p096_c | 基准 | ✓ | ✗ | ✗ | 同上 |
| 9 | ctad_lb13_c | 实验 | ✓ | ✓ | ✗ | 加 `-EnableReferenceSample`，跑 4 步 |
| 10 | ctad_p096_c | 实验 | ✓ | ✓ | ✗ | 同上 |

### 第三批：IIF-3 revise loop（4 次）

IIF-3 需要基准（公式+样稿，无 revise）和实验（公式+样稿+revise）各 2 题。

| 序号 | 候选ID | 组别 | 公式 | 样稿 | revise | 操作要点 |
|:----:|--------|:----:|:----:|:----:|:------:|----------|
| 11 | iie_reg_patient_c | 基准 | ✓ | ✓ | ✗ | 加 `-EnableReferenceSample`，跑 4 步 |
| 12 | iie_reg_mechanism_c | 基准 | ✓ | ✓ | ✗ | 同上 |
| 13 | iie_reg_patient_c | 实验 | ✓ | ✓ | ✓ | 加 `-EnableReferenceSample`，跑 **5 步**（含 revise） |
| 14 | iie_reg_mechanism_c | 实验 | ✓ | ✓ | ✓ | 同上 |

### 第四批：IIF-4 系统上限（3 次）

全部变量打开，全部跑 5 步。

| 序号 | 候选ID | 公式 | 样稿 | revise | 操作要点 |
|:----:|--------|:----:|:----:|:------:|----------|
| 15 | ctad_lb21_c | ✓ | ✓ | ✓ | 加 `-EnableReferenceSample`，跑 5 步 |
| 16 | ctad_p279_c | ✓ | ✓ | ✓ | 同上 |
| 17 | lecanemab_news_c | ✓ | ✓ | ✓ | 同上 |

---

## 每次执行后的检查清单

每次管线执行完成后，确认以下产物存在且非空：

- [ ] `whitebox_contract.json` — orchestrator 产出
- [ ] `whitebox_summary.md` — orchestrator 产出
- [ ] `whitebox_manifest.json` — orchestrator 产出
- [ ] `materials_manifest.json` — materials 产出
- [ ] `compiled_text.md` — materials 产出
- [ ] `draft_text.md` — draft 产出
- [ ] `score.json` — score 产出
- [ ] `revise_manifest.json` — revise 产出（仅限有 revise 的执行）

如果任何步骤报错：
1. 记录错误信息到 `{RUN_DIR}\error_log.txt`
2. 标记该次执行为 `agent_continue_required`
3. **继续**执行下一次管线，不阻塞

---

## 成果整理

每完成一个候选题的全部实验组+对照组执行后，在 `IIF成果整理\` 下创建全貌文件：

### 文件命名

- `IIF-1_{candidate_id}_全貌.md`
- `IIF-2_{candidate_id}_全貌.md`
- `IIF-3_{candidate_id}_全貌.md`
- `IIF-4_{candidate_id}_全貌.md`

### 全貌文件结构

```markdown
# IIF-{arm} {candidate_name} 全貌

## 主阅读层

### 实验配置
- 候选题：{id} / {name}
- 臂别：IIF-{arm}
- 自变量：公式={是/否} / 样稿={是/否} / revise={是/否}

### A 臂成稿（如适用）
> [完整稿件内嵌]

### B 臂 / 实验组成稿
> [完整稿件内嵌]

### 评分对比

| 维度 | A臂 | B臂/实验 | 差值 |
|------|-----|----------|------|
| route_alignment | | | |
| key_facts | | | |
| audience_style | | | |
| structure | | | |
| hallucination_control | | | |
| **weighted_total** | | | |

### 写作力副表对比

| 维度 | A臂 | B臂/实验 | 差值 |
|------|-----|----------|------|
| opening_hook | | | |
| transition_flow | | | |
| midgame_drive | | | |
| closing_tension | | | |
| anchor_fidelity | | | |

### 公式审计（仅B臂/有公式组）
- formula_compliance: {分数}
- formula_trace: [逐条 hit/miss/partial]

### revise 记录（如适用）
- 总轮次：{N}
- 分数轨迹：{R0→R1→R2...}
- 退出原因：{target_reached / stale_plateau / max_rounds / no_actionable}
- 回滚次数：{N}

## 工程附录层

### Prompt 全文
> [A臂 prompt / B臂 prompt 全文内嵌]

### 评分 JSON 全文
> [A臂 / B臂 score.json 内嵌]

### revise_manifest 全文（如适用）
> [revise_manifest.json 内嵌]
```

---

## 汇总结论

17 次全部跑完且全貌文件齐备后，输出两份结论文件到 `IIF成果整理\`：

### 1. `IIF_因果性结论.md`

基于 IIF-1 三题 A/B 对比：
- 3题各自的 weighted_total 差值
- 均值差是否 > 5 分
- B 臂 formula_compliance 均值是否 ≥ 70
- **结论**：因果性成立 / 不成立 / 边界

### 2. `IIF_系统上限结论.md`

基于 IIF-4 三题全开结果：
- 3 题各自的 weighted_total + 写作力副表
- 是否达到 ≥85（可交付草稿）或 ≥75（有价值底稿）
- claim_ceiling 标注：每个分维的理论天花板分和瓶颈原因
- **结论**：系统上限水平判定

---

## 执行约束

1. **不碰仓库主路径**——运行时产物全落在 `侠客岛-runtime\ii_whitebox\`，只有全貌文件和结论文件写入仓库内 `IIF成果整理\`
2. **不修改任何脚本**——只执行，不改
3. **formula_positions 清空/恢复必须配对**——A 臂跑完立刻恢复，不允许残留 null 状态
4. **LLM 调用失败不阻塞**——标记后继续下一题
5. **全部完成后做仓库卫生检查**——确认无临时文件残留

---

## 开始执行

从序号 1 开始，把上面 17 次管线依次跑完。每完成一个臂别的全部题目后，整理该臂全貌文件。全部 17 次跑完后，输出两份汇总结论。

开始。
