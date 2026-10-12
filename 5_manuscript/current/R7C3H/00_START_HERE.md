# R7C3H expert evidence audit and editorial candidate — 2026-10-12

Start with `07_Reports/00_R7C3H_执行摘要_证据主线与最终裁决.md`, then read the Results-inline review manuscript. This release preserves the scientific endpoints and immutable R7C3F baseline while rebuilding argument flow and figure ownership.

## File roles

| Role | File |
|---|---|
| Journal candidate editable main, figures at end | 01_Manuscript/Manuscript_ExpertRebuilt.docx |
| WPS parity copy of candidate | 01_Manuscript/Manuscript_ExpertRebuilt.pdf |
| Reading/review main, figures with Results | 01_Manuscript/Manuscript_AuthorReview_InlineFigures.docx and .pdf |
| Six independent main figure masters | 02_Figures/Figure_1.pdf … Figure_6.pdf |
| Editable masters and reading raster copies | Corresponding SVG and 300dpi PNG |
| Three supplementary figure masters, also inside SI | Figure_S1–S3 PDF/SVG/PNG |
| One combined supplementary information | 03_Supplement/Supplementary_Information_ExpertRebuilt.pdf |
| Original workbook | 03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx |
| Full primary and bounded external aggregate evidence | 05_Source_Data/Source_Data_1*.zip and Source_Data_2*.zip |
| Editorial cover letter draft | 04_Cover/Cover_Letter_ExpertRebuilt_DRAFT.docx |
| Source/figure/claim/edit/QA audit ledgers | 06_QA/ |
| Chinese expert analysis/action record | 07_Reports/ |
| Editorial-stage regeneration scripts | 09_Code/ |

Do not upload both main versions as two Main Manuscripts. Exact-version author review and actual publisher proof remain pending; no journal submission/DOI/new GitHub editorial release is asserted here.

The original S10 ledger preserves its historical figure metadata. Use `03_Supplement/Supplementary_Editorial_Panel_Crosswalk.tsv` for all 27 C-series and 10 MR-series current destinations; C17 chromatin status is superseded by S11. Current E-series claim IDs are distinct.

## Regeneration and source contract

Run stage scripts in this dependency order: 01 inspect → 02 scientific replay → 03 figures → 04 documents → 07 current asset maps → 04a historical crosswalk → 05 WPS export → 06 machine QA → actual visual review → 08 packaging. Packaging rejects stale visual-review receipts. Scripts use the existing `H:/SCI2/YR1` frozen R7C3F source package and donor-aware prior-stage evidence. They are project-stage scripts, not a standalone reimplementation of original GWAS/fine-mapping from raw inputs. The scientific analysis repository retains those upstream tools. Run Python scripts with the bundled Python recorded in the action report; 05 exports DOCX via hidden Windows WPS COM. Source archives and workbook are byte-identical to the previous candidate. Script06 performs machine checks, while the separate visual receipt records completed review judgement.

This release contains aggregate evidence, not source genotype BED/BAMs or donor pseudobulk matrices. Third-party source terms remain in force. Existing author-owned code is under the project's MIT licence; author-owned manuscript text, newly drawn figures and shareable aggregate outputs follow the existing CC BY4.0 scope. No third-party asset is relicensed by this README. Consult the repository licence and source manifests.

The full local ~39k-file identity inventory remains in `5_analysis/R7C3H_ExpertNarrative_20261012`, outside this reader package. Counts are snapshot-specific. Machine QA pass does not establish causal mediation, universal algorithmic superiority or editorial acceptance.


## R7C3H statistical closure

The source-matched disease sample size remains N=24,510. A frozen 33-comparison Neff stress test produced no state or disease credible-set membership changes. Figures 1–6 therefore remain byte-identical; Source Data 3 records the new robustness analysis.
