[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = (Resolve-Path (Join-Path $CodeRoot '..\..\..')).Path
$DataRoot = Join-Path $WorkspaceRoot '1_data\gwas\outcome\ssc_finngen_r12_r13'
$ResultRoot = Join-Path $WorkspaceRoot '3_results\00_audit\R4A12FG2'

python (Join-Path $CodeRoot 'finngen_manifest_audit.py') `
  --config (Join-Path $CodeRoot 'target_config.json') `
  --data-root $DataRoot `
  --result-root $ResultRoot

if ($LASTEXITCODE -ne 0) {
  throw "FinnGen manifest audit failed with exit code $LASTEXITCODE"
}
