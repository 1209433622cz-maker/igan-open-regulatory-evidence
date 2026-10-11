# R6A2B0 execution package

Copy all files under `code/` to:

`H:\SCI2\YR1\2_code\06_intake\igan_r6a2b0\`

Then run:

```powershell
Set-Location 'H:\SCI2\YR1'
pwsh -File '.\2_code\06_intake\igan_r6a2b0\RUN_R6A2B0_8LOCUS_BOUNDED_EXPANSION.ps1'
```

Do not run `07_build_targeted_source_ld.py` manually unless the machine adjudication creates a source-LD trigger.

Primary return files:
- `3_results/04_integration/R6A2B0/R6A2B0_coloc_smoke_summary.json`
- `3_results/04_integration/R6A2B0/R6A2B0_locus_adjudication.tsv`
- `3_results/04_integration/R6A2B0/R6A2B0_sourceLD_triggers.tsv`
- `3_results/04_integration/R6A2B0/R6A2B0_official_R_coloc_validation.tsv`
- `3_results/04_integration/R6A2B0/R6A2B0_final_machine_adjudication.json`
