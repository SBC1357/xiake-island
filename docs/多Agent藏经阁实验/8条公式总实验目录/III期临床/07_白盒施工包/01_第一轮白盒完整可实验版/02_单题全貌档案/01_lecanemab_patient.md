# 仑卡奈单抗患者向文章（白盒第一轮单题全貌）

状态：白盒第一轮实验运行结果
日期：2026-04-11
用途：人工审核第一读物。本文只认本轮白盒 runtime 直证，不让人工去翻工程清单。

## 当前有效口径

1. 当前单题口径只认本轮白盒 phase run 的直接证据：合同、取材、提示词、生成稿、评分与回指。
2. 本文是白盒第一轮实验结果，不替代旧 `IIIA/06_单题全貌档案` 的历史 run 记录，也不把白盒评分直接冒充为阶段最终裁定。
3. 当前最重要的阅读目标只有一个：看清模型看到了什么、被怎样约束、最终写歪在什么层。

case_id: ``lecanemab_patient``
task_id: ``本轮白盒无后端 task_id``
run_dir: ``D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient``

## 当前明确缺项

1. 独立 planning prompt：本轮不存在；原因：白盒当前在合同层完成上游约束，不单独落 planning prompt 文件。
2. 独立 quality prompt：本轮不存在；原因：白盒当前直接落 `score_prompt.md`，不单独命名为 quality prompt。
3. 后端 `task_id / delivery docx`：本轮不存在；原因：当前是白盒批跑，不走旧后端任务对象和 delivery 链。

## 主阅读层

### 一、人工审核先看

1. 写作合同：写给 `患者和家属`，目标字数 `1500`，稿型 `患者向科普解读`，本轮目的为：面向患者和家属，用他们能理解的语言翻译仑卡奈单抗48个月临床数据的价值，帮助理解长期治疗获益。
2. 当前判定：当前白盒评分为 58 分，未达白盒当前合格线；当前问题不在入口链路，而在合同、材料和成稿的对齐。
3. 审稿优先看：路线根本性偏离：采用学术报告结构而非患者沟通叙事，ARCH-04情感主线完全断裂；关键事实遗漏：72%极早期患者4年认知未变差——这是参考答案的核心情感锚点和可感知判断；受众语言严重错位：ApE分层、CDR-SB、BioFINDER等术语未做患者翻译，缺乏'黄金时光''踩刹车'等隐喻系统
4. 当前最该改：重写开头：以'确诊后最害怕的是以后——他还能记住我多久'建立普世恐惧锚点，延迟术语出现

### 二、本轮真正喂给写手的材料（人工整理版）

人工阅读提示：
1. 本轮实际材料来源文件：Froelich_48M Noncarriers and Heterozyg_ADPD26 FINAL.pdf
2. 白盒合同要求优先承重的事实：48个月随访核心获益数据；临床衰退延缓百分比与时间换算；非携带者与杂合子亚组获益差异；长期治疗获益量化指标
3. 材料噪声：原始材料实际来自 PDF 全文提取，存在学术论文式表达、页眉页脚和图表上下文断裂等噪声。

实际入模材料整理稿：
```text
这题本轮白盒允许材料共 1 份，可提取材料 1 份。
主承重事实按白盒合同冻结为：48个月随访核心获益数据；临床衰退延缓百分比与时间换算；非携带者与杂合子亚组获益差异；长期治疗获益量化指标。
材料来源依次为：Froelich_48M Noncarriers and Heterozyg_ADPD26 FINAL.pdf。
材料整理原则：不是按论文页码罗列，而是只把当前稿件应承重的核心事实压给写手。
噪声说明：原始材料实际来自 PDF 全文提取，存在学术论文式表达、页眉页脚和图表上下文断裂等噪声。
```

### 三、本轮给模型的 prompt 全文

system prompt：
```text
whitebox_compat_mode = single_prompt_drafting
说明：本次白盒出稿采用单提示词模式，系统级约束已经内嵌进 writing_user_prompt.txt 与 whitebox_contract.json。
如需追溯更上游状态，请看 state_cards/*.json 与 whitebox_contract.json。

```

user prompt：
```text
你是侠客岛白盒编排器的执行写手。请严格按下面合同写一篇完整中文文章。

【写作合同】
- 题目：仑卡奈单抗患者向文章
- 题型：C
- 受众：患者和家属
- 目标字数：1500
- 写作目的：面向患者和家属，用他们能理解的语言翻译仑卡奈单抗48个月临床数据的价值，帮助理解长期治疗获益。
- 体裁：患者向科普解读

【公式驱动约束（当前已接线公式位）】
以下约束来自藏经阁8条公式的机器编码，你必须逐条遵守。

■ 人格定位：患者关怀者——站在患者和家属的焦虑与期待中，把临床试验数字翻译成“这对我意味着什么”，用温度而非术语建立信任。
■ 写作范围：RANGE-05/患者选择沟通
■ 写作目标：让患者和家属理解仑卡奈单抗4年数据意味着阿尔茨海默病治疗究竟能抢回多少时间。
■ 排列规则：先用患者痛感锚定，再做核心获益翻译，后给风险与选择引导。
■ 内容组合策略：患者选择沟通型——患者痛感起手 + 核心获益翻译 + 风险坦诚 + 理解引导
■ 逻辑组合策略：ARCH-04承重 + 人群分流/选择建议落点——先锚定患者关切，沿获益证据链展开，回收到选择理解

■ 有效大纲（你必须按此大纲组织全文，每个板块必须有实质内容）：
  - [患者痛感锚定] 以患者和家属最常问的问题开场，建立共情锚点
  - [核心获益翻译] 48个月延缓数据→抢回多少个月→日常能力保留
  - [人群差异理解] 非携带者vs杂合子→不同人获益不同→别套别人的结论
  - [风险与边界] 长期治疗要付出什么、有什么局限
  - [选择引导] 这些数据放在你的处境里意味着什么

■ 有效内容单元（以下每个单元必须在正文中至少出现一次，缺一扣分）：
  - 一个关于长期获益的可感知判断
  - 一条关于适用人群边界的明确声明
  - 一段关于治疗代价与风险的患者语言解剖
  - 一个从临床数字到“这意味着什么”的解释桥

■ 有效逻辑单元（全文承重逻辑必须遵守以下约束）：
  - ARCH-04承重贯穿全文——从焦虑到数据到理解的单一主线
  - 人群分流/选择建议落点——最终回收到“这对你意味着什么”

【必写事实清单】
以下每一条必须在正文中找到对应段落或句子，不得遗漏：
- 48个月随访核心获益数据
- 临床衰退延缓百分比与时间换算
- 非携带者与杂合子亚组获益差异
- 长期治疗获益量化指标

【文章结构要求】
文章必须按以下结构组织，每个板块必须有实质内容：
- 患者痛点与治疗期待
- 核心获益数据翻译
- 亚组人群获益解读
- 长期治疗价值
- 患者理解与选择路径

【硬规则】
1. 只能使用提供材料，不得调用外部知识，不得补材。
2. 不得使用参考答案内容反向改写；参考答案此轮不可见。
3. 如果本轮放开了参考样稿，它也只能提供结构、语气和返修锚点；不得照抄样稿中的事实、数字、判断、标题或结论。
4. D类题必须避开伪承重点（即使材料里有大量相关内容，也不能写成主轴）：
（无）
5. 如果材料不足以支撑某个强判断，改用保守写法，不要硬编。
6. 必写事实清单中列出的每一条都必须在正文中出现，缺一条扣分一次。
7. 写给临床医生看的文章，要用临床语言，避免过度学术腔和文献编号堆砌。
8. 数据来源层级标注：模型预测数据首次出现时必须标注"模型预测"；临床观测数据标注对应试验名；OLE或真实世界数据标注"OLE数据"或"真实世界数据"。不得混淆不同证据层级。
9. 材料中出现的 Figure / Table 编号必须在引用对应数据时标注来源锚点（如"Figure 5"），不得只写数字不注出处。
10. 如果上方公式驱动约束存在，你必须把人格定位贯穿全文语气和视角，每个有效内容单元至少在正文中对应一处实质段落，逻辑组合策略必须真正体现在全文承重结构中。



【证据锚点卡】
以下是从原始材料中提取的关键证据要点，写作时必须确保这些要点在正文中有对应落地：

# 仑卡奈单抗患者向文章 G0 资料卡

状态: verified

来源: `D:\汇度编辑部1\项目文章\侠客岛测试任务\仑卡奈单抗患者向文章\inputs\Froelich_48M Noncarriers and Heterozyg_ADPD26 FINAL.pdf`

规则: 本卡仅使用 raw PDF；未读取 gold、样稿、成稿 docx 或任何答案形文档。

## Must-Have Exact Values

- `48 months` / `4 years`: poster 的时间主轴，所有长期结果都按 48 个月口径展开。
- `1,521`: Clarity AD 中被纳入分析的 `ApoE ε4 non-carriers or heterozygotes` 数量。
- `31% / 53% / 16%`: 随机化患者中 `non-carriers / heterozygotes / homozygotes` 的组成。
- `10 mg/kg biweekly`: lecanemab 的给药方案。
- `9.8` 和 `14.2 months`: 48 个月时的 time saved，比较对象是 `ADNI` 和 `BioFINDER`。
- `32%`: 相比 `ADNI natural history cohort`，进展到下一 AD stage 的风险降低幅度。
- `Adverse event rates were lower or stabilized each additional year`: 安全性趋势句，作为长期安全性锚点。

## 关键比较位

- `lecanemab` vs `ADNI natural history cohort`: 进展风险比较。
- `lecanemab` vs `BioFINDER` / `ADNI`: 48 个月 time saved 比较。
- `ApoE ε4 non-carriers or heterozygotes` 子群 vs 更广义 `Clarity AD` 随机化人群。
- `adverse events` 随时间递推的年际比较：每增加一年，不良事件率下降或稳定。

## 图表 / 页面锚点

- `PDF page 1`: 整页 poster，全部 raw 证据都在这一页。
- `Clarity AD Study Design`: 样本与分组锚点，包含 `1,521`、`31% / 53% / 16%`。
- `Time saved and time to progression to next stage of AD with lecanemab treatment was also evaluated through 48 months`: 时间获益锚点。
- `SB Time Saved Analysis in BioFINDER`: `9.8` / `14.2 months` 的图表锚点。
- `Summary of Adverse Events by 12 Month Interval`: 安全性图表锚点。

## 页码

- `PDF`: `page 1` only.

## 证据摘要

- raw PDF 页 1 直接包含 poster 标题、`1,521` 样本数、`31% / 53% / 16%` 分层和 `10 mg/kg biweekly` 给药方案。
- raw PDF 页 1 直接包含 `Time saved evaluated at 48 months for CDR-SB`、`was 9.8 and 14.2 months vs ADNI and BioFINDER` 以及 `reduced the risk of progression to next AD stage by 32% compared to the ADNI natural history cohort`。
- raw PDF 页 1 直接包含安全性段落 `Adverse event rates were lower or stabilized each additional year`，可作为长期安全性锚点。


【材料摘录】
### Froelich_48M Noncarriers and Heterozyg_ADPD26 FINAL.pdf
LECANEMAB FOR EARLY ALZHEIMER'S DISEASE:
48-MONTH RESULTS FOR APOE 4 NON-CARRIERS OR HETEROZYGOTES

              FROM THE CLARITY AD OPEN-LABEL EXTENSION

                                          Lutz Froelich,1 Shobha Dhadda,2 Michio Kanekiyo,2 Amanda Goodwin,2
                                        Mark Hodgkinson,3 Steven Hersch,2 Michael Irizarry,2 and Lynn D. Kramer2

                       1. Medical Faculty Mannheim, University of Heidelberg, Central Institute of Mental Health, Mannheim, Germany. 2. Eisai Inc. Nutley, NJ, USA.
                                                                               3. Eisai Europe Ltd - Hatfield (United Kingdom).

                       Introduction                                                                                                                                                           Results (continued)

� Approximately 7 million people in Europe are currently living     � CDR-SB results in ApoE 4 non-carriers or heterozygotes of                                                                                                                                           � Results for delaying the next stage of dementia (ie, moderate or

  with Alzheimer's disease (AD), with estimates predicting a rise      Clarity AD are shown in Figure 2                                                                                                                                                                     severe AD) also favored lecanemab, with a relative risk of
  to 14 million by 20301-2                                                                                                                                                                                                                                                  progression delayed with lecanemab treatment by 55% vs ADNI
                                                                     Figure 2. CDR-SB in ApoE 4 Non-Carriers or Heterozygotes
� Lecanemab is a humanized immunoglobulin G1 monoclonal                                                                                                                                                                                                                    Figure 5. Time to Worsening on CDR-SB

  antibody that selectively binds to soluble A aggregate species3   Note: OLE includes those participants on intravenous and subcutaneous formulations. BioFINDER data are from BioFINDER 1. Analysis done in ApoE 4 Non-                                                                                                                                                                                    CDR-SB Range                               Staging Category
                                                                    carriers or Heterozygotes. In the EU, lecanemab is indicated as an intravenous infusion at a dosage of 10 mg/kg body weight, administered once every 2


请直接输出完整文章正文，不要加解释，不要加前言，不要加代码块。


```

### 四、当前稿件全文

1. 生成稿全文（必须直接贴入，不得只写路径）：
```text
# 仑卡奈单抗四年数据：这对您和家人的生活意味着什么

## 患者痛点与治疗期待

"医生，这药到底能为我爸争取多少时间？"

这是诊室里最常见的问题，也是无数阿尔茨海默病患者家属深夜反复咀嚼的焦虑。当家人开始出现重复提问、迷路、算不清账，我们既害怕病情发展的速度，又渴望抓住任何能拖住时间的东西。仑卡奈单抗（lecanemab）进入视野时，大家听到的多是"清除脑内淀粉样蛋白"这样的医学概念——但这和"妈妈还能认得出我"之间，隔着一道需要翻译的鸿沟。

四年过去了。第一批接受治疗的患者已经走完48个月的旅程，他们的数据终于能回答那个最朴素的问题：**长期用药，究竟能抢回多少个月的生活？**

## 核心获益数据翻译

让我们直接看数字，再把它翻译成您餐桌旁能听懂的话。

在Clarity AD研究及其开放标签延伸期（OLE）中，针对ApoE ε4非携带者或杂合子人群——这是占入组患者绝大多数的群体（1,521人，占随机化人群的84%）——48个月时的分析显示：**与ADNI自然病史队列相比，仑卡奈单抗将进展至下一阶段阿尔茨海默病的风险降低了32%**（Figure 5）。

更直观的指标是"时间节省"（time saved）。通过与两个独立的真实世界队列比较，48个月时仑卡奈单抗治疗组在CDR-SB评分（临床痴呆评定量表-总分，衡量认知与日常功能的金标准）上展现出**9.8个月（对比ADNI）和14.2个月（对比BioFINDER）的延缓**（SB Time Saved Analysis in BioFINDER）。

**这意味着什么？** 一位早期阿尔茨海默病患者，如果不治疗，可能在第36个月就进入中度痴呆阶段；而坚持仑卡奈单抗治疗四年，这位患者有可能在第48个月仍维持在轻度阶段。多出来的这近一年到一年多，是还能自己穿衣吃饭、还能认出家人、还能参与家庭决策的时间。这不是"治愈"，这是**把"还能自理"的窗口期实实在在地拉长**。

## 亚组人群获益解读

但数据不能简单套用在每个人身上。这里必须坦诚一个关键区分：ApoE ε4基因状态。

在Clarity AD随机化人群中，31%为ApoE ε4非携带者，53%为杂合子，16%为纯合子。本次48个月分析聚焦于**非携带者和杂合子**——即那84%的大多数。为什么？因为纯合子患者面临更高的淀粉样蛋白相关影像异常（ARIA）风险，治疗决策需要更谨慎的个体化权衡。

**可感知判断**：如果您或家人属于非携带者或杂合子，这份四年数据对您有直接参考价值；如果是纯合子，则需要与医生讨论风险收益比，不能简单套用上述时间延缓数字。别人的"14个月"不一定是您的"14个月"，基因背景是疗效和安全性的重要调节器。

## 长期治疗价值

四年不是终点，但已经足够说明问题。长期治疗的价值体现在两个层面：

**第一，获益的累积性**。认知衰退的延缓不是"用一年算一年"，而是持续用药带来的持续保护。48个月数据显示，这种保护效应在四年间得以维持，没有出现"药效耗尽"的迹象。

**第二，安全性的可管理性**。这是家属最担心的——打四年针，身体吃得消吗？数据给出了相对安心的信号：**不良事件发生率随治疗年限增加而降低或趋于稳定**（Summary of Adverse Events by 12 Month Interval）。换句话说，最艰难的安全窗口往往在第一年，随着治疗延续，身体对药物的耐受性并未恶化，反而趋于平稳。

## 患者理解与选择路径

把这一切放回您的处境，这意味着什么？

**如果您正处于早期阿尔茨海默病，正在考虑是否开始或继续仑卡奈单抗：**

- 四年数据支持**长期治疗的合理性**——这不是短期尝试，而是一场需要承诺的马拉松
- 预期获益是**延缓而非逆转**，目标是把"轻度阶段"拉长近一年到一年多
- 前提是**定期MRI监测ARIA**，尤其是治疗初期

**如果您是家属，正在帮父母做决策：**

- 先确认ApoE ε4状态，这决定您该参考哪组数据
- 计算的不只是药费，还有**两年一次的输液/注射时间、往返医院的精力、监测影像的耐心**
- 最坏的打算也要做——如果出现ARIA，是否愿意暂停或终止治疗？

**一条关于适用人群边界的明确声明**：仑卡奈单抗适用于早期阿尔茨海默病患者（轻度认知障碍或轻度痴呆阶段），且需确认脑内淀粉样蛋白阳性。48个月数据 specifically 来自ApoE ε4非携带者或杂合子人群，每两周10mg/kg静脉给药方案。不适用于中重度痴呆患者，也不适用于未确认淀粉样蛋白病理的认知下降。

**一段关于治疗代价与风险的患者语言解剖**：四年治疗意味着约100次静脉输注，每次约1小时；意味着定期的MRI检查，前18个月尤其密集；意味着需要警惕的警告信号——剧烈头痛、视觉模糊、意识混乱，这些可能是ARIA的信号，需要立即就医。最常见的副作用是输液反应（寒战、发热）和ARIA（脑水肿或微出血）。好消息是，随着时间推移，这些风险并未累积加重。

---

四年数据终于让我们能对患者和家属说：**这不是一个虚无的承诺**。近一年的功能保留，是还能自己决定吃什么、还能和家人聊天、还能感受生活质量的365天。对于阿尔茨海默病这种至今无法治愈的疾病，**时间本身就是最珍贵的疗效**。

最终的选择权在您手中。带着这些数据，和您的医生讨论：您的基因背景、您的身体状况、您对生活质量的期待——然后决定，这四年证明的价值，是否值得您开始或继续这场与时间的赛跑。

```

### 五、当前审核意见与返修抓手

1. 总分与当前判定：`58` 分；`qualified=false`；白盒 review_bundle 已落盘。
2. 各维度关键失分：
   - `route_alignment`：路线严重偏离。合同要求RANGE-05/患者选择沟通路线，强调'患者痛感起手+核心获益翻译+风险坦诚+理解引导'的内容组合和'ARCH-04承重+人群分流/选择建议落点'的逻辑组合。系统稿采用学术报告式结构（痛点-数据-亚组-长期价值-选择路径），缺乏情感锚定和叙事张力，未沿'焦虑→数据→理解'的单一主线展开，而是信息罗列式推进。落点虽提及选择，但缺乏'这对你意味着什么'的强回收。
   - `key_facts`：核心数据存在但呈现方式错位。48个月延缓数据（9.8-14.2个月）已呈现，但关键事实'72%极早期患者4年认知未变差'完全缺失——这是参考答案的核心亮点和情感锚点。'进展风险降低55%'被替换为'32%'，数据来源表述混乱（ADNI/BioFINDER对比 vs 原始研究）。ApoE分层信息过度技术化，未转化为患者可感知的'不同人获益不同'的通俗解释。
   - `audience_style`：严重偏离患者受众要求。大量使用术语（'ApoE ε4非携带者或杂合子''CDR-SB评分''BioFINDER队列''ARIA''OLE'）未做患者语言翻译。语气冷静分析而非'温度建立信任'，缺乏'陪孙子过春节''多喘口气'等生活化锚点。第二人称使用生硬（'您'），缺乏真正共情。风险披露过度技术化（'前18个月MRI密集监测'），未转化为'这意味着什么'的情感理解。
   - `structure`：结构完整但不符合公式要求的outline。合同要求5段式结构：[患者痛感锚定]-[核心获益翻译]-[人群差异理解]-[风险与边界]-[选择引导]。系统稿实际为6段，将'人群差异'与'风险'拆分过细，且'患者痛感'段落过短、缺乏问题感建立，'选择引导'段落分散在多处而非强落点。小标题学术化（'亚组人群获益解读'），缺乏'黄金时光''踩刹车'等隐喻张力。
   - `hallucination_control`：无明显事实编造，但存在数据选择性呈现和来源混淆。'32%风险降低'与参考答案'55%'差异大，可能源于不同对比基准（ADNI vs 未治疗对照），但未向读者澄清。'100次静脉输注'计算准确（26周/年×4年≈104次，取整合理）。ApoE分层数据与参考文献一致。未出现虚构研究或夸大疗效。
3. 返修抓手：
   - 重写开头：以'确诊后最害怕的是以后——他还能记住我多久'建立普世恐惧锚点，延迟术语出现
   - 植入核心数据：必须加入'72%极早期患者4年认知未变差'，作为'可感知判断'的核心支撑
   - 建立隐喻系统：采用'踩刹车''黄金时光''抢回时间'等患者可感知隐喻，替代ADNI/BioFINDER等技术对比
   - 重构风险段落：集中解剖'四年100次输液''前18个月密集监测''ARIA信号识别'，用'这意味着什么'引导
   - 强化落点：结尾必须回收'这对你意味着什么'，针对个体处境（基因状态、病程阶段、照护资源）给出决策框架
4. 人工审核时的重点对照项：
   - 合同主线是否真的被成稿贯彻：`面向患者和家属，用他们能理解的语言翻译仑卡奈单抗48个月临床数据的价值，帮助理解长期治疗获益。`
   - 必写事实是否都在正文真正落句：48个月随访核心获益数据；临床衰退延缓百分比与时间换算；非携带者与杂合子亚组获益差异；长期治疗获益量化指标
   - 评分回指当前最重的问题：路线根本性偏离：采用学术报告结构而非患者沟通叙事，ARCH-04情感主线完全断裂；关键事实遗漏：72%极早期患者4年认知未变差——这是参考答案的核心情感锚点和可感知判断；受众语言严重错位：ApE分层、CDR-SB、BioFINDER等术语未做患者翻译，缺乏'黄金时光''踩刹车'等隐喻系统

## 工程附录

### Runtime 指针

1. `run_summary.md`：本轮白盒不存在；对应批量摘要为 `D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\phase_summary.md`
2. `task_detail.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\task_detail.json`
3. `generated.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\generated.txt`
4. `materials_full.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\materials_full.json`
5. `review_bundle.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\review_bundle.json`
6. `score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\score.json`
7. `summary.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\summary.json`
8. `writing_system_prompt.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\writing_system_prompt.txt`
9. `writing_user_prompt.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\writing_user_prompt.txt`

### 本轮关键证据

1. 上传与 evidence：当前白盒不走旧 upload 任务对象；证据直接来自 `D:\汇度编辑部1\项目文章\侠客岛测试任务\仑卡奈单抗患者向文章` 中允许的输入文件。
2. 阶段到达情况：`contract_ready=True` `materials_ready=True` `draft_ready=True` `scoring_ready=True` `review_bundle_ready=True`
3. 交付与评分：本轮生成稿路径为 `D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\generated.txt`，当前分数 `58`，达标结论 `False`。
4. planning / writing 卡片：本轮白盒上游状态卡目录为 `D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\state_cards`。

### materials 指针

1. 当前人工审稿材料文件：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\materials_full.json`
2. 同轮回退锚点：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\materials\materials_digest.md`

### prompt 指针

1. system prompt：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\writing_system_prompt.txt`
2. user prompt：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\writing_user_prompt.txt`
3. 同轮回退锚点：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\draft_prompt.md`

### 评分结果

1. 总分：`58`
2. 达标结论：`False`
3. 评分状态：`completed`
4. 各维度：
   - `任务完成度`：路线严重偏离。合同要求RANGE-05/患者选择沟通路线，强调'患者痛感起手+核心获益翻译+风险坦诚+理解引导'的内容组合和'ARCH-04承重+人群分流/选择建议落点'的逻辑组合。系统稿采用学术报告式结构（痛点-数据-亚组-长期价值-选择路径），缺乏情感锚定和叙事张力，未沿'焦虑→数据→理解'的单一主线展开，而是信息罗列式推进。落点虽提及选择，但缺乏'这对你意味着什么'的强回收。
   - `关键事实与关键数字覆盖`：核心数据存在但呈现方式错位。48个月延缓数据（9.8-14.2个月）已呈现，但关键事实'72%极早期患者4年认知未变差'完全缺失——这是参考答案的核心亮点和情感锚点。'进展风险降低55%'被替换为'32%'，数据来源表述混乱（ADNI/BioFINDER对比 vs 原始研究）。ApoE分层信息过度技术化，未转化为患者可感知的'不同人获益不同'的通俗解释。
   - `受众匹配与文风匹配`：严重偏离患者受众要求。大量使用术语（'ApoE ε4非携带者或杂合子''CDR-SB评分''BioFINDER队列''ARIA''OLE'）未做患者语言翻译。语气冷静分析而非'温度建立信任'，缺乏'陪孙子过春节''多喘口气'等生活化锚点。第二人称使用生硬（'您'），缺乏真正共情。风险披露过度技术化（'前18个月MRI密集监测'），未转化为'这意味着什么'的情感理解。
   - `AI味儿控制`：本轮白盒未单独拆出 AI 味儿维度；当前主要参考 `audience_style`、`formula_compliance` 与 `writing_strength` 回指。
   - `结构与信息取舍`：结构完整但不符合公式要求的outline。合同要求5段式结构：[患者痛感锚定]-[核心获益翻译]-[人群差异理解]-[风险与边界]-[选择引导]。系统稿实际为6段，将'人群差异'与'风险'拆分过细，且'患者痛感'段落过短、缺乏问题感建立，'选择引导'段落分散在多处而非强落点。小标题学术化（'亚组人群获益解读'），缺乏'黄金时光''踩刹车'等隐喻张力。
   - `标题角度与稿型适配`：本轮白盒未单独拆出标题维度；当前主要参考 `route_alignment` 与 `formula_trace` 中的稿型偏移判断。
   - `幻觉与越界编造控制`：无明显事实编造，但存在数据选择性呈现和来源混淆。'32%风险降低'与参考答案'55%'差异大，可能源于不同对比基准（ADNI vs 未治疗对照），但未向读者澄清。'100次静脉输注'计算准确（26周/年×4年≈104次，取整合理）。ApoE分层数据与参考文献一致。未出现虚构研究或夸大疗效。
5. 本轮已执行评分。

### 本轮真实 blocker

1. 路线根本性偏离：采用学术报告结构而非患者沟通叙事，ARCH-04情感主线完全断裂
2. 关键事实遗漏：72%极早期患者4年认知未变差——这是参考答案的核心情感锚点和可感知判断
3. 受众语言严重错位：ApE分层、CDR-SB、BioFINDER等术语未做患者翻译，缺乏'黄金时光''踩刹车'等隐喻系统
4. 内容组合失败：未实现'患者痛感起手+核心获益翻译+风险坦诚+理解引导'的沟通型结构，而是信息罗列型

### 证据摘要

1. 已直接核对：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\summary.json` 中 `task_status=completed`、`weighted_total=58`、`qualified=False`。
2. 已直接核对：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\review_bundle.json` 已直接给出 blocking_issues / missing_or_misaligned / backtrace，可回指失配层。
3. 已直接核对：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase\20260411_215434_236_iiia_whitebox_v1\contracts\20260411_215434_274_lecanemab_patient\writing_user_prompt.txt` 与 `generated.txt` 同轮存在，人工可直接看模型被怎样约束、最终写成什么。