# R7B0A PF10 source-identity recovery scanner
# Read-only: searches likely local locations and ZIP contents; does not modify scientific inputs.

param(
  [string[]]$Roots = @(
    'H:\SCI2\YR1',
    'C:\Users\Administrator\Downloads'
  ),
  [string]$OutDir = 'H:\SCI2\YR1\3_results\00_audit\R7B0A_PF10_SOURCE_RECOVERY'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$patterns = @(
  '*_covar_peer_factors_PF10.txt',
  '*_mx_pf50.txt',
  '*PEER*factors*.zip',
  '*updated_covariates*.zip'
)

$hits = New-Object System.Collections.Generic.List[object]

function Add-Hit {
  param([string]$Kind,[string]$Path,[string]$Container='',[string]$Member='')
  $sha = $null; $bytes = $null
  if ($Kind -eq 'FILE' -and (Test-Path -LiteralPath $Path -PathType Leaf)) {
    $fi = Get-Item -LiteralPath $Path
    $bytes = $fi.Length
    $sha = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLower()
  }
  $hits.Add([pscustomobject]@{
    kind=$Kind; path=$Path; container=$Container; member=$Member;
    bytes=$bytes; sha256=$sha
  }) | Out-Null
}

foreach ($root in $Roots) {
  if (-not (Test-Path -LiteralPath $root)) { continue }
  foreach ($pat in $patterns) {
    Get-ChildItem -LiteralPath $root -Recurse -File -Filter $pat -ErrorAction SilentlyContinue |
      ForEach-Object { Add-Hit -Kind 'FILE' -Path $_.FullName }
  }

  # Scan only likely ZIPs to avoid opening every archive on disk.
  Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.zip' -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match 'OneK|PEER|covar|R7|YR1' } |
    ForEach-Object {
      $zipPath = $_.FullName
      try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $za = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
        try {
          foreach ($e in $za.Entries) {
            if ($e.FullName -match 'covar_peer_factors_PF10\.txt$' -or
                $e.FullName -match '_mx_pf50\.txt$') {
              $hits.Add([pscustomobject]@{
                kind='ZIP_MEMBER'; path=''; container=$zipPath; member=$e.FullName;
                bytes=$e.Length; sha256=$null
              }) | Out-Null
            }
          }
        } finally { $za.Dispose() }
      } catch {
        Write-Warning "ZIP scan failed: $zipPath :: $($_.Exception.Message)"
      }
    }
}

$hits | Sort-Object kind,path,container,member |
  Export-Csv -LiteralPath (Join-Path $OutDir 'PF10_source_recovery_hits.tsv') -Delimiter "`t" -NoTypeInformation

# Search project text/code for the historical source path and generation rules.
$textHits = New-Object System.Collections.Generic.List[object]
foreach ($root in $Roots) {
  if (-not (Test-Path -LiteralPath $root)) { continue }
  Get-ChildItem -LiteralPath $root -Recurse -File -Include *.py,*.R,*.md,*.txt,*.json,*.ps1 -ErrorAction SilentlyContinue |
    ForEach-Object {
      try {
        $m = Select-String -LiteralPath $_.FullName -Pattern 'covar_peer_factors_PF10|round2_more_covar|make_new_PF_covar_option11|mx_pf50' -SimpleMatch:$false
        foreach ($x in $m) {
          $textHits.Add([pscustomobject]@{
            path=$_.FullName; line=$x.LineNumber; text=$x.Line.Trim()
          }) | Out-Null
        }
      } catch {}
    }
}
$textHits | Export-Csv -LiteralPath (Join-Path $OutDir 'PF10_source_code_references.tsv') -Delimiter "`t" -NoTypeInformation

Write-Host "PF10 recovery scan complete."
Write-Host "Hits: $($hits.Count)"
Write-Host "Output: $OutDir"
