param(
    [string]$CandidateId,
    [string]$CandidatePool = "",
    [string]$OutputRoot = "D:\汇度编辑部1\侠客岛-runtime\ii_whitebox",
    [switch]$EnableReferenceSample,
    [switch]$EnableL1WritingCraft,
    [string]$L1AssetsPath = "",
    [switch]$ListCandidates
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-DefaultCandidatePool {
    return Join-Path (Join-Path $PSScriptRoot "config") "ii_candidate_pool.json"
}

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
    $convertCmd = Get-Command ConvertTo-Json
    if ($convertCmd.Parameters.ContainsKey("Depth")) {
        $Payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
    }
    else {
        $Payload | ConvertTo-Json | Set-Content -LiteralPath $Path -Encoding UTF8
    }
}

function Write-MarkdownFile {
    param(
        [string]$Path,
        [string[]]$Lines
    )

    Set-Content -LiteralPath $Path -Value $Lines -Encoding UTF8
}

function Get-CandidatePoolData {
    param([string]$Path)

    $resolvedPath = if ($Path) { $Path } else { Get-DefaultCandidatePool }
    if (-not (Test-Path -LiteralPath $resolvedPath)) {
        throw "候选池不存在: $resolvedPath"
    }

    $pool = Read-JsonFile -Path $resolvedPath
    $candidateMap = @{}
    foreach ($candidate in $pool.candidates) {
        $candidateMap[$candidate.id] = $candidate
    }

    return [pscustomobject]@{
        Path = $resolvedPath
        Pool = $pool
        CandidateMap = $candidateMap
    }
}

function Get-RequiredManualGates {
    param(
        [object]$Candidate,
        [bool]$EnableReferenceSample
    )

    $gates = @()

    if ($Candidate.case_type -eq "D") {
        $pseudoPoints = @()
        if ($Candidate.PSObject.Properties.Name -contains "pseudo_load_bearing_points") {
            $pseudoPoints = @($Candidate.pseudo_load_bearing_points)
        }
        if ($pseudoPoints.Count -lt 1) {
            $gates += "缺少 D 类伪承重点"
        }
    }

    $referenceSample = Get-ReferenceSampleContract -Candidate $Candidate -EnableForDraft:$EnableReferenceSample
    if ($EnableReferenceSample) {
        if ([string]::IsNullOrWhiteSpace([string]$referenceSample.declared_path)) {
            $gates += "缺少 reference_sample_path"
        }
        elseif (-not $referenceSample.exists) {
            $gates += "reference_sample_path 不存在: $($referenceSample.resolved_path)"
        }
        elseif (-not $referenceSample.frozen) {
            $gates += "reference_sample 未冻结"
        }
    }

    return $gates
}

function Resolve-AnchorCardContract {
    param([object]$Candidate)

    $declaredPath = if ($Candidate.PSObject.Properties.Name -contains "anchor_card_path") { [string]$Candidate.anchor_card_path } else { "" }
    if (-not [string]::IsNullOrWhiteSpace($declaredPath)) {
        $resolvedPath = if (Test-Path -LiteralPath $declaredPath) { $declaredPath } else { Join-Path $Candidate.source_root $declaredPath }
        if (Test-Path -LiteralPath $resolvedPath) {
            return [ordered]@{
                declared_path = $declaredPath
                resolved_path = $resolvedPath
                source = "candidate_declared"
            }
        }
    }

    foreach ($fileName in @("topic_anchor_card.md", "evidence_anchor_card.md", "g0_evidence_card.md")) {
        $resolvedPath = Join-Path $Candidate.source_root $fileName
        if (Test-Path -LiteralPath $resolvedPath) {
            return [ordered]@{
                declared_path = $fileName
                resolved_path = $resolvedPath
                source = if ($fileName -eq "g0_evidence_card.md") { "legacy_g0_fallback" } else { "source_root_default" }
            }
        }
    }

    return [ordered]@{
        declared_path = $null
        resolved_path = $null
        source = "missing"
    }
}

function Get-ReferenceSampleContract {
    param(
        [object]$Candidate,
        [bool]$EnableForDraft
    )

    $declaredPath = if ($Candidate.PSObject.Properties.Name -contains "reference_sample_path") { [string]$Candidate.reference_sample_path } else { "" }
    $roles = if ($Candidate.PSObject.Properties.Name -contains "reference_sample_roles") { @($Candidate.reference_sample_roles) } else { @() }
    $selectionOwner = if ($Candidate.PSObject.Properties.Name -contains "reference_sample_selection_owner") { [string]$Candidate.reference_sample_selection_owner } else { "" }
    $visibilityStage = if ($Candidate.PSObject.Properties.Name -contains "reference_sample_visibility_stage") { [string]$Candidate.reference_sample_visibility_stage } else { "" }
    $boundary = if ($Candidate.PSObject.Properties.Name -contains "reference_sample_boundary") { [string]$Candidate.reference_sample_boundary } else { "" }
    $frozen = if ($Candidate.PSObject.Properties.Name -contains "reference_sample_frozen") { [bool]$Candidate.reference_sample_frozen } else { $false }

    $resolvedPath = $null
    $exists = $false
    if (-not [string]::IsNullOrWhiteSpace($declaredPath)) {
        $resolvedPath = if (Test-Path -LiteralPath $declaredPath) { $declaredPath } else { Join-Path $Candidate.source_root $declaredPath }
        $exists = Test-Path -LiteralPath $resolvedPath
    }

    return [ordered]@{
        declared_path = if ([string]::IsNullOrWhiteSpace($declaredPath)) { $null } else { $declaredPath }
        resolved_path = $resolvedPath
        exists = $exists
        frozen = $frozen
        selection_owner = $selectionOwner
        visibility_stage = $visibilityStage
        boundary = $boundary
        roles = $roles
        requested_for_draft = [bool]$EnableForDraft
        enabled_for_draft = [bool]($EnableForDraft -and $frozen -and $exists)
    }
}

function Get-RouteProfile {
    param([object]$Candidate)

    if ($Candidate.case_type -eq "D") {
        return [ordered]@{
            mode = "noisy_adversarial"
            required_steps = @(
                "锁定写作目的",
                "区分主承重/支撑/噪声/冲突/伪承重点",
                "限制全文只能沿已锁定主线写作",
                "遇到材料不足时回指到缺口，不补材"
            )
            required_outputs = @(
                "主承重清单",
                "噪声与冲突清单",
                "伪承重点清单",
                "成稿合同"
            )
            failure_modes = @(
                "被海量材料带成综述",
                "被亮眼副信息带偏标题",
                "把安全性决策稿写成疗效宣传稿"
            )
        }
    }

    return [ordered]@{
        mode = "closed_book_clean"
        required_steps = @(
            "锁定题型与受众",
            "从允许材料提取主承重事实",
            "组装成稿合同",
            "闭卷输出整稿"
        )
        required_outputs = @(
            "主承重清单",
            "必须写入的数字/事实",
            "成稿合同"
        )
        failure_modes = @(
            "路线不稳",
            "数字漏写",
            "语体不匹配"
        )
    }
}

function Build-WhiteboxContract {
    param(
        [object]$Candidate,
        [string]$CandidatePoolPath,
        [bool]$EnableReferenceSample
    )

    $referenceSampleContract = Get-ReferenceSampleContract -Candidate $Candidate -EnableForDraft:$EnableReferenceSample
    $anchorCardContract = Resolve-AnchorCardContract -Candidate $Candidate
    $manualGates = @(Get-RequiredManualGates -Candidate $Candidate -EnableReferenceSample:$EnableReferenceSample)
    $routeProfile = Get-RouteProfile -Candidate $Candidate

    $status = if ($manualGates.Count -gt 0) { "blocked_manual" } else { "ready" }
    $exitCode = if ($manualGates.Count -gt 0) { 2 } else { 0 }

    $inputRules = @($Candidate.input_rules)
    $forbiddenRules = @()
    foreach ($rule in $inputRules) {
        if ($rule.mode -eq "allow_all_except_docx") {
            $forbiddenRules += "禁止使用 $($rule.path) 下任何 docx 作为正式输入"
        }
    }
    if ($referenceSampleContract.declared_path) {
        $forbiddenRules += "禁止把 reference_sample.docx / 参考样稿当作事实源或 gold 替身"
    }

    $pseudoPoints = @()
    if ($Candidate.PSObject.Properties.Name -contains "pseudo_load_bearing_points") {
        $pseudoPoints = @($Candidate.pseudo_load_bearing_points)
    }

    $genre = ""
    if ($Candidate.PSObject.Properties.Name -contains "genre") {
        $genre = $Candidate.genre
    }

    $coreDataPoints = @()
    if ($Candidate.PSObject.Properties.Name -contains "core_data_points") {
        $coreDataPoints = @($Candidate.core_data_points)
    }

    $requiredStructure = @()
    if ($Candidate.PSObject.Properties.Name -contains "required_structure") {
        $requiredStructure = @($Candidate.required_structure)
    }

    # 读取公式位
    $formulaPositions = $null
    if ($Candidate.PSObject.Properties.Name -contains "formula_positions") {
        $fp = $Candidate.formula_positions
        $formulaPositions = [ordered]@{
            write_target = if ($fp.PSObject.Properties.Name -contains "write_target") { $fp.write_target } else { "" }
            arrangement_rule = if ($fp.PSObject.Properties.Name -contains "arrangement_rule") { $fp.arrangement_rule } else { "" }
            persona = if ($fp.PSObject.Properties.Name -contains "persona") { $fp.persona } else { "" }
            range = if ($fp.PSObject.Properties.Name -contains "range") { $fp.range } else { "" }
            min_content_unit = if ($fp.PSObject.Properties.Name -contains "min_content_unit") { @($fp.min_content_unit) } else { @() }
            min_logic_unit = if ($fp.PSObject.Properties.Name -contains "min_logic_unit") { @($fp.min_logic_unit) } else { @() }
            effective_content_unit = if ($fp.PSObject.Properties.Name -contains "effective_content_unit") { @($fp.effective_content_unit) } else { @() }
            effective_logic_unit = if ($fp.PSObject.Properties.Name -contains "effective_logic_unit") { @($fp.effective_logic_unit) } else { @() }
            content_combo = if ($fp.PSObject.Properties.Name -contains "content_combo") { $fp.content_combo } else { "" }
            logic_combo = if ($fp.PSObject.Properties.Name -contains "logic_combo") { $fp.logic_combo } else { "" }
            outline = if ($fp.PSObject.Properties.Name -contains "outline") { @($fp.outline) } else { @() }
            effective_outline = if ($fp.PSObject.Properties.Name -contains "effective_outline") { @($fp.effective_outline) } else { @() }
        }
    }

    return [pscustomobject][ordered]@{
        generated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        candidate_id = $Candidate.id
        candidate_name = $Candidate.name
        case_type = $Candidate.case_type
        status = $status
        exit_code = $exitCode
        source_root = $Candidate.source_root
        candidate_pool = $CandidatePoolPath
        input_contract = [ordered]@{
            allowed_inputs = $inputRules
            forbidden_inputs = $forbiddenRules
        }
        writing_contract = [ordered]@{
            audience = $Candidate.audience
            target_word_count = $Candidate.target_word_count
            purpose = $Candidate.purpose
            genre = $genre
            must_include_facts = $coreDataPoints
            required_structure = $requiredStructure
        }
        benchmark_evaluation_contract = [ordered]@{
            enabled = [bool]($Candidate.PSObject.Properties.Name -contains "reference_answer_path" -and -not [string]::IsNullOrWhiteSpace([string]$Candidate.reference_answer_path))
            reference_answer_path = if ($Candidate.PSObject.Properties.Name -contains "reference_answer_path") { $Candidate.reference_answer_path } else { $null }
            scoring_mode = "closed_book_then_reference_compare"
            boundary = "仅供 benchmark comparator 使用，不得进入上游写作编排和人工阻塞条件。"
        }
        reference_sample_contract = $referenceSampleContract
        orchestration_contract = [ordered]@{
            route_profile = $routeProfile
            pseudo_load_bearing_points = $pseudoPoints
        }
        formula_contract = $formulaPositions
        anchor_card_path = $anchorCardContract.resolved_path
        anchor_card_source = $anchorCardContract.source
        manual_gates = $manualGates
    }
}

function Build-StateCards {
    param([object]$Contract)

    $taskBrief = [pscustomobject][ordered]@{
        candidate_id = $Contract.candidate_id
        candidate_name = $Contract.candidate_name
        case_type = $Contract.case_type
        source_root = $Contract.source_root
        audience = $Contract.writing_contract.audience
        target_word_count = $Contract.writing_contract.target_word_count
        purpose = $Contract.writing_contract.purpose
        genre = $Contract.writing_contract.genre
    }

    $genreRouting = [pscustomobject][ordered]@{
        case_type = $Contract.case_type
        genre = $Contract.writing_contract.genre
        route_mode = $Contract.orchestration_contract.route_profile.mode
        required_steps = @($Contract.orchestration_contract.route_profile.required_steps)
        failure_modes = @($Contract.orchestration_contract.route_profile.failure_modes)
    }

    $sampleContract = [pscustomobject][ordered]@{
        declared_path = $Contract.reference_sample_contract.declared_path
        resolved_path = $Contract.reference_sample_contract.resolved_path
        exists = $Contract.reference_sample_contract.exists
        frozen = $Contract.reference_sample_contract.frozen
        roles = @($Contract.reference_sample_contract.roles)
        selection_owner = $Contract.reference_sample_contract.selection_owner
        visibility_stage = $Contract.reference_sample_contract.visibility_stage
        boundary = $Contract.reference_sample_contract.boundary
        enabled_for_draft = $Contract.reference_sample_contract.enabled_for_draft
    }

    $topicCandidatePacket = [pscustomobject][ordered]@{
        status = "construction_seed_only"
        derived_from = "writing_contract.purpose"
        recommended_mainline = $Contract.writing_contract.purpose
        alternative_mainline = $null
        supporting_points = @($Contract.writing_contract.must_include_facts)
        outline_seed = @($Contract.writing_contract.required_structure)
        current_gaps = @(
            "当前仍是施工期候选卡，不代表已完成真实主题探索",
            "备选主线与扩证方向仍待后续白盒节点真实产出"
        )
        next_action = "后续必须由主题探索节点真实补出推荐/备选主线，不能把这张卡直接当成正式主题结论。"
    }

    $topicConfirmationCard = [pscustomobject][ordered]@{
        status = "construction_placeholder"
        recommended_mainline = $topicCandidatePacket.recommended_mainline
        can_enter_writing_contract = $false
        blocked_by = @(
            "缺少正式主题确认裁决",
            "缺少成文闭环判断",
            "当前卡片仍是施工占位，不代表正式确认已发生"
        )
    }

    $themeLockPolicyCard = [pscustomobject][ordered]@{
        status = "construction_placeholder"
        selected_value = $null
        allowed_values = @("strict", "bounded", "open")
        note = "当前仅输出可选项，不在合同物化层预判锁策略，也不宣称主题锁已真实决策。"
    }

    return [pscustomobject][ordered]@{
        task_brief_card = $taskBrief
        genre_routing_card = $genreRouting
        sample_contract = $sampleContract
        topic_candidate_packet = $topicCandidatePacket
        topic_confirmation_card = $topicConfirmationCard
        theme_lock_policy_card = $themeLockPolicyCard
    }
}

function Write-StateCards {
    param(
        [string]$RunDirectory,
        [object]$StateCards
    )

    $cardsDir = Join-Path $RunDirectory "state_cards"
    New-Item -ItemType Directory -Path $cardsDir -Force | Out-Null

    $taskBriefJson = Join-Path $cardsDir "task_brief_card.json"
    $taskBriefMd = Join-Path $cardsDir "task_brief_card.md"
    Write-JsonFile -Path $taskBriefJson -Payload $StateCards.task_brief_card
    Write-MarkdownFile -Path $taskBriefMd -Lines @(
        "# task_brief_card",
        "",
        "- candidate_id: $($StateCards.task_brief_card.candidate_id)",
        "- candidate_name: $($StateCards.task_brief_card.candidate_name)",
        "- case_type: $($StateCards.task_brief_card.case_type)",
        "- source_root: $($StateCards.task_brief_card.source_root)",
        "- audience: $($StateCards.task_brief_card.audience)",
        "- target_word_count: $($StateCards.task_brief_card.target_word_count)",
        "- purpose: $($StateCards.task_brief_card.purpose)",
        "- genre: $($StateCards.task_brief_card.genre)"
    )

    $genreRoutingJson = Join-Path $cardsDir "genre_routing_card.json"
    $genreRoutingMd = Join-Path $cardsDir "genre_routing_card.md"
    Write-JsonFile -Path $genreRoutingJson -Payload $StateCards.genre_routing_card
    $genreLines = @(
        "# genre_routing_card",
        "",
        "- case_type: $($StateCards.genre_routing_card.case_type)",
        "- genre: $($StateCards.genre_routing_card.genre)",
        "- route_mode: $($StateCards.genre_routing_card.route_mode)",
        "",
        "## required_steps"
    )
    foreach ($item in @($StateCards.genre_routing_card.required_steps)) { $genreLines += "- $item" }
    $genreLines += ""
    $genreLines += "## failure_modes"
    foreach ($item in @($StateCards.genre_routing_card.failure_modes)) { $genreLines += "- $item" }
    Write-MarkdownFile -Path $genreRoutingMd -Lines $genreLines

    $sampleContractJson = Join-Path $cardsDir "sample_contract.json"
    $sampleContractMd = Join-Path $cardsDir "sample_contract.md"
    Write-JsonFile -Path $sampleContractJson -Payload $StateCards.sample_contract
    $sampleLines = @(
        "# sample_contract",
        "",
        "- declared_path: $($StateCards.sample_contract.declared_path)",
        "- resolved_path: $($StateCards.sample_contract.resolved_path)",
        "- exists: $($StateCards.sample_contract.exists)",
        "- frozen: $($StateCards.sample_contract.frozen)",
        "- selection_owner: $($StateCards.sample_contract.selection_owner)",
        "- visibility_stage: $($StateCards.sample_contract.visibility_stage)",
        "- enabled_for_draft: $($StateCards.sample_contract.enabled_for_draft)",
        "- boundary: $($StateCards.sample_contract.boundary)",
        "",
        "## roles"
    )
    foreach ($item in @($StateCards.sample_contract.roles)) { $sampleLines += "- $item" }
    Write-MarkdownFile -Path $sampleContractMd -Lines $sampleLines

    $topicCandidateJson = Join-Path $cardsDir "topic_candidate_packet.json"
    $topicCandidateMd = Join-Path $cardsDir "topic_candidate_packet.md"
    Write-JsonFile -Path $topicCandidateJson -Payload $StateCards.topic_candidate_packet
    $topicLines = @(
        "# topic_candidate_packet",
        "",
        "- status: $($StateCards.topic_candidate_packet.status)",
        "- recommended_mainline: $($StateCards.topic_candidate_packet.recommended_mainline)",
        "- alternative_mainline: $($StateCards.topic_candidate_packet.alternative_mainline)",
        "- next_action: $($StateCards.topic_candidate_packet.next_action)",
        "",
        "## supporting_points"
    )
    foreach ($item in @($StateCards.topic_candidate_packet.supporting_points)) { $topicLines += "- $item" }
    $topicLines += ""
    $topicLines += "## outline_seed"
    foreach ($item in @($StateCards.topic_candidate_packet.outline_seed)) { $topicLines += "- $item" }
    $topicLines += ""
    $topicLines += "## current_gaps"
    foreach ($item in @($StateCards.topic_candidate_packet.current_gaps)) { $topicLines += "- $item" }
    Write-MarkdownFile -Path $topicCandidateMd -Lines $topicLines

    $topicConfirmationJson = Join-Path $cardsDir "topic_confirmation_card.json"
    $topicConfirmationMd = Join-Path $cardsDir "topic_confirmation_card.md"
    Write-JsonFile -Path $topicConfirmationJson -Payload $StateCards.topic_confirmation_card
    $topicConfirmationLines = @(
        "# topic_confirmation_card",
        "",
        "- status: $($StateCards.topic_confirmation_card.status)",
        "- recommended_mainline: $($StateCards.topic_confirmation_card.recommended_mainline)",
        "- can_enter_writing_contract: $($StateCards.topic_confirmation_card.can_enter_writing_contract)",
        "",
        "## blocked_by"
    )
    foreach ($item in @($StateCards.topic_confirmation_card.blocked_by)) { $topicConfirmationLines += "- $item" }
    Write-MarkdownFile -Path $topicConfirmationMd -Lines $topicConfirmationLines

    $themePolicyJson = Join-Path $cardsDir "theme_lock_policy_card.json"
    $themePolicyMd = Join-Path $cardsDir "theme_lock_policy_card.md"
    Write-JsonFile -Path $themePolicyJson -Payload $StateCards.theme_lock_policy_card
    $themeLines = @(
        "# theme_lock_policy_card",
        "",
        "- status: $($StateCards.theme_lock_policy_card.status)",
        "- selected_value: $($StateCards.theme_lock_policy_card.selected_value)",
        "- note: $($StateCards.theme_lock_policy_card.note)",
        "",
        "## allowed_values"
    )
    foreach ($item in @($StateCards.theme_lock_policy_card.allowed_values)) { $themeLines += "- $item" }
    Write-MarkdownFile -Path $themePolicyMd -Lines $themeLines

    return [pscustomobject][ordered]@{
        directory = $cardsDir
        task_brief_card = $taskBriefJson
        task_brief_card_md = $taskBriefMd
        genre_routing_card = $genreRoutingJson
        genre_routing_card_md = $genreRoutingMd
        sample_contract = $sampleContractJson
        sample_contract_md = $sampleContractMd
        topic_candidate_packet = $topicCandidateJson
        topic_candidate_packet_md = $topicCandidateMd
        topic_confirmation_card = $topicConfirmationJson
        topic_confirmation_card_md = $topicConfirmationMd
        theme_lock_policy_card = $themePolicyJson
        theme_lock_policy_card_md = $themePolicyMd
    }
}

function Write-WhiteboxSummary {
    param(
        [string]$Path,
        [object]$Contract
    )

    $lines = @(
        "# II期白盒编排摘要",
        "",
        "- 题目: $($Contract.candidate_id) / $($Contract.candidate_name)",
        "- 题型: $($Contract.case_type)",
        "- 状态: $($Contract.status)",
        "- 来源目录: $($Contract.source_root)",
        ""
    )

    $lines += "## 写作合同"
    $lines += ""
    $lines += "- 受众: $($Contract.writing_contract.audience)"
    $lines += "- 目标字数: $($Contract.writing_contract.target_word_count)"
    $lines += "- 写作目的: $($Contract.writing_contract.purpose)"
    if ($Contract.writing_contract.genre) {
        $lines += "- 体裁: $($Contract.writing_contract.genre)"
    }
    $mustFacts = @($Contract.writing_contract.must_include_facts)
    if ($mustFacts.Count -gt 0) {
        $lines += ""
        $lines += "### 必写事实"
        foreach ($fact in $mustFacts) {
            $lines += "- $fact"
        }
    }
    $reqStruct = @($Contract.writing_contract.required_structure)
    if ($reqStruct.Count -gt 0) {
        $lines += ""
        $lines += "### 必备结构"
        foreach ($sec in $reqStruct) {
            $lines += "- $sec"
        }
    }
    $lines += ""
    $lines += "## 输入边界"
    $lines += ""

    foreach ($rule in @($Contract.input_contract.allowed_inputs)) {
        $lines += "- 允许: $($rule.path) [$($rule.mode)]"
    }
    foreach ($rule in @($Contract.input_contract.forbidden_inputs)) {
        $lines += "- 禁止: $rule"
    }

    $referenceSample = $Contract.reference_sample_contract
    if ($referenceSample -and $referenceSample.declared_path) {
        $lines += ""
        $lines += "## 样稿变量"
        $lines += ""
        $lines += "- 声明路径: $($referenceSample.declared_path)"
        if ($referenceSample.resolved_path) {
            $lines += "- 解析路径: $($referenceSample.resolved_path)"
        }
        $lines += "- 是否存在: $($referenceSample.exists)"
        $lines += "- 是否冻结: $($referenceSample.frozen)"
        $lines += "- 出稿阶段请求放开: $($referenceSample.requested_for_draft)"
        $lines += "- 当前是否真正放开: $($referenceSample.enabled_for_draft)"
        if ($referenceSample.selection_owner) {
            $lines += "- 选择人: $($referenceSample.selection_owner)"
        }
        if ($referenceSample.visibility_stage) {
            $lines += "- 可见阶段: $($referenceSample.visibility_stage)"
        }
        if ($referenceSample.boundary) {
            $lines += "- 防泄露边界: $($referenceSample.boundary)"
        }
        $roles = @($referenceSample.roles)
        if ($roles.Count -gt 0) {
            $lines += "- 允许角色: $($roles -join ' / ')"
        }
    }

    $lines += ""
    $lines += "## 编排要求"
    $lines += ""
    $lines += "- 模式: $($Contract.orchestration_contract.route_profile.mode)"
    foreach ($step in @($Contract.orchestration_contract.route_profile.required_steps)) {
        $lines += "- 必做: $step"
    }
    foreach ($failure in @($Contract.orchestration_contract.route_profile.failure_modes)) {
        $lines += "- 风险: $failure"
    }

    $pseudoPoints = @($Contract.orchestration_contract.pseudo_load_bearing_points)
    if ($pseudoPoints.Count -gt 0) {
        $lines += ""
        $lines += "## 伪承重点"
        $lines += ""
        foreach ($point in $pseudoPoints) {
            $lines += "- $point"
        }
    }

    $manualGates = @($Contract.manual_gates)
    if ($manualGates.Count -gt 0) {
        $lines += ""
        $lines += "## 人工阻塞"
        $lines += ""
        foreach ($gate in $manualGates) {
            $lines += "- $gate"
        }
    }

    $fc = $Contract.formula_contract
    if ($fc) {
        $lines += ""
        $lines += "## 公式位合同"
        $lines += ""
        if ($fc.persona) { $lines += "- 人格: $($fc.persona)" }
        if ($fc.range) { $lines += "- 写作范围: $($fc.range)" }
        if ($fc.write_target) { $lines += "- 写作目标: $($fc.write_target)" }
        if ($fc.content_combo) { $lines += "- 内容组合: $($fc.content_combo)" }
        if ($fc.logic_combo) { $lines += "- 逻辑组合: $($fc.logic_combo)" }
        $eOutline = @($fc.effective_outline)
        if ($eOutline.Count -gt 0) {
            $lines += ""
            $lines += "### 有效大纲"
            foreach ($item in $eOutline) { $lines += "- $item" }
        }
        $ecu = @($fc.effective_content_unit)
        if ($ecu.Count -gt 0) {
            $lines += ""
            $lines += "### 有效内容单元"
            foreach ($item in $ecu) { $lines += "- $item" }
        }
    }

    Set-Content -LiteralPath $Path -Value $lines -Encoding UTF8
}

$poolData = Get-CandidatePoolData -Path $CandidatePool

if ($ListCandidates) {
    foreach ($candidate in $poolData.Pool.candidates) {
        Write-Output "$($candidate.id): [$($candidate.case_type)] $($candidate.status) - $($candidate.name)"
    }
    exit 0
}

if ([string]::IsNullOrWhiteSpace($CandidateId)) {
    throw "必须提供 -CandidateId，或使用 -ListCandidates。"
}

if (-not $poolData.CandidateMap.ContainsKey($CandidateId)) {
    $available = ($poolData.CandidateMap.Keys | Sort-Object) -join ", "
    throw "未知候选题: $CandidateId；可用值: $available"
}

$candidate = $poolData.CandidateMap[$CandidateId]
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$runDir = Join-Path $OutputRoot "${timestamp}_$($candidate.id)"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$contractPath = Join-Path $runDir "whitebox_contract.json"
$summaryPath = Join-Path $runDir "whitebox_summary.md"
$manifestPath = Join-Path $runDir "whitebox_manifest.json"

$contract = Build-WhiteboxContract -Candidate $candidate -CandidatePoolPath $poolData.Path -EnableReferenceSample:$EnableReferenceSample
Write-JsonFile -Path $contractPath -Payload $contract
$stateCards = Build-StateCards -Contract $contract
$stateCardManifest = Write-StateCards -RunDirectory $runDir -StateCards $stateCards
Write-WhiteboxSummary -Path $summaryPath -Contract $contract

$manifest = [pscustomobject][ordered]@{
    timestamp = $timestamp
    candidate_id = $candidate.id
    candidate_name = $candidate.name
    case_type = $candidate.case_type
    status = $contract.status
    exit_code = $contract.exit_code
    run_directory = $runDir
    contract = $contractPath
    summary = $summaryPath
    state_cards = $stateCardManifest
    candidate_pool = $poolData.Path
    enable_l1_writing_craft = [bool]$EnableL1WritingCraft
    l1_assets_path = $L1AssetsPath
}
Write-JsonFile -Path $manifestPath -Payload $manifest

Write-Host "[INFO] 白盒摘要: $summaryPath"
Write-Host "[INFO] 白盒清单: $manifestPath"

exit $contract.exit_code
