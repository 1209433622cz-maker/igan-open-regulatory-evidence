"""Reorganize the existing public compendium without changing frozen scientific bytes.

Uses the already authenticated Git checkout. This prepares a reviewable tree only;
it does not delete a repository, rewrite Git history, push, or submit a manuscript.
"""
from pathlib import Path
import csv, hashlib, json, re, shutil, subprocess, datetime

ROOT = Path(r'H:\SCI2\YR1')
REPO = ROOT / '0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
STAGE = 'R7C3G1_20261012'
AN = ROOT / '5_analysis' / STAGE
REPORT = ROOT / '7.Report/rounds' / STAGE
PACK = ROOT / '5_manuscript/R7C3G_ExpertNarrative_20261012'
BACKUP = ROOT / '0_admin/backups/R7C3G1_GitHubEightFolder_20261012'
URL = 'https://github.com/1209433622cz-maker/igan-open-regulatory-evidence'
TAG = 'r7c3g1-eight-folder-expert-narrative-2026-10-12'
MOVE = {
    'analysis': '2_code', 'audit': '0_admin/audit', 'data': '1_data',
    'docs': '0_admin/docs', 'environment': '0_admin/environment',
    'figures': '4_figures/history', 'manuscript': '5_manuscript/history',
    'protocols': '0_admin/protocols', 'reports': '7.Report/rounds',
    'results': '3_results', 'workspace_support': '0_admin/workspace_support',
}
FOLDERS = ['0_admin','1_data','2_code','3_results','4_figures','5_manuscript','6_release','7.Report']

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def git(*args):
    return subprocess.check_output(['git','-C',str(REPO),*args]).decode('utf-8').strip()

def put(rel, text):
    p=REPO/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text.strip()+'\n',encoding='utf-8')

def save(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def tsv(p, rows, fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t')
        w.writeheader(); w.writerows(rows)

def map_old(rel):
    if rel=='data/README.md':return '1_data/history/README_before_R7C3G1.md'
    top,sep,tail=rel.partition('/')
    if top in MOVE:return MOVE[top]+('/'+tail if sep else '')
    return '0_admin/history/root_before_R7C3G1/'+rel

def main():
    assert git('status','--porcelain') == '', 'Checkout must be clean before preparation'
    assert (BACKUP/'before_restructure_all_refs.bundle').is_file()
    assert not (REPO/'0_admin').exists(), 'Do not run migration twice'
    AN.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
    head=git('rev-parse','HEAD')
    assert head == git('ls-remote','origin','refs/heads/main').split()[0], 'Remote diverged'
    oldfiles=git('ls-files','-z').split('\0')
    oldfiles=[p for p in oldfiles if p]
    original=[{'old_path':r,'new_path':map_old(r),'bytes':(REPO/r).stat().st_size,'sha256':sha(REPO/r)} for r in oldfiles]
    tsv(BACKUP/'original_tracked_files.tsv',original)
    # Root metadata is archived before any current navigation or status changes.
    for p in list(REPO.iterdir()):
        if p.is_file():
            dest=REPO/'0_admin/history/root_before_R7C3G1'/p.name
            dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
    # Move whole stage trees. Every historical data/script/report byte stays exact.
    for old,new in MOVE.items():
        src=REPO/old; dest=REPO/new
        assert src.is_dir() and not dest.exists(), (old,new)
        assert src.resolve().is_relative_to(REPO.resolve()) and dest.resolve().is_relative_to(REPO.resolve())
        dest.parent.mkdir(parents=True,exist_ok=True); shutil.move(str(src),str(dest))
    (REPO/'1_data/history').mkdir(parents=True,exist_ok=True)
    shutil.copy2(REPO/'1_data/README.md',REPO/'1_data/history/README_before_R7C3G1.md')
    for row in original:
        q=REPO/row['new_path']
        assert q.is_file() and sha(q)==row['sha256'], row['old_path']
        row['verification']='PASS_UNCHANGED_BYTES'
    tsv(REPO/'0_admin/audit/r7c3g1/PATH_MIGRATION_AND_PRESERVATION.tsv',original)
    # Freshly verify the editorial package against its frozen manifest.
    package_checks=0
    for line in (PACK/'checksums.sha256').read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():continue
        expected,rel=line.split('  ',1)
        assert sha(PACK/rel)==expected, rel
        package_checks+=1
    assert package_checks==93, package_checks
    current=REPO/'5_manuscript/current/R7C3G'
    assert not current.exists(); shutil.copytree(PACK,current)
    # Current outputs are deliberately mirrored in their scientific roles as well
    # as the self-contained exact-byte reader package.
    code=ROOT/'2_code/11_manuscript/R7C3G_ExpertNarrative_20261012'
    shutil.copytree(code,REPO/'2_code/11_manuscript/R7C3G',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    figure_rows=[]
    for i in ['1','2','3','4','5','6','S1','S2','S3']:
        role='main' if not i.startswith('S') else 'supplementary'
        folder=f'4_figures/Fig{i}/R7C3G' if role=='main' else f'4_figures/Supplementary/Fig{i}/R7C3G'
        for ext in ['pdf','svg','png']:
            src=PACK/'02_Figures'/f'Figure_{i}.{ext}'; dst=REPO/folder/src.name
            dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
            figure_rows.append({'figure':f'Figure_{i}','role':role,'format':ext,'repository_path':dst.relative_to(REPO).as_posix(),'bytes':dst.stat().st_size,'sha256':sha(dst)})
    tsv(REPO/'4_figures/CURRENT_FIGURE_INDEX.tsv',figure_rows)
    for p in (PACK/'07_Reports').iterdir():
        dest=REPO/'7.Report/rounds/r7c3g'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    for name in ['SCIENTIFIC_ENDPOINT_REPLAY_QA.tsv','EVIDENCE_AUDIT_STATE.json','COHORT_OUTCOMES_RECOMPUTED.tsv','A2_TO_M_RECOMPUTED.tsv','FIGURE_VALUES.json','SOURCE_ARCHIVE_FULL_INVENTORY.tsv']:
        dest=REPO/'3_results/r7c3g'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PACK/'06_QA'/name,dest)
    shutil.copy2(PACK/'08_Protocol/EDITORIAL_STATE.json',REPO/'0_admin/protocols/R7C3G_FROZEN_EDITORIAL_STATE.json')
    # Frozen source manifests are kept; add only an input-role guide.
    put('1_data/README.md','''# Input sources and identities

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
''')
    pointers=[]
    identity=ROOT/'5_analysis/R7C3G_ExpertNarrative_20261012/ALL_LOCAL_CURRENT_IDENTITY.tsv'
    with identity.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            rel=row['relative_path']
            if not rel.startswith('1_data/') or int(row['size_bytes'])<=10*1024*1024:continue
            p=ROOT/rel
            if not p.exists():continue
            st=p.stat();unchanged=st.st_size==int(row['size_bytes']) and st.st_mtime_ns==int(row['mtime_ns'])
            digest=row['sha256'] if unchanged else sha(p)
            pointers.append({'workspace_relative_path':rel,'bytes':st.st_size,'sha256':digest,'identity_basis':'PRIOR_FRESH_SHA256_REUSED_SIZE_MTIME_STILL_MATCH' if unchanged else 'NEW_FRESH_SHA256','in_git':'NO','recovery':'Original provider manifests or local frozen input; do not redistribute donor-level data'})
    tsv(REPO/'1_data/LOCAL_LARGE_INPUT_POINTERS.tsv',pointers)
    put('0_admin/README.md','''# Project administration, scope and identity

- [Current state](CURRENT_PROJECT_STATE.json): PBC remains GO; R7C3G is the latest editorial review candidate.
- [Eight-directory map](docs/EIGHT_FOLDER_MAP.md) and [evidence/reuse guide](docs/CURRENT_EVIDENCE_AND_REUSE.md).
- [Exact path migration](audit/r7c3g1/PATH_MIGRATION_AND_PRESERVATION.tsv): all old tracked file bytes survive at their mapped locations.
- `protocols/` preserves scientific freezes; new repository layout does not change their scope.
- `history/root_before_R7C3G1/` retains old README, manifests, citation and data/reproduction statements verbatim. Old IgAN descriptions here are historical, not the current PBC contract.
- `environment/` and `workspace_support/` retain stage environments and historical support scripts. This repository does not package installed runtimes or secrets.

Frozen stage documents retain their original local/repository paths. Use the migration table rather than editing scientific provenance. Historical tags and Releases retain the old tree. Git history has not been rewritten.
''')
    put('2_code/README.md','''# Code and reproduction stages

The original `analysis/` tree is now `2_code/`, preserving every original script byte. Current scientific stages include `r7b1/` (screen), `r7b1b_v2/` (642 multi-signal subset), `r7b1c/` (simulation), `r7b2a/` (same-input comparison), `r7c0/` and `r7c1/` (external evidence).

`11_manuscript/R7C3G/` reconstructs the current editorial figures/documents from frozen evidence. `00_repository/` verifies and reproduces this public tree organization. Original scripts use stage-specific local workspace paths; this is not a portable one-command raw-data-to-paper package. Consult [REPRODUCIBILITY](../REPRODUCIBILITY.md) and the relevant environment receipts first.

WPS COM is used for background DOCX/PDF export on Windows. Machine QA does not replace the separately recorded visual review. Original code is MIT; third-party code remains under its stated terms.
''')
    put('3_results/README.md','''# Reviewed aggregate results

This is the former `results/` tree, with every original byte retained. Historical SSc/MG/IgAN stages are archival. Current PBC evidence is versioned by scientific stage.

| Question | Entry |
|---|---|
| Same-input 642 trajectories | [R7B2A trajectories](r7b2a/adjudication/R7B2A_642_four_arm_trajectories.tsv) |
| Attribution summary | [R7B2A state](r7b2a/adjudication/R7B2A_attribution_state.json) |
| Known-truth simulation discovery/inference channels | [Channel table](r7b2a/simulation_audit/R7B2A_R7B1C_channel_summary.tsv) |
| External study/chromatin source limits | [External evidence](r7c1/external_evidence/) |
| Latest deterministic endpoint replay | [37 checks](r7c3g/SCIENTIFIC_ENDPOINT_REPLAY_QA.tsv) |
| Full primary and external tables used in the paper | [Exact Source Data ZIPs](../5_manuscript/current/R7C3G/05_Source_Data/) |

The repository restructuring did not rerun GWAS, LD, SuSiE or the 486,000 simulations. The R7C3G replay recomputed documented endpoints from frozen outputs. A historical pass/fail state is not silently updated by new navigation.
''')
    put('4_figures/README.md','''# Figure masters and historical selections

Current main figures: `Fig1/` through `Fig6/`. Current supplementary figures: `Supplementary/FigS1/` through `FigS3/`. Every figure has a vector PDF, editable SVG and 300-dpi PNG. [Index and checksums](CURRENT_FIGURE_INDEX.tsv).

| Figure | Question |
|---|---|
| 1 | Scope, input contract and outcome denominators |
| 2 | Same-input residual bidirectional reclassification |
| 3 | Signal-pair identity, cell context and PF10/PF50 sensitivity |
| 4 | Known-truth simulation gains, losses and evaluability |
| 5 | Bounded external IL12RB2 disease/chromatin support |
| 6 | Liver detectability and the corrected nonsignificant disease boundary |
| S1–S3 | Technical QA, simulation channels and correlated release sensitivity |

There are 22 main and 12 supplementary panels. PDFs/SVGs/PNGs are alternative formats, not independent experiments. `history/` preserves every earlier figure; superseded displays must not replace current model/cell/source definitions. See the [46-image selection ledger](../5_manuscript/current/R7C3G/06_QA/ALL_46_IMAGE_SELECTION_LEDGER.tsv), [34-panel source map](../5_manuscript/current/R7C3G/06_QA/PANEL_EVIDENCE_MAP.tsv), and [historical S10 crosswalk](../5_manuscript/current/R7C3G/03_Supplement/Supplementary_Editorial_Panel_Crosswalk.tsv).
''')
    put('5_manuscript/README.md','''# Manuscript versions

**Current editorial review candidate: [R7C3G](current/R7C3G/00_START_HERE.md).** It applies QiTeng v0.3.24.2 and preserves the scientific source archives/workbook. It is not a journal submission or acceptance.

- [Editable main manuscript](current/R7C3G/01_Manuscript/Manuscript_ExpertRebuilt.docx) and [24-page WPS PDF](current/R7C3G/01_Manuscript/Manuscript_ExpertRebuilt.pdf).
- [25-page inline-figure review PDF](current/R7C3G/01_Manuscript/Manuscript_AuthorReview_InlineFigures.pdf).
- [Figure review gallery](current/R7C3G/FIGURE_REVIEW_GALLERY.html), [supplement](current/R7C3G/03_Supplement/), [Source Data](current/R7C3G/05_Source_Data/).
- [Upload roles](current/R7C3G/UPLOAD_ROLES_AND_IDENTITIES.tsv), [editorial change ledger](current/R7C3G/06_QA/EDITORIAL_CHANGE_LEDGER.tsv), [WPS/visual QA](current/R7C3G/06_QA/).

The self-contained `current/R7C3G` package is an exact-byte copy of the audited local reader package. Its stage state is frozen and correctly records that GitHub publication had not occurred at creation time; the later repository publication receipt lives in `../0_admin/audit/r7c3g1/`.

`history/r7c3f/` retains the prior baseline, and all earlier manuscript stages are kept in `history/`. Author identities/declarations remain confirmed; the newly reconstructed exact version still requires final author review and publisher proof. Use one main manuscript at submission, not both reading variants.
''')
    put('6_release/README.md',f'''# Hash-frozen delivery releases

Current repository release: [{TAG}]({URL}/releases/tag/{TAG}). The R7C3G scientific/editorial ZIP is a GitHub Release asset rather than another redundant Git blob. Its SHA-256 is `12314510de0c1dc73cd9c3e4371cb4ffd079210bf58deb3df4c957810e094891`, size 17,314,147 bytes, CRC PASS and internal SHA-256 93/93 PASS. [Exact source receipt](R7C3G_RELEASE_RECEIPT.json).

Earlier tags and Releases remain intact at their historical paths. A public GitHub Release is not a journal submission, acceptance or Zenodo DOI. `PUBLICATION_RECEIPT.json` records the independently checked remote commit/tag/asset identity after publication.
''')
    receipt=ROOT/'6_release/R7C3G_20261012/RELEASE_RECEIPT.json'
    shutil.copy2(receipt,REPO/'6_release/R7C3G_RELEASE_RECEIPT.json')
    put('7.Report/README.md','''# Action reports and decision history

- [Latest expert audit and narrative reconstruction](rounds/r7c3g/01_R7C3G_导师级全量证据审计与叙事重构.md).
- [Latest full action record](rounds/r7c3g/99_R7C3G_详细行动记录_20261012.md).
- Repository restructuring/publication is recorded separately under `rounds/r7c3g1/`.
- All original `reports/` files survive under `rounds/`, retaining their exact bytes and stage-specific conclusions.

Historical “next stage”, gene priority and manuscript decisions are version-specific. Current PBC state is in [0_admin](../0_admin/CURRENT_PROJECT_STATE.json). SSc, MG and IgAN remain archives; their negative evidence and engineering methods can be reused without reviving those biological hypotheses. [Reuse guide](../0_admin/docs/CURRENT_EVIDENCE_AND_REUSE.md).
''')
    put('0_admin/docs/EIGHT_FOLDER_MAP.md','''# Canonical eight-directory GitHub layout

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
''')
    put('0_admin/docs/CURRENT_EVIDENCE_AND_REUSE.md','''# Current evidence, durable methods and bounded reuse

PBC remains the main project under RP v4. The strongest paper is an empirical study of regulatory attribution reliability: input matching, source/model-matched LD, multi-signal pair interpretation, covariate sensitivity, simulation trade-offs and explicit external/tissue boundaries.

| Evidence | Frozen finding | Limit |
|---|---|---|
| Screening | 6,923 registered; 5,460 eligible; 1,463 insufficient | Not all combinations underwent multi-signal inference |
| Follow-up | 642 comparisons; 47 loci/200 genes/14 cells/286 blocks | 184 primary, 455 H3 rescue, 3 borderline remain separately reported |
| PF10 | 92 H4 / 428 H3 / 59 sensitive / 63 uninformative | 92 comparisons are not 92 independent gene discoveries |
| Same-input A2→M | 8 H4→H3 and 10 H3→H4 | Real-data transitions are not truth-known error rates |
| Pair interpretation | 32 H4-supported comparisons also contain distinct pairs | A shared regional pair is not regional universal sharing |
| PF10/PF50 | 491/520 same, 4 change, 25 uninformative | Model sensitivity is retained, including FCRL3/CD8_ET |
| Simulation | 486,000 iterations; 160,782 pair-evaluable | False sharing 12.41→8.56%, shared recovery 32.99→26.66%; no universal superiority |
| External support | IL12RB2 disease-eQTL / disease-caQTL and peak link | NK QTL strata; peak-gene best cell PBMC; no direct mediation proof |
| Tissue | 5 PBC/5 controls, both axes detectable | Both corrected q≈0.111; no disease-specific enrichment |

The current figure order is scope/input contract → matched-input reclassification → pair/cell/model sensitivity → simulation trade-offs → external support → tissue boundary. This avoids letting strong external support conceal the model-sensitive counterexample or tissue null.

OneK1K/TenK10K sharing uses the same PBC disease GWAS, so it is independent molecular-resource support, not independent disease replication. FinnGen is an external study system; person-level overlap is unknown. R12/R13 are correlated sequential releases, not two independent cohorts. The PBMC peak-gene link must not be described as NK-specific causal mediation.

Preserve for future projects: checksum/provenance, variant/build/allele identity, active-donor and covariate identity, source-matched LD, source-CS coverage, complete negative/ambiguous states, prior/configuration sensitivity, pair identity, discovery versus inference simulation channels, donor-level tissue statistics, and source-to-panel-to-claim traceability. Archived SSc/MG/IgAN stop decisions are also valuable boundary evidence. Do not transfer their old genes as new biological assumptions.

No new disease/gene/cell screen or global simulation rerun is justified by the current audit. Next is R7C3H exact-version author review and publisher proof. A real submission receipt is required before declaring submission complete. Original code is MIT; author-owned text/figures/shareable aggregate outputs are CC BY4.0; provider data retain provider terms.
''')
    put('REPRODUCIBILITY.md','''# Current PBC reproducibility contract — RP v4 / R7C3G

The current primary project is **PBC**, not IgAN. The superseded root contract is archived in `0_admin/history/root_before_R7C3G1/REPRODUCIBILITY.md`.

1. Verify provider byte identity, genome build, alleles/effect direction, cell-specific active donors and source/covariate/model identity before statistical analysis. Large inputs are recovered from `1_data/` manifests, not mirrored here.
2. Preserve the 6,923 screening universe, 5,460 eligible comparisons and separate coverage-insufficient states. The source-matched multi-signal cohort is the prespecified 642 high-information subset (184 primary + 455 H3 rescue + 3 borderline), not an all-comparison multi-signal census.
3. Keep A0/A1/A2/M variant-support and disease-statistic contrasts distinct. Source/model-matched PF10 is primary and PF50 is sensitivity; retain actual signal-pair credible sets and diagnostic/evaluability states. The frozen stage protocols, not a simplified global rule, define each stage's gates and priors.
4. Scientific R stages used the recorded `coloc` 5.2.3 / `susieR` 0.14.2 environments. Stage scripts retain explicit local workspace/input settings. This is a documented research compendium, not a one-command portable raw-data-to-paper workflow.
5. Simulation separates credible-set discovery, pair-evaluable inference and end-to-end recovery. Never label uninformative or failed credible-set discovery as a biological distinct signal. Real-data reclassification is not a known-truth error rate.
6. R7C3G figure/document regeneration uses `2_code/11_manuscript/R7C3G`: 01 → 02 → 03 → 04 → 07 → 04a → 05 WPS → 06 machine QA → actual visual review → 08 package. Inputs are the frozen local R7C3F package and prior-stage results. WPS export is Windows-specific; automatic machine QA does not replace visual proof review.

Verify the current Git snapshot with Python standard library only:

```powershell
python 2_code/00_repository/verify_repository.py
```

This verifies canonical Git blobs against `MANIFEST.sha256`, independent of Windows working-tree line endings. The manifest excludes only itself. Old stage manifests retain original relative-path scope; use the path migration table when their repository paths refer to the old layout, or inspect the original historical tag. No original GWAS/LD/SuSiE/simulation fits were rerun by the repository restructuring.
''')
    state={'stage':'R7C3G1_GITHUB_EIGHT_FOLDER_RESTRUCTURE','date':'2026-10-12','PBC_PRIMARY_PROJECT':'GO','RP':'v4','current_editorial_candidate':'R7C3G','baseline':'R7C3F preserved','scientific_endpoints_changed':False,'original_scientific_fits_rerun':False,'new_candidate_exact_version_author_review':'PENDING','journal_submission_completed':False,'Zenodo_DOI_verified':False,'NEXT':'R7C3H_EXACT_VERSION_AUTHOR_REVIEW_AND_PUBLISHER_PROOF','scientific_replay':'37/37 PASS (R7C3G)','document_QA':'160/160 PASS (R7C3G)','WPS':'4/4 exports;56 pages reviewed (R7C3G)','new_public_folder_roots':FOLDERS,'archived_projects':['SSc','MG','IgAN']}
    save(REPO/'0_admin/CURRENT_PROJECT_STATE.json',state)
    put('README.md',f'''# PBC regulatory attribution reliability

**Input matched multisignal colocalization clarifies regulatory assignments at primary biliary cholangitis loci**

Current project: **PBC, RP v4**. Latest editorial candidate: **R7C3G**, prepared with QiTeng v0.3.24.2, with unchanged scientific endpoints and original Source Data. Repository structure: **R7C3G1, 12 October 2026**. The historical `igan-open-regulatory-evidence` URL is retained for manuscript links and scientific tags; IgAN is archived. This is open research and a submission-review candidate, not a submitted/accepted paper or a verified Zenodo DOI.

## Read the paper and its evidence

| Need | Entry |
|---|---|
| Editable current main manuscript | [DOCX](5_manuscript/current/R7C3G/01_Manuscript/Manuscript_ExpertRebuilt.docx) / [24-page WPS PDF](5_manuscript/current/R7C3G/01_Manuscript/Manuscript_ExpertRebuilt.pdf) |
| Read figures beside their Results | [25-page WPS review PDF](5_manuscript/current/R7C3G/01_Manuscript/Manuscript_AuthorReview_InlineFigures.pdf) |
| Current figure masters | [Fig1–6 and S1–S3](4_figures/README.md) / [figure gallery](5_manuscript/current/R7C3G/FIGURE_REVIEW_GALLERY.html) |
| Supplement and full aggregate evidence | [Supplement](5_manuscript/current/R7C3G/03_Supplement/) / [Source Data 1–2](5_manuscript/current/R7C3G/05_Source_Data/) |
| Expert audit and narrative decisions | [Expert report](7.Report/rounds/r7c3g/01_R7C3G_导师级全量证据审计与叙事重构.md) / [action record](7.Report/rounds/r7c3g/99_R7C3G_详细行动记录_20261012.md) |
| Source-to-panel-to-claim traceability | [34-panel map](5_manuscript/current/R7C3G/06_QA/PANEL_EVIDENCE_MAP.tsv) / [historical ledger crosswalk](5_manuscript/current/R7C3G/03_Supplement/Supplementary_Editorial_Panel_Crosswalk.tsv) |
| Portable snapshot identity check | [Reproduction contract](REPRODUCIBILITY.md) / [SHA-256 manifest](MANIFEST.sha256) |
| Full review-package download | [Versioned GitHub Release]({URL}/releases/tag/{TAG}) |

The HTML gallery can be downloaded with its package and opened locally; GitHub displays its source. Do not upload both manuscript reading variants as separate Main Manuscripts.

## Scientific question and narrative

The study asks when regulatory attribution is stable or changes after input matching, source/model-matched LD and multi-signal decomposition. It separates input-definition effects from causal-assumption effects and tests the consequences using known-truth simulation and bounded external/tissue evidence. The manuscript order is **scope and input contract → matched-input bidirectional reclassification → pair/cell/model sensitivity → simulation gains and losses → external IL12RB2 support → liver detectability and disease-null boundary**.

| Analysis | Frozen result | Interpretation boundary |
|---|---|---|
| PBC-wide screening | 6,923 registered; 5,460 eligible; 1,463 coverage-insufficient | Coverage insufficiency is not a negative result |
| High-information follow-up | 642 comparisons; 47 loci, 200 genes, 14 cells, 286 blocks | 184 primary + 455 H3 rescue + 3 borderline; not all screened comparisons |
| PF10 outcome | 92 H4, 428 H3, 59 model-sensitive, 63 uninformative | Comparison counts are not independent gene discoveries |
| Same-input A2→M | 8 H4→H3; 10 H3→H4 | Real-data reclassification is not a known-truth error rate |
| Pair-specific meaning | 32 H4-supported comparisons also have distinct pairs | One shared pair does not make all regional signals shared |
| PF10/PF50 sensitivity | 491/520 same; 4 change; 25 uninformative | FCRL3/CD8_ET is a retained model-sensitive counterexample |
| Simulation | 486,000 iterations; 160,782 pair-evaluable (33.08%) | Discovery adequacy and conditional inference are separate |
| Simulation trade-off | False sharing 12.41%→8.56%; shared recovery 32.99%→26.66% | No universal algorithm superiority |
| Liver tissue | 5 PBC versus 5 controls; targets detected | Both corrected q≈0.111; no PBC-specific enrichment |

OneK1K/TenK10K evidence is cross-resource molecular-QTL support using the same PBC GWAS. FinnGen is an external disease-study system, but participant non-overlap is unknown. IL12RB2 NK disease-eQTL/caQTL support and a **PBMC** peak-gene link do not establish NK-specific chromatin mediation. R12/R13 are correlated sequential releases. Known IL12RB2/FCRL3 genes are examples, not new causal discoveries or treatment mechanisms.

## Eight-directory repository

```text
0_admin/       protocols, decisions, environments, source and publication audits
1_data/        input-source metadata and large-file identities
2_code/        scientific workflows and figure/document/verification scripts
3_results/     compact reviewed aggregate results and QA
4_figures/     current Fig1–6/S1–S3 masters and historical figures
5_manuscript/  current exact-byte candidate and immutable previous versions
6_release/     release receipts, version identities and download routes
7.Report/      detailed action reports and next-stage decisions
```

[Directory map](0_admin/docs/EIGHT_FOLDER_MAP.md) · [old→new path and unchanged-byte map](0_admin/audit/r7c3g1/PATH_MIGRATION_AND_PRESERVATION.tsv) · [evidence and future reuse](0_admin/docs/CURRENT_EVIDENCE_AND_REUSE.md).

All pre-existing tracked file bytes survive at mapped locations. Historical tags/Releases retain their original layouts; no history was rewritten. Frozen historical scripts/documents keep stage-specific local paths and old conclusions. Use the current state and migration map instead of treating those as current instructions. SSc, MG and IgAN remain archived, with their negative evidence and engineering assets retained.

## A retained counterexample

![Figure 3: signal-pair identity, cell context and model sensitivity](4_figures/Fig3/R7C3G/Figure_3.png)

Figure 3 keeps the FCRL3/CD8_ET PF10/PF50 reversal visible. The manuscript uses it to expose model sensitivity, alongside supported B-cell contexts, rather than treating all strong regional eQTL as the same mechanism. The independent vector masters and full legend are in the manuscript package.

## Reproduction, inputs and quality

Read [REPRODUCIBILITY.md](REPRODUCIBILITY.md) before running a scientific stage. Reconstruct raw inputs from [source manifests](1_data/README.md); raw BAM/PLINK genotypes, donor matrices, large LD arrays, installed environments and copyrighted papers are not mirrored. Their local identities are recorded, with provider terms retained. See [data availability](DATA_AVAILABILITY.md).

```powershell
python 2_code/00_repository/verify_repository.py
```

The verifier checks canonical Git blobs. Scientific stage environments and fixed input contracts are preserved; scripts use explicit local workspace paths and are not advertised as a one-command end-to-end pipeline. R7C3G has 37/37 deterministic endpoint replay checks, 160/160 machine document checks, 4/4 WPS exports and 56/56 pages visually reviewed. Its 6 main + 3 supplementary figures comprise 34 traceable panels. Scientific data/previous baseline assets are unchanged. GitHub synchronization does not itself rerun or validate raw scientific fits.

## Authors, licences and disclosure

Zhi Chen (first author, [ORCID](https://orcid.org/0009-0001-0072-5576)) and Teng Qi (corresponding author, [ORCID](https://orcid.org/0009-0007-7648-4776)), School of Medicine, The Chinese University of Hong Kong, Shenzhen. Correspondence: tengqi@link.cuhk.edu.cn. Confirmed author identities and no-funding/no-competing-interest declarations remain in the manuscript. Generative AI assistance is disclosed under author responsibility; repository publication is not an author signature on publisher forms.

Original code: [MIT](LICENSE). Original author-owned text, figures, documentation and shareable aggregate outputs: [CC BY4.0](LICENSE_CONTENT.md), subject to [NOTICE](NOTICE.md). Third-party inputs retain their provider terms. No donor-level data or source access credential is published by this restructuring.

## Current decision

**PBC = GO. Next: R7C3H exact-version author review and publisher-generated PDF proof**, followed by an author-operated npj Genomic Medicine submission and recorded receipt. New biological candidate screening and global simulation reruns remain out of scope without a concrete scientific defect. No submission, acceptance, new experiment or DOI is claimed by this release. [Current state](0_admin/CURRENT_PROJECT_STATE.json).
''')
    put('DATA_AVAILABILITY.md','''# Current PBC data availability and redistribution scope

Original code, author-owned manuscript/figures/protocols and reviewed compact aggregate results are public. [Source Data 1 and 2](5_manuscript/current/R7C3G/05_Source_Data/) contain the frozen machine-readable primary and bounded external evidence. The [S1–S10 workbook](5_manuscript/current/R7C3G/03_Supplement/) is unchanged; the separate editorial crosswalk updates historical panel routes without overwriting source data.

Provider raw inputs are not redistributed: full GWAS/QTL archives, GJOKA source archive/large LD arrays, OneK1K genotypes/covariates/pseudobulk, TenK10K full cis-eQTL, BAM/RDS and copyrighted article PDFs. [Input manifest guide](1_data/README.md), [original large-data identities](1_data/LARGE_DATA_MANIFEST.tsv), [local large-input identity pointers](1_data/LOCAL_LARGE_INPUT_POINTERS.tsv), and [external source ledgers](3_results/r7c1/external_evidence/) record recovery routes and byte/source conditions. Public access does not imply unrestricted redistribution.

Individual participant content and the full private local-workspace index stay local. Public liver target-panel results are aggregate donor-level analysis outputs; they are not raw cell or read data. The 5-versus-5 analysis supports detectability, without corrected disease-specific enrichment. Cross-molecular-resource sharing reuses the discovery GWAS; FinnGen person-level non-overlap remains unknown.

The repository is a research compendium, not proof of journal submission or a generated Zenodo DOI. Code is MIT; original shareable author content is CC BY4.0; third-party sources retain provider terms under [NOTICE](NOTICE.md).
''')
    cff=(REPO/'CITATION.cff').read_text(encoding='utf-8').replace('1.4.0','1.5.0')
    (REPO/'CITATION.cff').write_text(cff,encoding='utf-8')
    zen=json.loads((REPO/'.zenodo.json').read_text(encoding='utf-8'))
    zen['version']='1.5.0'
    zen['description']='PBC regulatory attribution reliability research compendium. R7C3G rebuilds the manuscript narrative and 34 traceable panels with unchanged scientific endpoints and Source Data; R7C3G1 reorganizes the public repository into eight canonical directories. The prespecified 642 high-information comparisons, same-input bidirectional reclassification, model sensitivity, known-truth simulation trade-offs and bounded external/tissue evidence are reported. This is an editorial review candidate: exact-version author review, publisher proof and journal submission remain pending. Participant-level external independence, chromatin mediation and universal algorithm superiority are not established. This metadata file does not establish a Zenodo deposit or DOI.'
    save(REPO/'.zenodo.json',zen)
    put('.gitignore','''# Do not commit third-party raw inputs, donor content or installed runtimes.
raw_data/
**/__pycache__/
*.py[cod]
*.bed
*.bim
*.fam
*.pgen
*.pvar
*.psam
*.vcf
*.vcf.gz
*.bcf
*.bam
*.cram
*.h5ad
*.rds
*.RDS
*.npy
*.npz
*.tar
*.tar.gz
*active_donors.txt
*standardized*A1*dosage*
*correlation.float32.bin
.env
.env.*
*.pem
*.key
credentials*
secrets*
.Rhistory
.RData
.pytest_cache/
/logs/
# 1_data source metadata and audited aggregate Source Data ZIPs are intended.
''')
    save(AN/'PREPARATION_STATE.json',{'old_head':head,'original_files':len(original),'preserved_original_files':len(original),'current_package_checks':package_checks,'large_input_pointers':len(pointers),'folder_roots':FOLDERS,'tag':TAG,'repository':URL,'scientific_changes':False,'push_executed':False})
    print(json.dumps({'original_files_preserved':len(original),'package_checks':package_checks,'large_input_pointers':len(pointers),'status':'PREPARED_NOT_PUSHED'}))

if __name__=='__main__':main()
