$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$PathsFile = Join-Path $WorkspaceRoot "0_admin\workspace_paths.json"
$WorkspacePaths = Get-Content -LiteralPath $PathsFile -Raw -Encoding UTF8 | ConvertFrom-Json
$FrozenStageRoot = $WorkspacePaths.frozen_stage_workspace_root
if ([string]::IsNullOrWhiteSpace($FrozenStageRoot)) { throw "frozen_stage_workspace_root is not defined in $PathsFile" }
$FrozenRunner = Join-Path $FrozenStageRoot "R4A11\access\RUN_ACCESS_REFRESH.ps1"
if (-not (Test-Path -LiteralPath $FrozenRunner -PathType Leaf)) {
    throw "Frozen access audit runner is missing: $FrozenRunner"
}

& $FrozenRunner
$ToolExit = $LASTEXITCODE
if ($ToolExit -eq 0) {
    $SourceDir = Join-Path $FrozenStageRoot "R4A11\access"
    $ResultDir = Join-Path $WorkspaceRoot "3_results\00_audit\public_access"
    $ValidationDir = Join-Path $WorkspaceRoot "0_admin\validation\R4A11"
    New-Item -ItemType Directory -Path $ResultDir -Force | Out-Null
    foreach ($Name in @("R4A11_public_access_raw_compact.json", "R4A11_public_access_decision.json", "R4A11_public_access_validation.json")) {
        Copy-Item -LiteralPath (Join-Path $SourceDir $Name) -Destination (Join-Path $ResultDir $Name) -Force
    }
    Copy-Item -LiteralPath (Join-Path $SourceDir "R4A11_public_access_validation.json") -Destination (Join-Path $ValidationDir "R4A11_public_access_validation.json") -Force
}
exit $ToolExit
