"""Fail-closed rollback; default read-only, --apply restores previous figure layout.

New navigation and copied figures are archived, not deleted. All resolved paths
must remain within the workspace. Any changed file aborts the whole preflight.
"""
import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT=Path(r'H:\SCI2\YR1').resolve()
FIG=ROOT/'4_figures'
REG=ROOT/'0_admin/figure_registry/R7C3D_20261012'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(p):
    p=p.resolve()
    if not p.is_relative_to(ROOT):raise RuntimeError(f'Outside workspace: {p}')
    return p
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    rows=json.loads((REG/'classification_plan.json').read_text(encoding='utf-8'))
    codes=json.loads((REG/'code_path_changes.json').read_text(encoding='utf-8'))
    inventory=[]
    import csv
    with (REG/'AFTER_FIGURE_FILES.tsv').open(encoding='utf-8-sig',newline='') as f:inventory=list(csv.DictReader(f,delimiter='\t'))
    expected={r['relative'] for r in inventory}
    actual={p.relative_to(ROOT).as_posix() for p in FIG.rglob('*') if p.is_file()}
    if actual!=expected:raise RuntimeError('Figure inventory changed after organization; rollback requires review')
    for r in inventory:
        p=safe(ROOT/r['relative'])
        if digest(p)!=r['sha256']:raise RuntimeError(f'Figure/navigation changed: {p}')
    for r in rows:
        p=safe(ROOT/r['new_relative'])
        if digest(p)!=r['sha256']:raise RuntimeError(f'Archived or copied source changed: {p}')
    for r in codes:
        if digest(safe(ROOT/r['file']))!=r['new_sha256'] or digest(safe(ROOT/r['backup']))!=r['old_sha256']:
            raise RuntimeError(f'Code changed after adapter: {r["file"]}')
    print(json.dumps({'preflight':'PASS','original_files_to_restore':50,'code_files_to_restore':len(codes),'apply':args.apply}))
    if not args.apply:return
    archive=safe(ROOT/'9.Version/figure_reorganization/R7C3D_20261012'/('rollback_navigation_'+datetime.now().strftime('%Y%m%d_%H%M%S')))
    originals=[r for r in rows if r['kind'].startswith('ORIGINAL_')]
    original_dest={r['new_relative'] for r in originals}
    # Move newly created catalogue/navigation/copies out of the way first.
    for r in inventory:
        if r['relative'] in original_dest:continue
        p=safe(ROOT/r['relative']);dst=safe(archive/p.relative_to(FIG))
        if dst.exists():raise RuntimeError('Rollback archive collision')
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),str(dst))
    for r in originals:
        src=safe(ROOT/r['new_relative']);dst=safe(ROOT/r['old_relative'])
        if dst.exists():raise RuntimeError(f'Original destination unexpectedly occupied: {dst}')
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(src),str(dst))
    for r in codes:shutil.copy2(safe(ROOT/r['backup']),safe(ROOT/r['file']))
    for p in sorted(FIG.rglob('*'),key=lambda p:len(p.parts),reverse=True):
        if p.is_dir() and not any(p.iterdir()) and p.name not in {f'Fig{i}' for i in range(1,9)}:safe(p).rmdir()
    (FIG/'Supplementary').mkdir(exist_ok=True)
    for r in originals:
        if digest(ROOT/r['old_relative'])!=r['sha256']:raise RuntimeError('Restored identity failure')
    (REG/'rollback_state.json').write_text(json.dumps({'status':'RESTORED','archive':str(archive)},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Original layout and code restored; generated navigation/copies archived.')

if __name__=='__main__':main()
