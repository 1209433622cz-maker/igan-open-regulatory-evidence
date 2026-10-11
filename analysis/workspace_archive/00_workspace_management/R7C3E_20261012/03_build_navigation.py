"""Local-only, annotated file/directory navigation; never modify source bundles."""
from pathlib import Path
from collections import defaultdict, Counter
import csv, json, os, shutil, hashlib, html, re
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scan',HERE/'01_scan_and_plan.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
ROOT,OUT,REG,BACK=S.ROOT,S.OUT,S.REG,S.BACK

THEMES={
 '0_admin':('项目治理、冻结协议、来源登记与环境','navigation','当前项目导航；protocol/current 中保留的历史接口仍按原阶段解释。skills/tooling/repositories 的内部标准结构保持完整。'),
 '1_data':('原始来源数据与可复算输入','gwas','按疾病、资源、build 和原数据包结构使用。BED/BIM/FAM、矩阵/基因/条码和配套 covariates 不拆散；本轮只整理导航，不改变数据字节。'),
 '2_code':('可执行代码、分析门与发布制作','06_intake','阶段代码的路径和相邻模块是运行接口。保留固定代码目录；历史 SSc/MG/IgAN 代码可复用工程方法，不恢复其生物学主线。'),
 '3_results':('冻结结果、输入验收、模型比较与组织证据','04_integration','原始分母、阴性、QC failure、sensitive 和 uninformative 均保留。不得把目录名称或历史 PASS 当成当前论文阳性。'),
 '4_output':('阅读入口与历史展示导出','review','展示文件不替代规范结果与投稿权威图件。历史 REEP3 导出保留历史命题与证伪边界。'),
 '5_analysis':('自包含外部预验收与工作区审计','R7C3E_SubfolderOrganization_20261012','轮次目录保留输入、输出、失败尝试和核验链。目录全量清点属于文件层 QA，不等同逐项科学重算。'),
 '5_manuscript':('稿件版本、图注、补充材料与投稿候选','R7C3B_QiTeng_WPS_SubmissionRefinement_20261011','R7C3B 是最新 QiTeng/WPS 精修候选；R7C3C 是原字节投稿封装。旧 Human Genomics 与较早 PBC 分支是历史版本。编辑版批准、官方表格和出版社 proof 仍须独立闭环。'),
 '6_release':('冻结 ZIP、SHA-256、receipt 与构建快照','R7C3C_2026-10-12','真正的当前投稿候选由导航入口指定，旧 current 名称不自动代表最新。ZIP 与配套 checksum/receipt 同组；包内成员不改写。'),
 '7.Report':('详细行动记录、失败经验与长期项目记忆','rounds','按项目和原阶段恢复行动事实。准备执行、技术 PASS、科学支持与正式投稿完成是不同状态；旧记录保持原字节。'),
 '8.Reference':('论文、外部来源与写作方法参考','literature','54 篇论文按原人工分析矩阵分成六类范式，每篇保留原文件名、哈希和历史评价。来源文档是研究材料，不作为本轮操作指令。'),
 '9.Version':('研究计划、旧版归档、接收快照与回滚','research_plans','RP v4 的现有绝对路径保留。RP v3、旧包、构建缓存与回滚代码分别登记；不删除重复文件，不把接收快照替代规范数据。'),
 '9_Vote':('当前裁决与下一阶段任务','.', '当前主项目为 PBC，按 RP v4 推进。SSc/MG/IgAN 不默认恢复；目录整理不改变作者批准状态，不产生 DOI 或投稿回执。')
}

PURPOSE={
 '0_admin/navigation':'当前状态与跨目录查找；本轮全量索引和旧路径对照也在这里。',
 '0_admin/protocol':'冻结范围、分析假设与逐阶段状态；current 中仍有为历史脚本保留的固定接口。',
 '0_admin/protocols':'PBC-wide screening、642 高信息比较、模拟和同输入对照的原协议路径。',
 '0_admin/compatibility':'历史图件旧名称的隔离兼容副本；不是重新生成当前正式图件。',
 '0_admin/external_sources':'公开资源页面与元数据快照；用于来源定义和数据接入身份核对。',
 '0_admin/figure_registry':'Fig1–8 图件分类、哈希、原路径、版本身份与逐图内容分析。',
 '0_admin/reference_blueprints':'54-paper 写作范式人工矩阵与母版；作为历史方法教材，不照抄低证据机制结论。',
 '0_admin/repositories':'公共 Git 镜像；保持 .git 和仓库内部相对路径，不在本輪推送。',
 '0_admin/skills':'QiTeng 技能及版本注册；不是 CC 写作工作流。内部包结构不拆分。',
 '0_admin/tooling':'R、依赖包、工具与安装环境；软件标准结构保持完整。',
 '0_admin/intake':'接收文件、来源及输入验收；准备好了不等于已经计算完成。',
 '0_admin/validation':'格式、字段、哈希或工程检查；需按检查对象解释 PASS。',
 '0_admin/manifests':'清单目录接口；空目录表示尚无此处文件，不表示数据通过。',
 '0_admin/tmp':'临时运行文件；仅分类说明，不自动清理或删除。',
 '1_data/gwas':'疾病 GWAS，按项目及 build 保留来源对象、下载身份和 schema。',
 '1_data/qtl':'OneK1K、TenK10K、FinnGen/eQTLCatalogue 分子 QTL；source-aware LD 与 donor/model 输入不得混用。',
 '1_data/qtl/OneK1K':'公开 source-aware QTL 输入、980-donor genotype 与 cell-specific donor/model 接口；完整 cis-eQTL 与 genotype 组件保持相邻。',
 '1_data/qtl/TenK10K':'独立 molecular-QTL 资源输入；复用同一疾病 GWAS 时不是独立疾病复制。',
 '1_data/study_inputs':'PBC GJOKA disease/QTL covariance 及模型匹配接口；来源身份和 N 定义保留原协议。',
 '1_data/reference':'基因注释、liftover、variant identity 与 LD 参考；参考 LD 不冒充 source-matched LD。',
 '1_data/scrna':'单细胞公开来源、样本定义和原始/处理后接口；病例对照与 donor 独立性需按数据集判断。',
 '1_data/catalogs':'旧数据迁移清单，保持历史路径事实；查当前路径请用本轮 FILE_INDEX 与 OLD_PATH_LOOKUP。',
 '1_data/manifests':'数据冻结 manifest；原字节保留，不能因目录治理改写历史输入身份。',
 '1_data/software':'来源下载时配套的软件资产；软件目录和 DLL/配置组件保持相邻。',
 '1_data/tcga':'未来模板接口；空目录不是已执行 TCGA 分析。',
 '1_data/literature':'随数据接入保存的研究原文与补充来源，不与正式分析结果混淆。',
 '1_data/incoming':'数据接收缓冲；是否完成验收必须查 manifest/receipt。',
 '2_code/00_workspace_management':'工作区全量审计、图件分类、本轮整理及回滚；不会执行生物学重筛。',
 '2_code/00_utils':'历史管理入口；按其绑定的阶段运行，不按 CURRENT 文件名推断当前主项目。',
 '2_code/06_intake':'各疾病 byte-level、harmonization、LD、coloc 与 donor 门控；按项目/原阶段索引。',
 '2_code/07_analysis':'已有分析运行代码；计算输入和冻结模型是其可复算前提。',
 '2_code/08_reporting':'已有统计图/报告制作代码；图形路径兼容层不改变统计结果。',
 '2_code/09_release':'ZIP、checksum 与验收封装；历史发布 builder 保留旧固定接口。',
 '2_code/11_manuscript':'稿件/组图/补充与 WPS 制作代码；不得混合不同科学版本。',
 '2_code/99_reporting':'早期 SSc 阶段汇总与发布脚本；未搬动，避免改变 __file__ 推导的工作区层级。',
 '2_code/snapshots':'历史代码快照原件，不作为默认可执行最新入口。',
 '2_code/envs':'运行环境描述；安装依赖前核对原数据与软件版本。',
 '3_results/00_audit':'输入、来源、schema、发布/数字 QA；31 份旧肝样本来源网页已移入明确历史子目录。',
 '3_results/01_gwas':'GWAS 位点提取、变异身份和可计算性结果，不与 eQTL 信号混淆。',
 '3_results/01_intake':'源数据身份与接入结果；字节级 closure 不替代统计阳性。',
 '3_results/01_smoke':'早期 IL12RB2 单信号探索；保留 SSc 阶段身份。',
 '3_results/02_coloc':'早期冻结分子证据与 LD/fine-mapping；使用其原范围与原 source 定义。',
 '3_results/03_qtl':'cell-gene QTL、variant coverage 与 model-matched 输入；R7B1B_v2 是 frozen 642 子集接口。',
 '3_results/04_integration':'各阶段共定位/多信号/同输入对照结果；分母和模型版本保持绑定。',
 '3_results/05_simulation':'R7B1C 校准与 R7B2A 模拟复核；不可评价/无可信集结果必须保留。',
 '3_results/05_tissue':'真实 donor-level 组织检测及病例对照结果；detectability 不等于 PBC 特异富集。',
 '3_results/05_scrna':'较早单细胞可用性审计，不等于已完成大规模组织分析。',
 '3_results/legacy_by_round':'旧 SSc 轮次结果原件；保留阴性、技术门与方法工程价值。',
 '4_output/figures':'历史 REEP3 展示导出；其阴性/未定证据边界保留。',
 '4_output/review':'当前 WPS 审阅位置说明；没有新增 WPS/PDF 渲染。',
 '5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011':'RP v4 外部疾病/多模态来源预验收与接入；不把可获取性当已验证结果。',
 '5_analysis/R7C3_FullWorkspaceAudit_2026-10-11':'上一轮全量资产审计；保留其旧路径事实与清单。',
 '5_analysis/R7C3C_WorkspaceAudit_Organization_20261012':'本日全量字节审计、顶层整理、投稿封装和 GitHub 回执。',
 '5_analysis/R7C3D_FigureClassification_20261012':'Fig1–8 内容分析、原/新路径、向量与栅格核对；本轮不重开这些图件。',
 '5_analysis/R7C3E_SubfolderOrganization_20261012':'本轮十二个目录的内容索引、依赖审计、143 文件归档与独立守恒 QA。',
 '5_manuscript/00_outline':'原写作母版；属于教材/历史设计，不是投稿主稿。',
 '5_manuscript/01_methods':'早期冻结方法；不可替代当前 PBC 同输入模型的 Methods。',
 '6_release/current':'历史发布固定接口集合，含多项目旧阶段；文件夹名 current 不是最新状态裁决。',
 '6_release/history':'历史包、哈希和 receipt 的阶段归档；本轮移动的 ZIP 不重新压缩。',
 '7.Report/current':'历史脚本的报告接口集合；可移动的平铺旧稿已归入 rounds/90_历史散件。',
 '7.Report/rounds':'逐轮执行摘要、方法记录和详细行动报告；按原阶段解释。',
 '7.Report/project_history':'长期工作背景与对话记忆；只作历史材料，不覆盖最新用户决定。',
 '7.Report/reorganization':'较早工作区整理、依赖及回滚记录。',
 '7.Report/protocols':'报告型冻结协议与设计说明；保留原阶段范围。',
 '8.Reference/literature/54_papers':'54 篇原文按六类写作范式实物归档；分类权威为原 54-paper 分析矩阵。',
 '8.Reference/literature/MG':'MG 关联研究与复制边界原文快照；不默认恢复 MG 项目。',
 '8.Reference/literature/target_study':'SSc target-study 原文、补充与访问网页；冻结历史的来源证据。',
 '8.Reference/code':'外部或来源代码参考；作为方法来源，不冒充本研究原创代码。',
 '8.Reference/external_resources':'外部资源接口；空目录表示本路径无文件。',
 '9.Version/research_plans':'旧研究计划及其审计包；RP v4 原固定路径仍在根目录。',
 '9.Version/releases':'接收/历史发布原件与构建快照，按项目和阶段归组；不是当前投稿候选。',
 '9.Version/00_历史目录清单':'原迁移 catalog 与 quarantine 候选表，保留当时路径事实；没有执行删除。',
 '9.Version/stage_workspaces':'历史阶段工作快照，不替代规范 1_data/2_code/3_results。',
 '9.Version/staging_downloads':'接收的轻量输入/执行包解包；准备材料不解释为完成计算。',
 '9.Version/quarantine':'旧依赖尝试和非规范导出；仅保留与注释，没有删除。',
 '9.Version/superseded':'被替代的发布原件和旧目录布局；用于回滚与来历核对。',
 '9.Version/workspace_reorganization':'目录整理前原代码、原导航和逐轮恢复依据。',
 '9.Version/figure_reorganization':'Fig1–8 整理前原路径依赖代码/根说明的恢复依据。',
 '9.Version/workspace_snapshots':'收到的整体工作区 ZIP；作为来源快照，不当作当前完整原始数据。',
 '9.Version/project_archives':'SSc 等停止主线的项目状态与归档说明。',
 '9.Version/legacy_exports':'历史 ZIP 导出；完整包身份保留，不重复解释为当前结果。',
}

generated=[]
def write(rel,txt):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        old=BACK/'original_navigation'/rel
        old.parent.mkdir(parents=True,exist_ok=True)
        if not old.exists():shutil.copy2(p,old)
    p.write_text(txt,encoding='utf-8')
    generated.append({'path':rel,'sha256':S.U.digest(p),'backup':(BACK/'original_navigation'/rel).relative_to(ROOT).as_posix() if (BACK/'original_navigation'/rel).exists() else ''})

def purpose(rel):
    best=next((PURPOSE[k] for k in sorted(PURPOSE,key=len,reverse=True) if rel==k or rel.startswith(k+'/')),None)
    if best:return best
    top=rel.split('/')[0]
    return THEMES[top][2] if top in THEMES else '按所属项目、原阶段和文件内容索引使用。'

def md_link(rel,label=None):
    return f'[{label or Path(rel).name}](<{(ROOT/rel).as_posix()}>)'

def main():
    if (REG/'generated_navigation_files.json').exists():raise SystemExit('Navigation already generated; do not overwrite audit identities.')
    plan=json.loads((REG/'organization_plan.json').read_text(encoding='utf-8'))
    receipt=json.loads((REG/'execution_receipt.json').read_text(encoding='utf-8'))
    moves={x['source']:x['destination'] for x in receipt['moves']}
    code={x['path']:x for x in receipt['code_changes']}
    before=list(csv.DictReader((OUT/'BEFORE_FILES.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    rows=[]
    for old in before:
        if old['top_level'] not in S.TOPS:continue
        r=dict(old);r['original_path']=r['relative_path'];r['relative_path']=moves.get(r['relative_path'],r['relative_path'])
        if r['original_path'] in code:r['sha256']=code[r['original_path']]['after_sha256'];r['verification_basis']='FRESH_EXACT_READER_PATH_ADAPTER'
        r['organization_action']='MOVED_HASH_IDENTICAL' if r['original_path'] in moves else 'TWO_INPUT_PATHS_ADAPTED' if r['original_path'] in code else 'CANONICAL_RETAINED'
        if r['relative_path'].startswith('2_code/00_workspace_management/R7C3E_20261012/'):
            r['sha256']=S.U.digest(ROOT/r['relative_path']);r['size_bytes']=os.stat(S.U.extended(ROOT/r['relative_path'])).st_size
            r['verification_basis']='FRESH_THIS_ROUND_TOOL';r['organization_action']='THIS_ROUND_TOOL_NOT_PREEXISTING_USER_ASSET'
        r['original_sha256']=old['sha256'];rows.append(r)
    fields=['relative_path','original_path','top_level','project','primary_stage','role','handling','future_use','organization_action','size_bytes','sha256','original_sha256','verification_basis','content_status','title','content_detail','rows_or_pages','publication_policy','parse_error']
    S.U.tsv(OUT/'CLASSIFIED_ORIGINAL_FILES.tsv',rows,fields)
    S.U.tsv(REG/'OLD_PATH_LOOKUP.tsv',[{'original_path':x['source'],'current_path':x['destination'],'sha256':x['sha256'],'reason':x['reason']} for x in receipt['moves']],['original_path','current_path','sha256','reason'])
    folders=defaultdict(list)
    for r in rows:
        q=Path(r['relative_path'])
        for parent in q.parents:
            if str(parent)=='.':break
            folders[parent.as_posix()].append(r)
    # Include actual empty business directories; never follow the excluded links.
    for top in S.TOPS:
        for base,dirs,_ in os.walk(S.U.extended(ROOT/top),followlinks=False):
            base=Path(str(base)[4:])
            dirs[:]=[d for d in dirs if not os.lstat(S.U.extended(base/d)).st_file_attributes & 0x400 and d!='00_目录索引']
            rel=base.relative_to(ROOT).as_posix()
            folders.setdefault(rel,[])
    directory_rows=[]; detail_count=0
    for rel,items in sorted(folders.items(),key=lambda x:x[0].lower()):
        if any(rel==p.rstrip('/') or rel.startswith(p) for p in S.SELF):continue
        projects=';'.join(sorted({x['project'] for x in items}))
        roles=';'.join(k for k,_ in Counter(x['role'] for x in items).most_common(4))
        standard=any(x in '/'+rel.lower()+'/' for x in ['/tooling/','/skills/','/.git/','/repositories/','/quarantine/dependency_attempts/'])
        row={'directory':rel,'files_before_organization':len(items),'bytes_original':sum(int(x['size_bytes']) for x in items),'projects':projects,'roles':roles,'purpose':purpose(rel),'status':'STANDARD_SOFTWARE_STRUCTURE_RETAINED' if standard else 'EMPTY_INTERFACE_NO_EXECUTED_FILE_HERE' if not items else 'CLASSIFIED_CANONICAL_OR_ARCHIVED'}
        directory_rows.append(row)
        # Annotate business first/second-level folders outside immutable source bundles.
        parts=Path(rel).parts
        if len(parts) not in (2,3) or standard or any(k in parts for k in ['__pycache__','00_目录索引']):continue
        top=parts[0];label='__'.join(parts[1:])+'.md';annotation=f'{top}/00_目录索引/子文件夹说明/{label}'
        text=f'# {rel}\n\n更新：2026-10-12，R7C3E。\n\n{purpose(rel)}\n\n'
        text+=f'原有资产：{len(items):,} 个文件，{row["bytes_original"]:,} bytes。此计数来自本轮整理前全量资产，已按搬迁去向重新分组，不含本轮新增索引。\n\n'
        text+=f'项目/阶段归属：{projects or "尚无文件，保留接口"}。\n\n'
        if not items:text+='此目录为空；没有在这里执行过或保存过分析的证据。\n'
        else:
            groups=Counter(x['primary_stage'] for x in items)
            text+='| 原阶段/资源 | 文件数 |\n|---|---:|\n'+''.join(f'| {s} | {n:,} |\n' for s,n in groups.most_common(18))
            text+='\n| 代表性文件 | 身份/用途 |\n|---|---|\n'
            # Representative is descriptive, not preferential selection of positives.
            chosen=[]
            for x in sorted(items,key=lambda r:(0 if r['role'] not in ['环境/依赖/技能','Git 内部对象','公共仓库镜像'] and Path(r['relative_path']).suffix.lower() in ['.md','.json','.tsv','.docx','.zip'] else 1,r['relative_path'])):
                if x['role'] not in {a['role'] for a in chosen} or len(chosen)<4:chosen.append(x)
                if len(chosen)>=7:break
            for x in chosen:text+=f'| {md_link(x["relative_path"])} | {x["role"]}；{x["future_use"]} |\n'
        text+='\n全部文件均登记在同级索引的 FILE_INDEX.tsv；历史原路径可以用全局 OLD_PATH_LOOKUP.tsv 查询。没有修改原始数据或冻结科学结果。\n'
        write(annotation,text);detail_count+=1
    S.U.tsv(OUT/'DIRECTORY_CLASSIFICATION.tsv',directory_rows,list(directory_rows[0]))
    for top in S.TOPS:
        group=[r for r in rows if r['top_level']==top];dirs=[r for r in directory_rows if r['directory']==top or r['directory'].startswith(top+'/')]
        idx=ROOT/top/'00_目录索引';idx.mkdir(parents=True,exist_ok=True)
        for name,data,f in [('FILE_INDEX.tsv',group,fields),('DIRECTORY_INDEX.tsv',dirs,list(directory_rows[0]))]:
            p=idx/name;S.U.tsv(p,data,f);generated.append({'path':p.relative_to(ROOT).as_posix(),'sha256':S.U.digest(p),'backup':''})
        title,entry,boundary=THEMES[top]
        moved=[x for x in receipt['moves'] if x['source'].startswith(top+'/')]
        retained=[x for x in plan['candidates'] if x['source'].startswith(top+'/') and not x['decision'].startswith('MOVE')]
        children=[x for x in dirs if len(Path(x['directory']).parts)==2]
        text=f'# {top} — {title}\n\n更新：2026-10-12，R7C3E。{boundary}\n\n'
        text+=f'本轮为本目录的 {len(group):,} 个原有文件建立逐文件用途、项目/阶段、内容索引深度、大小和 SHA-256 清单。实际归档 {len(moved)} 个原件；有明确代码或配套包依赖的候选 {len(retained)} 个保留固定路径。\n\n'
        text+='| 子文件夹 | 原有文件数 | 原有大小 MiB | 用途/保留理由 |\n|---|---:|---:|---|\n'
        for d in children:text+=f'| {md_link(d["directory"],Path(d["directory"]).name)} | {d["files_before_organization"]:,} | {d["bytes_original"]/1048576:.2f} | {d["purpose"]} |\n'
        text+='\n'+md_link(f'{top}/00_目录索引/FILE_INDEX.tsv','逐文件内容与用途清单')+' · '+md_link(f'{top}/00_目录索引/DIRECTORY_INDEX.tsv','全部子文件夹索引')+' · '+md_link('0_admin/navigation/R7C3E_20261012/WORKSPACE_NAVIGATOR.html','全工作区离线检索')+'\n\n'
        text+='原有正文、原图、原数据和冻结 ZIP 内部路径均不改写。历史清单记录当时路径，查现路径使用本轮索引；不是逐项重新运行生物学分析。此处名称 current、PASS 或 COMPLETE 均须按其原阶段读取。\n'
        write(f'{top}/README_DIRECTORY.md',text)
        write(f'{top}/00_目录索引/README.md',f'# {top} 文件与子文件夹索引\n\n'+text.split('\n\n',2)[2]+'\n用途说明文件位于 子文件夹说明/。标准软件/库/Git 内部结构仅以目录清单注释，不在其内插入说明文件。\n')
    # Exact 54-paper identity table, retaining the original judgement as historical.
    papers=[]
    byname=defaultdict(list)
    for r in rows:byname[Path(r['relative_path']).name].append(r['relative_path'])
    for x in plan['candidates']:
        if not x['metadata']:continue
        m=x['metadata'];paths=byname.get(m['file'],[])
        papers.append({**m,'category':Path(x['destination']).parts[3],'original_pdf':x['source'],'current_pdf':x['destination'],'analysis_reports':';'.join(paths),'sha256':x['sha256'],'boundary':'评分/JIF/推荐是原矩阵的历史评价，本轮不重新背书；只分类文件'})
    S.U.tsv(REG/'54_PAPER_METHOD_AND_REUSE_INDEX.tsv',papers,list(papers[0]))
    papertext='# 54 篇参考论文：范式分类与复用入口\n\n54/54 原文按中文题名唯一匹配原人工分析矩阵，PDF 原文件名与哈希保持不变。类别是写作/方法范式，不是质量或阳性分级；旧评分、JIF 和推荐保留历史身份，未重新验证。\n\n'
    for cat,number in sorted(Counter(x['category'] for x in papers).items()):
        papertext+=f'## {cat}（{number} 篇）\n\n| 编号/原文 | 原分析范式 | 历史评语与复用边界 |\n|---|---|---|\n'
        for x in papers:
            if x['category']==cat:papertext+=f'| {md_link(x["current_pdf"],x["id"]+" "+x["title"])} | {x["archetype"]} | {x["verdict"]} |\n'
        papertext+='\n'
    write('8.Reference/00_目录索引/54篇论文_逐篇范式与复用说明.md',papertext)
    # Local asset reuse: disclose source/reporting boundaries rather than rank genes.
    reuse='# 可保留、复用和避免误用的项目资产\n\n'
    reuse+='| 资产 | 价值与未来用途 | 证据边界 |\n|---|---|---|\n'
    entries=[
        ('当前 PBC 投稿候选','5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011','当前主稿、图注、补充、WPS 阅读版与证据限界；现成审阅基础','仍需版本批准、官方表格和门户 proof；尚未投稿'),
        ('当前投稿 ZIP','6_release/R7C3C_2026-10-12','原字节封装与全量审计发布回执','本轮未重打包、未重新推送 GitHub、未生成 DOI'),
        ('PBC-wide 与同输入对照','3_results/04_integration/R7B2A','6,923 筛查范围、642 高信息子集的同输入比较及重分类','642 不是所有比较；输入改变量与方法改变量不能混为一谈'),
        ('源匹配与多信号输入','3_results/03_qtl/R7B1B_v2','286 cell-locus blocks；PF10/PF50 来源与模型敏感性','PF50 不自动是真值；source-aware 不等于无模型限制'),
        ('模拟校准','3_results/05_simulation/R7B1C','486,000 情景与可评价边界，可作可靠性/取舍教材','必须保留无可信集与 false-H4/恢复率之间取舍'),
        ('组织 donor 检测','3_results/05_tissue/R7A2A1_control','5 vs 5 donor-level 检测与相邻来源审计','两靶标 detectability 不构成 PBC 特异富集'),
        ('外部升级来源','5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011','RP v4 的来源、独立性、样本定义与多模态预验收','可访问性不是完成独立疾病复制或染色质介导证明'),
        ('SSc 历史工程','2_code/06_intake/h6_v2_1','P0/H6、variant identity、harmonization、LD QC、fail-closed','SSc 不默认恢复；IL12RB2/SYNGR1 旧预设不迁移'),
        ('MG 证伪记录','3_results/04_integration/R5A2A4','chr18 失败与 source-LD 多信号裁决的工程/决策教材','不把强疾病 locus 或强 eQTL 自动解释为共享机制'),
        ('IgAN bounded 结果','3_results/04_integration/R6A2B0','范围冻结、正控纠偏、bounded expansion 与负面结果','不因重新整理而复活 IgAN 主论文或只摘阳性'),
        ('54 篇写作教材','8.Reference/literature/54_papers','结果顺序、证据闭环、方法与机制叙事参考','历史推荐不代表当前期刊/创新性已验证'),
        ('历史行动记录','7.Report/rounds','完整恢复转向、暂停、失败、模型身份修正及工作决策','以用户最新决定与当前状态为准'),
        ('RP v4','9.Version/PBC_研究计划书_RP_v4_20261011.docx','当前双轨计划及升级 STOP/GO 门','组织整理不推进尚未实际获得的外部证据'),
    ]
    for label,path,value,bound in entries:reuse+=f'| {md_link(path,label)} | {value} | {bound} |\n'
    reuse+='\n环境和 Git 内部对象纳入数量与大小索引，但不列为本研究科学成果。原始个体层 genotype/covariates 和 donor 输入均保持本地，仅根据来源许可另行判断公开方式。\n'
    write('0_admin/navigation/R7C3E_20261012/VALUABLE_ASSETS_AND_REUSE.md',reuse)
    # Portable native lookup for immutable historical path strings.
    lookup='''"""Resolve historical file paths without rewriting frozen evidence rows."""\nimport json\nfrom pathlib import Path\nROOT=Path(r"H:\\SCI2\\YR1")\nPLAN=ROOT/"0_admin/navigation/R7C3E_20261012/organization_plan.json"\ndef resolve_workspace_path(path):\n    raw=str(path).replace("\\\\","/")\n    prefix=ROOT.as_posix()+"/"\n    rel=raw[len(prefix):] if raw.lower().startswith(prefix.lower()) else raw\n    mapping={x["source"].lower():x["destination"] for x in json.loads(PLAN.read_text(encoding="utf-8"))["candidates"] if x["decision"].startswith("MOVE")}\n    return ROOT/mapping.get(rel.lower(),rel)\n'''
    write('2_code/00_workspace_management/R7C3E_20261012/workspace_path_lookup.py',lookup)
    # Full twelve-root asset lookup (default hides standard environment and mirror).
    records=[[r['relative_path'],int(r['size_bytes']),r['project'],r['primary_stage'],r['role'],r.get('title',''),r['sha256'],r['content_status'],r['original_path']] for r in rows]
    data=json.dumps(records,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>YR1 全文件夹分类导航</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font:15px system-ui;margin:28px;background:#f5f7fa;color:#182c42}h1{font-size:25px}input,select,button{padding:8px;margin:4px;border:1px solid #ccd5df;border-radius:5px}input[type=search]{width:40%}table{width:100%;background:white;border-collapse:collapse}th,td{padding:9px;border-bottom:1px solid #e4e9f0;text-align:left;vertical-align:top}a{color:#1260a0}td:first-child{max-width:430px;overflow-wrap:anywhere}.muted{color:#617285}.bar{position:sticky;top:0;background:#f5f7fa;padding:8px 0}.pill{background:#e0ecf8;padding:4px;border-radius:4px}footer{padding:20px}</style><h1>YR1 十二个目录：逐文件内容、项目与用途索引</h1><p>2026-10-12 · 本地离线 · 原有资产索引；新增导航文件在 closing inventory 单独登记。</p><p>原数据包、软件/Git 标准结构、固定分析接口保留。旧 current 名称不代表最新状态。<a href="../../../4_figures/FIGURE_GALLERY.html">Fig1–8 图件入口</a> · <a href="VALUABLE_ASSETS_AND_REUSE.md">成果及复用边界</a> · <a href="OLD_PATH_LOOKUP.tsv">旧路径去向</a></p><div class="bar"><input id="q" type="search" placeholder="文件名、原路径、PBC/MG/IgAN、阶段或内容标题"><select id="top"><option value="">全部十二个目录</option></select><select id="sort"><option value="path">按路径</option><option value="size">按大小降序</option></select><label><input id="system" type="checkbox">显示软件环境与 Git 镜像</label><p id="status"></p><button id="prev">上一页</button><button id="next">下一页</button></div><table><thead><tr><th>文件 / 当前路径</th><th>大小</th><th>项目与阶段</th><th>用途 / 内容深度</th></tr></thead><tbody id="body"></tbody></table><footer>文件层内容索引不等于科学结果重算。源数据内容预览已按来源/个体层公开边界隐藏；不要将本离线索引直接上传公共仓库。</footer><script>const data=DATA;let page=0,filtered=[];const $=x=>document.getElementById(x);const hidden=new Set(['环境/依赖/技能','Git 内部对象','公共仓库镜像']);[...new Set(data.map(r=>r[0].split('/')[0]))].sort().forEach(t=>{let o=document.createElement('option');o.value=t;o.textContent=t;$('top').appendChild(o)});function filter(){let q=$('q').value.toLowerCase(),top=$('top').value;filtered=data.filter(r=>(!top||r[0].startsWith(top+'/'))&&($('system').checked||!hidden.has(r[4]))&&(!q||[r[0],r[2],r[3],r[4],r[5],r[8]].join(' ').toLowerCase().includes(q)));filtered.sort($('sort').value==='size'?(a,b)=>b[1]-a[1]:(a,b)=>a[0].localeCompare(b[0]));page=0;render()}function render(){$('body').replaceChildren();let start=page*100;filtered.slice(start,start+100).forEach(r=>{let tr=document.createElement('tr'),td=document.createElement('td'),a=document.createElement('a');a.href='../../../'+r[0].split('/').map(encodeURIComponent).join('/');a.textContent=r[0];a.title='SHA-256 '+r[6];td.append(a);if(r[8]!==r[0]){let d=document.createElement('div');d.className='muted';d.textContent='原路径：'+r[8];td.append(d)}tr.append(td);for(let t of [(r[1]/1048576).toFixed(3)+' MiB',r[2]+' / '+r[3],r[4]+' / '+r[7]]){let c=document.createElement('td');c.textContent=t;tr.append(c)}$('body').append(tr)});$('status').textContent='匹配 '+filtered.length.toLocaleString()+' / 原有 '+data.length.toLocaleString()+' 文件；第 '+(filtered.length?page+1:0)+' 页，每页 100 条。';$('prev').disabled=page===0;$('next').disabled=(page+1)*100>=filtered.length}['q','top','sort','system'].forEach(id=>$(id).addEventListener(id==='q'?'input':'change',filter));$('prev').onclick=()=>{page--;render()};$('next').onclick=()=>{page++;render()};filter();</script></html>'''.replace('DATA',data,1)
    write('0_admin/navigation/R7C3E_20261012/WORKSPACE_NAVIGATOR.html',doc)
    # Update only mutable navigation; archive the previous bytes.
    nav='# YR1 当前项目与文件入口\n\n更新：2026-10-12，R7C3E 子文件夹分类。主项目 PBC，按 RP v4 双轨计划；未新增生物学分析或投稿。\n\n'
    nav+=md_link('0_admin/navigation/R7C3E_20261012/WORKSPACE_NAVIGATOR.html','十二目录离线文件导航')+' · '+md_link('4_figures/FIGURE_GALLERY.html','Fig1–8 图件导航')+' · '+md_link('0_admin/navigation/R7C3E_20261012/VALUABLE_ASSETS_AND_REUSE.md','有价值成果与未来复用')+'\n\n'
    nav+='| 文件夹 | 职责 | 分类入口 |\n|---|---|---|\n'
    for top in S.TOPS:nav+=f'| {top} | {THEMES[top][0]} | {md_link(top+"/README_DIRECTORY.md","目录说明及全部子文件夹索引")} |\n'
    nav+='| 4_figures | Fig1–6 当前科学主题；Fig7 MG 和 Fig8 IgAN 历史 | '+md_link('4_figures/README.md','逐图分类入口')+' |\n\n'
    nav+='最新主稿：'+md_link('5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/01_Manuscript/R7C3B_npj_Manuscript.docx')+'。当前投稿封装：'+md_link('6_release/R7C3C_2026-10-12/CMM_R7C3C_npj_Submission_Candidate_20261012.zip')+'。当前计划：'+md_link('9.Version/PBC_研究计划书_RP_v4_20261011.docx')+'。\n\n'
    nav+='642 高信息子集不是所有 6,923 比较；分子 QTL 跨资源支持不是独立疾病复制；组织检测不构成 PBC 特异富集。原稿件、图件、补充材料与投稿包保持身份。当前尚未投稿，没有本轮 DOI 或 GitHub 推送。下一科学阶段仍为作者最终版本核对、官方表格、门户 proof 与真实投稿回执。\n\n'
    nav+='本轮记录：'+md_link('7.Report/rounds/R7C3E_20261012/99_R7C3E_十二目录子文件夹分类整理_详细行动记录_20261012.md')+'。旧 current 目录内为兼容历史脚本保留的文件，请查'+md_link('0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json','当前科学状态')+'，不要按文件夹名判断状态。\n'
    write('0_admin/navigation/CURRENT_PROJECT_AND_FILES.md',nav)
    S.dump(REG/'generated_navigation_files.json',generated)
    S.dump(REG/'navigation_state.json',{'status':'GENERATED_PENDING_INDEPENDENT_QA','roots':len(S.TOPS),'classified_original_files':len(rows),'annotated_business_subfolders':detail_count,'all_directory_rows':len(directory_rows),'navigation_files':len(generated),'moved':len(receipt['moves']),'paper_categories':dict(Counter(x['category'] for x in papers)),'public_upload':False})
    print(json.dumps({'roots':len(S.TOPS),'classified_original_files':len(rows),'annotated_business_subfolders':detail_count,'directory_rows':len(directory_rows),'navigation_files':len(generated),'paper_categories':dict(Counter(x['category'] for x in papers))},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
