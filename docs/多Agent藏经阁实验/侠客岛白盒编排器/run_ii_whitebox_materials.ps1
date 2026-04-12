param(
    [string]$CandidateId,
    [string]$CandidatePool = "",
    [string]$RunDirectory = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "whitebox_common.ps1")

if ([string]::IsNullOrWhiteSpace($RunDirectory)) {
    throw "必须提供 -RunDirectory。"
}

$poolData = Get-CandidatePoolData -Path $CandidatePool
$candidate = Resolve-Candidate -PoolData $poolData -CandidateId $CandidateId

$materialsDir = Join-Path $RunDirectory "materials"
New-Item -ItemType Directory -Path $materialsDir -Force | Out-Null

$manifestPath = Join-Path $materialsDir "materials_manifest.json"
$digestPath = Join-Path $materialsDir "materials_digest.md"
$compiledPath = Join-Path $materialsDir "materials_compiled.txt"

$items = @()
$compiledChunks = @()
$extractableCount = 0

foreach ($rule in @($candidate.input_rules)) {
    $resolved = Resolve-InputPath -SourceRoot $candidate.source_root -RelativeOrAbsolutePath $rule.path
    if (-not (Test-Path -LiteralPath $resolved)) {
        $items += [pscustomobject][ordered]@{
            source_rule = $rule.path
            resolved_path = $resolved
            type = "missing"
            extract_status = "missing"
            preview = ""
        }
        continue
    }

    $files = @()
    if ((Get-Item -LiteralPath $resolved) -is [System.IO.DirectoryInfo]) {
        if ($rule.mode -eq "allow_all_except_docx") {
            $files = @(Get-ChildItem -LiteralPath $resolved -Recurse -File | Where-Object { $_.Extension -notin @(".docx", ".DOCX") })
        }
    }
    elseif ($rule.mode -eq "allow_file") {
        $files = @((Get-Item -LiteralPath $resolved))
    }

    foreach ($file in $files) {
        $extract = Extract-FileText -Path $file.FullName
        $preview = ""
        if (-not [string]::IsNullOrWhiteSpace($extract.text)) {
            $preview = $extract.text.Substring(0, [Math]::Min(3000, $extract.text.Length))
            $compiledChunks += "### $($file.Name)`n$preview"
            $extractableCount += 1
        }
        $items += [pscustomobject][ordered]@{
            source_rule = $rule.path
            resolved_path = $file.FullName
            extension = $file.Extension
            size = $file.Length
            extract_status = $extract.status
            preview = $preview
        }
    }
}

$status = if (@($items).Count -eq 0) { "failed" } elseif ($extractableCount -gt 0) { "ready" } else { "partial" }
$exitCode = if ($status -eq "failed") { 1 } else { 0 }

Set-Content -LiteralPath $compiledPath -Value ($compiledChunks -join "`n`n") -Encoding UTF8

# 读取公式位产出 coverage 审计
$coverageAudit = $null
$contractPath = Join-Path $RunDirectory "whitebox_contract.json"
if (Test-Path -LiteralPath $contractPath) {
    $contractData = Read-JsonFile -Path $contractPath
    $fc = $null
    if ($contractData.PSObject.Properties.Name -contains "formula_contract" -and $null -ne $contractData.formula_contract) {
        $fc = $contractData.formula_contract
    }
    if ($fc) {
        $ecu = @()
        if ($fc.PSObject.Properties.Name -contains "effective_content_unit") { $ecu = @($fc.effective_content_unit) }
        $mcu = @()
        if ($fc.PSObject.Properties.Name -contains "min_content_unit") { $mcu = @($fc.min_content_unit) }
        $coverageAudit = [ordered]@{
            effective_content_unit_expected = $ecu
            min_content_unit_expected = $mcu
            extractable_count = $extractableCount
            compiled_text_length = if ($compiledChunks.Count -gt 0) { ($compiledChunks -join "`n`n").Length } else { 0 }
            audit_note = "content unit coverage 须在 draft 和 score 阶段由 LLM 逐条校验"
        }
    }
}

$manifest = [pscustomobject][ordered]@{
    candidate_id = $candidate.id
    candidate_name = $candidate.name
    status = $status
    exit_code = $exitCode
    run_directory = $materialsDir
    extractable_count = $extractableCount
    total_items = @($items).Count
    compiled_text = $compiledPath
    coverage_audit = $coverageAudit
    items = $items
}
Write-JsonFile -Path $manifestPath -Payload $manifest

$lines = @(
    "# 白盒取材摘要",
    "",
    "- 题目: $($candidate.id) / $($candidate.name)",
    "- 状态: $status",
    "- 总材料项: $(@($items).Count)",
    "- 可抽取文本项: $extractableCount",
    ""
)
foreach ($item in $items) {
    $lines += "- [$($item.extract_status)] $($item.resolved_path)"
}
Set-Content -LiteralPath $digestPath -Value $lines -Encoding UTF8

Write-Host "[INFO] 取材摘要: $digestPath"
Write-Host "[INFO] 取材清单: $manifestPath"
exit $exitCode
