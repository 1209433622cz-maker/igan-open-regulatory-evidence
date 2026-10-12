# PBC regulatory attribution reliability

Input-matched multi-signal colocalization, cell context, covariate sensitivity and bounded external evidence in primary biliary cholangitis.

**Current project: PBC, RP v4.** The latest scientific/editorial candidate is R7C3B (QiTeng v0.3.24.2; original WPS exports), packaged without scientific edits as **R7C3F, 12 October 2026**. This is open research and a submission candidate, **not a submitted/accepted paper or a generated Zenodo DOI**. The historical `igan-open-regulatory-evidence` URL is retained so manuscript code links and scientific tags remain stable; IgAN is archived.

## Start here

| Need | Authoritative entry |
|---|---|
| Current main manuscript | [DOCX](manuscript/r7c3f/01_Main/Manuscript.docx), [original WPS review PDF](manuscript/r7c3f/01_Main/Manuscript_WPS_Review.pdf) |
| Submission roles and remaining gates | [Start here](manuscript/r7c3f/00_START_HERE.md), [upload identity map](manuscript/r7c3f/UPLOAD_ROLES_AND_IDENTITIES.tsv) |
| Six separate vector figures | [Figure 1–6](manuscript/r7c3f/02_Figures/) |
| Supplement and machine-readable results | [S1–S10 workbook / SI](manuscript/r7c3f/03_Supplement/), [Source Data 1 and 2](manuscript/r7c3f/05_Source_Data/) |
| Scientific results and interpretation limits | [Evidence and reusable assets](docs/EVIDENCE_AND_REUSE.md) |
| Same-input comparison | [642 four-arm trajectories](results/r7b2a/adjudication/R7B2A_642_four_arm_trajectories.tsv), [attribution state](results/r7b2a/adjudication/R7B2A_attribution_state.json) |
| Simulation discovery/inference channels | [Channel table](results/r7b2a/simulation_audit/R7B2A_R7B1C_channel_summary.tsv) |
| External evidence | [Source ledger and adjudications](results/r7c1/external_evidence/) |
| Local workspace, source-only files and history | [Folder map](docs/WORKSPACE_STRUCTURE.md), [data availability](DATA_AVAILABILITY.md), [work-record guide](docs/WORK_RECORD_GUIDE.md) |

## Research question and main findings

The study asks why regulatory assignments change when single-causal screening is followed by source-matched multi-signal analysis. It separates variant support, disease statistics, causal assumptions, covariate models, credible-set discovery and external-evidence roles. The contribution is an auditable reliability analysis; known PBC genes are examples, not claims of first discovery or proven treatment mechanisms.

| Analysis | Frozen result | Interpretation |
|---|---|---|
| PBC-wide screen | 6,923 registered; 5,460 eligible; 1,463 coverage-insufficient | Insufficient coverage is not a negative biological result |
| High-information multi-signal follow-up | 642 comparisons, 47 loci, 200 genes, 14 cells, 286 blocks | Prespecified subset, not all screened comparisons |
| PF10 outcome | 92 H4, 428 H3, 59 model-sensitive, 63 uninformative | Comparison counts are not independent discoveries |
| Matched-input A2→M | 8 H4→H3; 10 H3→H4 | Bidirectional reclassification, not real-data truth/error rates |
| Covariate sensitivity | 491/520 agree; 4 differ; 25 PF50-uninformative | Model choice can change regulatory assignment |
| Known-truth simulation | 486,000 iterations; 160,782 pair-evaluable (33.08%) | Discovery adequacy is separate from conditional inference |
| Simulation trade-off | False sharing 12.41%→8.56%; shared recovery 32.99%→26.66% | No universal method superiority claim |
| Liver context | 5 PBC and 5 controls; both axes detected in every group donor | No corrected disease-specific enrichment |

All counts and estimates are tied to the frozen tables, Source Data and manuscript, not newly recalculated biological models in the workspace audit. IL12RB2–NK has additional external disease-study and linked-chromatin support, but participant non-overlap and causal mediation remain unestablished. OneK1K/TenK10K sharing reuses the discovery GWAS. Thirty-two H4-supported comparisons also contain distinct pairs; a shared pair does not make every regional signal shared.

## Reproduction and environments

1. Read the relevant frozen protocol and source manifest before downloading inputs. Download from providers; do not treat this repository as a donor-level raw-data mirror.
2. Recreate the stage-specific environments in [environment/](environment/) and recorded package/version receipts. Scientific runs used `coloc` 5.2.3 and `susieR` 0.14.2; local audit uses the recorded Python runtime. Some earlier historical stages have their own version receipts.
3. Restore the canonical local workspace roles using [the folder map](docs/WORKSPACE_STRUCTURE.md). Scripts retain stage-specific local input paths and are not advertised as a one-command portable end-to-end workflow. Edit explicit ROOT/input settings for another machine, preserving hashes, donor sets and model definitions.
4. Run the relevant frozen stages in order: [screen](analysis/r7b1/) → [source-matched follow-up](analysis/r7b1b_v2/) → [simulation](analysis/r7b1c/) → [matched-input audit](analysis/r7b2a/) → [external source audit](analysis/r7c0/) / [external manuscript evidence](analysis/r7c1/). Completed aggregate outputs are retained; no new discovery run is required for submission.
5. Verify scientific identities, negative/ambiguous states, reference build/alleles, signal-pair identity and model sensitivity before rebuilding figures/documents. The retained PDFs are WPS background exports; no LibreOffice parity is claimed.

Example verification from a repository checkout:

```powershell
python analysis/r7c3f/verify_public_manifest.py
```

This verifies canonical Git blobs against `MANIFEST.sha256`, so Windows line-ending normalization does not cause false scientific identity failures. Stage manifests retain their original coverage; they do not necessarily describe the entire rebuilt tree.

## Repository layout and history

`analysis/` holds original workflow and QA scripts; `results/` holds reviewed aggregate outputs; `protocols/` records frozen scope and decisions; `figures/` preserves stage figures; `manuscript/` contains versioned documents; `reports/` contains detailed action records; `audit/` contains identity/QA receipts; `data/` stores source pointers; `docs/` explains the current evidence and reuse paths. The complete local workspace stays in its thirteen classified folders.

The original Git history, scientific tags and Release descriptions/assets are backed up before repository recreation. Historical work records retain their original conclusions, including superseded counts and old “next” stages; consult the current state first. SSc, MG and IgAN remain archived. Their negative results and engineering assets are valuable for bounded future reuse, not a reason to resume failed biological hypotheses. Full audit/backup inventories with private machine paths stay local.

## Authors, licences and disclosure

Zhi Chen (first author; [ORCID](https://orcid.org/0009-0001-0072-5576)) and Teng Qi (corresponding author; [ORCID](https://orcid.org/0009-0007-7648-4776)), School of Medicine, The Chinese University of Hong Kong, Shenzhen. Correspondence: tengqi@link.cuhk.edu.cn. Author identities, originality, no funding/competing interests and AI-use disclosure were confirmed. Current declarations and factual contributions are in the manuscript; this repository does not sign a publisher declaration for the authors.

Original code: [MIT](LICENSE). Original author text, figures, protocols, documentation and aggregate derived results: [CC BY 4.0](LICENSE_CONTENT.md), subject to [NOTICE](NOTICE.md). Third-party data, tools and papers retain their own terms. Generative AI supported code/document preparation and review under author responsibility; no experimental result or source citation is created by that disclosure.

## Current submission decision

Target: **npj Genomic Medicine**, current article-type/portal instructions govern upload roles. Use one primary main DOCX. Exact-version author confirmation, actual official reporting forms, true-date cover letter, final-size figure check and publisher-generated merged PDF remain to be completed. No submission receipt or Zenodo DOI has been verified. Next: **R7C4 — final-version confirmation, reporting forms, portal proof and submission receipt**. New gene/cell/locus screening and global simulation reruns remain out of scope unless a concrete scientific defect emerges.

## Verified repository rebuild — 12 October 2026

The old repository was deleted (HTTP 204) and a new public repository was created at the same URL. New repository ID: 1414691109. All eight old tags and the old main at `archive/pre-rebuild-20261012` retain their Git identities; five historical Releases and ten asset files were restored. The new [R7C3F submission-candidate Release](https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/releases/tag/r7c3f-full-audit-rebuilt-submission-2026-10-12) is published. Twelve Release assets pass remote SHA-256 verification. See [publication receipt](audit/r7c3f/GITHUB_REBUILD_RECEIPT.json) and [detailed action report](reports/r7c3f/99_R7C3F_全量核查_GitHub重建_投稿包_详细行动记录_20261012.md). Repository/Release IDs and creation timestamps changed; journal submission and project DOI did not occur.
