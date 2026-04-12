# III期总留痕

状态：持续更新 / 阶段实验包唯一优先留痕
日期：2026-04-10
用途：记录 III 期阶段执行中的关键讨论、阶段切换、裁定摘要、重要回写判断；它是跨阶段的总过程留痕，不替代单题全貌档案和阶段结果总览

## 这份文件怎么用

1. 新 session 需要理解 III 期阶段实验包怎么一路推进到现在时，先读本文件。
2. 这里只追加：
   - 关键讨论
   - 关键裁决
   - 阶段切换
   - 需要回看背景时的最短摘要
3. 不在这里直播实时进度；当前阶段、当前阻塞、当前下一步只认 `00_入口索引/03_当前阶段任务卡.md`，runtime 只保留原始过程证据与直接锚点。

## 这份文件不替代什么

1. 不替代 `04_III期总实验方案层`。
2. 不替代各阶段的 `05_试运行结果总览.md`。
3. 不替代各阶段 `06_单题全貌档案/`。
4. 不替代各阶段 `07_主执行session裁决结论.md`。

## 发生什么写这里

| 发生了什么 | 是否写本文件 | 还要改哪里 |
| --- | --- | --- |
| 用户与 Agent 的关键讨论改变了阶段方向 | 是 | 必要时同步 `04` 层或对应阶段包 |
| 某阶段从“探索”切到“收敛” | 是 | 同步该阶段 `00_阶段入口.md`、`01_阶段目标.md` |
| 单题跑出了关键代表性结论 | 摘要写这里 | 详细结果写对应 `06_单题全貌档案/` |
| 主执行 session 给出阶段性裁决 | 摘要写这里 | 正式裁决写对应 `07_主执行session裁决结论.md` |
| 只是实时分数、实时阻塞、实时下一步 | 否 | 写 runtime 状态卡 |

## 当前固定读序

1. 上游四份仓库级规则
2. `00_入口索引/00_III期临床总入口.md`
3. `00_入口索引/03_当前阶段任务卡.md`
4. 本文件
5. 当前活跃阶段目录

## 最新裁定摘要

### 2026-04-10

1. `04` 层已改成“阶段生成法 + IIIA 既有锚点”，不再默认固定字母阶段。
2. `05` 本轮只收“启动执行前准备”，不进入实跑结果层。
3. 旧 `IIIA期试验/` 降为历史执行记录层，不再承担当前执行入口职责。
4. 当前阶段、当前阻塞、当前下一步只认 `00_入口索引/03_当前阶段任务卡.md`。
5. 当前已确认 `scripts/run_ii_benchmark.ps1` 是 IIIA 冒烟唯一入口；`run_ii_phase.ps1` 仍留在 II 期总控位，`benchmark_runner.py` 当前不承担 10 题入口权。
6. `lecanemab_patient` 首个 smoke 已触发系统级环境异常：当前机器上 Python 导入 `_overlapped` / `asyncio` 即报 `WinError 10106`，后端未能启动到 `/health`；这类异常只记为关键证据，不在此文件里继续播报当前 blocker。

## 证据摘要

1. 已直接核对 `II期` 的 `03_过程强留痕/00_总留痕.md`，确认“总留痕”负责跨阶段过程、讨论、裁决和切换，不替代单题结果。
2. 已直接核对 `II期成果整理/03_Q2_ctad_lb13_c_全貌.md`，确认“全貌”负责单题完整结果与过程，不适合承担总留痕职责。
---

### 2026-04-10（IIIA首轮smoke主执行session）

**关键事件序列**

1. 环境修复确认：`.venv` 下 `import _overlapped` / `import asyncio` 均通过；后端已启动到 `/health`。旧 WinError 10106 blocker 正式清除。
2. Preflight 自动化：首跑发现 2 处真相源冲突（任务卡残留旧 blocker 口径 + `benchmark_runner.py` 假阳性检测）；修复后 `ready_for_smoke=True`。
3. Smoke 第 1-2 枪失败：DashScope coding plan key 打在 `dashscope.aliyuncs.com/compatible-mode/v1` → 401 / 404。经 4 轮端点测试确认正确 URL：`coding.dashscope.aliyuncs.com/v1`。
4. Smoke 第 3 枪：生稿成功，评分链失败（volcengine 401 → DashScope "only for Coding Agents" → ANTHROPIC_API_KEY 无效 → MiniMax 超时或未触达）。
5. 评分链修复：`benchmark_runner.ps1` 中 `Get-PreferredScoringConfig` 候选顺序调整，MiniMax-M2.5 升为首位。
6. Smoke 第 4 枪（最终成功）：exit code 0，lecanemab_patient 72.45/100 PASS，1915 字，全链闭合。
7. 已知缺陷：评分维度明细 null（未解析），Vision/supplement 链路当时被判为待查项，且仅 1 枪无统计性。

**关键裁决摘要**

1. 机器评分有限可采信：72.45 可作参考基线，但维度明细丢失致无法做精确质量归因。
2. 本轮 smoke 部分支撑 IIIA 结论：全链闭合已证明，72.45 < 85 目标。
3. 回写范围：只回写评分链和输入链的已验证发现，不回写内容标准收紧。
4. 下一轮最高优先杠杆：修评分器输出解析 > 修 Vision API 配置 > 扩样跑 2-3 题。

**本session修改的文件**

`.env`、`iiia_preflight.ps1`、`benchmark_runner.ps1`、`03_当前阶段任务卡.md`、`04_试运行计划.md`、`05_试运行结果总览.md`、`06_单题全貌档案/01_lecanemab_patient.md`（新建）、`07_主执行session裁决结论.md`、`08_回写清单.md`
