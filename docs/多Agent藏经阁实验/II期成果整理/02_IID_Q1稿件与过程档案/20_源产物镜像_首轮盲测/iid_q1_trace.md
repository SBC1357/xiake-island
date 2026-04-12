# IID Q1 盲测留痕

日期：2026-04-06  
题目：ctad_p279_c / CTAD P279 长期治疗机制支撑  
性质：IID 第1题盲测，不看gold、不看样稿、不吃答案形约束

## 执行链

1. 读取 `raw_source_analysis.md`（等老刘-P279（学士）目录）
2. 运行白盒 orchestrator -> 合同生成成功（exit 0）
3. 运行白盒 materials -> 素材编译成功（exit 0）
4. 运行白盒 draft -> LLM API 报错（exit 1）
   - 错误：`llm_request_failed: MethodNotAllowed {"error": "Coding Plan is currently only available for Coding Agents"}`
   - 根因：`.env` 中 `OPENAI_BASE_URL=https://coding.dashscope.aliyuncs.com/v1` 是 coding agent 专用端点，不兼容通用 chat/completions
   - 处理：总控按同一合同（writing_contract + compiled materials + raw_source_analysis.md）直接出稿
5. 盲审通过，附2项返修
6. 返修完成（draft_v2.txt）

## 盲审回执

- 判定：**支持**
- 5/5 必写事实全部命中
- 5/5 结构板块全部有实质内容
- 0 一票否决项触发
- 返修项：(a) 补数据来源层级标注；(b) 补 figure/table 锚点引用
- 返修已完成

## 后验校准（盲测完后回看 raw_source_analysis.md 验证）

- raw_source_analysis.md 中提示的关键数字全部命中
- raw_source_analysis.md 中提示的"预测值和观察值要分开看"已在返修中修正
- raw_source_analysis.md 中提示的"Figure 5/6 是最重要锚点"已在返修中补标

## 系统优化发现

### OPT-01: writing_contract 缺 data_source_labeling 字段
- 问题：合同不要求写手区分"模型预测值"和"临床观测值"
- 后果：初稿混用两类数据层级
- 修复：在 writing_contract 增加 data_source_labeling 规则
- 沉淀对象：ii_candidate_pool.json / writing_contract 层 / 所有含模型预测的C类题

### OPT-02: input_contract 缺 figure_table_anchors 透传
- 问题：材料编译阶段不保留 figure/table 编号，writing_contract 的 must_include_facts 没有锚点信息
- 后果：写手无法回指具体 figure
- 修复：materials 编译时提取并保留 figure/table 编号，透传到 draft prompt
- 沉淀对象：run_ii_whitebox_materials.ps1 / input_contract 层

### 工程待办（非写作系统优化）
- LLM API endpoint 需从 coding.dashscope.aliyuncs.com 切换到通用 chat/completions 端点
- 或在 whitebox_common.ps1 中增加 fallback 端点逻辑

## 运行产物清单

- 合同：`D:\汇度编辑部1\侠客岛-runtime\iid_q1_blind_test\20260406_185457_405_ctad_p279_c\whitebox_contract.json`
- 素材：`D:\汇度编辑部1\侠客岛-runtime\iid_q1_blind_test\20260406_185457_405_ctad_p279_c\materials\`
- Prompt：`D:\汇度编辑部1\侠客岛-runtime\iid_q1_blind_test\20260406_185457_405_ctad_p279_c\draft_prompt.md`
- 初稿：`D:\汇度编辑部1\侠客岛-runtime\iid_q1_blind_test\20260406_185457_405_ctad_p279_c\draft.txt`
- 返修稿：`D:\汇度编辑部1\侠客岛-runtime\iid_q1_blind_test\20260406_185457_405_ctad_p279_c\draft_v2.txt`
- 本留痕：`D:\汇度编辑部1\侠客岛-runtime\iid_q1_blind_test\20260406_185457_405_ctad_p279_c\iid_q1_trace.md`
