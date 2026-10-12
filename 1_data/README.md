# Input sources and identities

This directory contains public source metadata, download identities and access receipts. It does not mirror individual-level or large third-party inputs. `LARGE_DATA_MANIFEST.tsv` retains its original rows, including archived IgAN sources; an archived row is not the current primary endpoint.

| Current PBC role | Source | Exact identity routes |
|---|---|---|
| Disease screening | GWAS Catalog GCST90061440 | Stage protocols and input-freeze tables in `../3_results/r7b1a/` and `../3_results/r7b2a/` |
| Study-matched disease statistics/LD | GJOKA | `../0_admin/protocols/`, `../3_results/r7b1b_v2/` and their original manifests |
| Molecular discovery and cell-specific model-matched LD | OneK1K | `LARGE_DATA_MANIFEST.tsv`; source identity recovery and donor/covariate receipts in `../3_results/` |
| Molecular resource replication | TenK10K | Stage source ledgers in `../3_results/r7a1c/` and `../3_results/r7c1/` |
| Bounded external disease/chromatin evidence | FinnGen | `../3_results/r7c1/external_evidence/` |
| Target-panel liver tissue | HRA008003 | Tissue source and byte receipts in `../3_results/`; this is 5 PBC versus 5 controls, not a new full atlas |
| Limited processed spatial resource | OMIX001122 | External source audit; missing coordinates/independent donors limit its role |

`LOCAL_LARGE_INPUT_POINTERS.tsv` records local input files exceeding 10 MiB, with fresh size/mtime identity checks against the latest audit and the hash basis explicitly stated. It contains workspace-relative paths, never donor content. Provider URLs and provider checksums remain in the original source manifests; do not infer a redistribution licence from public access. See [data availability](../DATA_AVAILABILITY.md).
