[CmdletBinding()]
param(
    [string]$ProjectRoot = 'H:\SCI2\YR1'
)
$ErrorActionPreference = 'Stop'
$Python = 'D:\bioinfor\python.exe'
$Code = Join-Path $ProjectRoot '2_code\06_intake\r7b1'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python missing: $Python" }
Set-Location -LiteralPath $ProjectRoot

& $Python (Join-Path $Code '08_freeze_r7b1b_v2_high_information_workload.py')
if ($LASTEXITCODE -ne 0) { throw 'R7B1B v2 freeze failed' }

& $Python -c 'import remotezip'
if ($LASTEXITCODE -ne 0) {
    & $Python -m pip install remotezip
    if ($LASTEXITCODE -ne 0) { throw 'remotezip installation failed' }
}

& $Python (Join-Path $Code '09_fetch_r7b1b_v2_gjoka_members.py')
if ($LASTEXITCODE -ne 0) { throw 'R7B1B v2 GJOKA intake failed' }

Write-Host 'R7B1B v2 GJOKA intake PASS'
