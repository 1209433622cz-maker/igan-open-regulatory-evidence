"""Curate original scripts/work records, retaining frozen science and privacy boundaries."""
from pathlib import Path
import csv, json, hashlib, shutil, re, zipfile, importlib.util
ROOT=Path(r'H:\SCI2\YR1'); PUB=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
AN=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012'
PACK=ROOT/'5_manuscript/R7C3F_SubmissionCandidate_20261012';REL=ROOT/'6_release/R7C3F_20261012'
SECRET=re.compile(rb'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def tsv(p,rows,fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter='\t',fieldnames=fields or list(rows[0]),extrasaction='ignore');w.writeheader();w.writerows(rows)
def copy(p,rel):
    b=p.read_bytes();assert not SECRET.search(b),'Credential-like token: '+str(p)
    assert len(b)<=10*1024**2,'Large file gate: '+str(p)
    q=PUB/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);return q
def main():
    # Correct the count: the 21 content assets are unchanged; checksum manifest is regenerated.
    ident=list(csv.DictReader((PACK/'ASSET_IDENTITY_R7C3F.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    ident=[r for r in ident if r['path']!='checksums.sha256'];assert len(ident)==21
    tsv(PACK/'ASSET_IDENTITY_R7C3F.tsv',ident)
    p=PACK/'00_START_HERE.md';p.write_text(p.read_text(encoding='utf-8').replace('22 个原有资产','21 个原有内容资产（原包另含旧校验清单）'),encoding='utf-8')
    ps=[p for p in sorted(PACK.rglob('*')) if p.is_file() and p.name!='checksums.sha256']
    (PACK/'checksums.sha256').write_text(''.join(f'{sha(p)}  {p.relative_to(PACK).as_posix()}\n' for p in ps),encoding='utf-8')
    for p in PACK.rglob('*'):
        if p.is_file():copy(p,'manuscript/r7c3f/'+p.relative_to(PACK).as_posix())
    zpath=REL/'CMM_R7C3F_npj_Submission_Candidate_20261012.zip'
    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(PACK.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(PACK).as_posix())
    (REL/(zpath.name+'.sha256')).write_text(f'{sha(zpath)}  {zpath.name}\n',encoding='utf-8')
    # Update only public counterparts whose old content identity matches a proven path adapter.
    changes=[];mapping=json.loads((ROOT/'0_admin/figure_registry/R7C3D_20261012/code_path_changes.json').read_text(encoding='utf-8'))
    for item in mapping:
        src=ROOT/item['file'];old=(ROOT/item['backup']).read_bytes().replace(b'\r\n',b'\n')
        for q in list((PUB/'analysis').rglob(src.name)):
            if q.read_bytes().replace(b'\r\n',b'\n')==old:
                h=sha(q);copy(src,q.relative_to(PUB).as_posix());changes.append({'public_path':q.relative_to(PUB).as_posix(),'old_sha256':h,'current_sha256':sha(q),'change':'FIGURE_PATH_ADAPTER_ONLY','upstream_ast_identity':item['path_normalized_AST_unchanged']})
    source=ROOT/'2_code/06_intake/r7a2/04_build_R7A2A0_source_audit.py'
    candidates=list((PUB/'analysis/r7a2').glob(source.name))
    for q in candidates:
        oldsha=sha(q);copy(source,q.relative_to(PUB).as_posix());changes.append({'public_path':q.relative_to(PUB).as_posix(),'old_sha256':oldsha,'current_sha256':sha(q),'change':'SOURCE_HTML_PATH_ADAPTER_ONLY','upstream_ast_identity':'Recorded in R7C3E; two source paths only'})
    existing={sha(p):p.relative_to(PUB).as_posix() for p in sorted(PUB.rglob('*')) if p.is_file()}
    rows=list(csv.DictReader((AN/'ALL_FILES_FRESH_SHA256.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    exported=[];excluded=[]
    # Original local workflow code only; never vendor packages, pyc, skill or environment payloads.
    for r in rows:
        rel=r['relative_path'];parts=rel.lower().split('/');ext=r['extension']
        if r['top_level']=='2_code' and ext in ['.py','.ps1','.r','.sh','.cmd','.bat']:
            if any(x in parts for x in ['node_modules','__pycache__','envs','snapshots','00_目录索引']):excluded.append({'path':rel,'reason':'vendor/runtime or redundant historical code tree'});continue
            p=ROOT/rel
            if sha(p)!=r['sha256']:excluded.append({'path':rel,'reason':'changed after frozen enumeration; handled by current-stage code export'});continue
            dest=existing.get(r['sha256'])
            if not dest:dest='analysis/workspace_archive/'+rel.removeprefix('2_code/');q=copy(p,dest);existing[r['sha256']]=dest
            exported.append({'local_relative_path':rel,'public_path':dest,'bytes':r['size_bytes'],'sha256':r['sha256'],'role':'ORIGINAL_WORKFLOW_CODE','review':'Full-byte secret-signature and identity scan; scientific semantics retain stage audits'})
        if r['top_level']=='7.Report' and ext=='.md' and '/00_目录索引/' not in rel and not rel.endswith('README_DIRECTORY.md'):
            p=ROOT/rel;h=sha(p);assert h==r['sha256'];dest=existing.get(h)
            if not dest:dest='reports/workspace_records/'+rel.removeprefix('7.Report/');copy(p,dest);existing[h]=dest
            exported.append({'local_relative_path':rel,'public_path':dest,'bytes':r['size_bytes'],'sha256':h,'role':'WORK_RECORD','review':'Original author work record; historical state is version-specific; full-text token/identity scan'})
    # Current classification annotations and originals remain independent from submission figures.
    for p in sorted((ROOT/'4_figures').rglob('*')):
        if p.is_file():
            rel='figures/classified/'+p.relative_to(ROOT/'4_figures').as_posix();copy(p,rel)
    # Compatibility files are exact small figure/support bytes, never donor data.
    for p in sorted((ROOT/'0_admin/compatibility/figure_stage_view').rglob('*')):
        if p.is_file():copy(p,'workspace_support/figure_stage_view/'+p.relative_to(ROOT/'0_admin/compatibility/figure_stage_view').as_posix())
    for p in [ROOT/'9.Version/PBC_研究计划书_RP_v4_20261011.docx']:
        copy(p,'docs/research_plans/'+p.name)
    for p in [ROOT/'9.Version/stage_workspaces/YR1_R4A11_frozen_2026-09-12/01_54篇论文写作范式矩阵.csv',ROOT/'9.Version/stage_workspaces/YR1_R4A11_frozen_2026-09-12/00_综合大报告_54篇论文写作方法逻辑与新论文母版.md']:
        copy(p,'docs/writing_methods/'+p.name)
    # Copy local path resolver code, but not its private full-path registry.
    copy(ROOT/'2_code/00_workspace_management/R7C3E_20261012/workspace_path_lookup.py','analysis/r7c3f/workspace_path_lookup.py')
    tsv(PUB/'docs/WORK_RECORD_AND_CODE_INDEX.tsv',exported)
    tsv(AN/'PUBLIC_EXPORT_EXCLUSIONS_LOCAL.tsv',excluded,['path','reason'])
    tsv(PUB/'audit/r7c3f/PATH_ADAPTERS.tsv',changes)
    state=json.loads((AN/'STATE_BEFORE.json').read_text(encoding='utf-8'))
    public_state={k:v for k,v in state.items() if k not in ['read_errors','exclusions']}
    public_state['private_full_inventory']='Not redistributed; counts include local vendor runtimes, Git metadata, archives and inputs. Content-schema review of an identical freshly verified hash may reuse prior audit.'
    save(PUB/'audit/r7c3f/FULL_LOCAL_AUDIT_SUMMARY.json',public_state)
    shutil.copy2(AN/'TOP_LEVEL_TOTALS.tsv',PUB/'audit/r7c3f/TOP_LEVEL_TOTALS.tsv')
    large=[];seen=set()
    for r in rows:
        if r['top_level']=='1_data' and int(r['size_bytes'])>10*1024**2 and r['sha256'] not in seen:
            seen.add(r['sha256']);lo=r['relative_path'].lower()
            resource=next((x for x in ['onek1k','tenk10k','finngen','gwas','gse','omix','ega'] if x in lo),'source_or_derived_input')
            large.append({'asset_id':f'LOCAL_LARGE_{len(large)+1:04d}','resource_family':resource,'format':r['extension'],'bytes':r['size_bytes'],'sha256':r['sha256'],'publication':'METADATA_ONLY_NOT_MIRRORED','retrieval':'Provider accession/URL in LARGE_DATA_MANIFEST.tsv and stage source ledgers; derived inputs rebuilt with stage code','local_index':'Exact path and schema retained in private ALL_FILES_FRESH_SHA256.tsv'})
    tsv(PUB/'data/R7C3F_LARGE_INPUT_IDENTITIES.tsv',large)
    text='''# Work-record navigation and reuse policy

Current scientific/editorial conclusions are in README.md and docs/EVIDENCE_AND_REUSE.md. The stage records below are contemporaneous logs, not current promises. Historical “next” stages, old journal targets and superseded counts retain their original meaning.

`WORK_RECORD_AND_CODE_INDEX.tsv` maps original local work records and original executable workflow code to reviewed public assets by SHA-256. Identical content is indexed to an existing public copy rather than repeatedly uploaded. Full per-file private inventories, individual-level data, copyrighted papers, skills, vendor packages and redundant runtime caches stay local.

Use SSc/MG/IgAN archives for methods and failure boundaries; use R7B/R7C PBC records for the active manuscript. The 54-paper writing-method matrix and original synthesis are in docs/writing_methods/; article PDFs are not redistributed. RP v4 is in docs/research_plans/. Classified Fig1–8 and annotations are in figures/classified/; the unique submission Figure 1–6 remain in manuscript/r7c3f/02_Figures/.

Original code is retained with stage-specific assumptions and local ROOT paths. Path adapters are recorded in audit/r7c3f/PATH_ADAPTERS.tsv; compatibility view assets are provided under workspace_support/figure_stage_view/ for reconstruction at the expected local 0_admin path. Their presence does not claim all historical programs were rerun on a new machine.
'''
    (PUB/'docs/WORK_RECORD_GUIDE.md').write_text(text,encoding='utf-8')
    save(AN/'CURATION_RECEIPT.json',{'export_index_rows':len(exported),'work_record_aliases':sum(r['role']=='WORK_RECORD' for r in exported),'workflow_code_aliases':sum(r['role']=='ORIGINAL_WORKFLOW_CODE' for r in exported),'public_path_adapters':changes,'large_input_unique_identities':len(large),'submission_original_content_assets':21,'submission_zip_sha256':sha(zpath),'submission_zip_bytes':zpath.stat().st_size,'science_changed':False,'scope':'Private workspace intact; duplicate bytes retained; public snapshots and original records indexed.'})
    print(json.dumps({'indexed':len(exported),'large':len(large),'adapters':len(changes),'submission_sha256':sha(zpath)},ensure_ascii=False))
if __name__=='__main__':main()
