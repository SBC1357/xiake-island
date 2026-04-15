# lecanemab_news 模型对照历史档案

状态：历史档案  
日期：2026-04-12  
用途：保留中国真实世界新闻报道单题的模型对照证据；仅供回看，不承接当前活状态，不作为执行入口。

## 活状态回指

本页不再承担“当前有效口径”。当前活状态只回指 `00_入口索引/03_当前阶段任务卡.md` 与 `07_白盒施工包/04_第四轮白盒测试+建设/白盒系统第四轮收口长线程包.md`。

## 归档说明

1. 这是一份历史模型对照单题档案，记录的是当轮 `k2.5` 与 `deepseek-reasoner` 在 `news` 题上的比较结果。
2. 文中出现的“当前主结论”“当前最该改”“当前 scorer”等措辞，均应按当轮归档口径理解，不再表示现时活状态。
3. 本页只保留模型对照证据和新闻题的历史判断，不再承担当前进度播报。

## 证据摘要

1. 归档主线来自同一轮模型对照运行标记 `20260412_041831_050_k25_vs_deepseek`，并配套保留了 `score.json`、`local_revise_manifest.json`、`draft_manifest.json`、`whitebox_contract.json`、`draft_prompt.md`、`revise_prompt.md` 等对照证据。
2. 当轮记录的主结论是：在当时的 scorer 下，`k2.5` 与 `deepseek-reasoner` 三阶段没有被明显拉开，瓶颈更像合同、问题线与 scorer 分辨力。
3. 证据卡中的关键 raw 锚点来自多中心真实世界材料，主线是浙江二院，其他中心作为补线。

## 归档结论

1. 这题不是单纯换模型就能解决，优先级更高的是把问题线和合同打硬。
2. 当轮判断保留为：浙江二院主线要更硬，华西、华山、海南瑞金更多承担补线作用。
3. 本页不再继续把模型差异写成现时播报，而是作为历史对照样本封存。

## 证据锚点卡

### G0 证据卡

- 题目：`lecanemab_news`
- 题型：医学新闻报道
- 证据层级：raw PDF + 白盒合同 + 起稿 prompt + 返修 prompt + 对照评分产物
- 归档状态：verified

### Must-Have Values

- `76` 例早期 AD：浙江单中心真实世界队列规模。
- `IRSE 18.4%`：浙江队列总体不良事件相关症状率。
- `ARIA 11` 例：浙江队列 ARIA 总数，全部无症状。
- `CDR-GS 1` vs `0.5`：CDR 分层对应更快的 MMSE 下降。
- `LOAD group β = -0.434`：年龄起病分层中的轨迹差异。
- `PVWMHs p = 0.008`：孤立 ARIA-H 与基线白质高信号风险信号。
- `407`、`68`、`64` 例：华山、华西、海南的中国真实世界补线规模。
- `12.15% ARIA`、`9.4% ARIA-H`、`3.1% ARIA-E`：多中心安全性补线关键值。

### 归档阅读提示

1. 这页不是当前播报页，不再提供“正在跑到哪一轮”的口径。
2. 这页只保留历史证据与结论，不再承担进度追踪、阻塞判断或续跑入口。
3. 若要继续看活状态，只回看上面的两份正式入口文件。

## 历史产物清单

1. `score.json`
2. `local_revise_manifest.json`
3. `draft_manifest.json`
4. `whitebox_contract.json`
5. `draft_prompt.md`
6. `revise_prompt.md`
7. `materials/materials_digest.md`
8. `compare_snapshots/base`
9. `compare_snapshots/whole`
10. `compare_snapshots/local_revise`

