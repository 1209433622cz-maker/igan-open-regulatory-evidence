$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$PathsFile = Join-Path $WorkspaceRoot "0_admin\workspace_paths.json"
$WorkspacePaths = Get-Content -LiteralPath $PathsFile -Raw -Encoding UTF8 | ConvertFrom-Json
$FrozenStageRoot = $WorkspacePaths.frozen_stage_workspace_root
if ([string]::IsNullOrWhiteSpace($FrozenStageRoot)) { throw "frozen_stage_workspace_root is not defined in $PathsFile" }
$Validator = Join-Path $FrozenStageRoot "R4A11\protocol\validate_analysis_manifest_v11.py"
if (-not (Test-Path -LiteralPath $Validator -PathType Leaf)) {
    throw "Frozen manifest validator is missing: $Validator"
}

if (Test-Path -LiteralPath "D:\bioinfor\python.exe" -PathType Leaf) {
    $PythonExe = "D:\bioinfor\python.exe"
} else {
    $PythonExe = (Get-Command python -ErrorAction Stop).Source
}
& $PythonExe $Validator
$ToolExit = $LASTEXITCODE
if ($ToolExit -eq 0) {
    $ProtocolDir = Split-Path -Parent $Validator
    $ValidationDir = Join-Path $WorkspaceRoot "0_admin\validation\R4A11"
    Copy-Item -LiteralPath (Join-Path $ProtocolDir "analysis_manifest_v11_validation.json") -Destination (Join-Path $ValidationDir "analysis_manifest_v11_validation.json") -Force
    Copy-Item -LiteralPath (Join-Path $ProtocolDir "analysis_manifest_v11_validation.md") -Destination (Join-Path $ValidationDir "analysis_manifest_v11_validation.md") -Force
}
exit $ToolExit
