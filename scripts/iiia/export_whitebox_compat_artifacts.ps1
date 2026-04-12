param(
    [Parameter(Mandatory = $true)]
    [string]$RunDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Payload
    )

    $Payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Write-TextFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Get-ContractRunDirectories {
    param([Parameter(Mandatory = $true)][string]$Root)

    $phaseManifestPath = Join-Path $Root "phase_manifest.json"
    $whiteboxManifestPath = Join-Path $Root "whitebox_manifest.json"

    if (Test-Path -LiteralPath $phaseManifestPath) {
        $phase = Read-JsonFile -Path $phaseManifestPath
        return @($phase.steps | ForEach-Object { $_.run_directory } | Where-Object { $_ -and (Test-Path -LiteralPath $_) })
    }

    if (Test-Path -LiteralPath $whiteboxManifestPath) {
        return @($Root)
    }

    throw "既不是白盒 phase 目录，也不是单题 contract 目录: $Root"
}

function Export-CompatArtifactsForContract {
    param([Parameter(Mandatory = $true)][string]$ContractDir)

    $whiteboxManifestPath = Join-Path $ContractDir "whitebox_manifest.json"
    if (-not (Test-Path -LiteralPath $whiteboxManifestPath)) {
        throw "缺少 whitebox_manifest.json: $ContractDir"
    }

    $whiteboxManifest = Read-JsonFile -Path $whiteboxManifestPath
    $contractPath = [string]$whiteboxManifest.contract
    $contract = Read-JsonFile -Path $contractPath

    $materialsManifestPath = Join-Path $ContractDir "materials\materials_manifest.json"
    $draftManifestPath = Join-Path $ContractDir "draft_manifest.json"
    $scoreManifestPath = Join-Path $ContractDir "score_manifest.json"
    $scorePath = Join-Path $ContractDir "score.json"

    $materialsManifest = if (Test-Path -LiteralPath $materialsManifestPath) { Read-JsonFile -Path $materialsManifestPath } else { $null }
    $draftManifest = if (Test-Path -LiteralPath $draftManifestPath) { Read-JsonFile -Path $draftManifestPath } else { $null }
    $scoreManifest = if (Test-Path -LiteralPath $scoreManifestPath) { Read-JsonFile -Path $scoreManifestPath } else { $null }
    $score = if (Test-Path -LiteralPath $scorePath) { Read-JsonFile -Path $scorePath } else { $null }

    $generatedPath = Join-Path $ContractDir "generated.txt"
    $writingUserPromptPath = Join-Path $ContractDir "writing_user_prompt.txt"
    $writingSystemPromptPath = Join-Path $ContractDir "writing_system_prompt.txt"
    $materialsFullPath = Join-Path $ContractDir "materials_full.json"
    $reviewBundlePath = Join-Path $ContractDir "review_bundle.json"
    $summaryPath = Join-Path $ContractDir "summary.json"
    $taskDetailPath = Join-Path $ContractDir "task_detail.json"
    $compatManifestPath = Join-Path $ContractDir "compat_manifest.json"

    if ($draftManifest -and $draftManifest.draft_path -and (Test-Path -LiteralPath $draftManifest.draft_path)) {
        Copy-Item -LiteralPath $draftManifest.draft_path -Destination $generatedPath -Force
    }

    if ($draftManifest -and $draftManifest.draft_prompt_path -and (Test-Path -LiteralPath $draftManifest.draft_prompt_path)) {
        $promptText = Get-Content -LiteralPath $draftManifest.draft_prompt_path -Raw -Encoding UTF8
        Write-TextFile -Path $writingUserPromptPath -Content $promptText
    }

    $systemPrompt = @(
        "whitebox_compat_mode = single_prompt_drafting",
        "说明：本次白盒出稿采用单提示词模式，系统级约束已经内嵌进 writing_user_prompt.txt 与 whitebox_contract.json。",
        "如需追溯更上游状态，请看 state_cards/*.json 与 whitebox_contract.json。"
    ) -join "`r`n"
    Write-TextFile -Path $writingSystemPromptPath -Content $systemPrompt

    if ($materialsManifest) {
        $compiledText = if ($materialsManifest.compiled_text -and (Test-Path -LiteralPath $materialsManifest.compiled_text)) {
            Get-Content -LiteralPath $materialsManifest.compiled_text -Raw -Encoding UTF8
        }
        else {
            ""
        }

        $materialsFull = [pscustomobject][ordered]@{
            mode = "whitebox_materials_export"
            candidate_id = $materialsManifest.candidate_id
            candidate_name = $materialsManifest.candidate_name
            status = $materialsManifest.status
            extractable_count = $materialsManifest.extractable_count
            total_items = $materialsManifest.total_items
            compiled_text_path = $materialsManifest.compiled_text
            compiled_text = $compiledText
            coverage_audit = $materialsManifest.coverage_audit
            items = $materialsManifest.items
        }
        Write-JsonFile -Path $materialsFullPath -Payload $materialsFull
    }

    if ($score) {
        $reviewBundle = [pscustomobject][ordered]@{
            mode = "whitebox_review_bundle"
            candidate_id = $contract.candidate_id
            candidate_name = $contract.candidate_name
            weighted_total = $score.weighted_total
            qualified = $score.qualified
            blocking_issues = $score.blocking_issues
            missing_or_misaligned = $score.missing_or_misaligned
            backtrace = $score.backtrace
            next_actions = $score.next_actions
            formula_compliance = $score.formula_compliance
            formula_compliance_summary = $score.formula_compliance_summary
            dimensions = $score.dimensions
            writing_strength = $score.writing_strength
        }
        Write-JsonFile -Path $reviewBundlePath -Payload $reviewBundle
    }

    $summary = [pscustomobject][ordered]@{
        mode = "whitebox_summary_export"
        candidate_id = $contract.candidate_id
        candidate_name = $contract.candidate_name
        task_status = if ($scoreManifest) { $scoreManifest.status } elseif ($draftManifest) { $draftManifest.status } else { $whiteboxManifest.status }
        qualified = if ($score) { $score.qualified } else { $false }
        weighted_total = if ($score) { $score.weighted_total } else { $null }
        generated_path = if (Test-Path -LiteralPath $generatedPath) { $generatedPath } else { $null }
        materials_full_path = if (Test-Path -LiteralPath $materialsFullPath) { $materialsFullPath } else { $null }
        writing_system_prompt_path = $writingSystemPromptPath
        writing_user_prompt_path = if (Test-Path -LiteralPath $writingUserPromptPath) { $writingUserPromptPath } else { $null }
        review_bundle_ready = Test-Path -LiteralPath $reviewBundlePath
        review_bundle_path = if (Test-Path -LiteralPath $reviewBundlePath) { $reviewBundlePath } else { $null }
        score_path = if (Test-Path -LiteralPath $scorePath) { $scorePath } else { $null }
    }
    Write-JsonFile -Path $summaryPath -Payload $summary

    $taskDetail = [pscustomobject][ordered]@{
        mode = "whitebox_task_detail_export"
        candidate_id = $contract.candidate_id
        candidate_name = $contract.candidate_name
        case_type = $contract.case_type
        source_root = $contract.source_root
        status = $summary.task_status
        stages = [pscustomobject][ordered]@{
            contract_ready = [bool](Test-Path -LiteralPath $contractPath)
            materials_ready = [bool](Test-Path -LiteralPath $materialsFullPath)
            draft_ready = [bool](Test-Path -LiteralPath $generatedPath)
            scoring_ready = [bool](Test-Path -LiteralPath $scorePath)
            review_bundle_ready = [bool](Test-Path -LiteralPath $reviewBundlePath)
        }
        outputs = [pscustomobject][ordered]@{
            whitebox_contract = $contractPath
            whitebox_manifest = $whiteboxManifestPath
            materials_full = if (Test-Path -LiteralPath $materialsFullPath) { $materialsFullPath } else { $null }
            generated = if (Test-Path -LiteralPath $generatedPath) { $generatedPath } else { $null }
            writing_system_prompt = $writingSystemPromptPath
            writing_user_prompt = if (Test-Path -LiteralPath $writingUserPromptPath) { $writingUserPromptPath } else { $null }
            review_bundle = if (Test-Path -LiteralPath $reviewBundlePath) { $reviewBundlePath } else { $null }
            score = if (Test-Path -LiteralPath $scorePath) { $scorePath } else { $null }
            summary = $summaryPath
        }
    }
    Write-JsonFile -Path $taskDetailPath -Payload $taskDetail

    $compatManifest = [pscustomobject][ordered]@{
        contract_run_directory = $ContractDir
        generated = if (Test-Path -LiteralPath $generatedPath) { $generatedPath } else { $null }
        writing_system_prompt = $writingSystemPromptPath
        writing_user_prompt = if (Test-Path -LiteralPath $writingUserPromptPath) { $writingUserPromptPath } else { $null }
        materials_full = if (Test-Path -LiteralPath $materialsFullPath) { $materialsFullPath } else { $null }
        review_bundle = if (Test-Path -LiteralPath $reviewBundlePath) { $reviewBundlePath } else { $null }
        summary = $summaryPath
        task_detail = $taskDetailPath
    }
    Write-JsonFile -Path $compatManifestPath -Payload $compatManifest

    return $compatManifest
}

$contractDirs = @(Get-ContractRunDirectories -Root $RunDirectory)
$exports = @()
foreach ($contractDir in $contractDirs) {
    $exports += Export-CompatArtifactsForContract -ContractDir $contractDir
}

$rootCompatPath = Join-Path $RunDirectory "compat_exports.json"
Write-JsonFile -Path $rootCompatPath -Payload $exports
Write-Host "[INFO] compat exports: $rootCompatPath"
