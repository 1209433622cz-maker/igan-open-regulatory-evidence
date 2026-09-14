# Large-input download

Set the repository or analysis project root, then run only the objects you need:

```powershell
$env:IGAN_PROJECT_ROOT = 'D:\igan-project'
pwsh -File .\data\RUN_DOWNLOAD_INPUTS.ps1 --ids igan_combined igan_european igan_asian
```

For the full R6A2B0 workflow, also request `onek_full_eqtl`, `onek_genotype` and `onek_covariates`. The downloader uses `.part` files, requests byte ranges when a partial file exists, validates the final byte count, and then checks MD5 or SHA-256 according to the manifest. Existing valid files are not downloaded again.

Some sources distribute archives that must be extracted to the directory names expected by the analysis scripts. Keep the original archives after extraction so their source hashes remain auditable.

