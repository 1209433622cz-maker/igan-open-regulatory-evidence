"""Fail-closed, reversible moves; exact scientific bytes are conserved."""
import argparse, ast, csv, hashlib, json, os, shutil
from pathlib import Path
from collections import defaultdict, Counter
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scan',HERE/'01_scan_and_plan.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
ROOT,OUT,REG,BACK=S.ROOT,S.OUT,S.REG,S.BACK

def safe(rel):
    p=(ROOT/rel).resolve()
    if not p.is_relative_to(ROOT.resolve()):raise ValueError(f'Outside workspace: {rel}')
    # No file operation through a junction or symbolic-link ancestor.
    import stat
    for q in [p]+list(p.parents):
        if q==ROOT:break
        if q.exists() and os.lstat(S.U.extended(q)).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError(f'Reparse path: {q}')
    return p

def refine():
    plan=json.loads((REG/'organization_plan.json').read_text(encoding='utf-8'))
    if plan['schema'].endswith('_V2'):return plan
    S.dump(REG/'organization_plan_initial_v1.json',plan)
    groups=defaultdict(list)
    for x in plan['candidates']:
        if x['source'].startswith(('6_release/','9.Version/releases/')):groups[str(Path(x['destination']).parent)].append(x)
        m=x['metadata']
        if m:
            a=m['archetype']
            if '单细胞' in a and ('MR' in a or '共定位' in a):cat='01_单细胞遗传归因_MR与共定位'
            elif 'MR' in a or '孟德尔' in a:cat='02_遗传因果推断与可成药靶点'
            elif any(s in a for s in ('环境暴露','网络毒理','网络药理','分子对接')):cat='03_暴露组_网络毒理与分子对接'
            elif any(s in a for s in ('生物信息','机器学习','生物标志')):cat='04_转录组与生物标志物'
            elif any(s in a for s in ('综述','Protocol','方案','操作','评论','协议','计量','评述')):cat='06_综述_操作规范与其他文体'
            else:cat='05_人群组学_遗传结构与实验机制'
            x['destination']=f"8.Reference/literature/54_papers/{cat}/{Path(x['source']).name}"
    for g in groups.values():
        if any(x['decision']!='MOVE' for x in g):
            deps=sorted({d for x in g for d in x['dependencies']})
            for x in g:
                x['decision']='RETAIN_CANONICAL_REFERENCED_BUNDLE'
                x['dependencies']=deps;x['reason']+='；同包 ZIP/sha256/receipt 不拆散'
    # Exact dynamic filename dependency discovered after the conservative scan.
    reader='2_code/06_intake/r7a2/04_build_R7A2A0_source_audit.py'
    replacements=[
        ('run_page = AUDIT / f"R7A2A0_{run}_runDetail.html"','run_page = AUDIT / "90_历史散件/PBC/R7A2A0/02_来源网页" / f"R7A2A0_{run}_runDetail.html"'),
        ('sample_page = AUDIT / f"R7A2A0_{sample}_sampleDetail.html"','sample_page = AUDIT / "90_历史散件/PBC/R7A2A0/02_来源网页" / f"R7A2A0_{sample}_sampleDetail.html"'),
    ]
    data=(ROOT/reader).read_bytes();text=data.decode('utf-8')
    adjusted=text
    for old,new in replacements:
        if text.count(old)!=1:raise ValueError('Reader path adapter not exact')
        adjusted=adjusted.replace(old,new)
    ast.parse(adjusted)
    # Reverting only the two path fragments must restore identical source bytes.
    reverted=adjusted
    for old,new in reversed(replacements):reverted=reverted.replace(new,old)
    if reverted!=text:raise ValueError('Non-path reader change')
    plan['code_changes']=[{'path':reader,'before_sha256':hashlib.sha256(data).hexdigest(),'after_sha256':hashlib.sha256(adjusted.encode('utf-8')).hexdigest(),'replacements':replacements,'scope':'TWO_INPUT_PATH_EXPRESSIONS_ONLY_OUTPUT_AND_ALGORITHM_UNCHANGED'}]
    for x in plan['candidates']:
        if x['source'].startswith('3_results/00_audit/R7A2A0_HR') and x['source'].endswith('.html') and ('runDetail' in x['source'] or 'sampleDetail' in x['source']):
            x['decision']='MOVE_WITH_EXACT_READER_ADAPTER';x['dependencies']=[reader]
            x['reason']+='；动态路径读取者已单独识别，仅适配输入路径'
    plan['schema']='R7C3E_NON_FIGURE_ORGANIZATION_V2'
    S.dump(REG/'organization_plan.json',plan)
    S.U.tsv(OUT/'FINAL_PLAN.tsv',[{**x,'dependencies':';'.join(x['dependencies']),'metadata':json.dumps(x['metadata'],ensure_ascii=False)} for x in plan['candidates']],['source','destination','decision','reason','size_bytes','sha256','dependencies','metadata'])
    return plan

def main():
    a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');args=a.parse_args()
    if (REG/'execution_receipt.json').exists():raise SystemExit('Moves already applied; refusing to execute twice.')
    plan=refine();moves=[x for x in plan['candidates'] if x['decision'].startswith('MOVE')]
    targets=set()
    for x in moves:
        src,dst=safe(x['source']),safe(x['destination'])
        if not src.is_file() or S.U.digest(src)!=x['sha256']:raise ValueError(f'Source identity: {src}')
        if dst.exists() or str(dst).lower() in targets:raise ValueError(f'Destination exists/collision: {dst}')
        targets.add(str(dst).lower())
    for c in plan['code_changes']:
        if S.U.digest(safe(c['path']))!=c['before_sha256']:raise ValueError('Reader changed after planning')
    print(json.dumps({'preflight':'PASS','moves':len(moves),'bytes':sum(x['size_bytes'] for x in moves),'reader_adapters':len(plan['code_changes']),'decisions':dict(Counter(x['decision'] for x in plan['candidates']))},ensure_ascii=False),flush=True)
    if not args.apply:return
    completed=[]; backups=[]
    for c in plan['code_changes']:
        src=safe(c['path']);dst=safe((BACK/'original_code'/c['path']).relative_to(ROOT))
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        backups.append({'path':c['path'],'backup':dst.relative_to(ROOT).as_posix(),'sha256':c['before_sha256']})
    for x in moves:
        src,dst=safe(x['source']),safe(x['destination']);dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(S.U.extended(src),S.U.extended(dst))
        if src.exists() or S.U.digest(dst)!=x['sha256']:raise ValueError('Post-move identity')
        completed.append({k:x[k] for k in ['source','destination','sha256','size_bytes','reason']})
        S.dump(REG/'partial_execution_receipt.json',{'completed':completed,'code_backups':backups})
    for c in plan['code_changes']:
        p=safe(c['path']);txt=p.read_bytes().decode('utf-8')
        for old,new in c['replacements']:txt=txt.replace(old,new)
        p.write_bytes(txt.encode('utf-8'))
        if S.U.digest(p)!=c['after_sha256']:raise ValueError('Adapter write identity')
    S.dump(REG/'execution_receipt.json',{'schema':'R7C3E_MOVE_RECEIPT_V1','date':'2026-10-12','moves':completed,'code_backups':backups,'code_changes':plan['code_changes'],'deleted_scientific_files':0,'renamed_scientific_files':0,'new_directory_links':0,'status':'PASS_MOVES_HASH_VERIFIED'})
    print(f'APPLIED {len(completed)} moves; exact reader path adapter=1',flush=True)

if __name__=='__main__':main()
