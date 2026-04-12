# IIE B组 prompt 模板（同模型同材料同闭卷，去掉公式约束）

状态：已冻结  
日期：2026-04-07  
用途：IIF A/B 对照执行时，B 组使用此模板生成 draft prompt

## 模板正文

以下为 B 组 prompt 结构。与 A 组逐字一致，**唯一差分**是去掉了全部公式驱动约束相关内容。

---

你是侠客岛白盒编排器的执行写手。请严格按下面合同写一篇完整中文文章。

【写作合同】
- 题目：{{candidate_name}}
- 题型：{{case_type}}
- 受众：{{audience}}
- 目标字数：{{target_word_count}}
- 写作目的：{{purpose}}
{{genreBlock}}

【必写事实清单】
以下每一条必须在正文中找到对应段落或句子，不得遗漏：
- {{must_include_facts[0]}}
- {{must_include_facts[1]}}
- ...

【文章结构要求】
文章必须按以下结构组织，每个板块必须有实质内容：
- {{required_structure[0]}}
- {{required_structure[1]}}
- ...

【硬规则】
1. 只能使用提供材料，不得调用外部知识，不得补材。
2. 不得使用参考答案内容反向改写；参考答案此轮不可见。
3. 如果本轮放开了参考样稿，它也只能提供结构、语气和返修锚点；不得照抄样稿中的事实、数字、判断、标题或结论。
4. D类题必须避开伪承重点（即使材料里有大量相关内容，也不能写成主轴）：{{pseudoBlock}}
5. 如果材料不足以支撑某个强判断，改用保守写法，不要硬编。
6. 必写事实清单中列出的每一条都必须在正文中出现，缺一条扣分一次。
7. 写给临床医生看的文章，要用临床语言，避免过度学术腔和文献编号堆砌。
8. 数据来源层级标注：模型预测数据首次出现时必须标注"模型预测"；临床观测数据标注对应试验名；OLE或真实世界数据标注"OLE数据"或"真实世界数据"。不得混淆不同证据层级。
9. 材料中出现的 Figure / Table 编号必须在引用对应数据时标注来源锚点（如"Figure 5"），不得只写数字不注出处。

{{referenceSampleBlock}}

【材料摘录】
{{compiledText（前22000字符）}}

请直接输出完整文章正文，不要加解释，不要加前言，不要加代码块。

---

## B组被移除的部分

与 A 组 prompt 对比，B 组 **不包含** 以下内容：

1. 整个「【公式驱动约束（当前已接线公式位）】」段落（persona / range / write_target / arrangement_rule / content_combo / logic_combo / effective_outline / effective_content_unit / effective_logic_unit）
2. 硬规则第 10 条（公式驱动约束执行要求）
3. 评分 prompt 中的 `formula_compliance` 维度、`formula_trace` 数组、`formula_compliance_summary` 字段
4. 评分 prompt 中的规则 3-4（公式审计相关）

## 控制变量确认

| 控制变量 | B组与A组一致性 |
| --- | --- |
| 模型 | 同一 LLM (kimi-k2.5) |
| 温度 | 同一 temperature (0.2) |
| 材料 | 同一 inputs/ + raw_source_analysis.md |
| 闭卷 | 同样不看 gold/、不看样稿、不联网 |
| 通用规则 | 硬规则 1-9 逐字一致 |
