# 历史单题全貌档案：lecanemab_mechanism

状态：2026-04-11 本轮三题 retest / 历史封存，非当前活状态真相源  
日期：2026-04-11  
用途：历史单题全貌档案的人工审核第一读物。先用主阅读层回放当时机制主线、补充资料噪声和当时质检死点，再用工程附录回查历史 runtime。  

case_id: `lecanemab_mechanism`
task_id: `fc482d8b-c02d-4e1f-9303-8eb8cc6088a3`
run_dir: `侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest`

## 历史封存口径

1. 本档只认 2026-04-11 本轮三题 retest 的同轮 runtime 直证，不回收旧 run 或旧聊天结论。
2. 主阅读层已经直接贴出材料整理稿、prompt 全文、当时稿件全文和返修抓手；人工审稿先看这里，不先点路径。
3. 本轮不存在的独立 planning / quality prompt 已明确写缺项；若 `score.json/summary.json` 未生成，也必须在本档中直接写明原因。

## 历史明确缺项

1. 独立 planning prompt：本轮不存在；原因：当时 standard_chain 只在 `stage_artifacts` 与 `review_bundle.planning` 留存 planning 结果，不单独导出 planning prompt 文件。
2. 独立 quality prompt：本轮不存在；原因：当时 quality 只落门禁结果与错误说明，不导出可回读 prompt 文件。
3. `score.json / summary.json`：本轮未生成；原因：`task_status=failed`、`halted_at=quality`，且 runner 在失败态后处理时报 `Count` 异常。

## 主阅读层

### 一、人工审核先看

1. 写作合同：面向 `对医学感兴趣的普通读者`；目标字数 `2500`；题眼是“关键获益是否真的足以改写决策！Approved dosing regimen。写作主轴采用监管里程碑叙事，围绕疗效分析、Mechanism证据展开，面向对医学感兴趣的普通读者完成新闻_评论型论证。”。
2. 当时判定：本轮未进入 `delivery/score`；`quality` 因 `inference_clean` 门禁失败，错误为“检测到推理泄露标记（<think> 或内部推理句式），阻断交付”。
3. 审稿优先看：先看标题、导语和机制段第一屏，确认正文是不是在解释 Fc-microglia-SPP1 机制链，而不是夹带内部推理痕迹或写成论文摘要。
4. 当时最该改：先清除任何触发“推理泄露”的句式和元叙事痕迹，再判断机制段是否还保留读者可读性。
5. 为什么会写歪：这题正式结构化 mechanism 事实只有 2 条，其余 27 条是 Nature Neuroscience 页级补充碎片；prompt 很长，写手容易把阅读过程、实验设计和解释层叠在一起。

### 二、本轮真正喂给写手的材料（人工整理版）

人工阅读提示：
1. 这题真正喂料很脏：结构化主干只有剂量和靶点两条，主要信息来自上传论文的页级碎片。
2. 人工审核先抓 4 个机制锚点：原纤维靶点、Fc 依赖的小胶质细胞参与、phagosome/lysosome 程序、SPP1/osteopontin。

实际入模材料整理稿：
```text
【写手前置合同】
- 题眼 / thesis: 关键获益是否真的足以改写决策！Approved dosing regimen。写作主轴采用监管里程碑叙事，围绕疗效分析、Mechanism证据展开，面向对医学感兴趣的普通读者完成新闻_评论型论证。
- 目标读者: 对医学感兴趣的普通读者
- 结构大纲: 引言 -> Mechanism -> 疗效分析 -> 结论
- 目标字数: 2500

【结构化主干事实】
- 获批用法用量: 10 mg/kg IV q2w
- 分子靶点：可溶性Aβ原纤维: Anti-Aβ protofibril antibody

【补充材料 / OCR 主干】
- Nature Neuroscience 论文主结论：Lecanemab 依赖小胶质细胞效应功能清除 Aβ，而不是单靠抗体黏住斑块。
- Fc-silenced 的 LALA-PG 版本可以结合斑块，但不能被 microglia 正常摄取，也不能产生同样的清除效果。
- 空间转录组和单细胞结果共同指向 phagosome/lysosome、抗原呈递和 SPP1 上调。
- OPN / SPP1 被诱导后可促进 Aβ clearance，是本题最值得保留的机制亮点。
```

### 三、本轮给模型的 prompt 全文

system prompt：
```text
你是侠客岛写作系统的医学编辑。
【核心铁律】只使用本次下发证据中明确出现的数据、数字和结论。严禁从训练知识或外部来源补充任何统计数据、样本量、百分比或年份。严禁编造'中国数据''真实世界验证''获批信息''市场预测'等证据外内容。如果证据中未提供某个具体数字，用定性描述替代（如「研究显示」「数据表明」），绝不编造具体数值。违反此条即为幻觉，将导致 hallucination_control 维度直接不及格。

写作策略: M3_PLAY_证据缺口
叙事弧线: ARC_MED_001
目标受众: 对医学感兴趣的普通读者
目标篇幅: 2500 字（允许浮动 ±10%，结构须与篇幅匹配，证据不足时收缩结构而非泛化扩写）

【受众写作风格 — 科普/普通读者】
- 专业概念必须用通俗比喻和类比解释
- 避免堆砌实验数据和统计指标，只保留最有说服力的核心数据
- 用讲故事的方式组织信息：先提出读者关心的问题，再逐步揭示答案
- 标题应有吸引力和可读性，如使用「揭秘」「原来」等引导词
- 文风活泼但不失准确，可用感叹号和省略号增加节奏感

风格要求:
- 语体等级: R3
- 正式程度: semi_formal
- Register 资产: Professional Education / 专业教育稿
- Register 语气: 兼顾专业性与可读性，可适度使用类比
- Play 说明: 先界定指南与实践中的循证空白（如{特定疾病分期}系统治疗时机不清、{特定治疗线序}后证据脱节），再用新研究的入组人群、分层模型与给药顺序重构决策路径，把"可做"转化为"何时做、给谁做"。
- Arc 说明: 通用的临床试验结果解读叙事结构
- Arc 结构: 背景 → 试验设计 → 主要结果 → 临床意义
- 论点派生规则: 监管里程碑叙事
- 论点模式: 以监管审批事件（获批/被拒/大反转）为时间锚点，解读背后的科学与政策逻辑。

L1 正式资产约束:
- Register 定义: 专业但可读
- 执行口径: 全部13条强制执行

L1 人格内核:
- Persona: Macro Strategist
- 人格说明: 战略家——看全局博弈，不看单点得失
- 语气DNA: strategic, comparative, second-order
- 注意力顺序: positioning versus established alternatives；portfolio as strategic asset；expansion pathway and optionality
- 默认怀疑: Narrative is optimized for signaling rather than substance；Short-term wins may trade off long-term resilience
- 偏好证据: competitive landscapes, trend data, scenario models
- 表达倾向参考: What game is being played；asset logic versus narrative logic；positioning only works if adoption follows（只转译倾向，不直接照抄原句）
L1 表达禁区: 重磅、激动人心、颠覆性、划时代、终于、逆袭

L1 语法戒律:
- 优先使用「动作→对象→结果」的句式，减少抽象名词作主语。简单关系直接用「是/有」，禁止用「作为/代表/充当/标志着」替代系动词。
- 连续「的」字嵌套不超过2层。超过2层时必须拆分为独立短句。
- 少用「被/被认为/被视为/被解读为」，改为明确主体的主动句式。
- 长短句交替使用，禁止连续三句长度相同。两项并列优于三项。段落结尾方式必须变化，不可每段都以总结句收束。
- 所有数字、百分比、统计值必须使用阿拉伯数字和国际符号。禁止写「百分之二十七」，必须写「27%」。
- 专业术语在全文中保持统一称谓，不做同义词替换。首次出现时可加括号注释。

L4 产品变量锚点:
- VAR_TARGET_PATHWAY
- VAR_EFFICACY_NUM
- VAR_SAFETY_RISK
- VAR_BIOMARKER_CHANGES

L4 产品关注点（仅在当时证据支持时使用）:
- 必须强调对『原纤维/寡聚体』的清除，不可仅提斑块。；只能作为关注点，不能替代当时证据，也不能倒推出未下发的数字或结论。
- 凡提Clarity AD，如当时证据明确支持，可优先说明ADAS-cog14或CDR-SB的准确百分比数据。；只能作为关注点，不能替代当时证据，也不能倒推出未下发的数字或结论。
- 提及ARIA风险时，必须同时提及MRI监测频率建议和大多数为无症状的定性描述。；只能作为关注点，不能替代当时证据，也不能倒推出未下发的数字或结论。
产品级禁用表达: 逆袭、完胜、碾压、吊打、王者

L4 产品表达方向:
- specialist: 已配置开篇方向 / 数据表达方向 / 安全性表达方向 / 收束方向 / 解释性类比；只可借鉴表达方向，不得照抄资产示例句。
- patient_education: 已配置开篇方向 / 数据表达方向 / 安全性表达方向 / 收束方向 / 解释性类比；只可借鉴表达方向，不得照抄资产示例句。
- primary_care: 已配置开篇方向 / 数据表达方向 / 安全性表达方向 / 收束方向；只可借鉴表达方向，不得照抄资产示例句。

L1 论证逻辑规则 (M1):
- 写作前必须先明确整篇文章想表达的核心内容。论证型文章还应在此基础上进一步收束为要让读者接受的核心判断。
- 多组证据的组织方式，先看证据之间的内在逻辑关系，不能机械平推，也不能机械套同一种结构。并列关系可先形成局部判断再汇总，递进关系则应按认知推进顺序展开。
- 背景与概念只保留后文论证真正会用到的部分。删去后不影响后文成立的铺垫，应移除。
- 陌生概念第一次出现时，必须先让读者知道“这是什么”。至于后续接“这意味着什么”“它是干什么用的”还是暂不展开，应按后文需要决定。

L1 风格灯塔:
- 风格定位: 以冷峻理性的数据和逻辑分析为底色，配合武侠世界的隐喻体系，将复杂的医药投资与政策问题还原为常识性判断，兼具专业深度与通俗张力。
```

user prompt：
```text
主题: 关键获益是否真的足以改写决策！Approved dosing regimen。写作主轴采用监管里程碑叙事，围绕疗效分析、Mechanism证据展开，面向对医学感兴趣的普通读者完成新闻_评论型论证。

大纲:
1. 引言
2. Mechanism
3. 疗效分析
4. 结论

【必须覆盖的关键事实与数字】
下列事实必须全部进入正文；可以转译表达，但不得改数字、时间点、适用人群，也不得把不同时间点混写。
- 必写1: 第1页主要是论文标题、作者和机构信息。；原始数字 Nature Neuroscience
nature neuroscience
https://doi.org/10.1038/s41593-025-02125-8
Article
The Alzheimer’s therapeutic Lecanemab 
attenuates Aβ pathology by inducing an 
amyloid-clearing program in microglia
 
Giulia Albertini 
  1,2,9 
, Magdalena Zielonka 
  1,2,9, Marie-Lynn Cuypers 
  3, 
An Snellinx1,2, Ciana Xu 
  1,2, Suresh Poovathingal1,4, Marta Wojno 
  1,4, 
Kristofer Davie 
  1,4, Veerle van Lieshout 
  1,2, Katleen Craessaerts1,2, 
Leen Wolfs1,2, Emanuela Pasciuto1,2,5,6, Tom Jaspers 
  3, Katrien Horré1,2, 
Lurgarde Serneels1,2, Mark Fiers1,2,7,8, Maarten Dewilde 
  3 & 
Bart De Strooper 
  1,2,7,8 
Controversies over a­nt­i-­am­yloid i­mm­un­ot­he­rapies underscore the 
need to elucidate their mechanisms of action. Here we demonstrate that 
Lecanemab, a leading anti-β-amyloid (Aβ) antibody, mediates amyloid 
clearance by activating microglial effector functions. Using a human 
microglia xenograft mouse model, we show that Lecanemab significantly 
reduces Aβ pathology and associated neuritic damage, while neither 
fragment crystallizable (Fc)-silenced Lecanemab nor microglia deficiency 
elicits this effect despite intact plaque binding. Single-cell RNA sequencing 
and spatial transcriptomic analyses reveal that Lecanemab induces a 
focused t­r­a­ns­c­r­ip­tional p­r­o­g­r­am that enhances phagocytosis, lysosomal 
degradation, metabolic reprogramming, interferon γ genes and antigen 
presentation. Finally, we identify SPP1/osteopontin as a major factor 
induced by Lecanemab treatment and demonstrate its role in promoting Aβ 
clearance. These findings highlight that effective amyloid removal depends 
on the engagement of microglia through the Fc fragment, providing critical 
insights for optimizing anti-amyloid therapies in Alzheimer’s disease.
Lecanemab, an antibody engineered to target soluble amyloid β-amyloid 
(Aβ) protofibrils1, effectively removes amyloid plaques from the brains 
of Alzheimer’s disease (AD) patients, slowing cognitive decline by 27%2. 
Although originally developed against peptides containing the rare 
Arctic mutation causally linked to inherited AD1, Lecanemab also shows 
efficacy in sporadic AD cases. Nonetheless, the precise mechanism by 
which its binding to Aβ oligomers leads to more effective Aβ-plaque 
clearance compared to other Aβ-binding antibodies3 remains unclear.
One prevailing hypothesis suggests that plaque clearance is medi-
ated by fragment crystallizable (Fc) γ receptor (FcγR) activation of 
microglia, triggering phagocytosis of Aβ4–6. However, direct experi-
mental evidence linking microglia activity to the therapeutic efficacy of 
Lecanemab is lacking. For instance, while some studies report microglia 
accumulation around amyloid plaques after immunotherapy5, such 
clustering is also observed without the antibody treatment and does not 
necessarily result in Aβ-plaque removal. Moreover, FcγR activation can 
Received: 30 July 2024
Accepted: 9 October 2025
Published online: xx xx xxxx
 Check for updates
1Centre for Brain and Disease Research, Flanders Institute for Biotechnology (VIB), Leuven, Belgium. 2Department of Neurosciences and Leuven Brain 
Institute, KU Leuven, Leuven, Belgium. 3Laboratory for Therapeutic and Diagnostic Antibodies, Department of Pharmaceutical and Pharmacological 
Sciences, KU Leuven, Leuven, Belgium. 4Single Cell Core, Flanders Institute for Biotechnology (VIB), Leuven, Belgium. 5Center for Molecular Neurology, 
Flanders Institute for Biotechnology (VIB), Antwerp, Belgium. 6Department of Biomedical Sciences, University of Antwerp, Antwerp, Belgium. 7UK 
Dementia Research Institute, University College London, London, UK. 8Department of Human Genetics, KU Leuven, Leuven, Belgium. 9These authors 
contributed equally: Giulia Albertini, Magdalena Zielonka. 
 e-mail: giulia.albertini@kuleuven.be; b.strooper@ucl.ac.uk
- 必写2: 第2页主要提供仑卡奈单抗相关的疗效结果、作用机制信息。；原始数字 Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
immunoglobulin G1 (IgG1) variant designed to abolish Fc-mediated 
effector functions14,15, Lecanemab LALA-PG. We leveraged our 
advanced human microglia xenotransplantation model for AD16,17. 
Using Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; Il2rgtm1.1Flv; Apptm3.1Tcs; Csf1Rem1Bdes mice, 
named hereafter as AppNL-G-F Csf1rΔFIRE/ΔFIRE mice, which lack endogenous 
microglia17,18, enabled us to assess these clinically relevant human anti-
bodies directly. Notably, we corroborated our observations in fully 
induce a pro-inflammatory response with the release of cytokines and 
other toxic mediators7,8, potentially mitigating the benefits of Aβ clear-
ance. Alternative FcγR-independent mechanisms of plaque removal 
have also been widely proposed9–12. Consequently, the exact mechanism 
by which Lecanemab clears amyloid plaques remains unresolved.
To uncover the mechanisms driving antibody-induced amy-
loid clearance, we generated Lecanemab13 alongside a human 
0
50
100
150
200
D54D2
Lecanemab
Lecanemab
LALA-PG
Lecanemab
LALA-PG
8 weeks
2 weeks
8 weeks
−0.3
0
0.3
Running enrichment
score 
0
0.4
1,000
2,000
3,000
4,000
Rank in ordered dataset
Ranked list
metric 
KEGG: lysosome
Lec
LALA-PG
NES
P.adj
0.016
+1.94
–1.77 0.006
ACP2
 AP1S2 
ASAH1
ATP6AP1 
ATP6V0C 
ATP6V0D1 
CD63
CTSD 
CTSL
CTSS
CTSZ
DMXL2
 DNASE2 
GGA2
GM2A
Leading edge genes 
(Lec)
 HEXA
IDS 
LGMN
 LIPA 
LITAF
M6PR
 NEU1
PLA2G15
PPT1
 PSAP
SCARB2
SLC11A1
SLC11A2 
TPP1
Significance
Both significant
Significant in Lec only
Significant in LALA-PG only
Neither significant
AL627171.2
ARFGEF1
C3
CD9
COL1A1
COL3A1
CSF1R
CSTB
CTSB
CX3CR1
CYBB
HTRA1
IFNGR1
ISCU
MT−ATP6
MT−CYB
MT−ND4
NME2
OLR1
PSAP
RAP2B
RBM22
RNASE1
RPL23
RPL35A
RPL38
RPL41
RPLP1
RPS13
SNHG29
SP100
TMEM126B
TPT1
APOE
ASAH1
CD74
CTSD
EEF1G
EMB
FTL
HLA−DRA
HLA−DRB5
IFI44L
IFI6
IFITM3
LIPA
MALAT1
MT −ND5
NIBAN1
NR1D2
RPL12
RPL18
RPL24
RPL36
SPP1
TENT4A
VSIG4
WDR61
AD000090.1
APOC1
MT −CO3
NAP1L1
RPS23
0
0.2
0.4
−0.2
0
0.2
Lec LALA-PG (LFC for 100 µm closer to pathology)
Lecanemab 8 weeks
Lecanemab LALA-PG 8 weeks
Lec (LFC for 100 µm closer to pathology)
DE of TDs with respect to distance to pathology (cortex)
–0.25
–0.50
0
0.25
Running enrichment
score 
0
0.4
1,000
2,000
3,000
4,000
Rank in ordered dataset
Ranked list
metric 
Lec
LALA-PG
NES
P.adj
0.027
+1.57
–1.63 0.006
ATP6AP1 
ATP6V0C 
ATP6V0D1 
ATP6V0E1 
ATP6V1B2 
ATP6V1F 
CLEC7A 
CTSL 
CTSS 
CYBA 
DYNC1I2 
FCGR1A 
HLA-B
HLA-C 
HLA-DMB 
HLA-DPA1
Leading edge genes 
(Lec)
HLA-DPB1 
HLA-DQB1 
HLA-DRA 
HLA-DRB1
 HLA-DRB5
 HLA-E
ITGB1
 ITGB2
ITGB5
M6PR 
OLR1
RAB7A 
SEC61G 
STX7 
TLR4
0
50
100
150
200
DAPI
hCD45
Lecanemab LALA-PG
D54D2
D54D2
D54D2
DAPI
hCD45
Lecanemab 
D54D2
b
c
d
a
e
g
f
hCD45
microglia
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
D54D2
plaques
IgG
antibody
Merge
with DAPI
KEGG: phagosome
100 µm
100 µm
100 µm
100 µm
100 µm
100 µm
- 必写3: 第3页主要提供仑卡奈单抗、4个月、6个月相关英文材料。；原始数字 Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
immune-competent mice treated with mouse analogs of Lecanemab. 
Our work probes a critical conundrum, that is, why do microglia—
although strongly activated in the presence of amyloid plaques—fail 
to clear these deposits? We hypothesize that antibody engagement 
unveils latent, transformative mechanisms, endowing microglia with 
an unexpected capacity for plaque clearance. Our work suggests 
that antibody treatment reprograms microglial function, providing 
insights into protective roles of these cells while also opening new 
avenues to understand and ultimately harness these changes for 
therapeutic benefit.
Results
Lecanemab binds to amyloid plaques
By 4 months of age, xenografted human microglia had efficiently 
colonized the mouse brain (Extended Data Fig. 1a,b) and, by 6 
months, they are fully able to mount amyloid responses that strongly 
resemble the ones observed in AD patients (as previously charac-
terized in ref. 16; Extended Data Fig. 1c). Starting from 4 months of 
age, we administered weekly intraperitoneal injections of 10 mg kg−1 
Lecanemab or Lecanemab LALA-PG19. After 8 weeks of treatment, 
we analyzed the distribution of the human antibodies in the brain 
parenchyma (Fig. 1a,b). Strikingly, while only sparse antibody signals 
were detected in Lecanemab-treated mice (notably within human 
CD45⁺ microglia surfaces, as reconstructed in Supplementary 
Video 1), Lecanemab LALA-PG strongly accumulated on Aβ plaques. 
This accumulation is already evident after 2 weeks of treatment 
(Fig. 1c). These data suggest that mutating the Fc fragment to abolish 
Fc-based effector functions prevents uptake of Lecanemab into micro-
glia. Additionally, our findings demonstrate that Lecanemab binds 
to plaques, challenging the common assumption that it is specific to 
Fig. 1 | Lecanemab drives strong transcriptional changes in human microglia 
associated with Aβ plaques. a–c, Representative high-magnification confocal 
z-stacks of CD45 (human microglia, blue), D54D2 (Aβ, green), IgG (human 
antibody, magenta) and a merged view with DAPI-stained nuclei (yellow). These 
high-resolution z-stacks are used to show the colocalization between D54D2 
and IgG, as well as the internalization of Lecanemab within the microglia. Scale 
bar = 50 µm. Staining shown is representative; experiments were performed 
on four mice per condition for 8-week treatments and three mice per condition 
for 2-week treatments, all from the same treatment batch, and the experiments 
were repeated across two independent staining batches. a, After 8 weeks of 
Lecanemab administration, human IgG is detected in the brain parenchyma, 
where it associates with Aβ plaques and is internalized by human microglia 
(arrows). b, Notably, after 8 weeks of Lecanemab LALA-PG administration, 
IgG exhibits strong accumulation on D54D2 + Aβ plaques, indicating that a 
functional Fc fragment is necessary for uptake in microglia. c, This accumulation 
is already apparent as early as 2 weeks after the treatment in Lecanemab 
LALA-PG-treated mice. d, Representative large-field images of the Nova-ST 
data coupled with immunofluorescence workflow for Lecanemab-treated (top) 
and Lecanemab LALA-PG-treated (bottom) mice. Immunofluorescence was 
performed to visualize human microglia (CD45+, blue), Aβ plaques (D54D2+, 
green), Lecanemab or Lecanemab LALA-PG (magenta) and DAPI-stained nuclei 
(yellow). D54D2 signal was used to define the plaque regions (outlined in cyan). 
Left, a merged view; middle, D54D2; right, spatial transcriptomic TDs (spots 
binned into hexbins with a diameter of 40 µm) overlayed with plaque ROIs. TDs 
are colored based on their relative expression of human transcripts (purple, 
low expression; yellow, high expression). Scale bar = 100 µm. Images shown 
are representative; experiments were performed on one mouse per condition 
in each of two independent Nova-ST batches (total two mice per condition). 
e, Quadrant plot showing the log2(FC) of genes in Lecanemab-treated (x axis) 
and Lecanemab LALA-PG-treated (y axis) TDs with respect to their distance to 
plaques in the Nova-ST dataset. TDs were analyzed in the cortical regions of 
n = 2 mice per condition. A positive log2(FC) indicates upregulation in proximity 
to plaques. Red, genes significant in Lecanemab microglia only; purple, genes 
significant in Lecanemab LALA-PG microglia only; green, genes significant in 
both comparisons; gray, genes not significant in either comparison. log2(FC) 
were calculated using edgeR’s quasi-likelihood F test (two-sided); P values were 
adjusted using the BH correction (Padj < 0.05). f,g, From the differential gene 
expression analysis in e, we performed GSEA to further explore shifts in the 
microglia phenotype after the antibody treatment. We observed a significant 
positive enrichment of lysosome (f) and phagosome (g) genes in Lecanemab TDs 
near Aβ plaques (red), whereas such enrichment was not observed in Lecanemab 
LALA-PG TDs (purple). The vertical lines indicate the ES. Vertical tick marks along 
the x axis show the location of individual genes in the gene set within the log2(FC)-
ranked gene list. The NES, two-sided Padj value and the leading-edge genes are 
shown for the GSEA performed on the Lecanemab and Lecanemab LALA-PG TDs. 
P values were adjusted using the BH correction. FC, fold change; ES, enrichment 
score; NES, normalized enrichment score. BH, Benjamini–Hochberg.
Fig. 2 | Lecanemab alleviates Aβ pathology by triggering effector functions 
in the microglia. a, AppNL-G-F Csf1rΔFIRE/ΔFIRE mice were xenotransplanted at P4 
with human-derived microglial progenitors differentiated in vitro. Starting 
from 4 months of age, mice were treated for 8 weeks with IgG1, Lecanemab or 
Lecanemab LALA-PG (10 mg kg−1, weekly i.p. injections) and killed for subsequent 
analysis. b, Representative confocal images of plaques stained with X-34 or 
82E1 in sagittal brain sections from mice treated with the indicated antibodies; 
scale bar = 1 mm; inset = 250 µm. c,d, Quantification of X-34 (c) and 82E1 (d) 
area expressed as percentage of the total section area; (c) Kruskal–Wallis test 
(P = 0.0003) and (d) one-way ANOVA (P < 0.0001; IgG1, n = 10 mice; Lec, n = 12 
mice; Lec LALA-PG, n = 9 mice). e, Distribution of X-34+ plaques based on their 
area (x axis) shows that Lecanemab mainly affects small plaques; Anderson–
Darling test, P < 0.0001 (IgG1 versus Lecanemab, P < 0.0003; Lecanemab 
versus Lecanemab LALA-PG, P < 0.0003; IgG1 versus Lecanemab LALA-PG, NS; 
two-sided Kolmogorov–Smirnov test; IgG1, n = 975 X-34+ plaques from 10 mice; 
Lec, n = 731 X-34+ plaques from 12 mice; Lec LALA-PG, n = 942 X-34+ plaques 
from 9 mice). To account for multiple comparisons (three in total), we applied a 
Bonferroni correction by multiplying the obtained P values by 3. f, MSD ELISA of 
Aβ42 (P = 0.0001, Kruskal–Wallis test followed by Dunn’s multiple comparison 
test), Aβ40 (NS, one-way ANOVA) and Aβ38 (P = 0.0117, one-way ANOVA 
followed by Bonferroni’s multiple comparisons test) levels in insoluble (GuHCl 
extractable) brain extracts (IgG1, n = 11 mice; Lec, n = 14 mice; Lec LALA-PG, n = 11 
mice). g, MSD ELISA of Aβ42 (P = 0.0505, Kruskal–Wallis test), Aβ40 (NS, one-way 
ANOVA) and Aβ38 (P = 0.0005, one-way ANOVA followed by Bonferroni’s multiple 
comparisons test) levels in soluble (T-PER buffer extractable) brain extracts 
(IgG1, n = 10-11 mice; Lec, n = 14 mice; Lec LALA-PG, n = 11 mice). h, A cohort of 
immunocompetent AppNL-G-F mice was used to assess the impact of mAb158 (a 
mouse version of Lecanemab), its engineered LALA-PG variant and a control 
mouse IgG2a on Aβ levels by MSD. i, MSD ELISA of Aβ42 (P < 0.0001, one-way 
ANOVA followed by Bonferroni’s multiple comparisons test), Aβ40 (P = 0.0005, 
one-way ANOVA followed by Bonferroni’s multiple comparisons test) and Aβ38 
(P < 0.0001, one-way ANOVA followed by Bonferroni’s multiple comparisons 
test) levels in insoluble brain extracts (IgG2a, n = 8–9 mice; mAb158, n = 8–9 
mice; mAb158 LALA-PG, n = 7–9 mice). j, MSD ELISA of Aβ42 (P = 0.0355, one-way 
ANOVA followed by Bonferroni’s multiple comparisons test), Aβ40 (P = 0.0026, 
one-way ANOVA followed by Bonferroni’s multiple comparisons test) and Aβ38 
(P = 0.0032, one-way ANOVA followed by Bonferroni’s multiple comparisons 
test) levels in soluble brain extracts (IgG2a, n = 8–9 mice; mAb158, n = 9 mice; 
mAb158 LALA-PG, n = 9 mice). k, A cohort of AppNL-G-F Csf1rΔFIRE/ΔFIRE mice was not 
xenotransplanted and used to assess if Lecanemab alters Aβ pathology in the 
absence of microglia. Panels a, h and k were created with BioRender.com. l, 
Representative confocal images for X-34 and 82E1 in sagittal brain sections from 
AppNL-G-F Csf1rΔFIRE/ΔFIRE mice treated with IgG1 or Lecanemab; scale bars = 1 mm, 
inset = 250 µm. m,n, Quantification of X-34 (m) and 82E1 (n) areas (unpaired two-
sided t-tests, NS) expressed as percentage of the section area (IgG1, n = 7 mice; 
Lec, n = 9 mice). o, MSD ELISA of Aβ42, Aβ40 and Aβ38 levels in insoluble brain 
extracts (unpaired two-sided t-tests, NS; IgG1, n = 9–10 mice; Lec, n = 12 mice). 
p, MSD ELISA of Aβ42, Aβ40 and Aβ38 levels in soluble brain extracts (unpaired 
two-sided t-tests, NS; IgG1, n = 9–10 mice; Lec, n = 12 mice). Mean ± s.e.m. shown 
for each group and points represent individual animals. Square symbols, males; 
triangle, females. hMPs, human microglial progenitors; NS, not significant; 
ANOVA, analysis of variance.
- 必写4: 分子靶点：可溶性Aβ原纤维；原始数字 Anti-Aβ protofibril antibody
- 必写5: 获批用法用量；原始数字 10 mg/kg IV q2w
- 必写6: 第4页主要提供仑卡奈单抗、4个月相关英文材料。；原始数字 Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
oligomers. These remarkable findings led us to investigate the poten-
tial changes these antibodies might induce in the human microglia 
surrounding the Aβ plaques20,21.
Spatial transcriptomics reveals Lecanemab-driven 
enhancement of microglial phagocytic and lysosomal 
pathways
We used Nova-ST22, a recently developed technique based on the 
Illumina NovaSeq flow cells, which enabled us to combine unbiased 
high-resolution spatial transcriptomics with immunofluorescence 
of amyloid plaques (positive for the anti-Aβ antibody D54D2) on the 
same tissue section (Fig. 1d and Extended Data Fig. 2). Because only the 
xenotransplanted cells are of human origin, all human-derived reads 
can be exclusively attributed to microglia23.
We first converted the raw spatial expression matrix by bin-
ning spots into hexbin pseudospots with a diameter of 40 μm and a 
center-to-center distance of 40 μm (tissue domains (TDs)), and retained 
only those with at least 30 human transcripts for further analysis. A 
IgG1 Lec
IgG1 Lec
0
0.5
1.0
1.5
X34 covered area (%)
Total brain
IgG1 Lec
IgG1 Lec
IgG1 Lec
IgG1 Lec
IgG1 Lec
IgG1 Lec
0
2,000
4,000
6,000
8,000
Aβ42 (pg mg
–1 of tissue)
0
20
40
60
80
Aβ38 (pg mg
–1 of tissue)
0
1
2
3
4
Aβ40 (pg mg
–1 of tissue)
0
1
2
3
4
Aβ38 (pg mg
–1 of tissue)
0
0.5
1.0
1.5
2.0
Aβ42 (pg mg
–1 of tissue)
0
0.05
0.10
0.15
0.20
Aβ40 (pg mg
–1 of tissue)
f
c
d
e
AppNL-G-F Csf1r∆FIRE/∆FIRE mice xenotransplanted with human microglia
AppNL-G-F
Csf1r∆FIRE/∆FIRE
P4 
 
Insoluble Aβ
Plaque load
g
Soluble Aβ
AppNL-G-F Csf1r∆FIRE/∆FIRE mice genetically lacking microglia
m
n
o
p
l
IgG1
X-34
Lecanemab
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
h
App
NL-G-F immunocompetent mice
i
Males
Females
Males
Females
Insoluble Aβ
j
Soluble Aβ
b
IgG1
Lecanemab
Lecanemab LALA-PG
X-34
82E1
a
Males
Females
Males
Females
Males
Females
Males
Females
Plaque load
Soluble Aβ
Males
Females
Insoluble Aβ
Males
Females
IgG1
Lec
Lec
LALA-PG
IgG1
Lec
Lec
LALA-PG
0
0.5
1.0
1.5
2.0
2.5
X-34 covered area (%)
Total brain
0.0207
0.0003
0
1
2
3
4
5
82E1 covered area (%)
Total brain
0.0003
<0.0001
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
0
5,000
10,000
15,000
Aβ42 (pg mg
–1 of tissue)
0.0001
0.0175
0
1
2
3
4
Aβ40 (pg mg
–1 of tissue)
0
50
100
150
200
Aβ38 (pg mg
–1 of tissue)
0.0093
0
1
2
3
4
5
Aβ38 (pg mg
–1 of tissue)
0.0004
0
0.1
0.2
0.3
Aβ40 (pg mg
–1 of tissue)
0
0.5
1.0
1.5
2.0
2.5
Aβ42 (pg mg
–1 of tissue)
AppNL-G-F
Csf1r∆FIRE/∆FIRE
 
0
20
40
60
80 100 120 140 160 180 200
0
100
200
300
400
500
X-34+ area (µm2) 
Number of values
IgG1
Lec
Lec LALA-PG
82E1
k
0
10
20
30
40
50
0.0020 <0.0001
0
2
4
6
8
0.0016 0.0019
IgG2a
mAb158
mAb158
IgG2a
mAb158
mAb158
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
0
1,000
2,000
3,000
4,000
5,000
Aβ38 (pg mg
–1 of tissue)
Aβ38 (pg mg
–1 of tissue)
Aβ40 (pg mg
–1 of tissue)
Aβ40 (pg mg
–1 of tissue)
Aβ42 (pg mg
–1 of tissue)
Aβ42 (pg mg
–1 of tissue)
<0.0001
<0.0001
0
0.1
0.2
0.3
0.4
0.0142
0
0.5
1.0
1.5
2.0
2.5
0.0025
0
0.2
0.4
0.6
0.8
1.0
0.0396
0
1
2
3
4
5
82E1 covered area (%)
Total brain
hMPs
250K
each side
hMPs
Day 18
4 months
Human
microglia
IgG1
Lec
8 weeks
10 mg kg
–1 weekly
Confocal microscopy
MSD
Confocal microscopy
MSD
Lec
LALA-PG
Mouse
 microglia
AppNL-G-F 
4 months 
IgG2a mAb158
8 weeks
10 mg kg
–1 weekly
No
microglia
4 months 
IgG
1Lec
8 weeks
10 mg kg
–1 weekly
MSD
mAb158
LALA-PG
250 µm
1 mm

【章节篇幅预算】
- 引言: 约 250 字（约 10%）
- 结论: 约 250 字（约 10%）
- Mechanism: 约 137 字（约 6%）
- 疗效分析: 约 1862 字（约 74%）
- 若总字数不足，优先补足主体分析段，不要只扩标题、引言或结尾。

证据详情:

【mechanism】
- Approved dosing regimen: 10 mg/kg IV q2w None
- Molecular target: soluble Aβ protofibrils: Anti-Aβ protofibril antibody None

【efficacy】
- 第1页主要是论文标题、作者和机构信息。: Nature Neuroscience
nature neuroscience
https://doi.org/10.1038/s41593-025-02125-8
Article
The Alzheimer’s therapeutic Lecanemab 
attenuates Aβ pathology by inducing an 
amyloid-clearing program in microglia
 
Giulia Albertini 
  1,2,9 
, Magdalena Zielonka 
  1,2,9, Marie-Lynn Cuypers 
  3, 
An Snellinx1,2, Ciana Xu 
  1,2, Suresh Poovathingal1,4, Marta Wojno 
  1,4, 
Kristofer Davie 
  1,4, Veerle van Lieshout 
  1,2, Katleen Craessaerts1,2, 
Leen Wolfs1,2, Emanuela Pasciuto1,2,5,6, Tom Jaspers 
  3, Katrien Horré1,2, 
Lurgarde Serneels1,2, Mark Fiers1,2,7,8, Maarten Dewilde 
  3 & 
Bart De Strooper 
  1,2,7,8 
Controversies over a­nt­i-­am­yloid i­mm­un­ot­he­rapies underscore the 
need to elucidate their mechanisms of action. Here we demonstrate that 
Lecanemab, a leading anti-β-amyloid (Aβ) antibody, mediates amyloid 
clearance by activating microglial effector functions. Using a human 
microglia xenograft mouse model, we show that Lecanemab significantly 
reduces Aβ pathology and associated neuritic damage, while neither 
fragment crystallizable (Fc)-silenced Lecanemab nor microglia deficiency 
elicits this effect despite intact plaque binding. Single-cell RNA sequencing 
and spatial transcriptomic analyses reveal that Lecanemab induces a 
focused t­r­a­ns­c­r­ip­tional p­r­o­g­r­am that enhances phagocytosis, lysosomal 
degradation, metabolic reprogramming, interferon γ genes and antigen 
presentation. Finally, we identify SPP1/osteopontin as a major factor 
induced by Lecanemab treatment and demonstrate its role in promoting Aβ 
clearance. These findings highlight that effective amyloid removal depends 
on the engagement of microglia through the Fc fragment, providing critical 
insights for optimizing anti-amyloid therapies in Alzheimer’s disease.
Lecanemab, an antibody engineered to target soluble amyloid β-amyloid 
(Aβ) protofibrils1, effectively removes amyloid plaques from the brains 
of Alzheimer’s disease (AD) patients, slowing cognitive decline by 27%2. 
Although originally developed against peptides containing the rare 
Arctic mutation causally linked to inherited AD1, Lecanemab also shows 
efficacy in sporadic AD cases. Nonetheless, the precise mechanism by 
which its binding to Aβ oligomers leads to more effective Aβ-plaque 
clearance compared to other Aβ-binding antibodies3 remains unclear.
One prevailing hypothesis suggests that plaque clearance is medi-
ated by fragment crystallizable (Fc) γ receptor (FcγR) activation of 
microglia, triggering phagocytosis of Aβ4–6. However, direct experi-
mental evidence linking microglia activity to the therapeutic efficacy of 
Lecanemab is lacking. For instance, while some studies report microglia 
accumulation around amyloid plaques after immunotherapy5, such 
clustering is also observed without the antibody treatment and does not 
necessarily result in Aβ-plaque removal. Moreover, FcγR activation can 
Received: 30 July 2024
Accepted: 9 October 2025
Published online: xx xx xxxx
 Check for updates
1Centre for Brain and Disease Research, Flanders Institute for Biotechnology (VIB), Leuven, Belgium. 2Department of Neurosciences and Leuven Brain 
Institute, KU Leuven, Leuven, Belgium. 3Laboratory for Therapeutic and Diagnostic Antibodies, Department of Pharmaceutical and Pharmacological 
Sciences, KU Leuven, Leuven, Belgium. 4Single Cell Core, Flanders Institute for Biotechnology (VIB), Leuven, Belgium. 5Center for Molecular Neurology, 
Flanders Institute for Biotechnology (VIB), Antwerp, Belgium. 6Department of Biomedical Sciences, University of Antwerp, Antwerp, Belgium. 7UK 
Dementia Research Institute, University College London, London, UK. 8Department of Human Genetics, KU Leuven, Leuven, Belgium. 9These authors 
contributed equally: Giulia Albertini, Magdalena Zielonka. 
 e-mail: giulia.albertini@kuleuven.be; b.strooper@ucl.ac.uk
- 第2页主要提供仑卡奈单抗相关的疗效结果、作用机制信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
immunoglobulin G1 (IgG1) variant designed to abolish Fc-mediated 
effector functions14,15, Lecanemab LALA-PG. We leveraged our 
advanced human microglia xenotransplantation model for AD16,17. 
Using Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; Il2rgtm1.1Flv; Apptm3.1Tcs; Csf1Rem1Bdes mice, 
named hereafter as AppNL-G-F Csf1rΔFIRE/ΔFIRE mice, which lack endogenous 
microglia17,18, enabled us to assess these clinically relevant human anti-
bodies directly. Notably, we corroborated our observations in fully 
induce a pro-inflammatory response with the release of cytokines and 
other toxic mediators7,8, potentially mitigating the benefits of Aβ clear-
ance. Alternative FcγR-independent mechanisms of plaque removal 
have also been widely proposed9–12. Consequently, the exact mechanism 
by which Lecanemab clears amyloid plaques remains unresolved.
To uncover the mechanisms driving antibody-induced amy-
loid clearance, we generated Lecanemab13 alongside a human 
0
50
100
150
200
D54D2
Lecanemab
Lecanemab
LALA-PG
Lecanemab
LALA-PG
8 weeks
2 weeks
8 weeks
−0.3
0
0.3
Running enrichment
score 
0
0.4
1,000
2,000
3,000
4,000
Rank in ordered dataset
Ranked list
metric 
KEGG: lysosome
Lec
LALA-PG
NES
P.adj
0.016
+1.94
–1.77 0.006
ACP2
 AP1S2 
ASAH1
ATP6AP1 
ATP6V0C 
ATP6V0D1 
CD63
CTSD 
CTSL
CTSS
CTSZ
DMXL2
 DNASE2 
GGA2
GM2A
Leading edge genes 
(Lec)
 HEXA
IDS 
LGMN
 LIPA 
LITAF
M6PR
 NEU1
PLA2G15
PPT1
 PSAP
SCARB2
SLC11A1
SLC11A2 
TPP1
Significance
Both significant
Significant in Lec only
Significant in LALA-PG only
Neither significant
AL627171.2
ARFGEF1
C3
CD9
COL1A1
COL3A1
CSF1R
CSTB
CTSB
CX3CR1
CYBB
HTRA1
IFNGR1
ISCU
MT−ATP6
MT−CYB
MT−ND4
NME2
OLR1
PSAP
RAP2B
RBM22
RNASE1
RPL23
RPL35A
RPL38
RPL41
RPLP1
RPS13
SNHG29
SP100
TMEM126B
TPT1
APOE
ASAH1
CD74
CTSD
EEF1G
EMB
FTL
HLA−DRA
HLA−DRB5
IFI44L
IFI6
IFITM3
LIPA
MALAT1
MT −ND5
NIBAN1
NR1D2
RPL12
RPL18
RPL24
RPL36
SPP1
TENT4A
VSIG4
WDR61
AD000090.1
APOC1
MT −CO3
NAP1L1
RPS23
0
0.2
0.4
−0.2
0
0.2
Lec LALA-PG (LFC for 100 µm closer to pathology)
Lecanemab 8 weeks
Lecanemab LALA-PG 8 weeks
Lec (LFC for 100 µm closer to pathology)
DE of TDs with respect to distance to pathology (cortex)
–0.25
–0.50
0
0.25
Running enrichment
score 
0
0.4
1,000
2,000
3,000
4,000
Rank in ordered dataset
Ranked list
metric 
Lec
LALA-PG
NES
P.adj
0.027
+1.57
–1.63 0.006
ATP6AP1 
ATP6V0C 
ATP6V0D1 
ATP6V0E1 
ATP6V1B2 
ATP6V1F 
CLEC7A 
CTSL 
CTSS 
CYBA 
DYNC1I2 
FCGR1A 
HLA-B
HLA-C 
HLA-DMB 
HLA-DPA1
Leading edge genes 
(Lec)
HLA-DPB1 
HLA-DQB1 
HLA-DRA 
HLA-DRB1
 HLA-DRB5
 HLA-E
ITGB1
 ITGB2
ITGB5
M6PR 
OLR1
RAB7A 
SEC61G 
STX7 
TLR4
0
50
100
150
200
DAPI
hCD45
Lecanemab LALA-PG
D54D2
D54D2
D54D2
DAPI
hCD45
Lecanemab 
D54D2
b
c
d
a
e
g
f
hCD45
microglia
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
50 µm
D54D2
plaques
IgG
antibody
Merge
with DAPI
KEGG: phagosome
100 µm
100 µm
100 µm
100 µm
100 µm
100 µm
- 第3页主要提供仑卡奈单抗、4个月、6个月相关英文材料。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
immune-competent mice treated with mouse analogs of Lecanemab. 
Our work probes a critical conundrum, that is, why do microglia—
although strongly activated in the presence of amyloid plaques—fail 
to clear these deposits? We hypothesize that antibody engagement 
unveils latent, transformative mechanisms, endowing microglia with 
an unexpected capacity for plaque clearance. Our work suggests 
that antibody treatment reprograms microglial function, providing 
insights into protective roles of these cells while also opening new 
avenues to understand and ultimately harness these changes for 
therapeutic benefit.
Results
Lecanemab binds to amyloid plaques
By 4 months of age, xenografted human microglia had efficiently 
colonized the mouse brain (Extended Data Fig. 1a,b) and, by 6 
months, they are fully able to mount amyloid responses that strongly 
resemble the ones observed in AD patients (as previously charac-
terized in ref. 16; Extended Data Fig. 1c). Starting from 4 months of 
age, we administered weekly intraperitoneal injections of 10 mg kg−1 
Lecanemab or Lecanemab LALA-PG19. After 8 weeks of treatment, 
we analyzed the distribution of the human antibodies in the brain 
parenchyma (Fig. 1a,b). Strikingly, while only sparse antibody signals 
were detected in Lecanemab-treated mice (notably within human 
CD45⁺ microglia surfaces, as reconstructed in Supplementary 
Video 1), Lecanemab LALA-PG strongly accumulated on Aβ plaques. 
This accumulation is already evident after 2 weeks of treatment 
(Fig. 1c). These data suggest that mutating the Fc fragment to abolish 
Fc-based effector functions prevents uptake of Lecanemab into micro-
glia. Additionally, our findings demonstrate that Lecanemab binds 
to plaques, challenging the common assumption that it is specific to 
Fig. 1 | Lecanemab drives strong transcriptional changes in human microglia 
associated with Aβ plaques. a–c, Representative high-magnification confocal 
z-stacks of CD45 (human microglia, blue), D54D2 (Aβ, green), IgG (human 
antibody, magenta) and a merged view with DAPI-stained nuclei (yellow). These 
high-resolution z-stacks are used to show the colocalization between D54D2 
and IgG, as well as the internalization of Lecanemab within the microglia. Scale 
bar = 50 µm. Staining shown is representative; experiments were performed 
on four mice per condition for 8-week treatments and three mice per condition 
for 2-week treatments, all from the same treatment batch, and the experiments 
were repeated across two independent staining batches. a, After 8 weeks of 
Lecanemab administration, human IgG is detected in the brain parenchyma, 
where it associates with Aβ plaques and is internalized by human microglia 
(arrows). b, Notably, after 8 weeks of Lecanemab LALA-PG administration, 
IgG exhibits strong accumulation on D54D2 + Aβ plaques, indicating that a 
functional Fc fragment is necessary for uptake in microglia. c, This accumulation 
is already apparent as early as 2 weeks after the treatment in Lecanemab 
LALA-PG-treated mice. d, Representative large-field images of the Nova-ST 
data coupled with immunofluorescence workflow for Lecanemab-treated (top) 
and Lecanemab LALA-PG-treated (bottom) mice. Immunofluorescence was 
performed to visualize human microglia (CD45+, blue), Aβ plaques (D54D2+, 
green), Lecanemab or Lecanemab LALA-PG (magenta) and DAPI-stained nuclei 
(yellow). D54D2 signal was used to define the plaque regions (outlined in cyan). 
Left, a merged view; middle, D54D2; right, spatial transcriptomic TDs (spots 
binned into hexbins with a diameter of 40 µm) overlayed with plaque ROIs. TDs 
are colored based on their relative expression of human transcripts (purple, 
low expression; yellow, high expression). Scale bar = 100 µm. Images shown 
are representative; experiments were performed on one mouse per condition 
in each of two independent Nova-ST batches (total two mice per condition). 
e, Quadrant plot showing the log2(FC) of genes in Lecanemab-treated (x axis) 
and Lecanemab LALA-PG-treated (y axis) TDs with respect to their distance to 
plaques in the Nova-ST dataset. TDs were analyzed in the cortical regions of 
n = 2 mice per condition. A positive log2(FC) indicates upregulation in proximity 
to plaques. Red, genes significant in Lecanemab microglia only; purple, genes 
significant in Lecanemab LALA-PG microglia only; green, genes significant in 
both comparisons; gray, genes not significant in either comparison. log2(FC) 
were calculated using edgeR’s quasi-likelihood F test (two-sided); P values were 
adjusted using the BH correction (Padj < 0.05). f,g, From the differential gene 
expression analysis in e, we performed GSEA to further explore shifts in the 
microglia phenotype after the antibody treatment. We observed a significant 
positive enrichment of lysosome (f) and phagosome (g) genes in Lecanemab TDs 
near Aβ plaques (red), whereas such enrichment was not observed in Lecanemab 
LALA-PG TDs (purple). The vertical lines indicate the ES. Vertical tick marks along 
the x axis show the location of individual genes in the gene set within the log2(FC)-
ranked gene list. The NES, two-sided Padj value and the leading-edge genes are 
shown for the GSEA performed on the Lecanemab and Lecanemab LALA-PG TDs. 
P values were adjusted using the BH correction. FC, fold change; ES, enrichment 
score; NES, normalized enrichment score. BH, Benjamini–Hochberg.
Fig. 2 | Lecanemab alleviates Aβ pathology by triggering effector functions 
in the microglia. a, AppNL-G-F Csf1rΔFIRE/ΔFIRE mice were xenotransplanted at P4 
with human-derived microglial progenitors differentiated in vitro. Starting 
from 4 months of age, mice were treated for 8 weeks with IgG1, Lecanemab or 
Lecanemab LALA-PG (10 mg kg−1, weekly i.p. injections) and killed for subsequent 
analysis. b, Representative confocal images of plaques stained with X-34 or 
82E1 in sagittal brain sections from mice treated with the indicated antibodies; 
scale bar = 1 mm; inset = 250 µm. c,d, Quantification of X-34 (c) and 82E1 (d) 
area expressed as percentage of the total section area; (c) Kruskal–Wallis test 
(P = 0.0003) and (d) one-way ANOVA (P < 0.0001; IgG1, n = 10 mice; Lec, n = 12 
mice; Lec LALA-PG, n = 9 mice). e, Distribution of X-34+ plaques based on their 
area (x axis) shows that Lecanemab mainly affects small plaques; Anderson–
Darling test, P < 0.0001 (IgG1 versus Lecanemab, P < 0.0003; Lecanemab 
versus Lecanemab LALA-PG, P < 0.0003; IgG1 versus Lecanemab LALA-PG, NS; 
two-sided Kolmogorov–Smirnov test; IgG1, n = 975 X-34+ plaques from 10 mice; 
Lec, n = 731 X-34+ plaques from 12 mice; Lec LALA-PG, n = 942 X-34+ plaques 
from 9 mice). To account for multiple comparisons (three in total), we applied a 
Bonferroni correction by multiplying the obtained P values by 3. f, MSD ELISA of 
Aβ42 (P = 0.0001, Kruskal–Wallis test followed by Dunn’s multiple comparison 
test), Aβ40 (NS, one-way ANOVA) and Aβ38 (P = 0.0117, one-way ANOVA 
followed by Bonferroni’s multiple comparisons test) levels in insoluble (GuHCl 
extractable) brain extracts (IgG1, n = 11 mice; Lec, n = 14 mice; Lec LALA-PG, n = 11 
mice). g, MSD ELISA of Aβ42 (P = 0.0505, Kruskal–Wallis test), Aβ40 (NS, one-way 
ANOVA) and Aβ38 (P = 0.0005, one-way ANOVA followed by Bonferroni’s multiple 
comparisons test) levels in soluble (T-PER buffer extractable) brain extracts 
(IgG1, n = 10-11 mice; Lec, n = 14 mice; Lec LALA-PG, n = 11 mice). h, A cohort of 
immunocompetent AppNL-G-F mice was used to assess the impact of mAb158 (a 
mouse version of Lecanemab), its engineered LALA-PG variant and a control 
mouse IgG2a on Aβ levels by MSD. i, MSD ELISA of Aβ42 (P < 0.0001, one-way 
ANOVA followed by Bonferroni’s multiple comparisons test), Aβ40 (P = 0.0005, 
one-way ANOVA followed by Bonferroni’s multiple comparisons test) and Aβ38 
(P < 0.0001, one-way ANOVA followed by Bonferroni’s multiple comparisons 
test) levels in insoluble brain extracts (IgG2a, n = 8–9 mice; mAb158, n = 8–9 
mice; mAb158 LALA-PG, n = 7–9 mice). j, MSD ELISA of Aβ42 (P = 0.0355, one-way 
ANOVA followed by Bonferroni’s multiple comparisons test), Aβ40 (P = 0.0026, 
one-way ANOVA followed by Bonferroni’s multiple comparisons test) and Aβ38 
(P = 0.0032, one-way ANOVA followed by Bonferroni’s multiple comparisons 
test) levels in soluble brain extracts (IgG2a, n = 8–9 mice; mAb158, n = 9 mice; 
mAb158 LALA-PG, n = 9 mice). k, A cohort of AppNL-G-F Csf1rΔFIRE/ΔFIRE mice was not 
xenotransplanted and used to assess if Lecanemab alters Aβ pathology in the 
absence of microglia. Panels a, h and k were created with BioRender.com. l, 
Representative confocal images for X-34 and 82E1 in sagittal brain sections from 
AppNL-G-F Csf1rΔFIRE/ΔFIRE mice treated with IgG1 or Lecanemab; scale bars = 1 mm, 
inset = 250 µm. m,n, Quantification of X-34 (m) and 82E1 (n) areas (unpaired two-
sided t-tests, NS) expressed as percentage of the section area (IgG1, n = 7 mice; 
Lec, n = 9 mice). o, MSD ELISA of Aβ42, Aβ40 and Aβ38 levels in insoluble brain 
extracts (unpaired two-sided t-tests, NS; IgG1, n = 9–10 mice; Lec, n = 12 mice). 
p, MSD ELISA of Aβ42, Aβ40 and Aβ38 levels in soluble brain extracts (unpaired 
two-sided t-tests, NS; IgG1, n = 9–10 mice; Lec, n = 12 mice). Mean ± s.e.m. shown 
for each group and points represent individual animals. Square symbols, males; 
triangle, females. hMPs, human microglial progenitors; NS, not significant; 
ANOVA, analysis of variance.
- 第4页主要提供仑卡奈单抗、4个月相关英文材料。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
oligomers. These remarkable findings led us to investigate the poten-
tial changes these antibodies might induce in the human microglia 
surrounding the Aβ plaques20,21.
Spatial transcriptomics reveals Lecanemab-driven 
enhancement of microglial phagocytic and lysosomal 
pathways
We used Nova-ST22, a recently developed technique based on the 
Illumina NovaSeq flow cells, which enabled us to combine unbiased 
high-resolution spatial transcriptomics with immunofluorescence 
of amyloid plaques (positive for the anti-Aβ antibody D54D2) on the 
same tissue section (Fig. 1d and Extended Data Fig. 2). Because only the 
xenotransplanted cells are of human origin, all human-derived reads 
can be exclusively attributed to microglia23.
We first converted the raw spatial expression matrix by bin-
ning spots into hexbin pseudospots with a diameter of 40 μm and a 
center-to-center distance of 40 μm (tissue domains (TDs)), and retained 
only those with at least 30 human transcripts for further analysis. A 
IgG1 Lec
IgG1 Lec
0
0.5
1.0
1.5
X34 covered area (%)
Total brain
IgG1 Lec
IgG1 Lec
IgG1 Lec
IgG1 Lec
IgG1 Lec
IgG1 Lec
0
2,000
4,000
6,000
8,000
Aβ42 (pg mg
–1 of tissue)
0
20
40
60
80
Aβ38 (pg mg
–1 of tissue)
0
1
2
3
4
Aβ40 (pg mg
–1 of tissue)
0
1
2
3
4
Aβ38 (pg mg
–1 of tissue)
0
0.5
1.0
1.5
2.0
Aβ42 (pg mg
–1 of tissue)
0
0.05
0.10
0.15
0.20
Aβ40 (pg mg
–1 of tissue)
f
c
d
e
AppNL-G-F Csf1r∆FIRE/∆FIRE mice xenotransplanted with human microglia
AppNL-G-F
Csf1r∆FIRE/∆FIRE
P4 
 
Insoluble Aβ
Plaque load
g
Soluble Aβ
AppNL-G-F Csf1r∆FIRE/∆FIRE mice genetically lacking microglia
m
n
o
p
l
IgG1
X-34
Lecanemab
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
1 mm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
250 µm
h
App
NL-G-F immunocompetent mice
i
Males
Females
Males
Females
Insoluble Aβ
j
Soluble Aβ
b
IgG1
Lecanemab
Lecanemab LALA-PG
X-34
82E1
a
Males
Females
Males
Females
Males
Females
Males
Females
Plaque load
Soluble Aβ
Males
Females
Insoluble Aβ
Males
Females
IgG1
Lec
Lec
LALA-PG
IgG1
Lec
Lec
LALA-PG
0
0.5
1.0
1.5
2.0
2.5
X-34 covered area (%)
Total brain
0.0207
0.0003
0
1
2
3
4
5
82E1 covered area (%)
Total brain
0.0003
<0.0001
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
IgG1
Lec
Lec
LALA-PG 
0
5,000
10,000
15,000
Aβ42 (pg mg
–1 of tissue)
0.0001
0.0175
0
1
2
3
4
Aβ40 (pg mg
–1 of tissue)
0
50
100
150
200
Aβ38 (pg mg
–1 of tissue)
0.0093
0
1
2
3
4
5
Aβ38 (pg mg
–1 of tissue)
0.0004
0
0.1
0.2
0.3
Aβ40 (pg mg
–1 of tissue)
0
0.5
1.0
1.5
2.0
2.5
Aβ42 (pg mg
–1 of tissue)
AppNL-G-F
Csf1r∆FIRE/∆FIRE
 
0
20
40
60
80 100 120 140 160 180 200
0
100
200
300
400
500
X-34+ area (µm2) 
Number of values
IgG1
Lec
Lec LALA-PG
82E1
k
0
10
20
30
40
50
0.0020 <0.0001
0
2
4
6
8
0.0016 0.0019
IgG2a
mAb158
mAb158
IgG2a
mAb158
mAb158
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
IgG2a
mAb158
mAb158
LALA-PG
0
1,000
2,000
3,000
4,000
5,000
Aβ38 (pg mg
–1 of tissue)
Aβ38 (pg mg
–1 of tissue)
Aβ40 (pg mg
–1 of tissue)
Aβ40 (pg mg
–1 of tissue)
Aβ42 (pg mg
–1 of tissue)
Aβ42 (pg mg
–1 of tissue)
<0.0001
<0.0001
0
0.1
0.2
0.3
0.4
0.0142
0
0.5
1.0
1.5
2.0
2.5
0.0025
0
0.2
0.4
0.6
0.8
1.0
0.0396
0
1
2
3
4
5
82E1 covered area (%)
Total brain
hMPs
250K
each side
hMPs
Day 18
4 months
Human
microglia
IgG1
Lec
8 weeks
10 mg kg
–1 weekly
Confocal microscopy
MSD
Confocal microscopy
MSD
Lec
LALA-PG
Mouse
 microglia
AppNL-G-F 
4 months 
IgG2a mAb158
8 weeks
10 mg kg
–1 weekly
No
microglia
4 months 
IgG
1Lec
8 weeks
10 mg kg
–1 weekly
MSD
mAb158
LALA-PG
250 µm
1 mm
- 第5页主要提供仑卡奈单抗、8个月相关的疗效结果、生物标志物信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
total of 32,568 TDs were obtained across the cortical regions of the 
four samples, with 17,186 bins in the Lecanemab-treated samples and 
15,382 from Lecanemab LALA-PG samples (Extended Data Fig. 2a,b). 
Each TD captured an average of 61.3 human genes and 74.4 unique 
molecular identifiers (UMIs; Extended Data Fig. 2c). We then per-
formed a continuous differential expression (DE) analysis of cortical 
bins based on their distance from D54D2+ Aβ plaques, revealing that 
the expression of several genes substantially increases in function of 
proximity to plaques in the Lecanemab-treated mice, including APOE, 
CTSD, SPP1, CD74 and other genes associated to antigen presenta-
tion (Fig. 1e). Notably, gene set enrichment analysis (GSEA) indicated 
a significant increase in the expression of pathways related to the 
lysosome (Fig. 1f and Extended Data Fig. 2d) and phagosome (Fig. 1g 
and Extended Data Fig. 2d), specifically in the Lecanemab-treated 
TDs. Interestingly, these gene sets were significantly downregulated 
in Lecanemab LALA-PG TDs in proximity to pathology (Fig. 1f,g and 
Extended Data Fig. 2e), suggesting that the Fc fragment is critical for 
the activation of these pathways in microglia near plaques. That said, 
we detected distinct transcriptomic effects induced by the Lecanemab 
LALA-PG treatment (Extended Data Fig. 2e,f), suggesting that the accu-
mulation of nonfunctional antibody also modulates microglial activity 
near plaques. These data prompted further investigation into how the 
observed enhancements in phagocytosis and lysosomal functions by 
Lecanemab might affect plaque load.
Lecanemab attenuates Aβ pathology through Fc-mediated 
microglial phagocytosis
To assess the impact of Fc-mediated phagocytosis on Aβ plaque load, 
we treated a cohort of xenotransplanted AppNL-G-F Csf1rΔFIRE/ΔFIRE mice 
with Lecanemab, Lecanemab LALA-PG or human IgG1 control for 8 
weeks (Fig. 2a). After the completion of the treatment (24 h after the 
last injection), we collected the brains (Fig. 2b) and used immunohis-
tochemistry to analyze the impact of treatment on amyloid pathol-
ogy. We quantified both β-sheeted amyloid aggregates using X-34 
(Fig. 2c), and Aβ-peptides using a specific antibody (82E1; Fig. 2d). 
Lecanemab treatment significantly reduced plaque area compared 
to IgG1 or Lecanemab LALA-PG. Interestingly, when analyzing X-34+ 
plaque distribution, we observed that Lecanemab had the most pro-
nounced effect on smaller plaques (Fig. 2e). Histological data were 
corroborated by the Meso Scale Discovery (MSD) platform, which 
revealed significantly reduced guanidine-extractable (insoluble) 
Aβ42 levels in Lecanemab-treated mice compared to those treated 
with IgG1 or Lecanemab LALA-PG (Fig. 2f). Notably, Aβ42 is the pre-
dominant Aβ species in AppNL-G-F mice24. A significant reduction in 
insoluble Aβ38 levels was also observed in Lecanemab-treated mice 
compared to IgG1-treated mice (Fig. 2f), while soluble Aβ38 levels were 
significantly reduced in Lecanemab-treated mice compared to those 
treated with Lecanemab LALA-PG (Fig. 2g). No changes were observed 
in insoluble Aβ40 levels (Fig. 2f,g). Our AppNL-G-F Csf1rΔFIRE/ΔFIRE mice 
lack a mature adaptive immune system to allow colonization of the 
human brain with xenografted human microglia. To demonstrate that 
Lecanemab’s effect on plaque load is not hampered by the presence 
of adaptive immune cells, we repeated the experiments in a cohort 
of immunocompetent AppNL-G-F mice treated with mAb158 (a mouse 
version of Lecanemab), its engineered LALA-PG variant and a control 
mouse IgG2a (Fig. 2h). After 8 weeks of treatment, mAb158 signifi-
cantly decreased Aβ levels as measured by MSD (Fig. 2i,j), whereas the 
LALA-PG mutation eliminated the antibody-mediated Aβ clearance 
effect in this model with an intact mouse immune system. Finally, we 
demonstrated the essential role of microglia in Lecanemab-mediated 
plaque clearance as AppNL-G-F Csf1rΔFIRE/ΔFIRE mice that did not receive 
xenotransplantation (Fig. 2k) showed no impact from Lecanemab 
on plaque load (Fig. 2l–p). Collectively, these findings demonstrate 
that Lecanemab attenuates Aβ pathology in vivo through Fc-mediated 
microglial effector functions.
We then evaluated the impact of Lecanemab on microglial phago-
cytosis of Aβ fibrils. In an in vitro assay using cryosections from AppNL-G-F 
mouse brains (Extended Data Fig. 3a), sections were incubated for 
1 h with control IgG1, Lecanemab or Lecanemab LALA-PG14. Subse-
quently, human-derived microglial cells16 were added and, after 3 
days, amyloid plaque area was quantified using the pan-Aβ antibody 
82E1 (Extended Data Fig. 3b). Lecanemab treatment sections exhibited 
a significantly reduced Aβ-plaque load relative to those exposed to 
control IgG1 or Lecanemab LALA-PG (Extended Data Fig. 3c). Nota-
bly, in the absence of microglia, no plaque clearance was observed 
(Extended Data Fig. 3d), confirming that Lecanemab facilitates 
microglia-mediated Aβ clearance in vitro. To validate these findings 
in vivo, a cohort of AppNL-G-F mice xenotransplanted with human micro-
glia was treated with either Lecanemab or IgG1 from 6 to 8 months of 
age. After the treatment, the mice received an intraperitoneal injection 
of Methoxy-X04, a fluorescence probe that crosses the blood–brain bar-
rier to stain Aβ25. Three hours after injection, human CD45⁺ microglia 
were collected and the proportion of Methoxy-X04⁺ cells was quanti-
fied by flow cytometry (Fig. 3a and Extended Data Fig. 3f). Lecanemab 
treatment resulted in a significant increase in Aβ uptake by hCD45⁺ 
microglia, particularly within the CD68high subset (Fig. 3b,c).
Given that increased phagocytosis may be detrimental if non-
specific—for instance, by leading to the removal of synapses in the 
proximity of plaques9—we assessed the density of the presynaptic 
marker Synaptophysin, the postsynaptic marker Homer1, and their 
overlap (synaptic puncta) in the peri-plaque area (defined as 5 µm from 
the X-34 edges; Fig. 3d). Synaptophysin (Fig. 3e) and synaptic puncta 
densities (Fig. 3g) remained unchanged, and we found a small but sig-
nificant increase in postsynaptic density in Lecanemab-treated mice 
compared to IgG1-treated and Lecanemab LALA-PG-treated animals 
(Fig. 3f). These findings suggest that Lecanemab-induced phagocytosis 
is specific to Aβ. We further investigated the downstream effects of 
reduced plaque load on Aβ-related pathologies. Lecanemab treatment 
significantly decreased neuritic pathology, as indicated by LAMP1 
staining across the total brain area (Fig. 3h,i). However, the ratio of 
LAMP1-positive area to amyloid plaque load was unchanged (Fig. 3j), 
suggesting that the reduction in dystrophic neurites is an indirect 
consequence of decreased plaque load.
Lecanemab remodels microglial transcriptome to activate 
clearance pathways
Microglia clear amyloid plaques effectively only when Lecanemab 
is present, suggesting that Fc engagement modifies their function-
ality. To investigate the mechanisms underlying plaque clearance 
with greater resolution, we performed a single-cell transcriptomic 
profiling of human microglia using the 10x Genomics platform, 
achieving deeper gene expression coverage than through spatial tran-
scriptomics. Because our data indicated that Lecanemab LALA-PG 
strongly accumulates on Aβ-plaques and affects microglial responses 
(Fig. 1b,c), we compared microglia treated with Lecanemab to those 
treated with a control IgG1. After quality control and removal of mac-
rophages (Extended Data Fig. 4a–d), a differential gene expression 
analysis between IgG1-treated and Lecanemab-treated human micro-
glia revealed approximately 300 significantly differentially expressed 
genes (Fig. 4a). Consistent with our spatial transcriptomics results, 
upregulated genes were enriched for terms associated with the phago-
some pathway and antigen presentation (Extended Data Fig. 4e). 
Additionally, we identified genes enriched for processes related to 
interferon response, metabolism and the unfolded protein response 
(Extended Data Fig. 4e).
Although we observed changes in gene expression levels, their 
magnitude is relatively subtle. Furthermore, Lecanemab’s efficacy does 
not appear to be driven by significant shifts in specific cell state popu-
lations, which primarily reflect broad transcriptional changes, such 
as the disease-associated microglia (DAM)/human leukocyte antigen
- 第6页主要提供仑卡奈单抗相关英文材料。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
(HLA) state (Fig. 4b,c and Extended Data Fig. 4f). This insight prompted 
us to investigate whether the gene set induced by Lecanemab is more 
specifically targeted. To do so, we performed weighted gene coexpres-
sion network analysis (WGCNA) and identified 14 modules of coex-
pressed genes (Extended Data Fig. 5a–c and Supplementary Table 1). 
GSEA revealed that five modules were significantly downregulated 
and six modules were significantly upregulated after the Lecanemab 
treatment (Fig. 4d). Among the upregulated modules (Fig. 4e and 
Supplementary Table 2), the yellow module was enriched for interferon 
genes, the red module for unfolded protein and protein folding genes, 
Counts (human CD45+
 microglia)
Comp-V450-A: Methoxy-X04
2.5K
103
104
2.0K
1.5K
1.0K
0
0
500
IgG1 Lec
Lec
LALA-PG
0
0.2
0.4
0.6
0.8
1.0
Synaptophysin (count per
µm2) X-34+ 5 µm area
0
0.1
0.2
0.3
0.4
0.5
Synaptic puncta (count per
 µm2) X-34+ 5 µm area
0
5
10
15
20
IBA1 covered area (%)
Total brain 
0
10
20
30
40
50
LAMP1 covered area (%)
Peri-plaque region (X-34+ 10 µm)
d
e
f
g
No synaptic loss
IgG1
Lecanemab
Lecanemab LALA-PG
X34
Synaptophysin
Homer 1
X34
Synaptophysin
Homer 1
X34
Synaptophysin
Homer 1
Synaptophysin
Synaptophysin
Homer 1
Homer 1
Synaptophysin
Synaptophysin
Homer 1
Homer 1
Synaptophysin
Synaptophysin
Homer 1
Homer 1
X34
X34
Synaptic puncta
X34
X34
Synaptic puncta
X34
X34
Synaptic puncta
h
i
j
k
Dystrophic neurites
Aβ phagocytosis
a
b
c
IgG1
Lecanemab
Lecanemab LALA-PG
Microglia
Dystrophic neurites
LAMP1
X34
LAMP1
X34
LAMP1
X34
IBA1
IBA1
IBA1
1 mm
1 mm
1 mm
1 mm
1 mm
250 µm
250 µm
10 µm
10 µm
10 µm
10 µm
10 µm
10 µm
10 µm
10 µm
10 µm
250 µm
1 mm
Males
Females
Males
Females
Males
Females
0
0.5
1.0
1.5
2.0
2.5
% Methoxy-X04+
Human microglia (hCD45+)
0.0402
IgG1
Lec
IgG1 Lec
0
10
20
30
40
% Methoxy-X04+
Human microglia 
(CD45+ CD68high)
0.0098
0
0.5
1.0
1.5
Homer1 (count per µm2)
X-34+ 5 µm area
0.0543
0.0051
IgG1 Lec
Lec
LALA-PG
IgG1 Lec
Lec
LALA-PG
IgG1 Lec
Lec
LALA-PG
IgG1 Lec
Lec
LALA-PG
IgG1 Lec
Lec
LALA-PG
0
0.5
1.0
1.5
2.0
LAMP1 covered area (%)
Total brain
0.0401
0.0167
Fig. 3 | Lecanemab induces phagocytosis of Aβ and alleviates downstream 
consequences of Aβ pathology through Fc-mediated microglial effector 
functions. a, Flow cytometry analysis of Methoxy-X04+ cells within the hCD45+ 
population (microglia) after 8 weeks of Lecanemab (red) or IgG1 (black) 
treatment. The x axis represents Methoxy-X04 fluorescence intensity, while the y 
axis shows the number of cells. The overlaid histograms (black and red) highlight 
differences in Methoxy-X04 staining levels. b, Percentage of X04+ microglia 
(CD45+) isolated from IgG1 or Lecanemab-treated mice (unpaired two-sided 
t-test; IgG1, n = 8 mice; Lec, n = 7 mice). c, Percentage of X04+ microglia (CD45+, 
CD68high) isolated from IgG1 or Lecanemab-treated mice (unpaired two-sided 
t-test; IgG1, n = 8 mice; Lec, n = 7 mice). d, Representative super-resolution 
confocal images of synaptic loss surrounding X-34+ plaques in IgG1-treated, 
Lecanemab-treated and Lecanemab LALA-PG-treated xenotransplanted mice. 
Synaptic puncta were defined as synaptophysin (magenta) and Homer1 (green) 
immunoreactive puncta (white) around X-34+ plaques (cyan). Scale bar = 10 µm. 
e–g, Quantification of synaptophysin (one-way ANOVA, NS; e), Homer1 (one-way 
ANOVA, P = 0.044; f) and synaptic puncta (one-way ANOVA, NS; g), in peri-plaque 
area (defined as 5 µm from the X-34 edges; IgG1, n = 10 mice; Lec, n = 12 mice; Lec 
LALA-PG, n = 9 mice). h, Representative confocal images for IBA1 (magenta), 
X-34 (yellow) and LAMP1 (blue) in sagittal brain sections from AppNL-G-F Csf1rΔFIRE/ΔFIRE 
mice xenotransplanted with human-derived microglia and treated with IgG1, 
Lecanemab and Lecanemab LALA-PG; scale bars = 1 mm, insets = 250 µm. The 
area of LAMP1 was assessed in the 10-µm rings surrounding X-34 (peri-plaque 
region) and then divided by the area of the brain section or the peri-plaque area. 
i,j, Quantification of LAMP1 area expressed as percentage of the total brain 
section (i) and the peri-plaque area (j); (i) one-way ANOVA (P = 0.0091) and (j) 
one-way ANOVA (NS; IgG1, n = 10 mice; Lec, n = 12 mice; Lec LALA-PG, n = 9 mice). 
k, Quantification of IBA1 area expressed as percentage of the total brain section 
(Kruskal–Wallis test, NS; IgG1, n = 10 mice; Lec, n = 12 mice; Lec LALA-PG, n = 9 
mice). Mean ± s.e.m. shown for each group and points represent individual 
animals. Square symbols, males; triangle, females.
- 第7页主要提供仑卡奈单抗相关的疗效结果、作用机制信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
the salmon module for antigen presentation genes, the black module 
for mitochondrial and immune signaling genes and the blue module 
for metabolism genes, particularly those involved in oxidative phos-
phorylation and aerobic respiration. The pink module, although not 
associated with a specific functional signature in gene ontology (GO) 
databases, was enriched for SPP1, LGALS1, CTSD and ITGAX, core genes 
of DAM/HLA, as well as the protective axon-tract-associated microglia 
(ATM) and proliferative-region-associated microglia (PAM) identified 
during early microglia development26,27 (Fig. 5a, Extended Data Fig. 5d 
and Supplementary Table 3). Notably, SPP1 (encoding osteopontin 
(OPN)) is also the most strongly upregulated gene in both our single-cell 
RNA sequencing (scRNA-seq) and spatial DE analyses. SPP1 is implicated 
in phagocytosis26,28 and has been linked to a protective response in 
developing microglia26. Although SPP1 and other pink module genes 
are markers of DAM/HLA16, which typically accumulate around amyloid 
plaques without clearing them, our findings suggest that Lecanemab 
induces even higher expression of these genes, which activate clear-
ance programs that are not fully engaged in DAM/HLA. Finally, in con-
trast to reports that Aducanumab—another anti-Aβ antibody—induces 
canonical inflammatory genes (Tnf, Il1b, Nfkb)6,8, Lecanemab-treated 
microglia exhibited reduced expression of the inflammatory brown 
module (Fig. 4e and Supplementary Table 2).
We then used our functional WGCNA modules generated on the 
scRNA-seq data to interpret changes in the spatial transcriptomic 
data relative to plaque proximity. Notably, two key modules iden-
tified as upregulated in the single-cell GSEA, the yellow module 
(interferon-related) and the red module (unfolded protein response), 
do not seem to be spatially associated with plaques, although sig-
nificantly enriched globally in the Lecanemab TDs compared to the 
Lecanemab LALA-PG TDs (Extended Data Fig. 5f,g). On the other hand, 
the pink module (enriched for SPP1) was the most significantly enriched 
in plaque-associated TDs (Fig. 5b,c), followed by modules associated 
d.
ITM2B
S100A9
SPP1
HSPA5
S100A8
MS4A7
IL3RA
CALR
FCGRT
LINC00996
C1QB
TPT1
VSIG4
IFI6
IFNGR1
P2RY12
HSP90B1
B2M
EEF1A1
RGS10
BST2
ITM2C
MT2A
P2RY13
ABCG2
IFITM3
DHRS9
TYMP
ISG15
MS4A6A
LTC4S
HMGB1
RPL34
TMEM176B
TMIGD3
GPR183
HLA−DRA
PNRC1
ZFP36L1
VMP1
TMSB10
IPCEF1
IFI44L
ID2
S100A11
MRC1
DNAJB1
LAP3
JUN
CD14
HSPA1B
KLF2
0
20
40
60
80
−0.25
0
0.25
0.50
log2(FC)
−log10(Padj) 
Downregulated (166)
NS
Upregulated (126)
Lec vs. IgG1
Direction (Padj < 0.05)
a
7.41 × 10
−19 (***)
2.49 × 10
−7 (***)
1.55 × 10
−23 (***)
1.18 × 10
−4 (***)
1.90 × 10
−2 (**)
5.92 × 10
−11 (***)
6.06 × 10
−3 (**)
4.52 × 10
−4 (***)
1.10 × 10
−6 (***)
8.57 × 10
−12 (***)
2.15 × 10
−23 (***)
Yellow
Red
Salmon
Black
Pink
Blue
Greenyellow
Brown
Turquoise
Magenta
Green
−3
−1
1
3
NES
GSEA Lec vs. IgG1: WGCNA modules
RM
HM
CRM
Prolif
DAM
IRM C3−high
tCRM
HLA
Cluster
HM
RM
tCRM
CRM
DAM
IRM
HLA
C3−high
Prolif
Treatment
Lec
IgG1
Prolif
C3high
HLA
IRM
DAM
CRM
tCRM
RM
HM
−2
−1
0
1
2
log OR
0.89 (0.52−1.52)
0.85 (0.64−1.14)
0.76 (0.52−1.09)
1.05 (0.60−1.85)
1.24 (0.93−1.66)
1.62 (0.62−4.22)
0.72 (0.36−1.46)
1.13 (0.76−1.69)
1.32 (0.76−2.30) 0.67
0.29
0.16
0.87
0.16
0.33
0.38
0.55
0.33
OR 
(95% CI)
P
UMAP 1
UMAP 2
d
e
c
b
Lysosomal lumen acidification (BP)
Lysosome organization (BP)
Lytic vacuole organization (BP)
Regulation of lysosomal lumen pH (BP)
Vacuolar acidification (BP)
ITM2B
C1QC
CST3
FCGRT
FOLR2
CD81
ALOX5AP
GPR34
LAPTM5
RNASET2
CSF1R
MRC1
SLCO2B1
GAL3ST4
LINC00996
OTULINL
ABCG2
ADGRG1
SELPLG
SIGLEC10
MALAT1
MAF
P2RY12
ATM
FYB1
PLXDC2
ITPR2
SLC4A7
IL6ST
DDX17
FOS
DUSP1
IER2
KLF2
CCL3L1
JUNB
GADD45B
CCL3
FOSB
JUN
TREM2
CD68
DNASE2
GRN
CD53
CTSL
PPT1
TIMP2
LAMP2
LRPAP1
TMSB4X
FTL
RPLP1
RPS18
RPL41
RPS27
RPL26
RPS12
RPL37
RPL13
CD9
SPP1
LGALS1
CD83
ASAH1
PDPN
LIPA
OLR1
CXCR4
SLC1A3
MT −ATP6
MT −CO3
MT −CO2
MT −ND3
MT −CO1
MT −CYB
MT − ND4
MT −ND1
MT −ND2
MT −ND5
HLA −DRA
HLA −DPA1
HLA −DRB5
HLA −DRB1
HLA −DPB1
HLA −DQB1
CD74
HLA −DMA
HLA −DMB
PLA2G7
HSP90B1
CALR
HSPA5
PPIB
PDIA3
PDIA6
SDF2L1
MANF
HSP90AB1
HSP90AA1
IFIT3
IFIT1
ISG15
IFI44L
IFI6
RSAD2
MX1
IFIT2
IFITM3
MX2
Amyloid−beta binding (MF)
Neg. regulation of glycoprotein metabolic process (BP)
Serine hydrolase activity (MF)
Serine-type peptidase activity (MF)
Signaling receptor activity (MF)
0
0.5
1.0
1.5
Green
Cargo receptor activity (MF)
Glycosaminoglycan binding (MF)
Molecular transducer activity (MF)
Signaling receptor activity (MF)
Transmembrane signaling receptor activity (MF)
Magenta
ATP-dependent activity, acting on DNA (MF)
Chromatin binding (MF)
Chromatin organization (BP)
Histone binding (MF)
Histone modification (BP)
0
5
10
0
2
4
Turquoise
Cellular response to tumor necrosis factor (BP)
DNA-binding transcription activator activity (MF)
DNA-binding transcription act, RNA pol. II−specific (MF)
Regulation of neuron death (BP)
Response to tumor necrosis factor (BP)
Green-yellow
0
2
4
6
Brown
Aerobic respiration (BP)
Cytoplasmic translation (BP)
Oxidative phosphorylation (BP)
Structural constituent of ribosome (MF)
Structural molecule activity (MF)
Chemokine binding (MF)
Coreceptor activity (MF)
Extracellular matrix binding (MF)
Immune receptor activity (MF)
Integrin binding (MF)
0
0.5
1.0
0
25
50
75
Blue
Pink
ATP-dependent protein folding chaperone (MF)
Protein folding (BP)
Protein folding chaperone (MF)
Response to topologically incorrect protein (BP)
Unfolded protein binding (MF)
0
5
10
15
20
25
Lipoprotein particle receptor activity (MF)
Low-dens. lipoprotein particle receptor act. (MF)
Molecular transducer activity (MF)
Signaling receptor activity (MF)
Transforming growth factor β binding (MF)
Red
0
1
2
3
4
Black
Defense response to symbiont (BP)
Defense response to virus (BP)
Innate immune response (BP)
Negative regulation of viral process (BP)
Response to virus (BP)
0
10
20
30
40
Yellow
Antigen processing and presentation of exogenous peptide
 antigen via MHC class II (BP)
MHC class II protein complex assembly (BP)
MHC class II protein complex binding (MF)
MHC protein complex binding (MF)
Peptide antigen assembly with MHC class II protein complex (BP)
0
5
10
15
20
−log
10(FDR)
0
1
2
3
−log
10(FDR)
Salmon
Fig. 4 | Transcriptomic changes in human microglia treated with Lecanemab. 
a, Volcano plots showing a gene expression comparison between Lecanemab-
treated and IgG1-treated human microglia (n = 6 mice per condition). The 
number of significant genes per condition is reported in brackets. Padj 
threshold < 0.05 (two-sided Wilcoxon rank-sum test, P values adjusted with 
Bonferroni correction based on the total number of genes in the dataset, NS). b, 
UMAP plot visualizing 22,420 (10,850 IgG1, 11,570 Lecanemab) human microglial 
cells after the removal of macrophages. Cells are colored according to clusters 
identified. The assignment of different clusters to distinct cell types or states is 
based on the previous experimental data from our laboratory14. c, OR and 95% CI 
for the differential abundance of cell states between Lecanemab-treated (n = 6 
mice) and IgG1-treated group (n = 6 mice) using MASC analysis. Points indicate 
the estimated OR, with horizontal lines representing the 95% CI. Two-sided 
tests were performed, and exact P values are shown. No significant changes 
in the proportion of cell states are detected between IgG1 and Lecanemab-
treated microglia. d, NES of significantly enriched (Padj < 0.05) WGCNA modules 
between IgG1 and Lecanemab-treated cells, as identified by GSEA with Padj values 
indicated. Two-sided P values were adjusted using the BH correction (**Padj < 0.01, 
***Padj < 0.001). e, Functional annotations based on GO pathway analyses (MF 
and BP) using an overrepresentation analysis (one-sided hypergeometric test). 
Enrichment for a given ontology is shown by q score, with thresholds indicated by 
red line (q < 0.1) and black line (q < 0.05). The top ten hub genes are shown based 
on the module eigengene-based connectivity (kME). P values were adjusted 
using the BH correction. OR, odds ratio; CI, confidence interval; MF, molecular 
function; BP, biological process; MASC, mixed-effects modeling association of 
single cells.
- 第8页主要提供仑卡奈单抗、6个月相关的疗效结果、生物标志物信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
with antigen presentation (salmon), lysosome (green-yellow) and 
metabolism (blue; Extended Data Fig. 5e). Consistent with our tran-
scriptomic data, OPN expression was elevated in IBA1+ microglia 
surrounding X-34+ and 82E1+ plaques in Lecanemab-treated mice com-
pared to those treated with IgG1 or Lecanemab LALA-PG (Fig. 5d–f). 
However, no significant increase in IBA1+ area around X-34+ plaques was 
observed (Fig. 5g), suggesting that the rise in OPN reflects an increased 
expression per cell rather than a higher number of OPN-expressing 
cells. This observation aligns with our results from the scRNA-seq DE 
analysis (Fig. 4a).
OPN-driven Aβ clearance in Lecanemab-treated microglia
The proximity of OPN+ cells to amyloid plaques suggests that 
Lecanemab restores protective phagocytic functions in human micro-
glia near Aβ deposits. To test this, we used our in vitro plaque clear-
ance system (Extended Data Fig. 3a–e) and stimulated human-derived 
microglia with increasing concentrations of human OPN (Fig. 5h,i). 
Remarkably, at the highest concentration tested, OPN stimulation 
significantly decreased the area covered by the pan-Aβ antibody 82E1 
(Fig. 5j), demonstrating that OPN, one of the main factors induced by 
Lecanemab, promotes Aβ clearance.
Discussion
Lecanemab stands as the most successful Aβ-plaque-clearing antibody 
in clinical use2,13. Our study demonstrates that its efficacy critically 
depends on the presence of microglia and the engagement of Fc effector 
functions, which activate a targeted amyloid-clearing program in these 
cells. Transcriptomic and functional analyses reveal that Lecanemab 
induces a distinct program in microglia that enhances phagocytosis 
and lysosomal activity without triggering the synaptophagy observed 
in other studies9. This selective activation correlates with a reduction 
in neuritic pathology, potentially underpinning the modest clinical 
improvements observed with Lecanemab.
Among the Lecanemab-induced upregulated genes, several are 
highly relevant to AD. For instance, the MS4A gene family, including 
MS4A6A, is strongly associated with AD risk and functions upstream of 
TREM2 (ref. 29). Upregulation of HSPA5, an ER stress marker, may indi-
cate enhanced Aβ uptake in Lecanemab-treated microglia, triggering 
the unfolded protein response30. Moreover, SPP1 was the most strongly 
upregulated gene in both our scRNA-seq and spatial transcriptomic 
differential gene expression analyses. It is important to note, however, 
that the overall magnitude of changes in expression levels is relatively 
limited, which, we postulate, may be due to the fact that the changes in 
our microglia are primarily localized to those in close proximity to the 
plaques. For this reason, despite acknowledging the potential biases 
of cell-level DE analyses, we believe a pseudobulk approach, which 
has been shown to better control for false discoveries31, would mask 
changes in distinct cell populations.
Nevertheless, despite the subtlety of these changes, our experi-
mental work clearly demonstrates that Lecanemab confers a func-
tional ability to clear plaques. To further extend our investigation 
of the transcriptional programs associated with this ability, we per-
formed WGCNA, which corroborated our GSEA by revealing that 
Lecanemab-induced genes cluster into distinct modules associated 
with the interferon response, antigen presentation, metabolism 
and the unfolded protein response. Strikingly, when we leveraged 
our functional WGCNA modules to analyze spatial transcriptomic 
changes relative to plaque proximity, we identified the pink module 
(enriched for SPP1) as significantly enhanced around Aβ plaques in the 
Lecanemab-treated samples, further supporting our scRNA-seq find-
ings. SPP1, a key hub gene in this module, is a well-established marker 
of DAM/HLA16, cells that accumulate around amyloid plaques without 
effectively clearing them. Its further induction by Lecanemab suggests 
the activation of clearance pathways that extend beyond the conven-
tional DAM state. This is supported by our findings that exogenous OPN 
enhances the amyloid clearance capacity of human microglia. Future 
studies should investigate whether additional genes and pathways 
within the Lecanemab-induced pink module contribute to amyloid 
clearance, and whether this transcriptional profile represents an ampli-
fication of known DAM/HLA microglia cell states or defines a distinct 
microglial phenotype with enhanced amyloid-clearing capacity. In any 
event, phagosome/phagocytosis emerged as one of the top pathways 
in both scRNA-seq and spatial GSEA analyses, and we functionally 
validated this signature by demonstrating that Lecanemab enhances 
Aβ phagocytosis in vivo and in vitro. Collectively, these findings indi-
cate that a limited set of genes is sufficient to reprogram microglia for 
efficient amyloid clearance.
Our work highlights the unique advantages of our xenograft 
human/mouse chimeric model, which enables direct in vivo evalua-
tion of the unmodified human antibody on human microglia. Although 
the Rag2−/− background necessary to prevent graft rejection precludes 
analysis of adaptive immunity, parallel experiments using a mouse 
variant of Lecanemab in immune-competent animals confirmed that 
amyloid clearance is not qualitatively different in the presence of 
adaptive immunity. This is particularly important given the distinct 
responses of human versus mouse microglia to amyloid plaques and 
the low sequence conservation of key AD risk genes like MS4A6A16 
between species.
It is tempting to speculate that differences in the clinical efficacy of 
anti-Aβ antibodies may, in part, reflect their distinct impacts on micro-
glial inflammatory responses. For example, while Aducanumab has been 
associated with robust pro-inflammatory activation8, our data suggest 
Fig. 5 | OPN/SPP1, one of the main factors induced by Lecanemab treatment, 
promotes Aβ clearance. a, Heatmap displaying the significance of enrichment 
of marker genes of previously reported microglial cell states16,26,27 in the pink 
WGCNA module, as assessed by a one-sided hypergeometric overlap test. Color 
intensity reflects enrichment significance, represented as −log10(FDR), with 
darker red indicating stronger enrichment. Respective BH Padj values for the 
enrichments are specified. The list of shared genes with significantly enriched 
states is outlined in Supplementary Table 3 (***Padj < 0.001). b, NES of WGCNA 
modules in Lecanemab TDs (40-μm hexbin pseudospots) with respect to 
distance to pathology, as identified by GSEA, performed on the DE analysis in 
Fig. 1e, with Padj values indicated. Two-sided P values were adjusted using the BH 
correction (**Padj< 0.01, ***Padj < 0.001). c, Cortical TDs in Lecanemab-treated 
mice colored based on their relative expression of genes belonging to the pink 
module (purple, low expression; yellow, high expression) and overlayed with 
plaque ROIs (white). ESs were obtained using Scanpy’s ‘score_genes()’ function. 
Please note the significant enrichment of the module in TDs close to Aβ plaques, 
as quantified in b. d, Representative confocal images of cortical X-34+ and 82E1+ 
plaques surrounded by OPN+ microglia in IgG1-treated, Lecanemab-treated 
and Lecanemab LALA-PG-treated mice. Scale bar = 25 µm. e,f, Quantification of 
the area of OPN+ area within IBA1+ cells around X-34+ (e) and 82E1+ plaques (f) in 
IgG1-treated and Lecanemab-treated mice; (e) one-way ANOVA (P = 0.0008) and 
(j) one-way ANOVA (P = 0.0007; IgG1, n = 10 mice; Lec, n = 12 mice; Lec LALA-PG, 
n = 9 mice). g, Quantification of the area covered by IBA1+ cells around X-34+ 
plaques; one-way ANOVA (NS) (IgG1, n = 10 mice; Lec, n = 12 mice; Lec LALA-PG, 
n = 9 mice). h, Schematic representation of the in vitro plaque clearance assay 
paradigm used to study Aβ clearance in response to OPN stimulation. Human-
derived microglial cells were plated onto sagittal cryosections from 6-month-
old AppNL-G-F mice, followed by the treatment with increasing concentrations of 
human OPN (17, 50, 150, 450 and 1,350 ng ml−1). After 3 days, Aβ plaque coverage 
was quantified using the pan-Aβ antibody 82E1. Panel h was created with 
BioRender.com. i, Representative confocal images of 82E1 (Aβ, cyan) and CD9 
(human microglia, magenta) immunoreactivity in AppNL-G-F brain cryosections 
after OPN stimulation. Scale bar = 1 mm; inset = 200 µm. j, Quantification of 
82E1 covered area (relative to no OPN) in sections plated with or without human 
microglia; modified chi-squared method (n = 3 independent experiments; 
P = 0.03). Graphs show mean ± s.e.m. and points represent individual animals 
(e–g) or independent experiments, with each being the average of one to four 
cryosections (j). Square symbols, males; triangles, females.
- 第9页主要提供仑卡奈单抗、6个月相关的安全性、作用机制信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
that Lecanemab elicits a more restrained immune activation, which may 
underlie its relatively greater clinical benefit. This contrast is intriguing 
but should be interpreted with caution, as prior studies were conducted 
in mouse microglia. In our study, Lecanemab-treated microglia upregu-
lated interferon-responsive genes but did not broadly induce classical 
pro-inflammatory cytokines. Interestingly, interferon signaling has been 
implicated in brain endothelial dysfunction in AD32, suggesting that this 
pathway contributes to amyloid-related imaging abnormalities—the 
most impactful adverse events associated with Lecanemab. However, a 
key limitation of our model is its reduced capacity to capture vascular 
pathology or blood–brain barrier dysfunction, as App knock-in mice 
models do not show substantial vascular defects at the studied age33.
Given the central role of inflammation in immunotherapy, deci-
phering how Fc receptor-mediated microglial activation shapes 
responses in other central nervous system cell types remains a criti-
cal avenue for future research. Our findings also raise the possibility 
d
e
f
g
h
i
j
e.
Aβ plaques
Microglial OPN
OPN
IgG1
Lecanemab
X34
82E1
IBA1
OPN
X34
82E1
IBA1
OPN
Lecanemab LALA-PG
X34
82E1
IBA1
OPN
In vitro plaque clearance assay
spatial_um1
spatial_um2
Expression level of pink module genes
0
0.01
–0.01
0.02
0.03
0.04
c
3.28 × 10
−15
3.42 × 10
−12
2.36 × 10
−40
2.29 × 10
−11
1.01 × 10
−5
Pink
HM
IRM
CRM
DAM
HLA
RM
tCRM
PAM
ATM
−log10(FDR)
0
10
20
30
Gene set enrichment heatmap
GSEA: Lec TDs with respect to distance to pathology
***
***
***
***
***
Males
Females
Experiment 1
Experiment 2
Experiment 3
0
0.5
1.0
1.5
2.0
OPN+ area (% IBA1+)
Peri-plaque region
(82E1+ 5 µm)
0.0044
0.0018
0
10
20
30
40
50
IBA1+ area (%) 
Peri-plaque region
(X-34+ 15 µm)
IgG1
Lec
Lec
LALA-PG
IgG1
Lec
Lec
LALA-PG
IgG1
Lec
Lec
LALA-PG
0
1
2
3
4
5
OPN+ area (% IBA1+) 
Peri-plaque region
(X-34+ 15 µm)
0.0027
0.0032
25 µm
25 µm
25 µm
25 µm
25 µm
25 µm
25 µm
25 µm
25 µm
17
50
150
450
1,350
0
0.5
1.0
1.5
2.0
OPN (ng ml
–1)
82E1 covered area (%)
Relative to no OPN
P = 0.004
No OPN
82E1
hCD9
82E1
hCD9
Microglia
OPN (1,350 ng ml
–1)
No OPN
OPN (1,350 ng ml
–1)
82E1
1 mm
1 mm
1 mm
1 mm
200 µm
200 µm
200 µm
200 µm
hCD9
82E1
hCD9
No Microglia
b
a
2.32 × 10
−10 (***)
8.55 × 10
−5 (***)
5.93 × 10
−4 (***)
9.42 × 10
−5 (***)
9.70 × 10
−8 (***)
Pink
Salmon
Greenyellow
Blue
Green
Magenta
Red
Yellow
−2
−1
0
1
2
NES
WGCNA modules
AppNL-G-F brain
6 months
H9-derived microglia + human OPN
Confocal microscopy
82E1, hCD9
72 h
37 °C
No microglia
Microglia
Direction
Up near plaques
Down near plaques
2.32 × 10
−10 (***)
6.26 × 10
−3 (**)
1.93 × 10
−4 (***)
- 第10页主要是论文标题、作者和机构信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
that distinct FcγRs expressed by microglia (Extended Data Fig. 4g and 
Supplementary Table 4) may differentially mediate beneficial versus 
detrimental effects of antibody treatment. Alternatively, activation 
of Fc or complement receptors on border-associated macrophages 
by the Fc moiety of Lecanemab could also trigger harmful vascular 
responses34. Finally, Lecanemab may reduce peripheral immune cell 
infiltration by dampening central nervous system inflammation, poten-
tially contributing to its attenuation of pathology35,36. Dissecting these 
mechanisms will be essential to clarify the balance between therapeutic 
efficacy and adverse effects of anti-Aβ immunotherapy.
While we cannot rule out the possibility that other anti-Aβ anti-
bodies differentially influence microglia by binding to distinct Aβ 
species13, our findings support the notion that the precise nature of the 
Aβ protofibrils1 targeted by Lecanemab is less critical than its ability to 
engage amyloid plaques and then microglia through its Fc moiety. This 
may explain the comparable clinical impact of Donanemab, another 
FDA-approved antibody that targets a pyroglutamate-modified amy-
loid peptide in the amyloid plaque itself3. Effective amyloid clearance 
may be achieved if the antibody binds amyloid fibrils sufficiently to 
correctly position its Fc domain for microglial activation. This insight 
opens new avenues for therapeutic innovation, including the develop-
ment of small compounds linked to Fc fragments or the engineering of 
antibodies with enhanced effector functions and reduced complement 
activation, an approach extensively used in other medical fields37, to 
improve antibody treatment outcomes in AD.
Online content
Any methods, additional references, Nature Portfolio reporting sum-
maries, source data, extended data, supplementary information, 
acknowledgements, peer review information; details of author con-
tributions and competing interests; and statements of data and code 
availability are available at https://doi.org/10.1038/s41593-025-02125-8.
References
1. 
Lord, A. et al. An amyloid-β protofibril-selective antibody prevents 
amyloid formation in a mouse model of Alzheimer’s disease. 
Neurobiol. Dis. 36, 425–434 (2009).
2. 
Van Dyck, C. H. et al. Lecanemab in early Alzheimer’s disease. 
N. Engl. J. Med. 388, 9–21 (2022).
3. 
Karran, E. & de Strooper, B. The amyloid hypothesis in Alzheimer 
disease: new insights from new therapeutics. Nat. Rev. Drug 
Discov. 21, 306–318 (2022).
4. 
DeMattos, R. B. et al. A plaque-specific antibody clears existing 
β-amyloid plaques in Alzheimer’s disease mice. Neuron 76, 
908–920 (2012).
5. 
Sevigny, J. et al. The antibody aducanumab reduces Aβ plaques in 
Alzheimer’s disease. Nature 537, 50–56 (2016).
6. 
Cadiz, M. P. et al. Aducanumab anti-amyloid immunotherapy 
induces sustained microglial and immune alterations. J. Exp. Med. 
221, e20231363 (2024).
7. 
Carbone, F., Nencioni, A., Mach, F., Vuilleumier, N. & Montecucco, F. 
Evidence on the pathogenic role of auto-antibodies in acute 
cardiovascular diseases. Thromb. Haemost. 109, 854–868 
(2013).
8. 
Jung, H. et al. Anti-inflammatory clearance of amyloid-β by a 
chimeric Gas6 fusion protein. Nat. Med. 28, 1802–1812 (2022).
9. 
Sun, X.-Y. et al. Fc effector of anti-Aβ antibody induces synapse 
loss and cognitive deficits in Alzheimer’s disease-like mouse 
model. Signal Transduct. Target. Ther. 8, 30 (2023).
10. Bacskai, B. J. et al. Non-Fc-mediated mechanisms are involved in 
clearance of amyloid-β in vivo by immunotherapy. J. Neurosci. 22, 
7873–7878 (2002).
11. 
Garcia-Alloza, M. et al. A limited role for microglia in antibody 
mediated plaque clearance in APP mice. Neurobiol. Dis. 28, 
286–292 (2007).
12. Das, P. et al. Amyloid-β immunization effectively reduces amyloid 
deposition in FcRγ −/− knock-out mice. J. Neurosci. 23, 8532–8538 
(2003).
13. Fertan, E. et al. Lecanemab preferentially binds to smaller 
aggregates present at early Alzheimer’s disease. Alzheimers 
Dement. 21, e70086 (2025).
14. Lo, M. et al. Effector-attenuating substitutions that maintain 
antibody stability and reduce toxicity in mice. J. Biol. Chem. 292, 
3900–3908 (2017).
15. Schlothauer, T. et al. Novel human IgG1 and IgG4 Fc-engineered 
antibodies with completely abolished immune effector functions. 
Protein Eng. Des. Sel. 29, 457–466 (2016).
16. Mancuso, R. et al. Xenografted human microglia display diverse 
transcriptomic states in response to Alzheimer’s disease- 
related amyloid-β pathology. Nat. Neurosci. 27, 886–900 
(2024).
17. Baligács, N. et al. Homeostatic microglia initially seed and 
activated microglia later reshape amyloid plaques in Alzheimer’s 
disease. Nat. Commun. 15, 10634 (2024).
18. Rojo, R. et al. Deletion of a Csf1r enhancer selectively impacts 
CSF1R expression and development of tissue macrophage 
populations. Nat. Commun. 10, 3215 (2019).
19. Tucker, S. et al. The murine version of BAN2401 (mAb158) 
selectively reduces amyloid-β protofibrils in brain and 
cerebrospinal fluid of tg-ArcSwe mice. J. Alzheimers Dis. 43, 
575–588 (2014).
20. Chen, W.-T. et al. Spatial transcriptomics and in situ sequencing to 
study Alzheimer’s disease. Cell 182, 976–991 (2020).
21. Mallach, A. et al. Microglia-astrocyte crosstalk in the amyloid 
plaque niche of an Alzheimer’s disease mouse model, as 
revealed by spatial transcriptomics. Cell Rep. 43, 114216 
(2024).
22. Poovathingal, S. et al. Nova-ST: nano-patterned ultra-dense 
platform for spatial transcriptomics. Cell Rep. Methods 4, 100831 
(2024).
23. Espuny-Camacho, I. et al. Hallmarks of Alzheimer’s disease in 
stem-cell-derived human neurons transplanted into mouse brain. 
Neuron 93, 1066–1081 (2017).
24. Saito, T. et al. Single App knock-in mouse models of Alzheimer’s 
disease. Nat. Neurosci. 17, 661–663 (2014).
25. Grubman, A. et al. Transcriptional signature in microglia 
associated with Aβ plaque phagocytosis. Nat. Commun. 12, 3015 
(2021).
26. Lawrence, A. R. et al. Microglia maintain structural integrity 
during fetal brain morphogenesis. Cell 187, 962–980 
(2024).
27. Li, Q. et al. Developmental heterogeneity of microglia and brain 
myeloid cells revealed by deep single-cell RNA sequencing. 
Neuron 101, 207–223 (2019).
28. Li, S. & Jakobs, T. C. Secreted phosphoprotein 1 slows 
neurodegeneration and rescues visual function in mouse models 
of aging and glaucoma. Cell Rep. 41, 111880 (2022).
29. Deming, Y. et al. The MS4A gene cluster is a key modulator of 
soluble TREM2 and Alzheimer’s disease risk. Sci. Transl. Med. 11, 
eaau2291 (2019).
30. Soejima, N. et al. Intracellular accumulation of toxic turn 
amyloid-β is associated with endoplasmic reticulum stress in 
Alzheimer’s disease. Curr. Alzheimer Res. 10, 11–20 
(2013).
31. Murphy, A. E. & Skene, N. G. A balanced measure shows 
superior performance of pseudobulk methods in single-cell 
RNA-sequencing analysis. Nat. Commun. 13, 7851 (2022).
32. Jana, A. et al. Increased type I interferon signaling and brain 
endothelial barrier dysfunction in an experimental model of 
Alzheimer’s disease. Sci. Rep. 12, 16488 (2022).
- 第11页主要是论文标题、作者和机构信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
33. Tachida, Y. et al. Endothelial expression of human amyloid 
precursor protein leads to amyloid β in the blood and induces 
cerebral amyloid angiopathy in knock-in mice. J. Biol. Chem. 298, 
101880 (2022).
34. Uekawa, K. et al. Border-associated macrophages promote 
cerebral amyloid angiopathy and cognitive impairment through 
vascular oxidative stress. Mol. Neurodegener. 18, 73 
(2023).
35. Huang, X. et al. Clearance and transport of amyloid β by 
peripheral monocytes correlate with Alzheimer’s disease 
progression. Nat. Commun. 15, 7998 (2024).
36. Rosenzweig, N. et al. PD-1/PD-L1 checkpoint blockade 
harnesses monocyte-derived macrophages to combat cognitive 
impairment in a tauopathy mouse model. Nat. Commun. 10, 465 
(2019).
37. Damelang, T. et al. Impact of structural modifications of IgG 
antibodies on effector functions. Front. Immunol. 14, 1304365 
(2024).
Publisher’s note Springer Nature remains neutral with regard to 
jurisdictional claims in published maps and institutional affiliations.
Open Access This article is licensed under a Creative Commons 
Attribution 4.0 International License, which permits use, sharing, 
adaptation, distribution and reproduction in any medium or format, 
as long as you give appropriate credit to the original author(s) and the 
source, provide a link to the Creative Commons licence, and indicate 
if changes were made. The images or other third party material in this 
article are included in the article’s Creative Commons licence, unless 
indicated otherwise in a credit line to the material. If material is not 
included in the article’s Creative Commons licence and your intended 
use is not permitted by statutory regulation or exceeds the permitted 
use, you will need to obtain permission directly from the copyright 
holder. To view a copy of this licence, visit http://creativecommons.
org/licenses/by/4.0/.
© The Author(s) 2025
- 第12页主要提供仑卡奈单抗、8个月相关的疗效结果信息。: Nature Neuroscience
Article
https://doi.org/10.1038/s41593-025-02125-8
Methods
Antibodies: design, production and quality control
Variable domain amino acid sequences for Lecanemab were retrieved 
from the KEGG DRUG database (Supplementary Table 5). Heavy and 
light chains were cloned into a single human IgG1 expression vector 
(pTRIOZ-hIgG, InvivoGen). For Lecanemab, the production was initially 
done in-house, then outsourced to GenScript. Synthetic genes encod-
ing for the respective variable domains, preceded by the mouse Ig 
heavy leader signal (Twist Biosciences), were cloned into pTRIOZ-hIgG 
(Invivogen). The VL domain was cloned using the restriction enzymes 
AscI/BsiWI, and the VH domain using AgeI/NheI. The antibody encoding 
open reading frames were sequence confirmed by Sanger sequencing 
(Eurofins). Plasmid DNA was delivered to CHO cells (Thermo Fisher 
Scientific, A29127) by transient transfection according to the manufac-
turer’s protocol (CHOgro High Yield Expression System; Mirus Bio, MIR 
6270). Transfected CHO cells were cultured for 14 days in suspension 
on agitation at 32 °C. Two weeks after transfection, cell supernatants 
were collected and incubated overnight at 4 °C with AmMag Protein A 
Magnetic Beads (GenScript, L00939). The beads were collected using a 
magnetic separation rack and targeted antibodies were separated using 
the AmMag SA Plus system (GenScript, L01013). To abolish Fc effector 
function, the heavy chain of Lecanemab was designed to include the 
P329G substitution combined with L234A and L235A (LALA-PG). The 
light chain was the same as for Lecanemab (Supplementary Table 5). 
Production was outsourced to GenScript. As a control, we used the 
human IgG1 isotype control (Imtec Diagnostics, LT9005). Production of 
the mouse antibodies (mAb158 and mAb158 LALA-PG) was outsourced 
to GenScript. The amino acid sequence mAb158 was retrieved from 
patent US 8025878 B2, seq IDs 115 and 116. The LALA-PG mutations were 
designed according to the details discussed in ref. 15. As a control, we 
used the mouse IgG2a isotype control (Leinco, P381). The purity of the 
antibodies was estimated to be above 75% by densitometric analysis of 
the Coomassie Blue-stained SDS–PAGE gel under nonreducing condi-
tions. Binding to Aβ1-42 (rPeptide, A-1163-2) was confirmed by ELISA 
and Dot Blot as performed in refs. 38,39.
Human microglial progenitors and xenotransplantation
Human embryonic stem cells WA09 (H9, female), obtained from WiCell 
Research Institute (WA09; RRID, CVCL_9773), were cultured on Matrigel 
(VWR International, BDAA356277) with E8‑Flex medium (Thermo Fisher 
Scientific, A2858501) at 37 °C and 5% CO2. At 70–80% confluence, colo-
nies were dissociated with Accutase (Sigma-Aldrich, A6964) and aggre-
gated as embryoid bodies in U‑bottom 96‑well plates (10,000 cells 
per well) in mTeSR1 (STEMCELL Technologies, 15883465) plus BMP4 
(50 ng ml−1), VEGF (50 ng ml−1) and SCF (20 ng ml−1) for 4 days. Embryoid 
bodies were transferred to six‑well plates in X‑VIVO medium (Lonza, 
02-060Q) plus SCF (50 ng ml−1), M‑CSF (50 ng ml−1), IL‑3 (50 ng ml−1), 
FLT3 (50 ng ml−1) and TPO (5 ng ml−1) for 7 days, then switched to X‑VIVO 
plus FLT3 (50 ng ml−1), M‑CSF (50 ng ml−1) and GM‑CSF (25 ng ml−1) on 
day 11. Floating microglial precursors were collected on day 18 and 
resuspended in 1× DPBS (Gibco, 14190-144) at 2.5 × 105 cells per µl. P4 
pups received 5 × 105 cells intracerebrally as described in refs. 16,40,41. 
Cytokines were from PeproTech. Additional collections were obtained 
by returning embryoid bodies to X‑VIVO with FLT3, M‑CSF and GM‑CSF.
Mice and husbandry
All mice were housed in a specific pathogen-free facility under a 14-h 
light/10-h dark cycle, at an ambient temperature of 21 °C and 40–60% 
humidity, in groups of two to five animals, with food and water provided 
ad libitum. All experiments were conducted according to the protocols 
approved by the local Ethical Committee for Laboratory Animals of the 
KU Leuven (government license, LA1210579; ECD projects P125/2022 
and P132/2022), following the country and European Union guidelines.
AppNL-G-F mice (C57BL/6 background; strain Apptm3.1Tcs+; discussed in 
ref. 24, RIKEN; RRID, IMSR_RBRC06344) were used. These mice express 
amyloid precursor proteins (APP) at endogenous levels with a human-
ized Aβ sequence carrying the Swedish (NL, K670_M671delinsNL), 
Arctic (G, E693G) and Iberian (F, I716F) familial AD-causing mutations.
Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; Il2rgtm1.1Flv; Apptm3.1Tcs; Csf1Rem1Bdes mice 
(mixed C57BL/6, Balb/c background; named AppNL-G-F Csf1rΔFIRE/ΔFIRE mice) 
were generated in-house at KU Leuven as described in refs. 17,18. Briefly, 
homozygous mouse oocytes from Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; Il2rgtm1.1Flv; 
Apptm3.1Tcs crosses were micro-injected with reagents targeting the 
FMS-intronic regulatory sequence (FIRE sequence) in the intron 2 of 
the mouse Csf1R gene18. Ribonucleoproteins containing 0.3-μM puri-
fied Cas9HiFi protein 0.3-μM crRNA (5’GTCCCTCAGTGTGTGAGA3’ 
and 5’CAATGAGTCTGTACTGGAGC3’) and 0.3-μM trans-activating 
crRNA (Integrated DNA Technologies) were injected into the pronu-
cleus of 120 embryos by the CBD Mouse Expertise Unit of KU Leuven. 
One female founder with the expected 428-bp deletion was selected 
and crossed with a Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; Il2rgtm1.1Flv; Apptm3.1Tcs male 
and the progeny were interbred to obtain a Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; 
Il2rgtm1.1Flv; Apptm3.1Tcs; Csf1Rem1Bdes. For maintaining the colony, AppNL-G-F 
Csf1rΔFIRE/ΔFIRE males were crossed with AppNL-G-F Csf1rΔFIRE/WT females, as 
five times homozygous females tend to take less care of their progeny. 
For grafting, AppNL-G-F Csf1rΔFIRE/ΔFIRE pups were fostered to CD1 mothers 
to facilitate their survival.
An extra cohort of Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; Il2rgtm1.1Flv; Apptm3.1Tcs 
mice (AppNL-G-F mice; mixed C57BL/6, Balb/c background; generated 
at KU Leuven as previously described in ref. 16) was xenotransplanted 
with human microglia16, treated between 6 and 8 months of age and 
used for the in vivo phagocytosis assay. To establish proper gating for 
this experiment, we also included Rag2tm1.1Flv; Csf1tm1(CSF1)Flv; Il2rgtm1.1Flv; 
Appem1Bdes mice (AppHu mice; mixed C57BL/6, Balb/c background; gener-
ated at KU Leuven as previously described in ref. 16) as negative con-
trols. These mice have humanized Aβ sequence42 and do not develop 
Aβ pathology. Like AppNL-G-F mice, they were xenotransplanted with 
human microglia. Because neither AppHu nor AppNL-G-F mice are geneti-
cally devoid of endogenous mouse microglia, these cells were depleted 
before transplantation by inhibiting the CSF1 receptor using BLZ945 
(Asclepia Outsourcing Solutions, BLZ945) at a dose of 200 mg kg−1 on 
postnatal days 2 and 3 (P2 and P3), as previously described in ref. 16.
Study design
To unravel microglial contributions to anti-Aβ immunotherapy, we 
used several experimental approaches, summarized below. To calcu-
late the number of mice needed to analyze the impact of treatment 
on amyloid pathology using immunofluorescence and MSD ELISA, 
we conducted a priori power analyses using G*Power (sample sizes 
noted throughout the test). The expected effect size was based on 
previous publications1,6,17. The α level and power were set at 5% and 80%, 
respectively, and a t-test was used for the sample size calculation. No 
statistical methods were used to predetermine sample sizes for the 
scRNA-seq analysis, but our sample sizes were estimated based on the 
previous publications16,41,43. Mice were randomly assigned to conditions 
and conditions were randomized to account for potential ordering 
effects. To avoid litter bias in the mouse experiments, experimental 
groups were composed of animals from different litters randomly 
distributed. All analyses were conducted blindly to the experimental 
condition, and we used an automated GA3 recipe in the NIS-Elements 
AR software for image analysis.
We excluded one mouse from the scRNA-seq datasets due to 
extremely low cell counts (likely due to technical errors). For ELISA 
data, statistical outliers (caused by technical errors) were identified 
using the ROUT test in Prism 10 (Q = 1%) and excluded from further 
analysis. No additional mice were excluded from the study.
 1. 
To analyze the distribution of the human antibodies in the 
brain parenchyma, a cohort of AppNL-G-F Csf1rΔFIRE/ΔFIRE mice 
xenotransplanted with human microglia was treated with either


【正式资产锚点】
- 论点规则: THESIS_R1
- 论点规则: THESIS_R2
- 论点规则: THESIS_R3
- 论点分类: 主张_证据
- 论点分类: 主张_证据
- 论点分类: 主张_证据 / 对比_推荐
- 论点规则: THESIS_R11
- 论点派生: 监管里程碑叙事
- 论点分类: 新闻_评论
- 论点模式: 以监管审批事件（获批/被拒/大反转）为时间锚点，解读背后的科学与政策逻辑。
- 论点模板: {监管事件}！{背后的逻辑/意义}
- 人格内核: Macro Strategist
- L4变量组: VAR_TARGET_PATHWAY
- L4变量组: VAR_EFFICACY_NUM
- L4变量组: VAR_SAFETY_RISK
- L4变量组: VAR_BIOMARKER_CHANGES
- L4关注点: M3_U_B_MECHANISM_DEEPDIVE: 必须强调对『原纤维/寡聚体』的清除，不可仅提斑块。；只能作为关注点，不能替代当时证据，也不能倒推出未下发的数字或结论。
- L4关注点: M3_U_B_TRIAL_DATA: 凡提Clarity AD，如当时证据明确支持，可优先说明ADAS-cog14或CDR-SB的准确百分比数据。；只能作为关注点，不能替代当时证据，也不能倒推出未下发的数字或结论。
- L4关注点: M3_U_B_SAFETY_MANAGEMENT: 提及ARIA风险时，必须同时提及MRI监测频率建议和大多数为无症状的定性描述。；只能作为关注点，不能替代当时证据，也不能倒推出未下发的数字或结论。
请根据以上信息生成文章，目标字数约 2500 字（±10%），
结构须与篇幅相匹配，避免泛化扩写。
```

### 四、当时稿件全文

1. 生成稿全文（必须直接贴入，不得只写路径）：

```text
# 仑卡奈单抗获批之后：27%的减缓背后，一场关于"谁来清除"的机制揭秘

## 引言：当抗体遇见小胶质细胞

2025年，仑卡奈单抗（Lecanemab）已非新药。这款靶向可溶性Aβ原纤维（soluble Aβ protofibrils）的单抗，以10 mg/kg静脉注射、每两周一次的方案获批上市，其临床试验中认知衰退减缓27%的数据曾引发广泛关注。然而，一个根本问题始终悬而未决：抗体与淀粉样蛋白结合后，究竟是什么真正完成了"清除"工作？

Nature Neuroscience最新发表的研究给出了清晰答案——小胶质细胞。比利时鲁汶大学Bart De Strooper团队利用人源小胶质细胞异种移植模型，首次在分子层面解构了仑卡奈单抗的作用机制。这不是简单的"抗体标记-细胞吞噬"故事，而是一场关于Fc片段功能、转录程序重编程与特定基因激活的精密调控。

## 机制解密：Fc片段是钥匙，小胶质细胞是执行者

研究团队设计了一个精巧的对照实验。他们比较了三种情况：完整仑卡奈单抗、Fc沉默突变体（Lecanemab LALA-PG，通过L234A/L235A/P329G突变 abolish Fc介导的效应功能），以及单纯缺乏小胶质细胞的模型。

结果呈现出鲜明的"全或无"特征。

完整仑卡奈单抗治疗8周后，小鼠脑内X-34标记的淀粉样斑块面积显著减少（P=0.0003），82E1标记的Aβ肽面积同样大幅下降（P<0.0001）。更细致的分析显示，这种清除主要作用于较小的斑块——Anderson-Darling检验显示斑块面积分布发生显著偏移（P<0.0001）。不溶性Aβ42水平降低（P=0.0001），可溶性Aβ38水平也显著下降（P=0.0005）。

然而，当Fc效应功能被沉默，Lecanemab LALA-PG虽然仍能结合斑块（事实上，由于无法被细胞摄取，它在斑块上的积累更为明显），却完全丧失了清除能力。斑块面积、Aβ水平与对照组无统计学差异。

最关键的一击来自"无小胶质细胞"实验。在AppNL-G-F Csf1rΔFIRE/ΔFIRE小鼠中，即使给予完整仑卡奈单抗，缺乏人源小胶质细胞的情况下，斑块负荷毫无变化（所有指标NS）。这构成了机制上的决定性证据：仑卡奈单抗的疗效，必须同时满足两个条件——功能性Fc片段，以及具备FcγR的小胶质细胞。

## 疗效分析：从分子结合到转录重编程的级联反应

### 空间转录组揭示的"吞噬程序"

研究团队采用Nova-ST空间转录组技术，在40μm分辨率的组织域（TDs）层面解析小胶质细胞的基因表达变化。距离Aβ斑块的远近成为关键变量——在仑卡奈单抗治疗组中，靠近斑块的TDs显示出强烈的转录特征。

基因集富集分析（GSEA）呈现出高度特异性的通路激活：溶酶体通路（NES +1.94, P.adj=0.016）和吞噬体通路（NES +1.57, P.adj=0.027）显著上调。这些通路的leading edge基因包括CTSD、CTSL、LIPA、LGMN等溶酶体蛋白酶，以及FCGR1A、ITGB2、TLR4等吞噬相关分子。

值得注意的是，这些变化在Lecanemab LALA-PG组中完全缺失，甚至呈现负向富集。这表明Fc介导的效应功能不仅是"可有可无"的增强因素，而是启动整个清除程序的必要开关。

单细胞RNA测序进一步细化了这一图景。约300个差异表达基因中，加权基因共表达网络分析（WGCNA）识别出14个功能模块。其中5个模块在仑卡奈单抗治疗后显著上调：黄色模块（干扰素应答）、红色模块（未折叠蛋白应答）、鲑鱼色模块（抗原呈递）、黑色模块（线粒体与免疫信号）、蓝色模块（代谢重编程），以及最关键的粉红色模块。

### SPP1/骨桥蛋白：被激活的"清除因子"

粉红色模块的核心发现是SPP1（编码骨桥蛋白，osteopontin）——这是单细胞和空间分析中上调最显著的基因。该模块同时包含LGALS1、CTSD、ITGAX等DAM/HLA状态标志物，但又超越了单纯的"疾病相关"表型。

空间分析显示，粉红色模块基因在斑块周围TDs中富集最为显著（P=3.28×10⁻¹⁵）。免疫荧光证实，仑卡奈单抗治疗后，IBA1⁺小胶质细胞中的OPN表达显著升高（X-34⁺斑块周围P=0.0027，82E1⁺斑块周围P=0.0044），而IBA1⁺细胞总面积并无增加——这意味着单个细胞的OPN表达量提升，而非细胞数量增多。

功能验证最为直接：体外实验中，外源性OPN刺激以剂量依赖性方式促进人源小胶质细胞清除Aβ斑块，最高浓度（1350 ng/ml）达到统计学显著性（P=0.03）。

### 神经毒性的边界：特异性吞噬与炎症控制

一个关键的安全性问题在于：增强的吞噬活性是否会"误伤"正常突触？此前研究显示，某些抗Aβ抗体的Fc效应可能导致突触吞噬（synaptophagy）。

本研究的超分辨率成像给出了相对安心的答案。在斑块周围5μm区域内，突触前标志物Synaptophysin密度无变化，突触后标志物Homer1密度甚至小幅增加（P=0.044），突触 puncta 密度保持稳定。这表明仑卡奈单抗诱导的吞噬具有Aβ特异性，而非泛化的"清道夫"模式。

此外，与Aducanumab等抗体不同，仑卡奈单抗未诱导典型促炎细胞因子（Tnf、Il1b、Nfkb）的广泛表达。相反，棕色炎症模块呈现下调趋势。这种"有吞噬、弱炎症"的表型，可能解释其相对可控的临床安全性特征。

### 神经病理的下游效应

仑卡奈单抗治疗显著降低了LAMP1标记的营养不良性神经突起（dystrophic neurites）总面积（P=0.0091）。然而，神经突起负荷与斑块负荷的比值保持不变——提示神经突起的减少是斑块清除的间接后果，而非独立的神经保护作用。

这一发现具有临床解读价值：27%的认知减缓，很可能主要归因于淀粉样病理的减轻，而非直接的神经功能改善。这符合抗淀粉样蛋白疗法的"上游干预"定位，也提示联合治疗策略的必要性。

## 结论：从"可做"到"何时做、给谁做"的决策重构

这项研究的价值超越了单纯的机制阐明。它揭示了抗Aβ免疫疗法的一个核心设计原则：有效的淀粉样蛋白清除，不取决于抗体与Aβ的结合亲和力本身，而取决于其能否通过Fc片段"桥接"小胶质细胞的效应功能。

这一发现对临床决策具有多重启示。

首先，患者选择需考虑小胶质细胞功能状态。衰老、APOE4携带状态、既往炎症史等因素可能影响FcγR表达或信号传导效率，这些变量或可作为疗效预测的生物标志物。

其次，治疗时机窗口可能早于当时实践。研究显示仑卡奈单抗对较小斑块的清除效应更为显著——这支持在疾病更早期、病理负荷较低时启动治疗，而非等待广泛斑块形成。

最后，Fc工程化策略的未来方向得以明确。研究提及"增强效应功能同时减少补体激活"的工程化思路，这与肿瘤免疫治疗中广泛应用的Fc优化技术形成跨领域呼应。SPP1通路的上调提示，直接靶向该信号轴的小分子或生物制剂，可能成为增强清除效率的辅助手段。

仑卡奈单抗的监管获批曾被视为淀粉样蛋白假说的"里程碑式验证"。而这项机制研究的深层意义在于：它将该药物从"一个有效的抗体"重新定位为"一个能够重编程先天免疫功能的疾病修饰工具"。27%的认知减缓不是终点，而是理解"神经-免疫-血管"复杂交互的起点。对于临床医生和患者而言，这意味着更精细的获益-风险评估；对于药物开发者而言，这指明了下一代疗法的优化路径——不是寻找更强的Aβ结合剂，而是设计更智能的免疫调节器。
```

### 五、当时审核意见与返修抓手

1. 本轮未执行评分；原因：`task_status=failed`，`halted_at=quality`，`error_message=质量门禁检查失败，阻断交付 | details={'quality_errors': [{'gate': 'inference_clean', 'message': '检测到推理泄露标记（<think> 或内部推理句式），阻断交付'}]}`。
2. 当时返修抓手：
- 先全文检索并清除任何可能触发 `inference_clean` 的痕迹，包括 `<think>`、自我指令、过程说明、元叙事句、对推理步骤的显式陈述。
- 机制段保留 4 个核心锚点即可：原纤维靶点、Fc 依赖的小胶质细胞、phagosome/lysosome 程序、SPP1/osteopontin；其他实验方法学压缩到背景句。
- 把“实验怎么做”压成“为什么能证明 Fc + microglia 是必要条件”，避免把正文写成 paper summary。
- 结论段不要再做超证据扩写，只保留“为什么这项机制研究会改变对药物作用方式的理解”。
- 本轮 `generated.txt` 与 `review_bundle.json` 已存在，返修应基于这份现稿做定向清洗，不需要从零重抽。
- 当时 runner 在失败态后处理又报 `Count` 异常；质量门过后需要重新 rerun，才能补齐 `summary.json/score.json`。
3. secondary blocker：当时 runner 在失败态后处理又报 `Count` 异常；质量门过后需要重新 rerun，才能补齐 `summary.json/score.json`。
4. 人工审核时的重点对照项：先回看标题、导语和机制段第一屏，确认正文是不是在解释 Fc-microglia-SPP1 机制链，而不是夹带内部推理痕迹或写成论文摘要。先回看标题、导语和机制段第一屏，确认正文是不是在解释 Fc-microglia-SPP1 机制链，而不是夹带内部推理痕迹或写成论文摘要。

## 工程附录

### Runtime 指针

1. `run_summary.md`：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\run_summary.md`
2. `task_detail.json`：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\task_detail.json`
3. `generated.txt`：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\generated.txt`
4. `materials_full.json`：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\materials_full.json`
5. `review_bundle.json`：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\review_bundle.json`
6. `score.json`：`本轮未生成 score.json`
7. `summary.json`：`本轮未生成 summary.json`
8. `writing_system_prompt.txt`：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\writing_system_prompt.txt`
9. `writing_user_prompt.txt`：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\writing_user_prompt.txt`

### 本轮关键证据

1. 上传与 evidence：`fact_count=29`；`catalog_fact_count=2`；`supplement_fact_count=27`；`supplement_upload_failures=0`。
2. 阶段到达情况：`evidence=completed`；`planning=completed`；`writing=completed`；`drafting=completed`；`quality=failed`；`delivery=not_reached`；`score=not_generated`；`review_bundle=present`。
3. 交付与评分：`task_status=failed`；`halted_at=quality`；`quality_overall_status=failed`；`final_docx_word_count=None`；`target_word_count=None`；`weighted_total=未评分`；`qualified=未评分`。
4. planning / writing 卡片：planning=`关键获益是否真的足以改写决策！Approved dosing regimen。写作主轴采用监管里程碑叙事，围绕疗效分析、Mechanism证据展开，面向对医学感兴趣的普通读者完成新闻_评论型论证。`；writing=`本轮写作任务：围绕“关键获益是否真的足以改写决策！Approved dosing regimen。写作主轴采用监管里…”写作。
面向读者：对医学感兴趣的普通读者；目标字数：2500。
结构重点：引言、Mechanism、疗效分析`。

### materials 指针

1. 历史人工审稿材料文件：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\materials_full.json`
2. 同轮回退锚点：`task_detail.json -> output_data.evidence / stage_artifacts.evidence`；`review_bundle.json -> materials / evidence`

### prompt 指针

1. system prompt：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\writing_system_prompt.txt`
2. user prompt：`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\writing_user_prompt.txt`
3. 同轮回退锚点：`review_bundle.json -> writing.system_prompt / writing.user_prompt`

### 评分结果

1. 总分：`本轮未执行评分`
2. 达标结论：`本轮未判定`
3. 评分状态：`未执行`
4. 各维度：`本轮未执行评分；原因：task_status=failed，halted_at=quality，quality 门禁已阻断交付，runner 后处理另报 Count 异常。`

### 本轮真实 blocker

1. 当时主链死在 `quality`，`halted_at=quality`，错误为：`质量门禁检查失败，阻断交付 | details={'quality_errors': [{'gate': 'inference_clean', 'message': '检测到推理泄露标记（<think> 或内部推理句式），阻断交付'}]}`。
2. supplement 证据前链已通：上传成功、evidence/planning/writing/drafting 均已完成，问题已经后移到质量门禁。
3. runner 在失败态收口又报 `Count` 异常，导致 `summary.json/score.json` 未落盘；这属于 secondary blocker。

### 证据摘要

1. 已直接核对 `侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\run_summary.md`，runner 退出码为 `1`，并记录了 `The property 'Count' cannot be found on this object.`。
2. 已直接核对 `侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\task_detail.json`，本轮 `task_status=failed`、`halted_at=quality`，`supplement_fact_count=27`、`supplement_upload_failures=[]`。
3. 已直接核对 `侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\generated.txt`、`侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173526_274_IIIA_20260411_retest\lecanemab_mechanism\review_bundle.json` 与 `writing_*prompt.txt`，正文和审稿包已生成，但 `score.json/summary.json` 本轮不存在。
