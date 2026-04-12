# IIIA期主执行session裁决结论

状态：扩样裁决版（3 case 全链完成）
日期：2026-04-10

硬边界：本文件是裁决快照，不是接手第一读物。没有先读单题全貌全文与 runtime 审稿包，不得直接引用本文件下判断。

说明：本文件在首枪 smoke 裁决快照基础上，追加扩样 3 case 的裁决结论。当前 blocker 和下一步只认 `00_入口索引/03_当前阶段任务卡.md`。

---

## 扩样裁决总结

### 全链闭合结论

**全链（上传→证据→规划→写作→出稿→评分）可复现闭合。**

直接证据：
- patient 全链 ✓（含评分闭合）
- mechanism 全链 ✓（含评分闭合）
- news 全链跑到 delivery 层，前 5 步（evidence→planning→writing→drafting→quality）全部 completed/passed，仅字数门禁差 30 字被拒。这是字数控制精度问题，不是链路断裂。

supplement 链路结论：**3/3 case 均健康**，无上传失败。
- patient: 48 facts (catalog=17, supplement=31)
- mechanism: 333 facts (catalog=2, supplement=331)
- news: 638 facts (catalog=17, supplement=621, 4 PDF)

### 评分分布

| case | weighted_total | qualified | 主要失分项 |
| --- | --- | --- | --- |
| lecanemab_patient（二次复现） | 77.5/100 | FAIL | hallucination_control=60（关键数字 72% 错写为 59%） |
| lecanemab_mechanism | 82.05/100 | PASS | key_facts=75（遗漏 81.4% 患者4年预后数据） |
| lecanemab_news | 未评分 | — | 字数门禁 FAIL（DOCX 2490 < 2520） |

3 case 中仅 1 case (mechanism) 完全 PASS。patient 的 hallucination_control=60 是唯一 <65 的维度；mechanism 最低维度 key_facts=75 仍在可接受范围。

### 六维归因后最大丢分项

跨 2 个有评分的 case，排列各维度：

| 维度 | patient | mechanism | 趋势 |
| --- | --- | --- | --- |
| task_completion | 85 | 88 | 稳定 |
| key_facts | 65 | 75 | **普遍偏弱** |
| audience_style | 90 | 85 | 稳定 |
| structure | 85 | 82 | 稳定 |
| title_angle | 80 | 88 | 稳定 |
| hallucination_control | 60 | 86 | **patient 个例严重** |

- **key_facts 是系统性弱项**（两 case 均为最低~次低维度），说明证据到稿件的关键数字覆盖率不足
- hallucination_control 的 60 分在 patient case 是个例问题（72%→59% 的关键数字错写），mechanism 的 86 证明系统不总是产生幻觉

### 主瓶颈判断

1. **内容质量瓶颈 > 工程链路瓶颈**。全链闭合已验证可复现，supplement 链路健康。当前主要卡点是"关键事实覆盖不完整"和"偶发关键数字错写"。
2. **调 prompt（写作指令层）优先级高于补资产**。证据阶段事实数量充足（48~638 条），问题出在写作稿件未命中金标准的关键数字，需加强写作 prompt 对关键数字的强调。
3. **字数控制需微调**。news 差 30 字，说明字数控制已接近但不够精确，可在 prompt 层或门禁容忍度上微调。

---

## 本轮 7 问裁决回答

### Q1: 全链是否可复现闭合？

**是。** 3/3 case 全链均可走到 delivery 层。patient 和 mechanism 全链含评分闭合。news 前 5 步正常，仅字数门禁差 30 字（非链路问题）。

### Q2: supplement/Vision 链路是否已修复？

**supplement 链路已验证健康。** 3 case 均无 `supplement_upload_failures`。patient 31 条、mechanism 331 条、news 621 条 supplement 全部成功。
Vision API 未在本轮做专门独立测试（本轮 3 case 均为 PDF 上传路径，不涉及 Vision API）。"Vision 已修"不能宣称，但 supplement 上传链路已有 3 case 直证。

### Q3: 扩样跨题分数是否稳定？

**尚不稳定。** 2 个有评分的 case 分数为 77.5 和 82.05，分差 4.55 分，但 1 PASS / 1 FAIL。1/3 的可用 PASS 率不足以宣称"跨题稳定"。加上 news 无评分，统计基线仍不完整。

### Q4: 评分六维归因后最大丢分项是什么？

**key_facts（关键事实与关键数字覆盖）是系统性最弱项。** patient 65 + mechanism 75 = 跨题均为最低~次低。hallucination_control 在 patient 的 60 分是本轮最严重的单维度问题（关键数字错写），但在 mechanism 恢复到 86，更可能是个例而非系统性。

### Q5: 主要瓶颈是 prompt 层还是资产层？

**prompt 层 > 资产层。** 证据数量充足（48~638 条），问题在于写作稿件未能充分命中金标准关键数字。建议在写作指令中显式列出"必须覆盖的关键数字清单"。

### Q6: 是否允许收紧标准件或进入 IIIB？

**不允许。** 当前 PASS 率 1/3（仅 mechanism），且 news 未获评分。按 03_阶段验收总表 的硬验收口径："这阶段只在'跑通最小闭环并形成可回写结论'时才算过"。当前闭环已跑通，但可回写结论仅限工程层（全链可复现、supplement 健康），内容质量结论不足以回写。需先解决 key_facts 系统性弱项和 news 字数门禁问题，再评估是否进入 IIIB。

### Q7: 本轮可回写的直接结论是什么？

**工程层可回写：**
1. 全链闭合可复现（3/3 case 直证）
2. supplement 链路健康（3/3 case 无上传失败）
3. 评分 provider MiniMax-M2.5 可用且六维可读
4. 字数门禁 ±10% 在 news case 触发了边界问题

**内容层不可回写：**
1. 仅 1/3 PASS，无法回写内容质量达标结论
2. key_facts 系统性弱项尚未修复
3. hallucination_control 偶发严重失分问题尚未有系统性解决方案

---
