"""Default is verification only. --apply performs guarded exact-file rollback.

No recursive deletion. Audit reports and original backups remain available.
If any moved file, generated navigation or adapted reader has changed, stop.
"""
from pathlib import Path
import argparse, csv, json, shutil, os, importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('apply_util',HERE/'02_refine_and_apply.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
S=A.S;ROOT,OUT,REG,BACK=A.ROOT,A.OUT,A.REG,A.BACK

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    receipt=json.loads((REG/'execution_receipt.json').read_text(encoding='utf-8'))
    generated=json.loads((REG/'generated_navigation_files.json').read_text(encoding='utf-8'))
    before={r['relative_path']:r for r in csv.DictReader((OUT/'BEFORE_FILES.tsv').open(encoding='utf-8-sig'),delimiter='\t')}
    errors=[]
    for x in receipt['moves']:
        src,dst=A.safe(x['source']),A.safe(x['destination'])
        if src.exists() or not dst.is_file() or S.U.digest(dst)!=x['sha256']:errors.append('Moved identity/conflict: '+x['destination'])
    for c in receipt['code_changes']:
        p=A.safe(c['path']);backup=next(x for x in receipt['code_backups'] if x['path']==c['path'])
        if not p.is_file() or S.U.digest(p)!=c['after_sha256'] or S.U.digest(A.safe(backup['backup']))!=c['before_sha256']:errors.append('Reader changed: '+c['path'])
    for x in generated:
        p=A.safe(x['path'])
        if not p.is_file() or S.U.digest(p)!=x['sha256']:errors.append('Navigation changed: '+x['path'])
        if x['backup']:
            backup=A.safe(x['backup'])
            if S.U.digest(backup)!=before[x['path']]['sha256']:errors.append('Original navigation backup changed: '+x['path'])
    state={'status':'PASS_DRY_RUN' if not errors else 'FAIL_CLOSED','moves':len(receipt['moves']),'navigation_entries':len(generated),'code_adapters':len(receipt['code_changes']),'errors':errors,'apply_requested':args.apply,'no_recursive_delete':True}
    S.dump(REG/'ROLLBACK_DRY_RUN.json',state);print(json.dumps(state,ensure_ascii=False),flush=True)
    if errors:raise SystemExit(1)
    if not args.apply:return
    if (REG/'rollback_applied.json').exists():raise SystemExit('Rollback already applied')
    completed=[]
    for x in reversed(receipt['moves']):
        src,dst=A.safe(x['source']),A.safe(x['destination']);src.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(S.U.extended(dst),S.U.extended(src))
        if S.U.digest(src)!=x['sha256']:raise ValueError('Rollback move identity')
        completed.append(x['source'])
        S.dump(REG/'rollback_partial.json',{'restored_originals':completed})
    for c in receipt['code_changes']:
        backup=next(x for x in receipt['code_backups'] if x['path']==c['path'])
        shutil.copy2(A.safe(backup['backup']),A.safe(c['path']))
    directories=set()
    for x in reversed(generated):
        p=A.safe(x['path'])
        if x['backup']:shutil.copy2(A.safe(x['backup']),p)
        else:
            # Only exact generated files with already-verified hashes are removed.
            os.unlink(S.U.extended(p));directories.update(q for q in p.parents if q!=ROOT and q.is_relative_to(ROOT))
    for x in receipt['moves']:
        p=ROOT/x['destination'];directories.update(q for q in p.parents if q!=ROOT and q.is_relative_to(ROOT))
    for d in sorted(directories,key=lambda p:len(p.parts),reverse=True):
        if len(d.relative_to(ROOT).parts)<2:continue
        try:
            if not any(os.scandir(S.U.extended(d))):os.rmdir(S.U.extended(A.safe(d.relative_to(ROOT))))
        except (FileNotFoundError,OSError):pass
    S.dump(REG/'rollback_applied.json',{'status':'ROLLED_BACK_ORIGINAL_BYTES_RESTORED','moves':completed,'audit_records_retained':True,'deleted_scientific_files':0})
    print('Rollback applied; original file identities restored. Audit retained.',flush=True)

if __name__=='__main__':main()
