$ErrorActionPreference = 'Stop'
$taskRoot = 'H:\SCI2\YR1\5_manuscript\R7C3B_QiTeng_WPS_SubmissionRefinement_20261011'
$taskDocuments = @(
    '01_Manuscript\R7C3B_npj_Manuscript.docx',
    '01_Manuscript\R7C3B_AuthorReview_InlineFigures.docx',
    '03_Supplement\R7C3B_Supplementary_Information.docx',
    '04_Cover\R7C3B_Cover_Letter_Candidate.docx'
)
$taskWps = $null
$taskInitialCount = $null
$taskReceipts = @()
try {
    $taskWps = New-Object -ComObject kwps.Application
    $taskInitialCount = $taskWps.Documents.Count
    $taskInitialVisible = $taskWps.Visible
    $taskInitialAlerts = $taskWps.DisplayAlerts
    if ($taskInitialCount -ne 0) {
        throw 'Existing WPS documents are open; background batch must not alter or close them.'
    }
    $taskWps.Visible = $false
    $taskWps.DisplayAlerts = 0
    foreach ($taskRel in $taskDocuments) {
        $taskDocx = Join-Path $taskRoot $taskRel
        $taskPdf = [IO.Path]::ChangeExtension($taskDocx, '.pdf')
        $taskDoc = $null
        try {
            if (-not (Test-Path -LiteralPath $taskDocx)) { throw "Missing DOCX $taskRel" }
            $taskBeforeHash = (Get-FileHash -LiteralPath $taskDocx -Algorithm SHA256).Hash
            $taskDoc = $taskWps.Documents.Open($taskDocx, $false, $true)
            $taskDoc.ExportAsFixedFormat($taskPdf, 17)
            if (-not (Test-Path -LiteralPath $taskPdf)) { throw "WPS PDF absent: $taskRel" }
            if ((Get-FileHash -LiteralPath $taskDocx -Algorithm SHA256).Hash -ne $taskBeforeHash) { throw 'Read-only WPS export changed DOCX bytes' }
            $taskReceipts += [PSCustomObject]@{
                docx = $taskRel; pdf = $taskPdf; renderer = 'WPS kwps.Application ExportAsFixedFormat 17';
                read_only = $true; docx_sha256 = $taskBeforeHash.ToLower();
                pdf_sha256 = (Get-FileHash -LiteralPath $taskPdf -Algorithm SHA256).Hash.ToLower();
                pdf_bytes = (Get-Item -LiteralPath $taskPdf).Length; exported_at = (Get-Date -Format o)
            }
            Write-Output "WPS_EXPORT_PASS $taskRel"
        }
        finally {
            if ($null -ne $taskDoc) {
                $taskDoc.Close($false)
                [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDoc)
            }
        }
    }
    $taskReceipts | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskRoot '06_QA\WPS_Export_Receipt.json') -Encoding utf8
}
finally {
    if ($null -ne $taskWps) {
        if ($taskInitialCount -eq 0 -and $taskWps.Documents.Count -eq 0) { $taskWps.Quit() }
        elseif ($null -ne $taskInitialCount) {
            $taskWps.Visible = $taskInitialVisible
            $taskWps.DisplayAlerts = $taskInitialAlerts
        }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWps)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
