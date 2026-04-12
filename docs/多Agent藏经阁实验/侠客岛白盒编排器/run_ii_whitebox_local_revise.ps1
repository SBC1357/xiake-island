param(
    [string]$CandidateId,
    [string]$CandidatePool = "",
    [string]$RunDirectory = "",
    [string]$ApiKey = "",
    [int]$MaxRounds = 3,
    [int]$TargetScore = 85,
    [int]$MaxStaleRounds = 2,
    [int]$MaxLocalTasksPerRound = 4
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "whitebox_common.ps1")

function Write-JsonFileDeep {
    param(
        [string]$Path,
        [object]$Payload
    )
    $Payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Split-DraftParagraphs {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return @()
    }

    return @(
        [regex]::Split($Text.Trim(), "\r?\n\s*\r?\n") |
            ForEach-Object { $_.Trim() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
}

function Join-DraftParagraphs {
    param([string[]]$Paragraphs)

    return ((@($Paragraphs) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join "`r`n`r`n")
}

function Get-ParagraphNumberedText {
    param([string[]]$Paragraphs)

    $lines = @()
    for ($i = 0; $i -lt $Paragraphs.Count; $i++) {
        $lines += "[$($i + 1)] $($Paragraphs[$i])"
        $lines += ""
    }
    return ($lines -join "`n").Trim()
}

function Get-SafeParagraph {
    param(
        [string[]]$Paragraphs,
        [int]$Index
    )

    if ($Index -lt 0 -or $Index -ge $Paragraphs.Count) {
        return ""
    }
    return $Paragraphs[$Index]
}

function Get-FormulaBlock {
    param([object]$Contract)

    $fc = $Contract.formula_contract
    if ($null -eq $fc) {
        return ""
    }

    $parts = @()
    $parts += "【公式驱动约束】"
    if ($fc.persona) { $parts += "- 人格定位：$($fc.persona)" }
    if ($fc.range) { $parts += "- 写作范围：$($fc.range)" }
    if ($fc.write_target) { $parts += "- 写作目标：$($fc.write_target)" }
    if ($fc.content_combo) { $parts += "- 内容组合：$($fc.content_combo)" }
    if ($fc.logic_combo) { $parts += "- 逻辑组合：$($fc.logic_combo)" }

    $ecu = @()
    if ($fc.PSObject.Properties.Name -contains "effective_content_unit") {
        $ecu = @($fc.effective_content_unit)
    }
    if ($ecu.Count -gt 0) {
        $parts += "- 有效内容单元："
        foreach ($item in $ecu) { $parts += "  - $item" }
    }

    $eOutline = @()
    if ($fc.PSObject.Properties.Name -contains "effective_outline") {
        $eOutline = @($fc.effective_outline)
    }
    if ($eOutline.Count -gt 0) {
        $parts += "- 有效大纲："
        foreach ($item in $eOutline) { $parts += "  - $item" }
    }

    return ($parts -join "`n")
}

function Get-MaterialsBlock {
    param([string]$RunDirectory)

    $materialsManifestPath = Join-Path (Join-Path $RunDirectory "materials") "materials_manifest.json"
    if (-not (Test-Path -LiteralPath $materialsManifestPath)) {
        return ""
    }

    $materialsManifest = Read-JsonFile -Path $materialsManifestPath
    $compiledTextPath = $materialsManifest.compiled_text
    if (-not $compiledTextPath -or -not (Test-Path -LiteralPath $compiledTextPath)) {
        return ""
    }

    $compiledMaterialsText = [System.IO.File]::ReadAllText($compiledTextPath, [System.Text.Encoding]::UTF8)
    if ([string]::IsNullOrWhiteSpace($compiledMaterialsText)) {
        return ""
    }

    return @"
【原材料摘录（局部返修缺失事实只能从这里补）】
$($compiledMaterialsText.Substring(0, [Math]::Min(16000, $compiledMaterialsText.Length)))
"@
}

function Invoke-LocalTaskRouting {
    param(
        [object]$CurrentScore,
        [string[]]$Paragraphs,
        [object]$Contract,
        [int]$MaxTasks,
        [string]$ApiKey
    )

    $formulaBlock = Get-FormulaBlock -Contract $Contract
    $paragraphText = Get-ParagraphNumberedText -Paragraphs $Paragraphs
    $blockingIssues = (@($CurrentScore.blocking_issues) | ForEach-Object { "- $_" }) -join "`n"
    $missingIssues = (@($CurrentScore.missing_or_misaligned) | ForEach-Object { "- $_" }) -join "`n"
    $nextActions = (@($CurrentScore.next_actions) | ForEach-Object { "- $_" }) -join "`n"

    $prompt = @"
你是侠客岛白盒编排器的“局部返修任务路由器”。目标不是提分，而是把审核问题拆成可执行的局部返修任务。

【写作合同】
- 题目：$($Contract.candidate_name)
- 受众：$($Contract.writing_contract.audience)
- 写作目的：$($Contract.writing_contract.purpose)

$formulaBlock

【当前评分问题】
阻塞问题：
$blockingIssues

缺失或偏差项：
$missingIssues

建议修改动作：
$nextActions

【当前稿件（按段编号）】
$paragraphText

请输出严格 JSON：
{
  "routing_summary": "...",
  "tasks": [
    {
      "task_id": "L1",
      "issue_level": "local|structural|task_understanding",
      "issue_source": "对应 blocking/missing/next_action 的原句",
      "target_paragraph": 1,
      "instruction": "这次只改什么",
      "acceptance_criteria": ["..."],
      "forbidden_changes": ["..."]
    }
  ]
}

规则：
1. 只有满足“1句话 / 1个信息点 / 1个空缺位”粒度的任务，才能标为 local。
2. 如果问题涉及故事线、大纲、稿型、受众、整段结构重构，必须标为 structural 或 task_understanding。
3. local 任务必须落到单个 target_paragraph。
4. 最多输出 $MaxTasks 条 local 任务；可以同时输出 structural/task_understanding 任务用于记录，但不要超过 8 条总任务。
5. instruction 必须可执行，不能写空话。
6. forbidden_changes 必须明确写“不要动什么”。
7. 只输出 JSON。
"@

    $prompt = Build-WhiteboxPromptWithProfile -Prompt $prompt -ProfileName "local_task_router"

    $raw = Invoke-WhiteboxLlm -Prompt $prompt -ApiKeyOverride $ApiKey -Temperature 0.1 -ProfileName "local_task_router"
    $parsed = Try-ParseJsonText -Text $raw
    if ($null -eq $parsed) {
        throw "无法解析局部返修任务 JSON"
    }
    return $parsed
}

function Invoke-LocalPatch {
    param(
        [object]$Task,
        [string[]]$Paragraphs,
        [object]$Contract,
        [string]$MaterialsBlock,
        [string]$ApiKey
    )

    $targetIndex = [Math]::Max(0, ([int]$Task.target_paragraph) - 1)
    $targetParagraph = Get-SafeParagraph -Paragraphs $Paragraphs -Index $targetIndex
    $previousParagraph = Get-SafeParagraph -Paragraphs $Paragraphs -Index ($targetIndex - 1)
    $nextParagraph = Get-SafeParagraph -Paragraphs $Paragraphs -Index ($targetIndex + 1)
    $formulaBlock = Get-FormulaBlock -Contract $Contract
    $acceptance = (@($Task.acceptance_criteria) | ForEach-Object { "- $_" }) -join "`n"
    $forbidden = (@($Task.forbidden_changes) | ForEach-Object { "- $_" }) -join "`n"

    $prompt = @"
你是侠客岛白盒编排器的“局部返修执行器”。这次只允许修改一个目标段落，其余上下文视为固定。

【写作合同】
- 题目：$($Contract.candidate_name)
- 受众：$($Contract.writing_contract.audience)
- 写作目的：$($Contract.writing_contract.purpose)

$formulaBlock

$MaterialsBlock

【任务来源】
- 来源问题：$($Task.issue_source)
- 目标段号：$($Task.target_paragraph)
- 本轮只改什么：$($Task.instruction)

【验收标准】
$acceptance

【不允许动的骨架】
$forbidden

【前文固定】
$previousParagraph

【待改段】
$targetParagraph

【后文固定】
$nextParagraph

执行规则：
1. 只输出“修改后的目标段落全文”，不要输出解释。
2. 不要改前文固定和后文固定。
3. 如需补一句过渡或医学描述，也只能在目标段内完成。
4. 缺失事实只能从原材料摘录中补，不能编造。
5. 尽量最小改动，优先精准补位，而不是整段重写风格。
"@

    $prompt = Build-WhiteboxPromptWithProfile -Prompt $prompt -ProfileName "local_patch"

    $revised = Invoke-WhiteboxLlm -Prompt $prompt -ApiKeyOverride $ApiKey -Temperature 0.2 -ProfileName "local_patch"
    return [pscustomobject]@{
        prompt = $prompt
        target_index = $targetIndex
        before = $targetParagraph
        after = $revised.Trim()
        previous = $previousParagraph
        next = $nextParagraph
    }
}

function Invoke-LocalPatchAudit {
    param(
        [object]$Task,
        [object]$PatchResult,
        [string]$ApiKey
    )

    $acceptance = (@($Task.acceptance_criteria) | ForEach-Object { "- $_" }) -join "`n"
    $forbidden = (@($Task.forbidden_changes) | ForEach-Object { "- $_" }) -join "`n"

    $prompt = @"
你是侠客岛白盒编排器的“局部返修核验器”。你只判断这次局部返修有没有按任务改准。

【任务来源】
- 来源问题：$($Task.issue_source)
- 本轮只改什么：$($Task.instruction)

【验收标准】
$acceptance

【不允许动的骨架】
$forbidden

【前文固定】
$($PatchResult.previous)

【原目标段】
$($PatchResult.before)

【修改后目标段】
$($PatchResult.after)

【后文固定】
$($PatchResult.next)

请输出严格 JSON：
{
  "status": "passed|failed",
  "executed_precisely": true,
  "issue_addressed": true,
  "scope_respected": true,
  "introduced_new_risk": false,
  "reason": "..."
}

规则：
1. 只看这次局部返修是否命中任务，不用重审整篇文章。
2. 如果任务要求没完成，issue_addressed=false。
3. 如果顺手改大了、改变了不该动的骨架，scope_respected=false。
4. 如果引入新事实风险、新路由偏移或明显新误导，introduced_new_risk=true。
5. 只有 executed_precisely=true、issue_addressed=true、scope_respected=true、introduced_new_risk=false 才能判 passed。
6. 只输出 JSON。
"@

    $prompt = Build-WhiteboxPromptWithProfile -Prompt $prompt -ProfileName "local_patch_audit"

    $raw = Invoke-WhiteboxLlm -Prompt $prompt -ApiKeyOverride $ApiKey -Temperature 0.1 -ProfileName "local_patch_audit"
    $parsed = Try-ParseJsonText -Text $raw
    if ($null -eq $parsed) {
        throw "无法解析局部返修核验 JSON"
    }
    return $parsed
}

if ([string]::IsNullOrWhiteSpace($RunDirectory)) {
    throw "必须提供 -RunDirectory。"
}

$poolData = Get-CandidatePoolData -Path $CandidatePool
$candidate = Resolve-Candidate -PoolData $poolData -CandidateId $CandidateId

$scorePath = Join-Path $RunDirectory "score.json"
$draftPath = Join-Path $RunDirectory "draft.txt"
$contractPath = Join-Path $RunDirectory "whitebox_contract.json"

if (-not (Test-Path -LiteralPath $scorePath)) { throw "缺少 score.json: $scorePath" }
if (-not (Test-Path -LiteralPath $draftPath)) { throw "缺少 draft.txt: $draftPath" }
if (-not (Test-Path -LiteralPath $contractPath)) { throw "缺少 whitebox_contract.json: $contractPath" }

$contract = Read-JsonFile -Path $contractPath
$materialsBlock = Get-MaterialsBlock -RunDirectory $RunDirectory

$reviseDir = Join-Path $RunDirectory "revise"
$localDir = Join-Path $RunDirectory "local_revise"
New-Item -ItemType Directory -Path $reviseDir -Force | Out-Null
New-Item -ItemType Directory -Path $localDir -Force | Out-Null

$reviseManifestPath = Join-Path $RunDirectory "revise_manifest.json"
$reviseSummaryPath = Join-Path $RunDirectory "revise_summary.md"
$localManifestPath = Join-Path $RunDirectory "local_revise_manifest.json"
$roundResults = @()

$currentDraftPath = $draftPath
$currentScorePath = $scorePath
$bestScore = 0
$bestDraftContent = ""
$previousScore = 0
$consecutiveStaleRounds = 0
$totalTaskCount = 0
$totalAppliedCount = 0
$totalPreciseCount = 0
$totalIssueClosedCount = 0
$totalScopeViolationCount = 0
$totalNewRiskCount = 0
$totalStructuralCount = 0
$totalTaskUnderstandingCount = 0

for ($round = 1; $round -le $MaxRounds; $round++) {
    $roundDir = Join-Path $localDir "round_$round"
    $taskPacketDir = Join-Path $roundDir "local_patch_packets"
    $taskResultDir = Join-Path $roundDir "local_patch_results"
    New-Item -ItemType Directory -Path $roundDir -Force | Out-Null
    New-Item -ItemType Directory -Path $taskPacketDir -Force | Out-Null
    New-Item -ItemType Directory -Path $taskResultDir -Force | Out-Null

    $currentScore = Read-JsonFile -Path $currentScorePath
    $currentDraft = [System.IO.File]::ReadAllText($currentDraftPath, [System.Text.Encoding]::UTF8)
    $currentTotal = [int]$currentScore.weighted_total

    if ($round -eq 1) {
        $bestScore = $currentTotal
        $bestDraftContent = $currentDraft
        $previousScore = $currentTotal
    }

    if ($currentTotal -ge $TargetScore -and @($currentScore.blocking_issues).Count -eq 0) {
        $roundResults += [ordered]@{
            round = $round
            mode = "local"
            status = "skipped_target_reached"
            reason = "总分 $currentTotal >= $TargetScore 且无阻塞问题"
        }
        break
    }

    if ($consecutiveStaleRounds -ge $MaxStaleRounds) {
        $roundResults += [ordered]@{
            round = $round
            mode = "local"
            status = "skipped_stale_plateau"
            reason = "连续 $consecutiveStaleRounds 轮局部返修未有效关闭问题"
        }
        break
    }

    $paragraphs = Split-DraftParagraphs -Text $currentDraft
    if ($paragraphs.Count -eq 0) {
        $roundResults += [ordered]@{
            round = $round
            mode = "local"
            status = "failed"
            error = "当前稿件无法拆成段落"
        }
        break
    }

    try {
        $routing = Invoke-LocalTaskRouting -CurrentScore $currentScore -Paragraphs $paragraphs -Contract $contract -MaxTasks $MaxLocalTasksPerRound -ApiKey $ApiKey
    }
    catch {
        $roundResults += [ordered]@{
            round = $round
            mode = "local"
            status = if ($_.Exception.Message -eq "missing_llm_api_key" -or $_.Exception.Message -like "llm_transport_unavailable:*") { "agent_continue_required" } else { "failed" }
            error = $_.Exception.Message
        }
        break
    }

    $routingPath = Join-Path $roundDir "revision_task_list.json"
    Write-JsonFileDeep -Path $routingPath -Payload $routing

    $allTasks = @($routing.tasks)
    $localTasks = @($allTasks | Where-Object { $_.issue_level -eq "local" } | Select-Object -First $MaxLocalTasksPerRound)
    $structuralTasks = @($allTasks | Where-Object { $_.issue_level -eq "structural" })
    $taskUnderstandingTasks = @($allTasks | Where-Object { $_.issue_level -eq "task_understanding" })
    $totalStructuralCount += $structuralTasks.Count
    $totalTaskUnderstandingCount += $taskUnderstandingTasks.Count

    if ($localTasks.Count -eq 0) {
        $roundResults += [ordered]@{
            round = $round
            mode = "local"
            status = "skipped_no_local_tasks"
            routing_summary = $routing.routing_summary
            structural_task_count = $structuralTasks.Count
            task_understanding_count = $taskUnderstandingTasks.Count
            reason = "当前轮没有可在局部粒度下安全执行的任务"
        }
        break
    }

    $roundTaskResults = @()
    $roundAppliedCount = 0
    $roundPreciseCount = 0
    $roundIssueClosedCount = 0
    $roundScopeViolationCount = 0
    $roundNewRiskCount = 0

    foreach ($task in $localTasks) {
        $taskId = if ($task.task_id) { [string]$task.task_id } else { "L$($roundTaskResults.Count + 1)" }
        $packetPath = Join-Path $taskPacketDir "${taskId}.json"
        Write-JsonFileDeep -Path $packetPath -Payload $task

        $targetIndex = ([int]$task.target_paragraph) - 1
        if ($targetIndex -lt 0 -or $targetIndex -ge $paragraphs.Count) {
            $result = [ordered]@{
                task_id = $taskId
                status = "failed_target_not_found"
                target_paragraph = $task.target_paragraph
            }
            $resultPath = Join-Path $taskResultDir "${taskId}.json"
            Write-JsonFileDeep -Path $resultPath -Payload $result
            $roundTaskResults += $result
            continue
        }

        try {
            $patch = Invoke-LocalPatch -Task $task -Paragraphs $paragraphs -Contract $contract -MaterialsBlock $materialsBlock -ApiKey $ApiKey
            $patchPromptPath = Join-Path $taskPacketDir "${taskId}_prompt.md"
            Set-Content -LiteralPath $patchPromptPath -Value $patch.prompt -Encoding UTF8
            $patchOutputPath = Join-Path $taskPacketDir "${taskId}_output.txt"
            Set-Content -LiteralPath $patchOutputPath -Value $patch.after -Encoding UTF8

            $audit = Invoke-LocalPatchAudit -Task $task -PatchResult $patch -ApiKey $ApiKey
            $result = [ordered]@{
                task_id = $taskId
                status = $audit.status
                issue_source = $task.issue_source
                target_paragraph = $task.target_paragraph
                executed_precisely = [bool]$audit.executed_precisely
                issue_addressed = [bool]$audit.issue_addressed
                scope_respected = [bool]$audit.scope_respected
                introduced_new_risk = [bool]$audit.introduced_new_risk
                applied = $false
                reason = [string]$audit.reason
                original_paragraph = $patch.before
                revised_paragraph = $patch.after
            }

            if ($result.executed_precisely) { $roundPreciseCount++ }
            if (-not $result.scope_respected) { $roundScopeViolationCount++ }
            if ($result.introduced_new_risk) { $roundNewRiskCount++ }

            if ($result.executed_precisely -and $result.issue_addressed -and $result.scope_respected -and -not $result.introduced_new_risk) {
                $paragraphs[$targetIndex] = $patch.after
                $result.applied = $true
                $roundAppliedCount++
                $roundIssueClosedCount++
            }

            $resultPath = Join-Path $taskResultDir "${taskId}.json"
            Write-JsonFileDeep -Path $resultPath -Payload $result
            $roundTaskResults += $result
        }
        catch {
            $result = [ordered]@{
                task_id = $taskId
                status = if ($_.Exception.Message -eq "missing_llm_api_key" -or $_.Exception.Message -like "llm_transport_unavailable:*") { "agent_continue_required" } else { "failed" }
                error = $_.Exception.Message
            }
            $resultPath = Join-Path $taskResultDir "${taskId}.json"
            Write-JsonFileDeep -Path $resultPath -Payload $result
            $roundTaskResults += $result
            if ($result.status -eq "agent_continue_required") {
                $roundResults += [ordered]@{
                    round = $round
                    mode = "local"
                    status = "agent_continue_required"
                    error = $result.error
                }
                break
            }
        }
    }

    if ($roundResults.Count -gt 0 -and $roundResults[-1].status -eq "agent_continue_required") {
        break
    }

    $totalTaskCount += $localTasks.Count
    $totalAppliedCount += $roundAppliedCount
    $totalPreciseCount += $roundPreciseCount
    $totalIssueClosedCount += $roundIssueClosedCount
    $totalScopeViolationCount += $roundScopeViolationCount
    $totalNewRiskCount += $roundNewRiskCount

    $revisedDraft = Join-DraftParagraphs -Paragraphs $paragraphs
    $revisedDraftPath = Join-Path $roundDir "revised_draft.txt"
    Set-Content -LiteralPath $revisedDraftPath -Value $revisedDraft -Encoding UTF8

    if ($roundAppliedCount -gt 0) {
        Set-Content -LiteralPath $draftPath -Value $revisedDraft -Encoding UTF8
        $scoreScriptPath = Join-Path $PSScriptRoot "run_ii_whitebox_score.ps1"
        $scoreArgs = @{
            CandidateId = $CandidateId
            CandidatePool = $(if ($CandidatePool) { $CandidatePool } else { "" })
            RunDirectory = $RunDirectory
            ApiKey = $ApiKey
        }
        try {
            & $scoreScriptPath @scoreArgs
        }
        catch {
        }
    }

    $newScore = if (Test-Path -LiteralPath $scorePath) { Read-JsonFile -Path $scorePath } else { $currentScore }
    $newTotal = [int]$newScore.weighted_total
    $roundScorePath = Join-Path $roundDir "score.json"
    Write-JsonFileDeep -Path $roundScorePath -Payload $newScore

    $precisionRate = if ($localTasks.Count -gt 0) { [Math]::Round(($roundPreciseCount / $localTasks.Count), 4) } else { 0 }
    $issueCloseRate = if ($localTasks.Count -gt 0) { [Math]::Round(($roundIssueClosedCount / $localTasks.Count), 4) } else { 0 }

    if ($newTotal -gt $bestScore) {
        $bestScore = $newTotal
        $bestDraftContent = [System.IO.File]::ReadAllText($draftPath, [System.Text.Encoding]::UTF8)
    }

    if ($roundIssueClosedCount -gt 0 -or $newTotal -gt $previousScore) {
        $consecutiveStaleRounds = 0
    }
    else {
        $consecutiveStaleRounds++
    }
    $previousScore = $newTotal

    $roundResults += [ordered]@{
        round = $round
        mode = "local"
        status = "completed"
        routing_summary = $routing.routing_summary
        local_task_count = $localTasks.Count
        structural_task_count = $structuralTasks.Count
        task_understanding_count = $taskUnderstandingTasks.Count
        applied_task_count = $roundAppliedCount
        precise_task_count = $roundPreciseCount
        issue_closed_count = $roundIssueClosedCount
        scope_violation_count = $roundScopeViolationCount
        new_risk_count = $roundNewRiskCount
        precision_rate = $precisionRate
        issue_close_rate = $issueCloseRate
        score_before = $currentTotal
        score_after = $newTotal
        qualified_after = $newScore.qualified
        revised_draft_path = $revisedDraftPath
    }

    if ($currentTotal -ge $TargetScore -or $consecutiveStaleRounds -ge $MaxStaleRounds) {
        break
    }
}

$finalScore = if (Test-Path -LiteralPath $scorePath) { Read-JsonFile -Path $scorePath } else { $null }
$executionPrecisionRate = if ($totalTaskCount -gt 0) { [Math]::Round(($totalPreciseCount / $totalTaskCount), 4) } else { 0 }
$issueCloseRateOverall = if ($totalTaskCount -gt 0) { [Math]::Round(($totalIssueClosedCount / $totalTaskCount), 4) } else { 0 }

$localManifest = [pscustomobject][ordered]@{
    candidate_id = $candidate.id
    candidate_name = $candidate.name
    revise_mode = "local"
    primary_metric = "execution_precision"
    max_rounds = $MaxRounds
    target_score = $TargetScore
    max_stale_rounds = $MaxStaleRounds
    max_local_tasks_per_round = $MaxLocalTasksPerRound
    actual_rounds = $roundResults.Count
    total_task_count = $totalTaskCount
    total_applied_task_count = $totalAppliedCount
    total_precise_task_count = $totalPreciseCount
    total_issue_closed_count = $totalIssueClosedCount
    total_scope_violation_count = $totalScopeViolationCount
    total_new_risk_count = $totalNewRiskCount
    total_structural_task_count = $totalStructuralCount
    total_task_understanding_count = $totalTaskUnderstandingCount
    execution_precision_rate = $executionPrecisionRate
    issue_close_rate = $issueCloseRateOverall
    final_weighted_total = if ($finalScore) { $finalScore.weighted_total } else { $null }
    final_qualified = if ($finalScore) { $finalScore.qualified } else { $null }
    best_score_achieved = $bestScore
    rounds = $roundResults
}
Write-JsonFileDeep -Path $localManifestPath -Payload $localManifest

$manifest = [pscustomobject][ordered]@{
    candidate_id = $candidate.id
    candidate_name = $candidate.name
    revise_mode = "local"
    primary_metric = "execution_precision"
    max_rounds = $MaxRounds
    target_score = $TargetScore
    max_stale_rounds = $MaxStaleRounds
    actual_rounds = $roundResults.Count
    best_score_achieved = $bestScore
    final_weighted_total = if ($finalScore) { $finalScore.weighted_total } else { $null }
    final_qualified = if ($finalScore) { $finalScore.qualified } else { $null }
    execution_precision_rate = $executionPrecisionRate
    issue_close_rate = $issueCloseRateOverall
    rounds = $roundResults
}
Write-JsonFileDeep -Path $reviseManifestPath -Payload $manifest

$summaryLines = @(
    "# 白盒局部返修摘要",
    "",
    "- 题目: $($candidate.id) / $($candidate.name)",
    "- 模式: local",
    "- 最大轮次: $MaxRounds",
    "- 每轮最多局部任务: $MaxLocalTasksPerRound",
    "- 实际轮次: $($roundResults.Count)",
    "- 执行精度率: $executionPrecisionRate",
    "- 问题关闭率: $issueCloseRateOverall",
    "- 最终总分: $(if ($finalScore) { $finalScore.weighted_total } else { 'n/a' })",
    "- 最终合格: $(if ($finalScore) { $finalScore.qualified } else { 'n/a' })"
)

foreach ($round in $roundResults) {
    $summaryLines += ""
    $summaryLines += "## Round $($round.round)"
    $summaryLines += "- 状态: $($round.status)"
    if ($round.PSObject.Properties.Name -contains "routing_summary") { $summaryLines += "- 路由摘要: $($round.routing_summary)" }
    if ($round.PSObject.Properties.Name -contains "local_task_count") { $summaryLines += "- 局部任务: $($round.local_task_count)" }
    if ($round.PSObject.Properties.Name -contains "applied_task_count") { $summaryLines += "- 实际应用: $($round.applied_task_count)" }
    if ($round.PSObject.Properties.Name -contains "precise_task_count") { $summaryLines += "- 精准执行: $($round.precise_task_count)" }
    if ($round.PSObject.Properties.Name -contains "issue_closed_count") { $summaryLines += "- 关闭问题: $($round.issue_closed_count)" }
    if ($round.PSObject.Properties.Name -contains "scope_violation_count") { $summaryLines += "- 越界改动: $($round.scope_violation_count)" }
    if ($round.PSObject.Properties.Name -contains "new_risk_count") { $summaryLines += "- 新风险: $($round.new_risk_count)" }
    if ($round.PSObject.Properties.Name -contains "score_before") { $summaryLines += "- 修前分数: $($round.score_before)" }
    if ($round.PSObject.Properties.Name -contains "score_after") { $summaryLines += "- 修后分数: $($round.score_after)" }
}

Set-Content -LiteralPath $reviseSummaryPath -Value $summaryLines -Encoding UTF8
Write-Host "[INFO] 局部返修摘要: $reviseSummaryPath"
Write-Host "[INFO] 局部返修清单: $localManifestPath"
exit 0
