# R4A9 independent reference and signed-LD audit

## Final status

**PASS — source provenance and the 1,555 retained-variant regional-VCF→BED→A1-dosage→signed-LD path were independently reproduced.**

This audit used PLINK2 to export dosage and did not reuse the R4A8B custom BED decoder.

## Exact source provenance

- Source: 1000 Genomes Phase 3 integrated v5a, GRCh37
- Zenodo record: https://zenodo.org/records/3359882
- Full chr1 VCF: 1,216,886,729 bytes
- VCF MD5: `609b38c12de89175b3d85c1588e4905c`; expected `609b38c12de89175b3d85c1588e4905c`; **PASS**
- Original TBI MD5: `5fa609a13f662d7abacfb6f2dc208410`; expected `5fa609a13f662d7abacfb6f2dc208410`; **PASS**
- Full VCF SHA256: `ae0eb80ea07c19033332d17de28fb05128a3f5778d9e16dc8eadcab7e3c21987`
- Original TBI SHA256: `08f3d07bcbb0df60ed8054e077d293bae9b21af5a39881e97bf09433cc41dc54`

## Population and regional reference

- Panel EUR samples: 503
- Panel, `EUR.samples`, FAM, and regional VCF sample order: **exact match**
- Regional biallelic SNPs: 27,067
- Regional VCF versus five-column manifest: **exact match**
- Missing rsID: 0; duplicate rsID: 0

## Independent dosage and LD reproduction

- PLINK2: `PLINK v2.00a3 SSE4.2 (18 Feb 2022)`
- Exported matrix: 503 samples × 1555 variants
- Regional VCF GT versus PLINK2 BED A1 dosage: 503 × 1555; maximum absolute difference `0.0`; mismatch cells `0`
- PLINK counted allele equals frozen GWAS A1 for every variant: **PASS**
- PLINK2 dosage versus frozen custom-decoder dosage maximum absolute difference: `0.0`
- Cells differing above `1e-12`: `0`
- Independent `numpy.corrcoef` versus frozen signed-LD maximum absolute difference: `6.99441e-15`
- rs3790566/rs3790567 signed r: `0.994613984367`; r²: `0.989256977898`

## Boundary

This PASS closes source provenance, regional manifest, retained-variant genotype conversion, allele orientation, and signed-LD implementation. It does not independently re-derive every regional genotype from the full chr1 VCF, does not override the failed full-summary RSS diagnostic, and does not authorize paper-grade credible sets from GCST009131.
