[CmdletBinding()]
param(
    [string]$ProjectRoot = 'H:\SCI2\YR1'
)
$ErrorActionPreference = 'Stop'
$Python = 'D:\bioinfor\python.exe'
$Code = Join-Path $ProjectRoot '2_code\06_intake\r7b1'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python missing: $Python" }
Set-Location -LiteralPath $ProjectRoot

$Steps = @(
    '01_build_r7b1_pbcwide_eligibility.py',
    '02_harmonize_pbc56_to_onek_bim.py',
    '03_run_r7b1_current_pf10_abf_screen.py',
    '04_independent_qa_and_freeze_r7b1a.py',
    '05_freeze_r7b1b_exact_workload.py'
)
foreach ($Step in $Steps) {
    Write-Host "RUN $Step"
    & $Python (Join-Path $Code $Step)
    if ($LASTEXITCODE -ne 0) { throw "R7B1A failed at $Step" }
}
Write-Host 'R7B1A full workflow PASS'
