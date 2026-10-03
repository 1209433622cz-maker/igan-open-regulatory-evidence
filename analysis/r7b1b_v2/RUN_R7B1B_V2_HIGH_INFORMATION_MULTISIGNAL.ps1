[CmdletBinding()]
param(
    [int]$Workers = 2,
    [switch]$SkipGJOKAIntake,
    [switch]$SkipInputBuild
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = if ($env:R7_PROJECT_ROOT) { $env:R7_PROJECT_ROOT } else { 'H:\SCI2\YR1' }
$env:R7_PROJECT_ROOT = $ProjectRoot
Set-Location -LiteralPath $ProjectRoot

function Run-Step {
    param([string]$Name, [scriptblock]$Command)
    Write-Host "STEP_START $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "STEP_FAILED $Name exit=$LASTEXITCODE"
    }
    Write-Host "STEP_PASS $Name"
}

Run-Step 'freeze_exact_642_286_94' {
    python -u '.\2_code\06_intake\r7b1\08_freeze_r7b1b_v2_high_information_workload.py'
}

if (-not $SkipGJOKAIntake) {
    Run-Step 'fetch_validate_94_GJOKA_members' {
        python -u '.\2_code\06_intake\r7b1\09_fetch_r7b1b_v2_gjoka_members.py'
    }
}

if (-not $SkipInputBuild) {
    Run-Step 'build_642_dualmodel_QTL_and_286_sourceLD_blocks' {
        python -u '.\2_code\06_intake\r7b1\10_build_r7b1b_v2_dualmodel_qtl_ld.py'
    }
}

Run-Step 'run_642_source_matched_SuSiE_coloc' {
    python -u '.\2_code\06_intake\r7b1\12_orchestrate_r7b1b_v2_multisignal.py' --workers $Workers
}

Run-Step 'apply_preresult_frozen_bidirectional_adjudication' {
    python -u '.\2_code\06_intake\r7b1\13_adjudicate_r7b1b_v2.py'
}

Run-Step 'independent_QA' {
    python -u '.\2_code\06_intake\r7b1\14_independent_qa_r7b1b_v2.py'
}

Run-Step 'build_benchmark_figures' {
    python -u '.\2_code\06_intake\r7b1\15_build_r7b1b_v2_figures.py'
}

Run-Step 'build_reports_and_lightweight_release' {
    python -u '.\2_code\06_intake\r7b1\16_build_r7b1b_v2_reports_release.py'
}

Write-Host 'R7B1B_V2_PIPELINE_PASS'
