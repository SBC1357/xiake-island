# III期完整架构

状态：正式架构层 / 当前白盒真实架构  
日期：2026-04-15  
用途：把当前已经稳定到足以成系统的白盒主链、返修链、侧链和边界收成一份正式架构说明  
边界：本文件不是施工手册，不展开阶段流水，不承载待验证经验池

## 证据摘要

1. 已直接核对当前白盒主链与运行手册，确认真实主链是 `materials -> layer1 -> writing_contract -> viewpoint -> outline -> draft(first) -> post_review -> three_flow_loop`，且 `pre_review` 是合同后的并行旁路，不是首稿前的硬串行闸门。
2. 已直接核对 `layer1`、`draft`、`post_review`、`local_patch` 与 `supplementary_evidence` 的脚本和协议，确认当前实现是“大盒 + 真 Agent + 侧链”混合态，而不是旧版 11 段主链口径。
3. 已直接核对当前白盒全貌与架构双图，确认 `layer1` 仍是大盒，`draft` 仍是 `first / revise` 双 mode，`post_review` 仍是三流裁决口，`supplementary_evidence` 仍是独立确定性侧链。
4. 已直接核对当前真实架构与理想 Harness 的对照说明，确认两者差距主要在 `layer1` 拆分度、`pre_review` 闸门级别、主链并行度和跨平台抽象层。

## 一、架构定位

III 期完整架构回答的是：

`这个系统当前到底怎么跑，哪些节点已经正式成型，哪些边界已经冻结，当前真实架构和理想 Harness 还差什么。`

它不回答：

1. 这轮阶段怎么排
2. 每条经验的原始全文是什么
3. 某一次 run 的运行细节
4. 节点内部的所有 prompt 微操
5. 施工包里的阶段流水和接棒口径

它只收：

1. 会改变节点职责的规则
2. 会改变主链路由的规则
3. 会改变上下游输入输出边界的规则
4. 会改变白盒 / 灰盒 / 黑盒边界的规则

## 二、当前真实主链

当前真实主链已经不是旧 `11` 段总层口径，而是下面这条白盒链：

`materials -> layer1 -> writing_contract -> viewpoint -> outline -> draft(first) -> post_review -> three_flow_loop`

其中：

1. `materials` 是原始材料导出位。
2. `layer1` 是前置冻结大盒。
3. `writing_contract` 冻结写作合同。
4. `viewpoint` 冻结观点与表达方向。
5. `outline` 把合同和观点收成大纲。
6. `draft` 以 `first / revise` 两种 mode 生成与整改正文。
7. `post_review` 是三流裁决口。
8. `three_flow_loop` 是后审后的返修回流总称，实际包含 `requirement_rework / whole_revise / local_patch` 三类路径。

### 2.1 并行旁路

`pre_review` 现在是合同后的并行旁路，不是主链硬闸门。

它的正确位置是：

`writing_contract -> pre_review`

它的正确理解是：

1. 它可以做侧审预警。
2. 它默认不阻塞大纲和首稿。
3. 它不能被写成已经接管主链裁决。

### 2.2 独立侧链

`supplementary_evidence` 是独立确定性侧链，不是默认主链节点。

它的正确理解是：

1. 它用于缺口补证。
2. 它有自己的脚本、协议和落盘。
3. 它不能污染主证据包，也不能冒充主链默认环节。

## 三、当前稳定的节点间逻辑

### 1. `materials`

作用：
- 把原始材料导出成当前 run 可用文本
- 区分 `full text` 与 `preview`

当前边界：
- 它是工具位，不是内容判断位
- 不能把整理稿或证据卡当正式输入

### 2. `layer1`

作用：
- 冻结任务理解
- 冻结可用证据
- 冻结样稿边界
- 决定是否可以进入写作合同层

当前现实：
- 它仍然是一个大盒
- 内部包着多个半 Agent

当前内部半 Agent 划分：

1. `layer1_main`：分流
2. `intent_extraction`：意图提炼
3. `evidence_preprocessing`：证据预处理
4. `sample_boundary`：样稿边界
5. `layer1_direct`：最终放行
6. `layer1_sp`：SP 停机路径

### 3. `writing_contract`

作用：
- 把意图包和证据包编译成正式写作合同

当前边界：
- 不直接碰原始材料
- 不自己猜任务
- 不读证据包 md

### 4. `viewpoint`

作用：
- 定文章主张、论证路线和表达方向

当前边界：
- 不写正文
- 不写大纲
- 不重造合同

### 5. `outline`

作用：
- 把合同与观点收成可执行大纲

当前边界：
- 必须消费 `viewpoint_card`
- 不能把自己写成第二份观点卡

### 6. `draft`

作用：
- 把大纲展开成正文

当前形态：
- 同一个 Agent，两个 mode
- `first`：首稿
- `revise`：整稿整改

当前边界：
- 不是两个无关节点
- 不是自由写作位

### 7. `post_review`

作用：
- 回原始材料核事实、核边界、核路线
- 给出问题级别裁决

当前输出：
- `pass`
- `requirement_rework`
- `whole_revise`
- `local_patch`

当前边界：
- 它是三流裁决口，不只是普通审稿意见
- 它不能被降级成“走马观花的复读层”

### 8. `three_flow_loop`

作用：
- 承接 `post_review` 的返修回流

当前真实分支：

1. `requirement_rework`：回 `layer1`，重新冻结任务理解
2. `whole_revise`：回 `draft(revise)`，整稿整改后再回后审
3. `local_patch`：进局改小闭环，再回后审

### 9. `local_patch`

作用：
- 做局部修补
- 再交 `local_patch_audit` 验收

当前边界：
- 它不是顺手改一句
- 它是一个带验收的小闭环

### 10. `supplementary_evidence`

作用：
- 在主链证据缺口成立时，独立补证

当前边界：
- 它是侧链，不是默认主链
- 补出来的结果不能回填污染主证据包

## 四、白盒 / 灰盒 / 黑盒边界

| 层级 | 当前对象 | 说明 |
| --- | --- | --- |
| 白盒 | `materials`、`writing_contract`、`viewpoint`、`outline`、`draft`、`post_review`、`local_patch` | 脚本、输入、输出、回流关系都能直接读懂 |
| 灰盒 | `layer1` 大盒、`pre_review` 并行旁路 | 能跑，但角色边界还没完全拆开 |
| 黑盒 | 外部 LLM、PDF 抽取质量、当前不进默认主链的补证侧链内部推理 | 可调用，但内部推理不可控，或当前未纳入默认主链 |

## 五、当前真实架构和理想 Harness 的差距

| 维度 | 当前真实实现 | 理想形态 |
| --- | --- | --- |
| 冻结层 | `layer1` 大盒 | 5 个独立真 Agent |
| 观点层接法 | 串行接在合同后 | 与合同并列上游 |
| 前审角色 | 并行预警，不默认阻塞 | 正式闸口，命中硬阻断时拦主链 |
| 成稿位 | 已有 `first / revise` 两种 mode | 继续保留，但更显式 |
| 后审 | 已是三流裁决口 | 保持，并把回流策略更清晰交给 Harness |
| 补证据 | 有 profile，有侧链位 | 作为正式可选侧链纳入，但不污染主链 |
| 平台抽象 | 仍然偏 Windows / PowerShell 语义 | 跨平台公共层更干净 |

当前最重要的现实结论是：

1. 系统已经不是“单个 prompt 写稿”。
2. 但它还没到“完全拆成理想 Harness”的程度。
3. 现在最值钱的是边界稳定和局部可调，而不是盲目增加节点数量。

## 六、当前最重要的系统纪律

1. 有多解先反向确认，没确认不准开工。
2. 输入先做标准化，不把预处理甩给用户。
3. `layer1` 先冻结再谈拆分。
4. 候选主题、样稿边界、证据边界不得互相冒充。
5. `draft` 的 `first / revise` 只能按 mode 理解，不能当成两个独立岗位。
6. `post_review` 必须保留三流裁决语义，不得降级成普通点评。
7. `local_patch` 必须带验收回流，不得当成顺手修补。
8. `supplementary_evidence` 必须保持侧链属性，不得污染主证据包。

## 七、当前还没有完全冻结的部分

1. `layer1` 内部各半 Agent 的最终拆分边界
2. `pre_review` 是否升级为正式硬闸门
3. 全节点 Persona 组合的完整推荐矩阵
4. 跨平台公共层的具体抽象切分
5. 更细的回归阈值与边界异常处理策略

这些内容已经有明确方向，但还不适合写成比当前架构更硬的正式冻结口径。

这些内容暂留在经验池，不直接写死成完整架构。
