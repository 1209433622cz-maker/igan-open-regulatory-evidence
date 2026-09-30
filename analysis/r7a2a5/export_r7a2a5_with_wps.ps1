$ErrorActionPreference = 'Stop'

$items = @(
    @{
        Docx = 'H:\SCI2\YR1\5_manuscript\R7A2A5_HumanGenomics\manuscript\R7A2A5_HumanGenomics_manuscript_v3.docx'
        Pdf  = 'H:\SCI2\YR1\5_manuscript\R7A2A5_HumanGenomics\manuscript\R7A2A5_HumanGenomics_manuscript_v3_WPS.pdf'
    },
    @{
        Docx = 'H:\SCI2\YR1\5_manuscript\R7A2A5_HumanGenomics\cover_letter\R7A2A5_HumanGenomics_cover_letter_DRAFT.docx'
        Pdf  = 'H:\SCI2\YR1\5_manuscript\R7A2A5_HumanGenomics\cover_letter\R7A2A5_HumanGenomics_cover_letter_DRAFT_WPS.pdf'
    }
)

$wps = $null
try {
    $wps = New-Object -ComObject kwps.Application
    $wps.Visible = $false
    foreach ($item in $items) {
        $doc = $null
        try {
            if (Test-Path -LiteralPath $item.Pdf) {
                Remove-Item -LiteralPath $item.Pdf -Force
            }
            $doc = $wps.Documents.Open($item.Docx, $false, $true)
            $doc.ExportAsFixedFormat($item.Pdf, 17)
        }
        finally {
            if ($null -ne $doc) {
                $doc.Close($false)
                [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
            }
        }
    }
}
finally {
    if ($null -ne $wps) {
        $wps.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wps)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Get-Item -LiteralPath ($items | ForEach-Object { $_.Pdf }) |
    Select-Object FullName, Length, LastWriteTime
