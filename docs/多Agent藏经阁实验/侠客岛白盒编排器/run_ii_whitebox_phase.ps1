param(
    [string]$CandidatePool = "",
    [string]$PlanConfig = "",
    [string]$OutputRoot = "D:\汇度编辑部1\侠客岛-runtime\ii_whitebox_phase",
    [string]$ApiKey = "",
    [switch]$EnableReferenceSample
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-DefaultCandidatePool {
    return Join-Path (Join-Path $PSScriptRoot "config") "ii_candidate_pool.json"
}

function Get-DefaultPlanConfig {
    return Join-Path (Join-Path $PSScriptRoot "config") "ii_whitebox_plan.json"
}

function Read-JsonFile {
    param([string]$Path)
    $content = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    return $content | ConvertFrom-Json
}

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Payload
    )
    $convertCmd = Get-Command ConvertTo-Json
    if ($convertCmd.Parameters.ContainsKey("Depth")) {
        $Payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
    }
    else {
        $Payload | ConvertTo-Json | Set-Content -LiteralPath $Path -Encoding UTF8
    }
}

function Get-OptionalPropertyValue {
    param(
        [object]$Object,
        [string]$Name,
        [object]$Default = $null
    )

    if ($null -eq $Object) {
        return $Default
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $Default
    }

    return $property.Value
}

function Resolve-NewChildRunDirectory {
    param(
        [string]$ContractsRoot,
        [string[]]$KnownDirectories,
        [string]$CandidateId
    )

    if (-not (Test-Path -LiteralPath $ContractsRoot)) {
        return $null
    }

    $knownMap = @{}
    foreach ($path in @($KnownDirectories)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$path)) {
            $knownMap[$path] = $true
        }
    }

    $newDirectories = @(
        Get-ChildItem -LiteralPath $ContractsRoot -Directory |
            Where-Object { -not $knownMap.ContainsKey($_.FullName) }
    )

    if ($newDirectories.Count -eq 1) {
        return $newDirectories[0]
    }

    if ($newDirectories.Count -gt 1) {
        $candidateScoped = @($newDirectories | Where-Object { $_.Name -like "*_$CandidateId" })
        if ($candidateScoped.Count -eq 1) {
            return $candidateScoped[0]
        }
        if ($candidateScoped.Count -gt 1) {
            return @($candidateScoped | Sort-Object CreationTimeUtc -Descending)[0]
        }
        return @($newDirectories | Sort-Object CreationTimeUtc -Descending)[0]
    }

    return $null
}

$poolPath = if ($CandidatePool) { $CandidatePool } else { Get-DefaultCandidatePool }
$planPath = if ($PlanConfig) { $PlanConfig } else { Get-DefaultPlanConfig }

if (-not (Test-Path -LiteralPath $poolPath)) {
    throw "候选池不存在: $poolPath"
}
if (-not (Test-Path -LiteralPath $planPath)) {
    throw "白盒计划不存在: $planPath"
}

$pool = Read-JsonFile -Path $poolPath
$plan = Read-JsonFile -Path $planPath
$runnerPath = Join-Path $PSScriptRoot "run_ii_whitebox_orchestrator.ps1"
$materialsPath = Join-Path $PSScriptRoot "run_ii_whitebox_materials.ps1"
$draftPath = Join-Path $PSScriptRoot "run_ii_whitebox_draft.ps1"
$scorePath = Join-Path $PSScriptRoot "run_ii_whitebox_score.ps1"
$revisePath = Join-Path $PSScriptRoot "run_ii_whitebox_revise.ps1"

$revisePlan = Get-OptionalPropertyValue -Object $plan -Name "revise"
$reviseEnabled = [bool](Get-OptionalPropertyValue -Object $revisePlan -Name "enabled" -Default $false)
$reviseMaxRounds = [int](Get-OptionalPropertyValue -Object $revisePlan -Name "max_rounds" -Default 3)
$reviseTargetScore = [int](Get-OptionalPropertyValue -Object $revisePlan -Name "target_score" -Default 70)
$reviseMaxStaleRounds = [int](Get-OptionalPropertyValue -Object $revisePlan -Name "max_stale_rounds" -Default 2)
$reviseMode = [string](Get-OptionalPropertyValue -Object $revisePlan -Name "mode" -Default "whole")
$reviseMaxLocalTasksPerRound = [int](Get-OptionalPropertyValue -Object $revisePlan -Name "max_local_tasks_per_round" -Default 4)
$reviseApplyToQualified = [bool](Get-OptionalPropertyValue -Object $revisePlan -Name "apply_to_qualified" -Default $false)
$reviseEnableL1WritingCraft = [bool](Get-OptionalPropertyValue -Object $revisePlan -Name "enable_l1_writing_craft" -Default $false)
$reviseL1AssetsPath = [string](Get-OptionalPropertyValue -Object $revisePlan -Name "l1_assets_path" -Default "")

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$runDir = Join-Path $OutputRoot "${timestamp}_$($plan.plan_id)"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$summaryPath = Join-Path $runDir "phase_summary.md"
$manifestPath = Join-Path $runDir "phase_manifest.json"
$stepResults = @()
$overallStatus = "completed"
$contractsRoot = Join-Path $runDir "contracts"
New-Item -ItemType Directory -Path $contractsRoot -Force | Out-Null

foreach ($candidateId in @($plan.candidate_order)) {
    $candidate = @($pool.candidates | Where-Object { $_.id -eq $candidateId }) | Select-Object -First 1
    if (-not $candidate) {
        $stepResults += [pscustomobject][ordered]@{
            candidate_id = $candidateId
            status = "missing_candidate"
            exit_code = 1
        }
        $overallStatus = "failed"
        break
    }

    $knownContractRuns = @(
        if (Test-Path -LiteralPath $contractsRoot) {
            Get-ChildItem -LiteralPath $contractsRoot -Directory | ForEach-Object { $_.FullName }
        }
    )

    & $runnerPath -CandidateId $candidateId -CandidatePool $poolPath -OutputRoot $contractsRoot -EnableReferenceSample:$EnableReferenceSample
    $exitCode = $LASTEXITCODE
    $latestRun = Resolve-NewChildRunDirectory -ContractsRoot $contractsRoot -KnownDirectories $knownContractRuns -CandidateId $candidateId
    $manifestFile = if ($latestRun) { Join-Path $latestRun.FullName "whitebox_manifest.json" } else { $null }
    $summaryFile = if ($latestRun) { Join-Path $latestRun.FullName "whitebox_summary.md" } else { $null }
    $contractFile = if ($latestRun) { Join-Path $latestRun.FullName "whitebox_contract.json" } else { $null }
    $childManifest = if ($manifestFile -and (Test-Path -LiteralPath $manifestFile)) { Read-JsonFile -Path $manifestFile } else { $null }

    $status = switch ($exitCode) {
        0 { "ready" }
        2 { "blocked_manual" }
        default { "failed" }
    }

    $materialsManifest = $null
    $draftManifest = $null
    $scoreManifest = $null
    $reviseManifest = $null
    $reviseSummary = $null
    $reviseOperationalStatus = "not_requested"
    $finalStatus = $status
    $finalExitCode = $exitCode
    $finalError = if ($childManifest -and $childManifest.status -eq "blocked_manual") { "存在人工阻塞" } else { $null }

    if ($status -eq "ready" -and -not $latestRun) {
        $finalStatus = "failed"
        $finalExitCode = 1
        $finalError = "无法精确绑定本轮白盒子运行目录"
    }

    if ($status -eq "ready" -and $latestRun) {
        & $materialsPath -CandidateId $candidateId -CandidatePool $poolPath -RunDirectory $latestRun.FullName
        $materialsExit = $LASTEXITCODE
        $materialsManifestFile = Join-Path (Join-Path $latestRun.FullName "materials") "materials_manifest.json"
        if (Test-Path -LiteralPath $materialsManifestFile) {
            $materialsManifest = Read-JsonFile -Path $materialsManifestFile
        }
        if ($materialsExit -ne 0) {
            $finalStatus = "failed"
            $finalExitCode = $materialsExit
            $finalError = "白盒取材失败"
        }
    }

    if ($finalStatus -eq "ready" -and $latestRun) {
        & $draftPath -CandidateId $candidateId -CandidatePool $poolPath -RunDirectory $latestRun.FullName -ApiKey $ApiKey
        $draftExit = $LASTEXITCODE
        $draftManifestFile = Join-Path $latestRun.FullName "draft_manifest.json"
        if (Test-Path -LiteralPath $draftManifestFile) {
            $draftManifest = Read-JsonFile -Path $draftManifestFile
        }
        if ($draftExit -eq 4) {
            $finalStatus = "agent_continue_required"
            $finalExitCode = $draftExit
            $finalError = if ($draftManifest) { $draftManifest.error } else { "白盒出稿需由托管 session 继续" }
        }
        elseif ($draftExit -ne 0) {
            $finalStatus = "failed"
            $finalExitCode = $draftExit
            $finalError = if ($draftManifest) { $draftManifest.error } else { "白盒出稿失败" }
        }
    }

    if ($finalStatus -eq "ready" -and $latestRun) {
        & $scorePath -CandidateId $candidateId -CandidatePool $poolPath -RunDirectory $latestRun.FullName -ApiKey $ApiKey
        $scoreExit = $LASTEXITCODE
        $scoreManifestFile = Join-Path $latestRun.FullName "score_manifest.json"
        if (Test-Path -LiteralPath $scoreManifestFile) {
            $scoreManifest = Read-JsonFile -Path $scoreManifestFile
        }
        if ($scoreExit -eq 4) {
            $finalStatus = "agent_continue_required"
            $finalExitCode = $scoreExit
            $finalError = if ($scoreManifest) { $scoreManifest.error } else { "白盒评分需由托管 session 继续" }
        }
        elseif ($scoreExit -ne 0) {
            $finalStatus = "failed"
            $finalExitCode = $scoreExit
            $finalError = if ($scoreManifest) { $scoreManifest.error } else { "白盒评分失败" }
        }
        else {
            $finalStatus = "completed"
            $finalExitCode = 0
            $finalError = $null
        }
    }

    if ($finalStatus -eq "completed" -and $latestRun -and $reviseEnabled) {
        $currentScore = if (Test-Path -LiteralPath (Join-Path $latestRun.FullName "score.json")) {
            Read-JsonFile -Path (Join-Path $latestRun.FullName "score.json")
        }
        else {
            $null
        }

        $shouldRunRevise = $true
        if ($currentScore -and -not $reviseApplyToQualified -and $currentScore.qualified) {
            $shouldRunRevise = $false
        }

        if ($shouldRunRevise) {
            if (-not (Test-Path -LiteralPath $revisePath)) {
                $finalStatus = "failed"
                $finalExitCode = 1
                $finalError = "白盒返修入口不存在: $revisePath"
            }
            else {
                $reviseArgs = @{
                    CandidateId = $candidateId
                    CandidatePool = $poolPath
                    RunDirectory = $latestRun.FullName
                    ApiKey = $ApiKey
                    MaxRounds = $reviseMaxRounds
                    TargetScore = $reviseTargetScore
                    MaxStaleRounds = $reviseMaxStaleRounds
                    ReviseMode = $reviseMode
                    MaxLocalTasksPerRound = $reviseMaxLocalTasksPerRound
                }

                if ($reviseEnableL1WritingCraft) {
                    $reviseArgs.EnableL1WritingCraft = $true
                    if (-not [string]::IsNullOrWhiteSpace($reviseL1AssetsPath)) {
                        $reviseArgs.L1AssetsPath = $reviseL1AssetsPath
                    }
                }

                & $revisePath @reviseArgs
                $reviseManifestFile = Join-Path $latestRun.FullName "revise_manifest.json"
                $reviseSummaryFile = Join-Path $latestRun.FullName "revise_summary.md"
                $reviseManifest = if (Test-Path -LiteralPath $reviseManifestFile) { Read-JsonFile -Path $reviseManifestFile } else { $null }
                $reviseSummary = if (Test-Path -LiteralPath $reviseSummaryFile) { $reviseSummaryFile } else { $null }

                if (-not $reviseManifest) {
                    $finalStatus = "failed"
                    $finalExitCode = 1
                    $finalError = "白盒返修未产出 revise_manifest.json"
                }
                else {
                    $roundStatuses = @($reviseManifest.rounds | ForEach-Object { $_.status })
                    if ($roundStatuses -contains "agent_continue_required") {
                        $reviseOperationalStatus = "agent_continue_required"
                        $finalStatus = "agent_continue_required"
                        $finalExitCode = 4
                        $finalError = "白盒返修需托管 session 继续"
                    }
                    elseif ($roundStatuses -contains "failed") {
                        $reviseOperationalStatus = "failed"
                        $failedRound = @($reviseManifest.rounds | Where-Object { $_.status -eq "failed" }) | Select-Object -First 1
                        $finalStatus = "failed"
                        $finalExitCode = 1
                        $finalError = if ($failedRound -and $failedRound.error) { [string]$failedRound.error } else { "白盒返修失败" }
                    }
                    else {
                        $reviseOperationalStatus = "completed"
                        $scoreManifestFile = Join-Path $latestRun.FullName "score_manifest.json"
                        if (Test-Path -LiteralPath $scoreManifestFile) {
                            $scoreManifest = Read-JsonFile -Path $scoreManifestFile
                        }
                        $finalStatus = "completed"
                        $finalExitCode = 0
                        $finalError = $null
                    }
                }
            }
        }
        else {
            $reviseOperationalStatus = "skipped_already_qualified"
        }
    }

    $stepResults += [pscustomobject][ordered]@{
        candidate_id = $candidateId
        candidate_name = $candidate.name
        case_type = $candidate.case_type
        status = $finalStatus
        exit_code = $finalExitCode
        run_directory = if ($latestRun) { $latestRun.FullName } else { $null }
        summary = if ($summaryFile -and (Test-Path -LiteralPath $summaryFile)) { $summaryFile } else { $null }
        manifest = if ($manifestFile -and (Test-Path -LiteralPath $manifestFile)) { $manifestFile } else { $null }
        contract = if ($contractFile -and (Test-Path -LiteralPath $contractFile)) { $contractFile } else { $null }
        materials = if ($materialsManifest) { $materialsManifest.run_directory } else { $null }
        draft = if ($draftManifest) { $draftManifest.draft_path } else { $null }
        draft_prompt = if ($draftManifest) { $draftManifest.draft_prompt_path } else { $null }
        score = if ($scoreManifest) { $scoreManifest.score_path } else { $null }
        score_prompt = if ($scoreManifest) { $scoreManifest.score_prompt_path } else { $null }
        revise_status = $reviseOperationalStatus
        revise_mode = if ($reviseEnabled) { $reviseMode } else { "not_requested" }
        revise_summary = $reviseSummary
        revise_manifest = if ($reviseManifest) { Join-Path $latestRun.FullName "revise_manifest.json" } else { $null }
        revise_best_score = if ($reviseManifest) { $reviseManifest.best_score_achieved } else { $null }
        revise_final_score = if ($reviseManifest) { $reviseManifest.final_weighted_total } else { $null }
        revise_final_qualified = if ($reviseManifest) { $reviseManifest.final_qualified } else { $null }
        error = $finalError
    }

    if ($finalStatus -eq "failed") {
        $overallStatus = "failed"
        break
    }

    if ($finalStatus -eq "blocked_manual") {
        $overallStatus = "blocked_manual"
        if (-not [bool]$plan.continue_on_blocked_manual) {
            break
        }
    }
    elseif ($finalStatus -eq "agent_continue_required") {
        $overallStatus = "agent_continue_required"
        break
    }
}

$phaseManifest = [pscustomobject][ordered]@{
    timestamp = $timestamp
    plan_id = $plan.plan_id
    status = $overallStatus
    run_directory = $runDir
    candidate_pool = $poolPath
    plan_config = $planPath
    steps = $stepResults
}
Write-JsonFile -Path $manifestPath -Payload $phaseManifest

$lines = @(
    "# III期白盒阶段摘要",
    "",
    "- 计划: $($plan.plan_id)",
    "- 状态: $overallStatus",
    "- 运行目录: $runDir",
    ""
)

foreach ($step in $stepResults) {
    $lines += "## $($step.candidate_id)"
    $lines += ""
    $lines += "- 名称: $($step.candidate_name)"
    $lines += "- 题型: $($step.case_type)"
    $lines += "- 状态: $($step.status)"
    $lines += "- 退出码: $($step.exit_code)"
    if ($step.run_directory) {
        $lines += "- 输出目录: $($step.run_directory)"
    }
    if ($step.summary) {
        $lines += "- 摘要: $($step.summary)"
    }
    if ($step.contract) {
        $lines += "- 合同: $($step.contract)"
    }
    if ($step.materials) {
        $lines += "- 取材目录: $($step.materials)"
    }
    if ($step.draft) {
        $lines += "- 稿件: $($step.draft)"
    }
    if ($step.draft_prompt) {
        $lines += "- 出稿提示词: $($step.draft_prompt)"
    }
    if ($step.score) {
        $lines += "- 评分: $($step.score)"
    }
    if ($step.score_prompt) {
        $lines += "- 评分提示词: $($step.score_prompt)"
    }
    if ($step.revise_status -and $step.revise_status -ne "not_requested") {
        $lines += "- 返修状态: $($step.revise_status)"
    }
    if ($step.revise_mode -and $step.revise_mode -ne "not_requested") {
        $lines += "- 返修模式: $($step.revise_mode)"
    }
    if ($step.revise_summary) {
        $lines += "- 返修摘要: $($step.revise_summary)"
    }
    if ($step.revise_manifest) {
        $lines += "- 返修清单: $($step.revise_manifest)"
    }
    if ($null -ne $step.revise_best_score) {
        $lines += "- 返修最高分: $($step.revise_best_score)"
    }
    if ($null -ne $step.revise_final_score) {
        $lines += "- 返修最终分: $($step.revise_final_score)"
    }
    if ($null -ne $step.revise_final_qualified) {
        $lines += "- 返修最终达标: $($step.revise_final_qualified)"
    }
    if ($step.error) {
        $lines += "- 说明: $($step.error)"
    }
    $lines += ""
}

Set-Content -LiteralPath $summaryPath -Value $lines -Encoding UTF8

Write-Host "[INFO] 白盒阶段摘要: $summaryPath"
Write-Host "[INFO] 白盒阶段清单: $manifestPath"

if ($overallStatus -eq "completed") {
    exit 0
}
if ($overallStatus -eq "blocked_manual") {
    exit 2
}
if ($overallStatus -eq "agent_continue_required") {
    exit 4
}
exit 1
