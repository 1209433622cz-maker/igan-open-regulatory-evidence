# R7A1B0 PBC three-control signal gate

This is an execution/hardening package. It does not contain third-party PBC GWAS, GJOKA LD, OneK genotypes or raw OneK cis-eQTL bytes.

Deploy `code/*` to:

`H:\SCI2\YR1\2_code\06_intake\r7a1b\`

Run:

```powershell
Set-Location 'H:\SCI2\YR1'
$env:R7_PROJECT_ROOT='H:\SCI2\YR1'
pwsh -File '.\2_code\06_intake\r7a1b\RUN_R7A1B_PBC_3CONTROL_SIGNAL_GATE.ps1'
```

Do not open TenK PBC disease colocalization or liver tissue analysis until `R7A1B_final_adjudication.json` reports at least two signal-specific PASS genes.
