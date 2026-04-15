# lecanemab_patient 模型对照历史档案

状态：历史档案  
日期：2026-04-12  
用途：保留患者向单题模型对照证据；仅供回看，不承接当前活状态，不作为执行入口。

## 活状态回指

本页不再承担“当前有效口径”。当前活状态只回指 `00_入口索引/03_当前阶段任务卡.md` 与 `07_白盒施工包/04_第四轮白盒测试+建设/白盒系统第四轮收口长线程包.md`。

## 归档说明

1. 这是一份历史模型对照单题档案，记录的是当轮 `k2.5` 与 `deepseek-reasoner` 在 `patient` 题上的比较结果。
2. 文中出现的“本页只认”“当前明确缺项”“当前判定”等措辞，均应按当轮归档口径理解，不再表示现时活状态。
3. 本页保留证据，但不再冒充当前真相源；任何后续执行判断，都应转回上面的两份活状态文件。

## 证据摘要

1. 归档主线来自同一轮模型对照运行标记 `20260412_041831_050_k25_vs_deepseek`，并配套保留了 `score.json`、`local_revise_manifest.json`、`draft_manifest.json`、`whitebox_contract.json`、`draft_prompt.md` 等对照证据。
2. 当轮记录的核心结论是：`deepseek-reasoner` 首稿硬层更强，`k2.5` 在 `whole revise` 后软层更强。
3. 证据卡中的关键 raw 锚点来自单页 poster，围绕 48 个月长期结果展开。

## 归档结论

1. 这题不是简单比“谁更会写”，而是比谁先打中合同关键位、谁在整稿返修后更像患者稿。
2. 当轮判断保留为：首稿阶段 `deepseek-reasoner` 更稳，返修收束阶段 `k2.5` 的患者沟通感与叙事推进更强。
3. 本页不再继续追问模型切换，而是把这组结论作为历史对照样本保存。

## 证据锚点卡

### G0 资料卡

- 题目：`lecanemab_patient`
- 题型：患者向科普解读
- 证据层级：raw PDF + 白盒合同 + 起稿 prompt + 对照评分产物
- 归档状态：verified

### Must-Have Values

- `48 months / 4 years`：时间主轴，所有长期结果都按四年口径展开。
- `1,521`：纳入分析的 `ApoE ε4 non-carriers or heterozygotes` 数量。
- `31% / 53% / 16%`：随机化患者中 `non-carriers / heterozygotes / homozygotes` 的组成。
- `10 mg/kg biweekly`：给药方案。
- `9.8 months` 与 `14.2 months`：48 个月时的 time saved，对照 `ADNI` 与 `BioFINDER`。
- `32%`：相较 `ADNI natural history cohort` 的进展风险降低幅度。
- `55%`：延迟进入下一 AD stage 的相对风险改善幅度。
- `Adverse event rates were lower or stabilized each additional year`：长期安全性趋势句。

### 归档阅读提示

1. 这页不是当前播报页，不再提供“现在跑到哪了”的口径。
2. 这页只保留历史证据与结论，不再承担进度追踪、阻塞判断或续跑入口。
3. 若要继续看活状态，只回看上面的两份正式入口文件。

## 历史产物清单

1. `score.json`
2. `local_revise_manifest.json`
3. `draft_manifest.json`
4. `whitebox_contract.json`
5. `draft_prompt.md`
6. `materials/materials_digest.md`
7. `compare_snapshots/base`
8. `compare_snapshots/whole`
9. `compare_snapshots/local_revise`

