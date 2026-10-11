$ErrorActionPreference = "Stop"
$CurrentTests = Join-Path $PSScriptRoot "h6_v2_1\RUN_TESTS.ps1"
if (-not (Test-Path -LiteralPath $CurrentTests -PathType Leaf)) {
    throw "Current H6 v2.1 test runner is missing: $CurrentTests"
}

& $CurrentTests
exit $LASTEXITCODE
