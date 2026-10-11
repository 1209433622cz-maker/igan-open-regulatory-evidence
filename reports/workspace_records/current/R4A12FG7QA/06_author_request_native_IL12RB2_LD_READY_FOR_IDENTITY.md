# TenK10K IL12RB2 source-LD 最小作者请求

> 状态：`READY_FOR_APPLICANT_IDENTITY / NOT SENT`。发送前补全申请人/PI、机构和机构邮箱。

## To

Dr Joseph E Powell / TenK10K DAC (`EGAC50000000931`)

## Subject

Request for native per-gene LD output for IL12RB2 (TenK10K Phase 1)

## Email body

Dear Dr Powell and the TenK10K team,

We are conducting a reproducible, non-commercial academic analysis of systemic sclerosis genetics using publicly released TenK10K Phase 1 single-cell eQTL summary statistics. Our bounded analysis focuses on **IL12RB2 (ENSG00000081985)** within the published ±100 kb cis window and uses aggregate GWAS/eQTL results.

We would like to apply the LD-aware multi-signal colocalisation framework implemented in the public TenK10K effector-gene workflow. The public v3 code indicates that the eQTL LD step generates a per-gene signed PLINK correlation matrix and BIM file, and that the multivariant colocalisation code reads the corresponding `{gene}.ld` and `{gene}.bim` files.

If permissible under the project’s data-governance policy, could you please provide the **native, untruncated derived LD outputs for IL12RB2**, ideally the objects generated as:

- `resources/ld/eqtl/tenk10k_phase1/chr1/ENSG00000081985.ld`
- `resources/ld/eqtl/tenk10k_phase1/chr1/ENSG00000081985.bim`

If the full per-gene derived files cannot be shared, a consistently ordered `.bim/.ld` subset covering the attached frozen list of 1,366 public IL12RB2 eQTL variants would still be useful. We can provide the list as `IL12RB2_TenK10K_100kb_native_variants_1366.tsv` (SHA-256 `b5195051ca88551d0ac1e6d7a31db5a2e2e83646c94d518c41814e07277a6fdc`).

We are not requesting individual-level genotypes if these derived files can be shared. We will preserve native variant order and allele coding, validate the matrix against the public IL12RB2 eQTL/SuSiE outputs, and use it only for the stated academic project. We will not attempt participant re-identification or individual-level linkage.

If these derived files cannot be shared directly, we would be grateful for guidance on whether access to `EGAS50000001654 / EGAD50000002377` is the preferred route for reconstructing the matrix in an approved institutional environment.

Thank you for your consideration.

Sincerely,

[Applicant / PI]  
[Institution]  
[Institutional email]

