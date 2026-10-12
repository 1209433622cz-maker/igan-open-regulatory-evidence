[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $CodeRoot
try {
  python -m unittest -v test_finngen_r12_r13_intake.py
  if ($LASTEXITCODE -ne 0) {
    throw "FinnGen intake tests failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
