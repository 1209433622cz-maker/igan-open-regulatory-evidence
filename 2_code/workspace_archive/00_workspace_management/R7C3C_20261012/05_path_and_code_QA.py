"""Check moved dependency paths and syntax without executing scientific models."""
from pathlib import Path
import csv,json,ast,os,subprocess,importlib.util
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT

def load(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def main():
    patches=load(OUT/'organization/PATH_ONLY_ADAPTERS.tsv')
    # Adapt old audit Git entry points too, but do not alter historical result tables.
    for name in ('06_audit_github_repository.py','10_prepare_public_sync.py','11_rebuild_repo_manifest.py','15_final_qa.py'):
        p=ROOT/'2_code/11_manuscript/R7C3_full_audit'/name
        b=p.read_bytes();s=b.decode('utf-8-sig');n=s.replace('ROOT / "github" / "igan-open-regulatory-evidence"','ROOT / "0_admin" / "repositories" / "igan-open-regulatory-evidence"').replace('YR1\\github\\igan-open-regulatory-evidence','YR1\\0_admin\\repositories\\igan-open-regulatory-evidence')
        if n!=s:
            rel=p.relative_to(ROOT).as_posix();bp=ROOT/'9.Version/workspace_reorganization/R7C3C_20261012/original_path_dependent_code'/rel
            bp.parent.mkdir(parents=True,exist_ok=True);bp.write_bytes(b);ast.parse(n);p.write_text(n,encoding='utf-8',newline='')
            patches.append({'path':rel,'backup':bp.relative_to(ROOT).as_posix(),'sha256_before':a.hashlib.sha256(b).hexdigest(),'sha256_after':a.digest(p),'change':'PATH_ONLY; historical output contract unchanged'})
    a.tsv(OUT/'organization/PATH_ONLY_ADAPTERS.tsv',patches)
    st=json.loads((OUT/'organization/STATE.json').read_text(encoding='utf-8'));st['path_only_adapters']=len(patches);a.save_json(OUT/'organization/STATE.json',st)
    results=[]
    for row in patches:
        p=ROOT/row['path'];r={'path':row['path'],'language':p.suffix,'status':'','detail':''}
        try:
            if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'));r['status']='PASS_AST_NO_EXECUTION'
            else:r['status']='AWAIT_NATIVE_PARSER'
        except Exception as e:r.update(status='FAIL',detail=type(e).__name__+':'+str(e))
        results.append(r)
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8-sig'));results.append({'path':p.relative_to(ROOT).as_posix(),'language':'.py','status':'PASS_AST_NO_EXECUTION','detail':''})
    a.tsv(OUT/'paths/PYTHON_AND_ADAPTER_SYNTAX.tsv',results)
    refs=load(OUT/'before/REPARSE_POINTS.tsv');linkrows=[]
    for r in refs:
        p=Path(r['path']);target=Path(os.path.realpath(a.extended(p)).removeprefix('\\\\?\\'))
        linkrows.append({'path':p.relative_to(ROOT).as_posix(),'resolved_target':str(target),'target_exists':target.exists(),'scope':'IN_WORKSPACE_ALREADY_COUNTED_PHYSICAL_DEPENDENCY' if target.is_relative_to(ROOT) else 'EXTERNAL_BUNDLED_NODE_RUNTIME_OUTSIDE_WORKSPACE'})
    a.tsv(OUT/'paths/REPARSE_TARGET_IDENTITIES_LOCAL.tsv',linkrows)
    paths=json.loads((ROOT/'0_admin/workspace_paths.json').read_text(encoding='utf-8'))
    checked=[{'key':k,'path':v,'exists':Path(v).exists()} for k,v in paths.items() if isinstance(v,str) and v.startswith('H:\\') and k not in ('workspace_root',)]
    a.tsv(OUT/'paths/ACTIVE_ENTRYPOINTS.tsv',checked)
    if any(not r['exists'] for r in checked) or any(r['status']=='FAIL' for r in results):raise SystemExit('Active path or Python syntax check failed')
    print(json.dumps({'path_adapters':len(patches),'python_syntax_pass':sum(r['status']=='PASS_AST_NO_EXECUTION' for r in results),'native_parsers_pending':sum(r['status']=='AWAIT_NATIVE_PARSER' for r in results),'active_paths':len(checked),'reparse_targets':len(linkrows)},ensure_ascii=False))

if __name__=='__main__':main()
