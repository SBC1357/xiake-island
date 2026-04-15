# III期系统 Persona 注入适配分析

- 日期：2026-04-15
- 状态：升级版 / 已切到当前白盒节点口径
- 性质：经验裁决层工作版，不直接替代正式 protocol；需要与当前白盒脚本和实测结果一起使用

## 这份文档现在解决什么

一句话：这份文档不再按旧 `03A / 03B / 04 / 05 / 06 / 07` 节点名讨论 Persona，而是按当前白盒节点来回答两件事：

1. 哪些节点适合强化 Persona / 认知框架。
2. 哪些节点不该上强 Persona，而应该保持中性、协议优先。

## 证据摘要

1. [whitebox_common.ps1](../../../侠客岛白盒编排器/whitebox_common.ps1) 里的 `Build-WhiteboxPromptWithProfile` 证明：当前系统真实 prompt stack 是先拼 `profile.prompt_prefix`，再接节点 prompt 正文，不是“单独一层 Persona 引擎”。
2. [whitebox_llm_profiles.json](../../../侠客岛白盒编排器/config/whitebox_llm_profiles.json) 证明：当前所有主要节点都已经有自己的 `prompt_prefix`，也就是都已经带有模块角色上下文。
3. [prompts](../../../侠客岛白盒编排器/prompts) 目录下当前白盒节点 prompt 已齐全，说明现在讨论的不是“要不要有角色”，而是“哪些节点要不要把角色进一步强化成更强认知框架”。

## 先说清楚：当前系统里的 Persona 到底是什么

当前白盒系统里，Persona 不是一层单独外挂的“人物扮演 prompt”，而是当前 prompt stack 里的角色上下文增强。

当前真实组合是：

1. `profile.prompt_prefix`
2. 节点 prompt 正文
3. 运行时注入的上游产物 / 材料 / 资产
4. 输出格式或协议约束

所以这份文档讨论的“Persona 注入”，更准确地说是：

**是否要把某个节点的 `prompt_prefix` 从普通模块角色，升级成更强的认知框架。**

## 核心判断框架

判断标准只有一句：

**这个节点的核心动作，是“理解与构思”，还是“执行与裁定”？**

### 适合强化 Persona 的节点

- 需要从材料里找主线
- 需要组织论证顺序
- 需要把复杂内容写成人类能读的成熟文本
- 需要补充证据搜索策略

### 不适合强化 Persona 的节点

- 主要做字段冻结
- 主要做结构化提取
- 主要做边界裁决
- 主要做局部执行精修
- 主要做协议性审核

## 当前白盒节点适配矩阵

| 当前节点 | 核心动作 | Persona 适配度 | 推荐认知框架 | 风险说明 |
| --- | --- | --- | --- | --- |
| `layer1_main` | 分流判断 | 低 | 不建议上强 Persona | 需要中立判断，不该被写作偏好带偏 |
| `layer1_sp` | 澄清 / 反问 / 路线比较 | 低到中 | 可保留“澄清型助手”气质，但不建议编辑 Persona | 太强 Persona 会抢答、替用户补意思 |
| `intent_extraction` | 结构化提取用户意图 | 低 | 不建议上强 Persona | 这是提取，不是写作 |
| `evidence_preprocessing` | 证据清洗与顺读文档化 | 低 | 不建议上强 Persona | 需要稳定提取，不需要写作者倾向 |
| `sample_boundary` | 样稿边界判断 | 低 | 不建议上强 Persona | 需要边界中性，不能带审美偏好 |
| `writing_contract` | 合同编译 | 低 | 不建议上强 Persona | 这是编译层，协议优先 |
| `viewpoint` | 冻结核心主张与医学策略 | 高 | `医学策略主编 / 资深观点编辑` | 这是最适合做强认知框架的节点之一 |
| `pre_review` | 开写前结构化风险判断 | 低到中 | 可用 `冷静审核官`，不宜强 Persona | 太强 Persona 会把前审写成意见文章 |
| `outline` | 组织结构、桥接、承重点 | 中到高 | `内容架构师 / 结构编辑` | 适合增强结构直觉，但不能压过合同与观点卡 |
| `draft_first` | 首稿写作 | 高 | 按受众/稿型绑定的写作者认知框架 | 这是 Persona 收益最大的节点之一 |
| `draft_revise` | 整稿重构 | 高 | 继承首稿认知框架，但必须服从整改卡 | 如果 Persona 太强，容易借整改之名重写过头 |
| `post_review` | 成稿终裁与三流分诊 | 中 | `事实核查总编 / 成品验收主编` | 只能中度增强，协议和边界必须压住 Persona |
| `local_patch` | 小范围精修执行 | 低 | 不建议上强 Persona | 需要最小改动，强 Persona 会越界改写 |
| `local_patch_audit` | 局改验收 | 低 | 不建议上强 Persona | 需要冷静裁定，不需要风格立场 |
| `supplementary_evidence` | 缺口补证与搜索策略 | 中到高 | `调查研究员 / 情报编辑` | 适合增强搜索与筛证能力，但不能回填污染主证据包 |

## 当前推荐组合

这里的“组合”指的是：

`profile.prompt_prefix` + `prompt_file` + 运行时注入 + 协议约束

### 第一优先级：应该优先测试的组合

| 组合 ID | 节点 | 推荐组合 | 目标 |
| --- | --- | --- | --- |
| `VP-1` | `viewpoint` | 当前模块角色 + `医学策略主编` 认知框架 | 看观点层能否更稳地锁主张、主线和论证路线 |
| `OL-1` | `outline` | 当前模块角色 + `内容架构师` 认知框架 | 看大纲是否更会搭桥，不重复观点层 |
| `DF-1` | `draft_first` | 当前模块角色 + 按受众绑定的写作者框架 | 看成稿是否既贴合同又更像成熟人稿 |
| `DR-1` | `draft_revise` | 继承 `draft_first` 认知框架 + 强整改纪律 | 看整稿重构时能否兼顾修准与不乱改 |
| `SE-1` | `supplementary_evidence` | 当前模块角色 + `调查研究员` | 看补证是否更会找缺口、挑证据 |

### 第二优先级：可测，但要防 Persona 抢协议

| 组合 ID | 节点 | 推荐组合 | 风险 |
| --- | --- | --- | --- |
| `PR-1` | `post_review` | 当前模块角色 + `事实核查总编` | 可能增强诊断质量，也可能让后审写得更主观 |
| `PV-1` | `pre_review` | 当前模块角色 + `冷静审核官` | 只能轻微增强，不应把前审变成成稿评论 |

## 当前不推荐组合

这些不是“永远不能测”，而是当前系统里大概率得不偿失：

| 节点 | 不推荐组合 | 原因 |
| --- | --- | --- |
| `layer1_main` | 编辑/作者型 Persona | 会干扰分流中立性 |
| `layer1_sp` | 资深编辑 Persona | 会让系统替用户补意思，而不是先问清楚 |
| `intent_extraction` | 作者型 Persona | 这是提取，不是创作 |
| `evidence_preprocessing` | 记者/作者 Persona | 会引入主观筛选偏好 |
| `sample_boundary` | 风格类 Persona | 会把边界裁决变成审美判断 |
| `writing_contract` | 主编/作者 Persona | 合同编译需要字段稳定，不需要写作者立场 |
| `local_patch` | 强写作者 Persona | 会把局改写成整段重写 |
| `local_patch_audit` | 主编 Persona | 会让验收从裁决滑向再创作 |

## draft_first 的动态绑定建议

当前系统里最值得做动态 Persona 绑定的是 `draft_first`。

不建议用“人名”，建议用“认知框架”：

| audience_profile / 受众线索 | 推荐认知框架 |
| --- | --- |
| `specialist` | `资深医学编辑` |
| `primary_care` | `临床沟通型医学编辑` |
| `patient_education` | `健康传播编辑` |
| `public_education` | `科学写作者 / 科普编辑` |

原因：

1. 当前资产系统已经会解析 `audience_profile`
2. 这比直接按人名模仿更稳
3. 这也更容易和 `draft` 的资产选择逻辑协同

## Persona 组合测试方法

### 最小测试法

每个组合至少要做 3 层验证：

1. **静态**  
   - 节点脚本是否真的拼上了 `profile.prompt_prefix`
   - `prompt_file` 是否存在
   - 运行时注入是否齐

2. **半动态**  
   - 导出最终 prompt
   - 对照看 Persona 语义有没有被协议完全吞掉
   - 对照看 Persona 有没有压过节点边界

3. **live**  
   - 环境齐备时，至少用最小样例跑一次
   - 看真实产物有没有变好，而不是只看 prompt 更花

### 评价维度

不是看“味道更足”就算赢，要按节点看：

| 节点 | 主要评价维度 |
| --- | --- |
| `viewpoint` | 主张清晰度、策略稳定性、边界自觉 |
| `outline` | 结构承重、桥接能力、不重复观点层 |
| `draft_first` | 可读性、证据落地、受众贴合度、不过界 |
| `draft_revise` | 修准率、整稿控制、不乱改 |
| `post_review` | 检出率、裁决稳定性、不过度主观 |
| `supplementary_evidence` | 补证命中率、来源质量、污染控制 |

## 当前最值得纳入长线程的 Persona 测试清单

建议本轮至少纳入这 6 组：

1. `viewpoint` baseline vs `VP-1`
2. `outline` baseline vs `OL-1`
3. `draft_first` baseline vs `DF-1`
4. `draft_revise` baseline vs `DR-1`
5. `post_review` baseline vs `PR-1`
6. `supplementary_evidence` baseline vs `SE-1`

## 一句话结论

当前白盒系统里，Persona 最值得强化的不是冻结层，也不是局改层，而是：

- `viewpoint`
- `outline`
- `draft_first`
- `draft_revise`
- `supplementary_evidence`

而 `writing_contract`、`pre_review`、`local_patch`、`local_patch_audit` 这些节点，当前更应该坚持“协议优先、Persona 从轻或不用”。
