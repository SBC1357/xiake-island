param(
    [string]$PhaseRunDirectory,
    [string]$CandidatePool = "",
    [string]$PlanConfig = "",
    [string]$ApiKey = "",
    [string]$CandidateId = "",
    [string]$DraftTextPath = "",
    [string]$ScoreJsonPath = "",
    [switch]$EnableReferenceSample
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "whitebox_common.ps1")

function Get-DefaultPlanConfig {
    return Join-Path (Join-Path $PSScriptRoot "config") "ii_whitebox_plan.json"
}

function Get-CandidateRunDirectory {
    param(
        [string]$ContractsRoot,
        [string]$ResolvedCandidateId
    )

    if (-not (Test-Path -LiteralPath $ContractsRoot)) {
        return $null
    }

    return Get-ChildItem -LiteralPath $ContractsRoot -Directory |
        Where-Object { $_.Name -like "*_$ResolvedCandidateId" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

function Build-PhaseSummaryLines {
    param(
        [string]$PlanId,
        [string]$OverallStatus,
        [string]$RunDirectory,
        [object[]]$StepResults
    )

    $lines = @(
        "# II期白盒阶段摘要",
        "",
        "- 计划: $PlanId",
        "- 状态: $OverallStatus",
        "- 运行目录: $RunDirectory",
        ""
    )

    foreach ($step in $StepResults) {
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
        if ($step.error) {
            $lines += "- 说明: $($step.error)"
        }
        $lines += ""
    }

    return $lines
}

if ([string]::IsNullOrWhiteSpace($PhaseRunDirectory)) {
    throw "必须提供 -PhaseRunDirectory。"
}
if (-not (Test-Path -LiteralPath $PhaseRunDirectory)) {
    throw "白盒阶段目录不存在: $PhaseRunDirectory"
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
$contractsRoot = Join-Path $PhaseRunDirectory "contracts"
New-Item -ItemType Directory -Path $contractsRoot -Force | Out-Null

$runnerPath = Join-Path $PSScriptRoot "run_ii_whitebox_orchestrator.ps1"
$materialsPath = Join-Path $PSScriptRoot "run_ii_whitebox_materials.ps1"
$draftPath = Join-Path $PSScriptRoot "run_ii_whitebox_draft.ps1"
$scorePath = Join-Path $PSScriptRoot "run_ii_whitebox_score.ps1"
$summaryPath = Join-Path $PhaseRunDirectory "phase_summary.md"
$manifestPath = Join-Path $PhaseRunDirectory "phase_manifest.json"

$stepResults = @()
$overallStatus = "completed"

foreach ($resolvedCandidateId in @($plan.candidate_order)) {
    $candidate = @($pool.candidates | Where-Object { $_.id -eq $resolvedCandidateId }) | Select-Object -First 1
    if (-not $candidate) {
        $stepResults += [pscustomobject][ordered]@{
            candidate_id = $resolvedCandidateId
            status = "missing_candidate"
            exit_code = 1
        }
        $overallStatus = "failed"
        break
    }

    $candidateRun = Get-CandidateRunDirectory -ContractsRoot $contractsRoot -ResolvedCandidateId $resolvedCandidateId
    if (-not $candidateRun) {
        & $runnerPath -CandidateId $resolvedCandidateId -CandidatePool $poolPath -OutputRoot $contractsRoot -EnableReferenceSample:$EnableReferenceSample
        $candidateRun = Get-CandidateRunDirectory -ContractsRoot $contractsRoot -ResolvedCandidateId $resolvedCandidateId
    }

    $manifestFile = if ($candidateRun) { Join-Path $candidateRun.FullName "whitebox_manifest.json" } else { $null }
    $summaryFile = if ($candidateRun) { Join-Path $candidateRun.FullName "whitebox_summary.md" } else { $null }
    $contractFile = if ($candidateRun) { Join-Path $candidateRun.FullName "whitebox_contract.json" } else { $null }
    $childManifest = if ($manifestFile -and (Test-Path -LiteralPath $manifestFile)) { Read-JsonFile -Path $manifestFile } else { $null }

    $status = if ($childManifest) {
        $childManifest.status
    }
    else {
        "failed"
    }

    $materialsManifest = $null
    $draftManifest = $null
    $scoreManifest = $null
    $finalStatus = $status
    $finalExitCode = if ($status -eq "ready") { 0 } elseif ($status -eq "blocked_manual") { 2 } else { 1 }
    $finalError = if ($status -eq "blocked_manual") { "存在人工阻塞" } else { $null }

    if ($finalStatus -eq "ready" -and $candidateRun) {
        $materialsManifestFile = Join-Path (Join-Path $candidateRun.FullName "materials") "materials_manifest.json"
        if (-not (Test-Path -LiteralPath $materialsManifestFile)) {
            & $materialsPath -CandidateId $resolvedCandidateId -CandidatePool $poolPath -RunDirectory $candidateRun.FullName
        }
        if (Test-Path -LiteralPath $materialsManifestFile) {
            $materialsManifest = Read-JsonFile -Path $materialsManifestFile
        }
        else {
            $finalStatus = "failed"
            $finalExitCode = 1
            $finalError = "白盒取材失败"
        }
    }

    if ($finalStatus -eq "ready" -and $candidateRun) {
        $draftManifestFile = Join-Path $candidateRun.FullName "draft_manifest.json"
        if (-not (Test-Path -LiteralPath $draftManifestFile) -or ((Read-JsonFile -Path $draftManifestFile).status -ne "completed")) {
            $draftArgs = @{
                CandidateId = $resolvedCandidateId
                CandidatePool = $poolPath
                RunDirectory = $candidateRun.FullName
                ApiKey = $ApiKey
            }
            if ($resolvedCandidateId -eq $CandidateId -and $DraftTextPath) {
                $draftArgs.DraftTextPath = $DraftTextPath
            }
            & $draftPath @draftArgs
        }
        if (Test-Path -LiteralPath $draftManifestFile) {
            $draftManifest = Read-JsonFile -Path $draftManifestFile
        }
        if ($draftManifest -and $draftManifest.status -eq "completed") {
            $finalStatus = "ready"
            $finalExitCode = 0
            $finalError = $null
        }
        elseif ($draftManifest -and $draftManifest.status -eq "agent_continue_required") {
            $finalStatus = "agent_continue_required"
            $finalExitCode = 4
            $finalError = $draftManifest.error
        }
        else {
            $finalStatus = "failed"
            $finalExitCode = if ($draftManifest) { $draftManifest.exit_code } else { 1 }
            $finalError = if ($draftManifest) { $draftManifest.error } else { "白盒出稿失败" }
        }
    }

    if ($finalStatus -eq "ready" -and $candidateRun) {
        $scoreManifestFile = Join-Path $candidateRun.FullName "score_manifest.json"
        if (-not (Test-Path -LiteralPath $scoreManifestFile) -or ((Read-JsonFile -Path $scoreManifestFile).status -ne "completed")) {
            $scoreArgs = @{
                CandidateId = $resolvedCandidateId
                CandidatePool = $poolPath
                RunDirectory = $candidateRun.FullName
                ApiKey = $ApiKey
            }
            if ($resolvedCandidateId -eq $CandidateId -and $ScoreJsonPath) {
                $scoreArgs.ScoreJsonPath = $ScoreJsonPath
            }
            & $scorePath @scoreArgs
        }
        if (Test-Path -LiteralPath $scoreManifestFile) {
            $scoreManifest = Read-JsonFile -Path $scoreManifestFile
        }
        if ($scoreManifest -and $scoreManifest.status -eq "completed") {
            $finalStatus = "completed"
            $finalExitCode = 0
            $finalError = $null
        }
        elseif ($scoreManifest -and $scoreManifest.status -eq "agent_continue_required") {
            $finalStatus = "agent_continue_required"
            $finalExitCode = 4
            $finalError = $scoreManifest.error
        }
        else {
            $finalStatus = "failed"
            $finalExitCode = if ($scoreManifest) { $scoreManifest.exit_code } else { 1 }
            $finalError = if ($scoreManifest) { $scoreManifest.error } else { "白盒评分失败" }
        }
    }

    $stepResults += [pscustomobject][ordered]@{
        candidate_id = $resolvedCandidateId
        candidate_name = $candidate.name
        case_type = $candidate.case_type
        status = $finalStatus
        exit_code = $finalExitCode
        run_directory = if ($candidateRun) { $candidateRun.FullName } else { $null }
        summary = if ($summaryFile -and (Test-Path -LiteralPath $summaryFile)) { $summaryFile } else { $null }
        manifest = if ($manifestFile -and (Test-Path -LiteralPath $manifestFile)) { $manifestFile } else { $null }
        contract = if ($contractFile -and (Test-Path -LiteralPath $contractFile)) { $contractFile } else { $null }
        materials = if ($materialsManifest) { $materialsManifest.run_directory } else { $null }
        draft = if ($draftManifest) { $draftManifest.draft_path } else { $null }
        draft_prompt = if ($draftManifest) { $draftManifest.draft_prompt_path } else { $null }
        score = if ($scoreManifest) { $scoreManifest.score_path } else { $null }
        score_prompt = if ($scoreManifest) { $scoreManifest.score_prompt_path } else { $null }
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
    plan_id = $plan.plan_id
    status = $overallStatus
    run_directory = $PhaseRunDirectory
    candidate_pool = $poolPath
    plan_config = $planPath
    steps = $stepResults
}
Write-JsonFile -Path $manifestPath -Payload $phaseManifest
Set-Content -LiteralPath $summaryPath -Value (Build-PhaseSummaryLines -PlanId $plan.plan_id -OverallStatus $overallStatus -RunDirectory $PhaseRunDirectory -StepResults $stepResults) -Encoding UTF8

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
