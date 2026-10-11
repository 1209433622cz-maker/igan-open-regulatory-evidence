[CmdletBinding()]
param(
  [ValidateSet('primary', 'all')]
  [string]$Selection = 'primary',
  [switch]$Execute
)

$ErrorActionPreference = 'Stop'
$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = (Resolve-Path (Join-Path $CodeRoot '..\..\..')).Path
$DataRoot = Join-Path $WorkspaceRoot '1_data\gwas\outcome\ssc_finngen_r12_r13'
$Plan = Join-Path $DataRoot 'metadata\download_plan.tsv'
$Receipt = Join-Path $WorkspaceRoot '3_results\00_audit\R4A12FG2\R4A12FG2_full_download_receipt.json'

$Arguments = @(
  (Join-Path $CodeRoot 'download_finngen_objects.py'),
  '--plan', $Plan,
  '--incoming-root', (Join-Path $DataRoot 'incoming'),
  '--receipt', $Receipt,
  '--selection', $Selection
)
if ($Execute) {
  $Arguments += '--execute'
}
python @Arguments
if ($LASTEXITCODE -ne 0) {
  throw "FinnGen download runner failed with exit code $LASTEXITCODE"
}
