# IIF 因果性结论

状态：frozen  
日期：2026-04-07  
数据来源：IIF-1 三题 A/B 对比（6次管线执行）

## 一、原始数据

| 候选题 | A臂 wt（无公式） | B臂 wt（有公式） | Δ | B臂 fc |
|--------|:-:|:-:|:-:|:-:|
| compassion15_os_c | 58 | 72 | **+14** | 72 |
| zolbetuximab_safety_d | 58 | 68 | **+10** | 62 |
| sindi_gastric_esmo_c | 72 | 58 | **-14** | 35 |

## 二、判定指标

| 指标 | 阈值 | 实测 | 是否达标 |
|------|------|------|:--------:|
| B臂 wt 均值 - A臂 wt 均值 | > 5 | +3.33 (66.0 vs 62.67) | ✗ |
| B臂 formula_compliance 均值 | ≥ 70 | 56.33 | ✗ |

## 三、结论

**因果性不成立。**

8公式驱动对稿件质量**没有**可测量的、稳定的正向增益。

### 事实依据

1. B臂均值仅高出A臂3.33分，未达5分阈值
2. B臂 formula_compliance 均值56.33，远低于70阈值
3. 3题中有1题（sindi_gastric_esmo_c）B臂反而比A臂低14分，说明公式在部分题目上不仅无效，还有负面干扰
4. 2题B臂提升（+14, +10）与1题大幅下降（-14）之间方差极大，不具有一致性

### 分维细节

| 维度 | A臂均值 | B臂均值 | Δ |
|------|:-------:|:-------:|:-:|
| route_alignment | 55.0 | 65.0 | +10.0 |
| key_facts | 69.3 | 67.7 | -1.7 |
| audience_style | 65.0 | 68.3 | +3.3 |
| structure | 64.3 | 67.7 | +3.3 |
| hallucination_control | 80.0 | 60.0 | **-20.0** |

公式驱动在 route_alignment 上有一定正向效果（+10），但在 hallucination_control 上出现严重倒退（-20），说明公式约束在提升路线对齐的同时可能引入了过度推断。

## 四、限制性说明

1. 3题样本量偏小，统计显著性低
2. compassion15_os_c / zolbetuximab_safety_d 的A臂 formula_positions 实际为空值结构（之前被清空再恢复），与"从未有公式"的理想对照组有微弱差异
3. sindi_gastric_esmo_c B臂的 fc=35 极低，说明该题的公式可能本身编码质量不足
4. 评分模型本身是 LLM 自评，存在评分器偏差

---

runtime产物路径：
- A臂: `侠客岛-runtime\ii_whitebox\20260407_020647_471_compassion15_os_c` / `_020840_503_zolbetuximab_safety_d` / `_021033_483_sindi_gastric_esmo_c`
- B臂: `侠客岛-runtime\ii_whitebox\20260407_021319_455_compassion15_os_c` / `_021501_434_zolbetuximab_safety_d` / `_021650_968_sindi_gastric_esmo_c`
