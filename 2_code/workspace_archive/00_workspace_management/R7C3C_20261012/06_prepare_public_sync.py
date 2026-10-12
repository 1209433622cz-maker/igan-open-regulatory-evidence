"""Prepare selected public assets; never git-add the entire local workspace."""
from pathlib import Path
import csv,json,shutil,subprocess,hashlib,re,zipfile,importlib.util
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT;REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence'
BASE=ROOT/'5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011'
PACK=ROOT/'5_manuscript/R7C3C_SubmissionCandidate_20261012'
REPORT=ROOT/'7.Report/rounds/R7C3C_20261012'

def git(*args):return subprocess.check_output(['git',*args],cwd=REPO).decode('utf-8').strip()
def load(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def text(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.rstrip()+'\n',encoding='utf-8')

def main():
    if git('status','--porcelain'):raise SystemExit('Repository has pre-existing changes; inspect before preparing public payload')
    beforehead=git('rev-parse','HEAD');pub=[]
    def copy(sp,rel,why):
        dp=REPO/rel;dp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(sp,dp)
        pub.append({'path':rel,'sha256':a.digest(dp),'bytes':dp.stat().st_size,'role':why})
    # Full inventories, direct donor records and runtime files stay local; public pointers are metadata-only.
    for rel in ['before/STATE.json','before/TOP_LEVEL_TOTALS.tsv','after/STATE.json','after/TOP_LEVEL_TOTALS.tsv','integrity/STATE.json','catalogue/VALUABLE_ASSETS.tsv','catalogue/PROJECT_TIMELINE.tsv','catalogue/STATE.json','organization/STATE.json','submission/IDENTITY_STATE.json','submission/OFFICIAL_GUIDELINES_20261012.json']:
        copy(OUT/rel,'audit/r7c3c/'+rel,'AGGREGATE_AUDIT_OR_CURATED_METADATA')
    copy(OUT/'catalogue/LARGE_ASSET_POINTERS_PUBLIC.tsv','data/R7C3C_LARGE_ASSET_POINTERS.tsv','METADATA_ONLY_NO_RAW_BYTES')
    # Selected stage records contain aggregate scientific evidence and governance, not donor identifiers.
    records=load(OUT/'catalogue/PROJECT_WORK_RECORDS.tsv')
    selected=[{'path':r['path'],'title':r['title'],'sha256':r['sha256'],'bytes':r['bytes'],'stage_tokens':r['stage_tokens'],'use':'Historical record; consult stage-specific definitions'} for r in records if r['path'].startswith('7.Report/')]
    a.tsv(REPO/'audit/r7c3c/PROJECT_RECORD_POINTERS.tsv',selected,['path','title','sha256','bytes','stage_tokens','use'])
    for sp in HERE.glob('*'):
        if sp.is_file() and sp.suffix in ('.py','.R'):copy(sp,'analysis/r7c3c/'+sp.name,'WORKSPACE_AUDIT_ORIGINAL_CODE')
    for sp in (ROOT/'2_code/11_manuscript/R7C3B_qiteng_finish').glob('*'):
        if sp.is_file() and sp.suffix in ('.py','.ps1'):copy(sp,'analysis/r7c3b/'+sp.name,'LATEST_DOCUMENT_BUILD_AND_QA_CODE')
    for sp in PACK.rglob('*'):
        if sp.is_file():copy(sp,'manuscript/r7c3c/'+sp.relative_to(PACK).as_posix(),'LATEST_WPS_CANDIDATE_ASSET_WITH_EXPLICIT_UPLOAD_ROLE')
    # The inline reviewer copy is separate from the unique main-upload choice.
    for name in ('R7C3B_AuthorReview_InlineFigures.docx','R7C3B_AuthorReview_InlineFigures.pdf'):
        copy(BASE/'01_Manuscript'/name,'manuscript/r7c3b_review/'+name,'REVIEW_ONLY_NOT_MAIN_UPLOAD')
    for sp in REPORT.glob('*.md'):copy(sp,'reports/r7c3c/'+sp.name,'CURATED_WORK_RECORD')
    # Only update an older public runnable script if its bytes exactly match the archived local original.
    # Never overwrite a different scientific implementation merely because its basename matches.
    tracked=git('ls-files','-z').split('\0');candidates={}
    for rel in tracked:
        if rel.startswith('analysis/') and Path(rel).suffix.lower() in ('.py','.r','.ps1'):
            candidates.setdefault(Path(rel).name,[]).append(rel)
    adapted=[]
    for row in load(OUT/'organization/PATH_ONLY_ADAPTERS.tsv'):
        matches=[p for p in candidates.get(Path(row['path']).name,[]) if a.digest(REPO/p)==row['sha256_before']]
        for rel in matches:
            copy(ROOT/row['path'],rel,'PATH_ONLY_RUNTIME_ADAPTER_IDENTICAL_ORIGINAL');adapted.append(rel)
    a.tsv(OUT/'github/PUBLIC_PAYLOAD_IDENTITIES.tsv',pub)
    a.save_json(OUT/'github/PREPARATION_STATE.json',{'starting_head':beforehead,'selected_files':len(pub),'path_only_public_adapters':len(adapted),'raw_data_mirrored':False,'full_local_inventory_published':False,'publication_limit_bytes':10*1024**2,'author_version_approval':'PENDING','journal_submission':False})
    prefix='''## Current release — 12 October 2026

**PBC remains the primary project. The latest editorial candidate is the QiTeng/WPS R7C3B manuscript, packaged as R7C3C.** The scientific baseline is unchanged; this release adds a complete local byte audit, reversible root organization, a reusable asset/work-record catalogue, corrected runtime paths and a hash-frozen submission candidate.

- [Unique main manuscript and upload roles](manuscript/r7c3c/README_SUBMISSION.md); [DOCX](manuscript/r7c3c/01_Main/Manuscript.docx); [WPS parity PDF](manuscript/r7c3c/01_Main/Manuscript_WPS_Review.pdf).
- [Candidate identity manifest](manuscript/r7c3c/UPLOAD_ROLES_AND_IDENTITIES.tsv), six separate vector figures, SI, S1–S10 workbook, and the two Source Data archives are in `manuscript/r7c3c/`. Do not upload the separate reviewer copy as another main manuscript.
- [Curated valuable assets](audit/r7c3c/catalogue/VALUABLE_ASSETS.tsv), [project timeline](audit/r7c3c/catalogue/PROJECT_TIMELINE.tsv), [historical record pointers](audit/r7c3c/PROJECT_RECORD_POINTERS.tsv), and [large-file identities](data/R7C3C_LARGE_ASSET_POINTERS.tsv).
- [Local audit summary](audit/r7c3c/before/STATE.json): all 34,769 physical files rehashed, 42.48 GiB, zero read errors; directory junction targets recorded separately. Post-organization snapshot is separately labelled. Raw/individual-level inputs and the complete private path/content inventory are not mirrored.
- [Action record](reports/r7c3c/99_CMM_R7C3C_详细行动记录_20261012.md) and [work directory roles](reports/r7c3c/01_全量文件核查与分类报告.md).

**This is an openly shared submission candidate, not a journal submission, accepted article, independent disease-replication claim, or minted Zenodo DOI.** Names/declarations were previously confirmed; approval of the R7C3B edited asset identities, actual publisher reporting forms, final figure-width proof and the publisher merged PDF remain pending. The next task is author-operated npj Genomic Medicine submission preparation and receipt capture; no new biological discovery screen is requested.

Original software: MIT. Original author text, figures, documentation and aggregate derived tables: CC BY 4.0. Third-party data and publications retain provider restrictions; see `NOTICE.md` and `DATA_AVAILABILITY.md`. New manuscript assets inherit the same scope and do not relicense their input sources. Scientific source tags remain unchanged; the new editorial/audit tag is separate.

The sections below retain the chronological project history. Old entries labelled “next” describe their own historical stage, not the current project state.

---

'''
    rd=REPO/'README.md';old=rd.read_text(encoding='utf-8-sig')
    if '## Current release — 12 October 2026' not in old:text(rd,old.split('\n',1)[0]+'\n\n'+prefix+old.split('\n',1)[1].lstrip())
    text(REPO/'analysis/r7c3c/README.md','''# Local workspace audit and reversible organization

Runtime paths: `0_admin/tooling`, `0_admin/skills/qiteng_runtime_v03242`, `0_admin/repositories/igan-open-regulatory-evidence`. Exact old-path scripts remain in local `9.Version/workspace_reorganization/R7C3C_20261012/original_path_dependent_code` and old release tags. No statistical threshold or formula was changed by runtime adapters.

`01_full_audit.py --label <new_snapshot>` inventories and freshly hashes regular workspace files, preserving explicit semantic scan depth. Do not infer biological validity from hashes or status words in archived records. `03_organize_workspace.py` is a one-time migration; its preflight refuses absent sources or occupied targets. `ROLLBACK_ORGANIZATION.py` defaults to dry-run and requires `--execute` for restoration. Other builders retain frozen stage output locations; rerun only in a separate workspace or deliberately selected new version.

The public data manifest contains pointers; retrieve raw inputs from original providers. No genotype, donor pseudobulk, raw LD or complete local content inventory is distributed by these scripts. No email, journal submission or Zenodo publication is executed.
''')
    # Keep metadata honest: no DOI identifier added to either citation format.
    cf=REPO/'CITATION.cff';s=cf.read_text(encoding='utf-8-sig').replace('version 1.3.0','version 1.4.0').replace('version: 1.3.0','version: 1.4.0').replace('date-released: 2026-10-11','date-released: 2026-10-12');text(cf,s)
    zp=REPO/'.zenodo.json';z=json.loads(zp.read_text(encoding='utf-8-sig'));z['version']='1.4.0';z['publication_date']='2026-10-12';z['description']+=' R7C3C retains the unchanged R7C3B QiTeng/WPS editorial candidate and adds byte-audited asset catalogues; edited-version author approval and publisher proof are pending. This file is publication metadata, not proof that a Zenodo deposit exists.';a.save_json(zp,z)
    print(json.dumps({'public_payload_files':len(pub),'path_only_public_adapters':len(adapted),'start_head':beforehead},ensure_ascii=False))

if __name__=='__main__':main()
