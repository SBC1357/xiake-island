# 侠客岛 Checkpoints 归档迁出清单

- 日期: 2026-03-29
- 状态: 历史清单；第一批优先迁出与第二批零入链迁出已执行；后续删除收口已完成，仅保留少量仍有活动引用的回溯文档
- 目标: 不直接删除 `checkpoints/` 与 `docs/checkpoints/`，而是先把适合迁出主路径的内容分层整理为可执行清单
- 清单口径: 本清单区分 `优先迁出`、`次级迁出`、`原地保留`，不在本文件中执行文件移动

> 说明：本文件保留为历史决策记录。其上列出的多数迁出候选已于 2026-03-29 后续删除收口；当前不应再将本清单视为活动待执行列表。

## 1. 结论摘要

`docs/checkpoints/` 不适合整目录直接删除，`checkpoints/` 也不适合整目录直接删除。更合理的动作是把“零入链、早期中间态、孤立附件”先迁出主路径，保留仍被项目文档引用的证据链。

建议按这个顺序处理：

1. 先迁出根 `checkpoints/` 下无历史外部引用的 `2026-03-24` 检查点和图片附件。
2. 再迁出 `docs/checkpoints/` 中当前无历史入链的 `21` 个 markdown。
3. 保留仍有历史引用的 `40` 个 checkpoint markdown。
4. `phase6_dryrun_test.py` 和 `2026-03-17-empty-dict-serialization-fix.md` 暂不单独动，它们仍被历史文档点名引用。

## 2. 建议的归档目标

为避免继续把项目记忆混在主路径，建议后续执行时统一迁到以下位置：

- `docs/archive/checkpoints-root/`
  - 存放根 `checkpoints/` 下的孤立检查点和图片附件
- `docs/archive/checkpoints-unlinked/`
  - 存放 `docs/checkpoints/` 下当前无历史入链的 markdown
- `docs/archive/checkpoints-linked-support/`
  - 预留给仍被单篇历史报告点名引用、但未来准备连同上游报告一起归档的支撑文件

本清单只给迁出目标，不在当前主仓创建这些目录。

## 3. 优先迁出

这批的特点是：当前不在运行链上，且在排除审计/日志类新文件后，没有历史外部引用。

| 源路径 | 大小 | 建议迁入 | 理由 |
| --- | ---: | --- | --- |
| `checkpoints/2026-03-24-frontend-backend-unified-modification.md` | `7447` B | `docs/archive/checkpoints-root/2026-03-24-frontend-backend-unified-modification.md` | 当前无历史外部引用，内容属于一次独立长线程执行检查点 |
| `checkpoints/image/2026-03-24-frontend-backend-unified-modification/1774316984971.png` | `208198` B | `docs/archive/checkpoints-root/image/2026-03-24-frontend-backend-unified-modification/1774316984971.png` | 当前无文本引用，且明显是上一条检查点的配套附件 |
| `docs/checkpoints/最小监督链验证_checkpoint_20260319.md` | `106` B | `docs/archive/checkpoints-unlinked/最小监督链验证_checkpoint_20260319.md` | 体量极小，内容更像一次会话通过标记，当前无历史入链 |
| `docs/checkpoints/编辑部工作台_batch-A-2_checkpoint_20260316.md` | `2028` B | `docs/archive/checkpoints-unlinked/编辑部工作台_batch-A-2_checkpoint_20260316.md` | 当前无历史入链，且被同题材后续版本 `编辑部工作台_batch-A-2_checkpoint.md` 实际覆盖 |

### 3.1 第一批执行结果

- 已执行迁出:
  - `checkpoints/2026-03-24-frontend-backend-unified-modification.md`
  - `checkpoints/image/2026-03-24-frontend-backend-unified-modification/1774316984971.png`
  - `docs/checkpoints/最小监督链验证_checkpoint_20260319.md`
  - `docs/checkpoints/编辑部工作台_batch-A-2_checkpoint_20260316.md`
- 当前落点:
  - `docs/archive/checkpoints-root/2026-03-24-frontend-backend-unified-modification.md`
  - `docs/archive/checkpoints-root/image/2026-03-24-frontend-backend-unified-modification/1774316984971.png`
  - `docs/archive/checkpoints-unlinked/最小监督链验证_checkpoint_20260319.md`
  - `docs/archive/checkpoints-unlinked/编辑部工作台_batch-A-2_checkpoint_20260316.md`
- 执行后状态:
  - 上述 4 个源路径均已不存在
  - 目标路径均已存在且文件大小与迁前一致
- 迁出后哨兵验证:
  - 前端 `npm run build` 成功
  - 前端 `npm run test:run` 通过 `11` 个测试文件、`71` 个测试
  - 后端 `/health = 200`
  - 后端 `/ = 200`

## 4. 次级迁出

这批的特点是：当前无历史入链，但内容仍属于阶段性项目记忆。更适合迁出归档，不建议直接删。

### 4.1 零入链批量候选

以下 `docs/checkpoints/` markdown 在仅统计历史文档与 checkpoint 文档互引时，当前都没有外部入链：

| 路径 | 大小 |
| --- | ---: |
| `docs/checkpoints/fix-batch_api行为对齐_20260317.md` | `3805` B |
| `docs/checkpoints/三系统解耦_2A-fix-batch-final_checkpoint_20260316.md` | `3332` B |
| `docs/checkpoints/三系统解耦_2A-fix-batch-v2_checkpoint_20260316.md` | `3604` B |
| `docs/checkpoints/三系统解耦_2A-fix-batch_checkpoint_20260316.md` | `2468` B |
| `docs/checkpoints/三系统解耦_2A-phase-0_checkpoint_20260315.md` | `2673` B |
| `docs/checkpoints/三系统解耦_2A-phase-1_checkpoint_20260315.md` | `2915` B |
| `docs/checkpoints/三系统解耦_2A-phase-2_checkpoint_20260315.md` | `2397` B |
| `docs/checkpoints/三系统解耦_2A-phase-3_checkpoint_20260315.md` | `2294` B |
| `docs/checkpoints/三系统解耦_2A-phase-4_checkpoint_20260315.md` | `1843` B |
| `docs/checkpoints/三系统解耦_2A-phase-5_checkpoint_20260315.md` | `1746` B |
| `docs/checkpoints/三系统解耦_2A-phase-6_checkpoint_20260315.md` | `3442` B |
| `docs/checkpoints/三系统解耦_2B-fix-batch_checkpoint_20260316.md` | `2597` B |
| `docs/checkpoints/三系统解耦_2C-CLOSURE_report_20260316.md` | `2782` B |
| `docs/checkpoints/三系统解耦_2C-fix-batch_checkpoint_20260316.md` | `2880` B |
| `docs/checkpoints/三系统解耦_2C-phase-6_checkpoint_20260316.md` | `3628` B |
| `docs/checkpoints/三系统解耦_phase-7_自审第一轮_20260315.md` | `5249` B |
| `docs/checkpoints/三系统解耦_phase-7_自审第二轮_20260315.md` | `2681` B |
| `docs/checkpoints/三系统解耦_最终自审_20260315.md` | `2544` B |
| `docs/checkpoints/长线程基线_stage-0_checkpoint_20260318.md` | `5976` B |

建议迁入：

- `docs/archive/checkpoints-unlinked/`

说明：

- 这批里 `三系统解耦*` 占多数，更像历史施工轨迹。
- 它们不是强删除候选，但已经不适合继续占据当前主路径。

### 4.1.1 第二批执行结果

- 已执行迁出：
  - 本节列出的 `19` 个零历史入链 markdown
- 当前落点：
  - `docs/archive/checkpoints-unlinked/`
- 执行后状态：
  - `docs/archive/checkpoints-unlinked/` 当前共 `21` 个文件
    - 含第一批迁入的 `2` 个文件
    - 含第二批迁入的 `19` 个文件
  - `docs/checkpoints/` 当前保留 `40` 个 markdown
- 迁出后哨兵验证：
  - 前端 `npm run build` 成功
  - 前端 `npm run test:run` 通过 `11` 个测试文件、`71` 个测试
  - 后端 `/health = 200`
  - 后端 `/ = 200`

### 4.2 条件迁出

以下文件不建议现在孤立迁出，但如果未来连同上游历史报告一起整理，可一起迁：

| 源路径 | 大小 | 当前状态 | 建议 |
| --- | ---: | --- | --- |
| `docs/checkpoints/phase6_dryrun_test.py` | `11713` B | 被 `docs/archive/root-historical/三系统解耦基线施工汇报_20260315.md` 点名引用 | 仅在对应汇报一并迁档时迁出 |

## 5. 原地保留

这批当前不建议动。

| 路径或集合 | 原因 |
| --- | --- |
| `docs/checkpoints/` 中其余 `40` 个有历史入链的 markdown | 仍被长线程续接、执行单、阶段拆分文档直接引用 |
| `checkpoints/2026-03-17-empty-dict-serialization-fix.md` | 仍被 `docs/checkpoints/编辑部工作台_batch-A-2_checkpoint.md` 引用 |

## 6. 执行顺序建议

如果后续要实际迁出，建议按这个顺序做：

1. 先迁 `优先迁出` 4 项。
2. 回读所有引用 `checkpoints/2026-03-24-frontend-backend-unified-modification.md` 的文档，确认确实没有历史外链漏网。
3. 再批量迁 `次级迁出` 的 `19` 个零入链 markdown。
4. 最后视是否要整理 `docs/archive/root-historical/三系统解耦基线施工汇报_20260315.md`，再决定 `phase6_dryrun_test.py` 是否一起迁。

## 7. 不建议直接做的事

- 不建议整目录删除 `docs/checkpoints/`
- 不建议整目录删除 `checkpoints/`
- 不建议孤立删除 `phase6_dryrun_test.py`
- 不建议移动 `2026-03-17-empty-dict-serialization-fix.md` 而不同时修正其引用文档

## 8. 证据摘要

- 目录体积核对：`checkpoints/` 约 `216K`、`docs/checkpoints/` 约 `332K`，它们不是仓库主要空间负担。
- 历史引用核对：在排除本轮审计/日志文档后，`docs/checkpoints/` 的 `61` 个 markdown 中有 `40` 个存在历史入链，`21` 个无历史入链。
- 根目录异构核对：`checkpoints/2026-03-17-empty-dict-serialization-fix.md` 仍有历史引用；`checkpoints/2026-03-24-frontend-backend-unified-modification.md` 及其 `203K` 图片附件无历史外部引用。
- 执行状态核对：第二批迁出完成后，`docs/archive/checkpoints-unlinked/` 共 `21` 个文件，`docs/checkpoints/` 还剩 `40` 个 markdown。
