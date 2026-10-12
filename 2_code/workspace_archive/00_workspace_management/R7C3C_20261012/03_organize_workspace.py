"""Reversible root consolidation, byte-preserving moves and path-only adapters."""
from pathlib import Path
import csv,json,shutil,os,re,ast,hashlib,importlib.util
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT
BACK=ROOT/'9.Version/workspace_reorganization/R7C3C_20261012/original_path_dependent_code'
CANON=['0_admin','1_data','2_code','3_results','4_figures','4_output','5_analysis','5_manuscript','6_release','7.Report','8.Reference','9.Version','9_Vote']

def inside(rel):
    p=(ROOT/rel).resolve()
    if not p.is_relative_to(ROOT.resolve()) or p==ROOT.resolve():raise ValueError('Outside workspace: '+str(p))
    return p

def planned():
    pairs=[('.qiteng_v03242_runtime','0_admin/skills/qiteng_runtime_v03242'),('tools','0_admin/tooling'),('github','0_admin/repositories'),('R5A2A2_OneK1K_archive_audit','3_results/00_audit/R5A2A2_archive_member_audit'),('finngen_R13_CHIRBIL_PRIM.gz.tbi','1_data/gwas/PBC/FinnGen_R13/indices/finngen_R13_CHIRBIL_PRIM.gz.tbi'),('YR1.zip','9.Version/workspace_snapshots/received_undated/YR1.zip'),('README_WORKSPACE.md','0_admin/navigation/archive/README_WORKSPACE_legacy_R7A2A1.md'),('PBC_FCRL3_IL12RB2_来源匹配多信号共定位_回溯性博士研究计划书_20261001.docx','9.Version/research_plans/archived_R7A_20261001/PBC_FCRL3_IL12RB2_来源匹配多信号共定位_回溯性博士研究计划书_20261001.docx'),('YGRE_本对话完整项目总结_截至2026-09-30.md','7.Report/project_history/YGRE_本对话完整项目总结_截至2026-09-30.md'),('YR1_CMM_SSc_对话全量总结_截至2026-09-13.md','7.Report/project_history/YR1_CMM_SSc_对话全量总结_截至2026-09-13.md')]
    for p in ROOT.glob('99_CMM_*.md'):
        s=re.search(r'(R\d+[A-Z][A-Z0-9]*)_',p.name)
        stage=s.group(1) if s else 'unassigned'
        pairs.append((p.name,'7.Report/rounds/'+stage+'/root_records/'+p.name))
    return pairs

def main():
    with (OUT/'before/ALL_FILES.tsv').open(encoding='utf-8-sig',newline='') as f:before=list(csv.DictReader(f,delimiter='\t'))
    pairs=planned();plan=[]
    for src,dst in pairs:
        sp,dp=inside(src),inside(dst)
        if not os.path.exists(a.extended(sp)):raise RuntimeError('Missing source '+src)
        if os.path.exists(a.extended(dp)):raise RuntimeError('Destination already exists '+dst)
        affected=[r for r in before if r['relative_path']==src or r['relative_path'].startswith(src+'/')]
        plan.append({'source':src,'destination':dst,'files':len(affected),'bytes':sum(int(r['size_bytes']) for r in affected),'operation':'MOVE_NO_REWRITE'})
    a.tsv(OUT/'organization/MOVE_PLAN.tsv',plan)
    journal=OUT/'organization/MOVE_JOURNAL.json';done=[]
    for item in plan:
        sp,dp=inside(item['source']),inside(item['destination']);dp.parent.mkdir(parents=True,exist_ok=True)
        # Both resolved targets checked, same volume rename; extended paths retain long filenames.
        shutil.move(a.extended(sp),a.extended(dp));done.append(item);a.save_json(journal,done)
        print('MOVED '+item['source']+' -> '+item['destination'],flush=True)
    identity=[]
    for r in before:
        dest=None
        for src,dst in pairs:
            if r['relative_path']==src or r['relative_path'].startswith(src+'/'):
                dest=dst+r['relative_path'][len(src):];break
        if dest is None:continue
        p=inside(dest);s=os.stat(a.extended(p));h=a.digest(p)
        identity.append({'old_path':r['relative_path'],'new_path':dest,'bytes_before':r['size_bytes'],'bytes_after':s.st_size,'sha256_before':r['sha256'],'sha256_after':h,'PASS':s.st_size==int(r['size_bytes']) and h==r['sha256']})
    a.tsv(OUT/'organization/MOVED_FILE_IDENTITIES.tsv',identity)
    if not all(r['PASS'] for r in identity):raise RuntimeError('Moved bytes differ')
    # Keep the original runtime/code bytes in release/version archives. Adapt only runnable local code.
    replacements=[('.qiteng_v03242_runtime','0_admin/skills/qiteng_runtime_v03242'),('github/igan-open-regulatory-evidence','0_admin/repositories/igan-open-regulatory-evidence'),('github\\igan-open-regulatory-evidence','0_admin\\repositories\\igan-open-regulatory-evidence'),('"github" / "igan-open-regulatory-evidence"','"0_admin" / "repositories" / "igan-open-regulatory-evidence"'),("'github' / 'igan-open-regulatory-evidence'","'0_admin' / 'repositories' / 'igan-open-regulatory-evidence'"),('/tools/','/0_admin/tooling/'),('\\tools\\','\\0_admin\\tooling\\'),("'tools\\","'0_admin\\tooling\\"),('"tools/','"0_admin/tooling/'),('"tools" /','"0_admin" / "tooling" /'),('"tools","R-library"','"0_admin","tooling","R-library"')]
    patched=[]
    targets=list((ROOT/'2_code').rglob('*'))+list((ROOT/'5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011/code').glob('*'))
    for p in targets:
        if not p.is_file() or p.suffix.lower() not in ('.py','.ps1','.r','.sh','.cmd','.bat'):continue
        rel=p.relative_to(ROOT).as_posix()
        if '/snapshots/' in rel or '/00_workspace_management/' in rel or '/R7C3_full_audit/' in rel:continue
        original=p.read_bytes()
        try:txt=original.decode('utf-8-sig')
        except UnicodeError:continue
        new=txt
        for x,y in replacements:new=new.replace(x,y)
        if new==txt:continue
        # Historical prose inside a code builder is backed up alongside its implementation.
        bp=BACK/rel;bp.parent.mkdir(parents=True,exist_ok=True);bp.write_bytes(original)
        # Preserve newline convention and BOM.
        raw=new.encode('utf-8');raw=(b'\xef\xbb\xbf'+raw) if original.startswith(b'\xef\xbb\xbf') else raw
        if p.suffix.lower()=='.py':ast.parse(new,filename=rel)
        p.write_bytes(raw)
        patched.append({'path':rel,'backup':bp.relative_to(ROOT).as_posix(),'sha256_before':hashlib.sha256(original).hexdigest(),'sha256_after':hashlib.sha256(raw).hexdigest(),'change':'PATH_ONLY; no thresholds, formulas or data changes'})
    a.tsv(OUT/'organization/PATH_ONLY_ADAPTERS.tsv',patched)
    # These two root administration maps are stale historical snapshots; retain byte originals before replacement.
    for name in ('WORKSPACE_MAP.md','workspace_paths.json'):
        p=ROOT/'0_admin'/name;bp=ROOT/'9.Version/workspace_reorganization/R7C3C_20261012/admin_navigation_before'/name
        bp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,bp)
    unexpected=[p.name for p in ROOT.iterdir() if p.name not in CANON]
    if unexpected:raise RuntimeError('Unexpected root entries '+str(unexpected))
    state={'root_folders':CANON,'move_operations':len(done),'moved_files':len(identity),'moved_bytes':sum(int(r['bytes_before']) for r in identity),'byte_identity_pass':sum(r['PASS'] for r in identity),'path_only_adapters':len(patched),'original_adapters_archived':True,'deleted_files':0,'unexpected_root_entries':unexpected}
    a.save_json(OUT/'organization/STATE.json',state);print(json.dumps(state,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
