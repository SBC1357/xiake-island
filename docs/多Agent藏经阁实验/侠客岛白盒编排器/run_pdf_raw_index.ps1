param(
    [Parameter(Mandatory = $true)]
    [string]$TaskDirectory,
    [string]$OutputRoot = "D:\汇度编辑部1\侠客岛-runtime\iid_pdf_raw_index",
    [switch]$SyncToTaskDirectory
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

function Test-IsForbiddenSource {
    param([string]$Path)

    $normalized = $Path.ToLowerInvariant()
    return (
        $normalized -like "*\gold\*" -or
        $normalized -like "*\样稿\*" -or
        $normalized -like "*\sample\*" -or
        $normalized -like "*\参考样稿\*" -or
        $normalized -like "*\成稿\*" -or
        $normalized -like "*.docx"
    )
}

if (-not (Test-Path -LiteralPath $TaskDirectory)) {
    throw "任务目录不存在: $TaskDirectory"
}

$inputsDir = Join-Path $TaskDirectory "inputs"
$searchRoot = if (Test-Path -LiteralPath $inputsDir) { $inputsDir } else { $TaskDirectory }

$pdfFiles = @(
    Get-ChildItem -LiteralPath $searchRoot -Recurse -File -Filter *.pdf |
        Where-Object { -not (Test-IsForbiddenSource -Path $_.FullName) }
)

if ($pdfFiles.Count -eq 0) {
    throw "未找到可用原始 PDF。当前只允许读取原始 PDF，且禁止读取 gold/样稿/docx。搜索根目录: $searchRoot"
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$taskSlug = Convert-ToSafeName -Text (Split-Path -Leaf $TaskDirectory)
$runDir = Join-Path $OutputRoot "${timestamp}_$taskSlug"
$pagesRoot = Join-Path $runDir "raw_pages"
New-Item -ItemType Directory -Path $pagesRoot -Force | Out-Null

$pdfEntries = @()
foreach ($pdf in $pdfFiles) {
    $pdfSlug = Convert-ToSafeName -Text $pdf.BaseName
    $pageTextPath = Join-Path $pagesRoot "${pdfSlug}_pages.txt"
    $pages = @(Get-PdfPageTexts -Path $pdf.FullName)
    $lines = @()
    foreach ($page in $pages) {
        $lines += "===== PAGE $($page.page_number) ====="
        $lines += $page.text
        $lines += ""
    }
    Set-Content -LiteralPath $pageTextPath -Value $lines -Encoding UTF8

    $pdfEntries += [pscustomobject][ordered]@{
        pdf_name = $pdf.Name
        pdf_path = $pdf.FullName
        relative_to_task = [System.IO.Path]::GetRelativePath($TaskDirectory, $pdf.FullName)
        page_count = $pages.Count
        page_text_path = $pageTextPath
        extraction_method = "raw-only pdftotext page split"
        allowed_as_raw_input = $true
        can_replace_main_input = $false
    }
}

$manifest = [pscustomobject][ordered]@{
    task_directory = $TaskDirectory
    search_root = $searchRoot
    generated_at = $timestamp
    rule = "raw-only"
    raw_input_note = "本索引只服务原始 noisy PDF 阅读；不得替代主输入，不得净化成答案形摘要。"
    forbidden_sources = @(
        "gold/",
        "参考样稿/样稿",
        "成稿 docx",
        "任何答案形摘要"
    )
    pdf_count = $pdfEntries.Count
    pdf_entries = $pdfEntries
}

$jsonPath = Join-Path $runDir "raw_input_manifest.json"
$mdPath = Join-Path $runDir "raw_input_manifest.md"
Write-JsonFile -Path $jsonPath -Payload $manifest

$lines = @(
    "# 原始 PDF 阅读索引",
    "",
    "- 任务目录: $TaskDirectory",
    "- 搜索根目录: $searchRoot",
    "- 生成时间: $timestamp",
    "- 模式: raw-only",
    "- 规则: 保留原始 noisy inputs；本索引不得替代主输入",
    "",
    "## 禁止源",
    "",
    "- gold/",
    "- 参考样稿/样稿",
    "- 成稿 docx",
    "- 任何答案形摘要",
    "",
    "## 原始 PDF 清单",
    ""
)

foreach ($entry in $pdfEntries) {
    $lines += "### $($entry.pdf_name)"
    $lines += ""
    $lines += "- 相对路径: $($entry.relative_to_task)"
    $lines += "- 页数: $($entry.page_count)"
    $lines += "- 页面文本: $($entry.page_text_path)"
    $lines += "- 说明: 允许作为 raw input 保留；不得替代主输入"
    $lines += ""
}

Set-Content -LiteralPath $mdPath -Value $lines -Encoding UTF8

if ($SyncToTaskDirectory) {
    Copy-Item -LiteralPath $jsonPath -Destination (Join-Path $TaskDirectory "raw_input_manifest.json") -Force
    Copy-Item -LiteralPath $mdPath -Destination (Join-Path $TaskDirectory "raw_input_manifest.md") -Force
}

Write-Host "[INFO] Raw input manifest: $mdPath"
Write-Host "[INFO] Raw input manifest JSON: $jsonPath"
exit 0
