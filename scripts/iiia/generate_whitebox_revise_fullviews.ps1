param(
    [string]$EvalRoot = "D:\汇度编辑部1\侠客岛-runtime\iiia_whitebox_revise_on_baseline_eval\20260412_0128_baseline_fixed_rescore",
    [string]$OutputDir = "D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\07_白盒施工包\01_第一轮白盒完整可实验版\03_返修Loop单题全貌档案"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

$scriptPath = Join-Path $PSScriptRoot "generate_whitebox_revise_fullviews.py"
& $python $scriptPath "--eval-root" $EvalRoot "--output-dir" $OutputDir
