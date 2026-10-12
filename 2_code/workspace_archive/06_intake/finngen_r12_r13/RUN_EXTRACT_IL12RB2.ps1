[CmdletBinding()]
param(
  [ValidateSet('R12', 'R13')]
  [string]$Release = 'R13'
)

$ErrorActionPreference = 'Stop'
$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = (Resolve-Path (Join-Path $CodeRoot '..\..\..')).Path
$DataRoot = Join-Path $WorkspaceRoot '1_data\gwas\outcome\ssc_finngen_r12_r13'
$InputDir = Join-Path $DataRoot "incoming\$Release\M13_SYSTSLCE"
$InputFile = Join-Path $InputDir "finngen_${Release}_M13_SYSTSLCE.gz"
$IndexFile = $InputFile + '.tbi'
$OutputDir = Join-Path $DataRoot 'regions\IL12RB2_GRCh38_pm500kb'
$OutputFile = Join-Path $OutputDir "${Release}_M13_SYSTSLCE.IL12RB2_GRCh38_pm500kb.tsv"
$Validation = Join-Path $WorkspaceRoot "3_results\00_audit\R4A12FG2\${Release}_M13_SYSTSLCE_IL12RB2_P0.json"
$Region = '1:66840524-67840524'

foreach ($Path in @($InputFile, $IndexFile)) {
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Required downloaded object is missing: $Path"
  }
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$WslInput = (& wsl.exe -d Ubuntu-22.04 --exec wslpath -a $InputFile).Trim()
$WslOutput = (& wsl.exe -d Ubuntu-22.04 --exec wslpath -a $OutputFile).Trim()
if (-not $WslInput -or -not $WslOutput) {
  throw 'wslpath conversion failed'
}

& wsl.exe -d Ubuntu-22.04 --exec /bin/bash -lc 'set -euo pipefail; tabix -h "$1" "$2" > "$3"' -- $WslInput $Region $WslOutput
if ($LASTEXITCODE -ne 0) {
  throw "WSL tabix extraction failed with exit code $LASTEXITCODE"
}

python (Join-Path $CodeRoot 'p0_validate_finngen_region.py') `
  --input $OutputFile `
  --config (Join-Path $CodeRoot 'target_config.json') `
  --release $Release `
  --endpoint M13_SYSTSLCE `
  --output $Validation
if ($LASTEXITCODE -ne 0) {
  throw "FinnGen regional P0 failed with exit code $LASTEXITCODE"
}
Write-Output "PASS: $OutputFile"
Write-Output "P0: $Validation"
