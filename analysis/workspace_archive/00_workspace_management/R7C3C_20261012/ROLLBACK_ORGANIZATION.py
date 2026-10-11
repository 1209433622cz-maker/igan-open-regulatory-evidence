"""Explicitly invoked rollback. Does not delete audit records or new assets."""
from pathlib import Path
import csv,json,shutil,sys
ROOT=Path(r'H:\SCI2\YR1').resolve();OUT=ROOT/'5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/organization'
def safe(rel):
    p=(ROOT/rel).resolve()
    if not p.is_relative_to(ROOT) or p==ROOT:raise ValueError(rel)
    return p
def ext(p):return '\\\\?\\'+str(p)
if '--execute' not in sys.argv:raise SystemExit('Dry-run only. Inspect MOVE_JOURNAL.json and PATH_ONLY_ADAPTERS.tsv. Use --execute to restore original root layout and original runnable code.')
with (OUT/'PATH_ONLY_ADAPTERS.tsv').open(encoding='utf-8-sig',newline='') as f:
    for row in csv.DictReader(f,delimiter='\t'):shutil.copy2(ext(safe(row['backup'])),ext(safe(row['path'])))
for item in reversed(json.loads((OUT/'MOVE_JOURNAL.json').read_text(encoding='utf-8'))):
    src,dst=safe(item['destination']),safe(item['source'])
    if dst.exists():raise SystemExit('Collision; refusing rollback overwrite: '+str(dst))
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.move(ext(src),ext(dst))
for name in ('WORKSPACE_MAP.md','workspace_paths.json'):
    src=ROOT/'9.Version/workspace_reorganization/R7C3C_20261012/admin_navigation_before'/name
    shutil.copy2(src,ROOT/'0_admin'/name)
print('Original locations and path-dependent code restored. New audit outputs and navigation READMEs retained; inspect them before reuse.')
