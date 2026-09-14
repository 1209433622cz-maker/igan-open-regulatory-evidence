# R6A3A v2 frozen protocol — IgAN completion-design gate

Date: 2026-09-14

## Frozen upstream evidence

```text
ZMIZ1_NK = VALIDATED_CROSS_RESOURCE_ANCHOR
REEP3_ONEK_ASIAN = DISCOVERY_PASS_ONLY
REEP3_TENK = INDEPENDENT_REPLICATION_FAIL
IMMUNE_CISEQTL_FULL24 = FROZEN_NO_GO
```

REEP3 cannot be counted as a replicated positive locus.

## Track A — public cis-pQTL

Primary public source: eQTL Catalogue `QTS000035 / QTD000584` (Sun 2018 INTERVAL plasma, 3,301 donors, aptamer assay).

Frozen genes only:

`TNFSF4, TNFRSF18, TNFSF8, TNFSF15, OVOL1, RELA, TNFSF12, TNFSF13, TNFRSF13B, LIF, OSM`.

Rules:

1. Direct public bytes only.
2. `GRCh38 ALT` is the molecular-QTL effect allele.
3. Small permutation + source SuSiE credible-set files are screened first; large nominal/LBF files are downloaded only after a frozen target is measured/source-supported.
4. All molecular probes for a frozen gene are retained; discordant probes are reported rather than selected away.
5. IgAN disease variants are lifted GRCh37→GRCh38 and harmonized by exact REF/ALT set; ambiguous palindromic variants are excluded without allele-frequency rescue.
6. Signal-level pQTL evidence uses source SuSiE log-BF components (`coloc.bf_bf`) rather than lead/proxy or MR alone.
7. A pQTL component PASS requires:
   - source credible set exists;
   - default PP.H4 >= 0.80;
   - default H4/(H3+H4) >= 0.80;
   - p12=1e-6 H4/(H3+H4) >= 0.50.
8. At least one independent frozen locus must PASS Track A.

## Track B — ZMIZ1 kidney evidence

Source: GSE127136 processed counts + SOFT, public GEO.

Primary inference:
- kidney only;
- donor is the biological replicate;
- 13 IgAN vs 6 kidney-cancer paracancer controls;
- aggregate-kidney ZMIZ1 pseudobulk with exact label permutation;
- paracancer controls are never called healthy kidney.

Secondary:
- deterministic canonical-marker localization is provisional only;
- it cannot replace full re-clustering if R6A3A restores manuscript-scale analysis.

Track-B status:
- `PASS_SUPPORTIVE_CASE_LOWER`: >=80% donor detection, case-lower direction and exact permutation P<0.05;
- `INTERPRETABLE_DONOR_LEVEL`: >=80% donor detection with valid effect/CI but no strict supportive shift;
- otherwise FAIL.

## Final gate

Manuscript-scale analysis resumes only when BOTH:

```text
AT_LEAST_ONE_ADDITIONAL_LOCUS_PQTL_SHARED_SIGNAL = PASS
ZMIZ1_KIDNEY_DONOR_LEVEL_LOCALIZATION = PASS_OR_INTERPRETABLE
CORE_CLAIM_REQUIRES_PERMISSION_DATA = FALSE
TARGET_SELECTION_WAS_PRE_FROZEN = TRUE
```

If either Track A or Track B fails:

```text
IGAN_REGULATORY_MAIN = FROZEN_ARCHIVE
NEXT = NEW_TOPIC_OPEN_DATA_BYTE_LEVEL_PREFLIGHT
```

No return to full-24 immune cis-eQTL expansion.
