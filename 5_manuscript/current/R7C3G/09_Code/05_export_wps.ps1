$ErrorActionPreference = 'Stop'
$taskRoot = 'H:\SCI2\YR1\5_manuscript\R7C3G_ExpertNarrative_20261012'
$taskFiles = @('01_Manuscript\Manuscript_ExpertRebuilt.docx','01_Manuscript\Manuscript_AuthorReview_InlineFigures.docx','03_Supplement\Supplementary_Information_ExpertRebuilt.docx','04_Cover\Cover_Letter_ExpertRebuilt_DRAFT.docx')
$taskWps = $null
$taskCount = $null
$taskReceipts = @()
try {
 $taskWps = New-Object -ComObject kwps.Application
 $taskCount = $taskWps.Documents.Count
 $taskInitialVisible = $taskWps.Visible
 $taskInitialAlerts = $taskWps.DisplayAlerts
 if ($taskCount -ne 0) { throw 'Existing WPS documents are open; do not alter the user session.' }
 $taskWps.Visible = $false
 $taskWps.DisplayAlerts = 0
 foreach ($taskRel in $taskFiles) {
  $taskDocx = Join-Path $taskRoot $taskRel
  $taskPdf = [IO.Path]::ChangeExtension($taskDocx,'.pdf')
  $taskHash = (Get-FileHash -LiteralPath $taskDocx -Algorithm SHA256).Hash.ToLower()
  $taskDoc = $null
  try {
   $taskDoc = $taskWps.Documents.Open($taskDocx,$false,$true)
   $taskDoc.ExportAsFixedFormat($taskPdf,17)
   if (-not (Test-Path -LiteralPath $taskPdf)) { throw "Missing PDF $taskPdf" }
   if ((Get-FileHash -LiteralPath $taskDocx -Algorithm SHA256).Hash.ToLower() -ne $taskHash) { throw 'WPS export changed read-only source' }
   $taskReceipts += [PSCustomObject]@{docx=$taskRel;docx_sha256=$taskHash;pdf=$taskPdf;pdf_sha256=(Get-FileHash -LiteralPath $taskPdf -Algorithm SHA256).Hash.ToLower();renderer='WPS kwps.Application ExportAsFixedFormat 17';background=$true;exported_at=(Get-Date -Format o)}
   Write-Output "WPS_EXPORT_PASS $taskRel"
  } finally { if ($null -ne $taskDoc) { $taskDoc.Close($false);[void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDoc) } }
 }
 $taskReceipts | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskRoot '06_QA\WPS_Export_Receipt.json') -Encoding utf8
} finally {
 if ($null -ne $taskWps) {
  if ($taskCount -eq 0 -and $taskWps.Documents.Count -eq 0) { $taskWps.Quit() }
  elseif ($null -ne $taskCount) { $taskWps.Visible=$taskInitialVisible;$taskWps.DisplayAlerts=$taskInitialAlerts }
  [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWps)
 }
 [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
