Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Net.Http

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
    $Payload | ConvertTo-Json | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-DefaultCandidatePool {
    return Join-Path (Join-Path $PSScriptRoot "config") "ii_candidate_pool.json"
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

function Resolve-Candidate {
    param(
        [object]$PoolData,
        [string]$CandidateId
    )

    if (-not $PoolData.CandidateMap.ContainsKey($CandidateId)) {
        $available = ($PoolData.CandidateMap.Keys | Sort-Object) -join ", "
        throw "未知候选题: $CandidateId；可用值: $available"
    }
    return $PoolData.CandidateMap[$CandidateId]
}

function Resolve-InputPath {
    param(
        [string]$SourceRoot,
        [string]$RelativeOrAbsolutePath
    )

    if (Test-Path -LiteralPath $RelativeOrAbsolutePath) {
        return $RelativeOrAbsolutePath
    }
    return Join-Path $SourceRoot $RelativeOrAbsolutePath
}

function Convert-XmlPayloadToText {
    param(
        [string]$Xml,
        [string[]]$ParagraphClosers
    )

    $text = $Xml
    foreach ($closer in $ParagraphClosers) {
        $text = $text -replace [regex]::Escape($closer), "`n`n"
    }
    $text = $text -replace "<[^>]+>", " "
    $text = [System.Net.WebUtility]::HtmlDecode($text)
    $lines = $text -split "(`r`n|`n|`r)" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    return ($lines -join "`n")
}

function Read-ZipEntryText {
    param(
        [string]$ArchivePath,
        [string[]]$EntryPatterns,
        [string[]]$ParagraphClosers
    )

    $readPath = $ArchivePath
    $tempCopy = $null
    try {
        $zip = [System.IO.Compression.ZipFile]::OpenRead($readPath)
    }
    catch {
        if ($_.Exception.InnerException -is [System.IO.IOException] -or $_.Exception.Message -match "being used by another process") {
            $tempCopy = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName() + [System.IO.Path]::GetExtension($ArchivePath))
            [System.IO.File]::Copy($ArchivePath, $tempCopy, $true)
            $readPath = $tempCopy
            $zip = [System.IO.Compression.ZipFile]::OpenRead($readPath)
        }
        else {
            throw
        }
    }
    try {
        $chunks = @()
        foreach ($entry in $zip.Entries) {
            $matched = $false
            foreach ($pattern in $EntryPatterns) {
                if ($entry.FullName -like $pattern) {
                    $matched = $true
                    break
                }
            }
            if (-not $matched) {
                continue
            }
            $reader = [System.IO.StreamReader]::new($entry.Open())
            try {
                $xml = $reader.ReadToEnd()
            }
            finally {
                $reader.Dispose()
            }
            $chunk = Convert-XmlPayloadToText -Xml $xml -ParagraphClosers $ParagraphClosers
            if (-not [string]::IsNullOrWhiteSpace($chunk)) {
                $chunks += $chunk
            }
        }
        return ($chunks -join "`n`n")
    }
    finally {
        $zip.Dispose()
        if ($tempCopy -and (Test-Path -LiteralPath $tempCopy)) {
            Remove-Item -LiteralPath $tempCopy -Force -ErrorAction SilentlyContinue
        }
    }
}

function Extract-DocxText {
    param([string]$Path)
    return Read-ZipEntryText -ArchivePath $Path -EntryPatterns @("word/document.xml") -ParagraphClosers @("</w:p>", "</w:tr>")
}

function Extract-PptxText {
    param([string]$Path)
    return Read-ZipEntryText -ArchivePath $Path -EntryPatterns @("ppt/slides/slide*.xml") -ParagraphClosers @("</a:p>", "</p:txBody>")
}

function Extract-XlsxText {
    param([string]$Path)
    return Read-ZipEntryText -ArchivePath $Path -EntryPatterns @("xl/sharedStrings.xml", "xl/worksheets/*.xml") -ParagraphClosers @("</si>", "</row>")
}

function Extract-PdfText {
    param([string]$Path)

    try {
        $pages = Get-PdfPageTexts -Path $Path
        if ($pages.Count -eq 0) {
            return $null
        }
        return (($pages | ForEach-Object { $_.text }) -join "`n`n")
    }
    catch {
        return $null
    }
}

function Get-PdfTextExtractorPath {
    $candidates = @(
        "C:\Program Files\Git\mingw64\bin\pdftotext.exe",
        "C:\Program Files (x86)\Git\mingw64\bin\pdftotext.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $command = Get-Command pdftotext -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    return $null
}

function Invoke-PdfTextExtraction {
    param(
        [string]$PdfPath,
        [string]$TextPath
    )

    $extractor = Get-PdfTextExtractorPath
    if (-not $extractor) {
        throw "pdftotext_not_found"
    }

    $workingPdf = $PdfPath
    $tempPdf = $null
    try {
        $tempPdf = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName() + ".pdf")
        Copy-Item -LiteralPath $PdfPath -Destination $tempPdf -Force
        $workingPdf = $tempPdf

        $workingDirectory = Split-Path -Parent $extractor
        $process = Start-Process -FilePath $extractor -ArgumentList @("-q", "-layout", $workingPdf, $TextPath) -WorkingDirectory $workingDirectory -Wait -NoNewWindow -PassThru
        if ($process.ExitCode -ne 0) {
            throw "pdftotext_exit_$($process.ExitCode)"
        }
        if (-not (Test-Path -LiteralPath $TextPath)) {
            throw "pdftotext_no_output"
        }
    }
    finally {
        if ($tempPdf -and (Test-Path -LiteralPath $tempPdf)) {
            Remove-Item -LiteralPath $tempPdf -Force -ErrorAction SilentlyContinue
        }
    }
}

function Get-PdfPageTexts {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "pdf_not_found: $Path"
    }

    $tempFile = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName() + ".txt")
    try {
        Invoke-PdfTextExtraction -PdfPath $Path -TextPath $tempFile
        $raw = Get-Content -LiteralPath $tempFile -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return @()
        }

        $pages = @()
        $segments = $raw -split [char]12
        for ($i = 0; $i -lt $segments.Count; $i++) {
            $pageText = $segments[$i].Trim()
            if (-not [string]::IsNullOrWhiteSpace($pageText)) {
                $pages += [pscustomobject]@{
                    page_number = $i + 1
                    text = $pageText
                }
            }
        }
        return $pages
    }
    finally {
        if (Test-Path -LiteralPath $tempFile) {
            Remove-Item -LiteralPath $tempFile -Force -ErrorAction SilentlyContinue
        }
    }
}

function Find-PdfEvidenceMatches {
    param(
        [string]$Path,
        [string[]]$Patterns,
        [int]$ContextChars = 160
    )

    $pages = @(Get-PdfPageTexts -Path $Path)
    $results = @()

    foreach ($pattern in $Patterns) {
        $matched = $false
        foreach ($page in $pages) {
            $regex = [regex]::new($pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            $match = $regex.Match($page.text)
            if (-not $match.Success) {
                continue
            }

            $start = [Math]::Max(0, $match.Index - $ContextChars)
            $length = [Math]::Min($page.text.Length - $start, $match.Length + (2 * $ContextChars))
            $excerpt = $page.text.Substring($start, $length).Trim()
            $results += [pscustomobject]@{
                pattern = $pattern
                page_number = $page.page_number
                matched_text = $match.Value
                excerpt = $excerpt
            }
            $matched = $true
            break
        }

        if (-not $matched) {
            $results += [pscustomobject]@{
                pattern = $pattern
                page_number = $null
                matched_text = $null
                excerpt = $null
            }
        }
    }

    return $results
}

function Extract-FileText {
    param([string]$Path)

    $extension = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
    switch ($extension) {
        ".txt" { return [pscustomobject]@{ status = "ok"; text = (Get-Content -LiteralPath $Path -Raw) } }
        ".md" { return [pscustomobject]@{ status = "ok"; text = (Get-Content -LiteralPath $Path -Raw) } }
        ".json" { return [pscustomobject]@{ status = "ok"; text = (Get-Content -LiteralPath $Path -Raw) } }
        ".csv" { return [pscustomobject]@{ status = "ok"; text = (Get-Content -LiteralPath $Path -Raw) } }
        ".docx" { return [pscustomobject]@{ status = "ok"; text = (Extract-DocxText -Path $Path) } }
        ".pptx" { return [pscustomobject]@{ status = "ok"; text = (Extract-PptxText -Path $Path) } }
        ".xlsx" { return [pscustomobject]@{ status = "ok"; text = (Extract-XlsxText -Path $Path) } }
        ".pdf" {
            $pdfText = Extract-PdfText -Path $Path
            if ($null -eq $pdfText) {
                return [pscustomobject]@{ status = "unsupported"; text = "" }
            }
            return [pscustomobject]@{ status = "ok"; text = $pdfText }
        }
        ".jpg" { return [pscustomobject]@{ status = "unsupported"; text = "" } }
        ".jpeg" { return [pscustomobject]@{ status = "unsupported"; text = "" } }
        ".png" { return [pscustomobject]@{ status = "unsupported"; text = "" } }
        default { return [pscustomobject]@{ status = "unsupported"; text = "" } }
    }
}

function Try-GetMemberValue {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

function Get-PrimaryHomePath {
    foreach ($candidate in @(
        [string]$env:XIAGEDAO_WHITEBOX_HOME,
        [string]$env:USERPROFILE,
        [string]$env:HOME,
        [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    )) {
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            return $candidate
        }
    }

    throw "无法推断用户主目录，请显式设置 XIAGEDAO_WHITEBOX_HOME。"
}

function Get-DefaultOpencodeAuthPath {
    if (-not [string]::IsNullOrWhiteSpace([string]$env:XIAGEDAO_WHITEBOX_AUTH_PATH)) {
        return $env:XIAGEDAO_WHITEBOX_AUTH_PATH
    }
    if (-not [string]::IsNullOrWhiteSpace([string]$env:OPENCODE_AUTH_PATH)) {
        return $env:OPENCODE_AUTH_PATH
    }

    return Join-Path (Join-Path (Get-PrimaryHomePath) ".local\share\opencode") "auth.json"
}

function Get-DefaultOpencodeConfigPath {
    if (-not [string]::IsNullOrWhiteSpace([string]$env:XIAGEDAO_WHITEBOX_CONFIG_PATH)) {
        return $env:XIAGEDAO_WHITEBOX_CONFIG_PATH
    }
    if (-not [string]::IsNullOrWhiteSpace([string]$env:OPENCODE_CONFIG_PATH)) {
        return $env:OPENCODE_CONFIG_PATH
    }

    return Join-Path (Join-Path (Get-PrimaryHomePath) ".config\opencode") "opencode.json"
}

function Get-DefaultWhiteboxProfileConfigPath {
    return Join-Path (Join-Path $PSScriptRoot "config") "whitebox_llm_profiles.json"
}

function Try-ReadJsonFile {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    try {
        return Read-JsonFile -Path $Path
    }
    catch {
        return $null
    }
}

function Get-WhiteboxProfileConfig {
    param(
        [string]$ProfileName = "",
        [string]$ProfileConfigPath = ""
    )

    if ([string]::IsNullOrWhiteSpace($ProfileName)) {
        return $null
    }

    $configPath = if (-not [string]::IsNullOrWhiteSpace($ProfileConfigPath)) {
        $ProfileConfigPath
    }
    else {
        Get-DefaultWhiteboxProfileConfigPath
    }

    $config = Try-ReadJsonFile -Path $configPath
    if ($null -eq $config) {
        return $null
    }

    $profiles = Try-GetMemberValue -Object $config -Name "profiles"
    if ($null -eq $profiles) {
        return $null
    }

    return Try-GetMemberValue -Object $profiles -Name $ProfileName
}

function Get-EnvValueByName {
    param([string]$Name)

    if ([string]::IsNullOrWhiteSpace($Name)) {
        return ""
    }

    $envItem = Get-Item -LiteralPath ("Env:{0}" -f $Name) -ErrorAction SilentlyContinue
    if ($null -eq $envItem) {
        return ""
    }

    return [string]$envItem.Value
}

function Get-WhiteboxProfileEnvValue {
    param(
        [string]$ProfileName,
        [string]$Field
    )

    if ([string]::IsNullOrWhiteSpace($ProfileName) -or [string]::IsNullOrWhiteSpace($Field)) {
        return ""
    }

    $normalizedProfile = ($ProfileName -replace "[^A-Za-z0-9]", "_").ToUpperInvariant()
    $envName = "XIAGEDAO_WHITEBOX_{0}_{1}" -f $normalizedProfile, $Field.ToUpperInvariant()
    $envItem = Get-Item -LiteralPath ("Env:{0}" -f $envName) -ErrorAction SilentlyContinue
    if ($null -eq $envItem) {
        return ""
    }

    return [string]$envItem.Value
}

function Resolve-WhiteboxProfileResourcePath {
    param(
        [string]$ProfileConfigPath = "",
        [string]$ResourcePath = ""
    )

    if ([string]::IsNullOrWhiteSpace($ResourcePath)) {
        return ""
    }

    if (Test-Path -LiteralPath $ResourcePath) {
        return $ResourcePath
    }

    $baseDirectory = if (-not [string]::IsNullOrWhiteSpace($ProfileConfigPath)) {
        Split-Path -Parent $ProfileConfigPath
    }
    else {
        Join-Path $PSScriptRoot "config"
    }

    $candidate = Join-Path $baseDirectory $ResourcePath
    if (Test-Path -LiteralPath $candidate) {
        return $candidate
    }

    return ""
}

function Get-WhiteboxProfilePromptAugmentation {
    param(
        [string]$ProfileName = "",
        [string]$ProfileConfigPath = ""
    )

    $profileConfig = Get-WhiteboxProfileConfig -ProfileName $ProfileName -ProfileConfigPath $ProfileConfigPath
    if ($null -eq $profileConfig) {
        return ""
    }

    $parts = @()
    $promptPrefix = [string](Try-GetMemberValue -Object $profileConfig -Name "prompt_prefix")
    if (-not [string]::IsNullOrWhiteSpace($promptPrefix)) {
        $parts += "【模块角色上下文】"
        $parts += $promptPrefix.Trim()
    }

    $fewShotPath = Resolve-WhiteboxProfileResourcePath -ProfileConfigPath $ProfileConfigPath -ResourcePath ([string](Try-GetMemberValue -Object $profileConfig -Name "few_shot_path"))
    if (-not [string]::IsNullOrWhiteSpace($fewShotPath)) {
        $fewShotText = Get-Content -LiteralPath $fewShotPath -Raw -Encoding UTF8
        if (-not [string]::IsNullOrWhiteSpace($fewShotText)) {
            $parts += "【模块样例或附加约束】"
            $parts += $fewShotText.Trim()
        }
    }

    return (($parts | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join "`n")
}

function Build-WhiteboxPromptWithProfile {
    param(
        [string]$Prompt,
        [string]$ProfileName = "",
        [string]$ProfileConfigPath = ""
    )

    $augmentation = Get-WhiteboxProfilePromptAugmentation -ProfileName $ProfileName -ProfileConfigPath $ProfileConfigPath
    if ([string]::IsNullOrWhiteSpace($augmentation)) {
        return $Prompt
    }

    return @"
$augmentation

$Prompt
"@
}

function Get-AuthProfileValue {
    param(
        [object]$AuthData,
        [string[]]$ProfileNames
    )

    foreach ($profileName in $ProfileNames) {
        $profile = Try-GetMemberValue -Object $AuthData -Name $profileName
        if ($null -eq $profile) {
            continue
        }

        $type = Try-GetMemberValue -Object $profile -Name "type"
        $key = Try-GetMemberValue -Object $profile -Name "key"
        if ($type -eq "api" -and -not [string]::IsNullOrWhiteSpace($key)) {
            return [pscustomobject]@{
                profile_name = $profileName
                key = $key
            }
        }
    }
    return $null
}

function Get-ConfigProviderSettings {
    param(
        [object]$ConfigData,
        [string]$ProviderName,
        [string]$ModelName
    )

    $providers = Try-GetMemberValue -Object $ConfigData -Name "provider"
    $provider = Try-GetMemberValue -Object $providers -Name $ProviderName
    if ($null -eq $provider) {
        return $null
    }

    $models = Try-GetMemberValue -Object $provider -Name "models"
    $modelEntry = Try-GetMemberValue -Object $models -Name $ModelName
    if ($null -eq $modelEntry) {
        return $null
    }

    $options = Try-GetMemberValue -Object $provider -Name "options"
    $baseUrl = Try-GetMemberValue -Object $options -Name "baseURL"
    $apiKey = Try-GetMemberValue -Object $options -Name "apiKey"
    $npmName = Try-GetMemberValue -Object $provider -Name "npm"

    return [pscustomobject]@{
        provider_name = $ProviderName
        model_name = $ModelName
        base_url = $baseUrl
        api_key = $apiKey
        adapter = $npmName
        protocol = Get-WhiteboxLlmProtocol -Adapter $npmName -BaseUrl $baseUrl
    }
}

function Get-WhiteboxLlmProtocol {
    param(
        [string]$Adapter = "",
        [string]$BaseUrl = ""
    )

    if (-not [string]::IsNullOrWhiteSpace($BaseUrl) -and $BaseUrl -match "/apps/anthropic") {
        return "anthropic"
    }
    if (-not [string]::IsNullOrWhiteSpace($BaseUrl) -and $BaseUrl -like "https://api.kimi.com/coding*") {
        return "anthropic"
    }
    if (-not [string]::IsNullOrWhiteSpace($Adapter) -and $Adapter -like "*anthropic*") {
        return "anthropic"
    }
    return "openai"
}

function Test-IsCodingPlanUrl {
    param([string]$Url = "")

    if ([string]::IsNullOrWhiteSpace($Url)) {
        return $false
    }
    return $Url -like "https://coding.dashscope.aliyuncs.com*"
}

function Resolve-WhiteboxPreferredConfig {
    param(
        [object]$AuthData,
        [object]$ConfigData
    )

    $preferredMatrix = @(
        [pscustomobject]@{
            provider_name = "bailian-coding-plan"
            model_name = "kimi-k2.5"
            auth_profiles = @()
        },
        [pscustomobject]@{
            provider_name = "bailian-coding-plan"
            model_name = "qwen3-coder-plus"
            auth_profiles = @()
        },
        [pscustomobject]@{
            provider_name = "bailian-coding-plan"
            model_name = "qwen3-coder-next"
            auth_profiles = @()
        },
        [pscustomobject]@{
            provider_name = "volcengine-plan"
            model_name = "kimi-k2.5"
            auth_profiles = @()
        },
        [pscustomobject]@{
            provider_name = "volcengine-plan"
            model_name = "ark-code-latest"
            auth_profiles = @()
        }
    )

    foreach ($candidate in $preferredMatrix) {
        $providerSettings = Get-ConfigProviderSettings -ConfigData $ConfigData -ProviderName $candidate.provider_name -ModelName $candidate.model_name
        if ($null -eq $providerSettings) {
            continue
        }

        if ($providerSettings.adapter -and $providerSettings.adapter -notlike "*openai-compatible*" -and $providerSettings.adapter -notlike "*anthropic*") {
            continue
        }

        $authProfile = if (@($candidate.auth_profiles).Count -gt 0) {
            Get-AuthProfileValue -AuthData $AuthData -ProfileNames $candidate.auth_profiles
        }
        else {
            $null
        }

        $resolvedKey = if ($authProfile) { $authProfile.key } elseif (-not [string]::IsNullOrWhiteSpace($providerSettings.api_key)) { $providerSettings.api_key } else { "" }
        if ([string]::IsNullOrWhiteSpace($resolvedKey)) {
            continue
        }

        return [pscustomobject]@{
            api_key = $resolvedKey
            base_url = $providerSettings.base_url
            model = $providerSettings.model_name
            protocol = $providerSettings.protocol
            source = if ($authProfile) { "auth:$($authProfile.profile_name)+config:$($providerSettings.provider_name)/$($providerSettings.model_name)" } else { "config:$($providerSettings.provider_name)/$($providerSettings.model_name)" }
        }
    }

    return $null
}

function Get-WhiteboxLlmSettings {
    param(
        [string]$ApiKeyOverride = "",
        [string]$ProfileName = "",
        [string]$ProfileConfigPath = ""
    )

    $baseUrlOverride = if ($env:XIAGEDAO_WHITEBOX_BASE_URL) { $env:XIAGEDAO_WHITEBOX_BASE_URL } elseif ($env:ANTHROPIC_BASE_URL) { $env:ANTHROPIC_BASE_URL } elseif ($env:XIAGEDAO_LLM_BASE_URL) { $env:XIAGEDAO_LLM_BASE_URL } elseif ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL } else { "" }
    $baseUrlOverrideSource = if ($env:XIAGEDAO_WHITEBOX_BASE_URL) { "env:XIAGEDAO_WHITEBOX_BASE_URL" } elseif ($env:ANTHROPIC_BASE_URL) { "env:ANTHROPIC_BASE_URL" } elseif ($env:XIAGEDAO_LLM_BASE_URL) { "env:XIAGEDAO_LLM_BASE_URL" } elseif ($env:OPENAI_BASE_URL) { "env:OPENAI_BASE_URL" } else { "" }
    $isExplicitWhiteboxOverride = [bool]$env:XIAGEDAO_WHITEBOX_BASE_URL
    $modelOverride = if ($env:XIAGEDAO_WHITEBOX_MODEL) { $env:XIAGEDAO_WHITEBOX_MODEL } elseif ($env:MODEL) { $env:MODEL } elseif ($env:LLM_MODEL) { $env:LLM_MODEL } else { "" }
    $authData = Try-ReadJsonFile -Path (Get-DefaultOpencodeAuthPath)
    $configData = Try-ReadJsonFile -Path (Get-DefaultOpencodeConfigPath)
    $preferredConfig = Resolve-WhiteboxPreferredConfig -AuthData $authData -ConfigData $configData
    $preferCodingPlanConfig = $preferredConfig -and $preferredConfig.protocol -eq "anthropic" -and (Test-IsCodingPlanUrl -Url $preferredConfig.base_url)
    # 只有显式白盒覆盖（XIAGEDAO_WHITEBOX_BASE_URL）或无合法 preferredConfig 时，才允许 env 覆盖
    # 其余环境变量（ANTHROPIC_BASE_URL / OPENAI_BASE_URL 等）不得劫持已有的 coding-plan 配置
    $useOpenAiStyleOverride = $baseUrlOverride -and $baseUrlOverride -notmatch "/anthropic" -and ($isExplicitWhiteboxOverride -or -not $preferCodingPlanConfig)

    $apiKey = ""
    $baseUrl = ""
    $model = ""
    $protocol = "openai"
    $source = ""

    if ($preferCodingPlanConfig -and -not $useOpenAiStyleOverride) {
        # 使用阿里云 coding plan 配置（只有 XIAGEDAO_WHITEBOX_BASE_URL 能覆盖）
        if ($baseUrlOverride -and -not $isExplicitWhiteboxOverride) {
            Write-Host "[WARN] 检测到环境变量 $baseUrlOverrideSource = $baseUrlOverride 试图覆盖 coding-plan 配置，已忽略。如需强制覆盖，请设 XIAGEDAO_WHITEBOX_BASE_URL。"
        }
        $apiKey = if (-not [string]::IsNullOrWhiteSpace($ApiKeyOverride)) {
            $ApiKeyOverride
        }
        elseif (-not [string]::IsNullOrWhiteSpace($preferredConfig.api_key)) {
            $preferredConfig.api_key
        }
        elseif (-not [string]::IsNullOrWhiteSpace($env:XIAGEDAO_API_KEY)) {
            $env:XIAGEDAO_API_KEY
        }
        elseif (-not [string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
            $env:OPENAI_API_KEY
        }
        else {
            ""
        }
        $baseUrl = $preferredConfig.base_url
        $model = if ($modelOverride) { $modelOverride } else { $preferredConfig.model }
        $protocol = $preferredConfig.protocol
        $source = if (-not [string]::IsNullOrWhiteSpace($ApiKeyOverride)) { "override+$($preferredConfig.source)" } else { $preferredConfig.source }
    }
    elseif ($useOpenAiStyleOverride) {
        # 使用 OpenAI 兼容端点覆盖
        $apiKey = if (-not [string]::IsNullOrWhiteSpace($ApiKeyOverride)) {
            $ApiKeyOverride
        }
        elseif (-not [string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
            $env:OPENAI_API_KEY
        }
        elseif ($preferredConfig) {
            $preferredConfig.api_key
        }
        else {
            ""
        }
        $baseUrl = $baseUrlOverride
        $model = if ($modelOverride) { $modelOverride } elseif ($preferredConfig) { $preferredConfig.model } else { "kimi-k2.5" }
        $protocol = "openai"
        $source = "$baseUrlOverrideSource+override"
    }
    elseif (-not [string]::IsNullOrWhiteSpace($ApiKeyOverride)) {
        $apiKey = $ApiKeyOverride
        $baseUrl = if ($baseUrlOverride) { $baseUrlOverride } elseif ($preferredConfig) { $preferredConfig.base_url } else { "https://api.openai.com/v1" }
        $model = if ($modelOverride) { $modelOverride } elseif ($preferredConfig) { $preferredConfig.model } else { "gpt-4o-mini" }
        $protocol = Get-WhiteboxLlmProtocol -BaseUrl $baseUrl
        $source = "override"
    }
    elseif (-not [string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
        $apiKey = $env:OPENAI_API_KEY
        $baseUrl = if ($baseUrlOverride) { $baseUrlOverride } elseif ($preferredConfig) { $preferredConfig.base_url } else { "https://api.openai.com/v1" }
        $model = if ($modelOverride) { $modelOverride } elseif ($preferredConfig) { $preferredConfig.model } else { "gpt-4o-mini" }
        $protocol = Get-WhiteboxLlmProtocol -BaseUrl $baseUrl
        $source = "env:OPENAI_API_KEY"
    }
    elseif (-not [string]::IsNullOrWhiteSpace($env:ANTHROPIC_API_KEY)) {
        $apiKey = $env:ANTHROPIC_API_KEY
        $baseUrl = if ($baseUrlOverride) { $baseUrlOverride } elseif ($preferredConfig) { $preferredConfig.base_url } else { "https://api.anthropic.com/v1" }
        $model = if ($modelOverride) { $modelOverride } elseif ($preferredConfig) { $preferredConfig.model } else { "claude-3-5-sonnet-latest" }
        $protocol = Get-WhiteboxLlmProtocol -BaseUrl $baseUrl
        $source = "env:ANTHROPIC_API_KEY"
    }
    elseif (-not [string]::IsNullOrWhiteSpace($env:XIAGEDAO_API_KEY)) {
        $apiKey = $env:XIAGEDAO_API_KEY
        $baseUrl = if ($baseUrlOverride) { $baseUrlOverride } elseif ($preferredConfig) { $preferredConfig.base_url } else { "https://api.openai.com/v1" }
        $model = if ($modelOverride) { $modelOverride } elseif ($preferredConfig) { $preferredConfig.model } else { "gpt-4o-mini" }
        $protocol = Get-WhiteboxLlmProtocol -BaseUrl $baseUrl
        $source = "env:XIAGEDAO_API_KEY"
    }
    elseif ($preferredConfig) {
        $apiKey = $preferredConfig.api_key
        $baseUrl = if ($baseUrlOverride) { $baseUrlOverride } else { $preferredConfig.base_url }
        $model = if ($modelOverride) { $modelOverride } else { $preferredConfig.model }
        $protocol = $preferredConfig.protocol
        $source = $preferredConfig.source
    }
    else {
        $apiKey = ""
        $baseUrl = if ($baseUrlOverride) { $baseUrlOverride } else { "https://api.openai.com/v1" }
        $model = if ($modelOverride) { $modelOverride } else { "gpt-4o-mini" }
        $protocol = Get-WhiteboxLlmProtocol -BaseUrl $baseUrl
        $source = "missing"
    }

    $profileConfig = Get-WhiteboxProfileConfig -ProfileName $ProfileName -ProfileConfigPath $ProfileConfigPath
    $profileModelOverride = Get-WhiteboxProfileEnvValue -ProfileName $ProfileName -Field "MODEL"
    $profileBaseUrlOverride = Get-WhiteboxProfileEnvValue -ProfileName $ProfileName -Field "BASE_URL"
    $profileProtocolOverride = Get-WhiteboxProfileEnvValue -ProfileName $ProfileName -Field "PROTOCOL"
    $profileApiKeyOverride = Get-WhiteboxProfileEnvValue -ProfileName $ProfileName -Field "API_KEY"

    $profileApiKeyEnvByName = if ($profileConfig) {
        Get-EnvValueByName -Name ([string](Try-GetMemberValue -Object $profileConfig -Name "api_key_env"))
    }
    else {
        ""
    }
    $profileBaseUrlEnvByName = if ($profileConfig) {
        Get-EnvValueByName -Name ([string](Try-GetMemberValue -Object $profileConfig -Name "base_url_env"))
    }
    else {
        ""
    }
    $profileModelEnvByName = if ($profileConfig) {
        Get-EnvValueByName -Name ([string](Try-GetMemberValue -Object $profileConfig -Name "model_env"))
    }
    else {
        ""
    }
    $profileProtocolEnvByName = if ($profileConfig) {
        Get-EnvValueByName -Name ([string](Try-GetMemberValue -Object $profileConfig -Name "protocol_env"))
    }
    else {
        ""
    }

    if (-not [string]::IsNullOrWhiteSpace($profileApiKeyOverride) -and [string]::IsNullOrWhiteSpace($ApiKeyOverride)) {
        $apiKey = $profileApiKeyOverride
    }
    elseif (-not [string]::IsNullOrWhiteSpace($profileApiKeyEnvByName) -and [string]::IsNullOrWhiteSpace($ApiKeyOverride)) {
        $apiKey = $profileApiKeyEnvByName
    }

    $resolvedProfileBaseUrl = if (-not [string]::IsNullOrWhiteSpace($profileBaseUrlOverride)) {
        $profileBaseUrlOverride
    }
    elseif (-not [string]::IsNullOrWhiteSpace($profileBaseUrlEnvByName)) {
        $profileBaseUrlEnvByName
    }
    elseif ($profileConfig) {
        [string](Try-GetMemberValue -Object $profileConfig -Name "base_url")
    }
    else {
        ""
    }
    if (-not [string]::IsNullOrWhiteSpace($resolvedProfileBaseUrl)) {
        $baseUrl = $resolvedProfileBaseUrl
        if ([string]::IsNullOrWhiteSpace($profileProtocolOverride)) {
            $protocol = Get-WhiteboxLlmProtocol -BaseUrl $baseUrl
        }
    }

    $resolvedProfileModel = if (-not [string]::IsNullOrWhiteSpace($profileModelOverride)) {
        $profileModelOverride
    }
    elseif (-not [string]::IsNullOrWhiteSpace($profileModelEnvByName)) {
        $profileModelEnvByName
    }
    elseif ($profileConfig) {
        [string](Try-GetMemberValue -Object $profileConfig -Name "model")
    }
    else {
        ""
    }
    if (-not [string]::IsNullOrWhiteSpace($resolvedProfileModel)) {
        $model = $resolvedProfileModel
    }

    $resolvedProfileProtocol = if (-not [string]::IsNullOrWhiteSpace($profileProtocolOverride)) {
        $profileProtocolOverride
    }
    elseif (-not [string]::IsNullOrWhiteSpace($profileProtocolEnvByName)) {
        $profileProtocolEnvByName
    }
    elseif ($profileConfig) {
        [string](Try-GetMemberValue -Object $profileConfig -Name "protocol")
    }
    else {
        ""
    }
    if (-not [string]::IsNullOrWhiteSpace($resolvedProfileProtocol)) {
        $protocol = $resolvedProfileProtocol
    }

    if (-not [string]::IsNullOrWhiteSpace($ProfileName)) {
        $source = if ($profileConfig) {
            "$source+profile:$ProfileName"
        }
        else {
            "$source+profile:$ProfileName(unconfigured)"
        }
    }

    return [pscustomobject]@{
        api_key = $apiKey
        base_url = $baseUrl
        model = $model
        protocol = $protocol
        source = $source
    }
}

function Invoke-WhiteboxLlm {
    param(
        [string]$Prompt,
        [string]$ApiKeyOverride = "",
        [double]$Temperature = 0.2,
        [string]$ProfileName = "",
        [string]$ProfileConfigPath = ""
    )

    $settings = Get-WhiteboxLlmSettings -ApiKeyOverride $ApiKeyOverride -ProfileName $ProfileName -ProfileConfigPath $ProfileConfigPath
    if (-not $settings.api_key) {
        throw "missing_llm_api_key"
    }

    $handler = [System.Net.Http.HttpClientHandler]::new()
    $handler.UseProxy = $false
    $client = [System.Net.Http.HttpClient]::new($handler)
    try {
        $client.Timeout = [TimeSpan]::FromSeconds(600)
        $client.DefaultRequestHeaders.UserAgent.ParseAdd("python-httpx/0.28.1")
        $baseUrl = $settings.base_url.TrimEnd("/")
        $request = $null
        if ($settings.protocol -eq "anthropic") {
            $payload = @{
                model = $settings.model
                max_tokens = 8192
                temperature = $Temperature
                messages = @(@{ role = "user"; content = $Prompt })
            } | ConvertTo-Json
            $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$baseUrl/messages")
            $request.Headers.Add("x-api-key", $settings.api_key)
            $request.Headers.Add("anthropic-version", "2023-06-01")
            $request.Content = [System.Net.Http.StringContent]::new($payload, [System.Text.Encoding]::UTF8, "application/json")
        }
        else {
            $payload = @{
                model = $settings.model
                messages = @(@{ role = "user"; content = $Prompt })
                temperature = $Temperature
            } | ConvertTo-Json
            $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Post, "$baseUrl/chat/completions")
            $request.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $settings.api_key)
            $request.Content = [System.Net.Http.StringContent]::new($payload, [System.Text.Encoding]::UTF8, "application/json")
        }
        $response = $client.SendAsync($request).GetAwaiter().GetResult()
        $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
        if (-not $response.IsSuccessStatusCode) {
            throw "llm_request_failed: $($response.StatusCode) $body"
        }
        $parsed = $body | ConvertFrom-Json
        if ($settings.protocol -eq "anthropic") {
            return (@($parsed.content | Where-Object { $_.type -eq "text" } | ForEach-Object { $_.text }) -join "")
        }
        return $parsed.choices[0].message.content
    }
    catch {
        $message = $_.Exception.Message
        if ($message -match "无法加载或初始化请求的服务提供程序") {
            throw "llm_transport_unavailable: $message；当前 LLM 来源：$($settings.source)"
        }
        throw
    }
    finally {
        $client.Dispose()
        $handler.Dispose()
    }
}

function Try-ParseJsonText {
    param([string]$Text)

    try {
        return $Text | ConvertFrom-Json
    }
    catch {
    }

    if ($Text -match '```json\s*(\{[\s\S]*\})\s*```') {
        try {
            return $matches[1] | ConvertFrom-Json
        }
        catch {
        }
    }
    return $null
}
