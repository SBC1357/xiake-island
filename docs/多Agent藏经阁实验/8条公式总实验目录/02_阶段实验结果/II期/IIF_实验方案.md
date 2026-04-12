# IIF 实验方案（终版）

状态：ready_to_execute  
日期：2026-04-08  
前序：IIE 管线搭建通过（72分 / qualified × 2, formula_compliance=65）

## 一、双目标定义

IIF 不是单一因果实验，而是同时回答两个问题：

1. **因果性**：8公式驱动对稿件质量有没有可测量的正向增益？
2. **系统上限**：当公式+样稿+revise loop 全部打开时，白盒管线能达到什么分数？

两个目标独立裁决。IIF-1 因果性失败不杀死 IIF-4 上限臂；上限臂无论因果性是否成立都要跑完。

## 二、变量设计

| 变量 | 含义 | 控制方式 |
|------|------|----------|
| formula_positions | 8公式位编码（15位） | A组无 / B组有 |
| reference_sample | 参考样稿 | 不放开 / 放开（-EnableReferenceSample） |
| revise_loop | score→revise循环 | 不做 / 做（max 3轮） |
| anchor_card | 轻量锚点卡(.md) | 全部放开（非自变量） |

### 变量来源边界硬规

formula_positions 只允许从以下来源推导：
- raw_source_analysis.md
- 候选题的 case_type / audience / purpose / genre
- IIB 共享映射规则（RANGE→min_content_unit / min_logic_unit 表）

**按样稿或 gold 去反推 formula_positions，视为变量污染，不得进入正式 IIF。**

## 三、4臂设计与题目分配

### IIF-1：公式因果性（3题）

| # | 候选ID | A臂（无公式） | B臂（有公式） |
|---|--------|---------------|---------------|
| 1 | compassion15_os_c | ✓ | ✓ |
| 2 | zolbetuximab_safety_d | ✓ | ✓ |
| 3 | sindi_gastric_esmo_c | ✓ | ✓ |

- 样稿：不放开
- revise loop：不做
- 评分：主表5维 + 公式审计（B臂）
- 判定：B臂 weighted_total 均值 > A臂均值 5分以上，且 formula_compliance ≥ 70

### IIF-2：样稿增益（2题）

| # | 候选ID | 公式 | 样稿 |
|---|--------|------|------|
| 4 | ctad_lb13_c | ✓ | ✓（-EnableReferenceSample） |
| 5 | ctad_p096_c | ✓ | ✓（-EnableReferenceSample） |

- 基准：IIF-1 B臂同配置（有公式无样稿）对 ctad_lb13_c 和 ctad_p096_c 各跑一次
- revise loop：不做
- 判定：加样稿后 weighted_total 较基准涨 ≥ 3分，且 writing_strength 有可见改善

### IIF-3：revise loop（2题）

| # | 候选ID | 公式 | 样稿 | revise |
|---|--------|------|------|--------|
| 6 | iie_reg_patient_c | ✓ | ✓ | ✓（max 3轮） |
| 7 | iie_reg_mechanism_c | ✓ | ✓ | ✓（max 3轮） |

- 基准：IIF-2 同配置（公式+样稿、无revise）对同题各跑一次
- 判定：revise loop 后 weighted_total 涨 ≥ 3分，且 missing_or_misaligned 项数下降

### IIF-4：系统上限（3题）

| # | 候选ID | 公式 | 样稿 | revise |
|---|--------|------|------|--------|
| 8 | ctad_lb21_c | ✓ | ✓ | ✓ |
| 9 | ctad_p279_c | ✓ | ✓ | ✓ |
| 10 | lecanemab_news_c | ✓ | ✓ | ✓ |

- 全部变量打开
- 额外：claim_ceiling标注（对每个分维给出"当前材料+管线能力下的理论天花板分"）
- 判定：weighted_total ≥ 85 为"可交付草稿"，≥ 75 为"有价值底稿"

## 四、评分系统

### 主表（5维，跨组可比）

| 维度 | 权重 | 说明 |
|------|------|------|
| route_alignment | 25% | 路线与写作目的一致性 |
| key_facts | 25% | 关键事实覆盖与准确度 |
| audience_style | 20% | 受众语体匹配度 |
| structure | 15% | 结构完整性与逻辑通畅度 |
| hallucination_control | 15% | 幻觉与越界编造控制 |

weighted_total = 加权总分（0-100），qualified = weighted_total ≥ 72

### 写作力副表（5维，0-100，不计入weighted_total）

| 维度 | 说明 |
|------|------|
| opening_hook | 开场抓力与问题感 |
| transition_flow | 段间过渡流畅度 |
| midgame_drive | 中段推进感与信息密度 |
| closing_tension | 收尾张力与意义回收 |
| anchor_fidelity | 锚点卡要点在正文中的落地度 |

### 公式审计（仅限有formula_contract的组）

- formula_compliance: 0-100（命中率80%以上且无关键位miss→80+）
- formula_trace: 逐条 hit/miss/partial + 证据
- formula_compliance_summary: 公式合规总评

## 五、输出规范

### 1. 运行时产物

全部落在 `D:\汇度编辑部1\侠客岛-runtime\ii_whitebox\` 下，按 `{timestamp}_{candidate_id}_iif{arm}_{group}` 命名。

### 2. 成果整理

每完成一题，在 `II期成果整理/` 下新增全貌文件：
- 命名：`IIF_{arm}_{candidate_id}_全貌.md`
- 结构：按现有全貌格式（主阅读层+工程附录层）
- 试验组和对照组的成稿都必须内嵌到全貌文件中
- 每题全貌必须包含：prompt全文、稿件全文、评分全文、revise记录（如有）

### 3. 汇总结论

IIF 全部跑完后，输出两份结论：
1. **因果性结论**：8公式驱动是否带来可测量的质量增益（基于IIF-1）
2. **系统上限结论**：当前白盒管线在全部变量打开时能达到的最高水平（基于IIF-4）

## 六、执行顺序

1. IIF-1 × 3题（A/B两组各跑一次，共6次）
2. IIF-2 × 2题（基准+样稿各1次，共4次）
3. IIF-3 × 2题（基准+revise各1次，共4次）
4. IIF-4 × 3题（全开各1次，共3次）

总计：17次管线执行

## 七、终止条件

- IIF-1 结果：如果B臂均值 ≤ A臂均值（公式无正向增益），因果性结论判"不成立"，但不终止IIF-2/3/4
- IIF-4 结果：如果3题 weighted_total 均 < 72，系统上限结论判"未达可交付水平"
- 任何题目 LLM 调用失败：标记 agent_continue_required，不阻塞其他题目

## 八、前置条件清单

| # | 条件 | 状态 | 验证证据 |
|---|------|------|----------|
| 1 | 10个候选全部在 ii_candidate_pool.json 中 | ✅ 已完成 | lecanemab_news_c 已加入；orchestrator -ListCandidates 列出10个 |
| 2 | 全部10个候选有 formula_positions | ✅ 已完成 | 7个原空位＋第10个新建，JSON validated |
| 3 | iie_reg_patient_c / iie_reg_mechanism_c 有 reference_sample_path | ✅ 已完成 | 两条 reference_sample_path + metadata 均已写入 |
| 4 | 10个候选都有轻量 anchor_card.md | ✅ 已完成 | 5个新建（sindi/lb21/p096/p279/mechanism），5个已有 |
| 5 | score.ps1 支持 writing_strength 副表 | ✅ 已完成 | 5维独立数组 + formula_compliance 分离 + 权重标注 |
| 6 | revise loop 脚本存在 | ✅ 已完成 | run_ii_whitebox_revise.ps1 ~230行，语法检查通过 |
| 7 | draft.ps1 支持读取 anchor_card.md | ✅ 已完成 | 读取 contract.anchor_card_path → 注入 prompt |
| 8 | orchestrator.ps1 支持 anchor_card 路径 | ✅ 已完成 | anchor_card_path 写入 contract；smoke test 确认字段存在 |
