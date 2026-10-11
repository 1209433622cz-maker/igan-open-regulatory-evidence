"""Content-informed organization of the twelve non-figure workspace roots.

Immutable data/model bundles and runnable stage interfaces retain their paths.
Loose historical documents are moved only after conservative dependency checks.
No deletion, raw-data modification, scientific recalculation or public upload.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, json, os, re, stat, time, importlib.util

ROOT = Path(r'H:\SCI2\YR1')
STAGE = 'R7C3E_20261012'
OUT = ROOT / '5_analysis/R7C3E_SubfolderOrganization_20261012'
REG = ROOT / '0_admin/navigation/R7C3E_20261012'
BACK = ROOT / '9.Version/workspace_reorganization/R7C3E_20261012'
TOPS = ['0_admin','1_data','2_code','3_results','4_output','5_analysis','5_manuscript','6_release','7.Report','8.Reference','9.Version','9_Vote']
spec = importlib.util.spec_from_file_location('audit_util', ROOT/'2_code/00_workspace_management/R7C3C_20261012/01_full_audit.py')
U = importlib.util.module_from_spec(spec); spec.loader.exec_module(U)
SELF = ['5_analysis/R7C3E_SubfolderOrganization_20261012/','0_admin/navigation/R7C3E_20261012/','9.Version/workspace_reorganization/R7C3E_20261012/']

def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def walk():
    skipped=[]
    for base, dirs, files in os.walk(U.extended(ROOT), followlinks=False):
        base = Path(str(base)[4:])
        for d in list(dirs):
            p=base/d; rel=p.relative_to(ROOT).as_posix()
            if rel in [x.rstrip('/') for x in SELF]: dirs.remove(d); continue
            st=os.lstat(U.extended(p))
            if st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                dirs.remove(d); skipped.append({'path':rel,'reason':'DIRECTORY_REPARSE_POINT_NOT_FOLLOWED'})
        for name in files: yield base/name
    dump(OUT/'SKIPPED_DIRECTORY_LINKS.json',skipped)

def role(rel,title=''):
    low=rel.lower(); name=Path(rel).name.lower()
    if '/.git/' in low: return 'Git 内部对象','固定软件/仓库结构','仅用于 Git 版本恢复，不作为科研结果'
    if '/tooling/' in low or '/skills/' in low or '/quarantine/dependency_attempts/' in low or '/software/' in low:
        return '环境/依赖/技能','固定软件/环境结构','重建本地运行环境；第三方内容不作为本研究成果'
    if '/repositories/' in low: return '公共仓库镜像','镜像而非本地权威结果','核对公开发布身份；推送前另行审查'
    if name.startswith(('readme','index','file_index','directory_index','organization')) or '/navigation/' in low:
        return '目录说明与导航','管理文件','查找权威资产、旧路径去向和复用边界'
    if low.startswith('1_data/'):
        return '来源数据/身份/样本接口','规范数据包，保持相邻组件','复算数据入口及来源匹配；数据许可与个体层公开边界须独立核对'
    if low.startswith('2_code/'):
        return ('历史代码快照' if '/snapshots/' in low else '可执行分析/验收/制作代码'),'阶段接口，保持运行路径','按原输入与阶段条件复跑；不能把准备脚本解释为已获得结果'
    if low.startswith('3_results/'):
        if any(x in low for x in ('r7a2a0_hr','r7a2a0_hra','source_audit','schema','preflight')): return '技术/来源身份验收','既有验收或失败记录','复用 BAM schema、source identity 和技术门；不等同生物学支持'
        return '冻结分析结果/技术验收','按项目阶段区分，保留阴性与不确定','方法比较、模型敏感性、模拟或组织证据；依照原分母和冻结定义引用'
    if low.startswith('5_manuscript/'):
        if '/r7c3b_' in low or '/r7c3c_' in low: return '当前精修稿/投稿候选','最终版本批准及投稿状态须单独核对','投稿审阅、图件与补充材料；不是已经投稿的证明'
        return '历史稿件/期刊分支','历史归档，非当前上传稿','追踪写作与证据修订；不能混用版本的图注/分母'
    if low.startswith('6_release/') or '/releases/' in low or name.endswith(('.zip','.sha256')):
        return '交付包/校验/构建记录','冻结包或构建快照','重现阶段交付身份；ZIP 内部路径与 checksum 不改写'
    if low.startswith('7.report/') or '行动记录' in rel:
        return '行动记录/科学或工程审计','历史项目记忆','恢复阶段裁决、失败原因、决策依据与可复用工程成果'
    if low.startswith('8.reference/'):
        return '参考文献/外部来源快照','来源材料，不是用户指令','借鉴写作、方法或核对既有研究；文件名中 JIF 等旧标注未重新验证'
    if '研究计划' in rel or '/research_plans/' in low: return '研究计划及版本比较','RP v4 为当前计划，旧版归档','对照研究问题、冻结范围与升级 STOP/GO 门'
    if low.startswith('9.version/'): return '归档/回滚/接收快照','历史与恢复用途','恢复旧原件或检查来历，不默认替代当前规范数据'
    if low.startswith('9_vote/'): return '当前项目裁决','状态与下一阶段','查找 PBC/RP v4 主线与尚未完成的投稿步骤'
    if low.startswith('5_analysis/'): return '自包含分析/文件审计目录','按轮次保持完整','查找来源追踪、内容索引、QA、路径迁移与回滚凭证'
    if low.startswith('4_output/'): return '导出/阅读入口','展示用途','阅读或历史图表展示，不定义分析结果权威版本'
    return '项目管理/冻结协议/来源登记','按原阶段解释','恢复协议、输入身份与 QA 决策，不将旧状态当成当前状态'

def project(rel,title=''):
    low=rel.lower(); tokens=re.findall(r'(?i)R[2-7][A-Z][A-Z0-9]*(?:_v\d+)?',rel)
    if '/54_papers/' in low or '54_paper_method' in low: return '跨领域写作方法参考','54-paper corpus'
    if '/tooling/' in low or '/skills/' in low or '/.git/' in low: return '共享环境/软件','STANDARD_LAYOUT'
    if '/repositories/' in low: return '公开镜像（多项目历史）','GIT_MIRROR'
    if any(s in low for s in ('workspace','reorganization','navigation','figure_registry','figure_reorganization','compatibility')):
        return '工作区治理/多项目',';'.join(dict.fromkeys(tokens)) or 'SHARED'
    if tokens:
        s=tokens[-1].upper()
        if s.startswith(('R2','R3','R4')): return 'SSc（冻结归档）',s
        if s.startswith('R5'): return 'MG（主线停止，工程归档）',s
        if s.startswith('R6'): return 'IgAN（冻结归档）',s
        if s=='R7A0' or s=='R7A1A': return 'PBC/CeD 前期组合预验收',s
        return 'PBC（当前主项目或其历史阶段）',s
    if any(s in low for s in ('/gwas/mg/','/scrna/mg/','/literature/mg/','/mg_')): return 'MG（主线停止，工程归档）','MG'
    if 'igan' in low or '/serum_iga/' in low: return 'IgAN（冻结归档）','IgAN'
    if 'ssc' in low or 'il12rb2' in low and ('tenk10k_' in low or 'source_ld' in low): return 'SSc 历史与共享方法资产','SSc/SHARED'
    if 'pbc' in low or 'rp_v' in low: return 'PBC（当前主项目或其历史阶段）','PBC/RP'
    if any(s in low for s in ('onek1k','tenk10k','eqtl','caqtl','annotation','liftover','variant_identity','/reference/ld')): return '跨项目共享来源资产','SOURCE_RESOURCE'
    return '共享/历史待按原协议使用','SHARED'

def stage_of(name):
    t=re.findall(r'(?i)R[2-7][A-Z][A-Z0-9]*(?:_v\d+)?',name)
    return t[0].upper() if t else 'shared_legacy'

def phase(stage):
    return 'SSc' if stage.startswith(('R2','R3','R4')) else 'MG' if stage.startswith('R5') else 'IgAN' if stage.startswith('R6') else 'PBC'

def main():
    if (OUT/'BEFORE_FILES.tsv').exists(): raise SystemExit('Frozen before inventory already exists. Refusing to overwrite.')
    OUT.mkdir(parents=True,exist_ok=True);REG.mkdir(parents=True,exist_ok=True)
    cachep=ROOT/'5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/final/ALL_FILES_FINAL_CLOSING.tsv'
    cache={r['relative_path']:r for r in csv.DictReader(cachep.open(encoding='utf-8-sig'),delimiter='\t')}
    rows=[]; errors=[]; fresh=0; reused=0; start=time.time()
    for i,p in enumerate(walk(),1):
        rel=p.relative_to(ROOT).as_posix()
        try:
            st=os.stat(U.extended(p));old=cache.get(rel)
            matched=old and int(old['size_bytes'])==st.st_size and int(old['mtime_ns'])==st.st_mtime_ns
            if matched: r=dict(old); basis='PRIOR_FULL_SHA256_MATCHED_PATH_SIZE_MTIME'; reused+=1
            else:
                category,policy=U.classify(rel)
                r={'relative_path':rel,'size_bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':U.digest(p),'category':category,'publication_policy':policy,'extension':p.suffix.lower(),'top_level':rel.split('/')[0]}
                r.update(U.summarize(p,rel,st.st_size));basis='FRESH_FULL_SHA256';fresh+=1
            r['verification_basis']=basis;r['role'],r['handling'],r['future_use']=role(rel,r.get('title',''))
            r['project'],r['primary_stage']=project(rel,r.get('title',''))
            rows.append(r)
        except Exception as e: errors.append({'relative_path':rel,'error':str(e)})
        if i%5000==0: print(f'INVENTORY {i} fresh={fresh} cached={reused}',flush=True)
    rows.sort(key=lambda x:x['relative_path'].lower())
    U.tsv(OUT/'BEFORE_FILES.tsv',rows,sorted({k for r in rows for k in r}));U.tsv(OUT/'READ_ERRORS.tsv',errors,['relative_path','error'])
    dump(OUT/'BEFORE_STATE.json',{'files':len(rows),'bytes':sum(int(r['size_bytes']) for r in rows),'fresh_hashes':fresh,'validated_cache_hashes':reused,'errors':len(errors),'seconds':round(time.time()-start,2),'scope':TOPS,'excluded_this_round_outputs':SELF})
    if errors: raise SystemExit('Read errors: plan not generated.')
    # Conservative code dependency search. Frozen reports/catalogues are provenance, not executable readers.
    corpus=[]
    for r in rows:
        rel=r['relative_path']; low=rel.lower()
        if r['extension'].lower() not in {'.py','.ps1','.r','.sh','.cmd','.bat'}:continue
        if not rel.startswith(('2_code/','5_manuscript/','5_analysis/R7C0_')):continue
        if '/00_workspace_management/' in low or '/snapshots/' in low or '/__pycache__/' in low:continue
        try:txt=U.read_text(ROOT/rel)
        except Exception:continue
        corpus.append((rel,txt.lower().replace('\\\\','/').replace('\\','/')))
    requests=[]
    def add(src,dst,reason,metadata=None):
        p=ROOT/src
        if not p.is_file():return
        txtname=p.name.lower(); hits=[]
        for code,txt in corpus:
            if src.lower() in txt or txtname in txt:
                hits.append(code)
        row=next(r for r in rows if r['relative_path']==src)
        requests.append({'source':src,'destination':dst,'reason':reason,'sha256':row['sha256'],'size_bytes':int(row['size_bytes']),'dependencies':hits,'decision':'RETAIN_CANONICAL_REFERENCED' if hits else 'MOVE','metadata':metadata or {}})
    for folder in ['3_results/00_audit','7.Report/current','0_admin/protocol/current']:
        for p in sorted((ROOT/folder).iterdir()):
            if not p.is_file() or p.name.lower().startswith(('readme','pbc_current','workspace_paths')):continue
            stage=stage_of(p.name)
            if folder.startswith('3_results'):
                kind='02_来源网页' if p.suffix.lower()=='.html' else '03_供者汇总' if 'compact_summary' in p.name else '01_验收与运行记录'
                dst=f'3_results/00_audit/90_历史散件/PBC/{stage}/{kind}/{p.name}'
            elif folder.startswith('7.Report'):
                kind='99_行动记录' if p.name.startswith('99_') else '00_执行摘要'
                dst=f'7.Report/rounds/90_历史散件/{phase(stage)}/{stage}/{kind}/{p.name}'
            else:
                dst=f'0_admin/protocol/history/90_历史散件/{phase(stage)}/{stage}/{p.name}'
            add(p.relative_to(ROOT).as_posix(),dst,'按真实阶段归档原 current/平铺历史散件；被可执行代码引用的路径保留')
    for p in sorted((ROOT/'6_release').iterdir()):
        if not p.is_file() or p.name.lower().startswith(('readme','release_catalog')):continue
        stage=stage_of(p.name);base=re.sub(r'(?:\.zip(?:\.sha256)?|\.receipt\.json|_release_receipt\.json)$','',p.name)
        add(p.relative_to(ROOT).as_posix(),f'6_release/history/PBC/{stage}/{base}/{p.name}','ZIP、外部哈希与 receipt 同组；包内文件不改')
    for p in sorted((ROOT/'9.Version').iterdir()):
        if not p.is_file() or p.name.lower().startswith('readme') or 'RP_v4' in p.name:continue
        if 'RP_v3' in p.name: dst=f'9.Version/research_plans/PBC/RP_v3_20261009/{p.name}'
        elif p.suffix.lower()=='.tsv':dst=f'9.Version/00_历史目录清单/{p.name}'
        else:dst=f'9.Version/research_plans/PBC/R7B2A_可行性复核_20261009/{p.name}'
        add(p.relative_to(ROOT).as_posix(),dst,'计划旧版本与其审计/原交付包归组；RP v4 当前路径保留')
    for p in sorted((ROOT/'9.Version/releases').iterdir()):
        if p.is_file() and not p.name.lower().startswith('readme'):
            st=stage_of(p.name);base=re.sub(r'\.zip(?:\.sha256)?$','',p.name)
            add(p.relative_to(ROOT).as_posix(),f'9.Version/releases/{phase(st)}/{st}/{base}/{p.name}','历史发布原件与校验同组，不与当前投稿包混放')
    # Original 54-paper matrix is the human-reviewed method classification authority.
    matrix=list(csv.DictReader((ROOT/'0_admin/reference_blueprints/54_paper_method_study/01_54篇论文写作范式矩阵.csv').open(encoding='utf-8-sig')))
    for p in sorted((ROOT/'8.Reference/literature/54_papers').iterdir()):
        if p.suffix.lower()!='.pdf':continue
        matches=[m for m in matrix if m['title'] in p.stem]
        if len(matches)!=1:raise RuntimeError(f'54-paper identity not unique: {p.name}')
        m=matches[0];a=m['archetype']
        if '单细胞' in a and ('MR' in a or '共定位' in a):cat='01_单细胞遗传归因_MR与共定位'
        elif 'MR' in a or '孟德尔' in a:cat='02_遗传因果推断与可成药靶点'
        elif '环境暴露' in a or '网络毒理' in a or '网络药理' in a or '分子对接' in a:cat='03_暴露组_网络毒理与分子对接'
        elif '生物信息' in a or '机器学习' in a or '生物标志' in a:cat='04_转录组与生物标志物'
        elif any(x in a for x in ('综述','Protocol','方案','操作','评论','协议','计量','评述')):cat='06_综述_操作规范与其他文体'
        else:cat='05_人群组学_遗传结构与实验机制'
        add(p.relative_to(ROOT).as_posix(),f'8.Reference/literature/54_papers/{cat}/{p.name}','原 54-paper 人工分析矩阵的写作范式分类；保留原文献文件名和 SHA-256',m)
    dump(REG/'organization_plan.json',{'schema':'R7C3E_NON_FIGURE_ORGANIZATION_V1','date':'2026-10-12','scope':TOPS,'policy':'NO_DELETE_NO_SCIENTIFIC_BYTES_CHANGED_REFERENCED_INTERFACES_RETAINED','candidates':requests})
    U.tsv(OUT/'CANDIDATE_DEPENDENCY_AUDIT.tsv',[{**x,'dependencies':';'.join(x['dependencies']),'metadata':json.dumps(x['metadata'],ensure_ascii=False)} for x in requests],['source','destination','decision','reason','size_bytes','sha256','dependencies','metadata'])
    print(json.dumps({'inventory':len(rows),'bytes':sum(int(r['size_bytes']) for r in rows),'fresh':fresh,'cached':reused,'candidate_decisions':dict(Counter(x['decision'] for x in requests)),'movable_by_root':dict(Counter(x['source'].split('/')[0] for x in requests if x['decision']=='MOVE'))},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
