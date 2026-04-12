# lecanemab_news 模型对照全貌

状态：已完成  
日期：2026-04-12  
用途：人工直接比较 `k2.5` 与 `deepseek-reasoner` 在 `news` 题上的起稿、整稿返修、整稿后局部返修表现。主阅读层直接贴材料、共用 draft prompt 和两边当前候选稿，不再停在结果审计表。

## 当前有效口径

1. 本页只认同轮 runtime：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek`。
2. 本页只认固定 scorer 下的 `score.json / local_revise_manifest.json / draft_manifest.json / whitebox_contract.json / draft_prompt.md / revise_prompt.md`。
3. 当前这题的主结论不是“谁更会写”，而是：在当前 scorer 下，`k2.5` 与 `deepseek-reasoner` 三阶段都没有被拉开，说明瓶颈更像合同/问题线/scorer 分辨力，而不是单纯模型切换。
4. 本页不再假装存在 compat `materials_full.json / writing_*prompt.txt`；本轮模型对照实际真相源是 `materials/materials_digest.md + whitebox_contract.json + draft_prompt.md`。

case_id: `lecanemab_news`
run_dir: `D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek`

## 当前明确缺项

1. 独立 planning prompt：本轮不存在；原因：模型对照 harness 只保留白盒合同与起稿 prompt。
2. compat `materials_full.json`：本轮不存在；原因：模型对照 harness 真实材料口径落在 `materials/materials_digest.md` 与 `draft_prompt.md`。
3. compat `writing_system_prompt.txt / writing_user_prompt.txt`：本轮不存在；原因：模型对照 harness 使用单份 `draft_prompt.md` 承载实际起稿 prompt。

## 主阅读层

### 一、人工审核先看

1. 写作合同：写给医学专业人士，核心任务是把浙二 76 例真实世界队列写成主线，再让华西/华山/海南做补线，最后回收到中国真实世界的安全性与临床落地。
2. 当前判定：当前 scorer 对两种模型几乎没有分辨力；两边都是 `72 / true / editorial 68`。
3. 审稿优先看：问题不在“模型完全写不出来”，而在“问题线是否够硬、浙二主线是否够独占、soft 审稿是否能识别新闻稿的差异”。
4. 当前最该改：继续打上游合同和问题线，不要误把“换模型”当主解法。

### 二、本轮真正喂给写手的材料（人工整理版）

人工阅读提示：
1. 本题不是单 PDF 题，而是 `浙二` 主线 + `华西 / 华山 / 海南瑞金` 三条补线。
2. 写手真正要解决的问题不是“材料不够”，而是“如何让多中心材料围着浙二主线转，而不是写成平行综述”。
3. 当前主风险是：多中心补线过长、新闻导语不够硬、临床落地段容易写成指南腔。

实际入模材料整理稿：
~~~text
# 白盒取材摘要

- 题目: lecanemab_news / 仑卡奈单抗中国真实世界新闻报道
- 状态: ready
- 总材料项: 4
- 可抽取文本项: 4

- [ok] D:\汇度编辑部1\项目文章\侠客岛测试任务\仑卡奈单抗新闻报道\inputs\【原文】华西.pdf
- [ok] D:\汇度编辑部1\项目文章\侠客岛测试任务\仑卡奈单抗新闻报道\inputs\【原文】浙二.pdf
- [ok] D:\汇度编辑部1\项目文章\侠客岛测试任务\仑卡奈单抗新闻报道\inputs\海南瑞金.pdf
- [ok] D:\汇度编辑部1\项目文章\侠客岛测试任务\仑卡奈单抗新闻报道\inputs\华山研究.pdf
~~~

补充可读整理：
1. 浙二是主线：`76例 / IRSE 18.4% / ARIA 11例 / EOAD 更快下降 / CDR 分层 / 12个月 PET 下降`。
2. 华西是病理与短期疗效补线；华山是大样本安全补线；海南瑞金是短期稳定与本土安全性补线。
3. 这题真正考的是“主线牵引补线”的写法，不是数据堆砌能力。

### 三、本轮给模型的 prompt 全文（两模型共用起稿 prompt）

说明：`k2.5` 与 `deepseek-reasoner` 在 base 阶段共用同一份 `draft_prompt.md`；差异只在 writer profile 的模型配置，不在 prompt 文案本身。

~~~text
【模块角色上下文】
你当前承担的是首稿生成节点。先忠实执行写作合同、样稿母本边界和题目主线，再追求中文表现力。允许把稿件写顺、写稳、写成人类编辑会交付的成熟文本，但不得为追求观感擅自改题、偷换证据边界、补不存在的事实。

你是侠客岛白盒编排器的执行写手。请严格按下面合同写一篇完整中文文章。

【写作合同】
- 题目：仑卡奈单抗中国真实世界新闻报道
- 题型：C
- 受众：医学专业人士
- 目标字数：2800
- 写作目的：把仑卡奈单抗在中国多中心真实世界中的疗效与安全性数据写成有临床落地感的新闻报道，突出浙二主线，并用其他中心作为补线佐证。
- 体裁：医学新闻报道

【公式驱动约束（当前已接线公式位）】
以下约束来自藏经阁8条公式的机器编码，你必须逐条遵守。

■ 人格定位：科学新闻记者——把多中心真实世界数据写成有临床落地感的新闻报道，用问题线拉动叙事而非罗列数据。
■ 写作范围：RANGE-03
■ 写作目标：让读者理解仑卡奈单抗在中国真实世界中的疗效与安全性全貌——以浙二主线带出多中心证据。
■ 排列规则：先锚核心新闻点，再展浙二主线，后补多中心佐证，收安全性关注与临床落地。
■ 内容组合策略：新闻报道型——核心发现导语 + 浙二主线数据 + 多中心补线 + 安全性坦陈 + 落地意义
■ 逻辑组合策略：ARCH-04承重 + 问题线——先抛核心新闻点，沿问题线展开证据，回收到临床落地

■ 有效大纲（你必须按此大纲组织全文，每个板块必须有实质内容）：
  - [导语] 一句话核心新闻点——中国首批真实世界数据说了什么
  - [背景] 仑卡奈单抗获批后中国真实世界数据为什么重要
  - [浙二主线] 76例队列安全性+认知变化+CDR分层+EOAD发现
  - [多中心补线] 其他中心共同指向，不是单点而是多中心支撑
  - [安全性收口] ARIA总体可控+与Clarity AD对齐度+真实世界用药注意事项

■ 有效内容单元（以下每个单元必须在正文中至少出现一次，缺一扣分）：
  - 一条关于中国真实世界主队列规模与核心发现的硬事实
  - 一个关于真实世界数据与III期试验安全性对齐度的判断
  - 浙二主线加其他中心补线的权威锚定

■ 有效逻辑单元（全文承重逻辑必须遵守以下约束）：
  - ARCH-04承重——沿“真实世界落地问题→浙二主线→多中心佐证→安全性关注”单一叙事线贯穿
  - 问题线主从——以“中国患者真实世界用药后怎么样”为主问题线拉动全文

【必写事实清单】
以下每一条必须在正文中找到对应段落或句子，不得遗漏：
- 浙二队列76例早期AD、IRSE 18.4%、ARIA 11例
- CDR分期与认知下降速度分层
- EOAD与LOAD的认知轨迹差异
- 中国多中心真实世界安全性与疗效信号

【文章结构要求】
文章必须按以下结构组织，每个板块必须有实质内容：
- 新闻导语（核心发现一句话）
- 研究背景与中国真实世界意义
- 浙二主线数据（安全性+认知变化）
- 多中心补线（其他中心作为佐证）
- 安全性关注与临床落地

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

# 仑卡奈单抗新闻报道 G0 证据卡

card_id: lecanemab_news_c_g0
status: verified
source_scope: raw inputs only
generated_at: 2026-04-06
primary_angle: 浙江二院真实世界研究是主线，其他三篇原始 PDF 用作中国真实世界安全/有效性背景对照

## 证据摘要

1. 浙江原始 PDF 的页 1/5/6/8/9/10 可直接回指到 76 例、18.4% IRSE、11 例 ARIA、PVWMHs 风险信号，以及 CDR / 年龄分层 MMSE 下降比较位。
2. 华西原始 PDF 的页 1/4/5/6 给出 68 例、ADAS-cog14 / CDR-SB / p-tau181 / p-tau217 / SUVR 的前后对照，能直接支撑“短期有效性与生物标志物响应”。
3. 华山与海南原始 PDF 分别在 33 页和 36 页内给出中国真实世界安全/有效性背景，分别可回指到 407 例与 64 例队列及其表图锚点。

## Must-Have Values

| label | exact value | comparison | anchor | page | status |
|---|---|---|---|---|---|
| Zhejiang cohort and exposure | 76 early-stage AD participants; mean age 65.53 ± 9.31; 51 female (67.1%); 49 ApoE ε4 carriers (64.5%); 58 treated >3 months, 44 >6 months, 12 >12 months | single-center Zhejiang real-world cohort | page 1 abstract; page 2 methods; Table 1 page 6 | 1-2, 6 | verified |
| Zhejiang safety and ARIA subtype | IRSE 14/76 (18.4%); ARIA in 11 participants, including 7 isolated ARIA-H and 4 ARIA-E with/without microhemorrhage; all ARIA asymptomatic | within the Zhejiang cohort | page 1 abstract; Fig. 2 page 5; Table 2 page 6; Table 4 page 8 | 1, 5-6, 8 | verified |
| Zhejiang risk and cognition comparisons | isolated ARIA-H was associated with higher baseline Fazekas PVWMHs (p = 0.008); CDR-GS 1 had faster MMSE decline than CDR-GS 0.5 (β = 0.537, 95% CI 0.099-0.974, p = 0.019); LOAD group β = -0.434, 95% CI -0.726 to -0.141, p = 0.004; no significant MMSE difference between baseline <20 and ≥20 within the MCI subgroup | cognitive decline stratified by CDR stage, age-of-onset, and baseline MMSE | page 5 ARIA text; Fig. 4 page 9; discussion page 10 | 5, 9-10 | verified |
| Zhejiang benchmark against Clarity AD | Clarity AD ARIA-E 12.6% and ARIA-H 17.3%; Asian subgroup ARIA-E 6.2% and ARIA-H 14.4%; IRSE 26.4% overall and 12.3% Asian subgroup | local Zhejiang cohort safety benchmarked against phase 3 Clarity AD | page 2 background section | 2 | verified |
| Huashan multicenter safety cohort | 407 AD patients; mean follow-up 5.6 ± 3.39 months; 22.22% treatment-related symptoms; 12.15% at least one ARIA; 4 symptomatic ARIA cases; 7 severe ARIA cases; 9.38% withdrew | multicenter China real-world cohort | page 1 abstract; page 10-12 results; Fig. 1-3 pages 10-12 | 1, 10-12 | verified |
| Huashan efficacy and risk stratification | higher baseline microhemorrhage count was associated with adverse events; no significant AE difference between moderate AD dementia and MCI; after 6 months biomarkers improved and cognitive function remained stable | disease stage and baseline MRI risk | page 2 abstract; page 10-12 results | 2, 10-12 | verified |
| West China short-term efficacy and biomarkers | 68 patients; ADAS-cog14 -4.32 points at 2.5 months and -4.62 at 7 months; CDR-SB -0.46 and -0.16; p-tau181 -2.05 and -3.57 pg/ml; p-tau217 -0.27 pg/ml at 7 months; whole-brain SUVR -0.20 at 12 months | baseline vs V1/V2; biomarker response during treatment | page 1 abstract; Table 1 page 4; Table 2 page 5; Fig. 1-3 pages 5-6 | 1, 4-6 | verified |
| West China safety and ARIA rates | total adverse effects 56.3%; discontinuation 7.8%; infusion-related reactions 20.3%; ARIA-H 9.4%; ARIA-E 3.1% | Chinese cohort safety vs Clarity AD | page 1 abstract; Table 2 page 5; Fig. 2-3 page 6 | 1, 5-6 | verified |
| Hainan real-world safety and effectiveness | 64 patients; infusion-related reactions 20.3% (13/64); 69.2% occurred during the initial infusion and 84.6% did not recur; ARIA-H 9.4% (6/64); ARIA-E 3.1% (2/64); only two symptomatic cases; Aβ42 +21.42% and Aβ40 +23.53% | baseline vs 6 months and safety in Chinese early AD cohort | page 3-4 abstract; Fig. 1-2 pages 28-29; Table 1 page 30-31; Table 2 page 32-33; Table 3 page 35-36 | 3-4, 28-29, 30-33, 35-36 | verified |
| Hainan 6-month cognitive stability | MMSE 22.33 ± 5.58 vs 21.27 ± 4.30 (P = 0.733); MoCA 16.38 ± 6.67 vs 15.90 ± 4.78 (P = 0.785); CDR-SB 2.30 ± 1.65 vs 3.16 ± 1.72 (P = 0.357) | baseline vs 6 mont

【材料摘录】
### 【原文】华西.pdf
Received: 30 June 2025  Revised: 1 September 2025  Accepted: 2 September 2025
DOI: 10.1002/alz.70750

RESEARCH ARTICLE

Lecanemab treatment for Alzheimer's Disease of varying
severities and associated plasma biomarkers monitoring: A
multi-center real-world study in China

Sihui Chen1 Ruwei Ou1 Qianqian Wei1 Chunyu Li1 Wei Song1 Bi Zhao1

Jing Yang1 Jiajia Fu1 Yuanzheng Ma1 Jiyong Liu1 Xiangming Wang2

Dengfu Fang3 Tao Hu4 Li Xiao5 Shushan Zhang6 Rui Huang7

Xiaoyan Guo8 Fei Feng9 Xueping Chen1                                           Huifang Shang1

1Department of Neurology, West China Hospital, Sichuan University, Chengdu, Sichuan, China
2Department of Neurology, Central Hospital of Panzhihua, Middle Section of Panzhihua Avenue, Dong District, Panzhihua, Sichuan, China
3Department of Neurology, Suining First People's Hospital, Suining, Sichuan, China
4Department of Neurology, The Affiliated Hospital of Sichuan Nursing Vocational College, Sichuan Provincial Third People's Hospital, Chengdu, Sichuan, China
5Department of Neurology, Sichuan Provincial Fifth People's Hospital, Chengdu, Sichuan, China
6Department of Neurology, Affiliated Hospital of North Sichuan Medical College, Nanchong, Sichuan, China
7Department of Neurology, Sichuan Academy of Medical Sciences & Sichuan Provincial People's Hospital, University of Electronic Science and Technology of China,
Chengdu, Sichuan, China
8Department of Neurology, The Affiliated Hospital of Southwest Medical University, Luzhou, Sichuan, China
9Department of Neurology, Zunyi First People's Hospital, Zunyi, GuiZhou, China

Correspondence                                 Abstract
Xueping Chen and Huifang Shang, Department     INTRODUCTION: We investigated real-world efficacy, safety, and plasma biomarker
of Neurology, West China Hospital, Sichuan     dynamics of Lecanemab in Chinese patients with Alzheimer's disease (AD).
University, No. 37 Guoxue Road, Chengdu,       METHODS: A multi-center prospective cohort study enrolled 68 AD patients. Cogni-
Sichuan 610041, China.                         tive scales and plasma biomarkers were assessed at baseline (V0), 2.5 months (V1), and
Email: chenxueping0606@sina.com and            7 months (V2).
hfshang2002@126.com                            RESULTS: Alzheimer's Disease Assessment Scale-Cognitive Subscale 14-item version
                                               (ADAS-cog14) scores improved significantly at both follow-ups, and plasma p-tau181
Funding information                            consistently declined. Both p-tau181 and p-tau217 correlated with cognition and par-
National Natural Science Foundation of China,  tially predicted treatment response (area under the curve [AUC] = 0.734 and 0.713).
Grant/Award Number: 82271272; Science and      Mixed-effects modeling confirmed their dynamic association with ADAS-cog14 scores.
Technology Bureau Fund of Sichuan Province     Subgroup analyses indicated benefits across s

### 【原文】浙二.pdf
Shang et al. Alzheimer's Research & Therapy (2025) 17:249      Alzheimer's Research &
https://doi.org/10.1186/s13195-025-01886-5                                       Therapy

RESEARCH                                                       Open Access

Real--world application of lecanemab
in early--stage alzheimer's disease: a single--
center prospective cohort analysis

Jia Shang1, Siyan Zhong1, Li Shang1, Qingze Zeng2, Shuai Zhao1, Xiao Luo2, Kaicheng Li2, Xinyi Zhang1,
Peiyu Huang2, Yaping Yan1, Zhirong Liu1, Baorong Zhang1* and Yanxing Chen1*

Abstract

Background and objectives Lecanemab (Leqembi�) has been approved for the treatment of early Alzheimer's
disease (AD) patients. However, the safety and efficacy of lecanemab in clinical practice in Asia population remain
unclear.

Design, setting, and participants This prospective cohort study was conducted in a single center in Eastern China,
including 76 early-stage AD participants treated with lecanemab. All participants underwent at least 1 lecanemab
infusion.

Results The mean age was 66 years (65.53�9.31), and 51 (67.1%) participants being female. A total of 49 (64.5%)
participants were ApoE-4 carriers, including 34 (44.7%) heterozygotes and 15 (19.7%) homozygotes. Infusion-
related side effects (IRSE), primarily occurred after the first infusion, were observed in 14 participants (18.4%). The
most common IRSE were fever and fatigue. Until 9 Aug 2025, 58 participants had received treatment for more than
3 months, 44 for more than 6 months and 12 for more than 12 months. Amyloid-related imaging abnormalities (ARIA)
were observed in 11 participants. Specifically, solitary ARIA-H (hemorrhage) was detected in 7 participants, while
ARIA-E (edema) with or without cerebral micro-hemorrhage was identified in 4. Notably, all the 11 participants with
ARIA were asymptomatic. Participants with isolated ARIA-H exhibited higher baseline Fazekas scores of PVWMHs
(p=0.008). Participants with a Clinical Dementia Rating Scale Global Score (CDR-GS) of 1 had a more rapid decline in
Mini-Mental State Global Score (MMSE) scores as compared to those with a CDR-GS of 0.5. Following 12 months of
lecanemab therapy, amyloid PET exhibited a significant reduction in brain amyloid burden.

Conclusion These data support that lecanemab appears to be generally tolerated in Asian population. The IRSE and
ARIA-E events were less common than the Clarity AD study.

Keywords Alzheimer's disease, Lecanemab, Amyloid-related imaging abnormalities, Cognitive progression

Jia Shang, Siyan Zhong and Li Shang these authors contributed  Yanxing Chen
equally to this study.
                                                               chenyanxing@zju.edu.cn
*Correspondence:                                               1Department of Neurology, The Second Affiliated Hospital, Zhejiang
Baorong Zhang
brzhang@zju.edu.cn                                             University School of Medicine, Ha

### 海南瑞金.pdf
Chinese Medicine Journal Publish Ahead of Print
10.1097/CM9.0000000000003888
Original Article
Safety and effectiveness of lecanemab in Chinese patients with early Alzheimer's
disease: Evidence from a multidimensional real-world study

Wenyan Kang1,2, Chao Gao1, Xiaoyan Li2, Xiaoxue Wang3, Huizhu Zhong2, Qiao Wei2, Yonghua

Tang4,5, Peijian Huang1,2, Ruinan Shen1, Lingyun Chen6, Jing Zhang4, Rong Fang1, Wei Wei7, Fengjuan

Zhang7, Gaiyan Zhou7, Weihong Yuan8, Xi Chen8, Zhao Yang1, Ying Wu3, Wenli Xu9, Shuo Zhu1,

Liwen Zhang10, Naying He4, Weihuan Fang4, Miao Zhang11, Yu Zhang11, Huijun Ju11, Yaya Bai11, Jun

D Liu1

1Department of Neurology, Institute of Neurology, Ruijin Hospital, Shanghai Jiao Tong University

T School of Medicine, No 197, Ruijin Second Road, Huangpu District, Shanghai 200025, China;
P 2Department of Neurology, Hainan Branch, Ruijin Hospital, Shanghai Jiao Tong University School of

Medicine, No 41, Kangxiang Road, Qionghai, Hainan 571437, China;

E 3Department of Biostatistics, School of Public Health, Southern Medical University, No 1023, Shatai

Road, Baiyun District, Guangzhou, Guangdong 510515, China;

C 4Department of Radiology, Ruijin Hospital, Shanghai Jiao Tong University School of Medicine, No

197, Ruijin Second Road, Huangpu District, Shanghai 200025, China;

C 5Department of Radiology, Hainan Branch, Ruijin Hospital, Shanghai Jiao Tong University School of
AMedicine, No 41, Kangxiang Road, Qionghai, Hainan 571437, China;

6Medical department, Eisai China Inc. No 1601 Nanjing West Road, Jing'an District, Shanghai 200400,

China;

7Neurology Department, Taicang Branch of Ruijin Hospital Affiliated to Shanghai Jiao Tong University

School of Medicine, Taicang, Jiangsu 215400, China;

8Real World study Institute of Hainan Lecheng, No. 32 Kangxiang Road, Boao Lecheng International
Medical Tourism Pilot Zone, Boao, Hainan 571437, China;
9Nursing Ward, Ruijin Hospital Affiliated to Shanghai Jiao Tong University School of Medicine, No.
888 Shuangding Road, Jiading District, Shanghai 201801, China;
10Institute for Medical Imaging Technology, Ruijin Hospital, Shanghai Jiao Tong University School of
Medicine, No. 888 Shuangding Road, Jiading District, Shanghai 201801, China;
11Department of Nuclear Medicine, Ruijin Hospital, Shanghai Jiao Tong University School of Medicine,

D No 197, Ruijin Second Road, Huangpu District, Shanghai 20025, China.

Correspondence to: Jun Liu, Department of Neurology, Institute of Neurology, Ruijin Hospital,

T Shanghai Jiao Tong University School of Medicine, No 197, Ruijin Second Road, Huangpu District,

Shanghai 20025, China

P E-Mail: jly0520@hotmail.com;
E Yonghua Tang, Department of Radiology, Ruijin Hospital, Shanghai Jiao Tong University School of

Medicine, No 197, Ruijin Second Road, Huangpu District, Shanghai 200025, China; Department of

C Radiology, Hainan Branch, Ruijin Hospital, Shanghai Jiao Tong University School of Med

### 华山研究.pdf
1   Safety and short-term outcomes of lecanemab for

2   Alzheimer's disease in China: a multicentre study

 3  Ling-Ling Li,1, Rong-Ze Wang,1,2, Zhen Wang,3, Hua Hu,4,,Wei Xu,5, Lin Zhu,6, Yan Sun,7,                                       Downloaded from https://academic.oup.com/brain/advance-article/doi/10.1093/brain/awaf427/8320297 by guest on 12 November 2025
 4      Ke-Liang Chen,1, Shu-Fen Chen,1, Xiao-Yu He,1 Ming-Yang Yuan,1 Yu-Yuan Huang,1
 5
 6  T Xiaoyan Liu,7 Ping Liu,7 Qin-Yong Ye,2 Jie Wang,1 Zi-Zhao Ju,8 Wei Zhang,9 Bin Hu,10 Yu
 7  IP Guo,1 Xiao-Yun Cao,11 Yu-Xin Li,10 Chuan-Tao Zuo,8 Wei Cheng,9 Teng Jiang,6 Lan Tan,5

 8    Xiao-Chun Chen,2 Qian-Hua Zhao,1 Mei Cui,1 Guo-Ping Peng,7 Jia-Wei Xin2 and Jin-Tai Yu1

 9  R These authors contributed equally to this work.
    SC Abstract
10  U Lecanemab is a newly approved monoclonal antibody targeting amyloid plaques for the
11  N treatment of early Alzheimer's disease. This study aimed to evaluate the safety and short-term
12  A biomarkers and cognition changes of lecanemab in Chinese clinical practice.

13  M This multicenter real-world study involved patients receiving lecanemab treatment across seven
14
15  hospitals in China. Patients underwent comprehensive assessments before treatment. Lecanemab
16  was administered via intravenous infusion every 2 weeks. Treatment-related symptoms were
17
18  D monitored through self-report, and amyloid-related imaging abnormalities were assessed via
19  E magnetic resonance imaging. Amyloid and tau biomarker changes were measured using positron
20  T emission tomography imaging or plasma testing. Follow-up cognitive assessments were
    P evaluated after 6 months of treatment. Short-term outcomes were analyzed using linear mixed-
21  E effect models, without an untreated control group.
22  C A total of 407 patients who received at least one lecanemab infusion were involved in this study,

23  with a mean follow-up time of 5.6�3.39 months. The mean age was 68.08 years, with 67.57%

    AC of patients being female. Of the participants, 56.51% were APOE 4 carriers, and 83.19% were
24 at biological stage C. During the study period, 22.22% of the patients experienced treatment -

    � The Author(s) 2025. Published by Oxford University Press on behalf of The Guarantors of Brain. This is an Open
    Access article distributed under the terms of the Creative Commons Attribution -NonCommercial License
    (https://crea tivecommons.org/licenses/by-nc/4.0/), which permits non-commercia l re-use, distribution, a nd
    reproduction in any medium, provided the original work is properly cited. For commercial re -use, please contact
    reprints@oup.com for reprints and translation rights for reprints. All other permissions can be obtained through our
    RightsLink service via the Permissions link on the article page on our site--for further information please contact
    journa ls.perm issions@oup.com .

         


请直接输出完整文章正文，不要加解释，不要加前言，不要加代码块。
~~~

### 四、当前稿件全文

#### A. `k2.5` 当前候选终稿（`whole+local`，hard `72` / soft `68`）

~~~text
仑卡奈单抗中国真实世界数据首揭面纱：总体安全可控，早干预窗口与亚组异质性并存

中国患者用上仑卡奈单抗后，真的和试验里一样安全有效吗？最新数据给出的答案是：总体安全可控，早干预窗口明确，但早发型亚组呈现更快认知下降——这一分层图景为临床决策提供了亟需的本土证据。来自浙江大学医学院附属第二医院（浙大二院）领衔的单中心前瞻性队列，联合华西医院、复旦大学附属华山医院及海南瑞金医院等多中心研究，共同描绘出这一抗淀粉样蛋白单抗在中国早期阿尔茨海默病（AD）患者中的疗效与安全性轮廓。

**从试验到病床：中国真实世界数据为何关键**

仑卡奈单抗于2023年基于Clarity AD III期试验获批，但临床试验的严格入排标准与真实临床场景存在显著落差。中国患者群体在遗传背景、脑血管风险因素谱、就诊疾病分期等方面均具独特性，使得本土真实世界数据成为打通"试验疗效"与"临床实效"的关键。更紧迫的是，亚洲人群在Clarity AD试验中亚组分析的ARIA-E发生率（6.2%）已显著低于整体人群（12.6%），但样本量限制使结论存疑。中国真实世界数据的大规模积累，正是为了回答：当药物走出试验中心，安全性谱系是否保持一致？

**浙大二院主线：76例队列的深度解剖**

浙大二院神经科的研究团队构建了迄今中国单中心报道最为完整的早期AD真实世界队列。该研究纳入76例经生物标志物确认的早期AD患者，平均年龄65.53岁，女性占67.1%，ApoE ε4携带率高达64.5%（34例杂合子、15例纯合子）。截至2025年8月，58例完成3个月以上治疗，44例超过6个月，12例跨越12个月节点。

安全性层面，输注相关副作用（IRSE）见于14例患者（18.4%），主要表现为首次输注后的发热与乏力。更具临床权重的是淀粉样蛋白相关影像学异常（ARIA）：11例患者出现影像学异常，其中7例（9.2%）为孤立性ARIA-H（脑微出血或含铁血黄素沉积），4例（5.3%）为ARIA-E（脑水肿）伴或不伴微出血。关键发现是，全部11例ARIA均为无症状性，未导致治疗中断或住院——这一"沉默性"特征与III期试验中症状性ARIA-E约3%的比例形成对照，提示真实世界严密监测下的风险可控性。

那么，哪些患者更容易出现ARIA？孤立性ARIA-H患者的基线脑白质病变（Fazekas脑室周围白质高信号评分）显著更高（p=0.008），印证了脑血管负荷作为ARIA预测因子的价值。对于基线MRI已显示中重度白质病变的患者，输注前后的影像监测频率与强度需相应调整。

疗效维度，浙大二院团队采用简易精神状态检查量表（MMSE）动态追踪认知变化，并引入临床痴呆评定量表整体评分（CDR-GS）与发病年龄进行分层。12个月时Aβ-PET显示全脑SUVR较基线显著下降（p=0.004），平均降幅达0.20，证实淀粉样蛋白清除效应。核心发现之一是疾病分期的差异化轨迹：CDR-GS 1分（轻度痴呆期）患者较CDR-GS 0.5分（轻度认知障碍期）呈现更快的MMSE下降速度（p=0.019）。这一"早干预窗口"效应提示，即使同属"早期AD"范畴，痴呆期启动治疗较认知障碍期可能面临更陡峭的自然病程斜率，早期干预的紧迫性由此凸显。

年龄分层揭示了另一重异质性。晚发型AD（LOAD，发病年龄≥65岁）患者显示MMSE下降减缓（p=0.004），而早发型AD（EOAD，发病年龄<65岁）亚组的MMSE下降速度显著快于晚发性（p<0.05）。值得注意的是，EOAD患者的ApoE ε4携带率并未显著高于晚发性人群，排除了遗传负荷对疗效差异的简单解释。这一警示性发现——EOAD较LOAD认知下降更快——提示临床需对该亚组强化监测，而非预设"越早越好"的疗效预期。

教育程度是否影响疗效？在MCI亚组内部，基线MMSE<20分与≥20分者差异无统计学意义（p=0.42），提示认知筛查阈值内的分层对短期轨迹预测价值有限，认知储备效应在本队列中未转化为治疗响应差异。

更具警示意义的是1例特殊病例：该患者ApoE ε3/ε3基因型，12个月随访时淀粉样蛋白PET显示SUVR升高而非降低，同时伴随认知评分下降。研究者推测，这一现象可能与个体先天免疫状态差异相关——小胶质细胞吞噬功能的不同可能导致淀粉样蛋白清除过程中的短暂病理波动。该个案提示，生物标志物响应并非单调线性，动态监测比单点评估更具临床价值。

**多中心补线：主线发现如何获得验证**

浙大二院关于病理清除与疗效分层的发现，在多中心数据中获得了交叉验证。华西医院牵头的多中心前瞻性研究纳入68例AD患者，覆盖从MCI至中度痴呆的连续疾病谱，为浙二主线的"认知-影像"关联提供了生物标志物层面的机制呼应：治疗2.5个月时阿尔茨海默病评估量表-认知子量表14项版（ADAS-cog14）评分改善4.32分，7个月时扩大至4.62分；血浆磷酸化tau181（p-tau181）在2.5个月下降2.05 pg/ml，7个月时较基线下降达3.57 pg/ml；全脑淀粉样蛋白PET标准化摄取值比值（SUVR）在12个月降低0.20。这一"认知-体液-影像"的三维改善模式，印证了浙二队列中12个月PET显著降负荷的个案趋势。

华西队列的安全性数据同样支撑主线结论：ARIA-H发生率9.4%，ARIA-E仅3.1%，与浙大二院及亚洲亚组趋势一致，共同指向中国真实世界ARIA-E发生率低于全球试验的整体判断。

华山医院团队构建的407例多中心真实世界队列，则将视野拓展至更大规模的社区实践场景，直接验证浙二主线关于ARIA风险因素的分层发现。该队列平均随访5.6个月，至少一次ARIA事件12.15%，症状性ARIA仅4例。关键验证在于：基线微出血灶数量与不良事件风险正相关——这与浙二发现的基线白质病变-ARIA-H关联形成互补，共同构建了"脑血管负荷-ARIA风险"的预测模型。值得注意的是，中度痴呆与MCI阶段的不良事件率无显著差异，这一发现与"疾病越早期、治疗越安全"的直觉假设形成张力，提示风险分层需整合影像标志物而非单纯依赖临床分期。

海南瑞金医院的64例真实世界队列进一步补充了浙二主线关于早期稳定性的证据：6个月时MMSE、蒙特利尔认知评估量表（MoCA）、CDR-总分（CDR-SB）均无显著恶化，血浆Aβ42与Aβ40分别上升21.42%与23.53%，提示病理清除的生化替代指标响应。IRSE发生率20.3%，其中69.2%发生于首次输注；ARIA-H 9.4%，ARIA-E 3.1%，症状性病例仅2例——这一安全性谱系与浙二、华西、华山数据高度一致，形成了多中心共同指向的"可控性"结论。

**安全性风险如何识别？ARIA可控性与临床落地要点**

综合四中心数据，中国真实世界ARIA-E发生率介于3.1%-6.2%区间，ARIA-H介于9.4%-12.15%，均低于或接近Clarity AD亚洲亚组水平（ARIA-E 6.2%，ARIA-H 14.4%）。症状性ARIA比例极低，未报告致死性事件，与III期试验的安全性谱系总体对齐。这一"可控性"结论的建立，依赖于真实世界中更为密集的MRI监测协议——多数中心采用输注前、第5剂前、第12剂前及出现症状时的多点扫描策略，较试验方案的灵活性更高。

因此，临床医生应当如何落地？四中心数据共同指向"患者筛选-监测-沟通"三步决策框架：

**第一步，患者筛选：** 确认生物标志物阳性（脑脊液或PET），评估CDR-GS分期（0.5分vs 1分直接影响疗效预期），识别EOAD人群（需调整疗效沟通框架并强化监测），排查脑血管负荷（基线MRI白质病变Fazekas评分、微出血灶数量）。

**第二步，监测强化：** IRSE主要集中于首次输注，预处理（抗组胺药、解热镇痛药）及输注速度阶梯调整可降低发生率；ARIA的"无症状性"特征要求影像监测而非症状驱动，建议输注前、第5剂前、第12剂前及出现症状时行MRI扫描。

**第三步，沟通校准：** 疾病分期与发病年龄纳入疗效预期沟通——CDR-GS 1分患者需知悉可能更快的认知下降斜率，EOAD患者需理解"认知下降更快"而非"必然改善"的现实，生物标志物动态监测（血浆p-tau181/217、Aβ42/40）可作为疗效评估的补充工具。

中国仑卡奈单抗真实世界数据的初步拼图，正在从"有没有"走向"怎么用"。浙大二院的深度分层、华西医院的生物标志物轨迹、华山医院的大规模安全监测、海南瑞金的早期稳定性证据——多中心异质性的背后，是共同指向的临床可行性：在严格筛选、严密监测、个体化风险管理的条件下，这一抗淀粉样蛋白治疗在中国早期AD患者中展现出与全球试验可比的疗效信号和可接受的安全边际。随着更多中心数据成熟与长期随访延展，真实世界证据将持续重塑中国AD治疗的临床实践图景。
~~~

#### B. `deepseek-reasoner` 当前候选终稿（`whole+local`，hard `72` / soft `68`）

~~~text
一项针对76例中国早期阿尔茨海默病患者的12个月真实世界随访显示，治疗相关影像学异常（ARIA）总体可控，但早发性阿尔茨海默病（EOAD）患者的认知下降速率显著更快（p=0.004）。

仑卡奈单抗（Lecanemab）在中国早期阿尔茨海默病（AD）患者中应用后，其真实世界疗效与安全性究竟如何？一项以浙江大学医学院附属第二医院（浙大二院）76例患者为主队列的研究，给出了首个本土化、历时12个月的答案。数据显示，治疗相关影像学异常（ARIA）总体可控，但疗效呈现出关键异质性：**发病年龄是重要分层因素，早发性AD（EOAD）患者的认知下降速率显著快于晚发性AD（LOAD）患者**。这一发现为临床精准监测与管理提供了紧迫指引。

**从临床试验到临床实践：为什么需要真实世界证据？**
仑卡奈单抗的获批基于全球III期Clarity AD试验，但其在更广泛、日常诊疗环境下的表现，尤其是中国人群的特异性反应，仍是未知数。真实世界研究旨在回答这一核心落地问题：药物在实际医疗场景中的安全性、疗效差异及长期管理策略，是连接试验数据与常规应用的必经桥梁。

**浙大二院主线：安全基线与疗效分层的详细图谱**
来自浙大二院神经内科团队（张宝荣、陈艳兴等）的前瞻性研究为此提供了详细的主线数据。该研究纳入76名早期AD患者，ApoEε4携带率为64.5%。截至分析时，12例患者完成了长达12个月的随访。

**ARIA可控但需影像筛查**
输液相关副作用（IRSE）发生率为18.4%，多出现于首次输注。共11例患者出现ARIA，均为无症状性。值得注意的发现是，出现孤立性微出血（ARIA-H）的患者，其基线脑白质高信号（Fazekas评分）显著更高，这提示基线磁共振成像（MRI）评估对于风险预判至关重要。研究还记录到一例特殊病例，其淀粉样蛋白PET（SUVr）在随访中不降反升（从1.278升至1.523），提示了精准医学时代下个体反应的复杂性。

**疗效揭示：早期干预窗口与起病年龄的双重影响**
分析首先确认了早期干预的价值：基线病情更重（临床痴呆评定量表总分[CDR-GS] = 1）的患者，其简易精神状态检查（MMSE）评分下降速度显著快于更早期（CDR-GS = 0.5）的患者（p=0.019）。
更具临床冲击力的发现与起病年龄相关。数据显示，晚发型AD（LOAD）患者组的认知下降速度显著慢于早发型AD（EOAD，发病年龄<65岁）组，后者呈现出更快的认知衰退趋势。进一步分析显示，这种差异并非由ApoEε4基因驱动（EOAD患者携带率未显著更高），也非由基线认知储备单一决定（基线MMSE评分以20分为界分层，两组未见显著疗效差异，提示教育程度不应成为治疗排除标准）。这强烈提示，**发病年龄本身是独立于疾病严重程度和遗传背景的关键疗效分层因素，EOAD患者可能需要更密集的认知监测**。在完成12个月随访的12例患者中，淀粉样蛋白PET显示脑内Aβ负荷较基线显著下降。

**多中心补线：共同指向安全可控与异质性存在**
浙二的发现并非孤例，近期同步发表的多项中国多中心研究，从不同角度提供了佐证与互证。
*   **华西医院牵头多中心研究（通讯作者：陈雪平、商慧芳）**：在68例患者中观察到，治疗2.5及7个月后，认知评分（ADAS-cog14）显著改善，且血浆p-tau181/217持续下降，印证了药物的生物标志物应答。其ARIA-E发生率仅为3.1%，同样支持了安全性在真实世界中可控的判断。
*   **华山医院全国多中心研究（通讯作者：郁金泰等）**：这项迄今最大规模的真实世界队列（407例）显示，ARIA总发生率为12.15%，症状性ARIA罕见（4例），在大样本中进一步夯实了ARIA风险总体可控的结论。
*   **上海瑞金医院海南分院研究（通讯作者：刘军）**：64例患者治疗6个月后，多项认知量表评分保持稳定，为药物延缓疾病进程提供了另一份稳定性证据。

**结论：从安全共识走向精准分层实践**
首批中国真实世界数据明确回答了核心关切：仑卡奈单抗在中国人群中的ARIA风险与全球关键试验数据可比，通过规范影像筛查与监测总体可控。超越安全性共识，数据更深刻地揭示了疗效的异质性图谱。其中，**起病年龄是至关重要的分层变量，早发型AD患者尽管同样安全耐受治疗，但其更快的认知下降趋势提示临床需建立更密集的MMSE监测方案**。这标志着中国AD诊疗实践正从“能否用药”快速转向“如何用好”，为个体化治疗策略的制定投下了第一束现实之光。
~~~

### 五、当前审核意见与返修抓手

1. 总分与当前判定：
   - `k2.5 base -> whole -> whole+local`：`72 / true -> 72 / true -> 72 / true`
   - `deepseek-reasoner base -> whole -> whole+local`：`72 / true -> 72 / true -> 72 / true`
2. 各维度关键失分：
   - 当前硬层主要盯住：一句话新闻导语、浙二主线的关键统计位、EOAD 与 CDR 分层、与 III 期安全性的对齐。
   - 当前软层主要抱怨：多中心补线像并列综述、结尾太像指南、中文仍有模板味。
   - 这题的得分停滞反证了：当前 scorer 对 `news` 场景的模型差异不够敏感。
3. 返修抓手：
   - 不先换总模型，先继续打 `news` 合同与导语问题线。
   - 如果后面再测模型，必须先升级 `news` 场景的 soft 审稿抓手，不然模型差异会继续被吞没。
   - local 当前证明了“能精准执行”，但没有证明“能继续提分”。
4. 人工审核时重点对照项：
   - 看导语是不是一句话硬新闻，而不是问题铺垫。
   - 看浙二是不是主线，还是又被华西/华山/海南分散掉。
   - 看结尾是“新闻收束”，还是“指南腔操作手册”。

## 工程附录

### Runtime 指针

1. `k2.5` 运行目录：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_042559_380_lecanemab_news`
2. `deepseek-reasoner` 运行目录：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_044402_378_lecanemab_news`
3. `k2.5 base draft_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_042559_380_lecanemab_news\compare_snapshots\base\draft_manifest.json`
4. `deepseek base draft_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_044402_378_lecanemab_news\compare_snapshots\base\draft_manifest.json`
5. `k2.5 whole score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_042559_380_lecanemab_news\compare_snapshots\whole\score.json`
6. `deepseek whole score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_044402_378_lecanemab_news\compare_snapshots\whole\score.json`
7. `k2.5 local_revise_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_042559_380_lecanemab_news\local_revise_manifest.json`
8. `deepseek local_revise_manifest.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\contracts\20260412_044402_378_lecanemab_news\local_revise_manifest.json`
9. 总汇总：`D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1\20260412_041831_050_k25_vs_deepseek\model_compare_summary.json`

### 本轮关键证据

1. 泄题边界：两边 base draft manifest 均直接显示 `reference_answer_visible_before_draft=false`、`reference_sample_enabled_for_draft=false`。
2. 三阶段结果：`model_compare_summary.json` 直接记录 `news` 两边全程同分：`72→72→72` 与 `72→72→72`。
3. whole 层判语：两边 `whole score.json` 都直接指出当前问题更像导语/主线/软层分辨力，而不是模型明显失手。
4. local 执行：两边 `local_revise_manifest.json` 都是 `execution_precision_rate=1.0`、`score_after=72`。

### 评分结果

1. `k2.5 whole revise`：
   - 总分：`72`
   - 达标结论：`true`
   - 软层：`editorial_total = 68`
2. `deepseek-reasoner whole revise`：
   - 总分：`72`
   - 达标结论：`true`
   - 软层：`editorial_total = 68`
3. local 执行：
   - `k2.5 local`：`precision=1`，`issue_close=1`，`72 -> 72`
   - `deepseek local`：`precision=1`，`issue_close=1`，`72 -> 72`

### 本轮真实 blocker

1. 这题当前 blocker 不是“哪个模型更强”，而是 `news` 场景的合同问题线和 scorer 分辨力不够。
2. 在现有评分器下，两模型差异被吞没；继续盲测模型的 ROI 已经下降。

### 证据摘要

1. 已直接核对 `draft_prompt.md`、`whitebox_contract.json`、两边候选终稿，确认这份全貌贴的是实际起稿合同与实际终稿，而不是结果表转述。
2. 已直接核对两边 `whole score.json`，确认当前有效结论是：三阶段同分，当前 scorer 对这题模型差异几乎无分辨力。
3. 已直接核对两边 `local_revise_manifest.json`，确认 local 在本题上是“能改准但不继续提分”的执行层。
