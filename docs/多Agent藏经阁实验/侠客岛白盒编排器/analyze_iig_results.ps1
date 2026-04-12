param(
    [string]$RuntimeRoot = "D:\汇度编辑部1\侠客岛-runtime\ii_whitebox",
    [string]$OutputDir = "d:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\II期成果整理\IIG成果整理"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([string]$Path)
    [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
}

# ── 收集所有 IIG 运行数据 ──
$allRuns = @()
$dirs = Get-ChildItem $RuntimeRoot -Directory | Where-Object { $_.Name -match "_iig[14]_?[abc]?$" } | Sort-Object Name

foreach ($dir in $dirs) {
    $scorePath = Join-Path $dir.FullName "score.json"
    $reviseManifestPath = Join-Path $dir.FullName "revise_manifest.json"
    if (-not (Test-Path $scorePath)) { continue }

    $score = Read-JsonFile -Path $scorePath
    $reviseManifest = if (Test-Path $reviseManifestPath) { Read-JsonFile -Path $reviseManifestPath } else { $null }

    # 优先使用 revise_manifest 中的 best_score_achieved（最佳分数）
    # 回退到 score.json 中的 weighted_total（可能是最后一轮而非最佳轮）
    $effectiveTotal = if ($reviseManifest -and $reviseManifest.best_score_achieved) {
        [double]$reviseManifest.best_score_achieved
    } else {
        [double]$score.weighted_total
    }

    # 尝试找到最佳轮次的 score.json 以获取准确的 writing_strength
    if ($reviseManifest -and $reviseManifest.best_score_achieved) {
        $bestRound = $reviseManifest.rounds | Where-Object { $_.PSObject.Properties.Name -contains "score_after" -and $_.score_after -eq $reviseManifest.best_score_achieved } | Select-Object -First 1
        if ($bestRound) {
            $bestRoundScorePath = Join-Path $dir.FullName "revise\round_$($bestRound.round)\score.json"
            if (Test-Path $bestRoundScorePath) {
                $score = Read-JsonFile -Path $bestRoundScorePath
            }
        }
    }
    
    # Parse arm from directory name
    $arm = ""
    if ($dir.Name -match "_iig1_a$") { $arm = "iig1_a" }
    elseif ($dir.Name -match "_iig1_b$") { $arm = "iig1_b" }
    elseif ($dir.Name -match "_iig1_c$") { $arm = "iig1_c" }
    elseif ($dir.Name -match "_iig4$") { $arm = "iig4" }
    else { continue }

    # Parse candidate ID
    $candidateId = ""
    if ($dir.Name -match "\d{8}_\d{6}_\d{3}_(.+)_iig") {
        $candidateId = $matches[1]
    }

    # Extract writing_strength
    $ws = @{}
    if ($score.writing_strength) {
        foreach ($item in @($score.writing_strength)) {
            $ws[$item.id] = $item.score
        }
    }

    $allRuns += [pscustomobject][ordered]@{
        arm = $arm
        candidate_id = $candidateId
        directory = $dir.FullName
        weighted_total = $effectiveTotal
        qualified = $score.qualified
        route_alignment = if ($score.dimensions) { ($score.dimensions | Where-Object { $_.id -eq "route_alignment" }).score } else { $null }
        key_facts = if ($score.dimensions) { ($score.dimensions | Where-Object { $_.id -eq "key_facts" }).score } else { $null }
        audience_style = if ($score.dimensions) { ($score.dimensions | Where-Object { $_.id -eq "audience_style" }).score } else { $null }
        structure = if ($score.dimensions) { ($score.dimensions | Where-Object { $_.id -eq "structure" }).score } else { $null }
        hallucination_control = if ($score.dimensions) { ($score.dimensions | Where-Object { $_.id -eq "hallucination_control" }).score } else { $null }
        formula_compliance = $score.formula_compliance
        ws_opening_hook = $ws["opening_hook"]
        ws_transition_flow = $ws["transition_flow"]
        ws_midgame_drive = $ws["midgame_drive"]
        ws_closing_tension = $ws["closing_tension"]
        ws_anchor_fidelity = $ws["anchor_fidelity"]
        best_score = if ($reviseManifest) { $reviseManifest.best_score_achieved } else { $null }
        actual_rounds = if ($reviseManifest) { $reviseManifest.actual_rounds } else { $null }
    }
}

Write-Host "收集到 $($allRuns.Count) 个有效运行"

$armA = @($allRuns | Where-Object { $_.arm -eq "iig1_a" })
$armB = @($allRuns | Where-Object { $_.arm -eq "iig1_b" })
$armC = @($allRuns | Where-Object { $_.arm -eq "iig1_c" })
$iig4 = @($allRuns | Where-Object { $_.arm -eq "iig4" })

Write-Host "A 臂: $($armA.Count) | B 臂: $($armB.Count) | C 臂: $($armC.Count) | IIG-4: $($iig4.Count)"

function Get-Mean { param([double[]]$Values) if ($Values.Count -eq 0) { return 0 } return [Math]::Round(($Values | Measure-Object -Average).Average, 2) }
function Get-StdDev { param([double[]]$Values) if ($Values.Count -le 1) { return 0 }; $m = ($Values | Measure-Object -Average).Average; $v = ($Values | ForEach-Object { ($_ - $m) * ($_ - $m) } | Measure-Object -Sum).Sum / ($Values.Count - 1); return [Math]::Round([Math]::Sqrt($v), 2) }

$meanA = Get-Mean ($armA.weighted_total)
$meanB = Get-Mean ($armB.weighted_total)
$meanC = Get-Mean ($armC.weighted_total)
$mean4 = Get-Mean ($iig4.weighted_total)
$sdA = Get-StdDev ($armA.weighted_total)
$sdB = Get-StdDev ($armB.weighted_total)
$sdC = Get-StdDev ($armC.weighted_total)
$sd4 = Get-StdDev ($iig4.weighted_total)

$deltaBA = [Math]::Round($meanB - $meanA, 2)
$deltaCB = [Math]::Round($meanC - $meanB, 2)
$deltaCA = [Math]::Round($meanC - $meanA, 2)

# ── 1. IIG_公式因果性结论.md ──
$formulaVerdict = if ($deltaBA -ge 5) { "成立" } else { "不成立" }
$formulaLines = @(
    "# IIG 公式因果性结论（B vs A）",
    "",
    "日期：$(Get-Date -Format 'yyyy-MM-dd')",
    "对照：IIG-1 B 臂（8公式+样稿+revise）vs A 臂（无公式+样稿+revise）",
    "样本量：各 $($armA.Count) 题",
    "",
    "## 数据汇总",
    "",
    "| 臂 | 均值 | 标准差 | 样本量 |",
    "|-----|------|--------|--------|",
    "| A（基线） | $meanA | $sdA | $($armA.Count) |",
    "| B（8公式） | $meanB | $sdB | $($armB.Count) |",
    "| **Δ (B-A)** | **$deltaBA** | — | — |",
    "",
    "## 逐题对比",
    "",
    "| # | 候选 ID | A 分数 | B 分数 | Δ | B胜? |",
    "|---|---------|--------|--------|---|------|"
)
$bWinCount = 0
for ($i = 0; $i -lt $armA.Count; $i++) {
    $a = $armA[$i]; $b = $armB | Where-Object { $_.candidate_id -eq $a.candidate_id } | Select-Object -First 1
    if ($b) {
        $d = [Math]::Round($b.weighted_total - $a.weighted_total, 1)
        $win = if ($d -gt 0) { "✓"; $bWinCount++ } else { "✗" }
        $formulaLines += "| $($i+1) | $($a.candidate_id) | $($a.weighted_total) | $($b.weighted_total) | $d | $win |"
    }
}
$formulaLines += @(
    "",
    "## 判定",
    "",
    "- 阈值：Δ ≥ 5 分",
    "- 实测 Δ = $deltaBA",
    "- B 胜场数：$bWinCount / $($armA.Count)",
    "- **结论：8公式因果性 $formulaVerdict**",
    "",
    "## 与 IIF 对比",
    "",
    "- IIF-1 Δ = +3.33（3 题，不成立）",
    "- IIG-1 Δ = $deltaBA（$($armA.Count) 题，$formulaVerdict）",
    "- $(if ($formulaVerdict -eq '不成立') { '扩样后结论未翻转，公式因果性仍不成立。' } else { '扩样后结论翻转，公式因果性成立。' })"
)
Set-Content -LiteralPath (Join-Path $OutputDir "IIG_公式因果性结论.md") -Value $formulaLines -Encoding UTF8
Write-Host "✓ IIG_公式因果性结论.md"

# ── 2. IIG_L1增量结论.md ──
# Check writing_strength improvements
$wsImproved = 0
$wsDims = @("ws_opening_hook", "ws_transition_flow", "ws_midgame_drive", "ws_closing_tension", "ws_anchor_fidelity")
$wsCompare = @()
foreach ($dim in $wsDims) {
    $bMean = Get-Mean @($armB | ForEach-Object { [double]$_.$dim })
    $cMean = Get-Mean @($armC | ForEach-Object { [double]$_.$dim })
    $delta = [Math]::Round($cMean - $bMean, 2)
    if ($delta -gt 0) { $wsImproved++ }
    $wsCompare += [pscustomobject]@{ dim = $dim.Replace("ws_", ""); b_mean = $bMean; c_mean = $cMean; delta = $delta }
}
$l1Verdict = if ($deltaCB -ge 3 -and $wsImproved -ge 2) { "成立" } else { "不成立" }
$l1Lines = @(
    "# IIG L1 增量结论（C vs B）",
    "",
    "日期：$(Get-Date -Format 'yyyy-MM-dd')",
    "对照：IIG-1 C 臂（8公式+L1+revise）vs B 臂（8公式+revise）",
    "样本量：各 $($armB.Count) 题",
    "",
    "## 主表数据",
    "",
    "| 臂 | 均值 | 标准差 |",
    "|-----|------|--------|",
    "| B（8公式） | $meanB | $sdB |",
    "| C（8公式+L1） | $meanC | $sdC |",
    "| **Δ (C-B)** | **$deltaCB** | — |",
    "",
    "## 写作力副表对比",
    "",
    "| 维度 | B 均值 | C 均值 | Δ | C优? |",
    "|------|--------|--------|---|------|"
)
foreach ($w in $wsCompare) {
    $win = if ($w.delta -gt 0) { "✓" } else { "✗" }
    $l1Lines += "| $($w.dim) | $($w.b_mean) | $($w.c_mean) | $($w.delta) | $win |"
}
$l1Lines += @(
    "",
    "## 判定",
    "",
    "- 主表阈值：Δ ≥ 3 分",
    "- 副表阈值：writing_strength 至少 2 维提升",
    "- 实测主表 Δ = $deltaCB",
    "- 副表提升维度数：$wsImproved / 5",
    "- **结论：L1 增量 $l1Verdict**"
)
Set-Content -LiteralPath (Join-Path $OutputDir "IIG_L1增量结论.md") -Value $l1Lines -Encoding UTF8
Write-Host "✓ IIG_L1增量结论.md"

# ── 3. IIG_叠加效应分析.md ──
$stackVerdict = if ($deltaCA -ge 8) { "成立" } else { "不成立" }
$stackLines = @(
    "# IIG 叠加效应分析（C vs A）",
    "",
    "日期：$(Get-Date -Format 'yyyy-MM-dd')",
    "对照：IIG-1 C 臂（8公式+L1）vs A 臂（基线）",
    "",
    "## 数据汇总",
    "",
    "| 臂 | 均值 | 标准差 |",
    "|-----|------|--------|",
    "| A（基线） | $meanA | $sdA |",
    "| C（8公式+L1） | $meanC | $sdC |",
    "| **Δ (C-A)** | **$deltaCA** | — |",
    "",
    "## 增益拆解",
    "",
    "| 来源 | Δ |",
    "|------|---|",
    "| 公式增益 (B-A) | $deltaBA |",
    "| L1 增量 (C-B) | $deltaCB |",
    "| 叠加合计 (C-A) | $deltaCA |",
    "| 交互效应 | $([Math]::Round($deltaCA - $deltaBA - $deltaCB, 2)) |",
    "",
    "## 判定",
    "",
    "- 阈值：Δ ≥ 8 分",
    "- 实测 Δ = $deltaCA",
    "- **结论：叠加效应 $stackVerdict**"
)
Set-Content -LiteralPath (Join-Path $OutputDir "IIG_叠加效应分析.md") -Value $stackLines -Encoding UTF8
Write-Host "✓ IIG_叠加效应分析.md"

# ── 4. IIG_系统上限结论.md ──
$above85 = @($iig4 | Where-Object { $_.weighted_total -ge 85 }).Count
$above80 = @($iig4 | Where-Object { $_.weighted_total -ge 80 }).Count
$upliftVerdict = if (($mean4 - 76) -ge 5) { "L1 对上限有显著贡献" } else { "L1 对上限贡献有限" }
$ceilingLines = @(
    "# IIG 系统上限结论（IIG-4）",
    "",
    "日期：$(Get-Date -Format 'yyyy-MM-dd')",
    "配置：公式+样稿+revise+L1 全开，MaxRounds=10",
    "对标：IIF-4 均值=76.0",
    "",
    "## 数据汇总",
    "",
    "| 指标 | 数值 |",
    "|------|------|",
    "| 均值 | $mean4 |",
    "| 标准差 | $sd4 |",
    "| ≥85（可交付） | $above85 / $($iig4.Count) |",
    "| ≥80（接近可交付） | $above80 / $($iig4.Count) |",
    "| vs IIF-4 (76) 提升 | $([Math]::Round($mean4 - 76, 2)) |",
    "",
    "## 逐题明细",
    "",
    "| # | 候选 ID | 终态分数 | ≥85? | 实际轮次 |",
    "|---|---------|---------|------|---------|"
)
for ($i = 0; $i -lt $iig4.Count; $i++) {
    $r = $iig4[$i]
    $tag = if ($r.weighted_total -ge 85) { "✓" } elseif ($r.weighted_total -ge 80) { "~" } else { "✗" }
    $ceilingLines += "| $($i+1) | $($r.candidate_id) | $($r.weighted_total) | $tag | $($r.actual_rounds) |"
}
$ceilingLines += @(
    "",
    "## 判定",
    "",
    "- ≥85 可交付线：$above85 / $($iig4.Count) 题达标",
    "- ≥80 接近线：$above80 / $($iig4.Count) 题达标",
    "- vs IIF-4 提升：$([Math]::Round($mean4 - 76, 2)) 分",
    "- **结论：$upliftVerdict**"
)
Set-Content -LiteralPath (Join-Path $OutputDir "IIG_系统上限结论.md") -Value $ceilingLines -Encoding UTF8
Write-Host "✓ IIG_系统上限结论.md"

# ── 5. IIG_写作力副表分析.md ──
$wsLines = @(
    "# IIG 写作力副表分析",
    "",
    "日期：$(Get-Date -Format 'yyyy-MM-dd')",
    "",
    "## 三臂 + IIG-4 五维对比",
    "",
    "| 维度 | A 均值 | B 均值 | C 均值 | IIG-4 均值 | B-A | C-B | C-A |",
    "|------|--------|--------|--------|-----------|-----|-----|-----|"
)
foreach ($dim in $wsDims) {
    $dn = $dim.Replace("ws_", "")
    $aMean = Get-Mean @($armA | ForEach-Object { [double]$_.$dim })
    $bMean = Get-Mean @($armB | ForEach-Object { [double]$_.$dim })
    $cMean = Get-Mean @($armC | ForEach-Object { [double]$_.$dim })
    $i4Mean = Get-Mean @($iig4 | ForEach-Object { [double]$_.$dim })
    $wsLines += "| $dn | $aMean | $bMean | $cMean | $i4Mean | $([Math]::Round($bMean - $aMean, 2)) | $([Math]::Round($cMean - $bMean, 2)) | $([Math]::Round($cMean - $aMean, 2)) |"
}
$wsLines += @(
    "",
    "## 观察要点",
    "",
    "- opening_hook：L1 修辞积木中的「问题陈述」块能否改善开场",
    "- transition_flow：L1 表达库的过渡短语能否消除翻译腔过渡",
    "- midgame_drive：L1 语法戒律能否提升信息密度和推进感",
    "- closing_tension：L1 修辞积木中的「风险防守」块能否提升收尾",
    "- anchor_fidelity：不预期 L1 对此有影响（控制维度）"
)
Set-Content -LiteralPath (Join-Path $OutputDir "IIG_写作力副表分析.md") -Value $wsLines -Encoding UTF8
Write-Host "✓ IIG_写作力副表分析.md"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  所有结论文件已生成" -ForegroundColor Green
Write-Host "  输出目录: $OutputDir" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
