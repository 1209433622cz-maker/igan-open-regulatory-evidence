"""Full public-tree file audit and auditable current navigation generation."""
from pathlib import Path
import csv, json, hashlib, re, subprocess, shutil, zipfile, urllib.parse, collections, datetime

ROOT=Path(r'H:\SCI2\YR1')
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
AN=ROOT/'5_analysis/R7C3G1_20261012'
REPORT=ROOT/'7.Report/rounds/R7C3G1_20261012'
CODE=ROOT/'2_code/00_workspace_management/R7C3G1_20261012'
TAG='r7c3g1-eight-folder-expert-narrative-2026-10-12'
URL='https://github.com/1209433622cz-maker/igan-open-regulatory-evidence'
FOLDERS=['0_admin','1_data','2_code','3_results','4_figures','5_manuscript','6_release','7.Report']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf-8')
def save(p,o):put(p,json.dumps(o,ensure_ascii=False,indent=2))
def tsv(p,rows,fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def paths():return sorted(p for p in REPO.rglob('*') if p.is_file() and '.git' not in p.relative_to(REPO).parts)

VERIFY='''"""Verify the whole current public tree using canonical Git blobs, no extra packages."""
from pathlib import Path
import hashlib, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
def main():
    manifest=subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:MANIFEST.sha256']).decode('utf-8')
    rows=[line.split('  ',1) for line in manifest.splitlines() if line.strip()]
    tracked=set(subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-rz','--name-only','HEAD']).decode('utf-8').split('\\0'))-{''}
    expected={p for h,p in rows}
    assert tracked==expected|{'MANIFEST.sha256'}, 'Manifest coverage must equal all tracked files except itself'
    proc=subprocess.Popen(['git','-C',str(ROOT),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        for digest,path in rows:
            proc.stdin.write(('HEAD:'+path+'\\n').encode('utf-8'));proc.stdin.flush()
            head=proc.stdout.readline().decode().strip().split()
            assert len(head)==3 and head[1]=='blob', 'Missing Git blob: '+path
            body=proc.stdout.read(int(head[2]));proc.stdout.read(1)
            assert hashlib.sha256(body).hexdigest()==digest, 'SHA-256 mismatch: '+path
    finally:
        proc.stdin.close();proc.wait()
    required=['0_admin','1_data','2_code','3_results','4_figures','5_manuscript','6_release','7.Report']
    assert {p.split('/')[0] for p in tracked if '/' in p}==set(required), 'Unexpected/missing directory roots'
    print(f'PASS {len(rows)}/{len(rows)} canonical Git-blob SHA-256; eight directory roots; exact manifest coverage')
if __name__=='__main__':main()
'''

def main():
    put(REPO/'2_code/00_repository/verify_repository.py',VERIFY)
    readme=REPO/'README.md'
    body=readme.read_text(encoding='utf-8')
    if '## A retained counterexample' not in body:
        section='''## A retained counterexample

![Figure 3: signal-pair identity, cell context and model sensitivity](4_figures/Fig3/R7C3G/Figure_3.png)

Figure 3 keeps the FCRL3/CD8_ET PF10/PF50 reversal visible. The manuscript uses it to expose model sensitivity, alongside supported B-cell contexts, rather than treating all strong regional eQTL as the same mechanism. Vector masters and full legends are in the manuscript package.

'''
        body=body.replace('## Reproduction, inputs and quality',section+'## Reproduction, inputs and quality')
        put(readme,body)
    # The publication scripts are visible separately; historical script copies are untouched.
    for p in CODE.glob('*.py'):
        dest=REPO/'2_code/00_repository/R7C3G1'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    put(REPO/'0_admin/audit/r7c3g1/README.md','''# Public tree audit scope

`MANIFEST.sha256` at repository root covers every tracked file except itself. Run the canonical Git-blob verifier on current HEAD; this is the authoritative whole-tree identity check.

`PUBLIC_FILE_CATALOG.tsv` provides roles, sizes and hashes for content files. To avoid self-reference it excludes itself, the whole-tree manifest and `DIRECTORY_SIZE_SUMMARY.tsv`; all three are covered by the whole-tree manifest. `DIRECTORY_SIZE_SUMMARY.tsv` includes its own converged size and all files except the root manifest, whose byte length can be read directly.

The preservation table maps all 2,335 pre-existing tracked files to unchanged identities. Frozen historical navigation retains original paths; current links are tested separately. The remote receipt identifies an independently fetched content commit. Later main commits append audit metadata; the external local final receipt records the last HEAD, avoiding a commit hash referencing itself.
''')
    checks=[];issues=[];stats=collections.defaultdict(lambda:[0,0]); extensions=collections.Counter()
    raw_suffixes={'.bed','.bim','.fam','.pgen','.pvar','.psam','.bam','.cram','.h5ad','.rds','.npy','.npz','.bcf'}
    # High-specificity patterns only. Diagnostic outputs never print token contents.
    secrets=[('GITHUB_CLASSIC',re.compile(rb'gh[pousr]_[A-Za-z0-9]{36,255}')),
             ('GITHUB_FINE_GRAINED',re.compile(rb'github_pat_[A-Za-z0-9_]{70,255}')),
             ('PRIVATE_KEY',re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
             ('AWS_ACCESS_ID',re.compile(rb'AKIA[A-Z0-9]{16}')),
             ('SLACK_TOKEN',re.compile(rb'xox[baprs]-[0-9A-Za-z-]{25,}'))]
    archive_rows=[]
    for p in paths():
        rel=p.relative_to(REPO).as_posix();n=p.stat().st_size
        stats[rel.split('/')[0]][0]+=1;stats[rel.split('/')[0]][1]+=n;extensions[p.suffix.lower()]+=1
        if n>10*1024*1024:issues.append({'path':rel,'kind':'GIT_BLOB_GT_10MIB'})
        if p.suffix.lower() in raw_suffixes:issues.append({'path':rel,'kind':'DONOR_OR_LARGE_RAW_FORMAT'})
        if p.name in ['.env','.env.local'] or p.suffix.lower() in {'.pem','.key'}:issues.append({'path':rel,'kind':'LOCAL_SECRET_FORMAT'})
        b=p.read_bytes()
        for label,pat in secrets:
            if pat.search(b):issues.append({'path':rel,'kind':label})
        if p.suffix.lower() in {'.zip','.docx','.xlsx'}:
            with zipfile.ZipFile(p) as z:
                assert z.testzip() is None, rel
                archive_rows.append({'path':rel,'members':len(z.infolist()),'crc':'PASS'})
                for member in z.infolist():
                    if member.is_dir():continue
                    if member.filename.lower().endswith(tuple(raw_suffixes)):issues.append({'path':rel+'::'+member.filename,'kind':'NESTED_DONOR_RAW_FORMAT'})
                    data=z.read(member)
                    for label,pat in secrets:
                        if pat.search(data):issues.append({'path':rel+'::'+member.filename,'kind':label})
    assert not issues, json.dumps(issues,ensure_ascii=False)  # Only file/kind; never credential bytes.
    tsv(REPO/'0_admin/audit/r7c3g1/ARCHIVE_CONTENT_QA.tsv',archive_rows)
    save(REPO/'0_admin/audit/r7c3g1/PUBLICATION_CONTENT_GATE.json',{'files_scanned':sum(v[0] for v in stats.values()),'bytes_scanned':sum(v[1] for v in stats.values()),'secret_pattern_hits':0,'raw_donor_format_hits':0,'git_blobs_gt_10MiB':0,'archives_crc_pass':len(archive_rows),'limitations':'Specific credential patterns and excluded raw formats were checked, not a guarantee of absence of every possible sensitive semantic content; original public baseline and reviewed aggregate package retained.'})
    # Validate current navigation only. Frozen historical links are preserved and mapped.
    nav=[REPO/'README.md',REPO/'REPRODUCIBILITY.md',REPO/'DATA_AVAILABILITY.md']+[REPO/f/'README.md' for f in FOLDERS]
    nav += [REPO/'0_admin/docs/EIGHT_FOLDER_MAP.md',REPO/'0_admin/docs/CURRENT_EVIDENCE_AND_REUSE.md']
    link_rows=[]
    for p in nav:
        text=p.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',text):
            target=target.strip().strip('<>')
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',target) or target.startswith('#'):continue
            target=urllib.parse.unquote(target.split('#',1)[0])
            resolved=p.parent/target
            ok=resolved.exists()
            link_rows.append({'document':p.relative_to(REPO).as_posix(),'target':target,'status':'PASS' if ok else 'FAIL'})
    failures=[r for r in link_rows if r['status']=='FAIL']
    assert not failures,json.dumps(failures,ensure_ascii=False)
    tsv(REPO/'0_admin/audit/r7c3g1/CURRENT_NAVIGATION_LINK_QA.tsv',link_rows)
    prep=json.loads((AN/'PREPARATION_STATE.json').read_text(encoding='utf-8'))
    preservation=REPO/'0_admin/audit/r7c3g1/PATH_MIGRATION_AND_PRESERVATION.tsv'
    with preservation.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            assert sha(REPO/row['new_path'])==row['sha256'], 'Changed historical identity: '+row['old_path']
    report=f'''# R7C3G1：GitHub八目录重构与最新版论文公开同步 — 2026-10-12

## 1. 授权与目的

本轮依据用户“按整理分析完的结果和现有论文情况推送并重构GitHub，至少包含图示八目录”的直接授权执行。操作对象为既有公开仓库 `{URL}`。本轮没有删除仓库、修改仓库名或改写历史；沿用既有已认证GitHub CLI和Git HTTPS。此前删除/新建仓库的动作不重复。

## 2. 真实输入与回退准备

推送前本地与远端main一致：`{prep['old_head']}`。已制作并验证完整Git bundle，包含14个refs，体积70,039,680 bytes；私有备份保存在本机 `0_admin/backups/R7C3G1_GitHubEightFolder_20261012`，不上传Git对象或账户配置。仓库元数据、既有Release描述和refs也已备份。

旧仓库共{prep['original_files']}个跟踪文件。对每个文件重新读取大小与SHA-256；根元数据先逐字节归档，再移动历史树。{prep['preserved_original_files']}/{prep['original_files']}原文件均在迁移表目标路径校验一致。历史main分支、tags及Releases继续保留原Git身份。

## 3. 八目录结构

| 目录 | 内容与迁移 |
|---|---|
| 0_admin | 原audit/docs/environment/protocols/workspace_support，当前状态、规范、环境和来源审计 |
| 1_data | 原data，provider来源与身份；新增{prep['large_input_pointers']}条>10MiB本地输入指针 |
| 2_code | 原analysis全部原始脚本；新增R7C3G组图/文档脚本及仓库校验工具 |
| 3_results | 原results；新增37项端点复算、图件值与SourceZIP成员索引 |
| 4_figures | 当前Fig1–6及S1–S3的PDF/SVG/PNG；原figures完整保存在history |
| 5_manuscript | current/R7C3G精确包；原manuscript全部保存在history，包括R7C3F |
| 6_release | 版本收据、原ZIP哈希、GitHub Release下载入口与发布记录 |
| 7.Report | 原reports→rounds；新增R7C3G专家报告和本轮记录 |

不改写冻结工作记录中的原科学路径/结论；使用逐文件迁移表解析旧路径，原历史tag仍可读取旧树。新版顶层README和目录README全部面向当前PBC证据；旧IgAN复现主线已归档并由当前PBC contract替换。`.gitignore`旧的整个`1_data/`忽略规则已移除，使来源文本可跟踪；原始BAM、PLINK、RDS、矩阵、credentials和运行缓存仍排除。

## 4. 最新论文、图片与科学身份

当前候选为R7C3G，QiTeng v0.3.24.2。独立复制前再次核验包内93/93 SHA-256；科学SourceZIP与S1–S10工作簿不变。24页主稿WPS PDF、25页图文内嵌审阅PDF、6页SI和1页Cover全部复制原审核字节。本轮未重新渲染、改写论文、重复图件选择或生成新科学结果。

当前6主图+3补图共有34子图：范围/输入→同输入双向重分类→pair/cell/model反例→模拟trade-off→外部IL12RB2支持→组织阴性边界。图像目录与自包含阅读包同时提供相同hash的PDF/SVG/PNG；文件格式不算新实验。46-image selection、34-panel map、E-series claims及37-row历史补充ledger crosswalk均保留。

37/37端点复算、160/160文档检查、4/4 WPS导出和56/56页面视觉复核是R7C3G已完成的证据，本轮做fresh字节验收，不冒称重跑GWAS/LD/SuSiE或486,000模拟。原始全量本地38,925文件索引属于上一轮指定时点；本轮全量扫描范围是重构后的公开仓库，不等于再次读取43GiB全部原始数据。

## 5. 公开内容与链接检查

当前树扫描{sum(v[0] for v in stats.values())}个文件、{sum(v[1] for v in stats.values()):,}bytes（最终报告/manifest文件增量另由最终snapshot清单覆盖）。高特异凭据模式0命中；排除的个体级/大矩阵原始格式0命中；>10MiB Git blob为0。{len(archive_rows)}个ZIP/DOCX/XLSX通过CRC，并逐成员检查排除的原始格式与凭据模式。该模式扫描不是对所有语义隐私的普适保证；公开基线和聚合审阅资产的内容边界已在NOTICE/DataAvailability明确。

当前导航{len(link_rows)}/{len(link_rows)}本地链接PASS；冻结历史文件中的相对链接不重写，迁移表记录原→新路径。许可证延续原代码MIT、作者文字/图件/可分享聚合结果CC BY4.0，provider原始数据不重授权。作者公开ORCID/单位/邮箱为已确认信息。

推送前canonical Git manifest检查真实捕获并修复两处迁移问题：历史logs目录的6份已公开MD被旧全局ignore规则漏掉，故把ignore限制为根运行logs；旧data/README在生成当前导航前额外精确归档到1_data/history，并更新逐文件迁移目标。修改后重新检查全部原文件identity，且manifest必须与Git tracked集合严格一一对应；未将失败提交单独推送为完成版本。

## 6. 有价值的成果与未来使用

PBC保留GO：6923/5460/1463筛查分母，642高信息subset，92/428/59/63完整状态，同输入8 H4→H3/10 H3→H4，32个共享同时有distinct pairs，PF10/PF50反例，模拟gain/loss/evaluability，以及外部/组织限制都必须共同报告。这里的价值是可审计的调控归因可靠性，不是新因果基因或治疗机制。

后续可复用：byte/provenance、build/allele/donor/covariate identity、source-matched LD、source-CS coverage、prior/config sensitivity、pair identity、真值模拟的discovery/inference区分、donor-level组织统计、panel/claim/source映射，以及SSc/MG/IgAN明确停止记录。旧疾病仍归档，不由本轮仓库重构自动重启。

## 7. 发布与退出状态

发布采用正常追加提交与push，不force push。后续独立核查远端main、全部canonical Git blob、八根目录、历史refs、Release资产hash。最终公开状态以`0_admin/audit/r7c3g1/REMOTE_CONTENT_VERIFICATION.json`及`6_release/PUBLICATION_RECEIPT.json`为准；本机最终回执另记录最后HEAD，避免将一个commit的自身hash写入同一个commit造成循环。

标签：`{TAG}`。Release说明明确这是开放研究和稿件审阅版本，不是期刊投稿、acceptance或已生成DOI。本轮最新editorial资产公开同步，但原R7C3G冻存state的“创建时未push”字段保持原字节，当前发布receipt提供后续事件。

下一阶段仍为 **R7C3H — exact-version作者审阅与publisher PDF proof**；随后才进入作者操作npj Genomic Medicine投稿与真实回执。没有新证据要求扩位点或重跑全部模拟。
'''
    published_path=REPO/'6_release/PUBLICATION_RECEIPT.json'
    published=json.loads(published_path.read_text(encoding='utf-8')) if published_path.exists() else None
    if published:
        report+=f'''\n## 8. 已完成的真实发布事件\n\n公开仓库内容已正常push，并从GitHub独立拉取到另一个bare repository逐blob验证。已核验内容提交：`{published['content_commit_verified']}`；{published['content_canonical_blob_checks']}/{published['content_canonical_blob_checks']} canonical SHA-256 PASS、2335/2335原文件身份PASS、8目录PASS、10旧refs不变。之后main追加本段和回执文件，最终HEAD在本机外部最终回执及最终重新拉取核验中记录，避免hash自引用。\n\n已发布公开审阅/prerelease：{published['release_url']}。3/3附件实际从GitHub下载，size与SHA-256全部匹配本地冻结文件。6个既有Release和12个既有asset的ID/size保留。作者/投稿边界与原Source Data均未改变；本轮未投稿、未生成或核实Zenodo DOI。当前editorial文件已经公开，原包创建时未push的state属于历史快照，另有当前publication receipt记录后续事件。\n'''
    local_report=REPORT/'99_R7C3G1_GitHub八目录重构与推送_详细行动记录_20261012.md'
    put(local_report,report)
    shutil.copy2(local_report,REPO/'7.Report/rounds/r7c3g1'/local_report.name) if (REPO/'7.Report/rounds/r7c3g1').exists() else None
    if not (REPO/'7.Report/rounds/r7c3g1').exists():
        (REPO/'7.Report/rounds/r7c3g1').mkdir(parents=True)
        shutil.copy2(local_report,REPO/'7.Report/rounds/r7c3g1'/local_report.name)
    # Catalogue excludes its own identity, manifest and generated size summary.
    # The whole-tree manifest still covers both generated metadata files.
    catalog=REPO/'0_admin/audit/r7c3g1/PUBLIC_FILE_CATALOG.tsv'
    size_summary=REPO/'0_admin/audit/r7c3g1/DIRECTORY_SIZE_SUMMARY.tsv'
    rows=[]
    for p in paths():
        rel=p.relative_to(REPO).as_posix()
        if p in {catalog,size_summary} or rel=='MANIFEST.sha256':continue
        rows.append({'repository_path':rel,'top_level':rel.split('/')[0] if '/' in rel else 'ROOT_METADATA','bytes':p.stat().st_size,'sha256':sha(p),'role':'CURRENT_CANDIDATE' if '/current/R7C3G/' in rel else 'CURRENT_FIGURE' if rel.startswith('4_figures/') and '/history/' not in rel else 'VERSIONED_RESEARCH_OR_ADMIN'})
    tsv(catalog,rows)
    # Resolve the summary's own byte count to a fixed point (usually two passes).
    if not size_summary.exists():size_summary.touch()
    for _ in range(5):
        before=size_summary.read_bytes()
        counts=collections.defaultdict(lambda:[0,0])
        for p in paths():
            if p.name=='MANIFEST.sha256' and p.parent==REPO:continue
            rel=p.relative_to(REPO).as_posix();key=rel.split('/')[0] if '/' in rel else 'ROOT_METADATA'
            counts[key][0]+=1;counts[key][1]+=p.stat().st_size
        tsv(size_summary,[{'directory':k,'files':v[0],'bytes':v[1]} for k,v in sorted(counts.items())])
        if size_summary.read_bytes()==before:break
    else:raise AssertionError('Directory size summary did not converge')
    with catalog.open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            q=REPO/row['repository_path']
            assert q.stat().st_size==int(row['bytes']) and sha(q)==row['sha256'],row['repository_path']
    manifest=[]
    for p in paths():
        if p==REPO/'MANIFEST.sha256':continue
        manifest.append(sha(p)+'  '+p.relative_to(REPO).as_posix())
    put(REPO/'MANIFEST.sha256','\n'.join(manifest))
    save(AN/'PUBLIC_TREE_AUDIT_STATE.json',{'manifest_entries':len(manifest),'old_files_preserved':prep['preserved_original_files'],'source_package_checks':93,'navigation_checks':len(link_rows),'archives_crc_checks':len(archive_rows),'secret_pattern_hits':0,'raw_format_hits':0,'gt10MiB':0,'report':str(local_report),'previous_content_push_verified':bool(published),'current_audit_file_changes_not_yet_pushed':True})
    print(json.dumps({'manifest_entries':len(manifest),'navigation_checks':len(link_rows),'archives_crc_checks':len(archive_rows),'status':'AUDIT_READY_FOR_COMMIT','previous_content_push_verified':bool(published)}))

if __name__=='__main__':main()
