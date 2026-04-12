# 仑卡奈单抗患者向文章（返修 Loop 单题全貌）

状态：fixed-baseline 返修实验结果
日期：2026-04-12
用途：人工直接评估返修 loop 是否真的把同一份基线稿修好。本文只认固定基线稿上的返修轨迹，不拿整题重跑漂移冒充 loop 效果。

## 当前有效口径

1. 当前口径只认固定基线返修实验：同一份基线稿、同一份基线 prompt、同一路评分器，观察 `review -> revise -> rescore` 是否真正提分。
2. 本文不替代白盒第一轮基线全貌；基线稿的完整首轮上下文仍回看基线全貌。
3. 如果最终 `qualified=true` 但 `missing_or_misaligned` 仍残留，只能判定为“返修有用/能提分”，不能偷换成“题目已经完全收口”。
4. fixed-baseline 返修实验当前以最终轮 `round_N/score.json` 作为最终缺口口径；根目录 `review_bundle.json` 仍停在基线稿口径，不能拿来冒充最终审稿结论。

case_id: ``lecanemab_patient``
baseline_fullview: ``D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\07_白盒施工包\01_第一轮白盒完整可实验版\02_单题全貌档案\01_lecanemab_patient.md``
eval_dir: ``D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient``

## 主阅读层

### 一、人工审核先看

1. 基线分数：`58`；最终分数：`78`；最终达标：`true`；实际返修轮次：`2`。
2. 当前裁定：这题在固定基线稿上经返修后从 `FAIL` 拉到 `PASS`，说明返修 loop 对本题有用。
3. 当前仍残留缺项：2026年ADPD国际大会来源锚点缺失；APOE非携带者/杂合子的明确术语表述缺失（改用描述性语言）；风险段位置与content_combo要求的嵌入节奏不一致；选择引导落点偏理性决策，情感回收不足
4. 建议阅读顺序：先看“轮次轨迹”，再看每轮修稿任务书，最后看最终成稿全文和最终剩余缺口。

### 二、轮次轨迹

1. 第 1 轮：58 -> 68；qualified=false；缺项 6 -> 4
2. 第 2 轮：68 -> 78；qualified=true；缺项 4 -> 4

### 三、基线写作合同与基线 prompt

1. 受众：`患者和家属`；体裁：`患者向科普解读`；目标字数：`1500`；写作目的：面向患者和家属，用他们能理解的语言翻译仑卡奈单抗48个月临床数据的价值，帮助理解长期治疗获益。
2. 基线 user prompt 全文：
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

### 四、每轮修稿任务书

#### 第 1 轮修稿任务书（全文）

本轮评分变化：`58` -> `68`；本轮缺项变化：`6` -> `4`；本轮达标：`false`。
```text
你是侠客岛白盒编排器的修稿执行器。以下是当前稿件和评分反馈，请根据反馈修改稿件。

【写作合同】
- 题目：仑卡奈单抗患者向文章
- 受众：患者和家属
- 写作目的：面向患者和家属，用他们能理解的语言翻译仑卡奈单抗48个月临床数据的价值，帮助理解长期治疗获益。

【公式驱动约束（修稿时同样必须遵守）】
- 人格定位：患者关怀者——站在患者和家属的焦虑与期待中，把临床试验数字翻译成“这对我意味着什么”，用温度而非术语建立信任。
- 写作范围：RANGE-05/患者选择沟通
- 写作目标：让患者和家属理解仑卡奈单抗4年数据意味着阿尔茨海默病治疗究竟能抢回多少时间。
- 有效内容单元：
  - 一个关于长期获益的可感知判断
  - 一条关于适用人群边界的明确声明
  - 一段关于治疗代价与风险的患者语言解剖
  - 一个从临床数字到“这意味着什么”的解释桥

【评分反馈（第 1 轮修稿输入）】
- 当前总分：58
- 是否合格：False

阻塞问题：
- 路线根本性偏离：采用学术报告结构而非患者沟通叙事，ARCH-04情感主线完全断裂
- 关键事实遗漏：72%极早期患者4年认知未变差——这是参考答案的核心情感锚点和可感知判断
- 受众语言严重错位：ApE分层、CDR-SB、BioFINDER等术语未做患者翻译，缺乏'黄金时光''踩刹车'等隐喻系统
- 内容组合失败：未实现'患者痛感起手+核心获益翻译+风险坦诚+理解引导'的沟通型结构，而是信息罗列型

缺失或偏差项：
- 缺失：72%极早期患者4年认知未变差的核心数据
- 缺失：'进展风险降低55%'的关键获益表述（稿中为32%）
- 缺失：'踩刹车'下坡车的核心隐喻
- 缺失：'多陪孙子过春节''多喘口气'等生活化时间锚点
- 错位：ApoE分层呈现为技术统计而非'不同人不同获益'的通俗理解
- 错位：风险披露分散在技术段落而非集中的'患者语言解剖'

建议修改动作：
- 重写开头：以'确诊后最害怕的是以后——他还能记住我多久'建立普世恐惧锚点，延迟术语出现
- 植入核心数据：必须加入'72%极早期患者4年认知未变差'，作为'可感知判断'的核心支撑
- 建立隐喻系统：采用'踩刹车''黄金时光''抢回时间'等患者可感知隐喻，替代ADNI/BioFINDER等技术对比
- 重构风险段落：集中解剖'四年100次输液''前18个月密集监测''ARIA信号识别'，用'这意味着什么'引导
- 强化落点：结尾必须回收'这对你意味着什么'，针对个体处境（基因状态、病程阶段、照护资源）给出决策框架

各维度得分：
- route_alignment: 55 — 路线严重偏离。合同要求RANGE-05/患者选择沟通路线，强调'患者痛感起手+核心获益翻译+风险坦诚+理解引导'的内容组合和'ARCH-04承重+人群分流/选择建议落点'的逻辑组合。系统稿采用学术报告式结构（痛点-数据-亚组-长期价值-选择路径），缺乏情感锚定和叙事张力，未沿'焦虑→数据→理解'的单一主线展开，而是信息罗列式推进。落点虽提及选择，但缺乏'这对你意味着什么'的强回收。
- key_facts: 65 — 核心数据存在但呈现方式错位。48个月延缓数据（9.8-14.2个月）已呈现，但关键事实'72%极早期患者4年认知未变差'完全缺失——这是参考答案的核心亮点和情感锚点。'进展风险降低55%'被替换为'32%'，数据来源表述混乱（ADNI/BioFINDER对比 vs 原始研究）。ApoE分层信息过度技术化，未转化为患者可感知的'不同人获益不同'的通俗解释。
- audience_style: 45 — 严重偏离患者受众要求。大量使用术语（'ApoE ε4非携带者或杂合子''CDR-SB评分''BioFINDER队列''ARIA''OLE'）未做患者语言翻译。语气冷静分析而非'温度建立信任'，缺乏'陪孙子过春节''多喘口气'等生活化锚点。第二人称使用生硬（'您'），缺乏真正共情。风险披露过度技术化（'前18个月MRI密集监测'），未转化为'这意味着什么'的情感理解。
- structure: 60 — 结构完整但不符合公式要求的outline。合同要求5段式结构：[患者痛感锚定]-[核心获益翻译]-[人群差异理解]-[风险与边界]-[选择引导]。系统稿实际为6段，将'人群差异'与'风险'拆分过细，且'患者痛感'段落过短、缺乏问题感建立，'选择引导'段落分散在多处而非强落点。小标题学术化（'亚组人群获益解读'），缺乏'黄金时光''踩刹车'等隐喻张力。
- hallucination_control: 70 — 无明显事实编造，但存在数据选择性呈现和来源混淆。'32%风险降低'与参考答案'55%'差异大，可能源于不同对比基准（ADNI vs 未治疗对照），但未向读者澄清。'100次静脉输注'计算准确（26周/年×4年≈104次，取整合理）。ApoE分层数据与参考文献一致。未出现虚构研究或夸大疗效。

问题回指：
- [formula_contract:content_combo] 内容组合类型错配。合同要求'患者选择沟通型'（痛感起手+获益翻译+风险坦诚+理解引导），系统稿实际为'研究解读型'（背景-方法-结果-讨论-结论）。
- [formula_contract:logic_combo] 逻辑组合主线断裂。合同要求'ARCH-04承重'（从焦虑到数据到理解的单一主线），系统稿为多线程信息模块。
- [formula_contract:effective_content_unit] 有效内容单元4项中3项严重miss。'可感知判断'被技术数据替代，'患者语言解剖'被术语堆砌替代，'解释桥'断裂。
- [formula_contract:effective_outline] 有效大纲5段式结构被改写为6段学术结构，关键段落'人群差异理解'和'风险与边界'错位。
- [orchestration_contract:audience] 受众定位执行失败。合同明确'患者和家属'，系统稿实际受众为医学专业人士或有医学背景的家属。

写作力副表（必须针对性修改低分项）：
- opening_hook: 35 — 公式位miss：未用'患者最常问的问题'建立共情锚点，而是直接抛出技术问题。'医生，这药到底能为我爸争取多少时间'虽有引用，但立即转入'淀粉样蛋白'术语，未沿'焦虑→期待'的情感曲线展开。缺乏'确诊后最害怕的是以后'的普世恐惧锚定。
- transition_flow: 40 — 公式位partial：段间过渡依赖小标题而非叙事流动。从'核心获益'到'亚组人群'的跳转生硬，缺乏'但这里有个重要区分'的引导。'把这一切放回您的处境'虽有回收意图，但前段过度技术化导致情感断裂。未沿'ARCH-04承重'的单一主线，而是信息模块拼接。
- midgame_drive: 45 — 公式位partial：中段信息密度高但断层明显。'72%极早期患者未变差'完全缺失——这是内容组合要求的'可感知判断'核心。'人群差异理解'被技术化呈现（ApoE分层统计），未转化为'别人的14个月不一定是您的'的通俗解释。风险披露分散在'长期治疗价值'和'选择路径'两段，缺乏集中解剖。
- closing_tension: 50 — 公式位partial：有落点意图但张力不足。'最终的选择权在您手中'符合'选择建议落点'，但前段过度技术化削弱了情感回收。'时间本身就是最珍贵的疗效'有金句潜质，但缺乏'不要等到记忆消退才行动'的紧迫感。未形成'这对你意味着什么'的强闭环。
- anchor_fidelity: 40 — 公式位miss严重：有效内容单元4项中，'关于长期获益的可感知判断'被技术数据淹没（9.8-14.2个月未转化为生活场景），'适用人群边界的明确声明'过度技术化，'治疗代价与风险的患者语言解剖'术语过多，'临床数字到这意味着什么的解释桥'断裂。有效逻辑单元中'ARCH-04承重'未贯穿，'人群分流'未通俗化。

公式位审计（miss/partial 的位必须在修稿中补齐）：
- formula_compliance 总分: 45
- [miss] persona: 患者关怀者: 稿中缺乏'站在焦虑与期待中'的温度，语气为客观分析而非共情陪伴。术语密集（'ApoE ε4杂合子''CDR-SB''BioFINDER'），未建立'信任'而是建立'信息权威'。
- [partial] range: RANGE-05/患者选择沟通: 有选择引导段落，但整体结构为学术报告式而非患者沟通式。缺乏'黄金时光''踩刹车'等患者可感知的隐喻系统。
- [partial] write_target: 让患者和家属理解仑卡奈单抗4年数据意味着阿尔茨海默病治疗究竟能抢回多少时间: '9.8-14.2个月'数据已呈现，但未转化为'多陪孙子过春节''自己穿衣吃饭'等生活时间锚点。'抢回'概念未显性化。
- [miss] content_combo: 患者选择沟通型——患者痛感起手 + 核心获益翻译 + 风险坦诚 + 理解引导: '患者痛感'段落过短且立即转入术语；'核心获益'技术化未翻译；'风险坦诚'分散且术语化；'理解引导'缺乏情感回收。整体为信息型而非沟通型。
- [miss] logic_combo: ARCH-04承重 + 人群分流/选择建议落点——先锚定患者关切，沿获益证据链展开，回收到选择理解: 未建立'从焦虑到数据到理解'的单一主线，而是多线程信息罗列。'人群分流'呈现为技术亚组分析，未转化为患者决策语言。
- [miss] effective_content_unit: 一个关于长期获益的可感知判断: '9.8-14.2个月延缓'为技术判断，缺乏'72%患者4年未变差'或'多过一年高质量生活'的可感知锚定。
- [partial] effective_content_unit: 一条关于适用人群边界的明确声明: 有ApoE分层声明，但过度技术化（'非携带者或杂合子''84%入组人群'），未转化为'这药对哪些人更管用'的患者语言。
- [miss] effective_content_unit: 一段关于治疗代价与风险的患者语言解剖: 'ARIA''MRI监测''输液反应'等术语未解剖，'100次静脉输注'有量化但缺乏情感重量（如'四年里每周抽时间去医院'）。
- [miss] effective_content_unit: 一个从临床数字到'这意味着什么'的解释桥: '这意味着什么？'段落存在，但解释内容为阶段对比（轻度vs中度痴呆）而非生活场景（'还能认出家人''还能参与决策'仅一笔带过）。
- [miss] effective_logic_unit: ARCH-04承重贯穿全文——从焦虑到数据到理解的单一主线: 主线断裂为：痛点→数据→亚组→长期价值→选择，缺乏情感曲线的'承重'，各段平行推进而非层层递进。
- [partial] effective_logic_unit: 人群分流/选择建议落点——最终回收到'这对你意味着什么': 有选择引导段落，但'这对你意味着什么'被拆分为多段（患者/家属/边界声明），缺乏单一强落点。
- [miss] effective_outline: [患者痛感锚定] 以患者和家属最常问的问题开场，建立共情锚点: 虽有引用问句，但立即转入'淀粉样蛋白'术语，未建立'最害怕的是以后'的普世恐惧共情。
- [partial] effective_outline: [核心获益翻译] 48个月延缓数据→抢回多少个月→日常能力保留: 数据→延缓月数存在，但'抢回'概念隐性，'日常能力保留'仅一句话（'自己穿衣吃饭'），未展开生活场景。
- [miss] effective_outline: [人群差异理解] 非携带者vs杂合子→不同人获益不同→别套别人的结论: 呈现为'亚组人群获益解读'技术段落，缺乏'别人的15个月不一定是您的'的通俗警示。
- [partial] effective_outline: [风险与边界] 长期治疗要付出什么、有什么局限: 风险信息分散，'付出什么'量化不足（100次输注有但缺乏情感计算），'局限'未显性化（如'不能逆转''纯合子风险更高'）。
- [partial] effective_outline: [选择引导] 这些数据放在你的处境里意味着什么: 有选择引导段落，但'你的处境'被泛化为患者/家属/边界三类，缺乏针对个体决策的强聚焦。



【原材料摘录（缺失事实只能从这里补充）】
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



【当前稿件】
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


【修稿规则】
1. 只修改评分反馈中指出的问题，不要重写全文。
2. 保持原稿的正确部分不变。
3. 缺失事实只能从原材料中补充，不得编造。
4. 修改后必须仍然符合写作合同和公式约束。
5. 写作力副表中低于 70 分的维度必须针对性修改：opening_hook 改开头、transition_flow 改段间衔接、midgame_drive 改中段信息密度和推进感、closing_tension 改收尾、anchor_fidelity 补锚点卡落地点。
6. 公式位审计中 miss 或 partial 的位必须在修稿中补齐或强化，不得跳过。
7. 修完后直接输出全文，不要加解释。
8. 每轮修稿必须逐条对照 L1 语法戒律，凡命中禁用条目的表述必须消除或改写。
9. 修辞积木为可选工具；一旦使用某积木，必须完整实现该积木的全部结构要素，不得只用标题。
10. 过渡短语优先使用 L1 表达库中的推荐项，禁用表达黑名单中的条目一律不得出现在修改后的稿件中。

请直接输出修改后的完整文章正文。

```

#### 第 2 轮修稿任务书（全文）

本轮评分变化：`68` -> `78`；本轮缺项变化：`4` -> `4`；本轮达标：`true`。
```text
你是侠客岛白盒编排器的修稿执行器。以下是当前稿件和评分反馈，请根据反馈修改稿件。

【写作合同】
- 题目：仑卡奈单抗患者向文章
- 受众：患者和家属
- 写作目的：面向患者和家属，用他们能理解的语言翻译仑卡奈单抗48个月临床数据的价值，帮助理解长期治疗获益。

【公式驱动约束（修稿时同样必须遵守）】
- 人格定位：患者关怀者——站在患者和家属的焦虑与期待中，把临床试验数字翻译成“这对我意味着什么”，用温度而非术语建立信任。
- 写作范围：RANGE-05/患者选择沟通
- 写作目标：让患者和家属理解仑卡奈单抗4年数据意味着阿尔茨海默病治疗究竟能抢回多少时间。
- 有效内容单元：
  - 一个关于长期获益的可感知判断
  - 一条关于适用人群边界的明确声明
  - 一段关于治疗代价与风险的患者语言解剖
  - 一个从临床数字到“这意味着什么”的解释桥

【评分反馈（第 2 轮修稿输入）】
- 当前总分：68
- 是否合格：False

阻塞问题：
- 核心数据锚定错误：将'Tau蛋白沉积少的极早期患者72%稳定率'与'ApoE基因型'错误关联，混淆两个独立亚组分析，可能严重误导患者对适用人群的自我判断
- 人群分流维度缺失：完全遗漏Tau蛋白分期这一关键分层标准，与参考答案的科学表述存在实质性偏差

缺失或偏差项：
- Tau蛋白沉积分期作为极早期患者筛选标准
- 72%稳定率与15个月延缓数据的来源区分
- ApoE基因型与疾病分期的独立作用解释
- 参考文献的规范呈现

建议修改动作：
- 重构核心获益段：将'9.8-14.2个月延缓'作为主锚点前置，'72%稳定率'明确标注为'Tau蛋白沉积少的极早期患者'独立结果，与基因型区分并列呈现
- 补充Tau蛋白分期维度：在'人群差异'段增加'Tau蛋白沉积程度'作为疾病早期判断标准，澄清与ApE基因型的独立作用
- 术语患者化：将'ApoE ε4非携带者'译为'不带特定基因变异的人'或类似表述，'CDR-SB'首次出现时附功能解释
- 核对监测强度：确认'前18个月密集MRI'的表述是否有原文支持，或调整为更保守的'定期MRI监测'

各维度得分：
- route_alignment: 75 — 整体沿患者关怀路线推进，从焦虑锚定到数据翻译再到选择引导，主线清晰。但存在关键偏离：将'72%极早期患者'置于核心获益位置，与参考答案的'10-15个月延缓'主锚点错位，导致路线重心偏移。
- key_facts: 65 — 核心数据'9.8-14.2个月延缓'和'55%进展风险降低'准确呈现，但存在严重事实错位：将'72%认知未变差'错误定位为极早期患者（ApoE非携带者/杂合子）的结果，而参考答案明确这是'Tau蛋白沉积少的极早期患者'的独立分析，与基因型无关。混淆了两个不同维度的亚组分析。
- audience_style: 70 — 患者语言运用较好，'踩刹车''多喘一口气'等翻译有效。但存在术语过载：'ApoE ε4非携带者/杂合子/纯合子'未经充分患者化翻译，'CDR-SB评分''ARIA'等缩写直接出现，与'用温度而非术语建立信任'的要求有差距。
- structure: 75 — 五段式结构完整，符合有效大纲框架。但'核心获益'段将两个不同来源的数据（72%稳定率与9.8-14.2个月延缓）混为一谈，造成逻辑跳跃；'人群差异'段对基因型与疾病分期的区分不清，结构承载信息有误。
- hallucination_control: 65 — 未出现完全编造的数据，但存在事实嫁接风险：将'Tau蛋白沉积少的极早期患者72%稳定率'与'ApoE基因型'错误关联，可能误导患者对适用人群的判断。'100次输液'等推算合理，但'前18个月密集MRI'的表述缺乏原文支持。

问题回指：
- [formula_contract] effective_content_unit要求'一个关于长期获益的可感知判断'，但系统稿将亚组特异性结果（72%稳定率）置于主位，替代了主数据（10-15个月延缓），违反content_combo中'核心获益翻译'的优先级
- [formula_contract] effective_outline要求'[人群差异理解]'覆盖非携带者vs杂合子vs纯合子，但系统稿遗漏了参考答案明确的'Tau蛋白沉积'分期维度，导致logic_combo中'人群分流'执行不完整
- [writing_contract] persona承诺'用温度而非术语建立信任'，但正文出现'ApoE ε4非携带者或杂合子''CDR-SB评分''ARIA'等未充分翻译的术语，与audience_style要求的患者语言存在落差

写作力副表（必须针对性修改低分项）：
- opening_hook: 80 — 以诊室常见问题开场，建立共情锚点，符合'患者痛感起手'要求。但'四年过去了'的时间感营造稍弱，未能充分制造'终于等到答案'的期待张力。
- transition_flow: 70 — 段间过渡基本流畅，但'核心获益'到'不同人不同获益'的转折存在逻辑断裂——前者混用两个亚组数据，后者才试图区分，造成读者困惑。'这对你意味着什么'段回收有力。
- midgame_drive: 65 — 中段信息密度不足，关键区分（Tau分期vs基因型）未澄清，反而制造混淆。'风险与边界'段对ARIA的描述符合'患者语言解剖'要求，但'前18个月密集MRI'的监测强度表述可能过度。
- closing_tension: 75 — 收尾落回'选择权在您手中'，符合'选择建议落点'要求。'时间本身就是最珍贵的疗效'升华有力，但'马拉松'隐喻与'踩刹车'核心意象略有冲突。
- anchor_fidelity: 60 — 严重偏离：'一个关于长期获益的可感知判断'被错误锚定为'72%认知未变差'，而非参考答案强调的'10-15个月延缓'；'适用人群边界'因混淆Tau分期与基因型而模糊；'解释桥'存在但搭错了数据关系。

公式位审计（miss/partial 的位必须在修稿中补齐）：
- formula_compliance 总分: 55
- [partial] persona: 患者关怀者: '这是诊室里最常见的问题，也是无数阿尔茨海默病患者家属深夜反复咀嚼的焦虑'体现共情，但术语使用（ApoE ε4、CDR-SB、ARIA）超出患者关怀者的温度承诺。
- [hit] range: RANGE-05/患者选择沟通: 全文围绕患者决策场景展开，从理解数据到权衡代价再到最终选择，符合患者选择沟通范围。
- [partial] write_target: 让患者和家属理解仑卡奈单抗4年数据意味着阿尔茨海默病治疗究竟能抢回多少时间: '9.8到14.2个月的延缓'明确回答，但核心位置被'72%认知未变差'挤占，导致目标达成度受损。
- [hit] content_combo: 患者选择沟通型——患者痛感起手 + 核心获益翻译 + 风险坦诚 + 理解引导: 四要素齐全：诊室问题（痛感）、踩刹车翻译（获益）、ARIA与局限（风险）、最终选择权（引导）。
- [partial] logic_combo: ARCH-04承重 + 人群分流/选择建议落点——先锚定患者关切，沿获益证据链展开，回收到选择理解: ARCH-04框架存在，但'获益证据链'因数据混淆而断裂；人群分流有尝试但分错维度；选择建议落点回收成功。
- [miss] effective_content_unit: 一个关于长期获益的可感知判断: 稿中核心判断为'72%的人四年认知未变差'，但参考答案明确这是极早期（Tau低）亚组结果，非主数据；主数据'10-15个月延缓'被后置弱化。可感知判断锚定错误。
- [partial] effective_content_unit: 一条关于适用人群边界的明确声明: 区分了ApoE基因型，但未澄清'Tau蛋白沉积少的极早期'是独立维度，导致患者可能误解'非携带者=极早期=72%获益'的错误等式。
- [hit] effective_content_unit: 一段关于治疗代价与风险的患者语言解剖: '时间代价''监测代价''风险代价'三段式解剖清晰，'每周抽出的固定时间''家属的陪同负担'等表述符合患者语言。
- [hit] effective_content_unit: 一个从临床数字到'这意味着什么'的解释桥: '还能自己穿衣吃饭''多陪孙子过一个春节'等翻译有效，但桥接的数据基础有误。
- [partial] effective_logic_unit: ARCH-04承重贯穿全文——从焦虑到数据到理解的单一主线: 主线存在，但'数据'环节因72%与15个月的错位而分叉，承重结构受损。
- [hit] effective_logic_unit: 人群分流/选择建议落点——最终回收到'这对你意味着什么': '这对你意味着什么'专段设置，分三种情境讨论，回收到位。
- [hit] effective_outline: [患者痛感锚定]: '医生，这药到底能为我爸争取多少时间？'直接引用患者问题，锚定成功。
- [partial] effective_outline: [核心获益翻译]: 翻译工作完成，但'72%稳定率'与'9.8-14.2个月延缓'两个数据来源混为一谈，翻译对象错误。
- [miss] effective_outline: [人群差异理解]: 仅讨论ApoE基因型，完全遗漏参考答案强调的'Tau蛋白沉积'分期维度，导致人群差异理解不完整。
- [hit] effective_outline: [风险与边界]: ARIA风险、治疗局限、适用阶段等边界清晰陈述。
- [hit] effective_outline: [选择引导]: 三段式情境讨论（早期患者/家属决策/最终选择权）结构完整。



【原材料摘录（缺失事实只能从这里补充）】
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



【当前稿件】
# 仑卡奈单抗四年数据：这对您和家人的生活意味着什么

## 确诊之后，您最害怕的是什么？

"医生，这药到底能为我爸争取多少时间？"

这是诊室里最常见的问题，也是无数阿尔茨海默病患者家属深夜反复咀嚼的焦虑。当家人开始出现重复提问、迷路、算不清账，我们既害怕病情发展的速度，又渴望抓住任何能拖住时间的东西。仑卡奈单抗进入视野时，大家听到的多是"清除脑内淀粉样蛋白"这样的医学概念——但这和"妈妈还能认得出我"之间，隔着一道需要翻译的鸿沟。

四年过去了。第一批接受治疗的患者已经走完48个月的旅程，他们的数据终于能回答那个最朴素的问题：**长期用药，究竟能抢回多少个月的生活？**

## 核心获益：72%的人，四年认知未变差

让我们直接看数字，再把它翻译成您餐桌旁能听懂的话。

在Clarity AD研究及其开放标签延伸期中，针对占绝大多数的患者群体——**72%的极早期患者（ApoE ε4非携带者或杂合子）在四年治疗后，认知功能评分未出现恶化**。这不是延缓，这是**踩住了刹车**。

更完整的图景是：与未治疗的自然病程相比，仑卡奈单抗将**进展至下一阶段痴呆的风险降低了55%**。在CDR-SB评分（衡量认知与日常功能的金标准）上，四年治疗带来了**9.8到14.2个月的延缓**——近一年到一年多的时间。

**这意味着什么？** 阿尔茨海默病像一辆下坡的车，不干预就会越滑越快。仑卡奈单抗不是让车掉头，而是**踩下刹车，让下坡慢下来**。一位早期患者如果不治疗，可能在第36个月就进入中度痴呆；而坚持治疗四年，他有可能在第48个月仍维持在轻度阶段。

多出来的这近一年，是**还能自己穿衣吃饭**的时间，是**还能认出家人、参与家庭决策**的时间，是**多陪孙子过一个春节、多喘一口气**的时间。这不是"治愈"，这是**把"还能自理"的黄金时光实实在在地拉长**。

## 不同人，不同获益：别套别人的结论

但这里有个重要区分——**别人的14个月，不一定是您的**。

在参与研究的患者中，约三成不带特定基因变异（ApoE ε4非携带者），五成多携带一个（杂合子），一成六携带两个（纯合子）。本次四年数据主要适用于**前两类人，即八成的绝大多数**。纯合子患者面临更高的脑部影像异常风险，需要更谨慎的个体化权衡。

**简单理解**：如果您或家人属于那八成，这份"踩刹车"的效果对您有直接参考价值；如果属于纯合子，则需要和医生单独讨论风险收益比。基因背景是疗效和安全性的重要调节器，**不能简单套用"平均数"**。

## 四年治疗，要付出什么？

长期治疗的价值，必须放在代价的天平上称一称。

**时间代价**：四年约100次输液，每次约1小时，加上往返医院——这是**每周抽出的固定时间，是生活节奏的重新安排**。

**监测代价**：前18个月需要密集的MRI检查，之后定期随访。这是**需要坚持的耐心，是家属的陪同负担**。

**风险代价**：最需要警惕的是ARIA——脑部可能出现水肿或微出血，表现为剧烈头痛、视觉模糊、意识混乱。好消息是，**随着时间推移，这些风险并未累积加重**，反而趋于平稳。最常见的副作用是输液反应（寒战、发热），通常可控。

**关键局限**：仑卡奈单抗适用于**早期患者**（轻度认知障碍或轻度痴呆），需确认脑内淀粉样蛋白阳性。它不适用于中重度痴呆，也不能逆转已经发生的损伤。

## 这对你意味着什么？

把这一切放回您的处境：

**如果您正处于早期阶段，正在考虑是否开始或继续**——四年数据支持长期治疗的合理性，但这是一场需要承诺的马拉松。预期是**延缓而非逆转**，目标是**抢回近一年的高质量生活**。

**如果您是家属，正在帮父母做决策**——先确认基因状态，这决定您该参考哪组数据；计算的不只是药费，还有**照护者的精力、往返的时间、监测的耐心**；最坏的打算也要做——如果出现副作用，是否愿意暂停或终止？

**最终的选择权在您手中**。带着这些数据，和您的医生讨论：您的基因背景、您的身体状况、您对生活质量的期待——然后决定，这四年证明的"踩刹车"价值，是否值得您开始或继续这场与时间的赛跑。

对于阿尔茨海默病这种至今无法治愈的疾病，**时间本身就是最珍贵的疗效**。而四年数据告诉我们：**有些时间，是可以抢回来的**。


【修稿规则】
1. 只修改评分反馈中指出的问题，不要重写全文。
2. 保持原稿的正确部分不变。
3. 缺失事实只能从原材料中补充，不得编造。
4. 修改后必须仍然符合写作合同和公式约束。
5. 写作力副表中低于 70 分的维度必须针对性修改：opening_hook 改开头、transition_flow 改段间衔接、midgame_drive 改中段信息密度和推进感、closing_tension 改收尾、anchor_fidelity 补锚点卡落地点。
6. 公式位审计中 miss 或 partial 的位必须在修稿中补齐或强化，不得跳过。
7. 修完后直接输出全文，不要加解释。
8. 每轮修稿必须逐条对照 L1 语法戒律，凡命中禁用条目的表述必须消除或改写。
9. 修辞积木为可选工具；一旦使用某积木，必须完整实现该积木的全部结构要素，不得只用标题。
10. 过渡短语优先使用 L1 表达库中的推荐项，禁用表达黑名单中的条目一律不得出现在修改后的稿件中。

请直接输出修改后的完整文章正文。

```

### 五、最终成稿全文

```text
# 仑卡奈单抗四年数据：这对您和家人的生活意味着什么

## 确诊之后，您最害怕的是什么？

"医生，这药到底能为我爸争取多少时间？"

这是诊室里最常见的问题，也是无数阿尔茨海默病患者家属深夜反复咀嚼的焦虑。当家人开始出现重复提问、迷路、算不清账，我们既害怕病情发展的速度，又渴望抓住任何能拖住时间的东西。仑卡奈单抗进入视野时，大家听到的多是"清除脑内淀粉样蛋白"这样的医学概念——但这和"妈妈还能认得出我"之间，隔着一道需要翻译的鸿沟。

**四年过去了。** 第一批接受治疗的患者已经走完48个月的旅程，他们的数据终于能回答那个最朴素的问题：长期用药，究竟能抢回多少个月的生活？

## 核心获益：近一年到一年多的延缓

让我们直接看数字，再把它翻译成您餐桌旁能听懂的话。

在Clarity AD研究及其开放标签延伸期中，针对占绝大多数的患者群体——**不带特定基因变异的人，或只携带一个变异的人**（约占参与者的八成），四年治疗带来了实实在在的延缓：与未治疗的自然病程相比，仑卡奈单抗将**进展至下一阶段痴呆的风险降低了55%**。在衡量认知与日常功能的临床评分（CDR-SB，医生用来评估患者"能不能自己管账、认路、安排日常"的标准工具）上，四年治疗带来了**9.8到14.2个月的延缓**——近一年到一年多的时间。

**这意味着什么？** 阿尔茨海默病像一辆下坡的车，不干预就会越滑越快。仑卡奈单抗不是让车掉头，而是**踩下刹车，让下坡慢下来**。一位早期患者如果不治疗，可能在第36个月就进入中度痴呆；而坚持治疗四年，他有可能在第48个月仍维持在轻度阶段。

多出来的这近一年，是**还能自己穿衣吃饭**的时间，是**还能认出家人、参与家庭决策**的时间，是**多陪孙子过一个春节、多喘一口气**的时间。这不是"治愈"，这是**把"还能自理"的黄金时光实实在在地拉长**。

**还有一个特别值得关注的发现**：在那些**Tau蛋白沉积较少的极早期患者**中——也就是疾病痕迹更轻的一群人——**72%的人在四年治疗后认知功能评分未出现恶化**。这是另一个维度的希望：越早期干预，越有可能真正"踩住刹车"。

## 不同人，不同获益：两个关键的分水岭

但这里有两个重要区分——**别人的14个月，不一定是您的**。

**第一个分水岭：基因背景。** 在参与研究的患者中，约三成不带特定基因变异，五成多携带一个，一成六携带两个。本次四年数据主要适用于**前两类人，即八成的绝大多数**。携带两个变异的人面临更高的脑部影像异常风险，需要更谨慎的个体化权衡。

**第二个分水岭：疾病分期。** 除了基因，**Tau蛋白沉积程度**是另一个关键指标——它反映疾病在脑内扎根的深度。Tau蛋白沉积少的极早期患者，正是那72%认知稳定的人群所在。简单说：**淀粉样蛋白阳性、Tau蛋白尚少、症状轻微**——这三个条件叠加，最可能从长期治疗中获益。

**简单理解**：基因背景和疾病分期是两个独立的判断维度。不带特定基因变异、且Tau蛋白沉积少的早期患者，面对的是最有利的数据；其他组合需要医生帮您具体分析。**不能简单套用"平均数"**。

## 四年治疗，要付出什么？

长期治疗的价值，必须放在代价的天平上称一称。

**时间代价**：四年约100次输液，每次约1小时，加上往返医院——这是**每周抽出的固定时间，是生活节奏的重新安排**。

**监测代价**：治疗期间需要定期MRI检查，尤其是初期阶段，之后转为规律随访。这是**需要坚持的耐心，是家属的陪同负担**。

**风险代价**：最需要警惕的是ARIA（淀粉样蛋白相关影像异常）——脑部可能出现水肿或微出血，表现为剧烈头痛、视觉模糊、意识混乱。好消息是，**随着时间推移，这些风险并未累积加重**，反而趋于平稳。最常见的副作用是输液反应（寒战、发热），通常可控。

**关键局限**：仑卡奈单抗适用于**早期患者**（轻度认知障碍或轻度痴呆），需确认脑内淀粉样蛋白阳性。它不适用于中重度痴呆，也不能逆转已经发生的损伤。

## 这对你意味着什么？

把这一切放回您的处境：

**如果您正处于早期阶段，正在考虑是否开始或继续**——四年数据支持长期治疗的合理性，但这是一场需要承诺的跋涉。预期是**延缓而非逆转**，目标是**抢回近一年的高质量生活**；如果Tau蛋白沉积尚少，您面对的可能不只是延缓，而是**真正稳住现状的机会**。

**如果您是家属，正在帮父母做决策**——先确认两个关键信息：基因状态，以及Tau蛋白分期。这决定您该参考哪组数据；计算的不只是药费，还有**照护者的精力、往返的时间、监测的耐心**；最坏的打算也要做——如果出现副作用，是否愿意暂停或终止？

**最终的选择权在您手中**。带着这些数据，和您的医生讨论：您的基因背景、您的疾病分期、您的身体状况、您对生活质量的期待——然后决定，这四年证明的"踩刹车"价值，是否值得您开始或继续这场与时间的赛跑。

对于阿尔茨海默病这种至今无法治愈的疾病，**时间本身就是最珍贵的疗效**。而四年数据告诉我们：**有些时间，是可以抢回来的**。

```

### 六、最终审核意见与剩余缺口

1. 最终总分与判定：`78`；`qualified=true`。
2. 最终 blocker：无
3. 最终剩余缺项：2026年ADPD国际大会来源锚点缺失；APOE非携带者/杂合子的明确术语表述缺失（改用描述性语言）；风险段位置与content_combo要求的嵌入节奏不一致；选择引导落点偏理性决策，情感回收不足
4. 最终下一刀：开篇压缩医学背景，将'淀粉样蛋白'等术语后移至核心获益段，强化'深夜反复咀嚼的焦虑'等情感锚定；将风险段前置，与核心获益交织呈现，实现'坦诚'而非'告知'的效果；明确使用'APOE非携带者''杂合子'术语并附患者化解释，提升精确性；结尾强化情感回收，补充'不要等到...才行动'式的主动建议，或'这四年，值得'式的情感落点；补充'2026年ADPD国际大会'来源锚点，增强可信度

## 工程附录

### Runtime 指针

1. `revise_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise_manifest.json`
2. `score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\score.json`
3. `review_bundle.json`（基线口径，未自动刷新）：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\review_bundle.json`
4. `最终轮 score.json`（当前最终缺口口径）：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_2\score.json`
5. `writing_user_prompt.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\writing_user_prompt.txt`
6. `generated.txt`（基线稿）：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\generated.txt`
7. `round_1\revise_prompt.md`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_1\revise_prompt.md`
8. `round_1\revised_draft.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_1\revised_draft.txt`
9. `round_1\score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_1\score.json`
10. `round_2\revise_prompt.md`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_2\revise_prompt.md`
11. `round_2\revised_draft.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_2\revised_draft.txt`
12. `round_2\score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_2\score.json`

### 证据摘要

1. 已直接核对：`D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise_manifest.json` 中轮次轨迹为 `第 1 轮：58 -> 68；qualified=false；缺项 6 -> 4；第 2 轮：68 -> 78；qualified=true；缺项 4 -> 4`，最终 `weighted_total=78`、`qualified=True`。
2. 已直接核对：最终轮 `score.json` 为 `D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore\lecanemab_patient\revise\round_2\score.json`，当前剩余缺项为 `2026年ADPD国际大会来源锚点缺失；APOE非携带者/杂合子的明确术语表述缺失（改用描述性语言）；风险段位置与content_combo要求的嵌入节奏不一致；选择引导落点偏理性决策，情感回收不足`；根目录 `review_bundle.json` 仍停在基线口径。
3. 已直接核对：每轮 `revise_prompt.md` 与最终 `revised_draft.txt` 已落盘，人工可直接顺着“基线稿 -> 修稿任务书 -> 最终稿”复盘 loop 过程。
