param(
    [string]$CandidatePool = "",
    [string]$PlanConfig = "",
    [string]$OutputRoot = "D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_phase",
    [string]$ApiKey = "",
    [switch]$EnableReferenceSample
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    return Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

function Get-DefaultCandidatePool {
    return Join-Path $PSScriptRoot "iiia_whitebox_candidate_pool.json"
}

function Get-DefaultPlanConfig {
    return Join-Path $PSScriptRoot "iiia_whitebox_plan.json"
}

function Get-PhaseRunnerPath {
    return Join-Path (Get-RepoRoot) "docs\多Agent藏经阁实验\侠客岛白盒编排器\run_ii_whitebox_phase.ps1"
}

$poolPath = if ($CandidatePool) { $CandidatePool } else { Get-DefaultCandidatePool }
$planPath = if ($PlanConfig) { $PlanConfig } else { Get-DefaultPlanConfig }
$phaseRunner = Get-PhaseRunnerPath

if (-not (Test-Path -LiteralPath $poolPath)) {
    throw "IIIA 白盒候选池不存在: $poolPath"
}

if (-not (Test-Path -LiteralPath $planPath)) {
    throw "IIIA 白盒计划不存在: $planPath"
}

if (-not (Test-Path -LiteralPath $phaseRunner)) {
    throw "白盒 phase 入口不存在: $phaseRunner"
}

& $phaseRunner -CandidatePool $poolPath -PlanConfig $planPath -OutputRoot $OutputRoot -ApiKey $ApiKey -EnableReferenceSample:$EnableReferenceSample
exit $LASTEXITCODE
