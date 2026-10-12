param([ValidateSet('Main','Supplement')][string]$DocumentRole = 'Main')
$ErrorActionPreference = 'Stop'
$taskRoot = 'H:\SCI2\YR1\5_manuscript\R7C3H1B_ExactVersionHandoff_20261013'
$taskDocx = Join-Path $taskRoot '01_Manuscript\Manuscript_SubmissionCandidate.docx'
if ($DocumentRole -eq 'Supplement') { $taskDocx = Join-Path $taskRoot '03_Supplement\Supplementary_Information_ExpertRebuilt.docx' }
$taskPdf = [IO.Path]::ChangeExtension($taskDocx,'.pdf')
$taskWps = $null
$taskCount = $null
$taskDoc = $null
try {
    $taskWps = New-Object -ComObject kwps.Application
    $taskCount = $taskWps.Documents.Count
    $taskInitialVisible = $taskWps.Visible
    $taskInitialAlerts = $taskWps.DisplayAlerts
    if ($taskCount -ne 0) { throw 'Existing WPS documents are open; preserve the user session.' }
    $taskWps.Visible = $false
    $taskWps.DisplayAlerts = 0
    $taskHash = (Get-FileHash -LiteralPath $taskDocx -Algorithm SHA256).Hash.ToLower()
    $taskDoc = $taskWps.Documents.Open($taskDocx,$false,$true)
    $taskDoc.ExportAsFixedFormat($taskPdf,17)
    if ((Get-FileHash -LiteralPath $taskDocx -Algorithm SHA256).Hash.ToLower() -ne $taskHash) { throw 'Read-only WPS export altered DOCX.' }
    $taskReceipt = [PSCustomObject]@{
        docx=$taskDocx; docx_sha256=$taskHash; pdf=$taskPdf
        pdf_sha256=(Get-FileHash -LiteralPath $taskPdf -Algorithm SHA256).Hash.ToLower()
        renderer='WPS kwps.Application ExportAsFixedFormat 17'
        read_only=$true; background=$true; exported_at=(Get-Date -Format o)
    }
    $taskReceiptFile = '06_QA\WPS_EXPORT_RECEIPT.json'
    if ($DocumentRole -eq 'Supplement') { $taskReceiptFile = '06_QA\WPS_SUPPLEMENT_EXPORT_RECEIPT.json' }
    $taskReceipt | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $taskRoot $taskReceiptFile) -Encoding utf8
    Write-Output 'WPS_EXPORT_PASS'
} finally {
    if ($null -ne $taskDoc) { $taskDoc.Close($false);[void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDoc) }
    if ($null -ne $taskWps) {
        if ($taskCount -eq 0 -and $taskWps.Documents.Count -eq 0) { $taskWps.Quit() }
        elseif ($null -ne $taskCount) { $taskWps.Visible=$taskInitialVisible;$taskWps.DisplayAlerts=$taskInitialAlerts }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWps)
    }
    [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
