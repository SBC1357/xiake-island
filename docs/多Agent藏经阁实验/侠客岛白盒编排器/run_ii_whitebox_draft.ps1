param(
    [string]$CandidateId,
    [string]$CandidatePool = "",
    [string]$RunDirectory = "",
    [string]$ApiKey = "",
    [string]$DraftTextPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "whitebox_common.ps1")

if ([string]::IsNullOrWhiteSpace($RunDirectory)) {
    throw "必须提供 -RunDirectory。"
}

$poolData = Get-CandidatePoolData -Path $CandidatePool
$candidate = Resolve-Candidate -PoolData $poolData -CandidateId $CandidateId

$contractPath = Join-Path $RunDirectory "whitebox_contract.json"
$materialsPath = Join-Path (Join-Path $RunDirectory "materials") "materials_manifest.json"

if (-not (Test-Path -LiteralPath $contractPath)) {
    throw "缺少 whitebox_contract.json: $contractPath"
}
if (-not (Test-Path -LiteralPath $materialsPath)) {
    throw "缺少 materials_manifest.json: $materialsPath"
}

$contract = Read-JsonFile -Path $contractPath
$materials = Read-JsonFile -Path $materialsPath
$compiledTextPath = $materials.compiled_text
$compiledText = if ($compiledTextPath -and (Test-Path -LiteralPath $compiledTextPath)) { Get-Content -LiteralPath $compiledTextPath -Raw } else { "" }
$benchmarkEvaluationContract = if ($contract.PSObject.Properties.Name -contains "benchmark_evaluation_contract") {
    $contract.benchmark_evaluation_contract
}
elseif ($contract.PSObject.Properties.Name -contains "evaluation_contract") {
    $contract.evaluation_contract
}
else {
    $null
}
$benchmarkReferencePath = if ($benchmarkEvaluationContract -and $benchmarkEvaluationContract.PSObject.Properties.Name -contains "reference_answer_path") {
    [string]$benchmarkEvaluationContract.reference_answer_path
}
else {
    ""
}
$referenceSampleContract = $contract.reference_sample_contract
$referenceSamplePath = $null
$referenceSampleEnabledForDraft = $false
$referenceSampleRoles = @()
$referenceSampleBoundary = ""
$referenceSampleExcerpt = ""
if ($referenceSampleContract) {
    $referenceSampleRoles = @($referenceSampleContract.roles)
    $referenceSampleBoundary = [string]$referenceSampleContract.boundary
    $referenceSamplePath = $referenceSampleContract.resolved_path
    $referenceSampleEnabledForDraft = [bool]$referenceSampleContract.enabled_for_draft
}
if ($referenceSampleEnabledForDraft -and $referenceSamplePath -and (Test-Path -LiteralPath $referenceSamplePath)) {
    if (-not [string]::IsNullOrWhiteSpace($benchmarkReferencePath) -and (Test-Path -LiteralPath $benchmarkReferencePath)) {
        $sampleResolved = (Resolve-Path -LiteralPath $referenceSamplePath).ProviderPath
        $referenceResolved = (Resolve-Path -LiteralPath $benchmarkReferencePath).ProviderPath
        if ($sampleResolved -eq $referenceResolved) {
            throw "reference_sample_matches_benchmark_reference: $referenceSamplePath"
        }
    }
    $sampleExtract = Extract-FileText -Path $referenceSamplePath
    if (-not [string]::IsNullOrWhiteSpace($sampleExtract.text)) {
        $referenceSampleExcerpt = $sampleExtract.text.Substring(0, [Math]::Min(8000, $sampleExtract.text.Length))
    }
}

$draftPath = Join-Path $RunDirectory "draft.txt"
$draftManifestPath = Join-Path $RunDirectory "draft_manifest.json"
$draftSummaryPath = Join-Path $RunDirectory "draft_summary.md"
$draftPromptPath = Join-Path $RunDirectory "draft_prompt.md"
$goldPath = Join-Path $RunDirectory "reference_answer.txt"
$draftStartedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$referenceAnswerVisibleBeforeDraft = Test-Path -LiteralPath $goldPath

if ($referenceAnswerVisibleBeforeDraft) {
    throw "reference_answer_visible_before_draft: $goldPath"
}

# Build genre section
$genreStr = $contract.writing_contract.genre
$genreBlock = if ($genreStr) { "- 体裁：$genreStr" } else { "" }

# Build must_include_facts section
$mustFacts = @($contract.writing_contract.must_include_facts)
$mustFactsBlock = if ($mustFacts.Count -gt 0) {
    "【必写事实清单】`n以下每一条必须在正文中找到对应段落或句子，不得遗漏：`n$(($mustFacts | ForEach-Object { "- $_" }) -join "`n")"
} else { "" }

# Build required_structure section
$reqStruct = @($contract.writing_contract.required_structure)
$reqStructBlock = if ($reqStruct.Count -gt 0) {
    "【文章结构要求】`n文章必须按以下结构组织，每个板块必须有实质内容：`n$(($reqStruct | ForEach-Object { "- $_" }) -join "`n")"
} else { "" }

# Build pseudo_load_bearing_points block
$pseudoPoints = @($contract.orchestration_contract.pseudo_load_bearing_points)
$pseudoBlock = if ($pseudoPoints.Count -gt 0) {
    "$(($pseudoPoints | ForEach-Object { "- $_" }) -join "`n")"
} else { "（无）" }
$referenceSampleRolesText = if ($referenceSampleRoles.Count -gt 0) { $referenceSampleRoles -join " / " } else { "风格锚点 / 结构锚点 / 返修锚点" }
$referenceSampleBlock = if ($referenceSampleEnabledForDraft -and -not [string]::IsNullOrWhiteSpace($referenceSampleExcerpt)) {
@"
【参考样稿锚点】
- 样稿路径：$referenceSamplePath
- 允许用途：$referenceSampleRolesText
- 防泄露边界：$(if ($referenceSampleBoundary) { $referenceSampleBoundary } else { "只借结构和语气，不借事实和答案。" })

$referenceSampleExcerpt
"@
} else { "" }

# 读取轻量锚点卡（anchor card）
$anchorCardBlock = ""
$anchorCardPath = $contract.anchor_card_path
if ($anchorCardPath -and (Test-Path -LiteralPath $anchorCardPath)) {
    $anchorCardText = Get-Content -LiteralPath $anchorCardPath -Raw
    if (-not [string]::IsNullOrWhiteSpace($anchorCardText)) {
        $anchorCardBlock = @"
【证据锚点卡】
以下是从原始材料中提取的关键证据要点，写作时必须确保这些要点在正文中有对应落地：

$($anchorCardText.Substring(0, [Math]::Min(4000, $anchorCardText.Length)))
"@
    }
}

# 构建公式驱动约束 block
$formulaBlock = ""
$fc = $contract.formula_contract
if ($null -ne $fc) {
    $fbParts = @()
$fbParts += "【公式驱动约束（当前已接线公式位）】"
    $fbParts += "以下约束来自藏经阁8条公式的机器编码，你必须逐条遵守。"
    $fbParts += ""
    if ($fc.persona) { $fbParts += "■ 人格定位：$($fc.persona)" }
    if ($fc.range) { $fbParts += "■ 写作范围：$($fc.range)" }
    if ($fc.write_target) { $fbParts += "■ 写作目标：$($fc.write_target)" }
    if ($fc.arrangement_rule) { $fbParts += "■ 排列规则：$($fc.arrangement_rule)" }
    if ($fc.content_combo) { $fbParts += "■ 内容组合策略：$($fc.content_combo)" }
    if ($fc.logic_combo) { $fbParts += "■ 逻辑组合策略：$($fc.logic_combo)" }
    $eOutline = @($fc.effective_outline)
    if ($eOutline.Count -gt 0) {
        $fbParts += ""
        $fbParts += "■ 有效大纲（你必须按此大纲组织全文，每个板块必须有实质内容）："
        foreach ($item in $eOutline) { $fbParts += "  - $item" }
    }
    $ecu = @($fc.effective_content_unit)
    if ($ecu.Count -gt 0) {
        $fbParts += ""
        $fbParts += "■ 有效内容单元（以下每个单元必须在正文中至少出现一次，缺一扣分）："
        foreach ($item in $ecu) { $fbParts += "  - $item" }
    }
    $elu = @($fc.effective_logic_unit)
    if ($elu.Count -gt 0) {
        $fbParts += ""
        $fbParts += "■ 有效逻辑单元（全文承重逻辑必须遵守以下约束）："
        foreach ($item in $elu) { $fbParts += "  - $item" }
    }
    $formulaBlock = ($fbParts -join "`n")
}

$prompt = @"
你是侠客岛白盒编排器的执行写手。请严格按下面合同写一篇完整中文文章。

【写作合同】
- 题目：$($contract.candidate_name)
- 题型：$($contract.case_type)
- 受众：$($contract.writing_contract.audience)
- 目标字数：$($contract.writing_contract.target_word_count)
- 写作目的：$($contract.writing_contract.purpose)
$genreBlock

$formulaBlock

$mustFactsBlock

$reqStructBlock

【硬规则】
1. 只能使用提供材料，不得调用外部知识，不得补材。
2. 不得使用参考答案内容反向改写；参考答案此轮不可见。
3. 如果本轮放开了参考样稿，它也只能提供结构、语气和返修锚点；不得照抄样稿中的事实、数字、判断、标题或结论。
4. D类题必须避开伪承重点（即使材料里有大量相关内容，也不能写成主轴）：
$pseudoBlock
5. 如果材料不足以支撑某个强判断，改用保守写法，不要硬编。
6. 必写事实清单中列出的每一条都必须在正文中出现，缺一条扣分一次。
7. 写给临床医生看的文章，要用临床语言，避免过度学术腔和文献编号堆砌。
8. 数据来源层级标注：模型预测数据首次出现时必须标注"模型预测"；临床观测数据标注对应试验名；OLE或真实世界数据标注"OLE数据"或"真实世界数据"。不得混淆不同证据层级。
9. 材料中出现的 Figure / Table 编号必须在引用对应数据时标注来源锚点（如"Figure 5"），不得只写数字不注出处。
10. 如果上方公式驱动约束存在，你必须把人格定位贯穿全文语气和视角，每个有效内容单元至少在正文中对应一处实质段落，逻辑组合策略必须真正体现在全文承重结构中。

$referenceSampleBlock

$anchorCardBlock

【材料摘录】
$($compiledText.Substring(0, [Math]::Min(22000, $compiledText.Length)))

请直接输出完整文章正文，不要加解释，不要加前言，不要加代码块。
"@

$prompt = Build-WhiteboxPromptWithProfile -Prompt $prompt -ProfileName "draft"

Set-Content -LiteralPath $draftPromptPath -Value $prompt -Encoding UTF8

if ($DraftTextPath) {
    if (-not (Test-Path -LiteralPath $DraftTextPath)) {
        throw "外部稿件不存在: $DraftTextPath"
    }
    $draft = Get-Content -LiteralPath $DraftTextPath -Raw
    if ([string]::IsNullOrWhiteSpace($draft)) {
        throw "外部稿件为空: $DraftTextPath"
    }
    $status = "completed"
    $exitCode = 0
    $errorMsg = $null
}
else {
    try {
        $draft = Invoke-WhiteboxLlm -Prompt $prompt -ApiKeyOverride $ApiKey -Temperature 0.2 -ProfileName "draft"
        $status = "completed"
        $exitCode = 0
        $errorMsg = $null
    }
    catch {
        $draft = ""
        $status = if ($_.Exception.Message -eq "missing_llm_api_key" -or $_.Exception.Message -like "llm_transport_unavailable:*") { "agent_continue_required" } else { "failed" }
        $exitCode = if ($status -eq "agent_continue_required") { 4 } else { 1 }
        $errorMsg = $_.Exception.Message
    }
}

if ($draft) {
    Set-Content -LiteralPath $draftPath -Value $draft -Encoding UTF8
}

$draftCompletedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$manifest = [pscustomobject][ordered]@{
    candidate_id = $candidate.id
    candidate_name = $candidate.name
    status = $status
    exit_code = $exitCode
    draft_origin = if ($DraftTextPath) { "external_injected" } elseif ($status -eq "completed") { "llm_generated" } else { "generation_failed" }
    external_draft_source_path = if ($DraftTextPath) { $DraftTextPath } else { $null }
    llm_profile = if (-not $DraftTextPath) { "draft" } else { $null }
    run_directory = $RunDirectory
    draft_started_at = $draftStartedAt
    draft_completed_at = $draftCompletedAt
    draft_path = if ($draft) { $draftPath } else { $null }
    draft_prompt_path = $draftPromptPath
    reference_answer_guard_path = $goldPath
    reference_answer_visible_before_draft = $referenceAnswerVisibleBeforeDraft
    reference_sample_path = $referenceSamplePath
    reference_sample_enabled_for_draft = $referenceSampleEnabledForDraft
    reference_sample_roles = $referenceSampleRoles
    error = $errorMsg
}
Write-JsonFile -Path $draftManifestPath -Payload $manifest

$lines = @(
    "# 白盒出稿摘要",
    "",
    "- 题目: $($candidate.id) / $($candidate.name)",
    "- 状态: $status"
)
if ($errorMsg) {
    $lines += "- 错误: $errorMsg"
}
if ($DraftTextPath) {
    $lines += "- 稿件来源: external_injected"
    $lines += "- 外部稿件路径: $DraftTextPath"
}
else {
    $lines += "- 稿件来源: llm_generated"
    $lines += "- LLM profile: draft"
}
if ($draftPromptPath) {
    $lines += "- 提示词: $draftPromptPath"
}
if ($draft) {
    $lines += "- 稿件: $draftPath"
    $lines += "- 字数: $($draft.Length)"
}
$lines += "- 出稿前 gold 是否可见: $referenceAnswerVisibleBeforeDraft"
$lines += "- 参考样稿是否进入出稿提示词: $referenceSampleEnabledForDraft"
if ($referenceSampleEnabledForDraft -and $referenceSamplePath) {
    $lines += "- 参考样稿路径: $referenceSamplePath"
}
Set-Content -LiteralPath $draftSummaryPath -Value $lines -Encoding UTF8

Write-Host "[INFO] 出稿摘要: $draftSummaryPath"
Write-Host "[INFO] 出稿清单: $draftManifestPath"
exit $exitCode
