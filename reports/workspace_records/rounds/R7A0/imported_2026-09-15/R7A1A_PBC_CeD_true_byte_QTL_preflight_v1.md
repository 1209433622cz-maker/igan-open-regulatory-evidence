# R7A1A frozen protocol — PBC vs CeD true-byte and QTL-positive-control intake

Date: 2026-09-15

## Portfolio transition

```text
SSc_MAIN = FROZEN_ARCHIVE
MG_REGULATORY_MAIN = FROZEN_ARCHIVE
IgAN_REGULATORY_MAIN = FROZEN_ARCHIVE

R7A0:
PBC = RANK_1_ADVANCE
CeD = RANK_2_ADVANCE
AA = FAIL_GATE0_UNDER_CURRENT_OPEN_GWAS_RULE
```

No new main project is approved yet.

## Why PBC is ranked above CeD

The user prioritizes completion probability and real positive-evidence density over maximum novelty. PBC has:
- 56 analysed non-HLA genome-wide-significant loci;
- European reanalysis N=24,510 (8,021 cases / 16,489 controls);
- public study-derived summary statistics and study LD matrices;
- published multi-omic colocalization positives at many loci;
- open 5 PBC + 5 control liver scRNA.

Its 2026 novelty overlap is a major penalty, but not a hard exclusion for a Q2/Q3-completion-first paper.

CeD has better novelty headroom but:
- no similarly verified in-sample disease-LD package in this audit;
- the freshest lesion scRNA has only 4 active CeD + 2 normal donors;
- exact public dense-GWAS byte/schema qualification remains necessary.

## Pre-registered controls

### PBC
1. IL12RB2 (1p31.3)
2. FCRL3 (1q23.1)
3. INAVA (1q32.1)

These are frozen because the 2021 PBC GWMA/moloc paper explicitly implicated them at GWS loci.

### CeD
1. CSK (15q24)
2. TRAFD1 (12q24)
3. UBASH3A (21q22)

These are frozen from the 2020 CeD integrative prioritization before OneK1K/TenK10K results are inspected.

## R7A1A duties

1. Download actual public GWAS bytes for PBC and CeD.
2. Generate MD5/SHA-256 receipts.
3. Validate allele/beta-or-OR/SE/P schema and numerical ranges.
4. Count non-MHC GWS rows and provisional 1-Mb distance-pruned regions; do NOT call them LD-independent without study/public LD.
5. Inventory PBC study-specific reanalysis ZIP and explicitly verify whether LD matrices are present.
6. Screen exactly the 3+3 frozen genes in OneK1K top-eQTL, TenK10K gene-level and TenK10K source-SuSiE indexes.
7. STOP before disease–QTL colocalization.

## Advance to R7A1B signal-level gate

A candidate advances only if:

```text
FULL_GWAS_BYTES_AND_SCHEMA = PASS
NON_MHC_GWS_REGIONS_PROVISIONAL >= 5
FROZEN_CONTROLS = 3
CROSS_RESOURCE_QTL_TESTABLE_CONTROLS >= 3
CORE_DATA_PERMISSION_REQUIRED = FALSE
```

R7A1B then runs the same source-aware disease↔OneK QTL framework used in MG/IgAN and requires:
- robust shared signal loci >=2/3 controls;
- at least one same-gene compatible-cell TenK independent replication;
- disease-tissue target detectability.

Only then can `NEW_PRIMARY_PROJECT = GO`.
