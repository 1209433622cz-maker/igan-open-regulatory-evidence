$ErrorActionPreference = 'Stop'
$ProjectRoot = if($env:IGAN_PROJECT_ROOT){$env:IGAN_PROJECT_ROOT}else{(Get-Location).Path}
python (Join-Path $PSScriptRoot 'download_large_inputs.py') --root $ProjectRoot @args
if($LASTEXITCODE -ne 0){ throw 'Input download or checksum gate failed' }

