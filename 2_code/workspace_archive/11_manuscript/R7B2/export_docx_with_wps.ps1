param(
    [Parameter(Mandatory=$true)][string]$InputDocx,
    [Parameter(Mandatory=$true)][string]$OutputPdf
)

$ErrorActionPreference = 'Stop'
$docx = [System.IO.Path]::GetFullPath($InputDocx)
$pdf = [System.IO.Path]::GetFullPath($OutputPdf)
if (-not (Test-Path -LiteralPath $docx)) { throw "DOCX not found: $docx" }
$outDir = Split-Path -Parent $pdf
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
if (Test-Path -LiteralPath $pdf) { Remove-Item -LiteralPath $pdf -Force }

$wps = $null
$doc = $null
try {
    $wps = New-Object -ComObject 'KWPS.Application'
    $wps.Visible = $false
    $wps.DisplayAlerts = 0
    $doc = $wps.Documents.Open($docx, $false, $true)
    if ($null -eq $doc) { throw 'WPS failed to open the document.' }
    try {
        # 17 is the Word-compatible PDF export format.
        $doc.ExportAsFixedFormat($pdf, 17)
    } catch {
        # WPS builds that do not expose ExportAsFixedFormat accept SaveAs2 with format 17.
        $doc.SaveAs2($pdf, 17)
    }
    $doc.Close($false)
    $doc = $null
    $wps.Quit()
    $wps = $null
} finally {
    if ($null -ne $doc) { try { $doc.Close($false) } catch {} }
    if ($null -ne $wps) { try { $wps.Quit() } catch {} }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}

if (-not (Test-Path -LiteralPath $pdf)) { throw "WPS did not create PDF: $pdf" }
$item = Get-Item -LiteralPath $pdf
if ($item.Length -lt 10000) { throw "WPS PDF is unexpectedly small: $($item.Length) bytes" }
Write-Output "WPS_PDF_OK`t$($item.FullName)`t$($item.Length)"
