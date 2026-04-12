param(
    [Parameter(Mandatory = $true)]
    [string]$PhaseRunDir,
    [string]$OutputDir = "D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\07_白盒施工包\01_第一轮白盒完整可实验版\02_单题全貌档案"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Read-TextFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8
}

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Add-Line {
    param(
        [Parameter(Mandatory = $true)][object]$Lines,
        [Parameter(Mandatory = $true)][string]$Text
    )
    [void]([System.Collections.Generic.List[string]]$Lines).Add($Text)
}

function Add-Blank {
    param([Parameter(Mandatory = $true)][object]$Lines)
    [void]([System.Collections.Generic.List[string]]$Lines).Add("")
}

function Add-MultiLineText {
    param(
        [Parameter(Mandatory = $true)][object]$Lines,
        [AllowEmptyString()][string]$Text
    )

    if ([string]::IsNullOrEmpty($Text)) {
        [void]([System.Collections.Generic.List[string]]$Lines).Add("")
        return
    }

    $normalized = $Text -replace "`r`n", "`n" -replace "`r", "`n"
    foreach ($line in ($normalized -split "`n")) {
        [void]([System.Collections.Generic.List[string]]$Lines).Add($line)
    }
}

function Join-ListInline {
    param([object[]]$Items)
    if ($null -eq $Items -or @($Items).Count -eq 0) {
        return "无"
    }
    return (@($Items) -join "；")
}

function Get-CaseFileName {
    param([string]$CandidateId)
    switch ($CandidateId) {
        "lecanemab_patient" { return "01_lecanemab_patient.md" }
        "lecanemab_mechanism" { return "02_lecanemab_mechanism.md" }
        "lecanemab_news" { return "03_lecanemab_news.md" }
        default { return "$CandidateId.md" }
    }
}

function Get-CaseHumanSummary {
    param(
        [Parameter(Mandatory = $true)]$Contract,
        [Parameter(Mandatory = $true)]$Materials,
        [Parameter(Mandatory = $true)]$Score
    )

    $sources = @($Materials.items | ForEach-Object { Split-Path -Leaf $_.resolved_path })
    $facts = @($Contract.writing_contract.must_include_facts)
    $issues = @($Score.blocking_issues)
    $missing = @($Score.missing_or_misaligned)
    $noise = if (@($Materials.items | Where-Object { $_.extension -eq ".pdf" }).Count -gt 0) {
        "原始材料实际来自 PDF 全文提取，存在学术论文式表达、页眉页脚和图表上下文断裂等噪声。"
    }
    else {
        "本轮材料噪声较低。"
    }

    return [pscustomobject]@{
        source_files = $sources
        main_facts = $facts
        issues = $issues
        missing = $missing
        noise = $noise
    }
}

function Get-DimensionReasonMap {
    param([Parameter(Mandatory = $true)]$Score)

    $map = @{}
    foreach ($dimension in @($Score.dimensions)) {
        $map[$dimension.id] = $dimension
    }
    return $map
}

function Add-CodeBlock {
    param(
        [Parameter(Mandatory = $true)][object]$Lines,
        [Parameter(Mandatory = $true)][string]$InfoString,
        [AllowEmptyString()][string]$Content
    )

    Add-Line -Lines $Lines -Text ('```' + $InfoString)
    Add-MultiLineText -Lines $Lines -Text $Content
    Add-Line -Lines $Lines -Text '```'
}

function Build-Fullview {
    param(
        [Parameter(Mandatory = $true)][string]$ContractDir,
        [Parameter(Mandatory = $true)][string]$OutPath
    )

    $contract = Read-JsonFile -Path (Join-Path $ContractDir "whitebox_contract.json")
    $whiteboxManifest = Read-JsonFile -Path (Join-Path $ContractDir "whitebox_manifest.json")
    $materials = Read-JsonFile -Path (Join-Path $ContractDir "materials\materials_manifest.json")
    $summary = Read-JsonFile -Path (Join-Path $ContractDir "summary.json")
    $score = Read-JsonFile -Path (Join-Path $ContractDir "score.json")
    $reviewBundle = Read-JsonFile -Path (Join-Path $ContractDir "review_bundle.json")
    $taskDetail = Read-JsonFile -Path (Join-Path $ContractDir "task_detail.json")

    $writingSystemPrompt = Read-TextFile -Path (Join-Path $ContractDir "writing_system_prompt.txt")
    $writingUserPrompt = Read-TextFile -Path (Join-Path $ContractDir "writing_user_prompt.txt")
    $generated = Read-TextFile -Path (Join-Path $ContractDir "generated.txt")

    $materialSummary = Get-CaseHumanSummary -Contract $contract -Materials $materials -Score $score
    $dimMap = Get-DimensionReasonMap -Score $score

    $reviewPriorities = if (@($score.blocking_issues).Count -gt 0) {
        @($score.blocking_issues | Select-Object -First 3)
    }
    else {
        @($score.missing_or_misaligned | Select-Object -First 3)
    }

    $nextActions = @($score.next_actions | Select-Object -First 5)
    $firstNextAction = if ($nextActions.Count -gt 0) { $nextActions[0] } else { "当前无额外建议" }
    $stateCardsDir = $whiteboxManifest.state_cards.directory
    $currentJudgment = if ($summary.qualified) {
        "当前白盒评分为 $($summary.weighted_total) 分，达到白盒当前合格线；但这仍只代表本轮白盒评分通过，不等于最终阶段收口。"
    }
    else {
        "当前白盒评分为 $($summary.weighted_total) 分，未达白盒当前合格线；当前问题不在入口链路，而在合同、材料和成稿的对齐。"
    }

    $lines = [System.Collections.Generic.List[string]]::new()
    Add-Line -Lines $lines -Text "# $($contract.candidate_name)（白盒第一轮单题全貌）"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "状态：白盒第一轮实验运行结果"
    Add-Line -Lines $lines -Text "日期：2026-04-11"
    Add-Line -Lines $lines -Text "用途：人工审核第一读物。本文只认本轮白盒 runtime 直证，不让人工去翻工程清单。"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "## 当前有效口径"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "1. 当前单题口径只认本轮白盒 phase run 的直接证据：合同、取材、提示词、生成稿、评分与回指。"
    Add-Line -Lines $lines -Text '2. 本文是白盒第一轮实验结果，不替代旧 `IIIA/06_单题全貌档案` 的历史 run 记录，也不把白盒评分直接冒充为阶段最终裁定。'
    Add-Line -Lines $lines -Text '3. 当前最重要的阅读目标只有一个：看清模型看到了什么、被怎样约束、最终写歪在什么层。'
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('case_id: ``{0}``' -f $contract.candidate_id)
    Add-Line -Lines $lines -Text 'task_id: ``本轮白盒无后端 task_id``'
    Add-Line -Lines $lines -Text ('run_dir: ``{0}``' -f $ContractDir)
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "## 当前明确缺项"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "1. 独立 planning prompt：本轮不存在；原因：白盒当前在合同层完成上游约束，不单独落 planning prompt 文件。"
    Add-Line -Lines $lines -Text '2. 独立 quality prompt：本轮不存在；原因：白盒当前直接落 `score_prompt.md`，不单独命名为 quality prompt。'
    Add-Line -Lines $lines -Text '3. 后端 `task_id / delivery docx`：本轮不存在；原因：当前是白盒批跑，不走旧后端任务对象和 delivery 链。'
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "## 主阅读层"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 一、人工审核先看"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. 写作合同：写给 `{0}`，目标字数 `{1}`，稿型 `{2}`，本轮目的为：{3}' -f $contract.writing_contract.audience, $contract.writing_contract.target_word_count, $contract.writing_contract.genre, $contract.writing_contract.purpose)
    Add-Line -Lines $lines -Text ("2. 当前判定：{0}" -f $currentJudgment)
    Add-Line -Lines $lines -Text ("3. 审稿优先看：{0}" -f (Join-ListInline -Items $reviewPriorities))
    Add-Line -Lines $lines -Text ("4. 当前最该改：{0}" -f $firstNextAction)
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 二、本轮真正喂给写手的材料（人工整理版）"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "人工阅读提示："
    Add-Line -Lines $lines -Text ("1. 本轮实际材料来源文件：{0}" -f (Join-ListInline -Items $materialSummary.source_files))
    Add-Line -Lines $lines -Text ("2. 白盒合同要求优先承重的事实：{0}" -f (Join-ListInline -Items $materialSummary.main_facts))
    Add-Line -Lines $lines -Text ("3. 材料噪声：{0}" -f $materialSummary.noise)
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "实际入模材料整理稿："
    $materialsDigest = @(
        "这题本轮白盒允许材料共 $($materials.total_items) 份，可提取材料 $($materials.extractable_count) 份。",
        "主承重事实按白盒合同冻结为：$((@($materialSummary.main_facts) -join '；'))。",
        "材料来源依次为：$((@($materialSummary.source_files) -join '；'))。",
        "材料整理原则：不是按论文页码罗列，而是只把当前稿件应承重的核心事实压给写手。",
        "噪声说明：$($materialSummary.noise)"
    ) -join "`r`n"
    Add-CodeBlock -Lines $lines -InfoString "text" -Content $materialsDigest
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 三、本轮给模型的 prompt 全文"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "system prompt："
    Add-CodeBlock -Lines $lines -InfoString "text" -Content $writingSystemPrompt
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "user prompt："
    Add-CodeBlock -Lines $lines -InfoString "text" -Content $writingUserPrompt
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 四、当前稿件全文"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "1. 生成稿全文（必须直接贴入，不得只写路径）："
    Add-CodeBlock -Lines $lines -InfoString "text" -Content $generated
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 五、当前审核意见与返修抓手"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. 总分与当前判定：`{0}` 分；`qualified={1}`；白盒 review_bundle 已落盘。' -f $score.weighted_total, $score.qualified.ToString().ToLower())
    Add-Line -Lines $lines -Text "2. 各维度关键失分："
    foreach ($dimension in @($score.dimensions)) {
        Add-Line -Lines $lines -Text ('   - `{0}`：{1}' -f $dimension.id, $dimension.reason)
    }
    Add-Line -Lines $lines -Text "3. 返修抓手："
    foreach ($action in $nextActions) {
        Add-Line -Lines $lines -Text ("   - {0}" -f $action)
    }
    Add-Line -Lines $lines -Text "4. 人工审核时的重点对照项："
    Add-Line -Lines $lines -Text ('   - 合同主线是否真的被成稿贯彻：`{0}`' -f $contract.writing_contract.purpose)
    Add-Line -Lines $lines -Text ('   - 必写事实是否都在正文真正落句：{0}' -f (Join-ListInline -Items $contract.writing_contract.must_include_facts))
    Add-Line -Lines $lines -Text ('   - 评分回指当前最重的问题：{0}' -f (Join-ListInline -Items $reviewPriorities))
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "## 工程附录"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### Runtime 指针"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. `run_summary.md`：本轮白盒不存在；对应批量摘要为 `{0}`' -f (Join-Path $PhaseRunDir "phase_summary.md"))
    Add-Line -Lines $lines -Text ('2. `task_detail.json`：`{0}`' -f (Join-Path $ContractDir "task_detail.json"))
    Add-Line -Lines $lines -Text ('3. `generated.txt`：`{0}`' -f (Join-Path $ContractDir "generated.txt"))
    Add-Line -Lines $lines -Text ('4. `materials_full.json`：`{0}`' -f (Join-Path $ContractDir "materials_full.json"))
    Add-Line -Lines $lines -Text ('5. `review_bundle.json`：`{0}`' -f (Join-Path $ContractDir "review_bundle.json"))
    Add-Line -Lines $lines -Text ('6. `score.json`：`{0}`' -f (Join-Path $ContractDir "score.json"))
    Add-Line -Lines $lines -Text ('7. `summary.json`：`{0}`' -f (Join-Path $ContractDir "summary.json"))
    Add-Line -Lines $lines -Text ('8. `writing_system_prompt.txt`：`{0}`' -f (Join-Path $ContractDir "writing_system_prompt.txt"))
    Add-Line -Lines $lines -Text ('9. `writing_user_prompt.txt`：`{0}`' -f (Join-Path $ContractDir "writing_user_prompt.txt"))
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 本轮关键证据"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. 上传与 evidence：当前白盒不走旧 upload 任务对象；证据直接来自 `{0}` 中允许的输入文件。' -f $contract.source_root)
    Add-Line -Lines $lines -Text ('2. 阶段到达情况：`contract_ready={0}` `materials_ready={1}` `draft_ready={2}` `scoring_ready={3}` `review_bundle_ready={4}`' -f $taskDetail.stages.contract_ready, $taskDetail.stages.materials_ready, $taskDetail.stages.draft_ready, $taskDetail.stages.scoring_ready, $taskDetail.stages.review_bundle_ready)
    Add-Line -Lines $lines -Text ('3. 交付与评分：本轮生成稿路径为 `{0}`，当前分数 `{1}`，达标结论 `{2}`。' -f $summary.generated_path, $summary.weighted_total, $summary.qualified)
    Add-Line -Lines $lines -Text ('4. planning / writing 卡片：本轮白盒上游状态卡目录为 `{0}`。' -f $stateCardsDir)
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### materials 指针"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. 当前人工审稿材料文件：`{0}`' -f (Join-Path $ContractDir "materials_full.json"))
    Add-Line -Lines $lines -Text ('2. 同轮回退锚点：`{0}`' -f (Join-Path $ContractDir "materials\materials_digest.md"))
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### prompt 指针"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. system prompt：`{0}`' -f (Join-Path $ContractDir "writing_system_prompt.txt"))
    Add-Line -Lines $lines -Text ('2. user prompt：`{0}`' -f (Join-Path $ContractDir "writing_user_prompt.txt"))
    Add-Line -Lines $lines -Text ('3. 同轮回退锚点：`{0}`' -f (Join-Path $ContractDir "draft_prompt.md"))
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 评分结果"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. 总分：`{0}`' -f $score.weighted_total)
    Add-Line -Lines $lines -Text ('2. 达标结论：`{0}`' -f $score.qualified)
    Add-Line -Lines $lines -Text ('3. 评分状态：`{0}`' -f $summary.task_status)
    Add-Line -Lines $lines -Text "4. 各维度："
    Add-Line -Lines $lines -Text ('   - `任务完成度`：{0}' -f $dimMap["route_alignment"].reason)
    Add-Line -Lines $lines -Text ('   - `关键事实与关键数字覆盖`：{0}' -f $dimMap["key_facts"].reason)
    Add-Line -Lines $lines -Text ('   - `受众匹配与文风匹配`：{0}' -f $dimMap["audience_style"].reason)
    Add-Line -Lines $lines -Text '   - `AI味儿控制`：本轮白盒未单独拆出 AI 味儿维度；当前主要参考 `audience_style`、`formula_compliance` 与 `writing_strength` 回指。'
    Add-Line -Lines $lines -Text ('   - `结构与信息取舍`：{0}' -f $dimMap["structure"].reason)
    Add-Line -Lines $lines -Text '   - `标题角度与稿型适配`：本轮白盒未单独拆出标题维度；当前主要参考 `route_alignment` 与 `formula_trace` 中的稿型偏移判断。'
    Add-Line -Lines $lines -Text ('   - `幻觉与越界编造控制`：{0}' -f $dimMap["hallucination_control"].reason)
    Add-Line -Lines $lines -Text "5. 本轮已执行评分。"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 本轮真实 blocker"
    Add-Blank -Lines $lines
    if (@($score.blocking_issues).Count -gt 0) {
        $index = 1
        foreach ($issue in @($score.blocking_issues)) {
            Add-Line -Lines $lines -Text ("{0}. {1}" -f $index, $issue)
            $index += 1
        }
    }
    else {
        Add-Line -Lines $lines -Text "1. 当前无链路级 blocker；当前主要问题已收缩到内容质量、公式位执行和稿型主线承重。"
    }
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text "### 证据摘要"
    Add-Blank -Lines $lines
    Add-Line -Lines $lines -Text ('1. 已直接核对：`{0}` 中 `task_status={1}`、`weighted_total={2}`、`qualified={3}`。' -f (Join-Path $ContractDir "summary.json"), $summary.task_status, $summary.weighted_total, $summary.qualified)
    Add-Line -Lines $lines -Text ('2. 已直接核对：`{0}` 已直接给出 blocking_issues / missing_or_misaligned / backtrace，可回指失配层。' -f (Join-Path $ContractDir "review_bundle.json"))
    Add-Line -Lines $lines -Text ('3. 已直接核对：`{0}` 与 `generated.txt` 同轮存在，人工可直接看模型被怎样约束、最终写成什么。' -f (Join-Path $ContractDir "writing_user_prompt.txt"))

    $content = [string]::Join("`r`n", $lines)
    [System.IO.File]::WriteAllText($OutPath, $content, [System.Text.Encoding]::UTF8)
}

Ensure-Directory -Path $OutputDir
$phaseManifest = Read-JsonFile -Path (Join-Path $PhaseRunDir "phase_manifest.json")

foreach ($step in @($phaseManifest.steps)) {
    $filename = Get-CaseFileName -CandidateId $step.candidate_id
    $outPath = Join-Path $OutputDir $filename
    Build-Fullview -ContractDir $step.run_directory -OutPath $outPath
}

Write-Host "[INFO] whitebox fullviews generated: $OutputDir"
