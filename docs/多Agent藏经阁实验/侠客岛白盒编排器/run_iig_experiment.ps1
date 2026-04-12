param(
    [ValidateSet("iig1_a", "iig1_b", "iig1_c", "iig4", "all")]
    [string]$Arm = "all",
    [string]$CandidateId = "",
    [string]$ApiKey = "",
    [string]$OutputRoot = "D:\汇度编辑部1\侠客岛-runtime\ii_whitebox",
    [string]$L1AssetsPath = "D:\汇度编辑部1\藏经阁\l1\writing_craft"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = $PSScriptRoot
$poolPath = Join-Path $scriptRoot "config\ii_candidate_pool.json"
$orchestratorPath = Join-Path $scriptRoot "run_ii_whitebox_orchestrator.ps1"
$materialsPath = Join-Path $scriptRoot "run_ii_whitebox_materials.ps1"
$draftPath = Join-Path $scriptRoot "run_ii_whitebox_draft.ps1"
$scorePath = Join-Path $scriptRoot "run_ii_whitebox_score.ps1"
$revisePath = Join-Path $scriptRoot "run_ii_whitebox_revise.ps1"

# Load .env if no ApiKey provided
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    $envPath = "D:\汇度编辑部1\侠客岛\.env"
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]+?)=(.*)$') {
                [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
            }
        }
        $ApiKey = $env:OPENAI_API_KEY
    }
}

function Read-JsonFile {
    param([string]$Path)
    $content = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    return $content | ConvertFrom-Json
}

function Write-JsonFile {
    param([string]$Path, [object]$Payload)
    $Payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
}

$pool = Read-JsonFile -Path $poolPath
$allCandidateIds = @($pool.candidates | ForEach-Object { $_.id })

if (-not [string]::IsNullOrWhiteSpace($CandidateId)) {
    $allCandidateIds = @($CandidateId)
}

# ── Arm 配置 ──
$armConfigs = @{
    "iig1_a" = @{
        suffix = "iig1_a"
        enableFormula = $false
        enableReferenceSample = $true
        maxRounds = 6
        enableL1 = $false
    }
    "iig1_b" = @{
        suffix = "iig1_b"
        enableFormula = $true
        enableReferenceSample = $true
        maxRounds = 6
        enableL1 = $false
    }
    "iig1_c" = @{
        suffix = "iig1_c"
        enableFormula = $true
        enableReferenceSample = $true
        maxRounds = 6
        enableL1 = $true
    }
    "iig4" = @{
        suffix = "iig4"
        enableFormula = $true
        enableReferenceSample = $true
        maxRounds = 10
        enableL1 = $true
    }
}

$armsToRun = if ($Arm -eq "all") { @("iig1_a", "iig1_b", "iig1_c", "iig4") } else { @($Arm) }
$experimentResults = @()
$experimentTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"

foreach ($armName in $armsToRun) {
    $config = $armConfigs[$armName]
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  ARM: $armName ($($allCandidateIds.Count) candidates)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    foreach ($candidateId in $allCandidateIds) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
        $runDirName = "${timestamp}_${candidateId}_$($config.suffix)"
        $runDir = Join-Path $OutputRoot $runDirName

        Write-Host "`n--- $candidateId | $armName ---" -ForegroundColor Yellow

        $runResult = [ordered]@{
            arm = $armName
            candidate_id = $candidateId
            run_directory = $runDir
            timestamp = $timestamp
            status = "pending"
            steps = @()
        }

        try {
            # Step 1: Orchestrator (build contract)
            Write-Host "[1/5] 构建合同..."
            $orchArgs = @{
                CandidateId = $candidateId
                CandidatePool = $poolPath
                OutputRoot = $OutputRoot
            }
            if ($config.enableReferenceSample) { $orchArgs.EnableReferenceSample = $true }
            if ($config.enableL1) {
                $orchArgs.EnableL1WritingCraft = $true
                $orchArgs.L1AssetsPath = $L1AssetsPath
            }

            & $orchestratorPath @orchArgs
            $orchExit = $LASTEXITCODE

            # Find the run directory just created by orchestrator
            $latestDir = Get-ChildItem $OutputRoot -Directory | Where-Object { $_.Name -like "*_${candidateId}" -and $_.Name -notlike "*_iig*" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if (-not $latestDir) {
                throw "Orchestrator 未创建运行目录"
            }

            # Rename to include arm suffix
            $finalRunDir = Join-Path $OutputRoot $runDirName
            if ($latestDir.FullName -ne $finalRunDir) {
                Rename-Item $latestDir.FullName $runDirName
            }
            $runDir = $finalRunDir
            $runResult.run_directory = $runDir

            if ($orchExit -ne 0) {
                throw "Orchestrator 退出码 $orchExit"
            }
            $runResult.steps += "orchestrator:ok"

            # For A arm: remove formula_contract from contract (no formula)
            if (-not $config.enableFormula) {
                $contractPath = Join-Path $runDir "whitebox_contract.json"
                $contract = Read-JsonFile -Path $contractPath
                $contract.formula_contract = $null
                Write-JsonFile -Path $contractPath -Payload $contract
                Write-Host "  A臂：已移除 formula_contract"
            }

            # Step 2: Materials
            Write-Host "[2/5] 取材..."
            & $materialsPath -CandidateId $candidateId -CandidatePool $poolPath -RunDirectory $runDir
            $matExit = $LASTEXITCODE
            if ($matExit -ne 0) { throw "Materials 退出码 $matExit" }
            $runResult.steps += "materials:ok"

            # Step 3: Draft
            Write-Host "[3/5] 出稿..."
            & $draftPath -CandidateId $candidateId -CandidatePool $poolPath -RunDirectory $runDir -ApiKey $ApiKey
            $draftExit = $LASTEXITCODE
            if ($draftExit -ne 0 -and $draftExit -ne 4) { throw "Draft 退出码 $draftExit" }
            if ($draftExit -eq 4) {
                Write-Host "  [WARN] Draft 需要 agent 继续，跳过后续步骤" -ForegroundColor DarkYellow
                $runResult.status = "agent_continue_required"
                $runResult.steps += "draft:agent_continue"
                $experimentResults += [pscustomobject]$runResult
                continue
            }
            $runResult.steps += "draft:ok"

            # Step 4: Score
            Write-Host "[4/5] 评分..."
            & $scorePath -CandidateId $candidateId -CandidatePool $poolPath -RunDirectory $runDir -ApiKey $ApiKey
            $scoreExit = $LASTEXITCODE
            if ($scoreExit -ne 0 -and $scoreExit -ne 4) { throw "Score 退出码 $scoreExit" }
            if ($scoreExit -eq 4) {
                $runResult.status = "agent_continue_required"
                $runResult.steps += "score:agent_continue"
                $experimentResults += [pscustomobject]$runResult
                continue
            }
            $runResult.steps += "score:ok"

            # Step 5: Revise
            Write-Host "[5/5] 修稿 (MaxRounds=$($config.maxRounds))..."
            $reviseArgs = @{
                CandidateId = $candidateId
                CandidatePool = $poolPath
                RunDirectory = $runDir
                ApiKey = $ApiKey
                MaxRounds = $config.maxRounds
            }
            if ($config.enableL1) {
                $reviseArgs.EnableL1WritingCraft = $true
                $reviseArgs.L1AssetsPath = $L1AssetsPath
            }

            & $revisePath @reviseArgs
            $reviseExit = $LASTEXITCODE
            $runResult.steps += "revise:exit_$reviseExit"

            # Read final score
            $finalScorePath = Join-Path $runDir "score.json"
            if (Test-Path $finalScorePath) {
                $finalScore = Read-JsonFile -Path $finalScorePath
                $runResult.final_score = $finalScore.weighted_total
                $runResult.qualified = $finalScore.qualified
                Write-Host "  最终分数: $($finalScore.weighted_total) | 合格: $($finalScore.qualified)" -ForegroundColor Green
            }

            $runResult.status = "completed"
        }
        catch {
            $runResult.status = "failed"
            $runResult.error = $_.Exception.Message
            Write-Host "  [ERROR] $($_.Exception.Message)" -ForegroundColor Red
        }

        $experimentResults += [pscustomobject]$runResult
    }
}

# ── 写入实验结果汇总 ──
$resultSummaryPath = Join-Path $OutputRoot "iig_experiment_${experimentTimestamp}.json"
$resultSummary = [pscustomobject][ordered]@{
    experiment = "IIG"
    timestamp = $experimentTimestamp
    arms_run = $armsToRun
    candidates = $allCandidateIds
    total_runs = $experimentResults.Count
    completed = @($experimentResults | Where-Object { $_.status -eq "completed" }).Count
    failed = @($experimentResults | Where-Object { $_.status -eq "failed" }).Count
    results = $experimentResults
}
Write-JsonFile -Path $resultSummaryPath -Payload $resultSummary

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  IIG 实验完成" -ForegroundColor Cyan
Write-Host "  总计: $($experimentResults.Count) runs" -ForegroundColor Cyan
Write-Host "  完成: $(@($experimentResults | Where-Object { $_.status -eq 'completed' }).Count)" -ForegroundColor Cyan
Write-Host "  失败: $(@($experimentResults | Where-Object { $_.status -eq 'failed' }).Count)" -ForegroundColor Cyan
Write-Host "  结果: $resultSummaryPath" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
