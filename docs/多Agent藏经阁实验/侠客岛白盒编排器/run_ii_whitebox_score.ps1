param(
    [string]$CandidateId,
    [string]$CandidatePool = "",
    [string]$RunDirectory = "",
    [string]$ApiKey = "",
    [string]$ScoreJsonPath = ""
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
$draftPath = Join-Path $RunDirectory "draft.txt"

if (-not (Test-Path -LiteralPath $contractPath)) {
    throw "缺少 whitebox_contract.json: $contractPath"
}
if (-not (Test-Path -LiteralPath $draftPath)) {
    throw "缺少 draft.txt: $draftPath"
}

$contract = Read-JsonFile -Path $contractPath
$draftText = [System.IO.File]::ReadAllText($draftPath, [System.Text.Encoding]::UTF8)
$benchmarkEvaluationContract = if ($contract.PSObject.Properties.Name -contains "benchmark_evaluation_contract") {
    $contract.benchmark_evaluation_contract
}
elseif ($contract.PSObject.Properties.Name -contains "evaluation_contract") {
    $contract.evaluation_contract
}
else {
    $null
}

# 读取公式合同（如有）
$fc = $null
if ($contract.PSObject.Properties.Name -contains "formula_contract" -and $null -ne $contract.formula_contract) {
    $fc = $contract.formula_contract
}
$formulaTraceBlock = ""
if ($null -ne $fc) {
    $ftParts = @()
    $ftParts += "【公式合规审计（formula_trace）】"
    $ftParts += "请逐条检查以下公式位在白盒系统稿中是否被正确调用。对每个公式位给出 hit/miss/partial 判定和证据。"
    $ftParts += ""
    if ($fc.persona) { $ftParts += "- persona: $($fc.persona)" }
    if ($fc.range) { $ftParts += "- range: $($fc.range)" }
    if ($fc.write_target) { $ftParts += "- write_target: $($fc.write_target)" }
    if ($fc.content_combo) { $ftParts += "- content_combo: $($fc.content_combo)" }
    if ($fc.logic_combo) { $ftParts += "- logic_combo: $($fc.logic_combo)" }
    $ecu = @()
    if ($fc.PSObject.Properties.Name -contains "effective_content_unit") { $ecu = @($fc.effective_content_unit) }
    if ($ecu.Count -gt 0) {
        $ftParts += "- effective_content_unit:"
        foreach ($item in $ecu) { $ftParts += "  - $item" }
    }
    $elu = @()
    if ($fc.PSObject.Properties.Name -contains "effective_logic_unit") { $elu = @($fc.effective_logic_unit) }
    if ($elu.Count -gt 0) {
        $ftParts += "- effective_logic_unit:"
        foreach ($item in $elu) { $ftParts += "  - $item" }
    }
    $eOutline = @()
    if ($fc.PSObject.Properties.Name -contains "effective_outline") { $eOutline = @($fc.effective_outline) }
    if ($eOutline.Count -gt 0) {
        $ftParts += "- effective_outline:"
        foreach ($item in $eOutline) { $ftParts += "  - $item" }
    }
    $formulaTraceBlock = ($ftParts -join "`n")
}

$referencePath = if ($benchmarkEvaluationContract -and $benchmarkEvaluationContract.PSObject.Properties.Name -contains "reference_answer_path") {
    [string]$benchmarkEvaluationContract.reference_answer_path
}
else {
    ""
}
$usesBenchmarkReference = -not [string]::IsNullOrWhiteSpace($referencePath)
if (-not $ScoreJsonPath -and -not $usesBenchmarkReference) {
    throw "缺少 benchmark reference_answer_path，当前评分器无法执行 reference compare。"
}
if ($usesBenchmarkReference -and -not (Test-Path -LiteralPath $referencePath)) {
    throw "参考答案不存在: $referencePath"
}
$referenceText = if ($usesBenchmarkReference) { Extract-DocxText -Path $referencePath } else { "" }

$goldPath = Join-Path $RunDirectory "reference_answer.txt"
$scorePath = Join-Path $RunDirectory "score.json"
$scoreSummaryPath = Join-Path $RunDirectory "score_summary.md"
$scoreManifestPath = Join-Path $RunDirectory "score_manifest.json"
$scorePromptPath = Join-Path $RunDirectory "score_prompt.md"
$scoreStartedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$referenceAnswerWrittenAt = $null
if ($usesBenchmarkReference) {
    Set-Content -LiteralPath $goldPath -Value $referenceText -Encoding UTF8
    $referenceAnswerWrittenAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$draftManifestPath = Join-Path $RunDirectory "draft_manifest.json"
$draftManifest = if (Test-Path -LiteralPath $draftManifestPath) { Read-JsonFile -Path $draftManifestPath } else { $null }

$prompt = @"
你是侠客岛白盒编排器的评分回指器。请比较"白盒系统稿"和"参考答案"，输出严格 JSON。
先做硬层（benchmark / 合同命中）判断，再做软层（编辑观感 / 可发表性）判断。

【题目】
- 名称：$($contract.candidate_name)
- 题型：$($contract.case_type)
- 受众：$($contract.writing_contract.audience)
- 写作目的：$($contract.writing_contract.purpose)

【合同中的伪承重点】
$((@($contract.orchestration_contract.pseudo_load_bearing_points) | ForEach-Object { "- $_" }) -join "`n")

$(if ($formulaTraceBlock) { $formulaTraceBlock } else { "" })

【参考答案】
$($referenceText.Substring(0, [Math]::Min(4000, $referenceText.Length)))

【白盒系统稿】
$($draftText.Substring(0, [Math]::Min(4000, $draftText.Length)))

请输出 JSON，字段必须包含：
{
  "weighted_total": 0-100整数（仅基于以下5个通用维度加权：route_alignment 25%、key_facts 25%、audience_style 20%、structure 15%、hallucination_control 15%）,
  "qualified": true/false,
  "dimensions": [
    {"id":"route_alignment","score":0-100,"weight":25,"reason":"..."},
    {"id":"key_facts","score":0-100,"weight":25,"reason":"..."},
    {"id":"audience_style","score":0-100,"weight":20,"reason":"..."},
    {"id":"structure","score":0-100,"weight":15,"reason":"..."},
    {"id":"hallucination_control","score":0-100,"weight":15,"reason":"..."}
  ],
  "editorial_total": 0-100整数（独立软层总评，不参与 qualified 判定）,
  "editorial_dimensions": [
    {"id":"publishability","score":0-100,"reason":"这篇稿是否已接近可发布状态"},
    {"id":"narrative_drive","score":0-100,"reason":"是否有推进力、读下去的动力、不是流水账"},
    {"id":"reader_fit","score":0-100,"reason":"是否真正贴合目标读者，而不只是合同字段命中"},
    {"id":"naturalness","score":0-100,"reason":"中文是否自然、像成熟编辑交稿，而不是模板腔"}
  ],
  "writing_strength": [
    {"id":"opening_hook","score":0-100,"reason":"开场是否用公式要求的内容单元建立问题感和抓力"},
    {"id":"transition_flow","score":0-100,"reason":"段间过渡是否沿逻辑组合的规定路径流畅衔接"},
    {"id":"midgame_drive","score":0-100,"reason":"中段是否按内容组合密度要求推进，信息不断层"},
    {"id":"closing_tension","score":0-100,"reason":"收尾是否落回逻辑单元要求的终点，有张力和意义回收"},
    {"id":"anchor_fidelity","score":0-100,"reason":"锚点卡要点是否按有效内容单元要求在正文中落地"}
  ],
  "formula_compliance": 0-100（如无公式合规审计段则填0）,
  "formula_trace": [
    {"position":"公式位名","status":"hit或miss或partial","evidence":"稿中对应段落摘录"}
  ],
  "formula_compliance_summary": "公式合规总评",
  "layer_judgment": {
    "hard_layer_verdict": "仅基于 benchmark / 合同命中的结论",
    "editorial_layer_verdict": "仅基于成稿观感和可发表性的结论",
    "overall_note": "说明两层是否一致，若不一致，指出差异来自哪里"
  },
  "blocking_issues": ["..."],
  "missing_or_misaligned": ["..."],
  "backtrace": [
    {"target_layer":"input_contract|orchestration_contract|writing_contract|materials_coverage|formula_contract","issue":"...","evidence":"..."}
  ],
  "next_actions": ["..."]
}

规则：
1. 如果路线错、关键事实漏得厉害、或出现明显越界编造，qualified=false。
2. backtrace 必须尽量把问题回指到合同层或公式合同层，不要只说"写得不好"。
3. formula_trace 必须逐条审计公式合规审计段中列出的每个公式位。如果没有公式合规审计段，formula_trace 为空数组，formula_compliance 填0。
4. formula_compliance 评分：命中率80%以上且无关键位 miss 得80+；有关键位 miss 扣到60以下。
5. weighted_total 仅由5个通用维度按权重计算，不含 formula_compliance 和 writing_strength。
6. editorial_total 与 editorial_dimensions 是软层，不得直接改变 qualified；即使稿子更顺、更像人写，只要硬层缺事实或路线错，qualified 仍应为 false。
7. writing_strength 是写作力副表，独立评估，不计入 weighted_total。评估顺序：先独立打5维写作力分，再用公式合同中的 effective_content_unit、effective_logic_unit、content_combo、logic_combo 逐条校验——如果某维度得分高但对应公式位 miss，该维度须下修；如果公式位 hit 但写作力弱，照实打低分。
8. 如果硬层和软层结论不一致，必须在 layer_judgment.overall_note 中明确写出差异原因。例如“合同命中不足但成稿观感较好”“事实基本齐但中文交付感弱”。
9. blocking_issues 和 missing_or_misaligned 优先承载硬层问题；纯观感问题优先放进 editorial_dimensions、writing_strength 或 next_actions，不要硬塞成 blocking。
10. 只输出 JSON。
"@

$prompt = Build-WhiteboxPromptWithProfile -Prompt $prompt -ProfileName "review_score"

Set-Content -LiteralPath $scorePromptPath -Value $prompt -Encoding UTF8

if ($ScoreJsonPath) {
    if (-not (Test-Path -LiteralPath $ScoreJsonPath)) {
        throw "外部评分 JSON 不存在: $ScoreJsonPath"
    }
    $parsed = Read-JsonFile -Path $ScoreJsonPath
    $status = "completed"
    $exitCode = 0
$errorMsg = $null
}
else {
    try {
        $raw = Invoke-WhiteboxLlm -Prompt $prompt -ApiKeyOverride $ApiKey -Temperature 0.1 -ProfileName "review_score"
        $parsed = Try-ParseJsonText -Text $raw
        if ($null -eq $parsed) {
            throw "无法解析评分 JSON"
        }
        $status = "completed"
        $exitCode = 0
    $errorMsg = $null
    }
    catch {
        $parsed = $null
        $status = if ($_.Exception.Message -eq "missing_llm_api_key" -or $_.Exception.Message -like "llm_transport_unavailable:*") { "agent_continue_required" } else { "failed" }
        $exitCode = if ($status -eq "agent_continue_required") { 4 } else { 1 }
        $errorMsg = $_.Exception.Message
    }
}

if ($parsed) {
    Write-JsonFile -Path $scorePath -Payload $parsed
}

$scoreCompletedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$manifest = [pscustomobject][ordered]@{
    candidate_id = $candidate.id
    candidate_name = $candidate.name
    status = $status
    exit_code = $exitCode
    score_origin = if ($ScoreJsonPath) { "external_injected" } elseif ($status -eq "completed") { "benchmark_llm_generated" } else { "generation_failed" }
    external_score_source_path = if ($ScoreJsonPath) { $ScoreJsonPath } else { $null }
    llm_profile = if (-not $ScoreJsonPath) { "review_score" } else { $null }
    benchmark_mode = $usesBenchmarkReference
    run_directory = $RunDirectory
    score_started_at = $scoreStartedAt
    score_completed_at = $scoreCompletedAt
    score_path = if ($parsed) { $scorePath } else { $null }
    score_prompt_path = $scorePromptPath
    reference_answer_source_path = $referencePath
    reference_answer_materialized_path = if ($usesBenchmarkReference) { $goldPath } else { $null }
    reference_answer_written_at = $referenceAnswerWrittenAt
    draft_manifest_path = if ($draftManifest) { $draftManifestPath } else { $null }
    draft_reference_answer_visible_before_draft = if ($draftManifest) { $draftManifest.reference_answer_visible_before_draft } else { $null }
    error = $errorMsg
}
Write-JsonFile -Path $scoreManifestPath -Payload $manifest

$lines = @(
    "# 白盒评分摘要",
    "",
    "- 题目: $($candidate.id) / $($candidate.name)",
    "- 状态: $status"
)
if ($errorMsg) {
    $lines += "- 错误: $errorMsg"
}
if ($ScoreJsonPath) {
    $lines += "- 评分来源: external_injected"
    $lines += "- 外部评分路径: $ScoreJsonPath"
}
else {
    $lines += "- 评分来源: benchmark_llm_generated"
    $lines += "- LLM profile: review_score"
}
if ($scorePromptPath) {
    $lines += "- 提示词: $scorePromptPath"
}
if ($parsed) {
    $lines += "- 总分: $($parsed.weighted_total)"
    $lines += "- 是否合格: $($parsed.qualified)"
    if ($parsed.PSObject.Properties.Name -contains "editorial_total") {
        $lines += "- 编辑软层总评: $($parsed.editorial_total)"
    }
    if ($usesBenchmarkReference) {
        $lines += "- benchmark comparator: enabled"
        $lines += "- gold 写入时间: $referenceAnswerWrittenAt"
    }
    else {
        $lines += "- benchmark comparator: disabled"
    }
    if ($usesBenchmarkReference -and $draftManifest) {
        $lines += "- 出稿前 gold 是否可见: $($draftManifest.reference_answer_visible_before_draft)"
    }
    foreach ($issue in @($parsed.blocking_issues)) {
        $lines += "- 阻塞: $issue"
    }
}
Set-Content -LiteralPath $scoreSummaryPath -Value $lines -Encoding UTF8

Write-Host "[INFO] 评分摘要: $scoreSummaryPath"
Write-Host "[INFO] 评分清单: $scoreManifestPath"
exit $exitCode
