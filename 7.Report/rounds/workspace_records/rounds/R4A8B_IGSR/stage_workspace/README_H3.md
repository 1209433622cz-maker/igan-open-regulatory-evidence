# R4A8B H3 diagnostic bundle

Copy these files into:

`H:\SCI2\YR1\R4A8B_IGSR\`

Do **not** overwrite or modify the frozen H2 outputs.

Run in Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "H:\SCI2\YR1\R4A8B_IGSR\RUN_R4A8B_H3.ps1"
```

H3 is diagnostic only. It does not run SuSiE-RSS and does not delete variants.

The purpose is to test whether the H2 RSS HOLD is driven by variant-dependent
study coverage/meta-analysis covariance rather than a broken allele or LD
pipeline.
