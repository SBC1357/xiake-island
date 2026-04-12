# IID IIC失败样式重归因表

状态：已填写 / 首轮归因版  
日期：2026-04-06  
用途：`IID` 正式执行资产；把 `IIC` 已知失败样式逐条压回到公式位缺口和管线层缺口，直接驱动 `IIE` 首批施工包。

## 证据摘要

- 已直接核对 [03_题型验证结果.md](03_题型验证结果.md) 的 `F1 / F2 / G1 / G2` 结果卡，确认 `IIC` 的真实失败不是“路线完全错”，而是集中在图表 exact value 入链、临床上下文不足、稿面张力不足、原始输出留痕不完整。
- 已直接核对 [00_状态卡.md](00_状态卡.md)，确认白盒高频失败模式已经被正式压成 `materials_coverage / writing_contract / input_contract / orchestration_contract` 四类。
- 已直接核对 [IID_8公式缺位矩阵.md](IID_8公式缺位矩阵.md)，确认当前只有 `写作目的` 直接编码，`文章大纲` 通过 `required_structure` 代理写入，`写作目标 / 写作范围 / 最小有效内容单元` 只是残余代理，其余 `10` 位缺失。

## 归因口径

1. 本表优先把失败样式回指到 `15` 个公式位。
2. 如某条问题本质上不属于公式位缺失，而是运行留痕或证据链断档，必须直接写明，不强行伪装成公式问题。
3. `问题层级` 允许出现 `runtime_trace`，专门承接“原始产物没留全”这类不属于 `contract / materials / draft_prompt / scoring` 四层的执行缺口。

## 重归因表

| # | 失败样式 | 对应缺失公式位 | 问题层级 | OPT-01/02 已覆盖？ | 进入 IIE 施工包 | 直接依据 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `IIC` F1：患者向文章稿面未达“会写”标准 | `人格`、`有效大纲` | `draft_prompt` / `scoring` | 否 | 补患者向 `persona` 约束；补“可交付成稿”表达线；补 `effective_outline` 检查 | [03_题型验证结果.md](03_题型验证结果.md) 明确写了“患者支方向没跑偏，但读者牵引、场景承重与患者决策翻译不足” |
| 2 | `IIC` F1：题面要求保留的 `72%` exact value 未稳定写入 | `最小有效内容单元` | `materials` | 部分覆盖（仅 `OPT-02` 锚点透传，不解决 exact value 抽取） | 补图表 exact value 结构化抽取；把关键 figure/table 数字升为材料层显式单元 | [03_题型验证结果.md](03_题型验证结果.md) 明确写了“PDF 文本层无法稳定抽出 `72%` 精确值” |
| 3 | `IIC` F2：机制科普稿面临床上下文不足、答案丰满度不够 | `最小有效内容单元`、`内容组合`、`文章大纲` | `materials` / `draft_prompt` | 否 | 补机制题的临床上下文单元；补“机制解释 + 临床意义”组合；把大纲从代理约束升级为公式驱动 | [03_题型验证结果.md](03_题型验证结果.md) 明确写了“系统只吃住了机制论文本体，没吃住更强临床上下文与答案丰满度” |
| 4 | `IIC` F2：成稿张力不足 | `人格`、`有效大纲` | `draft_prompt` / `scoring` | 否 | 补标题张力、节奏控制、读者牵引的表达线；评分补 `AI味儿 / 可交付性` 闸门 | [03_题型验证结果.md](03_题型验证结果.md) 明确写了“会解释，但还不会写成外部可交付科普稿” |
| 5 | 白盒高频失败：`materials_coverage` 不足 | `最小有效内容单元`、`内容组合` | `materials` | 部分覆盖（`OPT-02` 只补锚点，不补 coverage） | 补材料层单元化与 coverage 审计；把关键事实、关键比较位、关键锚点一起写进材料合同 | [00_状态卡.md](00_状态卡.md) 已正式记录高频失败集中到 `materials_coverage` |
| 6 | 白盒高频失败：`writing_contract` 缺失 | `写作目的`、`人格`、`写作范围`、`文章大纲` | `contract` | 否 | 先补 `persona / range / outline` 字段，停止只靠 `purpose + required_structure` 兜底 | [00_状态卡.md](00_状态卡.md) 已正式记录高频失败集中到 `writing_contract` |
| 7 | 白盒高频失败：`input_contract` 缺失 | `最小内容单元`、`最小有效内容单元`、`内容组合` | `materials` | 部分覆盖（`OPT-02` 仅覆盖 figure/table 锚点角落） | 补 `input_contract` 的内容单元、比较位、关键数字、来源锚点 | [00_状态卡.md](00_状态卡.md) 已正式记录高频失败集中到 `input_contract` |
| 8 | 白盒高频失败：`orchestration_contract` 缺失 | `最小逻辑单元`、`最小有效逻辑单元`、`逻辑组合`、`有效大纲` | `contract` / `draft_prompt` | 否 | 补逻辑位路由、有效大纲推导、伪承重点之外的正承重点 | [00_状态卡.md](00_状态卡.md) 已正式记录高频失败集中到 `orchestration_contract` |
| 9 | `IIC` 过程缺陷：原始逐字系统稿未单独留档 | `无（非公式位，属证据链缺口）` | `runtime_trace` | 否 | 补 runtime 留痕 schema；把 `draft.txt / draft_manifest.json / score.json / score_manifest.json` 设为整稿题强制产物 | [03_题型验证结果.md](03_题型验证结果.md) 明确写了“原始逐字系统稿未单独留档” |
| 10 | 当前 scoring 只做参考答案对照，不检查公式推导链 | `写作目的`、`写作范围`、`文章大纲`、`有效大纲` | `scoring` | 否 | 上线 `formula_trace` 闸门和公式合规评分；未留 trace 的题直接判 `Step 2` 不过 | [run_ii_whitebox_score.ps1](../../../侠客岛白盒编排器/run_ii_whitebox_score.ps1) 当前只要求五维对照分和 backtrace，没有公式 trace 检查 |

## 归因汇总

| 问题层级 | 涉及失败样式数 | 涉及缺失公式位 |
| --- | --- | --- |
| `contract` | `2` | `写作目的`、`人格`、`写作范围`、`文章大纲`、`最小逻辑单元`、`最小有效逻辑单元`、`逻辑组合`、`有效大纲` |
| `materials` | `4` | `最小内容单元`、`最小有效内容单元`、`内容组合`、`文章大纲` |
| `draft_prompt` | `4` | `人格`、`有效大纲`、`内容组合`、`文章大纲`、`最小逻辑单元`、`逻辑组合` |
| `scoring` | `3` | `写作目的`、`写作范围`、`文章大纲`、`有效大纲` |
| `runtime_trace` | `1` | `无（非公式位）` |

## 与 OPT 覆盖关系

| OPT 编号 | 覆盖的失败样式 | 未覆盖的残余 |
| --- | --- | --- |
| `OPT-01`（数据来源层级标注） | 只覆盖“证据层级不要混写”这一个角度 | 不解决 `persona / range / outline / effective_outline`，也不解决稿面张力和材料 coverage |
| `OPT-02`（figure/table 锚点透传） | 对 `72% exact value`、`input_contract`、`materials_coverage` 只起到部分辅助 | 不解决 exact value 抽取本身，也不解决内容单元结构化、组合规则、逻辑位路由 |

## 当前结论

1. `IIC` 的失败主因不在“路线完全错”，而在 `materials -> draft_prompt -> contract` 三层缺位叠加。
2. 最先该进 `IIE` 的不是继续多跑题，而是：
   - 补 `materials` 层的 exact value / 内容单元结构化
   - 补 `contract` 层的 `persona / range / outline / effective_outline`
   - 补 `draft_prompt` 层的表达线和公式展开
   - 补 `scoring` 层的公式合规与 `formula_trace` 闸门
3. `OPT-01 / OPT-02` 已证明有用，但只能覆盖局部提分点，远不足以替代 `8` 公式全链路编码。
