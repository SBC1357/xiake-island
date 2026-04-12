param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$CasesConfig = "",
    [string]$CaseId = "lecanemab_patient",
    [string]$PreflightRoot = "D:\汇度编辑部1\侠客岛-runtime\iiia_preflight",
    [string]$SmokeOutputRoot = "D:\汇度编辑部1\侠客岛-runtime\ii_phase_runs",
    [switch]$RunSmoke,
    [Alias("ApiKey")]
    [string]$ScoringApiKey = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertFrom-JsonCompat {
    param([Parameter(ValueFromPipeline = $true)][string]$Text)

    process {
        if ($PSVersionTable.PSVersion.Major -ge 6) {
            return $Text | ConvertFrom-Json -Depth 100
        }
        return $Text | ConvertFrom-Json
    }
}

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-JsonCompat
}

function Get-Timestamp {
    return Get-Date -Format "yyyyMMdd_HHmmss"
}

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function New-PreflightRunDir {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$TargetId
    )

    Ensure-Directory -Path $Root
    $leaf = "{0}_{1}" -f (Get-Timestamp), $TargetId
    $dir = Join-Path $Root $leaf
    Ensure-Directory -Path $dir
    return $dir
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)]$Data,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $Data | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Test-ObjectKey {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Key
    )

    if ($null -eq $Object) {
        return $false
    }

    if ($Object -is [System.Collections.IDictionary]) {
        return $Object.Contains($Key)
    }

    return $Object.PSObject.Properties.Name -contains $Key
}

function Get-DefaultCasesConfig {
    return Join-Path (Join-Path $PSScriptRoot "..\config") "ii_benchmark_cases.json"
}

function Get-RepoRoot {
    return Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

function Get-RepoEnvPath {
    return Join-Path (Get-RepoRoot) ".env"
}

function Load-RepoEnv {
    param([string]$EnvPath)

    if (-not (Test-Path -LiteralPath $EnvPath)) {
        return
    }

    foreach ($line in Get-Content -LiteralPath $EnvPath -Encoding UTF8) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line.TrimStart().StartsWith('#')) { continue }
        $eqIndex = $line.IndexOf('=')
        if ($eqIndex -lt 1) { continue }

        $key = $line.Substring(0, $eqIndex).Trim()
        $value = $line.Substring($eqIndex + 1).Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        if (-not [Environment]::GetEnvironmentVariable($key)) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

function Get-RunBenchmarkPath {
    return Join-Path (Get-RepoRoot) "scripts\run_ii_benchmark.ps1"
}

function Get-BenchmarkRunnerPath {
    return Join-Path (Get-RepoRoot) "scripts\benchmark_runner.ps1"
}

function Get-CurrentTaskCardPath {
    return Join-Path (Get-RepoRoot) "docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\00_入口索引\03_当前阶段任务卡.md"
}

function Get-StagePlanPath {
    return Join-Path (Get-RepoRoot) "docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\05_阶段实验包\IIIA\04_试运行计划.md"
}

function Get-LegacyIIIAPath {
    return Join-Path (Get-RepoRoot) "docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\IIIA期试验\00_步骤拆解.md"
}

function Resolve-CaseCatalog {
    param([string]$ConfigPath)

    $resolvedPath = if ($ConfigPath) { $ConfigPath } else { Get-DefaultCasesConfig }
    if (-not (Test-Path -LiteralPath $resolvedPath)) {
        throw "题库配置不存在: $resolvedPath"
    }

    $config = Read-JsonFile -Path $resolvedPath
    return [pscustomobject]@{
        Path = $resolvedPath
        Config = $config
    }
}

function Resolve-CaseConfig {
    param(
        [Parameter(Mandatory = $true)]$Catalog,
        [Parameter(Mandatory = $true)][string]$TargetCaseId
    )

    foreach ($case in $Catalog.Config.cases) {
        if ($case.id -eq $TargetCaseId) {
            return $case
        }
    }

    throw "找不到 case_id=$TargetCaseId"
}

function Get-CaseShapeReport {
    param([Parameter(Mandatory = $true)]$CaseConfig)

    $caseDir = [string]$CaseConfig.dir
    $inputsDir = Join-Path $caseDir "inputs"
    $goldDir = Join-Path $caseDir "gold"

    $inputsExists = Test-Path -LiteralPath $inputsDir
    $goldExists = Test-Path -LiteralPath $goldDir
    $pdfCount = 0
    $docxCount = 0

    if ($inputsExists) {
        $pdfCount = @(Get-ChildItem -LiteralPath $inputsDir -File -Filter *.pdf -ErrorAction SilentlyContinue).Count
    }

    if ($goldExists) {
        $docxCount = @(Get-ChildItem -LiteralPath $goldDir -File -Filter *.docx -ErrorAction SilentlyContinue).Count
    }

    $allowed = $inputsExists -and $goldExists -and ($pdfCount -ge 1) -and ($docxCount -ge 1)

    return [ordered]@{
        case_id = [string]$CaseConfig.id
        case_name = [string]$CaseConfig.name
        case_dir = $caseDir
        inputs_dir = $inputsDir
        gold_dir = $goldDir
        inputs_exists = $inputsExists
        gold_exists = $goldExists
        pdf_count = $pdfCount
        docx_count = $docxCount
        allowed_for_smoke = $allowed
        blocked_reason = if ($allowed) {
            $null
        }
        elseif (-not $inputsExists -or -not $goldExists) {
            "缺少 inputs/ 或 gold/ 子目录"
        }
        elseif ($pdfCount -lt 1) {
            "inputs/ 下缺少 PDF"
        }
        else {
            "gold/ 下缺少 docx"
        }
    }
}

function Test-Health {
    param([Parameter(Mandatory = $true)][string]$HealthUrl)

    try {
        $resp = Invoke-RestMethod -Uri $HealthUrl -Method Get -TimeoutSec 10
        return [ordered]@{
            ok = $true
            url = $HealthUrl
            response = $resp
            error = $null
        }
    }
    catch {
        return [ordered]@{
            ok = $false
            url = $HealthUrl
            response = $null
            error = $_.Exception.Message
        }
    }
}

function Get-OpenCodeConfigPath {
    return "C:\Users\96138\.config\opencode\opencode.json"
}

function Get-ScoringEnvReport {
    param([string]$OverrideApiKey)

    $report = [ordered]@{
        override_key_present = -not [string]::IsNullOrWhiteSpace($OverrideApiKey)
        openai_api_key_present = -not [string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)
        xiagedao_api_key_present = -not [string]::IsNullOrWhiteSpace($env:XIAGEDAO_API_KEY)
        anthropic_api_key_present = -not [string]::IsNullOrWhiteSpace($env:ANTHROPIC_API_KEY)
        openai_base_url = $env:OPENAI_BASE_URL
        xiagedao_llm_base_url = $env:XIAGEDAO_LLM_BASE_URL
        opencode_config_exists = $false
        opencode_preferred_provider_present = $false
        ready_for_scoring = $false
        note = $null
    }

    $opencodeConfig = Get-OpenCodeConfigPath
    if (Test-Path -LiteralPath $opencodeConfig) {
        $report.opencode_config_exists = $true
        try {
            $config = Read-JsonFile -Path $opencodeConfig
            if ($null -ne $config -and (Test-ObjectKey -Object $config -Key "provider")) {
                $provider = $config.provider
                foreach ($name in @("volcengine-plan", "bailian-coding-plan", "minimax")) {
                    if (Test-ObjectKey -Object $provider -Key $name) {
                        $report.opencode_preferred_provider_present = $true
                        break
                    }
                }
            }
        }
        catch {
            $report.note = "opencode 配置读取失败: $($_.Exception.Message)"
        }
    }

    $report.ready_for_scoring = $report.override_key_present -or
        $report.openai_api_key_present -or
        $report.xiagedao_api_key_present -or
        $report.anthropic_api_key_present -or
        $report.opencode_preferred_provider_present

    if (-not $report.ready_for_scoring -and [string]::IsNullOrWhiteSpace([string]$report.note)) {
        $report.note = "未发现显式评分 key 或 opencode 首选 provider"
    }

    return $report
}

function Get-EntryContractReport {
    $runBenchmarkPath = Get-RunBenchmarkPath
    $runnerPath = Get-BenchmarkRunnerPath
    $planPath = Get-StagePlanPath
    $legacyPath = Get-LegacyIIIAPath
    $taskCardPath = Get-CurrentTaskCardPath

    $runContent = Get-Content -LiteralPath $runBenchmarkPath -Raw -Encoding UTF8
    $planContent = Get-Content -LiteralPath $planPath -Raw -Encoding UTF8
    $legacyContent = Get-Content -LiteralPath $legacyPath -Raw -Encoding UTF8
    $taskCardContent = Get-Content -LiteralPath $taskCardPath -Raw -Encoding UTF8

    return [ordered]@{
        run_benchmark_exists = Test-Path -LiteralPath $runBenchmarkPath
        benchmark_runner_exists = Test-Path -LiteralPath $runnerPath
        task_card_exists = Test-Path -LiteralPath $taskCardPath
        iiia_plan_exists = Test-Path -LiteralPath $planPath
        legacy_steps_exists = Test-Path -LiteralPath $legacyPath
        run_benchmark_calls_ps1_runner = $runContent -match 'benchmark_runner\.ps1'
        iiia_plan_mentions_unique_entry = $planContent -match 'run_ii_benchmark\.ps1'
        iiia_plan_mentions_unique_runner = $planContent -match 'benchmark_runner\.ps1'
        task_card_mentions_unique_entry = $taskCardContent -match 'run_ii_benchmark\.ps1'
        legacy_steps_marked_historical = $legacyContent -match '历史执行记录'
        default_suite_risk = $runContent -match '\$Suite\s*=\s*"IIC首批"'
        stale_environment_blocker_in_task_card = $taskCardContent -match '_overlapped' -or $taskCardContent -match 'WinError 10106'
    }
}

function Get-TruthSourceConflictReport {
    $taskCardPath = Get-CurrentTaskCardPath
    $planPath = Get-StagePlanPath
    $legacyPath = Get-LegacyIIIAPath

    $taskCardContent = Get-Content -LiteralPath $taskCardPath -Raw -Encoding UTF8
    $planContent = Get-Content -LiteralPath $planPath -Raw -Encoding UTF8
    $legacyContent = Get-Content -LiteralPath $legacyPath -Raw -Encoding UTF8

    $issues = @()

    if ($taskCardContent -match 'WinError 10106' -or $taskCardContent -match '_overlapped') {
        $issues += "当前阶段任务卡仍残留旧的 Codex 宿主环境 blocker 口径"
    }

    if ($planContent -match 'benchmark_runner\.py') {
        # Per-line check: only flag if benchmark_runner.py is mentioned positively as active executor
        $pyActiveRef = $false
        foreach ($line in ($planContent -split "`n")) {
            if ($line -match 'benchmark_runner\.py' -and $line -notmatch '不作为|不适合|不应|不承担') {
                $pyActiveRef = $true
                break
            }
        }
        if ($pyActiveRef) {
            $issues += "IIIA 试运行计划仍把 benchmark_runner.py 写成活跃评分执行器"
        }
    }

    if (-not ($legacyContent -match '历史执行记录')) {
        $issues += "旧 IIIA 步骤拆解未明确降为历史执行记录"
    }

    return [ordered]@{
        has_conflicts = ($issues.Count -gt 0)
        issues = $issues
    }
}

function Write-SummaryMarkdown {
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $lines = @(
        "# IIIA 自动化预检摘要",
        "",
        "- 目标 case: $($Manifest.case_id)",
        "- 预检目录: $($Manifest.preflight_dir)",
        "- health: $(if ($Manifest.health.ok) { 'ok' } else { 'failed' })",
        "- case 形态: $(if ($Manifest.case_shape.allowed_for_smoke) { 'allow' } else { 'blocked' })",
        "- 评分环境: $(if ($Manifest.scoring_env.ready_for_scoring) { 'ready' } else { 'not_ready' })",
        "- 真相源冲突: $(if ($Manifest.truth_source.has_conflicts) { 'yes' } else { 'no' })",
        "- 可直接开跑: $(if ($Manifest.ready_for_smoke) { 'yes' } else { 'no' })",
        ""
    )

    if ($Manifest.truth_source.has_conflicts) {
        $lines += "## 当前冲突"
        $lines += ""
        foreach ($issue in $Manifest.truth_source.issues) {
            $lines += "- $issue"
        }
        $lines += ""
    }

    if ($Manifest.smoke -ne $null) {
        $lines += "## Smoke"
        $lines += ""
        $lines += "- 已执行: yes"
        $lines += "- exit_code: $($Manifest.smoke.exit_code)"
        $lines += "- output_root: $($Manifest.smoke.output_root)"
        if ($Manifest.smoke.error) {
            $lines += "- error: $($Manifest.smoke.error)"
        }
        $lines += ""
    }

    Set-Content -LiteralPath $Path -Value $lines -Encoding UTF8
}

$repoEnvPath = Get-RepoEnvPath
Load-RepoEnv -EnvPath $repoEnvPath

$catalog = Resolve-CaseCatalog -ConfigPath $CasesConfig
$caseConfig = Resolve-CaseConfig -Catalog $catalog -TargetCaseId $CaseId
$preflightDir = New-PreflightRunDir -Root $PreflightRoot -TargetId $CaseId
$healthUrl = "$($BaseUrl.TrimEnd('/'))/health"

$health = Test-Health -HealthUrl $healthUrl
$caseShape = Get-CaseShapeReport -CaseConfig $caseConfig
$scoringEnv = Get-ScoringEnvReport -OverrideApiKey $ScoringApiKey
$entryContract = Get-EntryContractReport
$truthSource = Get-TruthSourceConflictReport

$readyForSmoke = $health.ok -and
    $caseShape.allowed_for_smoke -and
    $scoringEnv.ready_for_scoring -and
    -not $truthSource.has_conflicts

$manifest = [ordered]@{
    generated_at = (Get-Date).ToString("s")
    case_id = $CaseId
    case_name = [string]$caseConfig.name
    preflight_dir = $preflightDir
    health = $health
    case_shape = $caseShape
    scoring_env = $scoringEnv
    entry_contract = $entryContract
    truth_source = $truthSource
    ready_for_smoke = $readyForSmoke
    smoke = $null
}

Write-JsonFile -Data $caseShape -Path (Join-Path $preflightDir "case_shape_report.json")
Write-JsonFile -Data $scoringEnv -Path (Join-Path $preflightDir "scoring_env_report.json")
Write-JsonFile -Data $entryContract -Path (Join-Path $preflightDir "precheck_entry_contract.json")
Write-JsonFile -Data $truthSource -Path (Join-Path $preflightDir "truth_source_report.json")

if ($RunSmoke) {
    $smoke = [ordered]@{
        attempted = $true
        entry = Get-RunBenchmarkPath
        output_root = $SmokeOutputRoot
        exit_code = $null
        error = $null
    }

    try {
        & (Get-RunBenchmarkPath) -CaseId $CaseId -BaseUrl $BaseUrl -OutputRoot $SmokeOutputRoot @(
            if (-not [string]::IsNullOrWhiteSpace($ScoringApiKey)) { @("-ScoringApiKey", $ScoringApiKey) } else { @() }
        )
        $smoke.exit_code = $LASTEXITCODE
    }
    catch {
        $smoke.exit_code = if ($LASTEXITCODE) { $LASTEXITCODE } else { 1 }
        $smoke.error = $_.Exception.Message
    }

    $manifest.smoke = $smoke
}

Write-JsonFile -Data $manifest -Path (Join-Path $preflightDir "precheck_manifest.json")
Write-SummaryMarkdown -Manifest $manifest -Path (Join-Path $preflightDir "precheck_summary.md")

$manifestPath = Join-Path $preflightDir "precheck_manifest.json"
$summaryPath = Join-Path $preflightDir "precheck_summary.md"

Write-Host "[INFO] IIIA 预检目录: $preflightDir"
Write-Host "[INFO] 预检清单: $manifestPath"
Write-Host "[INFO] 预检摘要: $summaryPath"
Write-Host "[INFO] ready_for_smoke=$readyForSmoke"
