# lecanemab_patient 模型对照全貌

状态：已完成  
日期：2026-04-12  
用途：人工直接比较 `k2.5` 与 `deepseek-reasoner` 在 `patient` 题上的起稿、整稿返修、整稿后局部返修表现。主阅读层直接贴材料、共用 draft prompt 和两边当前最强候选稿，不再只给结果摘要。

## 当前有效口径

1. 本页只认同轮 runtime：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek`。
2. 本页只认固定 scorer 下的 `score.json / local_revise_manifest.json / draft_manifest.json / whitebox_contract.json / draft_prompt.md`。
3. 当前这题的结论不是“换总模型”，而是：`deepseek-reasoner` 首稿硬层更强，`k2.5` 在 `whole revise` 后软层更强。
4. 本页不再假装存在 compat `materials_full.json / writing_system_prompt.txt / writing_user_prompt.txt`；本轮模型对照实际真相源是 `materials/materials_digest.md + whitebox_contract.json + draft_prompt.md`。

case_id: `lecanemab_patient`
run_dir: `D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek`

## 当前明确缺项

1. 独立 planning prompt：本轮不存在；原因：模型对照 harness 只保留白盒合同与起稿 prompt，不单独导出 planning prompt。
2. compat `materials_full.json`：本轮不存在；原因：模型对照 harness 真实材料口径落在 `materials/materials_digest.md` 与 `draft_prompt.md`。
3. compat `writing_system_prompt.txt / writing_user_prompt.txt`：本轮不存在；原因：模型对照 harness 使用单份 `draft_prompt.md` 承载实际起稿 prompt。

## 主阅读层

### 一、人工审核先看

1. 写作合同：写给患者和家属，核心任务是把 48 个月仑卡奈单抗数据翻译成“究竟抢回多少时间、代价是什么、哪些人更适合”。
2. 当前判定：`deepseek-reasoner` 在首稿更容易把合同关键位先打中；但进入 `whole revise` 后，`k2.5` 的患者沟通感、叙事推进和自然度更强。
3. 审稿优先看：两边 strongest 版本在“关键事实命中”已经打平，真正差异落在患者语言、段落气口、收束张力和 soft editorial 判语。
4. 当前最该改：不是先切全链总模型，而是把 `patient` 场景拆成更明确的模块角色，再测“首稿模型”和“整稿返修模型”是否应分流。

### 二、本轮真正喂给写手的材料（人工整理版）

人工阅读提示：
1. 本题只有 1 份原始 PDF poster 材料，白盒取材并不复杂，真正难点在于如何把临床 poster 翻译成患者沟通稿。
2. 当前白盒合同已经明确要写：48 个月、15 个月黄金时光、72% 极早期患者稳定、55% 进展风险降低、ApoE 分层、长期输液与 ARIA 风险。
3. 当前主风险不在“材料太脏”，而在“如何把同一份事实包翻成更有温度、更像成熟患者稿的成文”。

实际入模材料整理稿：
~~~text
# 白盒取材摘要

- 题目: lecanemab_patient / 仑卡奈单抗患者向文章
- 状态: ready
- 总材料项: 1
- 可抽取文本项: 1

- [ok] D:\汇度编辑部1\项目文章\侠客岛测试任务\仑卡奈单抗患者向文章\inputs\Froelich_48M Noncarriers and Heterozyg_ADPD26 FINAL.pdf
~~~

补充可读整理：
1. 材料主轴只有一页 poster，核心事实非常集中：`48 months / 1,521 / 9.8 and 14.2 months / 55% / adverse event rates were lower or stabilized each additional year`。
2. 白盒合同要求把这些数字翻成患者可感知收益，而不是写成会议摘要。
3. 当前 compare 实验的关键，不是再找新材料，而是看不同模型在同一事实包上如何成稿。

### 三、本轮给模型的 prompt 全文（两模型共用起稿 prompt）

说明：`k2.5` 与 `deepseek-reasoner` 在 base 阶段共用同一份 `draft_prompt.md`；差异只在 writer profile 的模型配置，不在 prompt 文案本身。

~~~text
【模块角色上下文】
你当前承担的是首稿生成节点。先忠实执行写作合同、样稿母本边界和题目主线，再追求中文表现力。允许把稿件写顺、写稳、写成人类编辑会交付的成熟文本，但不得为追求观感擅自改题、偷换证据边界、补不存在的事实。

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
~~~

### 四、当前稿件全文

#### A. `k2.5` 当前最强版（`whole revise`，hard `78` / soft `82`）

~~~text
当家人被确诊为早期阿尔茨海默病，最常被问到的问题往往是："治疗到底能争取多少时间？"这不是一个关于百分比或统计显著性的学术问题，而是一个关于日常生活、关于还能自己系鞋带多久、关于还能认出孙辈面孔多久的切身之问。这种对未来的不确定，往往比疾病本身更令人窒息。2026年ADPD大会上，仑卡奈单抗48个月随访数据新鲜出炉——对于最可能获益的人群，四年治疗意味着认知衰退被推迟近一年，超过七成患者功能保持稳定，疾病进展的风险被砍掉一半以上。

**约15个月的"黄金时光"：从数字到日子**

在ApoE ε4非携带者或杂合子人群中——这占了Clarity AD随机化患者的84%（31%为非携带者，53%为杂合子，共1,521人纳入分析）——仑卡奈单抗治疗至48个月时展现出明确的延缓效应。

与ADNI自然病史队列相比，患者的临床衰退进程被推迟了9.8个月；若与另一项独立研究BioFINDER队列比较，这一数字达到14.2个月。取这两个独立来源的中间值，约为15个月——这就是四年治疗可能为你争取的"黄金时光"。接受每两周10 mg/kg静脉输注治疗的患者，在四年结束时，认知和功能状态相当于未治疗人群提前近一年时的水平。

这段时间可能意味着什么？也许是多陪孙子过一个春节，也许是多维持一年自主管理财务的能力，也许是多保留一季参与家庭决策的清醒，也许是让照护者能多喘一口气。

**七成患者稳住不动：疾病进展的刹车效应**

更关键的数字藏在疾病阶段进展中。在认知功能评估得分较低、处于极早期的患者里，72%的人在四年治疗期间认知功能保持稳定，未出现临床意义上的恶化。这里的"认知功能评估"（医生称之为CDR-SB评分）衡量的是日常生活能力——能否自己穿衣、能否记住约会、能否处理简单财务，这些你每天都在做的事。

同时，仑卡奈单抗将患者进入下一阿尔茨海默病阶段（中度或重度痴呆）的风险降低了55%（相比ADNI自然病史队列）。对于早期患者而言，这55%不是抽象数字，而是"还能维持轻度阶段多久"的具体概率——延缓进入需要全天候照护的阶段，意味着家庭结构、经济安排和情感准备都能获得更充裕的调整期。

**不是所有人都一样：你的基因型决定获益边界**

必须坦诚的是，这份四年数据并非适用于所有患者。上述约15个月延缓、72%稳定比例、55%风险降低，明确限定于ApoE ε4非携带者或杂合子人群——即不携带风险基因者，或仅携带一个风险基因者。ApoE ε4纯合子患者（携带两个风险基因）未被纳入此次48个月分析，其长期获益边界需要更多研究确认。

这一区分至关重要。如果你或家人属于ApoE ε4杂合子——即携带一个风险基因——现有证据支持四年治疗可带来上述时间获益；若不携带风险基因，同样适用。但若携带两个风险基因，当前数据尚不足以给出同等确定性的预期。临床决策时，务必与医生确认基因型分层信息，避免将他人的结论套用于自身处境。

**长期治疗的代价与真实边界**

四年的治疗意味着什么？首先是时间投入：每两周一次的静脉输注，需要持续前往输注中心。其次是安全性考量：淀粉样蛋白相关影像异常（ARIA）仍是需要警惕的不良事件——简单说，就是脑部影像检查可能出现暂时性异常信号，多数患者并无症状，医生会通过定期监测来管理。值得注意的是，随着治疗年限延长，ARIA发生率呈现逐年下降或保持稳定的趋势，长期安全性轮廓优于早期预期。超过280名患者完成了四年治疗，这一样本量为长期安全性评估提供了扎实基础。

然而局限同样存在。仑卡奈单抗针对的是极早期患者，即大脑中Tau蛋白沉积尚处于低水平的阶段（医生常以此判断疾病早期程度），已进入中度痴呆阶段者不在适应症范围内。治疗不能逆转已发生的损伤，只能延缓后续衰退。四年数据证实的是"踩刹车"而非"治愈"，患者仍会经历疾病进展，只是速度更慢。

**和医生聊的时候，不妨直接问这三个问题**

回到最初的问题：治疗能争取多少时间？对于ApoE ε4非携带者或杂合子的早期患者，四年数据给出的可感知判断是——大约15个月的额外窗口期，以及超过七成的概率让认知状态稳住不动。

这不是承诺，而是概率。55%的进展风险降低意味着统计学上的优势，而非个体确定性。但相较于自然病程的被动等待，主动治疗提供了可量化的时间筹码。

不要等到记忆消退之后才行动。和医生讨论时，不妨直接问这三个问题：我的基因型是否匹配现有证据？本地输注中心能否支持两年一周期的长期计划？这15个月对我个人生活目标的实际价值是什么？

数据已经给出了方向，但时钟在你手里——时间既是阿尔茨海默病最大的敌人，也可以成为治疗最诚实的盟友。
~~~

#### B. `deepseek-reasoner` 当前最强版（`whole revise`，hard `78` / soft `76`）

~~~text
**“他还能记住我多久？”——4年数据出炉：仑卡奈单抗为部分患者“抢”回近15个月黄金时光**

当我们面对阿尔茨海默病，心中最常盘旋的，或许正是这个简单到令人心碎的问题：**“他还能记住我多久？”** 治疗，究竟能为所爱的人，**抢回多少清醒的、有质量的时光？** 是几个月，还是几年？这些时间，又能让我们留住多少顿一起吃的饭，多少次认得出家人的微笑？这份对时间流逝的恐惧与对留住记忆的渴望，是每个家庭最真实的起点。

今天，我们基于一项名为 **Clarity AD** 研究的长期随访数据，尝试回答这个问题。这项研究探索了药物**仑卡奈单抗**（Lecanemab）在为期 **48个月**（4年）的治疗中，能为早期阿尔茨海默病患者带来什么。

**一、 核心数据翻译：48个月，意味着“抢”回近一年到一年多的时间**

临床试验用专业量表衡量病情衰退的速度。根据 **Clarity AD** 研究的长期数据*，在治疗48个月时，研究者做了一个关键换算：与未接受此类治疗的疾病自然发展的速度相比，仑卡奈单抗治疗平均为患者**节省了9.8个月至14.2个月**的疾病进展时间。

**这“意味着什么”？**
这意味着，如果疾病自然发展会在未来一年内让患者的认知和日常功能下降一个明显的台阶，那么治疗可能将这一步**推迟了近一年甚至更久**。这“抢”回来的时间，可能是多记住一年孙辈的名字，可能是多完成一年熟悉的家务，也可能是多参与一年家庭的重要决策——这些，都是生活质量的核心。

**在这里，我们必须引入一个关键理解：这些具体数据，主要来自“ApoE ε4基因非携带者”（您可以理解为遗传风险相对较低的人群）。** 对于同样适用此药的“杂合子携带者”（带有一个风险基因拷贝），治疗同样能延缓疾病，但获益的幅度可能有所不同。**这意味着，理解数据的第一步，是别轻易套用别人的结论，而是要看清它最初来源于哪部分人群。**

**二、 更深层的保护：大幅降低进展风险，甚至长期稳住病情**

除了“节省时间”，延缓进入更严重疾病阶段（如从轻度进展到中度）更为关键。

1.  **风险降低超一半**：对于上述人群，与自然病程相比，仑卡奈单抗治疗将**进展到下一疾病阶段的风险降低了55%**。这是一个非常显著的降低幅度。
2.  **一个格外令人振奋的发现**：在疾病程度**极早期**就开始治疗的患者中，经过4年治疗，高达**72%** 的人病情依然保持在“轻度”或更早的阶段。这意味着，**每10位极早期坚持治疗的患者中，约有7位能长期稳住病情**。早期干预，为延长宝贵的稳定期带来了更大的可能性。

**三、 长期治疗的代价与风险：一份持续四年的“答卷”**

选择长期治疗，意味着同时接受其伴随的代价与风险。我们需要用患者的语言来理解它们：

1.  **治疗本身是长期承诺**：仑卡奈单抗的标准给药方式是**每两周一次静脉输注**。这代表着至少每月两次去医院，是对患者和家属时间、精力的长期考验。
2.  **需要关注的安全性话题**：治疗中，医生会通过脑部核磁共振（MRI）监测一种可能的风险，即 **“ARIA”**（您可以将其理解为**大脑扫描图片上可能出现的一些暂时性变化，大多数人感觉不到，但需要医生密切留意**）。长期数据给出了一个积极的趋势：**在超过280名坚持治疗4年的患者中，观察到随着治疗时间延长，这类影像变化的发生率呈现减少或保持稳定的态势**。这表明，长期治疗的总体耐受性良好。
3.  **局限性**：数据虽覆盖48个月，展现了清晰的长期获益趋势，但阿尔茨海默病是更为漫长的旅程。**更长期的数据仍在积累中**。治疗的目标是“延缓”与“稳住”，这是在怀抱希望时需要理性锚定的认知。

**四、 放在您的处境里：现在该怎么做？**

面对这些数字，最终的问题总是：“所以，对我（或我的家人）来说，该怎么选？”

这串问题没有标准答案，但清晰的思路可以帮助您：
- **首先，明确自身位置**：与医生确认您或家人的 **ApoE ε4 基因状态**（如果已知）。这是判断上述长期数据参考价值大小的关键一步，特别是区分您属于“非携带者”还是“杂合子”，因为获益的参照系可能不同。
- **如果您的基因型符合本次分析的人群**，那么48个月的数据为您描绘了一幅**长期获益的参考画面**：治疗不仅有潜力赢得近一年或更长的宝贵时间，更能大幅降低病情进展的风险，甚至为长期稳定创造显著机会。
- **无论基因型如何**，您都需要与医生一起权衡：**为争取这样的时间和稳定性，您和家人是否愿意且能够承担每两周一次输液的长期安排**，并共同管理相关的随访监测。
- **最终，选择在于价值排序**：如果您最珍视的是在疾病早期阶段尽可能延长独立、有质量的生活，那么这些延缓与稳定的数据就格外有分量。

**总结而言，仑卡奈单抗48个月的数据，为我们传递了一个核心信息：对于相当一部分患者，早期开始并坚持长期规范治疗，不仅有机会夺回以“月”计的重要时光，更能显著降低进展风险，为长期稳定病情提供坚实可能。** 请记住，**不要等到记忆消退之后才行动——时间是最大的敌人，也是坚持治疗最好的盟友。** 请带着这些信息，与您的主治医生进行一场深入的、关于“时间、风险与代价”的对话，找到最适合您家庭的那条路。

---
*注：本文提及的48个月数据，来源于Clarity AD研究的开放标签扩展阶段，并与ADNI、BioFINDER等研究中的自然进展历史数据进行了对比分析，主要针对ApoE ε4基因非携带者及杂合子携带者人群。
~~~

### 五、当前审核意见与返修抓手

1. 总分与当前判定：
   - `k2.5 base -> whole -> whole+local`：`68 / false -> 78 / true -> 78 / true`
   - `deepseek-reasoner base -> whole -> whole+local`：`72 / true -> 78 / true -> 78 / true`
2. 各维度关键失分：
   - `deepseek-reasoner` 的 hard layer 首稿更强，说明它更容易首轮打中关键事实与合同位。
   - `k2.5` 的 `whole revise` soft layer 更强，说明它在患者沟通感、自然度、叙事推进上更像成熟患者稿。
   - 两边 local 都是高精度执行，但都没有继续提硬分，说明 local 在这题更像精准补丁器，不是继续冲分器。
3. 返修抓手：
   - 如果追首稿通过率：继续拿 `deepseek-reasoner` 做候选首稿模型。
   - 如果追整稿交付感：`k2.5` 的 `whole revise` 当前更优。
   - 下一轮不应只比总分，应拆成 `draft` / `whole revise` 两个 profile 单独比。
4. 人工审核时重点对照项：
   - 看哪一版更像“患者关怀者”，不是更像学术 poster 口吻。
   - 看结尾是“真正回收到患者选择”还是“只把数字再说一遍”。
   - 看风险段是患者语言还是术语堆积。

## 工程附录

### Runtime 指针

1. `k2.5` 运行目录：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_041831_109_lecanemab_patient`
2. `deepseek-reasoner` 运行目录：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_043335_715_lecanemab_patient`
3. `k2.5 base draft_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_041831_109_lecanemab_patient\compare_snapshots\base\draft_manifest.json`
4. `deepseek base draft_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_043335_715_lecanemab_patient\compare_snapshots\base\draft_manifest.json`
5. `k2.5 whole score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_041831_109_lecanemab_patient\compare_snapshots\whole\score.json`
6. `deepseek whole score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_043335_715_lecanemab_patient\compare_snapshots\whole\score.json`
7. `k2.5 local_revise_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_041831_109_lecanemab_patient\local_revise_manifest.json`
8. `deepseek local_revise_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_043335_715_lecanemab_patient\local_revise_manifest.json`
9. 总汇总：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\model_compare_summary.json`

### 本轮关键证据

1. 泄题边界：两边 base draft manifest 均直接显示 `reference_answer_visible_before_draft=false`、`reference_sample_enabled_for_draft=false`。
2. 三阶段结果：`model_compare_summary.json` 直接记录 `patient` 的两组对照：`k2.5 68→78→78`，`deepseek 72→78→78`。
3. 整稿观感差异：`whole score.json` 直接给出 `editorial_total 82 vs 76`，差异不在 `qualified`，而在编辑观感层。
4. 局部返修：两边 `local_revise_manifest.json` 都显示 `execution_precision_rate=1.0` 且 `score_after` 不再上涨。

### 评分结果

1. `k2.5 whole revise`：
   - 总分：`78`
   - 达标结论：`true`
   - 软层：`editorial_total = 82`
2. `deepseek-reasoner whole revise`：
   - 总分：`78`
   - 达标结论：`true`
   - 软层：`editorial_total = 76`
3. local 执行：
   - `k2.5 local`：`precision=1`，`issue_close=1`，`78 -> 78`
   - `deepseek local`：`precision=1`，`issue_close=1`，`78 -> 78`

### 本轮真实 blocker

1. 这题当前 blocker 已不是“谁能把题写过”，而是“首稿 profile 和整稿返修 profile 是否应拆模”。
2. 当前 scorer 已能区分 `patient` 题上的 hard / editorial 差异，但还不能替代人工对“哪版更像成熟患者稿”的最终裁定。

### 证据摘要

1. 已直接核对 `draft_prompt.md`、`whitebox_contract.json`、两边 strongest `whole/draft.txt`，确认这份全貌贴的是实际起稿合同与实际 strongest 成稿，不是结果转述。
2. 已直接核对两边 `whole score.json`，确认当前有效结论是：hard 打平，soft `k2.5` 更强。
3. 已直接核对两边 `local_revise_manifest.json`，确认 local 在本题上是“改得准但不继续涨分”的执行层。
