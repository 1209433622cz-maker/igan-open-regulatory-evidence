[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][string]$Release,
    [Parameter(Mandatory = $true)][string]$Phenocode,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$Output,
    [Parameter(Mandatory = $true)][string]$Receipt
)

$ErrorActionPreference = "Stop"
$Node = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$Script = Join-Path $PSScriptRoot "query_finngen_region.mjs"
if (-not (Test-Path -LiteralPath $Node -PathType Leaf)) {
    throw "Pinned Node.js runtime not found: $Node"
}
& $Node $Script --url $Url --release $Release --phenocode $Phenocode --region $Region --output $Output --receipt $Receipt
if ($LASTEXITCODE -ne 0) {
    throw "Remote Tabix query failed with exit code $LASTEXITCODE"
}
