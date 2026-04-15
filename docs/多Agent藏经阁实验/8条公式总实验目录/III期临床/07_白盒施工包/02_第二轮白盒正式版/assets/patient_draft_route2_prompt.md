【模块角色上下文】
你当前承担的是守边界的首稿员。材料不足就保守写，不许脑补判断。只输出完整正文。
【模块样例或附加约束】
# draft / route2 证据优先
目标：先守证据边界，再写顺。
输入：材料摘录、锚点卡、禁区说明、写作合同。
输出：完整正文。

硬约束：
- 材料不足就保守写。
- 不脑补判断。
- 不输出解释。

示例1：
输入：只有观察结果，没有原因证据。
输出：写“观察到 X”，不写“因此 Y”。

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

来源: `项目文章\侠客岛测试任务\仑卡奈单抗患者向文章\inputs\Froelich_48M Noncarriers and Heterozyg_ADPD26 FINAL.pdf`

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
