param(
    [string]$CandidatePool = "",
    [string[]]$Candidates = @("lecanemab_patient", "lecanemab_news"),
    [string]$OutputRoot = "D:\汇度编辑部1\侠客岛-runtime\iiia_model_compare_persona_v1",
    [string]$DeepSeekApiKey = "",
    [string]$DeepSeekBaseUrl = "https://api.deepseek.com/v1",
    [string]$DeepSeekModel = "deepseek-reasoner",
    [int]$WholeReviseMaxRounds = 3,
    [int]$WholeReviseTargetScore = 85,
    [int]$WholeReviseMaxStaleRounds = 2,
    [int]$LocalReviseMaxRounds = 1,
    [int]$LocalReviseTargetScore = 85,
    [int]$LocalReviseMaxStaleRounds = 1,
    [int]$LocalReviseMaxTasksPerRound = 4
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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
    $Payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
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
        if ($candidateScoped.Count -gt 0) {
            return @($candidateScoped | Sort-Object CreationTimeUtc -Descending)[0]
        }
        return @($newDirectories | Sort-Object CreationTimeUtc -Descending)[0]
    }

    return $null
}

function Set-EnvValueSafe {
    param(
        [string]$Name,
        [AllowNull()][string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Name)) {
        return
    }

    if ($null -eq $Value -or $Value -eq "") {
        Remove-Item -LiteralPath ("Env:{0}" -f $Name) -ErrorAction SilentlyContinue
    }
    else {
        Set-Item -LiteralPath ("Env:{0}" -f $Name) -Value $Value
    }
}

function Invoke-WithEnvOverrides {
    param(
        [hashtable]$Overrides,
        [scriptblock]$Action
    )

    $previousValues = @{}
    foreach ($key in $Overrides.Keys) {
        $envItem = Get-Item -LiteralPath ("Env:{0}" -f $key) -ErrorAction SilentlyContinue
        $previousValues[$key] = if ($null -ne $envItem) { [string]$envItem.Value } else { $null }
        Set-EnvValueSafe -Name $key -Value ([string]$Overrides[$key])
    }

    try {
        & $Action
    }
    finally {
        foreach ($key in $Overrides.Keys) {
            Set-EnvValueSafe -Name $key -Value $previousValues[$key]
        }
    }
}

function Copy-CompareSnapshot {
    param(
        [string]$RunDirectory,
        [string]$StageName
    )

    $snapshotDir = Join-Path (Join-Path $RunDirectory "compare_snapshots") $StageName
    New-Item -ItemType Directory -Path $snapshotDir -Force | Out-Null

    $copyTargets = @(
        "draft.txt",
        "draft_manifest.json",
        "draft_prompt.md",
        "score.json",
        "score_manifest.json",
        "score_summary.md",
        "score_prompt.md",
        "revise_manifest.json",
        "revise_summary.md",
        "local_revise_manifest.json"
    )

    foreach ($name in $copyTargets) {
        $source = Join-Path $RunDirectory $name
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination (Join-Path $snapshotDir $name) -Force
        }
    }

    return $snapshotDir
}

function Get-StageSummary {
    param(
        [string]$RunDirectory,
        [string]$StageName
    )

    $snapshotDir = Join-Path (Join-Path $RunDirectory "compare_snapshots") $StageName
    $scorePath = Join-Path $snapshotDir "score.json"
    $manifestPath = Join-Path $snapshotDir "score_manifest.json"
    $draftPath = Join-Path $snapshotDir "draft.txt"

    $score = if (Test-Path -LiteralPath $scorePath) { Read-JsonFile -Path $scorePath } else { $null }
    $manifest = if (Test-Path -LiteralPath $manifestPath) { Read-JsonFile -Path $manifestPath } else { $null }

    return [pscustomobject][ordered]@{
        stage = $StageName
        snapshot_directory = $snapshotDir
        draft_path = if (Test-Path -LiteralPath $draftPath) { $draftPath } else { $null }
        score_path = if ($score) { $scorePath } else { $null }
        weighted_total = if ($score) { [int]$score.weighted_total } else { $null }
        qualified = if ($score) { [bool]$score.qualified } else { $null }
        editorial_total = if ($score -and $score.PSObject.Properties.Name -contains "editorial_total") { [int]$score.editorial_total } else { $null }
        blocking_count = if ($score) { @($score.blocking_issues).Count } else { $null }
        missing_count = if ($score) { @($score.missing_or_misaligned).Count } else { $null }
        score_origin = if ($manifest) { [string](Get-OptionalPropertyValue -Object $manifest -Name "score_origin" -Default "") } else { "" }
    }
}

if ([string]::IsNullOrWhiteSpace($CandidatePool)) {
    $CandidatePool = Join-Path $PSScriptRoot "iiia_whitebox_candidate_pool.json"
}
if (-not (Test-Path -LiteralPath $CandidatePool)) {
    throw "候选池不存在: $CandidatePool"
}

$whiteboxRoot = Join-Path $PSScriptRoot "..\..\docs\多Agent藏经阁实验\侠客岛白盒编排器"
$whiteboxRoot = (Resolve-Path -LiteralPath $whiteboxRoot).ProviderPath
$runnerPath = Join-Path $whiteboxRoot "run_ii_whitebox_orchestrator.ps1"
$materialsPath = Join-Path $whiteboxRoot "run_ii_whitebox_materials.ps1"
$draftPath = Join-Path $whiteboxRoot "run_ii_whitebox_draft.ps1"
$scorePath = Join-Path $whiteboxRoot "run_ii_whitebox_score.ps1"
$revisePath = Join-Path $whiteboxRoot "run_ii_whitebox_revise.ps1"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$runDir = Join-Path $OutputRoot "${timestamp}_k25_vs_deepseek"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$contractsRoot = Join-Path $runDir "contracts"
New-Item -ItemType Directory -Path $contractsRoot -Force | Out-Null

$modelConfigs = @(
    [pscustomobject]@{
        id = "k25_default"
        writer_env = @{}
        note = "默认 writer/revise profiles，review_score 固定留在当前默认 scorer。"
    }
)

if (-not [string]::IsNullOrWhiteSpace($DeepSeekApiKey)) {
    $modelConfigs += [pscustomobject]@{
        id = "deepseek_reasoner"
        writer_env = @{
            XIAGEDAO_WHITEBOX_DRAFT_BASE_URL = $DeepSeekBaseUrl
            XIAGEDAO_WHITEBOX_DRAFT_MODEL = $DeepSeekModel
            XIAGEDAO_WHITEBOX_DRAFT_PROTOCOL = "openai"
            XIAGEDAO_WHITEBOX_DRAFT_API_KEY = $DeepSeekApiKey
            XIAGEDAO_WHITEBOX_WHOLE_REVISE_BASE_URL = $DeepSeekBaseUrl
            XIAGEDAO_WHITEBOX_WHOLE_REVISE_MODEL = $DeepSeekModel
            XIAGEDAO_WHITEBOX_WHOLE_REVISE_PROTOCOL = "openai"
            XIAGEDAO_WHITEBOX_WHOLE_REVISE_API_KEY = $DeepSeekApiKey
            XIAGEDAO_WHITEBOX_LOCAL_TASK_ROUTER_BASE_URL = $DeepSeekBaseUrl
            XIAGEDAO_WHITEBOX_LOCAL_TASK_ROUTER_MODEL = $DeepSeekModel
            XIAGEDAO_WHITEBOX_LOCAL_TASK_ROUTER_PROTOCOL = "openai"
            XIAGEDAO_WHITEBOX_LOCAL_TASK_ROUTER_API_KEY = $DeepSeekApiKey
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_BASE_URL = $DeepSeekBaseUrl
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_MODEL = $DeepSeekModel
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_PROTOCOL = "openai"
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_API_KEY = $DeepSeekApiKey
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_AUDIT_BASE_URL = $DeepSeekBaseUrl
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_AUDIT_MODEL = $DeepSeekModel
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_AUDIT_PROTOCOL = "openai"
            XIAGEDAO_WHITEBOX_LOCAL_PATCH_AUDIT_API_KEY = $DeepSeekApiKey
        }
        note = "writer/revise/local profiles 切到 deepseek-reasoner，review_score 固定留在默认 scorer。"
    }
}

$results = @()

foreach ($modelConfig in $modelConfigs) {
    foreach ($candidateId in $Candidates) {
        $knownDirectories = @(
            if (Test-Path -LiteralPath $contractsRoot) {
                Get-ChildItem -LiteralPath $contractsRoot -Directory | ForEach-Object { $_.FullName }
            }
        )

        $entry = Invoke-WithEnvOverrides -Overrides $modelConfig.writer_env -Action {
            & $runnerPath -CandidateId $candidateId -CandidatePool $CandidatePool -OutputRoot $contractsRoot
            if ($LASTEXITCODE -ne 0) {
                throw "orchestrator_failed:${candidateId}:$($modelConfig.id):$LASTEXITCODE"
            }

            $latestRun = Resolve-NewChildRunDirectory -ContractsRoot $contractsRoot -KnownDirectories $knownDirectories -CandidateId $candidateId
            if (-not $latestRun) {
                throw "child_run_directory_not_found:${candidateId}:$($modelConfig.id)"
            }

            $latestRunDir = $latestRun.FullName

            $compareMeta = [pscustomobject][ordered]@{
                model_id = $modelConfig.id
                candidate_id = $candidateId
                note = $modelConfig.note
                writer_env_keys = @($modelConfig.writer_env.Keys | Sort-Object)
                run_directory = $latestRunDir
            }
            Write-JsonFile -Path (Join-Path $latestRunDir "model_compare_meta.json") -Payload $compareMeta

            & $materialsPath -CandidateId $candidateId -CandidatePool $CandidatePool -RunDirectory $latestRunDir
            if ($LASTEXITCODE -ne 0) {
                throw "materials_failed:${candidateId}:$($modelConfig.id):$LASTEXITCODE"
            }

            & $draftPath -CandidateId $candidateId -CandidatePool $CandidatePool -RunDirectory $latestRunDir
            if ($LASTEXITCODE -ne 0) {
                throw "draft_failed:${candidateId}:$($modelConfig.id):$LASTEXITCODE"
            }

            & $scorePath -CandidateId $candidateId -CandidatePool $CandidatePool -RunDirectory $latestRunDir
            if ($LASTEXITCODE -ne 0) {
                throw "score_failed:${candidateId}:$($modelConfig.id):$LASTEXITCODE"
            }
            Copy-CompareSnapshot -RunDirectory $latestRunDir -StageName "base" | Out-Null

            & $revisePath -CandidateId $candidateId -CandidatePool $CandidatePool -RunDirectory $latestRunDir -MaxRounds $WholeReviseMaxRounds -TargetScore $WholeReviseTargetScore -MaxStaleRounds $WholeReviseMaxStaleRounds -ReviseMode "whole"
            Copy-CompareSnapshot -RunDirectory $latestRunDir -StageName "whole" | Out-Null

            & $revisePath -CandidateId $candidateId -CandidatePool $CandidatePool -RunDirectory $latestRunDir -MaxRounds $LocalReviseMaxRounds -TargetScore $LocalReviseTargetScore -MaxStaleRounds $LocalReviseMaxStaleRounds -ReviseMode "local" -MaxLocalTasksPerRound $LocalReviseMaxTasksPerRound
            Copy-CompareSnapshot -RunDirectory $latestRunDir -StageName "whole_local" | Out-Null

            return [pscustomobject][ordered]@{
                model_id = $modelConfig.id
                candidate_id = $candidateId
                note = $modelConfig.note
                run_directory = $latestRunDir
                base = Get-StageSummary -RunDirectory $latestRunDir -StageName "base"
                whole = Get-StageSummary -RunDirectory $latestRunDir -StageName "whole"
                whole_local = Get-StageSummary -RunDirectory $latestRunDir -StageName "whole_local"
                whole_manifest_path = Join-Path $latestRunDir "revise_manifest.json"
                local_manifest_path = Join-Path $latestRunDir "local_revise_manifest.json"
            }
        }
        $results += $entry
    }
}

$sanitizedModels = @(
    foreach ($modelConfig in $modelConfigs) {
        [pscustomobject][ordered]@{
            id = $modelConfig.id
            note = $modelConfig.note
            writer_env_keys = @($modelConfig.writer_env.Keys | Sort-Object)
        }
    }
)

$summary = [pscustomobject][ordered]@{
    generated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    output_root = $runDir
    candidate_pool = $CandidatePool
    models = $sanitizedModels
    results = $results
}

$summaryJsonPath = Join-Path $runDir "model_compare_summary.json"
$summaryMdPath = Join-Path $runDir "model_compare_summary.md"
Write-JsonFile -Path $summaryJsonPath -Payload $summary

$lines = @(
    "# IIIA 模型对照摘要",
    "",
    "- 生成时间: $($summary.generated_at)",
    "- 输出目录: $runDir",
    "- 候选池: $CandidatePool",
    ""
)

foreach ($entry in $results) {
    $lines += "## $($entry.candidate_id) / $($entry.model_id)"
    $lines += ""
    $lines += "- 运行目录: $($entry.run_directory)"
    $lines += "- 备注: $($entry.note)"
    foreach ($stageName in @("base", "whole", "whole_local")) {
        $stage = $entry.$stageName
        $lines += "- ${stageName}: hard=$($stage.weighted_total) / qualified=$($stage.qualified) / editorial=$($stage.editorial_total)"
    }
    $lines += ""
}

Set-Content -LiteralPath $summaryMdPath -Value $lines -Encoding UTF8
Write-Host "[INFO] 模型对照摘要: $summaryMdPath"
Write-Host "[INFO] 模型对照清单: $summaryJsonPath"
