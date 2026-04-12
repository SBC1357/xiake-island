param(
    [string]$CandidateId,
    [string]$CandidatePool = "",
    [string]$RunDirectory = "",
    [string]$ApiKey = "",
    [int]$MaxRounds = 6,
    [int]$TargetScore = 85,
    [int]$MaxStaleRounds = 2,
    [ValidateSet("whole", "local")]
    [string]$ReviseMode = "whole",
    [int]$MaxLocalTasksPerRound = 4,
    [switch]$EnableL1WritingCraft,
    [string]$L1AssetsPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "whitebox_common.ps1")

if ([string]::IsNullOrWhiteSpace($RunDirectory)) {
    throw "必须提供 -RunDirectory。"
}

if ($ReviseMode -eq "local") {
    $localRevisePath = Join-Path $PSScriptRoot "run_ii_whitebox_local_revise.ps1"
    if (-not (Test-Path -LiteralPath $localRevisePath)) {
        throw "局部返修入口不存在: $localRevisePath"
    }

    $localArgs = @{
        CandidateId = $CandidateId
        CandidatePool = $CandidatePool
        RunDirectory = $RunDirectory
        ApiKey = $ApiKey
        MaxRounds = $MaxRounds
        TargetScore = $TargetScore
        MaxStaleRounds = $MaxStaleRounds
        MaxLocalTasksPerRound = $MaxLocalTasksPerRound
    }
    & $localRevisePath @localArgs
    exit $LASTEXITCODE
}

$poolData = Get-CandidatePoolData -Path $CandidatePool
$candidate = Resolve-Candidate -PoolData $poolData -CandidateId $CandidateId

$scorePath = Join-Path $RunDirectory "score.json"
$draftPath = Join-Path $RunDirectory "draft.txt"
$contractPath = Join-Path $RunDirectory "whitebox_contract.json"

if (-not (Test-Path -LiteralPath $scorePath)) {
    throw "缺少 score.json: $scorePath"
}
if (-not (Test-Path -LiteralPath $draftPath)) {
    throw "缺少 draft.txt: $draftPath"
}
if (-not (Test-Path -LiteralPath $contractPath)) {
    throw "缺少 whitebox_contract.json: $contractPath"
}

$contract = Read-JsonFile -Path $contractPath
$benchmarkEvaluationContract = if ($contract.PSObject.Properties.Name -contains "benchmark_evaluation_contract") {
    $contract.benchmark_evaluation_contract
}
elseif ($contract.PSObject.Properties.Name -contains "evaluation_contract") {
    $contract.evaluation_contract
}
else {
    $null
}
$benchmarkReferencePath = if ($benchmarkEvaluationContract -and $benchmarkEvaluationContract.PSObject.Properties.Name -contains "reference_answer_path") {
    [string]$benchmarkEvaluationContract.reference_answer_path
}
else {
    ""
}
$reviseDir = Join-Path $RunDirectory "revise"
if (-not (Test-Path -LiteralPath $reviseDir)) {
    New-Item -ItemType Directory -Path $reviseDir -Force | Out-Null
}

# ── 加载原材料 ──
$materialsManifestPath = Join-Path (Join-Path $RunDirectory "materials") "materials_manifest.json"
$compiledMaterialsText = ""
if (Test-Path -LiteralPath $materialsManifestPath) {
    $materialsManifest = Read-JsonFile -Path $materialsManifestPath
    $compiledTextPath = $materialsManifest.compiled_text
    if ($compiledTextPath -and (Test-Path -LiteralPath $compiledTextPath)) {
        $compiledMaterialsText = [System.IO.File]::ReadAllText($compiledTextPath, [System.Text.Encoding]::UTF8)
    }
}

# ── 加载参考样稿 ──
$referenceSampleExcerpt = ""
$referenceSampleContract = $contract.reference_sample_contract
if ($referenceSampleContract) {
    $sampleEnabled = [bool]$referenceSampleContract.enabled_for_draft
    $samplePath = $referenceSampleContract.resolved_path
    $sampleBoundary = [string]$referenceSampleContract.boundary
    $sampleRoles = @($referenceSampleContract.roles)
    if ($sampleEnabled -and $samplePath -and (Test-Path -LiteralPath $samplePath)) {
        if (-not [string]::IsNullOrWhiteSpace($benchmarkReferencePath) -and (Test-Path -LiteralPath $benchmarkReferencePath)) {
            $sampleResolved = (Resolve-Path -LiteralPath $samplePath).ProviderPath
            $referenceResolved = (Resolve-Path -LiteralPath $benchmarkReferencePath).ProviderPath
            if ($sampleResolved -eq $referenceResolved) {
                throw "reference_sample_matches_benchmark_reference: $samplePath"
            }
        }
        $sampleExtract = Extract-FileText -Path $samplePath
        if (-not [string]::IsNullOrWhiteSpace($sampleExtract.text)) {
            $referenceSampleExcerpt = $sampleExtract.text.Substring(0, [Math]::Min(6000, $sampleExtract.text.Length))
        }
    }
}

$reviseManifestPath = Join-Path $RunDirectory "revise_manifest.json"
$reviseSummaryPath = Join-Path $RunDirectory "revise_summary.md"
$roundResults = @()

$currentDraftPath = $draftPath
$currentScorePath = $scorePath

# ── 回滚与停滞追踪 ──
$bestScore = 0
$bestDraftContent = ""
$consecutiveStaleRounds = 0
$previousScore = 0

for ($round = 1; $round -le $MaxRounds; $round++) {
    $roundDir = Join-Path $reviseDir "round_$round"
    New-Item -ItemType Directory -Path $roundDir -Force | Out-Null

    $currentScore = Read-JsonFile -Path $currentScorePath
    $currentDraft = [System.IO.File]::ReadAllText($currentDraftPath, [System.Text.Encoding]::UTF8)

    # 检查是否已合格且无阻塞问题
    $missingItems = @($currentScore.missing_or_misaligned)
    $nextActions = @($currentScore.next_actions)
    $blockingIssues = @($currentScore.blocking_issues)
    $currentTotal = [int]$currentScore.weighted_total

    # 记录初始最高分
    if ($round -eq 1) {
        $bestScore = $currentTotal
        $bestDraftContent = $currentDraft
        $previousScore = $currentTotal
    }

    # 退出条件 1: 已达到目标分数
    if ($currentTotal -ge $TargetScore -and $blockingIssues.Count -eq 0) {
        $roundResults += [ordered]@{
            round = $round
            status = "skipped_target_reached"
            reason = "总分 $currentTotal >= $TargetScore 且无阻塞问题"
        }
        break
    }

    # 退出条件 2: 连续不提分轮次达上限
    if ($consecutiveStaleRounds -ge $MaxStaleRounds) {
        $roundResults += [ordered]@{
            round = $round
            status = "skipped_stale_plateau"
            reason = "连续 $consecutiveStaleRounds 轮未提分（上限 $MaxStaleRounds 轮），判定已到瓶颈"
        }
        break
    }

    # 退出条件 3: 无可修改点
    if ($currentScore.qualified -eq $true -and $missingItems.Count -eq 0 -and $blockingIssues.Count -eq 0 -and $nextActions.Count -eq 0) {
        $roundResults += [ordered]@{
            round = $round
            status = "skipped_no_actionable_items"
            reason = "评分已合格且无 missing/blocking/next_actions"
        }
        break
    }

    # 构建修稿反馈段落
    $feedbackParts = @()
    $feedbackParts += "【评分反馈（第 $round 轮修稿输入）】"
    $feedbackParts += "- 当前总分：$($currentScore.weighted_total)"
    $feedbackParts += "- 是否合格：$($currentScore.qualified)"
    $feedbackParts += ""

    if ($blockingIssues.Count -gt 0) {
        $feedbackParts += "阻塞问题："
        foreach ($issue in $blockingIssues) { $feedbackParts += "- $issue" }
        $feedbackParts += ""
    }

    if ($missingItems.Count -gt 0) {
        $feedbackParts += "缺失或偏差项："
        foreach ($item in $missingItems) { $feedbackParts += "- $item" }
        $feedbackParts += ""
    }

    if ($nextActions.Count -gt 0) {
        $feedbackParts += "建议修改动作："
        foreach ($action in $nextActions) { $feedbackParts += "- $action" }
        $feedbackParts += ""
    }

    # 提取维度详情
    $dims = @($currentScore.dimensions)
    if ($dims.Count -gt 0) {
        $feedbackParts += "各维度得分："
        foreach ($dim in $dims) {
            $feedbackParts += "- $($dim.id): $($dim.score) — $($dim.reason)"
        }
        $feedbackParts += ""
    }

    # backtrace
    $traces = @($currentScore.backtrace)
    if ($traces.Count -gt 0) {
        $feedbackParts += "问题回指："
        foreach ($trace in $traces) {
            $feedbackParts += "- [$($trace.target_layer)] $($trace.issue)"
        }
        $feedbackParts += ""
    }

    # 写作力副表
    $wsItems = @($currentScore.writing_strength)
    if ($wsItems.Count -gt 0) {
        $feedbackParts += "写作力副表（必须针对性修改低分项）："
        foreach ($ws in $wsItems) {
            $feedbackParts += "- $($ws.id): $($ws.score) — $($ws.reason)"
        }
        $feedbackParts += ""
    }

    # 公式合规审计
    $ftItems = @($currentScore.formula_trace)
    if ($ftItems.Count -gt 0) {
        $feedbackParts += "公式位审计（miss/partial 的位必须在修稿中补齐）："
        $feedbackParts += "- formula_compliance 总分: $($currentScore.formula_compliance)"
        foreach ($ft in $ftItems) {
            $feedbackParts += "- [$($ft.status)] $($ft.position): $($ft.evidence)"
        }
        $feedbackParts += ""
    }

    $feedbackBlock = ($feedbackParts -join "`n")

    # 读取公式约束（如有）
    $formulaBlock = ""
    $fc = $contract.formula_contract
    if ($null -ne $fc) {
        $fbParts = @()
        $fbParts += "【公式驱动约束（修稿时同样必须遵守）】"
        if ($fc.persona) { $fbParts += "- 人格定位：$($fc.persona)" }
        if ($fc.range) { $fbParts += "- 写作范围：$($fc.range)" }
        if ($fc.write_target) { $fbParts += "- 写作目标：$($fc.write_target)" }
        $ecu = @()
        if ($fc.PSObject.Properties.Name -contains "effective_content_unit") { $ecu = @($fc.effective_content_unit) }
        if ($ecu.Count -gt 0) {
            $fbParts += "- 有效内容单元："
            foreach ($item in $ecu) { $fbParts += "  - $item" }
        }
        $formulaBlock = ($fbParts -join "`n")
    }

    # 构建参考样稿 block
    $sampleBlock = ""
    if (-not [string]::IsNullOrWhiteSpace($referenceSampleExcerpt)) {
        $sampleRolesText = if ($sampleRoles.Count -gt 0) { $sampleRoles -join " / " } else { "风格锚点 / 结构锚点 / 返修锚点" }
        $sampleBlock = @"

【参考样稿锚点（仅借结构和语气，不借事实和答案）】
- 允许用途：$sampleRolesText
- 防泄露边界：$(if ($sampleBoundary) { $sampleBoundary } else { "只借结构和语气，不借事实和答案。" })

$referenceSampleExcerpt
"@
    }

    # 构建材料 block
    $materialsBlock = ""
    if (-not [string]::IsNullOrWhiteSpace($compiledMaterialsText)) {
        $materialsBlock = @"

【原材料摘录（缺失事实只能从这里补充）】
$($compiledMaterialsText.Substring(0, [Math]::Min(18000, $compiledMaterialsText.Length)))
"@
    }

    # ── L1 写作手艺约束注入 ──
    $l1Block = ""
    if ($EnableL1WritingCraft -and $L1AssetsPath) {
        $syntaxPath   = Join-Path $L1AssetsPath "native_syntax_rules.json"
        $exprPath     = Join-Path $L1AssetsPath "expression_base.json"
        $rhetoricPath = Join-Path $L1AssetsPath "m4_rhetoric_blocks.json"

        $syntaxRules   = if (Test-Path -LiteralPath $syntaxPath)   { Get-Content $syntaxPath   -Encoding UTF8 -Raw | ConvertFrom-Json } else { $null }
        $exprRules     = if (Test-Path -LiteralPath $exprPath)     { Get-Content $exprPath     -Encoding UTF8 -Raw | ConvertFrom-Json } else { $null }
        $rhetoricRules = if (Test-Path -LiteralPath $rhetoricPath) { Get-Content $rhetoricPath  -Encoding UTF8 -Raw | ConvertFrom-Json } else { $null }

        $l1Parts = @()
        $l1Parts += ""
        $l1Parts += "【L1 写作手艺约束（来自藏经阁 L1 层）】"
        $l1Parts += ""

        # 语法戒律（4 组合并）
        if ($syntaxRules) {
            $l1Parts += "## 语法戒律"
            $allRules = @()
            foreach ($groupName in @("group_1_句法戒律", "group_2_去机味戒律", "group_3_正文门禁与修订策略")) {
                $grp = $syntaxRules.$groupName
                if ($grp -and $grp.rules) {
                    $allRules += @($grp.rules)
                }
            }
            foreach ($r in $allRules) {
                $l1Parts += "- [$($r.id)] $($r.name)：$($r.rule)"
            }
            $l1Parts += ""
        }

        # 禁用表达
        if ($exprRules -and $exprRules.universal_additions) {
            $banned = @($exprRules.universal_additions.forbidden_expressions)
            if ($banned.Count -gt 0) {
                $l1Parts += "## 禁用表达黑名单"
                foreach ($expr in $banned) {
                    $l1Parts += "- 禁用：「$expr」"
                }
                $l1Parts += ""
            }
            $transitions = @($exprRules.universal_additions.transition_phrases)
            if ($transitions.Count -gt 0) {
                $l1Parts += "## 推荐过渡短语（优先使用）"
                $shownCount = [Math]::Min(20, $transitions.Count)
                for ($ti = 0; $ti -lt $shownCount; $ti++) {
                    $l1Parts += "- $($transitions[$ti])"
                }
                if ($transitions.Count -gt 20) {
                    $l1Parts += "- （共 $($transitions.Count) 条，仅展示前 20 条）"
                }
                $l1Parts += ""
            }
        }

        # 修辞积木原型
        if ($rhetoricRules -and $rhetoricRules.m4_rhetoric_prototypes) {
            $l1Parts += "## 修辞积木原型（可选使用，使用则必须完整实现）"
            foreach ($block in @($rhetoricRules.m4_rhetoric_prototypes)) {
                $l1Parts += "- [$($block.prototype_id)] $($block.name)：$($block.description)"
            }
            $l1Parts += ""
        }

        $l1Block = ($l1Parts -join "`n")
    }

    $revisePrompt = @"
你是侠客岛白盒编排器的修稿执行器。以下是当前稿件和评分反馈，请根据反馈修改稿件。

【写作合同】
- 题目：$($contract.candidate_name)
- 受众：$($contract.writing_contract.audience)
- 写作目的：$($contract.writing_contract.purpose)

$formulaBlock

$feedbackBlock
$sampleBlock
$materialsBlock
$l1Block

【当前稿件】
$($currentDraft.Substring(0, [Math]::Min(20000, $currentDraft.Length)))

【修稿规则】
1. 只修改评分反馈中指出的问题，不要重写全文。
2. 保持原稿的正确部分不变。
3. 缺失事实只能从原材料中补充，不得编造。
4. 修改后必须仍然符合写作合同和公式约束。
5. 写作力副表中低于 70 分的维度必须针对性修改：opening_hook 改开头、transition_flow 改段间衔接、midgame_drive 改中段信息密度和推进感、closing_tension 改收尾、anchor_fidelity 补锚点卡落地点。
6. 公式位审计中 miss 或 partial 的位必须在修稿中补齐或强化，不得跳过。
7. 修完后直接输出全文，不要加解释。
8. 每轮修稿必须逐条对照 L1 语法戒律，凡命中禁用条目的表述必须消除或改写。
9. 修辞积木为可选工具；一旦使用某积木，必须完整实现该积木的全部结构要素，不得只用标题。
10. 过渡短语优先使用 L1 表达库中的推荐项，禁用表达黑名单中的条目一律不得出现在修改后的稿件中。

请直接输出修改后的完整文章正文。
"@

    $revisePrompt = Build-WhiteboxPromptWithProfile -Prompt $revisePrompt -ProfileName "whole_revise"

    $revisePromptPath = Join-Path $roundDir "revise_prompt.md"
    Set-Content -LiteralPath $revisePromptPath -Value $revisePrompt -Encoding UTF8

    $revisedDraftPath = Join-Path $roundDir "revised_draft.txt"
    $reviseStartedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    try {
        $revisedDraft = Invoke-WhiteboxLlm -Prompt $revisePrompt -ApiKeyOverride $ApiKey -Temperature 0.2 -ProfileName "whole_revise"
        Set-Content -LiteralPath $revisedDraftPath -Value $revisedDraft -Encoding UTF8
        $reviseStatus = "completed"
        $reviseError = $null
    }
    catch {
        $revisedDraft = ""
        $reviseStatus = if ($_.Exception.Message -eq "missing_llm_api_key" -or $_.Exception.Message -like "llm_transport_unavailable:*") { "agent_continue_required" } else { "failed" }
        $reviseError = $_.Exception.Message
    }

    $reviseCompletedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    if ($reviseStatus -ne "completed") {
        $roundResults += [ordered]@{
            round = $round
            status = $reviseStatus
            error = $reviseError
            started_at = $reviseStartedAt
            completed_at = $reviseCompletedAt
        }
        break
    }

    # 用修改后的稿件覆写主 draft.txt，然后重新评分
    Set-Content -LiteralPath $draftPath -Value $revisedDraft -Encoding UTF8

    # 调用评分脚本
    $scoreScriptPath = Join-Path $PSScriptRoot "run_ii_whitebox_score.ps1"
    $scoreArgs = @{
        CandidateId = $CandidateId
        CandidatePool = $(if ($CandidatePool) { $CandidatePool } else { "" })
        RunDirectory = $RunDirectory
        ApiKey = $ApiKey
    }

    try {
        & $scoreScriptPath @scoreArgs
        $scoreExitCode = $LASTEXITCODE
    }
    catch {
        $scoreExitCode = 1
    }

    # 读取新评分
    $newScorePath = Join-Path $RunDirectory "score.json"
    $newScore = if (Test-Path -LiteralPath $newScorePath) { Read-JsonFile -Path $newScorePath } else { $null }

    # 保存本轮评分副本
    $roundScorePath = Join-Path $roundDir "score.json"
    if ($newScore) {
        Write-JsonFile -Path $roundScorePath -Payload $newScore
    }

    $newTotal = if ($newScore) { [int]$newScore.weighted_total } else { 0 }

    # ── 回滚逻辑：分数下降时回退到最高分版本 ──
    $rollbackApplied = $false
    if ($newScore -and $newTotal -lt $previousScore) {
        # 分数下降，回滚到历史最高分版本
        Set-Content -LiteralPath $draftPath -Value $bestDraftContent -Encoding UTF8
        Write-Host "[WARN] Round $round 分数下降 ($previousScore -> $newTotal)，回滚到最高分版本 ($bestScore)"
        $rollbackApplied = $true
        $consecutiveStaleRounds++
    }
    elseif ($newScore -and $newTotal -gt $previousScore) {
        # 分数提升，更新最高分，重置停滞计数
        $consecutiveStaleRounds = 0
        if ($newTotal -gt $bestScore) {
            $bestScore = $newTotal
            $bestDraftContent = $revisedDraft
        }
        $previousScore = $newTotal
    }
    else {
        # 分数持平，计为停滞
        $consecutiveStaleRounds++
        $previousScore = $newTotal
    }

    $roundResults += [ordered]@{
        round = $round
        status = "completed"
        revise_started_at = $reviseStartedAt
        revise_completed_at = $reviseCompletedAt
        revised_draft_path = $revisedDraftPath
        score_before = $currentTotal
        score_after = $newTotal
        qualified_after = if ($newScore) { $newScore.qualified } else { $null }
        missing_before = $missingItems.Count
        missing_after = if ($newScore) { @($newScore.missing_or_misaligned).Count } else { $null }
        rollback_applied = $rollbackApplied
        consecutive_stale_rounds = $consecutiveStaleRounds
        best_score = $bestScore
    }

    # 更新当前路径
    $currentDraftPath = $draftPath
    $currentScorePath = $newScorePath

    # 退出条件: 达到目标分数
    if ($newScore -and $newTotal -ge $TargetScore) {
        break
    }

    # 退出条件: 连续不提分达上限
    if ($consecutiveStaleRounds -ge $MaxStaleRounds) {
        break
    }
}

# 写 manifest
$finalScore = if (Test-Path -LiteralPath $scorePath) { Read-JsonFile -Path $scorePath } else { $null }
$manifest = [pscustomobject][ordered]@{
    candidate_id = $candidate.id
    candidate_name = $candidate.name
    max_rounds = $MaxRounds
    target_score = $TargetScore
    max_stale_rounds = $MaxStaleRounds
    actual_rounds = $roundResults.Count
    best_score_achieved = $bestScore
    final_stale_rounds = $consecutiveStaleRounds
    rounds = $roundResults
    final_weighted_total = if ($finalScore) { $finalScore.weighted_total } else { $null }
    final_qualified = if ($finalScore) { $finalScore.qualified } else { $null }
}
Write-JsonFile -Path $reviseManifestPath -Payload $manifest

# 写 summary
$summaryLines = @(
    "# 白盒修稿摘要",
    "",
    "- 题目: $($candidate.id) / $($candidate.name)",
    "- 最大轮次: $MaxRounds",
    "- 目标分数: $TargetScore",
    "- 连续不提分上限: $MaxStaleRounds",
    "- 实际轮次: $($roundResults.Count)",
    "- 历史最高分: $bestScore",
    "- 最终连续停滞轮次: $consecutiveStaleRounds"
)

foreach ($r in $roundResults) {
    $summaryLines += ""
    $summaryLines += "## Round $($r.round)"
    $summaryLines += "- 状态: $($r.status)"
    if ($r.PSObject.Properties.Name -contains "score_before") { $summaryLines += "- 修前分数: $($r.score_before)" }
    if ($r.PSObject.Properties.Name -contains "score_after") { $summaryLines += "- 修后分数: $($r.score_after)" }
    if (($r.PSObject.Properties.Name -contains "qualified_after") -and $r.qualified_after -ne $null) { $summaryLines += "- 修后合格: $($r.qualified_after)" }
    if (($r.PSObject.Properties.Name -contains "missing_before") -and $r.missing_before -ne $null) { $summaryLines += "- 修前缺项: $($r.missing_before)" }
    if (($r.PSObject.Properties.Name -contains "missing_after") -and $r.missing_after -ne $null) { $summaryLines += "- 修后缺项: $($r.missing_after)" }
    if (($r.PSObject.Properties.Name -contains "rollback_applied") -and $r.rollback_applied) { $summaryLines += "- **回滚已执行**: 分数下降，已回退到最高分版本 ($($r.best_score))" }
    if (($r.PSObject.Properties.Name -contains "consecutive_stale_rounds") -and $r.consecutive_stale_rounds) { $summaryLines += "- 连续停滞轮次: $($r.consecutive_stale_rounds)" }
    if ($r.PSObject.Properties.Name -contains "error" -and $r.error) { $summaryLines += "- 错误: $($r.error)" }
}

if ($finalScore) {
    $summaryLines += ""
    $summaryLines += "## 最终"
    $summaryLines += "- 总分: $($finalScore.weighted_total)"
    $summaryLines += "- 合格: $($finalScore.qualified)"
}

Set-Content -LiteralPath $reviseSummaryPath -Value $summaryLines -Encoding UTF8

Write-Host "[INFO] 修稿摘要: $reviseSummaryPath"
Write-Host "[INFO] 修稿清单: $reviseManifestPath"

$finalExitCode = if ($finalScore -and $finalScore.qualified) { 0 } else { 1 }
exit $finalExitCode
