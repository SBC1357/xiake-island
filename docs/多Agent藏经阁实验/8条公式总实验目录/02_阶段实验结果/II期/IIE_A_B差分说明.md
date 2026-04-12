# IIE A/B 差分说明

状态：已冻结  
日期：2026-04-07  
用途：逐条可审计的 A/B prompt 差分清单。IIF 执行前不得修改。

## 差分总则

- A 组 = 白盒管线 + 当前已接线的公式驱动约束进入 prompt / contract / scoring
- B 组 = 同模型同材料同闭卷通用写作指令
- **唯一自变量**：8 公式驱动约束的有无

## Draft Prompt 差分

### 差分 1：公式驱动约束段落

| 位置 | A 组 | B 组 |
| --- | --- | --- |
| 写作合同之后、必写事实清单之前 | 存在「【公式驱动约束（当前已接线公式位）】」完整段落 | **不存在** |

**A 组独有内容**：
```
【公式驱动约束（当前已接线公式位）】
以下约束来自藏经阁8条公式的机器编码，你必须逐条遵守。

■ 人格定位：{{persona}}
■ 写作范围：{{range}}
■ 写作目标：{{write_target}}
■ 排列规则：{{arrangement_rule}}
■ 内容组合策略：{{content_combo}}
■ 逻辑组合策略：{{logic_combo}}

■ 有效大纲：[列表]
■ 有效内容单元：[列表]
■ 有效逻辑单元：[列表]
```

### 差分 2：硬规则第 10 条

| 位置 | A 组 | B 组 |
| --- | --- | --- |
| 硬规则列表末尾 | 存在第 10 条 | 硬规则只到第 9 条 |

**A 组独有内容**：
```
10. 如果上方公式驱动约束存在，你必须把人格定位贯穿全文语气和视角，
    每个有效内容单元至少在正文中对应一处实质段落，
    逻辑组合策略必须真正体现在全文承重结构中。
```

## Score Prompt 差分

### 差分 3：评分维度 formula_compliance

| 位置 | A 组 | B 组 |
| --- | --- | --- |
| dimensions 数组 | 含 `formula_compliance` 维度 | 不含 |

### 差分 4：formula_trace 输出

| 位置 | A 组 | B 组 |
| --- | --- | --- |
| JSON 输出 schema | 含 `formula_trace` 数组 + `formula_compliance_summary` 字段 | 不含 |

### 差分 5：评分规则 3-4

| 位置 | A 组 | B 组 |
| --- | --- | --- |
| 评分规则 3 | `formula_trace 必须逐条审计公式合规审计段中列出的每个公式位` | 不存在 |
| 评分规则 4 | `formula_compliance 评分：命中率80%以上且无关键位miss得80+` | 不存在 |

### 差分 6：公式合规审计段

| 位置 | A 组 | B 组 |
| --- | --- | --- |
| 评分 prompt 中参考答案段之前 | 存在「【公式合规审计（formula_trace）】」段落 | 不存在 |

### 差分 7：backtrace 回指层

| 位置 | A 组 | B 组 |
| --- | --- | --- |
| backtrace.target_layer 枚举 | 含 `formula_contract` | 不含 `formula_contract` |

## Contract 差分

### 差分 8：whitebox_contract.json

| 字段 | A 组 | B 组 |
| --- | --- | --- |
| `formula_contract` | 存在当前已落进白盒 contract 的机器可读公式对象；未独立成键的公式位不得提前宣称“完整 15 位对象” | 不存在此字段 |

## 通用部分确认（A/B 逐字一致）

以下部分 A/B 两组必须完全相同：

1. 写作合同段（题目、题型、受众、目标字数、写作目的、体裁）
2. 必写事实清单段
3. 文章结构要求段
4. 硬规则 1-9
5. 参考样稿锚点段（如有）
6. 材料摘录段
7. 结尾指令句

## 实现方式

A 组：直接使用当前 `run_ii_whitebox_draft.ps1` + `run_ii_whitebox_score.ps1`（candidate 含 `formula_positions`）  
B 组：使用同一管线，但 candidate 的 `formula_positions` 字段设为 `null` 或不提供 → 管线自动跳过公式段落

## 审计检查点

- [ ] A 组 draft_prompt.md 包含「公式驱动约束」段落
- [ ] B 组 draft_prompt.md 不包含「公式驱动约束」段落
- [ ] A 组 score_prompt.md 包含 `formula_compliance` 维度
- [ ] B 组 score_prompt.md 不包含 `formula_compliance` 维度
- [ ] A/B 两组 draft_prompt.md 的通用部分逐字一致
- [ ] A/B 两组闭卷条件一致（draft_manifest.json 中 reference_answer_visible_before_draft = false）
