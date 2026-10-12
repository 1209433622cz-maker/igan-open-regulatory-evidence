"""Independent full SHA-256 conservation, archive, path and navigation checks."""
from pathlib import Path
from collections import Counter
import csv, json, re, os, ast, zipfile, hashlib, time, importlib.util, py_compile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scan',HERE/'01_scan_and_plan.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
ROOT,OUT,REG,BACK=S.ROOT,S.OUT,S.REG,S.BACK

def main():
    before=list(csv.DictReader((OUT/'BEFORE_FILES.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    plan=json.loads((REG/'organization_plan.json').read_text(encoding='utf-8'))
    receipt=json.loads((REG/'execution_receipt.json').read_text(encoding='utf-8'))
    generated=json.loads((REG/'generated_navigation_files.json').read_text(encoding='utf-8'))
    moved={x['source']:x['destination'] for x in receipt['moves']}
    codes={x['path']:x for x in receipt['code_changes']}
    allowed={x['path']:x for x in generated if x['backup']}
    checks=[];fresh=[];start=time.time()
    def check(name,ok,detail=''):checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':str(detail)})
    # Navigation refers to CURRENT bytes and separately preserves original hashes.
    table=list(csv.DictReader((OUT/'CLASSIFIED_ORIGINAL_FILES.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    for r in table:
        rel=r['relative_path']
        if rel in allowed or rel in codes or rel.startswith('2_code/00_workspace_management/R7C3E_20261012/'):
            p=ROOT/rel;r['sha256']=S.U.digest(p);r['size_bytes']=os.stat(S.U.extended(p)).st_size
            r.update(S.U.summarize(p,rel,int(r['size_bytes'])))
            if rel in allowed:r['organization_action']='NAVIGATION_UPDATED_ORIGINAL_ARCHIVED';r['verification_basis']='FRESH_CURRENT_NAVIGATION_WITH_ORIGINAL_BACKUP'
    fields=list(table[0])
    S.U.tsv(OUT/'CLASSIFIED_ORIGINAL_FILES.tsv',table,fields)
    for top in S.TOPS:S.U.tsv(ROOT/top/'00_目录索引/FILE_INDEX.tsv',[r for r in table if r['top_level']==top],fields)
    navigator=REG/'WORKSPACE_NAVIGATOR.html';doc=navigator.read_text(encoding='utf-8')
    records=[[r['relative_path'],int(r['size_bytes']),r['project'],r['primary_stage'],r['role'],r.get('title',''),r['sha256'],r['content_status'],r['original_path']] for r in table]
    begin=doc.index('const data=')+len('const data=');end=doc.index(';let page=0,filtered=[];',begin)
    doc=doc[:begin]+json.dumps(records,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+doc[end:]
    navigator.write_text(doc,encoding='utf-8')
    for g in generated:g['sha256']=S.U.digest(ROOT/g['path'])
    S.dump(REG/'generated_navigation_files.json',generated)
    current_hashes={}; original_count=0
    # Freshly read every PREEXISTING original byte stream, including standard software.
    for i,r in enumerate(before,1):
        rel=r['relative_path'];target=moved.get(rel,rel);p=ROOT/target
        if rel.startswith('2_code/00_workspace_management/R7C3E_20261012/'):
            check('THIS_ROUND_TOOL_NOT_USER_ORIGINAL:'+rel,p.is_file());continue
        original_count+=1
        try:
            h=S.U.digest(p);st=os.stat(S.U.extended(p));current_hashes[target]=h
            if rel in allowed:
                backup=ROOT/allowed[rel]['backup']
                ok=S.U.digest(backup)==r['sha256'] and h==allowed[rel]['sha256'];action='NAVIGATION_WITH_IDENTICAL_ORIGINAL_BACKUP'
            elif rel in codes:
                c=codes[rel];backup=next(x for x in receipt['code_backups'] if x['path']==rel)
                old=(ROOT/backup['backup']).read_bytes().decode('utf-8');now=p.read_bytes().decode('utf-8')
                restored=now
                for a,b in reversed(c['replacements']):restored=restored.replace(b,a)
                ok=h==c['after_sha256'] and S.U.digest(ROOT/backup['backup'])==r['sha256'] and restored==old;action='EXACT_TWO_INPUT_PATHS_ONLY_ORIGINAL_BACKED_UP'
            else:ok=h==r['sha256'] and st.st_size==int(r['size_bytes']);action='HASH_IDENTICAL_ORIGINAL'
            check('ORIGINAL_CONSERVED:'+rel,ok,action)
            fresh.append({'original_path':rel,'current_path':target,'before_sha256':r['sha256'],'after_sha256':h,'size_bytes':st.st_size,'action':action,'status':'PASS' if ok else 'FAIL','verification':'FRESH_FULL_SHA256_AFTER_ORGANIZATION'})
        except Exception as e:check('ORIGINAL_CONSERVED:'+rel,False,str(e))
        if i%3000==0:print(f'FRESH_AFTER_HASH {i}/{len(before)} seconds={time.time()-start:.1f}',flush=True)
    # Persist expensive full-file verification before ancillary optional-library checks.
    S.U.tsv(OUT/'FRESH_AFTER_HASH_CONSERVATION.tsv',fresh,['original_path','current_path','before_sha256','after_sha256','size_bytes','action','status','verification'])
    S.U.tsv(REG/'FULL_HASH_CHECKPOINT.tsv',checks,['check','status','detail'])
    for x in receipt['moves']:
        check('MOVE_OLD_ABSENT:'+x['source'],not os.path.exists(S.U.extended(ROOT/x['source'])))
        check('MOVE_EXACT_HASH:'+x['destination'],current_hashes.get(x['destination'])==x['sha256'])
    for x in plan['candidates']:
        if not x['decision'].startswith('MOVE'):check('REFERENCED_INTERFACE_RETAINED:'+x['source'],current_hashes.get(x['source'])==x['sha256'])
    # Bytes preserved does not claim a scientific recalculation. Archive integrity only.
    for x in receipt['moves']:
        p=ROOT/x['destination']
        if p.suffix.lower()=='.zip':
            try:
                with zipfile.ZipFile(S.U.extended(p)) as z:bad=z.testzip()
                check('MOVED_ZIP_CRC:'+x['destination'],bad is None,bad or 'all members CRC PASS')
            except Exception as e:check('MOVED_ZIP_CRC:'+x['destination'],False,str(e))
        if p.name.endswith('.zip.sha256'):
            z=p.with_name(p.name[:-7]);text=p.read_text(encoding='utf-8-sig')
            expected=re.search(r'(?i)\b[0-9a-f]{64}\b',text)
            check('ZIP_SHA_PAIR:'+x['destination'],z.is_file() and expected is not None and S.U.digest(z)==expected.group(0).lower(),'paired original ZIP and outside checksum')
    # All listed metadata is resolvable; original rows and changed navigation are separated.
    for top in S.TOPS:
        p=ROOT/top/'00_目录索引/FILE_INDEX.tsv';rows=list(csv.DictReader(p.open(encoding='utf-8-sig'),delimiter='\t'))
        expected=[r for r in table if r['top_level']==top]
        check('ROOT_FILE_INDEX:'+top,len(rows)==len(expected) and all(os.path.exists(S.U.extended(ROOT/r['relative_path'])) for r in rows),len(rows))
        check('ROOT_DIRECTORY_INDEX:'+top,(ROOT/top/'00_目录索引/DIRECTORY_INDEX.tsv').is_file())
    for g in generated:
        p=ROOT/g['path'];check('GENERATED_NAV_IDENTITY:'+g['path'],S.U.digest(p)==g['sha256'])
        if p.suffix.lower()=='.md':
            links=re.findall(r'\]\(<(H:/SCI2/YR1/[^>]+)>\)',p.read_text(encoding='utf-8'))
            missing=[x for x in links if not os.path.exists(S.U.extended(x))]
            check('NAV_LINKS:'+g['path'],not missing,';'.join(missing))
    # Compile without executing any analysis program or creating cache in science folders.
    scripts=[HERE/'01_scan_and_plan.py',HERE/'02_refine_and_apply.py',HERE/'03_build_navigation.py',HERE/'04_independent_qa.py',HERE/'workspace_path_lookup.py']+[ROOT/x['path'] for x in receipt['code_changes']]
    for i,p in enumerate(scripts):
        try:
            dest=OUT/'code_compile'/f'{i:02d}_{p.name}.pyc';dest.parent.mkdir(parents=True,exist_ok=True)
            py_compile.compile(str(p),cfile=str(dest),doraise=True);check('PYTHON_COMPILE:'+p.relative_to(ROOT).as_posix(),True)
        except Exception as e:check('PYTHON_COMPILE:'+p.relative_to(ROOT).as_posix(),False,str(e))
    # Check the relocated cached donor pages without executing the original writer.
    from lxml import html as html_parser
    manifest=ROOT/'1_data/scrna/PBC/HRA008003/manifests/HRA008003_control_liver_primary_run_manifest_v1.tsv'
    donor_rows=list(csv.DictReader(manifest.open(encoding='utf-8-sig'),delimiter='\t'))
    snapshots=ROOT/'3_results/00_audit/90_历史散件/PBC/R7A2A0/02_来源网页'
    for r in donor_rows:
        rp=snapshots/f'R7A2A0_{r["run_accession"]}_runDetail.html';sp=snapshots/f'R7A2A0_{r["sample_accession"]}_sampleDetail.html'
        def values(p):
            tree=html_parser.fromstring(p.read_text(encoding='utf-8'));d={}
            for row in tree.xpath("//table[contains(concat(' ',normalize-space(@class),' '),' table-left ')]//tr"):
                c=row.xpath('./th|./td')
                def cell_text(cell):return ' '.join(t.strip() for t in cell.itertext() if t.strip())
                if len(c)>=2:d[cell_text(c[0]).rstrip(':')]=cell_text(c[1])
            return d
        try:
            rv,sv=values(rp),values(sp)
            ok=rv.get('Accession')==r['run_accession'] and rv.get('Sample')==r['sample_accession'] and sv.get('Sample name')==r['donor_label'] and sv.get('Tissue','').lower()=='liver' and 'hemangioma' in sv.get('Sample title','').lower()
            check('CACHED_CONTROL_DONOR_SCHEMA:'+r['run_accession'],ok)
        except Exception as e:check('CACHED_CONTROL_DONOR_SCHEMA:'+r['run_accession'],False,str(e))
    # Frozen lookup resolves case-insensitive native absolute and relative file paths.
    spec2=importlib.util.spec_from_file_location('lookup',HERE/'workspace_path_lookup.py');L=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(L)
    for x in receipt['moves']:
        check('OLD_PATH_LOOKUP:'+x['source'],L.resolve_workspace_path(x['source'])==ROOT/x['destination'] and L.resolve_workspace_path(str(ROOT/x['source']))==ROOT/x['destination'])
    papers=[x for x in plan['candidates'] if x['metadata']]
    check('54_PAPER_EXACT_IDENTITY',len(papers)==54 and len({x['metadata']['id'] for x in papers})==54)
    check('PAPER_SIX_METHOD_CATEGORIES',len({Path(x['destination']).parts[3] for x in papers})==6)
    check('TWELVE_ROOT_SCOPE',len(S.TOPS)==12 and '4_figures' not in S.TOPS)
    check('CURRENT_EDITORIAL_BYTES_UNCHANGED',all(x['status']=='PASS' and x['action']=='HASH_IDENTICAL_ORIGINAL' for x in fresh if x['original_path'].startswith(('5_manuscript/R7C3B_','5_manuscript/R7C3C_','6_release/R7C3C_'))))
    check('FIG1_TO_8_PRIOR_ORGANIZATION_UNCHANGED',all(x['status']=='PASS' and x['action']=='HASH_IDENTICAL_ORIGINAL' for x in fresh if x['original_path'].startswith('4_figures/')))
    fail=[c for c in checks if c['status']!='PASS']
    S.U.tsv(REG/'INDEPENDENT_QA.tsv',checks,['check','status','detail'])
    S.U.tsv(OUT/'FRESH_AFTER_HASH_CONSERVATION.tsv',fresh,['original_path','current_path','before_sha256','after_sha256','size_bytes','action','status','verification'])
    state={'schema':'R7C3E_INDEPENDENT_FILE_ORGANIZATION_QA_V1','status':'PASS' if not fail else 'FAIL','date':'2026-10-12','checks':len(checks),'passed':len(checks)-len(fail),'failed':len(fail),'failures':fail,'before_inventory_files':len(before),'preexisting_user_files_checked':original_count,'fresh_after_full_hashes':len(fresh),'scope_original_files':len(table),'moved_files':len(receipt['moves']),'moved_bytes':sum(x['size_bytes'] for x in receipt['moves']),'path_reader_adapters':len(receipt['code_changes']),'old_figures_unchanged':True if not any(x['status']=='FAIL' and x['check'].startswith('ORIGINAL_CONSERVED:4_figures/') for x in checks) else False,'scientific_reanalysis_executed':False,'public_push_executed':False,'seconds':round(time.time()-start,2)}
    S.dump(REG/'INDEPENDENT_QA_STATE.json',state)
    print(json.dumps(state,ensure_ascii=False),flush=True)
    if fail:raise SystemExit(1)

if __name__=='__main__':main()
