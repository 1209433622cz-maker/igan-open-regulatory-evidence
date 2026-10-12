# R4A8B-H5: 2026 sex-specific SSc GWAS acquisition gate

Copy these files into:

`H:\SCI2\YR1\R4A8B_IGSR\`

Run in Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "H:\SCI2\YR1\R4A8B_IGSR\RUN_R4A8B_H5.ps1"
```

H5 performs read-only queries against the official NHGRI-EBI GWAS Catalog v2 API.

It uses GCST009131 as a positive control, then searches PMID 41999721 without
guessing a new GCST accession.

H5 does not modify H1-H4, does not download a large GWAS file, and does not run
fine-mapping.
