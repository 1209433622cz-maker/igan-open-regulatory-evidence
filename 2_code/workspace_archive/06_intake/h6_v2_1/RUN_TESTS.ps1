$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path -LiteralPath "D:\bioinfor\python.exe" -PathType Leaf) {
    $PythonExe = "D:\bioinfor\python.exe"
} else {
    $PythonExe = (Get-Command python -ErrorAction Stop).Source
}

& $PythonExe -m py_compile `
    (Join-Path $Here "intake_core.py") `
    (Join-Path $Here "inspect_sex_specific_sumstats_v2_1.py") `
    (Join-Path $Here "test_h6_v2_1.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonExe (Join-Path $Here "test_h6_v2_1.py")
$RegressionExit = $LASTEXITCODE
if ($RegressionExit -ne 0) { exit $RegressionExit }

$HostileSuite = Join-Path (Split-Path -Parent $Here) "audit\H6_v2_1_hostile_test.py"
& $PythonExe -m py_compile $HostileSuite
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonExe $HostileSuite
exit $LASTEXITCODE
