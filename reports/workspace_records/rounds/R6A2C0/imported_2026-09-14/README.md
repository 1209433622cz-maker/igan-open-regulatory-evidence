# R6A2C REEP3 Asian-specific falsification execution pack

Copy `code/` to:

`H:\SCI2\YR1\2_code\06_intake\igan_r6a2c\`

Run:

```powershell
Set-Location 'H:\SCI2\YR1'
pwsh -File '.\2_code\06_intake\igan_r6a2c\RUN_R6A2C_REEP3_FALSIFICATION.ps1'
```

Return these outputs:
- `3_results/04_integration/R6A2C/R6A2C_final_adjudication.json`
- `3_results/04_integration/R6A2C/R6A2C_asian_signal_gate.tsv`
- `3_results/04_integration/R6A2C/multisignal/R6A2C_susie_summary.tsv`
- `3_results/04_integration/R6A2C/multisignal/R6A2C_susie_credible_sets.tsv`
- `3_results/04_integration/R6A2C/multisignal/R6A2C_signal_coloc.tsv`
- `3_results/04_integration/R6A2C/sourceLD/REEP3_REEP3_CD4_NC/covariate_residual_LD_QC.json`

The runner intentionally stops before TenK10K. TenK is triggered only by a signal-specific PASS.
