"""Prepare a reviewable public tree and exact-byte submission candidate."""
from pathlib import Path
import subprocess, tarfile, tempfile, hashlib, json, shutil, csv, zipfile, re, os
ROOT=Path(r'H:\SCI2\YR1'); OLD=ROOT/'0_admin/repositories/igan-open-regulatory-evidence'
PUB=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
AN=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012'
PACK=ROOT/'5_manuscript/R7C3F_SubmissionCandidate_20261012'
SOURCE=ROOT/'5_manuscript/R7C3C_SubmissionCandidate_20261012'
REL=ROOT/'6_release/R7C3F_20261012'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def put(rel,text):p=PUB/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def tsv(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def main():
    assert not PUB.exists(), 'Do not overwrite a staged or published repository'
    PUB.mkdir(parents=True)
    head=subprocess.check_output(['git','-C',str(OLD),'rev-parse','HEAD'],text=True).strip()
    with tempfile.TemporaryDirectory(prefix='r7c3f_archive_') as td:
        a=Path(td)/'snapshot.tar'
        subprocess.run(['git','-C',str(OLD),'archive','--format=tar','--output',str(a),head],check=True)
        with tarfile.open(a) as t:t.extractall(PUB,filter='data')
    # The public baseline is canonical Git blobs, not a CRLF-normalized checkout.
    (PUB/'docs/history').mkdir(parents=True,exist_ok=True)
    shutil.copy2(PUB/'README.md',PUB/'docs/history/README_before_R7C3F.md')
    shutil.copy2(PUB/'DATA_AVAILABILITY.md',PUB/'docs/history/DATA_AVAILABILITY_before_R7C3F.md')
    # Archive superseded whole-tree manifests, leaving historical stage manifests intact.
    if (PUB/'MANIFEST.sha256').exists():shutil.move(str(PUB/'MANIFEST.sha256'),str(PUB/'docs/history/MANIFEST_before_R7C3F.sha256'))
    assert not PACK.exists();shutil.copytree(SOURCE,PACK)
    roles=[]
    for p in sorted(SOURCE.rglob('*')):
        if p.is_file():
            target=PACK/p.relative_to(SOURCE);assert sha(p)==sha(target)
            roles.append({'path':p.relative_to(SOURCE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'identity':'UNCHANGED_FROM_R7C3C'})
    (PACK/'00_START_HERE.md').write_text('''# npj Genomic Medicine 投稿候选包 — R7C3F，2026-10-12

这是一份重新校验的投稿候选包，不是投稿回执。22 个原有资产与 R7C3C 逐字节一致：主稿文字、作者信息、六幅图、WPS PDF、补充工作簿和两份 Source Data 均未修改。新增文件仅提供本轮导航和身份验证。

1. 唯一主稿：`01_Main/Manuscript.docx`。包含文末 Figure 1–6；WPS PDF 用于比对，不自动作为第二份主稿。
2. 独立 Figure PDF 是否上传，以实际门户要求为准。若要求无图主稿，应从同一批准文字生成新模式，重新核验并记录新哈希。
3. 补充文件：SI PDF、Supplementary Data 1（S1–S10）、Source Data 1、Source Data 2（含 S11）。可编辑 SI 及 PDF/DOCX cover companions 是工作底稿，避免重复上传。
4. 提交前补齐这组文件的最终作者确认、实际官方 reporting forms、真实投稿日期、最终尺寸图件和出版社合并 proof 检查。
5. 既有作者身份、原创性、无 funding/利益冲突及 AI 披露授权保留；本轮不代签作者、不产生期刊投稿回执或 Zenodo DOI。

科学证据保持 RP v4 上限：调控归因可靠性、同输入方法对照、双向多信号重分类、模型敏感性和外部证据边界。共有信号不等于因果机制；组织检出不等于疾病特异富集。原稿代码链接仍使用同一 GitHub 仓库网址与既有科学 tag。

`ASSET_IDENTITY_R7C3F.tsv` 给出全部原有资产身份；`checksums.sha256` 校验本候选包所有文件，校验清单自身除外。PDF 保留原 WPS 后台导出版本，本轮没有重新渲染，也没有声称重新做了逐页视觉审稿。
''',encoding='utf-8')
    tsv(PACK/'ASSET_IDENTITY_R7C3F.tsv',roles)
    files=[p for p in sorted(PACK.rglob('*')) if p.is_file() and p.name!='checksums.sha256']
    (PACK/'checksums.sha256').write_text(''.join(f'{sha(p)}  {p.relative_to(PACK).as_posix()}\n' for p in files),encoding='utf-8')
    REL.mkdir(parents=True,exist_ok=True);zpath=REL/'CMM_R7C3F_npj_Submission_Candidate_20261012.zip'
    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(PACK.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(PACK).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        for line in z.read('checksums.sha256').decode().splitlines():
            h,n=line.split('  ',1);assert hashlib.sha256(z.read(n)).hexdigest()==h
    (REL/(zpath.name+'.sha256')).write_text(f'{sha(zpath)}  {zpath.name}\n',encoding='utf-8')
    # Publish exact submission assets in a distinct current folder; preserve old stages.
    shutil.copytree(PACK,PUB/'manuscript/r7c3f')
    for name in ['VALUABLE_ASSETS.tsv','PROJECT_TIMELINE.tsv']:
        shutil.copy2(OLD/'audit/r7c3c/catalogue'/name,PUB/'docs'/name)
    put('docs/WORKSPACE_STRUCTURE.md','''# Local workspace and public research tree

The local H:/SCI2/YR1 workspace contains thirteen canonical folders. This public tree retains portable stage paths so historical scripts and manuscript citations continue to resolve. Navigation catalogues do not imply that all local sources are redistributed.

| Local folder | Role | Public counterpart / policy |
|---|---|---|
| 0_admin | States, protocols, licences, navigation and toolchain | protocols/, audit/, environment/; credentials and vendor runtimes stay local |
| 1_data | Frozen third-party input bytes and derived donor matrices | data/ accession/URL/size/checksum pointers only |
| 2_code | Intake, harmonization, LD, inference, QA and document assembly | analysis/ original scripts |
| 3_results | Complete aggregate result and diagnostic outputs | results/ reviewed aggregate outputs |
| 4_figures | Fig1–8 with stages and content annotations | figures/ scientific assets; Fig7 MG and Fig8 IgAN are archives |
| 4_output | Intermediate exports | selected outputs only; not a scientific authority |
| 5_analysis | Interpretive audits and classification tables | audit/ and docs/ reviewed summaries; full private paths stay local |
| 5_manuscript | Versioned manuscript/submission candidates | manuscript/r7c3f is current; earlier directories are historical |
| 6_release | Hash-frozen delivery ZIPs | GitHub Releases, not redundant raw-data commits |
| 7.Report | Detailed action records and round conclusions | reports/ reviewed stage records |
| 8.Reference | Papers, bibliographic and guideline sources | source identifiers and original synthesis only; article PDFs stay local |
| 9.Version | Immutable snapshots, rollback backups and research plans | historical Git refs and reviewed records; bulk backups stay local |
| 9_Vote | Current and historical decisions | protocols/ current state and records |

Full-size inputs are listed in data/LARGE_DATA_MANIFEST.tsv and stage-specific source ledgers. Local full-byte audit includes vendor runtimes and Git objects, but neither is scientific evidence by itself. Historical frozen text retains its original paths; the local OLD_PATH_LOOKUP.tsv resolves reorganized assets. Existing runtime adapters preserve referenced interfaces. Duplicate bytes are reported, not automatically deleted.
''')
    put('docs/EVIDENCE_AND_REUSE.md','''# Evidence, durable assets and bounded reuse

## Current PBC evidence

The project examines the reliability of regulatory assignment, not the first discovery of IL12RB2 or FCRL3 and not a general claim of method superiority. Sources are the manuscript, Source Data 1/2, results/r7b2a and results/r7c1.

- Registry: 6,923 comparisons; 5,460 ABF-eligible; 1,463 coverage-insufficient. High-information follow-up: 642 = 184 primary + 455 H3 rescue/falsification + 3 borderline. It covers 47 loci, 200 genes, 14 cell types and 286 cell–locus blocks. This is not a multi-signal census of all 6,923.
- PF10: 92 H4-supported, 428 H3-supported, 59 model-sensitive, 63 uninformative. The 92 comparisons involve 27 genes and 19 loci. 32 H4 comparisons also contain qualifying H3 pairs; a regional binary label is insufficient.
- Same-input A2→M: eight H4→H3 and ten H3→H4 transitions. Support restriction and disease-definition matching change 15 and 19 states; counts may overlap. Real-data transitions are not known-truth error rates.
- PF10/PF50: among 520 definite PF10 outcomes, 491 agree, four change and 25 become PF50-uninformative. FCRL3/CD8_ET is model-sensitive, not a discarded inconvenient result.
- Simulation: 486,000 iterations; 160,782 pair-evaluable (33.08%). False H4 falls from 12.41% to 8.56% while shared-signal recovery falls from 32.99% to 26.66%. Two empirical LD templates and fixed sample sizes bound generalization.
- IL12RB2–NK/FCRL3–B have cross-resource molecular-QTL support. OneK1K and TenK10K reuse the same PBC discovery GWAS; this is not independent disease replication.
- FinnGen R13 adds a different disease-study system (795 cases); person-level independence is not established. IL12RB2 disease–eQTL/caQTL and peak–gene links support signal coherence; the missing direct eQTL–caQTL posterior prevents a mediation claim.
- Liver: five PBC versus five non-lesion surgical controls; both target-lineage axes detected in 5/5 each. Neither is significant after correction (both q≈0.111). Detectability does not establish disease enrichment.

## Reusable engineering and records

Keep byte provenance, variant/build/allele identity, active-donor sets, covariate/model-matched LD, source-CS coverage, complete non-trigger states, prior sensitivity, posterior signal-pair identity, known-truth simulation channels, donor-level rather than cell-level comparison, and WPS/manuscript/source-data traceability. Exact stage protocols and action reports preserve what was tested and what was not.

The archived SSc/MG/IgAN projects contribute intake, LD and negative-evidence methods; they are not the current biological hypothesis. REEP3 molecular-replication failure and the MG chr18/chr5 stop decisions are retained. The local 54-paper corpus and its writing-method matrix can guide future synthesis; article PDFs remain local. Historical missing individual paper-analysis reports are logged as not located in the scanned local archive, not recreated or declared permanently lost.

## Next decisions

Keep PBC and the exact R7C3B/QiTeng/WPS candidate. Finish final-version author confirmation, official reporting forms, actual-date cover letter and publisher merged-PDF proof. Capture a real submission receipt before marking submission complete. Do not enlarge the gene/cell/locus universe or rerun 486,000 simulations without a specific new defect. A Zenodo DOI remains unverified; a GitHub tag or newly recreated repository is not a DOI.
''')
    put('DATA_AVAILABILITY.md','''# Data availability and redistribution boundaries

Original analysis code, protocols, aggregate derived tables, source-bound figures, work records and current manuscript assets are public here. Original code is MIT; original text/figures/documentation and aggregate derived results are CC BY 4.0 under NOTICE.md. Third-party inputs retain provider terms and are not relicensed.

The current candidate is [manuscript/r7c3f](manuscript/r7c3f/00_START_HERE.md). [Source Data 1](manuscript/r7c3f/05_Source_Data/Source_Data_1_Primary_Machine_Readable_Data.zip) contains the primary machine-readable scientific tables; [Source Data 2](manuscript/r7c3f/05_Source_Data/Source_Data_2_External_Regulatory_Evidence.zip) contains the external-evidence supplement. All 48 scientific members are unchanged from the frozen prior submission assets.

Use [LARGE_DATA_MANIFEST.tsv](data/LARGE_DATA_MANIFEST.tsv), [additional large-asset identities](data/R7C3C_LARGE_ASSET_POINTERS.tsv), and the ledgers in results/r7c1/external_evidence/ for exact provider URLs, accessions, expected byte counts, checksums and source roles. Primary sources include GCST90061440, GJOKA, OneK1K, TenK10K, FinnGen and HRA008003; OMIX001122 is bounded by the documented missing coordinates and sample structure. Full raw GWAS/QTL archives, PLINK donor genotypes, covariates, pseudobulk, LD matrices, BAM, RDS and copyrighted article PDFs are not mirrored. A publicly downloadable source is not automatically an unrestricted redistribution licence.

The exact five-versus-five liver target-panel analysis is complete. It supports detectability without corrected disease-specific enrichment. Reusing the discovery PBC GWAS across molecular-QTL resources does not establish independent disease replication. FinnGen person-level non-overlap remains unverified.

The complete local path/content inventory stays private. Its public summary reports size/count/format/review limits, without donor-level content. Old work records are version-specific and do not replace the current state. No Zenodo DOI or journal receipt is asserted by this rebuild.
''')
    put('README.md','''# PBC regulatory attribution reliability

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
''')
    save(AN/'PREPARATION_RECEIPT.json',{'old_head':head,'public_tree':str(PUB),'submission':str(PACK),'original_assets_unchanged':len(roles),'submission_zip':str(zpath),'zip_bytes':zpath.stat().st_size,'zip_sha256':sha(zpath),'zip_crc':'PASS','internal_checksums':len(files),'scientific_refit':False,'new_WPS_render':False,'repository_deleted':False,'repository_created':False})
    print(json.dumps({'public':str(PUB),'submission_zip':str(zpath),'sha256':sha(zpath),'checksums':len(files)},ensure_ascii=False))
if __name__=='__main__':main()
