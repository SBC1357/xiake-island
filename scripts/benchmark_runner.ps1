param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$OutputDir = "D:\汇度编辑部1\侠客岛-runtime\benchmark_output",
    [string]$CasesConfig = "",
    [string[]]$CaseId,
    [switch]$SkipGenerate,
    [switch]$ListCases,
    [switch]$ListSuites,
    [string]$ScoringApiKey = "",
    [int]$MaxWaitSeconds = 3600,
    [int]$PollIntervalSeconds = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Net.Http

$script:HttpClient = $null

function ConvertFrom-JsonCompat {
    param([Parameter(ValueFromPipeline = $true)][string]$Text)

    process {
        if ($PSVersionTable.PSVersion.Major -ge 6) {
            return $Text | ConvertFrom-Json -Depth 100
        }
        return $Text | ConvertFrom-Json
    }
}

function Test-ObjectKey {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Key
    )

    if ($null -eq $Object) {
        return $false
    }

    if ($Object -is [System.Collections.IDictionary]) {
        return $Object.Contains($Key)
    }

    return $Object.PSObject.Properties.Name -contains $Key
}

function Get-ObjectValue {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Key
    )

    if ($null -eq $Object) {
        return $null
    }

    if ($Object -is [System.Collections.IDictionary]) {
        if ($Object.Contains($Key)) {
            return $Object[$Key]
        }
        return $null
    }

    if ($Object.PSObject.Properties.Name -contains $Key) {
        return $Object.$Key
    }

    return $null
}

function Get-AnthropicMessagesUrl {
    param([Parameter(Mandatory = $true)][string]$BaseUrl)

    $trimmed = $BaseUrl.TrimEnd('/')
    if ($trimmed -match '/v1$') {
        return "$trimmed/messages"
    }
    return "$trimmed/v1/messages"
}

function Get-DefaultOpencodeConfigPath {
    return "C:\Users\96138\.config\opencode\opencode.json"
}

function Load-RepoEnv {
    param([string]$EnvPath)

    if (-not (Test-Path -LiteralPath $EnvPath)) {
        return
    }

    foreach ($line in Get-Content -LiteralPath $EnvPath -Encoding UTF8) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line.TrimStart().StartsWith('#')) { continue }
        $eqIndex = $line.IndexOf('=')
        if ($eqIndex -lt 1) { continue }

        $key = $line.Substring(0, $eqIndex).Trim()
        $value = $line.Substring($eqIndex + 1).Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        if (-not [Environment]::GetEnvironmentVariable($key)) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

function Get-PreferredScoringConfig {
    $configPath = Get-DefaultOpencodeConfigPath
    if (-not (Test-Path -LiteralPath $configPath)) {
        return $null
    }

    $config = Read-JsonFile -Path $configPath
    if ($null -eq $config -or $null -eq $config.provider) {
        return $null
    }

    $candidates = @(
        @{ provider = "minimax"; model = "MiniMax-M2.5" },
        @{ provider = "volcengine-plan"; model = "kimi-k2.5" },
        @{ provider = "volcengine-plan"; model = "ark-code-latest" },
        @{ provider = "bailian-coding-plan"; model = "kimi-k2.5" },
        @{ provider = "bailian-coding-plan"; model = "glm-4.7" }
    )

    foreach ($candidate in $candidates) {
        if (-not (Test-ObjectKey -Object $config.provider -Key $candidate.provider)) {
            continue
        }

        $provider = Get-ObjectValue -Object $config.provider -Key $candidate.provider
        if ($null -eq $provider) {
            continue
        }

        $options = Get-ObjectValue -Object $provider -Key "options"
        $models = Get-ObjectValue -Object $provider -Key "models"
        if ($null -eq $options -or $null -eq $models) {
            continue
        }

        $baseUrl = Get-ObjectValue -Object $options -Key "baseURL"
        $apiKey = Get-ObjectValue -Object $options -Key "apiKey"
        if ([string]::IsNullOrWhiteSpace($baseUrl) -or [string]::IsNullOrWhiteSpace($apiKey)) {
            continue
        }

        if (-not (Test-ObjectKey -Object $models -Key $candidate.model)) {
            continue
        }

        $protocol = if (($baseUrl -match "/anthropic") -or ((Get-ObjectValue -Object $provider -Key "npm") -like "*anthropic*")) {
            "anthropic"
        } else {
            "openai"
        }

        return [pscustomobject]@{
            api_key = $apiKey
            base_url = $baseUrl
            model = $candidate.model
            protocol = $protocol
            source = "opencode:$($candidate.provider)/$($candidate.model)"
        }
    }

    return $null
}

function Build-ScoringProviderConfig {
    param(
        [string]$ApiKey,
        [string]$BaseUrl,
        [string]$Model,
        [string]$Protocol,
        [string]$Source
    )

    return [pscustomobject]@{
        api_key = $ApiKey
        base_url = $BaseUrl
        model = $Model
        protocol = $Protocol
        source = $Source
    }
}

function Get-ScoringConfigCandidates {
    param([string]$ScoringKey)

    $candidates = @()

    $preferred = Get-PreferredScoringConfig
    if ($null -ne $preferred) {
        $candidates += $preferred
    }

    if (-not [string]::IsNullOrWhiteSpace($ScoringKey)) {
        $candidates += Build-ScoringProviderConfig -ApiKey $ScoringKey `
            -BaseUrl $(if ($env:XIAGEDAO_LLM_BASE_URL) { $env:XIAGEDAO_LLM_BASE_URL } elseif ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL } else { "https://api.openai.com/v1" }) `
            -Model $(if ($env:XIAGEDAO_SCORING_MODEL) { $env:XIAGEDAO_SCORING_MODEL } elseif ($env:LLM_MODEL) { $env:LLM_MODEL } else { "gpt-4o" }) `
            -Protocol "openai" `
            -Source "override:ScoringApiKey"
    }

    if (-not [string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
        $candidates += Build-ScoringProviderConfig -ApiKey $env:OPENAI_API_KEY `
            -BaseUrl $(if ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL } elseif ($env:XIAGEDAO_LLM_BASE_URL) { $env:XIAGEDAO_LLM_BASE_URL } else { "https://api.openai.com/v1" }) `
            -Model $(if ($env:XIAGEDAO_SCORING_MODEL) { $env:XIAGEDAO_SCORING_MODEL } elseif ($env:LLM_MODEL) { $env:LLM_MODEL } else { "gpt-4o" }) `
            -Protocol "openai" `
            -Source "env:OPENAI_API_KEY"
    }
    elseif (-not [string]::IsNullOrWhiteSpace($env:XIAGEDAO_API_KEY)) {
        $candidates += Build-ScoringProviderConfig -ApiKey $env:XIAGEDAO_API_KEY `
            -BaseUrl $(if ($env:XIAGEDAO_LLM_BASE_URL) { $env:XIAGEDAO_LLM_BASE_URL } elseif ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL } else { "https://api.openai.com/v1" }) `
            -Model $(if ($env:XIAGEDAO_SCORING_MODEL) { $env:XIAGEDAO_SCORING_MODEL } elseif ($env:LLM_MODEL) { $env:LLM_MODEL } else { "gpt-4o" }) `
            -Protocol "openai" `
            -Source "env:XIAGEDAO_API_KEY"
    }

    if (-not [string]::IsNullOrWhiteSpace($env:ANTHROPIC_API_KEY)) {
        $candidates += Build-ScoringProviderConfig -ApiKey $env:ANTHROPIC_API_KEY `
            -BaseUrl $(if ($env:ANTHROPIC_BASE_URL) { $env:ANTHROPIC_BASE_URL } else { "https://api.anthropic.com/v1" }) `
            -Model $(if ($env:ANTHROPIC_MODEL) { $env:ANTHROPIC_MODEL } else { "claude-3-5-sonnet-latest" }) `
            -Protocol "anthropic" `
            -Source "env:ANTHROPIC_API_KEY"
    }

    $deduped = @{}
    $result = @()
    foreach ($item in $candidates) {
        $key = "$($item.api_key)|$($item.base_url)|$($item.model)|$($item.protocol)"
        if (-not $deduped.ContainsKey($key)) {
            $deduped[$key] = $true
            $result += $item
        }
    }

    return $result
}

function Get-ScoringDimensionMaps {
    $dimensionIdByName = @{}
    $dimensionNameById = @{}
    $dimensionWeightByKey = @{}

    foreach ($dimension in $scoringDimensions) {
        $dimensionIdByName[$dimension.name] = $dimension.id
        $dimensionNameById[$dimension.id] = $dimension.name
        $dimensionWeightByKey[$dimension.name] = [double]$dimension.weight
        $dimensionWeightByKey[$dimension.id] = [double]$dimension.weight
    }

    return [pscustomobject]@{
        id_by_name = $dimensionIdByName
        name_by_id = $dimensionNameById
        weight_by_key = $dimensionWeightByKey
    }
}

function Convert-ToNormalizedScoringDimensions {
    param([object]$Dimensions)

    $maps = Get-ScoringDimensionMaps
    $normalizedDimensions = @()

    foreach ($dimension in @($Dimensions)) {
        if ($null -eq $dimension) {
            continue
        }

        $dimensionId = if (Test-ObjectKey -Object $dimension -Key "id") {
            [string](Get-ObjectValue -Object $dimension -Key "id")
        } else { "" }
        $dimensionName = if (Test-ObjectKey -Object $dimension -Key "name") {
            [string](Get-ObjectValue -Object $dimension -Key "name")
        } else { "" }

        if ([string]::IsNullOrWhiteSpace($dimensionId) -and -not [string]::IsNullOrWhiteSpace($dimensionName) -and $maps.id_by_name.ContainsKey($dimensionName)) {
            $dimensionId = $maps.id_by_name[$dimensionName]
        }
        if ([string]::IsNullOrWhiteSpace($dimensionName) -and -not [string]::IsNullOrWhiteSpace($dimensionId) -and $maps.name_by_id.ContainsKey($dimensionId)) {
            $dimensionName = $maps.name_by_id[$dimensionId]
        }
        if ([string]::IsNullOrWhiteSpace($dimensionName)) {
            $dimensionName = $dimensionId
        }
        if ([string]::IsNullOrWhiteSpace($dimensionId)) {
            $dimensionId = $dimensionName
        }

        $dimensionWeight = 0.0
        if ((Test-ObjectKey -Object $dimension -Key "weight") -and $null -ne (Get-ObjectValue -Object $dimension -Key "weight")) {
            $dimensionWeight = [double](Get-ObjectValue -Object $dimension -Key "weight")
        }
        elseif ($maps.weight_by_key.ContainsKey($dimensionId)) {
            $dimensionWeight = $maps.weight_by_key[$dimensionId]
        }
        elseif ($maps.weight_by_key.ContainsKey($dimensionName)) {
            $dimensionWeight = $maps.weight_by_key[$dimensionName]
        }

        $normalizedDimensions += [ordered]@{
            id = $dimensionId
            name = $dimensionName
            weight = $dimensionWeight
            score = if ((Test-ObjectKey -Object $dimension -Key "score") -and $null -ne (Get-ObjectValue -Object $dimension -Key "score")) {
                [double](Get-ObjectValue -Object $dimension -Key "score")
            } else { 0 }
            reason = if ((Test-ObjectKey -Object $dimension -Key "reason") -and $null -ne (Get-ObjectValue -Object $dimension -Key "reason")) {
                [string](Get-ObjectValue -Object $dimension -Key "reason")
            } else { "" }
        }
    }

    return @($normalizedDimensions)
}

function Convert-ScoreMapToDimensions {
    param([object]$ScoresObject)

    if ($null -eq $ScoresObject) {
        return @()
    }

    $maps = Get-ScoringDimensionMaps
    $normalizedDimensions = @()
    foreach ($property in @($ScoresObject.PSObject.Properties)) {
        $dimensionKey = [string]$property.Name
        $rawDimension = $property.Value
        $dimensionId = if ($maps.id_by_name.ContainsKey($dimensionKey)) { $maps.id_by_name[$dimensionKey] } else { $dimensionKey }
        $dimensionName = if ($maps.name_by_id.ContainsKey($dimensionKey)) {
            $maps.name_by_id[$dimensionKey]
        }
        elseif ($maps.name_by_id.ContainsKey($dimensionId)) {
            $maps.name_by_id[$dimensionId]
        }
        else {
            $dimensionKey
        }

        $normalizedDimensions += [ordered]@{
            id = $dimensionId
            name = $dimensionName
            weight = if ($maps.weight_by_key.ContainsKey($dimensionId)) { $maps.weight_by_key[$dimensionId] } elseif ($maps.weight_by_key.ContainsKey($dimensionName)) { $maps.weight_by_key[$dimensionName] } else { 0 }
            score = if ($null -ne $rawDimension -and (Test-ObjectKey -Object $rawDimension -Key "score") -and $null -ne (Get-ObjectValue -Object $rawDimension -Key "score")) {
                [double](Get-ObjectValue -Object $rawDimension -Key "score")
            }
            else { 0 }
            reason = if ($null -ne $rawDimension -and (Test-ObjectKey -Object $rawDimension -Key "reason") -and $null -ne (Get-ObjectValue -Object $rawDimension -Key "reason")) {
                [string](Get-ObjectValue -Object $rawDimension -Key "reason")
            } else { "" }
        }
    }

    return @($normalizedDimensions)
}

function Resolve-QualifiedFlag {
    param([object]$Value)

    if ($Value -is [bool]) {
        return [bool]$Value
    }

    if ($null -eq $Value) {
        return $false
    }

    $text = ([string]$Value).Trim()
    return $text -in @("合格", "通过", "true", "True", "TRUE", "yes", "1")
}

function Apply-ScoringHardThresholds {
    param([object]$ScoreResult)

    if ($null -eq $ScoreResult) {
        return $ScoreResult
    }

    $violations = @()
    foreach ($dimension in @($ScoreResult.dimensions)) {
        if ($null -eq $dimension) {
            continue
        }

        $dimensionId = [string](Get-ObjectValue -Object $dimension -Key "id")
        if ([string]::IsNullOrWhiteSpace($dimensionId)) {
            continue
        }

        $dimensionSpec = @($scoringDimensions | Where-Object { $_.id -eq $dimensionId } | Select-Object -First 1)
        if ($dimensionSpec.Count -eq 0) {
            continue
        }
        $dimensionSpec = $dimensionSpec[0]
        if (-not (Test-ObjectKey -Object $dimensionSpec -Key "hard_threshold")) {
            continue
        }

        $threshold = [double]$dimensionSpec.hard_threshold
        $score = 0
        if (Test-ObjectKey -Object $dimension -Key "score") {
            $rawScore = Get-ObjectValue -Object $dimension -Key "score"
            if ($null -ne $rawScore) {
                $score = [double]$rawScore
            }
        }

        if ($score -lt $threshold) {
            $violations += "$dimensionId=$score<$threshold"
        }
    }

    if ($violations.Count -eq 0) {
        return $ScoreResult
    }

    $ScoreResult["qualified"] = $false
    $violationReason = "硬门槛未通过：" + ($violations -join "；")
    $existingReason = $null
    if (Test-ObjectKey -Object $ScoreResult -Key "disqualify_reason") {
        $existingReason = Get-ObjectValue -Object $ScoreResult -Key "disqualify_reason"
    }

    if ([string]::IsNullOrWhiteSpace([string]$existingReason)) {
        $ScoreResult["disqualify_reason"] = $violationReason
    }
    elseif ([string]$existingReason -like "*$violationReason*") {
        $ScoreResult["disqualify_reason"] = [string]$existingReason
    }
    else {
        $ScoreResult["disqualify_reason"] = ([string]$existingReason).TrimEnd() + "；" + $violationReason
    }

    return $ScoreResult
}

function Complete-ScoringDimensions {
    param([object]$Dimensions)

    $normalizedInput = @(Convert-ToNormalizedScoringDimensions -Dimensions $Dimensions)
    if ($normalizedInput.Count -eq 0) {
        return @()
    }

    $byId = @{}
    foreach ($dimension in @($normalizedInput)) {
        $dimensionId = [string](Get-ObjectValue -Object $dimension -Key "id")
        if (-not [string]::IsNullOrWhiteSpace($dimensionId)) {
            $byId[$dimensionId] = $dimension
        }
    }

    $shouldInjectAiFlavor = ($normalizedInput.Count -ge ($scoringDimensions.Count - 1)) -and
        (-not $byId.ContainsKey("ai_flavor_control")) -and
        $byId.ContainsKey("audience_style")

    $orderedDimensions = @()
    foreach ($expected in $scoringDimensions) {
        if ($byId.ContainsKey($expected.id)) {
            $orderedDimensions += $byId[$expected.id]
            continue
        }

        if ($shouldInjectAiFlavor -and $expected.id -eq "ai_flavor_control") {
            $source = $byId["audience_style"]
            $orderedDimensions += [ordered]@{
                id = $expected.id
                name = $expected.name
                weight = [double]$expected.weight
                score = if (Test-ObjectKey -Object $source -Key "score") { [double](Get-ObjectValue -Object $source -Key "score") } else { 0 }
                reason = "评分模型未单列 AI味儿 控制，当前沿用 audience_style 判语拆分；原始判语：$([string](Get-ObjectValue -Object $source -Key 'reason'))"
                derived_from = "audience_style"
            }
        }
    }

    foreach ($dimension in @($normalizedInput)) {
        $dimensionId = [string](Get-ObjectValue -Object $dimension -Key "id")
        $alreadyIncluded = @($orderedDimensions | Where-Object { [string](Get-ObjectValue -Object $_ -Key "id") -eq $dimensionId }).Count -gt 0
        if (-not $alreadyIncluded) {
            $orderedDimensions += $dimension
        }
    }

    return @($orderedDimensions)
}

function Get-ScoringFieldMappingZh {
    return [ordered]@{
        weighted_total = "总分"
        qualified = "达标结论"
        disqualify_reason = "不达标原因"
        dimensions = "评分维度原始列表"
        task_completion = "任务完成度"
        key_facts = "关键事实与关键数字覆盖"
        audience_style = "受众匹配与文风匹配"
        ai_flavor_control = "AI味儿控制"
        structure = "结构与信息取舍"
        title_angle = "标题角度与稿型适配"
        hallucination_control = "幻觉与越界编造控制"
        review_bundle_ready = "审稿包已齐"
        supplement_upload_failures = "补充材料上传失败列表"
    }
}

function Get-SummaryFieldMappingZh {
    return [ordered]@{
        id = "题号"
        name = "题目名称"
        task_id = "任务ID"
        generated_length = "生成稿字数"
        gold_length = "金标稿字数"
        weighted_total = "总分"
        qualified = "达标结论"
        scoring_status = "评分状态"
        review_bundle_ready = "审稿包已齐"
    }
}

function Get-QualifiedDisplayLabel {
    param([object]$ScoreResult)

    $dimensions = @(Get-ObjectValue -Object $ScoreResult -Key "dimensions")
    $environmentError = (Test-ObjectKey -Object $ScoreResult -Key "environment_error") -and
        (-not [string]::IsNullOrWhiteSpace([string](Get-ObjectValue -Object $ScoreResult -Key "environment_error")))

    if ($environmentError -or $dimensions.Count -eq 0) {
        return "未判定"
    }

    if (Resolve-QualifiedFlag -Value (Get-ObjectValue -Object $ScoreResult -Key "qualified")) {
        return "达标"
    }

    return "不达标"
}

function Build-ScoringDisplayZh {
    param([object]$ScoreResult)

    $displayDimensions = @()
    foreach ($dimension in @(Get-ObjectValue -Object $ScoreResult -Key "dimensions")) {
        if ($null -eq $dimension) {
            continue
        }

        $displayItem = [ordered]@{
            id = [string](Get-ObjectValue -Object $dimension -Key "id")
            名称 = if (Test-ObjectKey -Object $dimension -Key "name") { [string](Get-ObjectValue -Object $dimension -Key "name") } else { [string](Get-ObjectValue -Object $dimension -Key "id") }
            权重 = if (Test-ObjectKey -Object $dimension -Key "weight") { [double](Get-ObjectValue -Object $dimension -Key "weight") } else { 0 }
            得分 = if (Test-ObjectKey -Object $dimension -Key "score") { [double](Get-ObjectValue -Object $dimension -Key "score") } else { 0 }
            失分原因 = if (Test-ObjectKey -Object $dimension -Key "reason") { [string](Get-ObjectValue -Object $dimension -Key "reason") } else { "" }
        }
        if (Test-ObjectKey -Object $dimension -Key "derived_from") {
            $displayItem["来源"] = [string](Get-ObjectValue -Object $dimension -Key "derived_from")
        }
        $displayDimensions += $displayItem
    }

    $display = [ordered]@{
        总分 = if (Test-ObjectKey -Object $ScoreResult -Key "weighted_total") { [double](Get-ObjectValue -Object $ScoreResult -Key "weighted_total") } else { 0 }
        达标结论 = Get-QualifiedDisplayLabel -ScoreResult $ScoreResult
        不达标原因 = if (Test-ObjectKey -Object $ScoreResult -Key "disqualify_reason") { Get-ObjectValue -Object $ScoreResult -Key "disqualify_reason" } else { $null }
        评分维度 = $displayDimensions
        字段映射 = Get-ScoringFieldMappingZh
    }
    if ((Test-ObjectKey -Object $ScoreResult -Key "environment_error") -and -not [string]::IsNullOrWhiteSpace([string](Get-ObjectValue -Object $ScoreResult -Key "environment_error"))) {
        $display["评分环境"] = [string](Get-ObjectValue -Object $ScoreResult -Key "environment_error")
    }
    return $display
}

function Build-SummaryDisplayZh {
    param(
        [object]$Case,
        [object]$SummaryPayload,
        [object]$ScoreResult
    )

    $scoringStatus = if ((Test-ObjectKey -Object $ScoreResult -Key "environment_error") -and -not [string]::IsNullOrWhiteSpace([string](Get-ObjectValue -Object $ScoreResult -Key "environment_error"))) {
        "评分环境异常"
    }
    elseif (@(Get-ObjectValue -Object $ScoreResult -Key "dimensions").Count -eq 0) {
        "未执行"
    }
    else {
        "ok"
    }

    return [ordered]@{
        题号 = [string](Get-ObjectValue -Object $Case -Key "id")
        题目名称 = [string](Get-ObjectValue -Object $Case -Key "name")
        任务ID = if (Test-ObjectKey -Object $SummaryPayload -Key "task_id") { Get-ObjectValue -Object $SummaryPayload -Key "task_id" } else { $null }
        生成稿字数 = if (Test-ObjectKey -Object $SummaryPayload -Key "generated_length") { [int](Get-ObjectValue -Object $SummaryPayload -Key "generated_length") } else { 0 }
        金标稿字数 = if (Test-ObjectKey -Object $SummaryPayload -Key "gold_length") { [int](Get-ObjectValue -Object $SummaryPayload -Key "gold_length") } else { 0 }
        总分 = if (Test-ObjectKey -Object $ScoreResult -Key "weighted_total") { [double](Get-ObjectValue -Object $ScoreResult -Key "weighted_total") } else { 0 }
        达标结论 = Get-QualifiedDisplayLabel -ScoreResult $ScoreResult
        评分状态 = $scoringStatus
        审稿包已齐 = if (Test-ObjectKey -Object $SummaryPayload -Key "review_bundle_ready") { [bool](Get-ObjectValue -Object $SummaryPayload -Key "review_bundle_ready") } else { $false }
        评分维度 = if (Test-ObjectKey -Object $ScoreResult -Key "display_zh") { @(Get-ObjectValue -Object (Get-ObjectValue -Object $ScoreResult -Key "display_zh") -Key "评分维度") } else { @() }
        字段映射 = Get-SummaryFieldMappingZh
    }
}

function Normalize-ScoringResult {
    param([object]$Result)

    if ($null -eq $Result) {
        return @{
            dimensions = @()
            weighted_total = 0
            qualified = $false
            disqualify_reason = "评分返回为空"
            field_mapping_zh = Get-ScoringFieldMappingZh
            display_zh = [ordered]@{
                总分 = 0
                达标结论 = "未判定"
                不达标原因 = "评分返回为空"
                评分维度 = @()
                字段映射 = Get-ScoringFieldMappingZh
            }
            schema_version = "scoring_v2_zh_display_7d"
        }
    }

    $dimensions = if (Test-ObjectKey -Object $Result -Key "dimensions") {
        @(Convert-ToNormalizedScoringDimensions -Dimensions (Get-ObjectValue -Object $Result -Key "dimensions"))
    } else { @() }
    $dimensions = @(Complete-ScoringDimensions -Dimensions $dimensions)

    $weightedTotal = if (Test-ObjectKey -Object $Result -Key "weighted_total") { [double](Get-ObjectValue -Object $Result -Key "weighted_total") } else { 0 }
    $derivedAiFlavor = @($dimensions | Where-Object {
            (Test-ObjectKey -Object $_ -Key "derived_from") -and
            ([string](Get-ObjectValue -Object $_ -Key "derived_from") -eq "audience_style")
        }).Count -gt 0
    if (($weightedTotal -eq 0 -or $derivedAiFlavor) -and $dimensions.Count -gt 0) {
        $weightedTotal = [Math]::Round((@($dimensions | ForEach-Object {
                    $dimensionScore = if (Test-ObjectKey -Object $_ -Key "score") { [double](Get-ObjectValue -Object $_ -Key "score") } else { 0 }
                    $dimensionWeight = if (Test-ObjectKey -Object $_ -Key "weight") { [double](Get-ObjectValue -Object $_ -Key "weight") } else { 0 }
                    ($dimensionScore * $dimensionWeight) / 100.0
                } | Measure-Object -Sum).Sum), 2)
    }

    $normalized = [ordered]@{
        dimensions = $dimensions
        weighted_total = $weightedTotal
        qualified = if (Test-ObjectKey -Object $Result -Key "qualified") { Resolve-QualifiedFlag -Value (Get-ObjectValue -Object $Result -Key "qualified") } else { $false }
        disqualify_reason = if (Test-ObjectKey -Object $Result -Key "disqualify_reason") { Get-ObjectValue -Object $Result -Key "disqualify_reason" } else { $null }
        field_mapping_zh = Get-ScoringFieldMappingZh
        display_zh = $null
        schema_version = "scoring_v2_zh_display_7d"
    }
    if (Test-ObjectKey -Object $Result -Key "environment_error") {
        $errorValue = Get-ObjectValue -Object $Result -Key "environment_error"
        if ($null -ne $errorValue -and [string]::IsNullOrWhiteSpace([string]$errorValue) -eq $false) {
            $normalized["environment_error"] = [string]$errorValue
        }
    }
    $normalized = Apply-ScoringHardThresholds -ScoreResult $normalized
    $normalized.display_zh = Build-ScoringDisplayZh -ScoreResult $normalized
    return $normalized
}

function Normalize-ScoringSchema {
    param([object]$Result)

    if ($null -eq $Result) {
        return $null
    }

    $hasCanonicalEnglishKeys = (Test-ObjectKey -Object $Result -Key "dimensions") -and
        (Test-ObjectKey -Object $Result -Key "weighted_total") -and
        (Test-ObjectKey -Object $Result -Key "qualified")
    if ($hasCanonicalEnglishKeys) {
        $normalizedDimensions = @(Convert-ToNormalizedScoringDimensions -Dimensions (Get-ObjectValue -Object $Result -Key "dimensions"))
        if ($normalizedDimensions.Count -eq 0 -and (Test-ObjectKey -Object $Result -Key "scores")) {
            $normalizedDimensions = @(Convert-ScoreMapToDimensions -ScoresObject (Get-ObjectValue -Object $Result -Key "scores"))
        }

        return [ordered]@{
            dimensions = $normalizedDimensions
            weighted_total = [double](Get-ObjectValue -Object $Result -Key "weighted_total")
            qualified = Resolve-QualifiedFlag -Value (Get-ObjectValue -Object $Result -Key "qualified")
            disqualify_reason = if (Test-ObjectKey -Object $Result -Key "disqualify_reason") { Get-ObjectValue -Object $Result -Key "disqualify_reason" } else { $null }
        }
    }

    $hasAlternateEnglishKeys = (Test-ObjectKey -Object $Result -Key "dimensions") -and
        ((Test-ObjectKey -Object $Result -Key "total_score") -or (Test-ObjectKey -Object $Result -Key "passed"))
    if ($hasAlternateEnglishKeys) {
        $normalizedDimensions = @(Convert-ToNormalizedScoringDimensions -Dimensions (Get-ObjectValue -Object $Result -Key "dimensions"))
        if ($normalizedDimensions.Count -eq 0 -and (Test-ObjectKey -Object $Result -Key "scores")) {
            $normalizedDimensions = @(Convert-ScoreMapToDimensions -ScoresObject (Get-ObjectValue -Object $Result -Key "scores"))
        }

        $normalized = [ordered]@{
            dimensions = $normalizedDimensions
            weighted_total = if (Test-ObjectKey -Object $Result -Key "total_score") { [double](Get-ObjectValue -Object $Result -Key "total_score") } else { 0 }
            qualified = if (Test-ObjectKey -Object $Result -Key "passed") { Resolve-QualifiedFlag -Value (Get-ObjectValue -Object $Result -Key "passed") } else { $false }
            disqualify_reason = if (Test-ObjectKey -Object $Result -Key "disqualify_reason") { Get-ObjectValue -Object $Result -Key "disqualify_reason" } else { $null }
        }
        if (Test-ObjectKey -Object $Result -Key "environment_error") {
            $errorValue = Get-ObjectValue -Object $Result -Key "environment_error"
            if ($null -ne $errorValue -and [string]::IsNullOrWhiteSpace([string]$errorValue) -eq $false) {
                $normalized["environment_error"] = [string]$errorValue
            }
        }
        return $normalized
    }

    $hasChineseKeys = (Test-ObjectKey -Object $Result -Key "评分维度") -or
        (Test-ObjectKey -Object $Result -Key "加权总分") -or
        (Test-ObjectKey -Object $Result -Key "是否合格")
    if (-not $hasChineseKeys) {
        $hasScores = Test-ObjectKey -Object $Result -Key "scores"
        if (-not $hasScores) {
            return $Result
        }

        $normalizedDimensions = @(Convert-ScoreMapToDimensions -ScoresObject (Get-ObjectValue -Object $Result -Key "scores"))
        $qualified = Resolve-QualifiedFlag -Value (Get-ObjectValue -Object $Result -Key "pass_status")

        $weightedTotal = if (Test-ObjectKey -Object $Result -Key "weighted_total") {
            [double](Get-ObjectValue -Object $Result -Key "weighted_total")
        } else { 0 }
        if ($weightedTotal -le 0 -and $normalizedDimensions.Count -gt 0) {
            $weightedTotal = 0
            foreach ($dimension in $normalizedDimensions) {
                $weightedTotal += [double]($dimension.score) * [double]($dimension.weight) / 100
            }
            $weightedTotal = [Math]::Round($weightedTotal, 2)
        }

        return [ordered]@{
            dimensions = $normalizedDimensions
            weighted_total = $weightedTotal
            qualified = $qualified
            disqualify_reason = if (Test-ObjectKey -Object $Result -Key "disqualify_reason") {
                Get-ObjectValue -Object $Result -Key "disqualify_reason"
            } else { if ($qualified) { $null } else { $null } }
        }
    }

    $normalizedDimensions = @()
    $rawDimensions = Get-ObjectValue -Object $Result -Key "评分维度"
    if ($rawDimensions -ne $null) {
        foreach ($dimension in @($rawDimensions)) {
            $dimensionName = if (Test-ObjectKey -Object $dimension -Key "维度名称") { [string](Get-ObjectValue -Object $dimension -Key "维度名称") } else { "" }
            $normalizedDimensions += [ordered]@{
                id = $dimensionName
                name = $dimensionName
                weight = if (Test-ObjectKey -Object $dimension -Key "权重") { [double](Get-ObjectValue -Object $dimension -Key "权重") } else { 0 }
                score = if (Test-ObjectKey -Object $dimension -Key "得分") { [double](Get-ObjectValue -Object $dimension -Key "得分") } else { 0 }
                reason = if (Test-ObjectKey -Object $dimension -Key "失分原因") { [string](Get-ObjectValue -Object $dimension -Key "失分原因") } else { "" }
            }
        }
    }

    $qualifiedValue = Get-ObjectValue -Object $Result -Key "是否合格"
    $qualified = Resolve-QualifiedFlag -Value $qualifiedValue

    return [ordered]@{
        dimensions = $normalizedDimensions
        weighted_total = if (Test-ObjectKey -Object $Result -Key "加权总分") { [double](Get-ObjectValue -Object $Result -Key "加权总分") } else { 0 }
        qualified = $qualified
        disqualify_reason = if ($qualified) { $null } else { $null }
    }
}

function Get-ScoringTextFromResponse {
    param([object]$ResponseBody, [bool]$UseAnthropic)

    if ($null -eq $ResponseBody) {
        return $null
    }

    if ($UseAnthropic) {
        $content = @(Get-ObjectValue -Object $ResponseBody -Key "content")
        if ($content.Count -gt 0) {
            $text = @($content | Where-Object { (Get-ObjectValue -Object $_ -Key "type") -eq "text" } | ForEach-Object { Get-ObjectValue -Object $_ -Key "text" }) -join ""
            if (-not [string]::IsNullOrWhiteSpace($text)) {
                return $text
            }
        }
        return $null
    }

    $choices = @(Get-ObjectValue -Object $ResponseBody -Key "choices")
    if ($choices.Count -gt 0) {
        $firstChoice = $choices[0]
        $message = Get-ObjectValue -Object $firstChoice -Key "message"
        if ($message -ne $null) {
            $messageContent = Get-ObjectValue -Object $message -Key "content"
            if (-not [string]::IsNullOrWhiteSpace([string]$messageContent)) {
                return [string]$messageContent
            }
        }

        if (Test-ObjectKey -Object $firstChoice -Key "content") {
            return [string](Get-ObjectValue -Object $firstChoice -Key "content")
        }
        if (Test-ObjectKey -Object $firstChoice -Key "text") {
            return [string](Get-ObjectValue -Object $firstChoice -Key "text")
        }
    }

    if (Test-ObjectKey -Object $ResponseBody -Key "output") {
        $output = @(Get-ObjectValue -Object $ResponseBody -Key "output")
        if ($output.Count -gt 0) {
            $outputText = Get-ObjectValue -Object $output[0] -Key "text"
            if (-not [string]::IsNullOrWhiteSpace([string]$outputText)) {
                return [string]$outputText
            }
        }
    }

    return $null
}

$scoringDimensions = @(
    @{ id = "task_completion"; name = "任务完成度"; weight = 15; description = "文章是否完成了题目要求的任务类型（患者向/机制科普/新闻报道），是否覆盖核心意图" },
    @{ id = "key_facts"; name = "关键事实与关键数字覆盖"; weight = 25; description = "标准答案中的核心数据点、关键结论、重要数字是否在生成文中准确出现"; hard_threshold = 60 },
    @{ id = "audience_style"; name = "受众匹配与文风匹配"; weight = 10; description = "语体是否匹配目标受众，文风是否符合对应稿型（科普/新闻/患者向），是否真正对准该受众而非泛用安全稿" },
    @{ id = "ai_flavor_control"; name = "AI味儿控制"; weight = 10; description = "是否存在明显模板腔、翻译腔、套话感、匀质化表达或机械排比，是否像人写而不是 AI 默认腔" },
    @{ id = "structure"; name = "结构与信息取舍"; weight = 10; description = "文章结构是否合理，信息详略是否得当，是否做了有效取舍而非简单堆砌" },
    @{ id = "title_angle"; name = "标题角度与稿型适配"; weight = 10; description = "标题是否有角度和吸引力，是否符合稿型特征（新闻感/科普感/温度感）" },
    @{ id = "hallucination_control"; name = "幻觉与越界编造控制"; weight = 20; description = "是否存在原文未提及的编造数据/结论/因果关系，是否存在超出原文材料的过度推断"; hard_threshold = 60 }
)

$repoEnvPath = Join-Path (Split-Path $PSScriptRoot -Parent) ".env"
Load-RepoEnv -EnvPath $repoEnvPath

function Get-DefaultCasesConfig {
    return Join-Path (Join-Path $PSScriptRoot "config") "ii_benchmark_cases.json"
}

function Read-JsonFile {
    param([string]$Path)

    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-JsonCompat
}

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Payload
    )

    $Payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Resolve-CaseConfig {
    param([string]$ConfigPath)

    $resolvedPath = if ($ConfigPath) { $ConfigPath } else { Get-DefaultCasesConfig }
    if (-not (Test-Path -LiteralPath $resolvedPath)) {
        throw "题库配置不存在: $resolvedPath"
    }

    $config = Read-JsonFile -Path $resolvedPath
    $caseMap = @{}
    foreach ($case in $config.cases) {
        $caseMap[$case.id] = $case
    }

    $suiteMap = @{}
    foreach ($suite in $config.suites) {
        $suiteMap[$suite.id] = $suite
    }

    return [pscustomobject]@{
        Path = $resolvedPath
        Config = $config
        CaseMap = $caseMap
        SuiteMap = $suiteMap
    }
}

function Resolve-TestCases {
    param(
        [object]$Catalog,
        [string[]]$SelectedCaseIds
    )

    if (-not $SelectedCaseIds -or $SelectedCaseIds.Count -eq 0) {
        return @($Catalog.Config.cases)
    }

    $resolved = @()
    $unknown = @()
    foreach ($caseId in $SelectedCaseIds) {
        if ($Catalog.CaseMap.ContainsKey($caseId)) {
            $resolved += $Catalog.CaseMap[$caseId]
        }
        else {
            $unknown += $caseId
        }
    }

    if ($unknown.Count -gt 0) {
        $available = ($Catalog.CaseMap.Keys | Sort-Object) -join ", "
        throw "未知 case_id: $($unknown -join ', ')；可用值: $available"
    }

    return $resolved
}

function Get-HttpClient {
    param([string]$BaseUrlValue)

    if ($script:HttpClient -ne $null) {
        return $script:HttpClient
    }

    $handler = [System.Net.Http.HttpClientHandler]::new()
    $handler.CookieContainer = [System.Net.CookieContainer]::new()
    $handler.AutomaticDecompression = [System.Net.DecompressionMethods]::GZip -bor [System.Net.DecompressionMethods]::Deflate

    $client = [System.Net.Http.HttpClient]::new($handler)
    $client.Timeout = [TimeSpan]::FromSeconds(180)

    $username = [Environment]::GetEnvironmentVariable("XIAGEDAO_AUTH_USERNAME")
    $password = [Environment]::GetEnvironmentVariable("XIAGEDAO_AUTH_PASSWORD")
    $authEnabledRaw = [Environment]::GetEnvironmentVariable("XIAGEDAO_AUTH_ENABLED")
    if ($null -eq $authEnabledRaw) {
        $authEnabled = ""
    }
    else {
        $authEnabled = $authEnabledRaw.ToLowerInvariant()
    }

    if (($authEnabled -eq "true" -or $authEnabled -eq "1" -or $authEnabled -eq "yes") -and $username -and $password) {
        $payload = @{ username = $username; password = $password } | ConvertTo-Json -Depth 5
        $content = [System.Net.Http.StringContent]::new($payload, [System.Text.Encoding]::UTF8, "application/json")
        $response = $client.PostAsync("$BaseUrlValue/v1/auth/login", $content).GetAwaiter().GetResult()
        if (-not $response.IsSuccessStatusCode) {
            $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            throw "认证登录失败: $($response.StatusCode) $body"
        }
        Write-Host "  认证登录成功 (user=$username)"
    }

    $script:HttpClient = $client
    return $script:HttpClient
}

function Invoke-JsonGet {
    param(
        [string]$BaseUrlValue,
        [string]$Url
    )

    $client = Get-HttpClient -BaseUrlValue $BaseUrlValue
    $response = $client.GetAsync($Url).GetAwaiter().GetResult()
    $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    if (-not $response.IsSuccessStatusCode) {
        throw "GET 失败: $($response.StatusCode) $body"
    }

    if ([string]::IsNullOrWhiteSpace($body)) {
        return $null
    }
    return $body | ConvertFrom-JsonCompat
}

function Invoke-JsonPost {
    param(
        [string]$BaseUrlValue,
        [string]$Url,
        [object]$Payload
    )

    $client = Get-HttpClient -BaseUrlValue $BaseUrlValue
    $json = $Payload | ConvertTo-Json -Depth 100
    $content = [System.Net.Http.StringContent]::new($json, [System.Text.Encoding]::UTF8, "application/json")
    $response = $client.PostAsync($Url, $content).GetAwaiter().GetResult()
    $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    if (-not $response.IsSuccessStatusCode) {
        throw "POST 失败: $($response.StatusCode) $body"
    }
    return $body | ConvertFrom-JsonCompat
}

function Upload-Pdf {
    param(
        [string]$BaseUrlValue,
        [string]$PdfPath
    )

    $client = Get-HttpClient -BaseUrlValue $BaseUrlValue
    $url = "$BaseUrlValue/v1/evidence/upload/file/stash"
    $multipart = [System.Net.Http.MultipartFormDataContent]::new()
    $fileStream = [System.IO.File]::OpenRead($PdfPath)
    try {
        $streamContent = [System.Net.Http.StreamContent]::new($fileStream)
        $streamContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/pdf")
        $multipart.Add($streamContent, "file", [System.IO.Path]::GetFileName($PdfPath))
        $response = $client.PostAsync($url, $multipart).GetAwaiter().GetResult()
        $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
        if (-not $response.IsSuccessStatusCode) {
            throw "上传失败: $($response.StatusCode) $body"
        }
        $json = $body | ConvertFrom-JsonCompat
        return $json.upload_id
    }
    finally {
        $multipart.Dispose()
        $fileStream.Dispose()
    }
}

function Start-StandardChain {
    param(
        [string]$BaseUrlValue,
        [object]$Case,
        [string[]]$UploadIds
    )

    $payload = @{
        product_id = $Case.product_id
        domain = $Case.domain
        register = $Case.register
        audience = $Case.audience
        target_word_count = [int]$Case.target_word_count
        metadata = @{
            supplement_upload_ids = $UploadIds
        }
    }

    $result = Invoke-JsonPost -BaseUrlValue $BaseUrlValue -Url "$BaseUrlValue/v1/workflow/standard-chain" -Payload $payload
    return $result.task_id
}

function Poll-TaskCompletion {
    param(
        [string]$BaseUrlValue,
        [string]$TaskId,
        [int]$MaxWait = 3600,
        [int]$PollInterval = 10
    )

    $deadline = (Get-Date).AddSeconds($MaxWait)
    while ((Get-Date) -lt $deadline) {
        $data = Invoke-JsonGet -BaseUrlValue $BaseUrlValue -Url "$BaseUrlValue/v1/tasks/$TaskId"
        $status = [string]$data.status
        if ($status -in @("completed", "failed", "error")) {
            return $data
        }
        Write-Host "  ... 状态: $status"
        Start-Sleep -Seconds $PollInterval
    }

    throw "任务 $TaskId 超时（${MaxWait}s）"
}

function Extract-GeneratedArticle {
    param([object]$TaskDetail)

    if ($null -eq $TaskDetail) {
        return $null
    }

    $workingCopy = if (Test-ObjectKey -Object $TaskDetail -Key "working_copy") {
        Get-ObjectValue -Object $TaskDetail -Key "working_copy"
    } else { $null }
    if ($null -ne $workingCopy -and (Test-ObjectKey -Object $workingCopy -Key "content")) {
        $workingCopyContent = Get-ObjectValue -Object $workingCopy -Key "content"
        if (-not [string]::IsNullOrWhiteSpace([string]$workingCopyContent)) {
            return [string]$workingCopyContent
        }
    }

    $outputData = if (Test-ObjectKey -Object $TaskDetail -Key "output_data") {
        Get-ObjectValue -Object $TaskDetail -Key "output_data"
    } else { $null }
    if ($null -ne $outputData -and (Test-ObjectKey -Object $outputData -Key "drafting")) {
        $draftingData = Get-ObjectValue -Object $outputData -Key "drafting"
        if ($null -ne $draftingData) {
            if (Test-ObjectKey -Object $draftingData -Key "content_preview") {
                $contentPreview = Get-ObjectValue -Object $draftingData -Key "content_preview"
                if (-not [string]::IsNullOrWhiteSpace([string]$contentPreview)) {
                    return [string]$contentPreview
                }
            }
            if (Test-ObjectKey -Object $draftingData -Key "content") {
                $draftingContent = Get-ObjectValue -Object $draftingData -Key "content"
                if (-not [string]::IsNullOrWhiteSpace([string]$draftingContent)) {
                    return [string]$draftingContent
                }
            }
        }
    }

    $resultData = if (Test-ObjectKey -Object $TaskDetail -Key "result") {
        Get-ObjectValue -Object $TaskDetail -Key "result"
    } else { $null }
    if ($null -ne $resultData -and (Test-ObjectKey -Object $resultData -Key "delivery")) {
        $deliveryData = Get-ObjectValue -Object $resultData -Key "delivery"
        foreach ($field in @("article", "content", "text")) {
            if ($null -ne $deliveryData -and (Test-ObjectKey -Object $deliveryData -Key $field)) {
                $deliveryText = Get-ObjectValue -Object $deliveryData -Key $field
                if (-not [string]::IsNullOrWhiteSpace([string]$deliveryText)) {
                    return [string]$deliveryText
                }
            }
        }
    }

    if ($null -ne $resultData -and (Test-ObjectKey -Object $resultData -Key "drafting")) {
        $resultDrafting = Get-ObjectValue -Object $resultData -Key "drafting"
        foreach ($field in @("article", "content", "text")) {
            if ($null -ne $resultDrafting -and (Test-ObjectKey -Object $resultDrafting -Key $field)) {
                $resultDraftingText = Get-ObjectValue -Object $resultDrafting -Key $field
                if (-not [string]::IsNullOrWhiteSpace([string]$resultDraftingText)) {
                    return [string]$resultDraftingText
                }
            }
        }
    }
    if ($TaskDetail.child_results) {
        foreach ($child in $TaskDetail.child_results) {
            if ($child.module_name -in @("delivery", "drafting") -and $child.result) {
                foreach ($field in @("article", "content", "text")) {
                    if ($child.result.PSObject.Properties.Name -contains $field -and $child.result.$field) {
                        return [string]$child.result.$field
                    }
                }
            }
        }
    }

    return $null
}

function Get-TaskReviewBundle {
    param([object]$TaskDetail)

    if ($null -eq $TaskDetail) {
        return $null
    }

    $outputData = if (Test-ObjectKey -Object $TaskDetail -Key "output_data") {
        Get-ObjectValue -Object $TaskDetail -Key "output_data"
    } else { $null }
    if ($null -eq $outputData) {
        return $null
    }

    $evidenceData = if (Test-ObjectKey -Object $outputData -Key "evidence") {
        Get-ObjectValue -Object $outputData -Key "evidence"
    } else { $null }
    $planningData = if (Test-ObjectKey -Object $outputData -Key "planning") {
        Get-ObjectValue -Object $outputData -Key "planning"
    } else { $null }
    $writingData = if (Test-ObjectKey -Object $outputData -Key "writing") {
        Get-ObjectValue -Object $outputData -Key "writing"
    } else { $null }
    $draftingData = if (Test-ObjectKey -Object $outputData -Key "drafting") {
        Get-ObjectValue -Object $outputData -Key "drafting"
    } else { $null }

    $materials = @()
    if ($null -ne $evidenceData -and (Test-ObjectKey -Object $evidenceData -Key "facts_full")) {
        foreach ($item in @((Get-ObjectValue -Object $evidenceData -Key "facts_full"))) {
            if ($null -ne $item) {
                $materials += $item
            }
        }
    }

    $systemPrompt = if ($null -ne $writingData -and (Test-ObjectKey -Object $writingData -Key "system_prompt")) {
        [string](Get-ObjectValue -Object $writingData -Key "system_prompt")
    } else { "" }
    $userPrompt = if ($null -ne $writingData -and (Test-ObjectKey -Object $writingData -Key "user_prompt")) {
        [string](Get-ObjectValue -Object $writingData -Key "user_prompt")
    } else { "" }

    if ($materials.Count -eq 0 -and [string]::IsNullOrWhiteSpace($systemPrompt) -and [string]::IsNullOrWhiteSpace($userPrompt)) {
        return $null
    }

    return [ordered]@{
        task_id = if (Test-ObjectKey -Object $TaskDetail -Key "task_id") { [string](Get-ObjectValue -Object $TaskDetail -Key "task_id") } else { $null }
        workflow_name = if (Test-ObjectKey -Object $outputData -Key "workflow_name") { [string](Get-ObjectValue -Object $outputData -Key "workflow_name") } else { $null }
        material_fact_count = $materials.Count
        materials = $materials
        evidence = if ($null -ne $evidenceData) { $evidenceData } else { $null }
        planning = if ($null -ne $planningData) { $planningData } else { $null }
        writing = if ($null -ne $writingData) { $writingData } else { $null }
        drafting = if ($null -ne $draftingData) { $draftingData } else { $null }
        review_bundle_ready = ($materials.Count -gt 0) -and (-not [string]::IsNullOrWhiteSpace($userPrompt))
    }
}

function Test-TaskEligibleForScoring {
    param([object]$TaskDetail)

    if ($null -eq $TaskDetail) {
        return $false
    }

    $taskStatus = if (Test-ObjectKey -Object $TaskDetail -Key "status") {
        [string](Get-ObjectValue -Object $TaskDetail -Key "status")
    } else { "" }
    if ($taskStatus -eq "completed") {
        return $true
    }
    if ($taskStatus -ne "failed") {
        return $false
    }

    $outputData = if (Test-ObjectKey -Object $TaskDetail -Key "output_data") {
        Get-ObjectValue -Object $TaskDetail -Key "output_data"
    } else { $null }
    if ($null -eq $outputData) {
        return $false
    }

    $haltedAt = if (Test-ObjectKey -Object $outputData -Key "halted_at") {
        [string](Get-ObjectValue -Object $outputData -Key "halted_at")
    } else { "" }
    if ($haltedAt -ne "delivery") {
        return $false
    }

    $deliveryData = if (Test-ObjectKey -Object $outputData -Key "delivery") {
        Get-ObjectValue -Object $outputData -Key "delivery"
    } else { $null }
    if ($null -eq $deliveryData) {
        return $false
    }

    $deliveryGatePassed = if (Test-ObjectKey -Object $deliveryData -Key "delivery_word_count_gate_passed") {
        [bool](Get-ObjectValue -Object $deliveryData -Key "delivery_word_count_gate_passed")
    }
    elseif (Test-ObjectKey -Object $deliveryData -Key "word_count_gate_passed") {
        [bool](Get-ObjectValue -Object $deliveryData -Key "word_count_gate_passed")
    }
    else {
        $true
    }

    $scoringGatePassed = if (Test-ObjectKey -Object $deliveryData -Key "scoring_word_count_gate_passed") {
        [bool](Get-ObjectValue -Object $deliveryData -Key "scoring_word_count_gate_passed")
    } else { $false }

    return (-not $deliveryGatePassed) -and $scoringGatePassed
}

function Extract-DocxText {
    param([string]$DocxPath)

    $zip = [System.IO.Compression.ZipFile]::OpenRead($DocxPath)
    try {
        $entry = $zip.Entries | Where-Object { $_.FullName -eq "word/document.xml" } | Select-Object -First 1
        if ($null -eq $entry) {
            throw "word/document.xml 不存在"
        }
        $reader = [System.IO.StreamReader]::new($entry.Open())
        try {
            $xml = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }
    }
    finally {
        $zip.Dispose()
    }

    $text = $xml -replace "</w:p>", "`n`n" -replace "<[^>]+>", ""
    $text = [System.Net.WebUtility]::HtmlDecode($text)
    $lines = $text -split "(`r`n|`n|`r)" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    return ($lines -join "`n`n")
}

function Build-ScoringPrompt {
    param(
        [object]$Case,
        [string]$GoldText,
        [string]$GeneratedText
    )

    $dimensionsDesc = ($scoringDimensions | ForEach-Object {
        "- **$($_.name)** (权重 $($_.weight)分): $($_.description)"
    }) -join "`n"

    $lines = @(
        "你是一位资深医学内容编辑，负责评判 AI 生成的医学文章质量。",
        "",
        "## 评测任务",
        "题目名称: $($Case.name)",
        "目标受众: $($Case.audience)",
        "目标字数: $($Case.target_word_count)",
        "",
        "## 评分维度（总计 100 分）",
        $dimensionsDesc,
        "",
        "## 标准答案",
        "以下是人工撰写的标准答案（作为参考基准）：",
        "",
        '```',
        $GoldText.Substring(0, [Math]::Min(6000, $GoldText.Length)),
        '```',
        "",
        "## 待评文章",
        "以下是 AI 生成的待评文章：",
        "",
        '```',
        $GeneratedText.Substring(0, [Math]::Min(6000, $GeneratedText.Length)),
        '```',
        "",
        "## 评分要求",
        "",
        "1. 逐维度给出 0-100 的分数和 1-2 句失分原因",
        "2. 算出加权总分（各维度分 × 权重 / 100 再求和）",
        '3. 如果“关键事实与关键数字覆盖”或“幻觉与越界编造控制”任一维度 < 60，标记该题为“不合格”',
        "",
        "请严格按以下 JSON 格式输出，不要包含其他文本。",
        "注意：reason 字段内部不要使用英文双引号，改用中文引号或单引号标注专有名词。",
        "",
        '```json',
        "{",
        '  "dimensions": [',
        "    {",
        '      "id": "task_completion",',
        '      "score": <0-100>,',
        '      "reason": "<失分原因>"',
        "    },",
        "    {",
        '      "id": "key_facts",',
        '      "score": <0-100>,',
        '      "reason": "<失分原因>"',
        "    },",
        "    {",
        '      "id": "audience_style",',
        '      "score": <0-100>,',
        '      "reason": "<失分原因>"',
        "    },",
        "    {",
        '      "id": "ai_flavor_control",',
        '      "score": <0-100>,',
        '      "reason": "<失分原因>"',
        "    },",
        "    {",
        '      "id": "structure",',
        '      "score": <0-100>,',
        '      "reason": "<失分原因>"',
        "    },",
        "    {",
        '      "id": "title_angle",',
        '      "score": <0-100>,',
        '      "reason": "<失分原因>"',
        "    },",
        "    {",
        '      "id": "hallucination_control",',
        '      "score": <0-100>,',
        '      "reason": "<失分原因>"',
        "    }",
        "  ],",
        '  "weighted_total": <加权总分>,',
        '  "qualified": <true/false>,',
        '  "disqualify_reason": "<不合格原因，合格则为 null>"',
        "}",
        '```'
    )

    return ($lines -join "`n")
}

function Try-ParseJsonText {
    param([string]$Text)

    try {
        return $Text | ConvertFrom-JsonCompat
    }
    catch {
    }

    $codeMatch = [regex]::Match($Text, '```(?:json)?\s*(.*?)\s*```', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($codeMatch.Success) {
        try {
            return $codeMatch.Groups[1].Value | ConvertFrom-JsonCompat
        }
        catch {
        }
    }

    $jsonMatch = [regex]::Match($Text, '\{.*\}', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($jsonMatch.Success) {
        try {
            return $jsonMatch.Value | ConvertFrom-JsonCompat
        }
        catch {
        }
    }

    return $null
}

function Get-MockScore {
    $dimensions = @()
    foreach ($dimension in $scoringDimensions) {
        $dimensions += @{
            id = $dimension.id
            score = 0
            reason = "模拟评分：无 LLM 连接"
        }
    }
    return @{
        dimensions = $dimensions
        weighted_total = 0
        qualified = $false
        disqualify_reason = "模拟评分模式，无实际评分"
    }
}

function Score-WithLLM {
    param(
        [object]$Case,
        [string]$GoldText,
        [string]$GeneratedText,
        [string]$ScoringKey
    )

    $prompt = Build-ScoringPrompt -Case $Case -GoldText $GoldText -GeneratedText $GeneratedText
    $configCandidates = Get-ScoringConfigCandidates -ScoringKey $ScoringKey
    if ($configCandidates.Count -eq 0) {
        Write-Host "WARNING: 无 LLM API key，当前题目标记为评分环境缺失"
        return @{
            dimensions = @()
            weighted_total = 0
            qualified = $false
            disqualify_reason = "评分环境缺失: 无 LLM API key"
            environment_error = "missing_llm_api_key"
        }
    }

    $attemptErrors = @()
    foreach ($cfg in $configCandidates) {
        $handler = $null
        $client = $null
        try {
            $useAnthropic = $cfg.protocol -eq "anthropic"
            Write-Host "  评分 provider: $($cfg.source)"

            $handler = [System.Net.Http.HttpClientHandler]::new()
            $client = [System.Net.Http.HttpClient]::new($handler)
            $client.Timeout = [TimeSpan]::FromSeconds(180)

            if ($useAnthropic) {
                $payload = @{
                    model = $cfg.model
                    max_tokens = 8192
                    temperature = 0.1
                    messages = @(@{ role = "user"; content = $prompt })
                } | ConvertTo-Json -Depth 20
                $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, (Get-AnthropicMessagesUrl -BaseUrl $cfg.base_url))
                $request.Headers.Add("x-api-key", $cfg.api_key)
                $request.Headers.Add("anthropic-version", "2023-06-01")
                $request.Content = [System.Net.Http.StringContent]::new($payload, [System.Text.Encoding]::UTF8, "application/json")
            }
            else {
                $payload = @{
                    model = $cfg.model
                    messages = @(@{ role = "user"; content = $prompt })
                    temperature = 0.1
                } | ConvertTo-Json -Depth 20
                $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$($cfg.base_url)/chat/completions")
                $request.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $cfg.api_key)
                $request.Content = [System.Net.Http.StringContent]::new($payload, [System.Text.Encoding]::UTF8, "application/json")
            }

            $response = $client.SendAsync($request).GetAwaiter().GetResult()
            $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            if (-not $response.IsSuccessStatusCode) {
                throw "评分请求失败: $($response.StatusCode) $body"
            }

            $parsedBody = $body | ConvertFrom-JsonCompat
            $raw = Get-ScoringTextFromResponse -ResponseBody $parsedBody -UseAnthropic $useAnthropic
            if ([string]::IsNullOrWhiteSpace($raw)) {
                throw "评分响应缺失内容文本"
            }

            $parsed = Try-ParseJsonText -Text $raw
            if ($null -eq $parsed) {
                throw "无法解析评分 JSON: $raw"
            }

            $parsed = Normalize-ScoringSchema -Result $parsed
            $requiredKeys = @("dimensions", "weighted_total", "qualified")
            $missingKeys = @($requiredKeys | Where-Object { -not (Test-ObjectKey -Object $parsed -Key $_) })
            if ($missingKeys.Count -gt 0) {
                throw "评分 JSON 缺字段 ($($missingKeys -join ', ')): $raw"
            }

            $normalizedScore = Normalize-ScoringResult -Result $parsed
            $normalizedDimensions = @(Get-ObjectValue -Object $normalizedScore -Key "dimensions")
            if ($normalizedDimensions.Count -ne $scoringDimensions.Count) {
                throw "评分 JSON 维度不完整（期望 $($scoringDimensions.Count) 个，实际 $($normalizedDimensions.Count) 个）: $raw"
            }

            return $normalizedScore
        }
        catch {
            $attemptErrors += "$($cfg.source): $($_.Exception.Message)"
        }
        finally {
            if ($null -ne $client) {
                $client.Dispose()
            }
            if ($null -ne $handler) {
                $handler.Dispose()
            }
        }
    }

    return @{
        dimensions = @()
        weighted_total = 0
        qualified = $false
        disqualify_reason = "评分失败: " + ($attemptErrors -join "; ")
        environment_error = "scoring_provider_unavailable"
    }
}

function Get-CaseArtifactPaths {
    param(
        [string]$OutputRoot,
        [string]$CaseId,
        [string]$Timestamp
    )

    $caseDir = Join-Path $OutputRoot $CaseId
    New-Item -ItemType Directory -Path $caseDir -Force | Out-Null
    return @{
        case_dir = $caseDir
        generated_latest = Join-Path $caseDir "generated.txt"
        generated_snapshot = Join-Path $caseDir "generated_$Timestamp.txt"
        task_detail_latest = Join-Path $caseDir "task_detail.json"
        task_detail_snapshot = Join-Path $caseDir "task_detail_$Timestamp.json"
        materials_latest = Join-Path $caseDir "materials_full.json"
        materials_snapshot = Join-Path $caseDir "materials_full_$Timestamp.json"
        writing_system_prompt_latest = Join-Path $caseDir "writing_system_prompt.txt"
        writing_system_prompt_snapshot = Join-Path $caseDir "writing_system_prompt_$Timestamp.txt"
        writing_user_prompt_latest = Join-Path $caseDir "writing_user_prompt.txt"
        writing_user_prompt_snapshot = Join-Path $caseDir "writing_user_prompt_$Timestamp.txt"
        review_bundle_latest = Join-Path $caseDir "review_bundle.json"
        review_bundle_snapshot = Join-Path $caseDir "review_bundle_$Timestamp.json"
        gold_latest = Join-Path $caseDir "gold.txt"
        gold_snapshot = Join-Path $caseDir "gold_$Timestamp.txt"
        score_latest = Join-Path $caseDir "score.json"
        score_snapshot = Join-Path $caseDir "score_$Timestamp.json"
        summary_latest = Join-Path $caseDir "summary.json"
        summary_snapshot = Join-Path $caseDir "summary_$Timestamp.json"
        legacy_generated = Join-Path $OutputRoot "$CaseId`_generated.txt"
    }
}

function Write-ReviewBundleArtifacts {
    param(
        [hashtable]$Paths,
        [object]$ReviewBundle
    )

    if ($null -eq $ReviewBundle) {
        return
    }

    Write-JsonFile -Path $Paths.review_bundle_latest -Payload $ReviewBundle
    Write-JsonFile -Path $Paths.review_bundle_snapshot -Payload $ReviewBundle

    if ($ReviewBundle.materials.Count -gt 0) {
        Write-JsonFile -Path $Paths.materials_latest -Payload $ReviewBundle.materials
        Write-JsonFile -Path $Paths.materials_snapshot -Payload $ReviewBundle.materials
    }

    $writingPayload = Get-ObjectValue -Object $ReviewBundle -Key "writing"
    if ($null -eq $writingPayload) {
        return
    }

    if ((Test-ObjectKey -Object $writingPayload -Key "system_prompt") -and -not [string]::IsNullOrWhiteSpace([string](Get-ObjectValue -Object $writingPayload -Key "system_prompt"))) {
        $systemPrompt = [string](Get-ObjectValue -Object $writingPayload -Key "system_prompt")
        Set-Content -LiteralPath $Paths.writing_system_prompt_latest -Value $systemPrompt -Encoding UTF8
        Set-Content -LiteralPath $Paths.writing_system_prompt_snapshot -Value $systemPrompt -Encoding UTF8
    }
    if ((Test-ObjectKey -Object $writingPayload -Key "user_prompt") -and -not [string]::IsNullOrWhiteSpace([string](Get-ObjectValue -Object $writingPayload -Key "user_prompt"))) {
        $userPrompt = [string](Get-ObjectValue -Object $writingPayload -Key "user_prompt")
        Set-Content -LiteralPath $Paths.writing_user_prompt_latest -Value $userPrompt -Encoding UTF8
        Set-Content -LiteralPath $Paths.writing_user_prompt_snapshot -Value $userPrompt -Encoding UTF8
    }
}

function Get-TaskDetailDeliveryGateValue {
    param(
        [object]$TaskDetail,
        [string]$FieldName
    )

    if ($null -eq $TaskDetail -or -not (Test-ObjectKey -Object $TaskDetail -Key "output_data")) {
        return $null
    }

    $outputData = Get-ObjectValue -Object $TaskDetail -Key "output_data"
    if ($null -eq $outputData -or -not (Test-ObjectKey -Object $outputData -Key "delivery")) {
        return $null
    }

    $deliveryData = Get-ObjectValue -Object $outputData -Key "delivery"
    if ($null -eq $deliveryData) {
        return $null
    }

    if (Test-ObjectKey -Object $deliveryData -Key $FieldName) {
        return Get-ObjectValue -Object $deliveryData -Key $FieldName
    }

    if ($FieldName -eq "delivery_word_count_gate_passed" -and (Test-ObjectKey -Object $deliveryData -Key "word_count_gate_passed")) {
        return Get-ObjectValue -Object $deliveryData -Key "word_count_gate_passed"
    }

    return $null
}

function Get-TaskStatusLabel {
    param(
        [object]$TaskDetail
    )

    if ($null -eq $TaskDetail) {
        return $null
    }

    if (Test-ObjectKey -Object $TaskDetail -Key "status") {
        return [string](Get-ObjectValue -Object $TaskDetail -Key "status")
    }

    return $null
}

function Get-CaseArtifactsPayload {
    param(
        [hashtable]$Paths,
        [object]$TaskDetail
    )

    return [ordered]@{
        case_dir = $Paths.case_dir
        generated_file = if (Test-Path -LiteralPath $Paths.generated_latest) { $Paths.generated_latest } else { $null }
        task_detail_file = if ($null -ne $TaskDetail -and (Test-Path -LiteralPath $Paths.task_detail_latest)) { $Paths.task_detail_latest } else { $null }
        materials_file = if (Test-Path -LiteralPath $Paths.materials_latest) { $Paths.materials_latest } else { $null }
        writing_system_prompt_file = if (Test-Path -LiteralPath $Paths.writing_system_prompt_latest) { $Paths.writing_system_prompt_latest } else { $null }
        writing_user_prompt_file = if (Test-Path -LiteralPath $Paths.writing_user_prompt_latest) { $Paths.writing_user_prompt_latest } else { $null }
        review_bundle_file = if (Test-Path -LiteralPath $Paths.review_bundle_latest) { $Paths.review_bundle_latest } else { $null }
        gold_file = if (Test-Path -LiteralPath $Paths.gold_latest) { $Paths.gold_latest } else { $null }
        score_file = if (Test-Path -LiteralPath $Paths.score_latest) { $Paths.score_latest } else { $null }
        summary_file = if (Test-Path -LiteralPath $Paths.summary_latest) { $Paths.summary_latest } else { $null }
    }
}

function Write-FailureCaseSummary {
    param(
        [hashtable]$Paths,
        [object]$Case,
        [string]$TaskId,
        [object]$TaskDetail,
        [string]$GeneratedText,
        [string]$GoldText,
        [object]$ReviewBundle,
        [string]$ErrorMessage
    )

    $scoreResult = Normalize-ScoringResult -Result @{
        dimensions = @()
        weighted_total = 0
        qualified = $false
        disqualify_reason = $ErrorMessage
    }

    $taskStatus = if ($null -ne $TaskDetail -and (Test-ObjectKey -Object $TaskDetail -Key "status")) {
        [string](Get-ObjectValue -Object $TaskDetail -Key "status")
    }
    elseif (-not [string]::IsNullOrWhiteSpace($TaskId)) {
        "failed"
    }
    else {
        "error"
    }

    $summaryPayload = [ordered]@{
        id = $Case.id
        name = $Case.name
        task_id = $TaskId
        task_status = $taskStatus
        generated_length = if ($GeneratedText) { $GeneratedText.Length } else { 0 }
        gold_length = if ($GoldText) { $GoldText.Length } else { 0 }
        qualified = $false
        weighted_total = 0
        scoring_status = "skipped"
        review_bundle_ready = if ($null -ne $ReviewBundle -and (Test-ObjectKey -Object $ReviewBundle -Key "review_bundle_ready")) { [bool](Get-ObjectValue -Object $ReviewBundle -Key "review_bundle_ready") } else { $false }
        delivery_gate_passed = if ($null -ne (Get-TaskDetailDeliveryGateValue -TaskDetail $TaskDetail -FieldName "delivery_word_count_gate_passed")) { [bool](Get-TaskDetailDeliveryGateValue -TaskDetail $TaskDetail -FieldName "delivery_word_count_gate_passed") } else { $null }
        scoring_gate_passed = if ($null -ne (Get-TaskDetailDeliveryGateValue -TaskDetail $TaskDetail -FieldName "scoring_word_count_gate_passed")) { [bool](Get-TaskDetailDeliveryGateValue -TaskDetail $TaskDetail -FieldName "scoring_word_count_gate_passed") } else { $null }
        error = $ErrorMessage
        field_mapping_zh = Get-SummaryFieldMappingZh
        display_zh = $null
    }
    $summaryPayload.display_zh = Build-SummaryDisplayZh -Case $Case -SummaryPayload $summaryPayload -ScoreResult $scoreResult

    Write-JsonFile -Path $Paths.score_latest -Payload $scoreResult
    Write-JsonFile -Path $Paths.score_snapshot -Payload $scoreResult
    Write-JsonFile -Path $Paths.summary_latest -Payload $summaryPayload
    Write-JsonFile -Path $Paths.summary_snapshot -Payload $summaryPayload

    return [ordered]@{
        id = $Case.id
        name = $Case.name
        task_id = $TaskId
        task_status = $taskStatus
        generated_length = $summaryPayload.generated_length
        gold_length = $summaryPayload.gold_length
        scoring_status = "skipped"
        error = $ErrorMessage
        artifacts = Get-CaseArtifactsPayload -Paths $Paths -TaskDetail $TaskDetail
    }
}

function Invoke-Benchmark {
    param(
        [string]$BaseUrlValue,
        [string]$OutputRoot,
        [object[]]$Cases,
        [switch]$UseCachedGeneration,
        [string]$ScoringKey,
        [int]$MaxWait,
        [int]$PollInterval
    )

    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $report = [ordered]@{
        timestamp = $timestamp
        base_url = $BaseUrlValue
        selected_case_ids = @($Cases | ForEach-Object { $_.id })
        test_cases = @()
    }

    foreach ($case in $Cases) {
        Write-Host ""
        Write-Host ("=" * 60)
        Write-Host "评测: $($case.name)"
        Write-Host ("=" * 60)

        $caseDir = $case.dir
        $inputsDir = Join-Path $caseDir "inputs"
        $goldPath = Join-Path (Join-Path $caseDir "gold") $case.gold_filename
        $paths = Get-CaseArtifactPaths -OutputRoot $OutputRoot -CaseId $case.id -Timestamp $timestamp

        if (-not (Test-Path -LiteralPath $inputsDir)) {
            $report.test_cases += Write-FailureCaseSummary -Paths $paths -Case $case -TaskId $taskId -TaskDetail $taskDetail -GeneratedText $generatedText -GoldText $goldText -ReviewBundle $reviewBundle -ErrorMessage "inputs/ 目录不存在: $inputsDir"
            continue
        }
        if (-not (Test-Path -LiteralPath $goldPath)) {
            $report.test_cases += Write-FailureCaseSummary -Paths $paths -Case $case -TaskId $taskId -TaskDetail $taskDetail -GeneratedText $generatedText -GoldText $goldText -ReviewBundle $reviewBundle -ErrorMessage "gold 文件不存在: $goldPath"
            continue
        }

        $generatedText = $null
        $taskId = $null
        $taskDetail = $null
        $reviewBundle = $null
        $goldText = $null

        $goldText = Extract-DocxText -DocxPath $goldPath
        Set-Content -LiteralPath $paths.gold_latest -Value $goldText -Encoding UTF8
        Set-Content -LiteralPath $paths.gold_snapshot -Value $goldText -Encoding UTF8

        if ($UseCachedGeneration -and (Test-Path -LiteralPath $paths.generated_latest)) {
            Write-Host "  跳过生成，使用已有结果"
            $generatedText = Get-Content -LiteralPath $paths.generated_latest -Raw
            if (Test-Path -LiteralPath $paths.task_detail_latest) {
                $taskDetail = Read-JsonFile -Path $paths.task_detail_latest
                $reviewBundle = Get-TaskReviewBundle -TaskDetail $taskDetail
                Write-ReviewBundleArtifacts -Paths $paths -ReviewBundle $reviewBundle
            }
        }
        elseif ($UseCachedGeneration -and (Test-Path -LiteralPath $paths.legacy_generated)) {
            Write-Host "  跳过生成，使用旧版已有结果"
            $generatedText = Get-Content -LiteralPath $paths.legacy_generated -Raw
            Set-Content -LiteralPath $paths.generated_latest -Value $generatedText -Encoding UTF8
            Set-Content -LiteralPath $paths.generated_snapshot -Value $generatedText -Encoding UTF8
        }
        elseif ($UseCachedGeneration) {
            $report.test_cases += Write-FailureCaseSummary -Paths $paths -Case $case -TaskId $taskId -TaskDetail $taskDetail -GeneratedText $generatedText -GoldText $goldText -ReviewBundle $reviewBundle -ErrorMessage "skip-generate 模式下未找到缓存生成稿"
            continue
        }
        else {
            $uploadIds = @()
            Get-ChildItem -LiteralPath $inputsDir -Filter *.pdf | Sort-Object Name | ForEach-Object {
                Write-Host "  上传: $($_.Name)"
                try {
                    $uploadId = Upload-Pdf -BaseUrlValue $BaseUrlValue -PdfPath $_.FullName
                    $uploadIds += $uploadId
                    Write-Host "    -> upload_id: $uploadId"
                }
                catch {
                    Write-Host "    上传失败: $($_.Exception.Message)"
                }
            }

            if ($uploadIds.Count -eq 0) {
                $report.test_cases += Write-FailureCaseSummary -Paths $paths -Case $case -TaskId $taskId -TaskDetail $taskDetail -GeneratedText $generatedText -GoldText $goldText -ReviewBundle $reviewBundle -ErrorMessage "无文件成功上传"
                continue
            }

            try {
                $taskId = Start-StandardChain -BaseUrlValue $BaseUrlValue -Case $case -UploadIds $uploadIds
                Write-Host "  task_id: $taskId"
                $taskDetail = Poll-TaskCompletion -BaseUrlValue $BaseUrlValue -TaskId $taskId -MaxWait $MaxWait -PollInterval $PollInterval
            }
            catch {
                $report.test_cases += Write-FailureCaseSummary -Paths $paths -Case $case -TaskId $taskId -TaskDetail $taskDetail -GeneratedText $generatedText -GoldText $goldText -ReviewBundle $reviewBundle -ErrorMessage $_.Exception.Message
                continue
            }

            Write-JsonFile -Path $paths.task_detail_latest -Payload $taskDetail
            Write-JsonFile -Path $paths.task_detail_snapshot -Payload $taskDetail

            $reviewBundle = Get-TaskReviewBundle -TaskDetail $taskDetail
            Write-ReviewBundleArtifacts -Paths $paths -ReviewBundle $reviewBundle

            $generatedText = Extract-GeneratedArticle -TaskDetail $taskDetail
            if ($generatedText) {
                Set-Content -LiteralPath $paths.generated_latest -Value $generatedText -Encoding UTF8
                Set-Content -LiteralPath $paths.generated_snapshot -Value $generatedText -Encoding UTF8
            }

            $taskEligibleForScoring = Test-TaskEligibleForScoring -TaskDetail $taskDetail
            if ([string]$taskDetail.status -ne "completed" -and -not $taskEligibleForScoring) {
                $hasTaskErrorMessage = (Test-ObjectKey -Object $taskDetail -Key "error_message") -and (Get-ObjectValue -Object $taskDetail -Key "error_message")
                $failureMessage = if ($hasTaskErrorMessage) {
                    "任务状态: $($taskDetail.status)；$($taskDetail.error_message)"
                } else {
                    "任务状态: $($taskDetail.status)"
                }
                $report.test_cases += Write-FailureCaseSummary -Paths $paths -Case $case -TaskId $taskId -TaskDetail $taskDetail -GeneratedText $generatedText -GoldText $goldText -ReviewBundle $reviewBundle -ErrorMessage $failureMessage
                continue
            }

            if (-not $generatedText) {
                $report.test_cases += Write-FailureCaseSummary -Paths $paths -Case $case -TaskId $taskId -TaskDetail $taskDetail -GeneratedText $generatedText -GoldText $goldText -ReviewBundle $reviewBundle -ErrorMessage "无法提取生成文章"
                continue
            }
        }

        try {
            $scoreResult = Score-WithLLM -Case $case -GoldText $goldText -GeneratedText $generatedText -ScoringKey $ScoringKey
        }
        catch {
            $message = $_.Exception.Message
            $isEnvironmentError = $message -match 'Incorrect API key|Authentication|Unauthorized|1309|到期|expired|invalid_api_key|missing_llm_api_key|NOT_FOUND'
            $scoreResult = @{
                dimensions = @()
                weighted_total = 0
                qualified = $false
                disqualify_reason = "评分失败: $message"
            }
            if ($isEnvironmentError) {
                $scoreResult.environment_error = "scoring_provider_unavailable"
            }
        }

        $scoreResult = Normalize-ScoringResult -Result $scoreResult
        $taskStatus = Get-TaskStatusLabel -TaskDetail $taskDetail

        $summaryPayload = [ordered]@{
            id = $case.id
            name = $case.name
            task_id = $taskId
            task_status = $taskStatus
            generated_length = if ($generatedText) { $generatedText.Length } else { 0 }
            gold_length = $goldText.Length
            qualified = [bool](Get-ObjectValue -Object $scoreResult -Key "qualified")
            weighted_total = if (Test-ObjectKey -Object $scoreResult -Key "weighted_total") { [double](Get-ObjectValue -Object $scoreResult -Key "weighted_total") } else { 0 }
            scoring_status = if ((Test-ObjectKey -Object $scoreResult -Key "environment_error") -and -not [string]::IsNullOrWhiteSpace([string](Get-ObjectValue -Object $scoreResult -Key "environment_error"))) { "environment_error" } else { "ok" }
            review_bundle_ready = if ($null -ne $reviewBundle -and (Test-ObjectKey -Object $reviewBundle -Key "review_bundle_ready")) { [bool](Get-ObjectValue -Object $reviewBundle -Key "review_bundle_ready") } else { $false }
            delivery_gate_passed = if ($null -ne (Get-TaskDetailDeliveryGateValue -TaskDetail $taskDetail -FieldName "delivery_word_count_gate_passed")) { [bool](Get-TaskDetailDeliveryGateValue -TaskDetail $taskDetail -FieldName "delivery_word_count_gate_passed") } else { $null }
            scoring_gate_passed = if ($null -ne (Get-TaskDetailDeliveryGateValue -TaskDetail $taskDetail -FieldName "scoring_word_count_gate_passed")) { [bool](Get-TaskDetailDeliveryGateValue -TaskDetail $taskDetail -FieldName "scoring_word_count_gate_passed") } else { $null }
            field_mapping_zh = Get-SummaryFieldMappingZh
            display_zh = $null
        }
        $summaryPayload.display_zh = Build-SummaryDisplayZh -Case $case -SummaryPayload $summaryPayload -ScoreResult $scoreResult

        Write-JsonFile -Path $paths.score_latest -Payload $scoreResult
        Write-JsonFile -Path $paths.score_snapshot -Payload $scoreResult
        Write-JsonFile -Path $paths.summary_latest -Payload $summaryPayload
        Write-JsonFile -Path $paths.summary_snapshot -Payload $summaryPayload

        $report.test_cases += [ordered]@{
            id = $case.id
            name = $case.name
            task_id = $taskId
            task_status = $taskStatus
            generated_length = $summaryPayload.generated_length
            gold_length = $summaryPayload.gold_length
            score = $scoreResult
            scoring_status = $summaryPayload.scoring_status
            artifacts = Get-CaseArtifactsPayload -Paths $paths -TaskDetail $taskDetail
        }
    }

    $allPass = $true
    foreach ($caseResult in $report.test_cases) {
        if (Test-ObjectKey -Object $caseResult -Key "error") {
            $allPass = $false
            continue
        }
        $score = Get-ObjectValue -Object $caseResult -Key "score"
        if (-not [bool](Get-ObjectValue -Object $score -Key "qualified")) {
            $allPass = $false
        }
    }

    $hasErrors = @($report.test_cases | Where-Object { Test-ObjectKey -Object $_ -Key "error" }).Count -gt 0
    $report.all_pass = $allPass
    $report.has_errors = $hasErrors
    $report.exit_code = if ($allPass -and -not $hasErrors) { 0 } else { 1 }

    $reportPath = Join-Path $OutputRoot "benchmark_report_$timestamp.json"
    $latestReportPath = Join-Path $OutputRoot "benchmark_report_latest.json"
    Write-JsonFile -Path $reportPath -Payload $report
    Write-JsonFile -Path $latestReportPath -Payload $report
    Write-Host "完整报告已保存: $reportPath"
    Write-Host "latest 报告已更新: $latestReportPath"

    return $report
}

$catalog = Resolve-CaseConfig -ConfigPath $CasesConfig

if ($ListSuites) {
    foreach ($suite in $catalog.Config.suites) {
        Write-Output "$($suite.id): $($suite.description)"
    }
    exit 0
}

if ($ListCases) {
    $casesToList = Resolve-TestCases -Catalog $catalog -SelectedCaseIds $CaseId
    foreach ($case in $casesToList) {
        Write-Output "$($case.id): $($case.name)"
    }
    exit 0
}

$selectedCases = Resolve-TestCases -Catalog $catalog -SelectedCaseIds $CaseId
$report = Invoke-Benchmark -BaseUrlValue $BaseUrl -OutputRoot $OutputDir -Cases $selectedCases -UseCachedGeneration:$SkipGenerate -ScoringKey $ScoringApiKey -MaxWait $MaxWaitSeconds -PollInterval $PollIntervalSeconds
exit [int]$report.exit_code
