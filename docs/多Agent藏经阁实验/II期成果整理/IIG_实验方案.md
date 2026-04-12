# IIG 实验方案（终版）

状态：ready_to_execute  
日期：2026-04-08  
前序：IIF 4臂17次执行完成（因果性Δ=+3.33不成立 / 样稿增益Δ=+13成立 / revise增益Δ=0不成立 / 系统上限mean=76有价值底稿）

## 一、核心使命

IIF 的核心发现：

1. 公式因果性**不成立**（Δ=+3.33 < 5分阈值），但 IIF 只用了 3 题，样本量不足
2. 样稿增益**成立**（Δ=+13分）
3. revise loop**增益不成立**（Δ=0分）——revise 有机械修补能力但没有文字品质提升能力
4. 系统上限停在76分（有价值底稿，0/3达到85可交付线）

IIG 回答三个问题：

1. **公式因果性复验**：IIF 因果性不成立是真命题（8公式对质量没用）还是样本量不足的假阴性？用全部 10 题、三臂对照重做
2. **L1 增量**：在8公式基础上叠加 L1 写作手艺资产（语法戒律 + 表达库 + 修辞积木），能否产生可测量的额外增益？
3. **系统新上限**：IIF 最强配置（公式 + 样稿 + revise）+ L1 全部打开、轮次加大时，能否突破 76 分天花板？

三个问题独立裁决。公式因果性失败不杀死 L1 增量判定；L1 增量失败不杀死 IIG-4 上限臂。

## 二、变量设计

IIG-1 是三臂对照（A / B / C），有两个自变量：

| 变量 | 含义 | A 臂 | B 臂 | C 臂 |
|------|------|------|------|------|
| **formula_positions** | 8公式位编码 | ✗ 无 | ✓ 有 | ✓ 有 |
| **l1_writing_craft** | L1 层写作手艺规则注入 revise | ✗ 无 | ✗ 无 | ✓ 有 |

以下变量三臂全部锁定（非自变量）：

| 变量 | 状态 | 说明 |
|------|------|------|
| reference_sample | 打开 | IIF-2 样稿增益成立，锁定为标配 |
| revise_loop | 打开（MaxRounds=6） | revise 机制保留，观测 L1 是否激活它 |
| anchor_card | 全部打开 | 非自变量 |

## 三、L1 注入资产清单

### 核心三件（必须注入）

| 文件 | 路径 | 内容摘要 | 注入理由 |
|------|------|----------|----------|
| **native_syntax_rules.json** | `藏经阁/l1/writing_craft/` | 13 条通用语法戒律 v3.1（4 组：句法 SYN / 词法 LEX / 语义 SEM / 连贯 COH），消灭翻译腔与 AI 机味 | IIF revise 写作力副表长期卡在 opening_hook / transition_flow 低分，正是语法戒律覆盖范围 |
| **expression_base.json** | `藏经阁/l1/writing_craft/` | 12 条通用过渡短语 + 禁用表达黑名单（来自三位作者语料蒸馏） | 替换 LLM 默认的翻译腔过渡词（"在…背景下""不仅…而且"） |
| **m4_rhetoric_blocks.json** | `藏经阁/l1/writing_craft/` | 8 种通用修辞积木原型 v2.0（问题陈述 / 机制解析 / 核心证据 / 横向对比 / 客观指标 / 权威引用 / 风险防守 / 目标画像） | 给 revise 提供结构化修辞工具，突破"信息正确但表达平庸"的天花板 |

### 可选附加（按受众语域匹配）

| 文件 | 条件 | 用法 |
|------|------|------|
| register_levels.json | 受众语域明确为 R3-R5（科普/传播） | 约束 revise 输出的语域一致性 |
| m1_argument_logic_rules.json | 评分发现论证逻辑断层 | 约束论证力度与立论门禁 |
| m2_narrative_primitives.json | 稿件结构停在叙事层 | 提供叙事原语框架 |

**不注入的对象**：8 个 lighthouse persona 文件、persona_kernels.json、style_dna_schema.json。理由：persona 属于文风层（L2/L3 上层），IIG 只测 L1 基础写作手艺的增益，不引入文风变量。

## 四、L1 注入机制（revise 脚本改造方案）

### 4.1 注入位置

在 `run_ii_whitebox_revise.ps1` 的 revise prompt 模板中，在 `$materialsBlock` 之后、`【当前稿件】` 之前，新增 `$l1Block`：

```
$revisePrompt = @"
你是侠客岛白盒编排器的修稿执行器。...

【写作合同】
...
$formulaBlock
$feedbackBlock
$sampleBlock
$materialsBlock

$l1Block          ← 新增 L1 注入点

【当前稿件】
...
【修稿规则】
1-7. （原有规则不变）
8. 每轮修稿必须逐条对照 L1 语法戒律，凡命中禁用条目的表述必须消除或改写。
9. 修辞积木为可选工具；一旦使用某积木，必须完整实现该积木的全部结构要素，不得只用标题。
10. 过渡短语优先使用 L1 表达库中的推荐项，禁用表达黑名单中的条目一律不得出现在修改后的稿件中。
"@
```

### 4.2 `$l1Block` 的构建逻辑

```powershell
# ── 新增参数 ──
param(
    ...
    [string]$L1AssetsPath = "",           # L1 资产目录路径
    [switch]$EnableL1WritingCraft         # 是否启用 L1 注入
)

# ── L1 加载逻辑 ──
$l1Block = ""
if ($EnableL1WritingCraft -and $L1AssetsPath) {
    $syntaxPath   = Join-Path $L1AssetsPath "native_syntax_rules.json"
    $exprPath     = Join-Path $L1AssetsPath "expression_base.json"
    $rhetoricPath = Join-Path $L1AssetsPath "m4_rhetoric_blocks.json"

    $syntaxRules   = if (Test-Path $syntaxPath)   { Get-Content $syntaxPath -Encoding UTF8 -Raw | ConvertFrom-Json } else { $null }
    $exprRules     = if (Test-Path $exprPath)      { Get-Content $exprPath   -Encoding UTF8 -Raw | ConvertFrom-Json } else { $null }
    $rhetoricRules = if (Test-Path $rhetoricPath)  { Get-Content $rhetoricPath -Encoding UTF8 -Raw | ConvertFrom-Json } else { $null }

    $l1Block = @"

【L1 写作手艺约束（来自藏经阁 L1 层）】

## 语法戒律
$( ($syntaxRules.rules | ForEach-Object { "- [$($_.id)] $($_.name)：$($_.description)" }) -join "`n" )

## 禁用表达
$( ($exprRules.banned_expressions | ForEach-Object { "- 禁用：「$($_.text)」→ 替代：「$($_.replacement)」" }) -join "`n" )

## 修辞积木原型（可选使用，使用则必须完整）
$( ($rhetoricRules.blocks | ForEach-Object { "- [$($_.id)] $($_.name)：$($_.description)" }) -join "`n" )
"@
}
```

### 4.3 Context 预算控制

L1 三个核心 JSON 精简注入后预估 token 占用：

| 文件 | 精简后字数 | 预估 token |
|------|-----------|-----------|
| native_syntax_rules（13 条） | ~1500 字 | ~800 |
| expression_base（禁用+替代） | ~800 字 | ~400 |
| m4_rhetoric_blocks（8 种积木） | ~1200 字 | ~600 |
| **合计** | ~3500 字 | ~1800 |

当前 revise prompt 主体（公式+反馈+样稿+材料+稿件+规则）约 40000 字 / ~20000 token。L1 新增 ~1800 token，占比 < 10%，不会触碰 context 上限。

## 五、三臂设计与题目分配

### IIG-1：公式因果性 + L1 增量三臂对照（10 题 × 3 臂 = 30 runs）

| # | 候选 ID | A 臂（基线） | B 臂（8公式） | C 臂（8公式+L1） |
|---|---------|-------------|-------------|-----------------|
| 1 | compassion15_os_c | ✓ | ✓ | ✓ |
| 2 | zolbetuximab_safety_d | ✓ | ✓ | ✓ |
| 3 | sindi_gastric_esmo_c | ✓ | ✓ | ✓ |
| 4 | ctad_lb13_c | ✓ | ✓ | ✓ |
| 5 | ctad_lb21_c | ✓ | ✓ | ✓ |
| 6 | ctad_p096_c | ✓ | ✓ | ✓ |
| 7 | ctad_p279_c | ✓ | ✓ | ✓ |
| 8 | iie_reg_patient_c | ✓ | ✓ | ✓ |
| 9 | iie_reg_mechanism_c | ✓ | ✓ | ✓ |
| 10 | lecanemab_news_c | ✓ | ✓ | ✓ |

**A 臂（基线）配置**：

- formula_positions：**✗**（不传 formula_contract）
- reference_sample：✓（-EnableReferenceSample）
- revise loop：✓（MaxRounds=6）
- L1 writing craft：**✗**

**B 臂（8公式）配置**：

- formula_positions：**✓**（从 candidate pool 读取）
- reference_sample：✓（-EnableReferenceSample）
- revise loop：✓（MaxRounds=6）
- L1 writing craft：**✗**

**C 臂（8公式+L1）配置**：

- formula_positions：**✓**（从 candidate pool 读取）
- reference_sample：✓（-EnableReferenceSample）
- revise loop：✓（MaxRounds=6）
- L1 writing craft：**✓**（-EnableL1WritingCraft -L1AssetsPath "D:\汇度编辑部1\藏经阁\l1\writing_craft"）

**对照约束**：
- 三臂使用同一 candidate pool、同一评分脚本、同一 LLM、同一 temperature
- A→B 唯一差异：formula_positions 有无
- B→C 唯一差异：L1 写作手艺注入有无
- 三臂顺序随机或交叉执行，避免系统性偏差

**判定标准（三层）**：

| 对照 | 判定目标 | 成立阈值 | 说明 |
|------|---------|---------|------|
| B vs A | 8公式因果性 | B 均值 > A 均值 **≥ 5 分**，且 formula_compliance ≥ 70 | 与 IIF-1 同一阈值，10 题扩样复验 |
| C vs B | L1 增量 | C 均值 > B 均值 **≥ 3 分**，且 writing_strength 至少 2 维有提升 | L1 在公式之上的额外增益 |
| C vs A | 叠加效应 | C 均值 > A 均值 **≥ 8 分** | 公式 + L1 的合计增益 |

### IIG-4：系统上限（IIF 最强配置 + L1，10 题 = 10 runs）

| # | 候选 ID | 公式 | 样稿 | revise | L1 | MaxRounds |
|---|---------|------|------|--------|----|-----------|
| 1-10 | 全部 10 题 | ✓ | ✓ | ✓ | ✓ | **10**（加大） |

**配置说明**：

以 IIF 最强配置（公式 + 样稿 + revise 全开）为底，叠加 L1 写作手艺约束，轮次从 IIF 的 6 轮加大到 10 轮，全力冲击系统天花板。

L1 从第 1 轮即注入（不做 Phase 分段），原因：IIG-1 C 臂已经测了"从头带 L1"的效果，IIG-4 目标是看最强配置下的绝对上限。

**判定标准**：
- weighted_total ≥ **85** 为"可交付草稿"
- weighted_total ≥ **80** 为"接近可交付"
- 10 题均值比 IIF-4 的 76 分提升 ≥ 5 分为"L1 对上限有显著贡献"

## 六、评分系统

**与 IIF 完全一致**，不改评分维度和权重。

### 主表（5 维，跨组可比）

| 维度 | 权重 |
|------|------|
| route_alignment | 25% |
| key_facts | 25% |
| audience_style | 20% |
| structure | 15% |
| hallucination_control | 15% |

### 写作力副表（5 维，不计入 weighted_total，但本期重点观察）

| 维度 | IIG 观察重点 |
|------|------------|
| opening_hook | L1 修辞积木中的"问题陈述"块能否改善开场 |
| transition_flow | L1 表达库的过渡短语能否消除翻译腔过渡 |
| midgame_drive | L1 语法戒律能否提升信息密度和推进感 |
| closing_tension | L1 修辞积木中的"风险防守"块能否提升收尾 |
| anchor_fidelity | 不预期 L1 对此有影响（控制维度） |

### 公式审计

与 IIF 一致（formula_compliance + formula_trace）。

### 新增：L1 合规审计（仅 C 臂 + IIG-4）

| 维度 | 说明 |
|------|------|
| l1_syntax_violations | 13 条戒律中仍被违反的条数 |
| l1_banned_expression_hits | 禁用表达黑名单中仍出现的条数 |
| l1_rhetoric_blocks_used | 使用的修辞积木种数 |

## 七、输出规范

### Runtime 产物

落在仓库外 `D:\汇度编辑部1\侠客岛-runtime\ii_whitebox\`，命名格式：

```
{timestamp}_{candidate_id}_iig1_a     ← IIG-1 A 臂（基线）
{timestamp}_{candidate_id}_iig1_b     ← IIG-1 B 臂（8公式）
{timestamp}_{candidate_id}_iig1_c     ← IIG-1 C 臂（8公式+L1）
{timestamp}_{candidate_id}_iig4       ← IIG-4 全开
```

### 正式结论文件

**必须落在** `d:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\II期成果整理\IIG成果整理\`：

| 文件 | 内容 |
|------|------|
| `IIG_公式因果性结论.md` | IIG-1 B vs A 对照统计 + 判定（10 题扩样复验） |
| `IIG_L1增量结论.md` | IIG-1 C vs B 对照统计 + 判定 |
| `IIG_叠加效应分析.md` | IIG-1 C vs A 合计增益分析 |
| `IIG_系统上限结论.md` | IIG-4 10 题终态数据 + 判定 |
| `IIG_写作力副表分析.md` | writing_strength 5 维三臂对比 |

### 成果索引更新

执行完成后必须在 `II期成果整理/00_成果索引.md` 中新增 `0.6 IIG 正式执行结果` 节。

## 八、执行顺序

1. **Phase 0（准备）**：修改 `run_ii_whitebox_revise.ps1`，新增 `-EnableL1WritingCraft` / `-L1AssetsPath` 参数和 `$l1Block` 逻辑
2. **Phase 0.5（Smoke test）**：选 1 道题跑 C 臂 1 轮，验证 L1 block 正确注入 revise prompt
3. **IIG-1 A 臂**：10 题 × 1 = 10 runs（基线：无公式，无 L1）
4. **IIG-1 B 臂**：10 题 × 1 = 10 runs（8公式，无 L1）
5. **IIG-1 C 臂**：10 题 × 1 = 10 runs（8公式 + L1）
6. **IIG-4**：10 题 × 1 = 10 runs（IIF 最强配置 + L1，MaxRounds=10）

**总计：40 次管线执行**（+ 1 次 smoke test）

## 九、脚本改造清单

| 文件 | 改动 | 量级 |
|------|------|------|
| `run_ii_whitebox_revise.ps1` | 新增 `-EnableL1WritingCraft` / `-L1AssetsPath` 参数；新增 `$l1Block` 构建逻辑；修稿规则新增 8-10 条 | ~50 行 |
| `run_ii_whitebox_orchestrator.ps1` | 透传 `-EnableL1WritingCraft` / `-L1AssetsPath` 到 revise 脚本 | ~5 行 |

**不改的文件**：draft.ps1、score.ps1、materials.ps1、candidate pool JSON。L1 只在 revise 环节注入。

## 十、IIF 基线对照参考

| 臂 | 均值 | 判定 |
|----|------|------|
| IIF-1 A（无公式） | 62.67 | — |
| IIF-1 B（有公式） | 66.0 | Δ=+3.33，不成立 |
| IIF-2 baseline | 65 | — |
| IIF-2 + 样稿 | 78 | Δ=+13，成立 |
| IIF-3 baseline | 75 | — |
| IIF-3 + revise | 75 | Δ=0，不成立 |
| IIF-4 全开 | 76.0 | mean=76，0/3≥85 |

IIG 的直接对标：
- IIG-1 A 臂（基线：无公式+样稿+revise）应约等于 IIF-1 A 水平（~62-63 分），可交叉验证
- IIG-1 B 臂（8公式+样稿+revise）应约等于 IIF-4 水平（~76 分），扩样到 10 题重验公式因果性
- IIG-1 B vs A 差值直接对标 IIF-1 的 Δ=+3.33，看 10 题扩样后结论是否翻转
- IIG-1 C vs B 差值是 L1 的净增益（公式控制不变，只看 L1 的边际贡献）
- IIG-4 的目标是突破 76→85

## 十一、前置条件清单

| # | 条件 | 当前状态 | 执行时验证 |
|---|------|----------|-----------|
| 1 | 10 个候选全部在 candidate pool 中 | ✅ 已有 | 跑前确认 |
| 2 | 全部 10 个候选有 formula_positions | ✅ 已有 | 跑前确认 |
| 3 | 全部 10 个候选有 reference_sample_path | ✅ 已有 | 跑前确认 |
| 4 | L1 三个核心 JSON 存在且可读 | ✅ 已验证路径存在 | 跑前 `Test-Path` |
| 5 | revise.ps1 新增 L1 参数和 block | ❌ 待改 | Phase 0 改完后 smoke test |
| 6 | orchestrator.ps1 透传 L1 参数 | ❌ 待改 | Phase 0 改完后 smoke test |
| 7 | A 臂调用方式支持「不传 formula_contract」 | ✅ 已有（IIF-1 A 臂验证过） | 跑前确认 |

## 十二、不做清单

1. 不改评分系统（不引入新维度到主表）
2. 不改 draft.ps1（L1 只在 revise 环节）
3. 不引入 persona / style DNA / lighthouse（L1 基底层only）
4. 不扩候选池
5. 不在 IIG 期间改 formula_positions
6. 不在中途改 L1 JSON 内容（冻结为实验输入）
