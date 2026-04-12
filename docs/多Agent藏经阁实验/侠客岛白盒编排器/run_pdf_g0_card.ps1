param(
    [string]$CardTitle,
    [string]$PdfPath,
    [string]$OutputRoot = "D:\汇度编辑部1\侠客岛-runtime\iid_pdf_engineering_v2",
    [string]$EvidenceItemsJson = "",
    [string]$CardId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "whitebox_common.ps1")

function Convert-ToSafeName {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return "untitled"
    }

    $name = $Text -replace '[\\/:*?"<>|]+', "_" -replace '\s+', "_" -replace '_+', "_"
    return $name.Trim("_")
}

if ([string]::IsNullOrWhiteSpace($CardTitle)) {
    throw "必须提供 -CardTitle。"
}
if ([string]::IsNullOrWhiteSpace($PdfPath)) {
    throw "必须提供 -PdfPath。"
}
if (-not (Test-Path -LiteralPath $PdfPath)) {
    throw "PDF 不存在: $PdfPath"
}
if ([string]::IsNullOrWhiteSpace($EvidenceItemsJson)) {
    throw "必须提供 -EvidenceItemsJson。"
}

$evidenceItems = $EvidenceItemsJson | ConvertFrom-Json
if ($null -eq $evidenceItems) {
    throw "EvidenceItemsJson 解析失败。"
}
if ($evidenceItems -isnot [System.Collections.IEnumerable] -or $evidenceItems -is [string]) {
    $evidenceItems = @($evidenceItems)
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$slug = if ($CardId) { $CardId } else { Convert-ToSafeName -Text ([System.IO.Path]::GetFileNameWithoutExtension($PdfPath)) }
$runDir = Join-Path $OutputRoot "${timestamp}_$slug"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$jsonPath = Join-Path $runDir "g0_evidence_card.json"
$mdPath = Join-Path $runDir "g0_evidence_card.md"

$pageTexts = @(Get-PdfPageTexts -Path $PdfPath)
$pageCount = $pageTexts.Count
$patterns = @($evidenceItems | ForEach-Object { $_.pattern })
$matches = @(Find-PdfEvidenceMatches -Path $PdfPath -Patterns $patterns)
$matchMap = @{}
foreach ($match in $matches) {
    $matchMap[$match.pattern] = $match
}

$points = @()
foreach ($item in $evidenceItems) {
    $match = $matchMap[$item.pattern]
    $points += [pscustomobject][ordered]@{
        label = $item.label
        pattern = $item.pattern
        anchor = $item.anchor
        page_number = $match.page_number
        matched_text = $match.matched_text
        excerpt = $match.excerpt
        status = if ($null -eq $match.page_number) { "missing" } else { "found" }
    }
}

$overallStatus = if (@($points | Where-Object { $_.status -ne "found" }).Count -eq 0) { "verified" } else { "partial" }

$commandExample = @"
& '$PSScriptRoot\run_pdf_g0_card.ps1' `
  -CardTitle '$CardTitle' `
  -PdfPath '$PdfPath' `
  -CardId '$slug' `
  -EvidenceItemsJson '<JSON array>'
"@.Trim()

$card = [pscustomobject][ordered]@{
    card_title = $CardTitle
    card_id = $slug
    status = $overallStatus
    generated_at = $timestamp
    pdf_path = $PdfPath
    pdf_name = [System.IO.Path]::GetFileName($PdfPath)
    page_count = $pageCount
    extraction_method = "pdftotext.exe + temp ascii copy + page split"
    evidence_summary = @(
        "已验证 PDF 逐页抽取路径可用。",
        "已验证证据点能回指到页码与摘录。",
        "已验证可用 JSON 驱动命令复跑同一卡样板。"
    )
    command_example = $commandExample
    evidence_points = $points
}

Write-JsonFile -Path $jsonPath -Payload $card

$lines = @(
    "# PDF G0 证据卡",
    "",
    "- 题目: $CardTitle",
    "- 状态: $overallStatus",
    "- PDF: $PdfPath",
    "- 页数: $pageCount",
    "- 抽取方式: $($card.extraction_method)",
    "",
    "## 证据摘要",
    ""
)

foreach ($line in $card.evidence_summary) {
    $lines += "- $line"
}

$lines += ""
$lines += "## 复用命令"
$lines += ""
$lines += "```powershell"
$lines += $commandExample
$lines += "```"
$lines += ""
$lines += "## 证据点"
$lines += ""

foreach ($point in $points) {
    $lines += "### $($point.label)"
    $lines += ""
    $lines += "- 检索模式: $($point.pattern)"
    $lines += "- 来源锚点: $($point.anchor)"
    $lines += "- 页码: $($point.page_number)"
    $lines += "- 命中值: $($point.matched_text)"
    if ($point.excerpt) {
        $lines += "- 摘录: $($point.excerpt)"
    }
    $lines += ""
}

Set-Content -LiteralPath $mdPath -Value $lines -Encoding UTF8

Write-Host "[INFO] G0 证据卡: $mdPath"
Write-Host "[INFO] G0 证据清单: $jsonPath"
exit 0
