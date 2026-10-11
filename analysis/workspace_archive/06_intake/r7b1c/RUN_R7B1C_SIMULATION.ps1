param(
  [int]$Workers = 12,
  [switch]$SkipTemplateBuild,
  [switch]$SkipPilotValidation
)
$ErrorActionPreference = 'Stop'
$Root = 'H:\SCI2\YR1'
$Code = Join-Path $Root '2_code\06_intake\r7b1c'
Set-Location $Root
if (-not $SkipTemplateBuild) {
  python (Join-Path $Code '01_build_r7b1c_empirical_ld_templates.py')
}
if (-not $SkipPilotValidation) {
  python (Join-Path $Code '03_validate_r7b1c_pilot.py')
}
python (Join-Path $Code '04_orchestrate_r7b1c_full_grid.py') --workers $Workers
python (Join-Path $Code '05_aggregate_r7b1c_simulation.py')
python (Join-Path $Code '06_independent_qa_r7b1c.py')
python (Join-Path $Code '07_build_r7b1c_figures.py')
python (Join-Path $Code '08_build_r7b1c_reports_release.py')
