# Canonical eight-directory GitHub layout

| Directory | Role | Former repository roots |
|---|---|---|
| `0_admin` | Protocols, decisions, environments, provenance, docs | `audit`, `docs`, `environment`, `protocols`, `workspace_support` |
| `1_data` | Source metadata and large-input recovery pointers | `data` |
| `2_code` | Scientific workflow, figure/document and verification code | `analysis` |
| `3_results` | Compact reviewed scientific and QA outputs | `results` |
| `4_figures` | Current Fig1–6/S1–S3 masters and historical figures | `figures` becomes `history/` |
| `5_manuscript` | Current exact-byte candidate and immutable earlier versions | `manuscript` becomes `history/` |
| `6_release` | Delivery receipts, versions and Release asset navigation | New canonical release index |
| `7.Report` | Stage action reports, value/reuse and next-stage records | `reports` becomes `rounds/` |

Full local raw data, installed runtimes, Git object backups, copyrighted papers and private full-workspace inventories remain local. Local `5_analysis`, `8.Reference`, `9.Version`, `9_Vote` are represented by selected audits, source citations, protocol/state records and historical refs within these eight public roles.

All historical file bytes are preserved. `../audit/r7c3g1/PATH_MIGRATION_AND_PRESERVATION.tsv` maps every old tracked path to its exact new identity. Historical local paths in frozen documents are not rewritten; historical Git tags still expose the original tree. Use current root README links for the active paper.
