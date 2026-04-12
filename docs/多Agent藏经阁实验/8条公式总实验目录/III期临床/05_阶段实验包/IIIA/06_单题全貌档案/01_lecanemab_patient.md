# 单题全貌档案：lecanemab_patient

状态：2026-04-11 本轮三题 retest / 已按当前 runtime 更新  
日期：2026-04-11  
用途：人工审核第一读物。先用主阅读层判断患者向题眼、喂料时间点、prompt 约束和当前稿件偏差，再用工程附录回查 runtime。  

case_id: `lecanemab_patient`
task_id: `13d4be80-4f83-4396-be4c-38d15ea43f10`
run_dir: `D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest`

## 当前有效口径

1. 本档只认 2026-04-11 本轮三题 retest 的同轮 runtime 直证，不回收旧 run 或旧聊天结论。
2. 主阅读层已经直接贴出材料整理稿、prompt 全文、当前稿件全文和返修抓手；人工审稿先看这里，不先点路径。
3. 本轮不存在的独立 planning / quality prompt 已明确写缺项；若 `score.json/summary.json` 未生成，也必须在本档中直接写明原因。

## 当前明确缺项

1. 独立 planning prompt：本轮不存在；原因：当前 standard_chain 只在 `stage_artifacts` 与 `review_bundle.planning` 留存 planning 结果，不单独导出 planning prompt 文件。
2. 独立 quality prompt：本轮不存在；原因：当前 quality 只落门禁结果与错误说明，不导出可回读 prompt 文件。
3. 其他缺项：本轮评分与 summary 已落盘，无额外工程缺项。

## 主阅读层

### 一、人工审核先看

1. 写作合同：面向 `患者和家属`；目标字数 `1500`；题眼是“关键获益是否真的足以改写决策？把疗效分析获益翻译成读者能理解的现实变化。写作主轴采用续停药争议裁决，围绕疗效分析证据展开，面向患者和家属完成主张_证据 / 叙事_反思型论证。”。
2. 当前判定：本轮 `score.json` 给出 `56.0/100` 且 `qualified=True`，但 `key_facts=40 < 60`，与当前评分硬门口径冲突；人工先按异常待裁定稿审，不把 PASS 标签当真。
3. 审稿优先看：先看标题、导语、时间点切换句和停药争议段；这些位置最容易把 18 个月结果错写成 4 年患者结论。
4. 当前最该改：先把标题和导语从“18个月差异/停药争议”切回题目真正要求的患者长期获益表达，并给每个关键数字补上明确时间点。
5. 为什么会写歪：本轮 planning thesis 仍然把主轴放在“续停药争议 + 疗效分析转译”，没有直接把 4 年患者收益当第一标题锚点，所以写手自然抓住了 18 个月主终点。

### 二、本轮真正喂给写手的材料（人工整理版）

人工阅读提示：
1. 这题材料相对干净，正式目录事实为主，补充资料只有 1 条；真正风险不在 evidence 缺失，而在时间点和患者转译口径。
2. 人工审核先盯 4 个高风险口径：18个月/36个月/48个月是否混写；无恶化 vs 改善是否混写；风险降低数字是否越界；是否把给药便利性和长期获益硬串成确定结论。

实际入模材料整理稿：
```text
【写手前置合同】
- 题眼 / thesis: 关键获益是否真的足以改写决策？把疗效分析获益翻译成读者能理解的现实变化。写作主轴采用续停药争议裁决，围绕疗效分析证据展开，面向患者和家属完成主张_证据 / 叙事_反思型论证。
- 目标读者: 患者和家属
- 结构大纲: 引言 -> 疗效分析 -> 结论
- 目标字数: 1500

【结构化主干事实】
- 18个月时ADAS-Cog14较基线变化的治疗差异: -1.44 points
- 18个月时ADCOMS下降的相对减缓比例: 24% percentage
- 18个月时ADCS-MCI-ADL下降的相对减缓比例: 37% percentage
- 18个月时淀粉样蛋白PET较基线变化（centiloid值）: -55.48 centiloids
- 18个月时CDR-SB较基线变化的治疗组与安慰剂组差异: -0.45 points
- CDR-SB主要终点的P值: p<0.001 p-value
- 18个月时CDR-SB下降的相对减缓比例: 27% percentage
- Clarity AD研究入组患者总数: 1795 patients

【补充材料 / OCR 主干】
- 长期延续资料仍出现：48个月 amyloid PET 下降 93%，且 CDR-SB 与安慰剂差距继续拉开。
- 延续治疗阶段提示：18 个月双周给药后转为每月维持给药，结局与持续双周相近。
- 安全性延续信息提示：ARIA-E 风险主要集中在前 6 个月，之后没有新的安全信号。
```

### 三、本轮给模型的 prompt 全文

system prompt：
```text
你是侠客岛写作系统的医学编辑。
【核心铁律】只使用本次下发证据中明确出现的数据、数字和结论。严禁从训练知识或外部来源补充任何统计数据、样本量、百分比或年份。严禁编造'中国数据''真实世界验证''获批信息''市场预测'等证据外内容。如果证据中未提供某个具体数字，用定性描述替代（如「研究显示」「数据表明」），绝不编造具体数值。违反此条即为幻觉，将导致 hallucination_control 维度直接不及格。

══════════════════════════════════════
【最高优先级：本文面向患者和家属——以下规则覆盖一切冲突的专业化指令】
══════════════════════════════════════

▎标题规则:
- 标题应优先体现患者可感知的核心结局或最重要的决策信息，但不得为追求冲击力改写、取整或放大数字
- 标题中的任何数字、时间点和适用人群都必须与证据原文一致
- 标题可出现药品通用名，但不得把未经证据支持的希望、承诺或结论写成既成事实
- 禁止学术论文式标题，也禁止营销口号式标题
- 可采用“药品通用名 + 关键结局/关键信息 + 明确时间点或人群”的结构，但必须自行组织语言

▎重要约束:
- 引用证据数字时必须使用证据原文中出现的数字，不得自行计算或推导
- ApoE ε4、非携带者、杂合子等基因术语必须转译为患者能理解的说法（如'大多数患者'）
- 严禁编造'中国数据''中国验证''真实世界数据'等证据材料之外的内容
- 严禁独立成段讲述证据外的市场/流行病学统计

▎情感弧线（必须按此顺序）:
- 开篇：从患者和家属真正关心的长期变化或现实决策问题切入，但必须自行组织语言，不得复用固定示范句
- 核心数据：将关键临床结局转译为患者能理解的变化，但不得虚构生活场景或借用参考答案式表述
- 分层信息：如证据中存在与主结论直接相关的明确亚组/分层数据，可单独解释；没有则不要强造亮点
- 安全性：用'能不能放心用'的患者视角精简讲述，但措辞不得超出证据边界
- 行动提示：只给出当前证据能够支持的下一步判断或沟通建议，不得写成诊疗保证

▎证据使用优先级:
- 最优先：疾病延缓时间、认知稳定比例、风险降低百分比——这些是患者最关心的
- 次优先：安全性数据（发生率趋势、长期稳定性）
- 最低优先：生物标志物定量（PET centiloid、tau定量等）——仅可作背景1-2句提及，严禁独立成段/成节
- 药物机制仅可用1-2句通俗描述，且必须来自当前证据，严禁单独扩展成机制/生物标志物章节
- 引用百分比时必须标注证据中对应的时间点（如'18个月时''长期随访时'），不得混淆不同时间点的数据
- 安全性描述必须跟随证据原文措辞——如证据说'减少或稳定'，不可写成'逐年走低'
- 可用通俗解释帮助理解，但不得虚构患者故事、经历或生活细节来充实篇幅

▎表达铁律:
- 遇到 ADAS-Cog、CDR-SB、ARIA、centiloid、APOE、原纤维等概念，必须先用患者语言解释
- 如使用类比，必须是中性的解释性类比，不得引入证据外结论或固定模板
- 可将抽象量表转译为功能变化维度，但不得虚构具体生活情节
- 禁止使用：裁决、衰减、重构、异质性、序贯、疾病修饰效应、靶向清除等学术/翻译腔词汇
- 下方 L4 产品约束中的专业术语，一律转译为患者能懂的表达后再使用
══════════════════════════════════════

写作策略: M3_PLAY_证据缺口
叙事弧线: ARC_AJMD_001
目标受众: 患者和家属
目标篇幅: 1500 字（允许浮动 ±10%，结构须与篇幅匹配，证据不足时收缩结构而非泛化扩写）

风格要求:
- 语体等级: R4
- 正式程度: informal
- Arc 说明: 极简开篇→情绪铺垫→数据重击→反转收束
- Arc 结构: 极简戏剧化开篇 → 情绪/共识铺垫 → 数据加特林 → 反共识反转 → 冷酷断言收束
- 论点派生规则: 续停药争议裁决
- 论点模式: 直接回应「是否应停药」这一核心临床争议，用数据给出倾向性但非绝对化的答案。

L1 人格内核:
- Persona: End-User Advocate
- 人格说明: 代言人——以终端用户体验为锚点，不接受技术黑话
- 语气DNA: human-centered, rights-aware, concrete
- 注意力顺序: meaningful real-life benefit；risk communication clarity；equity of access
- 默认怀疑: Gains are measurable but not experientially meaningful；Risk language is too technical for informed decision-making
- 偏好证据: user-reported outcomes, accessibility audits, equity data
- 表达倾向参考: What changes for the end user this month；Understandable risk is ethical risk；Access delayed is access denied（只转译倾向，不直接照抄原句）
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

L4 产品关注点（仅在当前证据支持时使用）:
- 必须强调对『原纤维/寡聚体』的清除，不可仅提斑块。；只能作为关注点，不能替代当前证据，也不能倒推出未下发的数字或结论。
- 凡提Clarity AD，如当前证据明确支持，可优先说明ADAS-cog14或CDR-SB的准确百分比数据。；只能作为关注点，不能替代当前证据，也不能倒推出未下发的数字或结论。
- 提及ARIA风险时，必须同时提及MRI监测频率建议和大多数为无症状的定性描述。；只能作为关注点，不能替代当前证据，也不能倒推出未下发的数字或结论。
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
- 风格定位: 以宏大的历史纵深和详实的细节铺陈，将复杂的商业/经济/政治事件转化为引人入胜的硬核故事，兼具学术严谨与通俗张力。
```

user prompt：
```text
主题: 关键获益是否真的足以改写决策？把疗效分析获益翻译成读者能理解的现实变化。写作主轴采用续停药争议裁决，围绕疗效分析证据展开，面向患者和家属完成主张_证据 / 叙事_反思型论证。

大纲:
1. 引言
2. 疗效分析
3. 结论

【必须覆盖的关键事实与数字】
下列事实必须全部进入正文；可以转译表达，但不得改数字、时间点、适用人群，也不得把不同时间点混写。
- 必写1: 18个月时ADAS-Cog14较基线变化的治疗差异；原始数字 -1.44 points
- 必写2: 18个月时ADCOMS下降的相对减缓比例；原始数字 24% percentage
- 必写3: 18个月时ADCS-MCI-ADL下降的相对减缓比例；原始数字 37% percentage
- 必写4: 18个月时CDR-SB较基线变化的治疗组与安慰剂组差异；原始数字 -0.45 points
- 必写5: 18个月时淀粉样蛋白PET较基线变化（centiloid值）；原始数字 -55.48 centiloids
- 必写6: 18个月时CDR-SB下降的相对减缓比例；原始数字 27% percentage

【章节篇幅预算】
- 引言: 约 150 字（约 10%）
- 结论: 约 150 字（约 10%）
- 疗效分析: 约 1200 字（约 80%）
- 若总字数不足，优先补足主体分析段，不要只扩标题、引言或结尾。

证据详情:

【efficacy】
- Change from baseline in ADAS-Cog14 at 18 months (treatment difference): -1.44 points
- Relative reduction in ADCOMS decline at 18 months: 24% percentage
- Relative reduction in ADCS-MCI-ADL decline at 18 months: 37% percentage
- Amyloid PET change from baseline at 18 months (centiloids): -55.48 centiloids
- Change from baseline in CDR-SB at 18 months (treatment difference): -0.45 points
- P-value for CDR-SB primary endpoint: p<0.001 p-value
- Relative reduction in CDR-SB decline at 18 months: 27% percentage
- Total enrolled patients in Clarity AD: 1795 patients
- {'content': 'Lecanemab treatment resulted in 93% reduction in amyloid PET at 48 months with continued separation from placebo group in CDR-SB outcomes', 'page': 11}: see_definition None
- {'content': 'Simulation outcomes show lecanemab has greater impact on cognitive outcome earlier in the disease (MCI stage vs Mild AD stage)', 'page': 13}: see_definition None
- {'content': 'Monthly maintenance dosing provides similar outcomes as continuous biweekly treatment after initial 18-month biweekly treatment', 'page': 14}: see_definition None
- {'content': 'Lecanemab disrupts tau accumulation across brain regions, with impact seen in earliest medial temporal regions in no/low tau group and broader impact in intermediate/high tau group', 'pag: see_definition None


【正式资产锚点】
- 论点规则: THESIS_R1
- 论点规则: THESIS_R2
- 论点规则: THESIS_R3
- 论点分类: 主张_证据
- 论点分类: 主张_证据
- 论点分类: 主张_证据 / 对比_推荐
- 论点规则: THESIS_R10
- 论点派生: 续停药争议裁决
- 论点分类: 主张_证据
- 论点分类: 叙事_反思
- 论点模式: 直接回应「是否应停药」这一核心临床争议，用数据给出倾向性但非绝对化的答案。
- 论点模板: {停药相关争议问题}？{数据支持的答案}
- 人格内核: End-User Advocate
- L4变量组: VAR_TARGET_PATHWAY
- L4变量组: VAR_EFFICACY_NUM
- L4变量组: VAR_SAFETY_RISK
- L4变量组: VAR_BIOMARKER_CHANGES
- L4关注点: M3_U_B_MECHANISM_DEEPDIVE: 必须强调对『原纤维/寡聚体』的清除，不可仅提斑块。；只能作为关注点，不能替代当前证据，也不能倒推出未下发的数字或结论。
- L4关注点: M3_U_B_TRIAL_DATA: 凡提Clarity AD，如当前证据明确支持，可优先说明ADAS-cog14或CDR-SB的准确百分比数据。；只能作为关注点，不能替代当前证据，也不能倒推出未下发的数字或结论。
- L4关注点: M3_U_B_SAFETY_MANAGEMENT: 提及ARIA风险时，必须同时提及MRI监测频率建议和大多数为无症状的定性描述。；只能作为关注点，不能替代当前证据，也不能倒推出未下发的数字或结论。

【患者向写作提示——请务必遵守】
1. 优先呈现患者可感知的临床结局，但所有数字、时间点和适用人群必须与证据原文一致
2. 如存在与主结论直接相关的明确亚组/分层数据，可单独成段解释；没有就不要强造亮点
3. 将原始评分量表、基因分型和机制术语转为患者能理解的说法，但不得改变原意
4. 机制/生物标志物/PET 数据仅在确有必要时简要说明，且不独立成段
5. 同一指标若有多个时间点，必须明确标注各自时间点和口径，不得默认用较晚时间点覆盖较早数据
6. 如使用类比或通俗解释，必须服务理解且不虚构故事、不加入证据外情节
7. 不优先展开样本量、HR值、P值、入组比例等研究者口径指标，除非它们直接影响患者理解某项核心风险或获益
8. 严禁添加证据之外的内容（如'中国数据''真实世界验证'等），只用上方下发的证据
请根据以上信息生成文章，目标字数约 1500 字（±10%），
结构须与篇幅相匹配，避免泛化扩写。
```

### 四、当前稿件全文

1. 生成稿全文（必须直接贴入，不得只写路径）：

```text
# 停药还是继续？把数字翻译成生活里的答案

一位患者用了18个月药，认知测试分数比没用药的人少掉了0.45分。这到底是该庆祝，还是该失望？

---

## 一、疗效分析：0.45分意味着什么

阿尔茨海默病的临床量表（CDR-SB）满分为18分，分数越高，独立生活能力越差。0.45分的差距，放在18分的量表上看似微小，但研究给出的信号是明确的：18个月时，用药组的认知功能衰退速度比安慰剂组慢了27%。

这不是治愈。但"慢27%"翻译成日常，是穿衣、算账、记住约会这些事的退化节奏被拖长了。研究同时显示，另一项综合认知评估（ADCOMS）的下降速度减缓了24%，而日常活动能力量表（ADCS-MCI-ADL）的衰退则慢了37%——后者直接对应患者能否自己管理药物、处理财务、保持社交。

更值得细读的是ADAS-Cog14的数据：18个月时，用药组与安慰剂组的认知测试分数差距为-1.44分。这个量表满分70分，覆盖记忆、语言、定向等多个维度。1.44分的差距，约等于早期患者在"单词回忆"子项上多记住1-2个词，或"命名物品"时少犯一次错。对家属而言，这可能是某次对话里，患者突然叫出了孙辈的名字，而非沉默以对。

生物标志物的变化更为剧烈：淀粉样蛋白PET扫描显示，18个月时患者脑内斑块负荷下降了55.48 centiloids。这个数字患者无需深究，但它解释了为什么认知变化虽慢却真实——药物确实在清除致病蛋白，而清除的对象不仅是沉积的斑块，更包括正在扩散的原纤维和寡聚体。这些中间形态的蛋白被认为是神经毒性的主要来源。

---

## 二、时间窗口：为什么"早"比"久"更关键

研究提示了一个容易被忽略的分层：疾病阶段越早，药物对认知结局的影响越大。模拟数据显示，处于轻度认知障碍（MCI）阶段开始用药，比已进入轻度痴呆阶段再用药，长期获益更为显著。

这指向一个残酷的决策现实：停药争议往往发生在用药18个月后——恰好是现有证据最充足的时间点。但此时患者可能已经滑入更晚期的阶段，药物能挽回的空间正在收窄。

更长的随访数据提供了另一把标尺：48个月时，持续用药组的淀粉样蛋白清除率达到93%，且CDR-SB评分与安慰剂组的差距持续拉开。这意味着获益并非昙花一现，而是随时间累积。同时，一项关键的操作性发现是：完成18个月的双周输注后，转为每月维持给药，疗效与持续双周给药相当。这为长期用药的便利性提供了出口，也降低了"终身输液"带来的心理负担。

---

## 三、安全与监测：能不能放心继续

任何长期用药决策都必须穿过安全性的窄门。该类药物最突出的风险是ARIA（淀粉样蛋白相关影像异常），表现为脑水肿或微出血。证据中的定性描述是：大多数ARIA为无症状，通过定期MRI监测可识别和管理。

"大多数无症状"是关键词。这意味着风险并非等同于灾难，而是需要纳入监测流程的可控事件。MRI监测频率的建议应遵循临床指导——通常是治疗初期密集扫描，稳定后延长间隔。患者和家属需要与医生确认的具体问题是：下一次扫描安排在何时？出现哪些症状需要立即就诊？

长期安全性数据显示，ARIA发生率在治疗后期趋于稳定或下降，而非随累积剂量递增。这为"继续用药"提供了风险层面的支撑。

---

## 四、反转：为什么"足够好"成了最难接受的答案

回到开篇的0.45分。批评者指出，这一效应量低于患者和家属的直观期待——没有人愿意为"可能多记住一个单词"而每月奔波输液。这种落差是真实的，也是争议的根源。

但数据支持的反转在于：阿尔茨海默病的既往治疗从未在此类指标上显示出统计学显著且方向一致的获益。27%的减缓、37%的日常功能保护、持续四年的疗效分离——这些数字在过往20年的药物研发史中几乎空白。它不是"足够好"的绝对标准，而是"比没有更好"的相对突破。

更关键的反转是停药时机。若因"效果不明显"而在18个月停药，可能恰好截断了获益累积的拐点——48个月的93%蛋白清除和持续认知分离，前提是用药不中断。停药决策的风险不是"浪费钱"，而是"关闭了一个需要时间才能兑现的窗口"。

---

## 五、冷酷断言：这不是答案，是问题的重新表述

是否继续用药？证据给出的倾向性答案是：如果18个月时耐受良好，且患者仍处于轻度阶段，继续治疗的获益-风险比倾向于支持维持。但这一判断必须个体化——患者的输液负担、照护者精力、经济可及性、对"延缓"而非"逆转"的心理接受度，都是证据无法裁决的变量。

药物清除了原纤维和寡聚体，但它清除不了决策的复杂性。0.45分是一个数字，也是一个提醒：在阿尔茨海默病领域，"足够好"的治疗本身就是稀缺的。患者和家属需要做的，不是被数字说服或吓退，而是带着这些数字，与医生讨论"对我家而言，下18个月值不值得"。
```

### 五、当前审核意见与返修抓手

1. 总分与当前判定：`56.0/100`；`qualified=True`；评分状态 `ok`。
2. 各维度关键失分：
- `任务完成度` `60.0`：文章确认为患者向文章，也涉及仑卡奈单抗疗效，但核心内容是18个月数据，而题目明确要求的是4年数据，导致核心任务偏离
- `关键事实与关键数字覆盖` `40.0`：标准答案中的关键数字10-15个月延缓、55%风险降低、72%极早期患者4年不变差均未出现，反以18个月数据（0.45分）为主
- `受众匹配与文风匹配` `70.0`：语体基本匹配患者受众，有生活化类比解释专业术语，但AI味偏重影响了患者向的亲和力
- `AI味儿控制` `50.0`：标题'停药还是继续？把数字翻译成生活里的答案'有明显的模板感，结构为典型的五段式'疗效-时间窗口-安全-反转-结论'，语言过于工整刻意
- `结构与信息取舍` `65.0`：逻辑递进清晰，信息从疗效到决策逐步深入，但信息取舍有偏差，将18个月数据作为重点而忽视了4年数据这一核心
- `标题角度与稿型适配` `70.0`：标题有患者视角的决策导向，但相比标准答案'抢回15个月黄金时光'的新闻感和情绪冲击力偏弱，更像常规科普标题
- `幻觉与越界编造控制` `60.0`：主要数据有出处，但存在过度推断如'18个月后停药会截断获益拐点'，以及'完成18个月后转为每月维持给药'等超出原文的描述
3. 返修抓手：
- 把 18 个月主终点和长期延续结论拆开，不再用 18 个月数据直接回答 4 年题眼。
- 逐段强制标出时间点，所有带数字的句子都要能回答“这是 18、36 还是 48 个月”。
- 删掉“停药会截断获益拐点”“每月维持给药已经足以回答患者决策”等超出证据边界的推论。
- 把标题角度从“是否继续/停药争议”切回“长期获益到底给患者带来什么”，减少争议型噱头。
4. 人工审核时的重点对照项：先看标题、导语、时间点切换句和停药争议段；这些位置最容易把 18 个月结果错写成 4 年患者结论。

## 工程附录

### Runtime 指针

1. `run_summary.md`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\run_summary.md`
2. `task_detail.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\task_detail.json`
3. `generated.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\generated.txt`
4. `materials_full.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\materials_full.json`
5. `review_bundle.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\review_bundle.json`
6. `score.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\score.json`
7. `summary.json`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\summary.json`
8. `writing_system_prompt.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\writing_system_prompt.txt`
9. `writing_user_prompt.txt`：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\writing_user_prompt.txt`

### 本轮关键证据

1. 上传与 evidence：`fact_count=21`；`catalog_fact_count=20`；`supplement_fact_count=1`；`supplement_upload_failures=0`。
2. 阶段到达情况：`evidence=completed`；`planning=completed`；`writing=completed`；`drafting=completed`；`quality=completed`；`delivery=completed`；`score=completed`；`review_bundle=present`。
3. 交付与评分：`task_status=completed`；`halted_at=None`；`quality_overall_status=passed`；`final_docx_word_count=1573`；`target_word_count=1500`；`weighted_total=56.0`；`qualified=True`。
4. planning / writing 卡片：planning=`关键获益是否真的足以改写决策？把疗效分析获益翻译成读者能理解的现实变化。写作主轴采用续停药争议裁决，围绕疗效分析证据展开，面向患者和家属完成主张_证据 / 叙事_反思型论证。`；writing=`本轮写作任务：围绕“关键获益是否真的足以改写决策？把疗效分析获益翻译成读者能理解的现实变化。写作主轴采用续停药争议裁…”写作。
面向读者：患者和家属；目标字数：1500。
结构重点：引言、疗效分析、结论`。

### materials 指针

1. 当前人工审稿材料文件：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\materials_full.json`
2. 同轮回退锚点：`task_detail.json -> output_data.evidence / stage_artifacts.evidence`；`review_bundle.json -> materials / evidence`

### prompt 指针

1. system prompt：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\writing_system_prompt.txt`
2. user prompt：`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\writing_user_prompt.txt`
3. 同轮回退锚点：`review_bundle.json -> writing.system_prompt / writing.user_prompt`

### 评分结果

1. 总分：`56.0/100`
2. 达标结论：`qualified=True`
3. 评分状态：`ok`
4. 各维度：
- `任务完成度` `60.0`：文章确认为患者向文章，也涉及仑卡奈单抗疗效，但核心内容是18个月数据，而题目明确要求的是4年数据，导致核心任务偏离
- `关键事实与关键数字覆盖` `40.0`：标准答案中的关键数字10-15个月延缓、55%风险降低、72%极早期患者4年不变差均未出现，反以18个月数据（0.45分）为主
- `受众匹配与文风匹配` `70.0`：语体基本匹配患者受众，有生活化类比解释专业术语，但AI味偏重影响了患者向的亲和力
- `AI味儿控制` `50.0`：标题'停药还是继续？把数字翻译成生活里的答案'有明显的模板感，结构为典型的五段式'疗效-时间窗口-安全-反转-结论'，语言过于工整刻意
- `结构与信息取舍` `65.0`：逻辑递进清晰，信息从疗效到决策逐步深入，但信息取舍有偏差，将18个月数据作为重点而忽视了4年数据这一核心
- `标题角度与稿型适配` `70.0`：标题有患者视角的决策导向，但相比标准答案'抢回15个月黄金时光'的新闻感和情绪冲击力偏弱，更像常规科普标题
- `幻觉与越界编造控制` `60.0`：主要数据有出处，但存在过度推断如'18个月后停药会截断获益拐点'，以及'完成18个月后转为每月维持给药'等超出原文的描述

### 本轮真实 blocker

1. 当前主链没有 workflow blocker，evidence -> delivery -> review_bundle -> score 都已落盘。
2. 当前真实 blocker 是内容事实与评分口径双重异常：正文仍抓住 18 个月疗效主终点，而 `score.json` 又给出 `56.0/100 + qualified=True` 的冲突结果。
3. 下一棒应先修患者向主线与时间点，再单独核评分 `qualified` 口径为什么没有被 `key_facts<60` 拉成不达标。

### 证据摘要

1. 已直接核对 `D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\summary.json`，本轮 `weighted_total=56.0`、`qualified=True`、`delivery_gate_passed=True`、`scoring_gate_passed=True`。
2. 已直接核对 `D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\task_detail.json`，本轮阶段卡片完整到 `delivery`，`supplement_fact_count=1`、`supplement_upload_failures=[]`。
3. 已直接核对 `D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\writing_system_prompt.txt`、`D:\汇度编辑部1\侠客岛-runtime\iiia_rerun_20260411_post_noise_cleanup\20260411_173225_738_IIIA_20260411_retest\lecanemab_patient\writing_user_prompt.txt` 与 `generated.txt`，主阅读层贴出的 prompt 与正文均来自本轮 runtime。
