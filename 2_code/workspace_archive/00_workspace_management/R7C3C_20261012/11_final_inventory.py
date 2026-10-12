"""Final metadata delta, separate from the earlier frozen audit ZIP."""
from pathlib import Path
import importlib.util,csv,json,os,stat
spec=importlib.util.spec_from_file_location('audit',Path(__file__).parent/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT

def main():
    with (OUT/'after/ALL_FILES.tsv').open(encoding='utf-8-sig',newline='') as f:cache={r['relative_path']:r for r in csv.DictReader(f,delimiter='\t')}
    rows=[];fresh=0;reused=0;errors=[]
    for current,ds,fs in os.walk(a.extended(ROOT)):
        # extended(ROOT) always begins with the four-character Windows long-path prefix.
        normal=Path(current[4:])
        if normal==OUT or OUT in normal.parents:ds[:]=[];continue
        ds[:]=[d for d in ds if not (os.lstat(Path(current)/d).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)]
        for n in fs:
            p=normal/n;rel=p.relative_to(ROOT).as_posix()
            try:
                s=os.stat(a.extended(p));old=cache.get(rel)
                if old and int(old['size_bytes'])==s.st_size and int(old['mtime_ns'])==s.st_mtime_ns:
                    r=dict(old);r['closing_hash_basis']='SAME_ROUND_FRESH_HASH_CACHE_MATCHED_SIZE_MTIME';reused+=1
                else:
                    cat,pub=a.classify(rel);r={'relative_path':rel,'top_level':rel.split('/')[0],'size_bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':a.digest(p),'hash_state':'FRESH_FULL_SHA256','category':cat,'publication_policy':pub,'extension':p.suffix.lower() or '[none]'};r.update(a.summarize(p,rel,s.st_size));r['closing_hash_basis']='FRESH_CLOSING_DELTA_SHA';fresh+=1
                rows.append(r)
            except Exception as e:errors.append({'path':rel,'error':type(e).__name__+':'+str(e)[:200]})
    rows.sort(key=lambda r:r['relative_path'].casefold());a.tsv(OUT/'final/ALL_FILES_FINAL_CLOSING.tsv',rows,sorted({k for r in rows for k in r}));a.tsv(OUT/'final/READ_ERRORS.tsv',errors,['path','error'])
    state={'stage':'R7C3C_FINAL_CLOSING','date':'2026-10-12','files':len(rows),'bytes':sum(int(r['size_bytes']) for r in rows),'GiB':sum(int(r['size_bytes']) for r in rows)/1024**3,'fresh_delta_hashes':fresh,'same_round_cached_hashes':reused,'errors':len(errors),'root_folders':sorted(p.name for p in ROOT.iterdir()),'self_excluded_audit_output':str(OUT),'after_public_sync_and_local_audit_release':True,'note':'Closing snapshot reuses hashes from this round full fresh after scan only when size and mtime agree. Later small final receipts are outside this snapshot; the central delta is separate from the already-frozen full audit ZIP.'}
    a.save_json(OUT/'final/STATE.json',state)
    if errors:raise SystemExit('Closing read errors')
    print(json.dumps(state,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
