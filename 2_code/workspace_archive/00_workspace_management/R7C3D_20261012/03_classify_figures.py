"""Content-reviewed figure classification with hash-conserving, reversible moves.

Default is plan-only; --apply executes the previously reviewed fixed plan.
Historical plotting scripts use an isolated compatibility staging area.
Scientific assets, manuscript originals, and frozen releases are never edited.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(r'H:\SCI2\YR1').resolve()
FIG = ROOT/'4_figures'
OUT = ROOT/'5_analysis/R7C3D_FigureClassification_20261012'
REG = ROOT/'0_admin/figure_registry/R7C3D_20261012'
BACK = ROOT/'9.Version/figure_reorganization/R7C3D_20261012'
BRIDGE = ROOT/'0_admin/compatibility/figure_stage_view'
REPORT = ROOT/'7.Report/rounds/R7C3D_20261012'
FORMAL = ROOT/'5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/02_Figures'
IMAGE_EXTS = {'.png','.pdf','.svg'}
TOPICS = {
 1:'PBC研究设计与范围', 2:'PBC同输入归因与双向重分类',
 3:'PBC模拟校准与可评价性', 4:'PBC外部疾病与多模态证据',
 5:'PBC细胞上下文与模型敏感性', 6:'PBC肝组织供者证据',
 7:'MG历史项目归档', 8:'IgAN历史项目归档'}

# Reviewed after all 16 PNG plots and all 18 vector equivalents were rendered.
# Fields: old stage/stem, Fig family, subfolder, new descriptive stem, role,
#         panels, quantitative anchors, limitations, reuse, plotting source.
SPECS = [
 ('R5A2A4','Figure_R5A2A4_NK_R_ZCCHC2_adjudication',7,'10_MG_chr18_表达路线失败',
  '01_R5A2A4_MG_chr18_NK_R_ZCCHC2_源LD与多信号终裁','ROBUSTNESS_DIAGNOSTIC',
  'A 区域边际eQTL；B disease lead与QTL top的残差化LD；C 强制条件分析；D SuSiE PIP。',
  'source q≈0.383；lead-top r²=0.0124；条件P≈0.0177；max PIP≈0.0296；95% CS=0。',
  'MG而非PBC；未发现可信QTL共享信号。不能把无CS当作全疾病位点无遗传效应。',
  '保留源LD、条件分析、弱QTL停止规则的负例与工程历史；不纳入当前PBC主图。',
  '2_code/06_intake/mg_r5a2a4/plot_r5a2a4_adjudication.py'),
 ('R5A2B','Figure_R5A2B_chr5_bounded_adjudication',7,'20_MG_chr5_有边界竞争终止',
  '01_R5A2B_MG_chr5_TNIP1_基因竞争与先验敏感性','STATISTICAL_EVIDENCE',
  'A EOMG关联；B NK/TNIP1区域eQTL；C 八基因H3-H4散点；D p12敏感性。',
  'rs6861227疾病P≈1.053e-9；NK/TNIP1 top P≈1.70e-7，lead P≈0.00631；图中无H4过0.8。',
  '强疾病关联或强QTL不等于共享信号；这里只是已终止MG表达介导路线的冻结终裁。',
  '可复用bounded gene competition、先验敏感性图法；不扩大MG候选池。',
  '2_code/06_intake/mg_r5a2b/09_plot_chr5_bounded_adjudication.py'),
 ('R6A1','Figure_R6A1_preflight_overview',8,'10_IgAN_早期数据预验收',
  '01_R6A1_IgAN_位点数据可用性_历史正控定义待纠偏','STUDY_DESIGN',
  'A 24个非HLA位点跨QTL/serum IgA/肾组织的资源覆盖；B 初始GO门计数。',
  '24 published loci、22 OneK、24 TenK、22 cross-resource、9 serum IgA、3 benchmark。',
  '覆盖/存在不是疾病共定位。图中文字“DICE controls recovered”属于早期定义，后续R6A2A0已纠偏，不能当作恢复了4基因3位点阳性。',
  '保留数据可用性矩阵模板与阶段纠错记录；只作IgAN归档。',
  '2_code/06_intake/igan_r6a1/08_plot_r6a1_preflight.py'),
 ('R6A2A1','Figure_R6A2A1_benchmark_and_ZMIZ1_replication',8,'20_IgAN_正控与ZMIZ1跨资源',
  '01_R6A2A1_IgAN_ZMIZ1_NK_正控与细胞特异复制','STATISTICAL_EVIDENCE',
  'A combined IgAN与OneK预定正控H3/H4；B ZMIZ1在祖源及TenK NK亚群中对照。',
  'ZMIZ1：OneK combined H4≈0.931、European≈0.789、Asian≈0.967；TenK NK≈0.998，NK CD56bright≈0.019。',
  'European未达到默认0.8；不同NK亚群不能合并成一致阳性；跨QTL资源不是新增独立疾病GWAS复制。',
  '保留正控定义、细胞匹配和跨祖源边界的教学/方法资产。',
  '2_code/06_intake/igan_r6a2a/09_plot_r6a2a1.py'),
 ('R6A2B0','R6A2B0_decision_summary',8,'30_IgAN_八位点扩展与REEP3待证伪',
  '01_R6A2B0_IgAN_八位点筛查与REEP3祖源分歧','ROBUSTNESS_DIAGNOSTIC',
  'A 八个预定locus的最佳combined H4；B REEP3/CD4_NC三祖源H4。',
  '八位点combined最高TNFSF12/13≈0.391；REEP3 combined≈0.076、European≈0.015、Asian≈0.906。',
  'Asian高H4是当时的后续证伪触发，并非最终跨资源成功；后续R6A2C冻结结论优先。',
  '保留有界扩展、祖源差异触发与停止规则图；不作为当前PBC证据。',
  '2_code/06_intake/igan_r6a2b0/11_plot_r6a2b0_summary.py'),
 ('R7A1B','R7A1B_PBC_signal_gate_summary',5,'20_历史正控门_来源身份需按R7B0A解释',
  '01_R7A1B_PBC_IL12RB2_FCRL3_INAVA_历史模型门','ROBUSTNESS_DIAGNOSTIC',
  '左：九比较ABF smoke；右：七比较PF/L配置的最佳signal-pair H4。',
  'IL12RB2/NK≈0.998；FCRL3/B_IN≈0.994；CD8_ET≈0.004；INAVA弱/无信息。',
  '图中的历史PF10/PF50列不能代表当前同源双模型。R7B0A记录历史PF10字节身份未恢复，后续current-release de novo结果才是当前依据。',
  '保留从早期双基因机制路线转向来源/模型可靠性论文的历史证据；不上传为当前Fig5。',
  '2_code/06_intake/r7a1b/11_build_r7a1b_summary_assets.py'),
 ('R7A2A1','R7A2A1_PBC_vs_control_target_panel',6,'10_五比五供者原始CPM展示',
  '01_R7A2A1_PBC_vs_Control_FCRL3_B_IL12RB2_NK_供者散点','STATISTICAL_EVIDENCE',
  '两个target-lineage面板；每点一供者；CPM对数坐标，中位数与IQR。',
  '5 PBC vs 5 controls；FCRL3 log1p差=-0.786，P=0.1111；IL12RB2差=+0.330，P=0.0635；两者q=0.1111。',
  '此图是log轴原始CPM；当前Fig6为log1p(CPM)展示。数值/供者来源相同，画法不同。未支持校正后PBC特异富集或组织介导。',
  '当前组织结论的可追溯前身；讲清donor-level统计与阴性边界。',
  '2_code/06_intake/r7a2/07_plot_R7A2A1_tissue_gate.py'),
 ('R7B1B_v2','Figure_R7B1B_1_bidirectional_reclassification',2,'20_历史筛查到多信号_R7B1B',
  '01_R7B1B_642_ABF到多信号_历史双向转移矩阵','STATISTICAL_EVIDENCE',
  '四类历史ABF行到五类PF10多信号列；每格计数及行百分比。',
  '行总数112/72/455/3；历史stable H4=78，H4→H3=4，H3→H4=8，stable H3=409；列和92/428/59/63/0。',
  '尚未采用R7B2A同输入A2对照；不能把4/8直接写成当前8/10。642是高信息子集，不是全部6923比较。',
  '保留对照设计演进与历史四类筛查来源；当期主图使用00目录当前参考版。',
  '2_code/06_intake/r7b1/15_build_r7b1b_v2_figures.py'),
 ('R7B1B_v2','Figure_R7B1B_2_cohort_separated_outcomes',2,'20_历史筛查到多信号_R7B1B',
  '02_R7B1B_184_455_3_分队列多信号结局','STATISTICAL_EVIDENCE',
  '按184 primary、455 H3 rescue、3 borderline分开堆叠PF10结局。',
  'Primary 83/19/52/30；H3队列8/409/7/31；borderline 1/0/0/2；总计642。',
  '角色是预冻结筛查队列，不是匹配后A2 H4=113/H3=452分母；不同层级数字不能互换。',
  '保留对称证伪设计与队列分开报告逻辑，可用于补充说明。',
  '2_code/06_intake/r7b1/15_build_r7b1b_v2_figures.py'),
 ('R7B1B_v2','Figure_R7B1B_3_cell_context_reclassification',5,'10_历史细胞重分类分布_R7B1B',
  '01_R7B1B_14细胞_历史稳定与严格重分类分布','STATISTICAL_EVIDENCE',
  '十四细胞按stable H4/H3、H4→H3、H3→H4四类水平条形分布。',
  '只展示历史strict/stable四类499比较；NK H3→H4=4，CD4_NC=2，Mono_NC=2；不展示全部143其它结局。',
  '跨细胞计数不是样本量独立复制；未对每个cell universe做新的多重检验；阶段历史定义。',
  '可作为cell-context异质性图法与旧版补充图，不替代当前模型特异Fig5。',
  '2_code/06_intake/r7b1/15_build_r7b1b_v2_figures.py'),
 ('R7B1C','Figure_R7B1C_1_scenario_H4_decisions',3,'20_六场景H4决策率_R7B1C',
  '01_R7B1C_六场景_ABF与多信号_无条件H4决策率','STATISTICAL_EVIDENCE',
  'S1–S6真值已知场景；ABF与source-matched多信号H4决策率柱形对照。',
  'S2 distinct：20.50%→16.00%；S5 distinct：4.32%→1.12%；S1 shared：65.94%→54.12%。',
  '这是全部replicates无条件决策率；没有pair时不构成可评价的模型分类。共享恢复同时下降，不能宣称普遍优越。',
  '模拟trade-off原型；与R7B2A可评价性图及当前Fig3并读。',
  '2_code/06_intake/r7b1c/07_build_r7b1c_figures.py'),
 ('R7B1C','Figure_R7B1C_2_LD_stratified_decisions',3,'21_LD相关度分层_R7B1C',
  '01_R7B1C_六场景_因果变异r2分层决策率','ROBUSTNESS_DIAGNOSTIC',
  '六小面板；r²=0.2/0.5/0.8；两方法无条件H4率曲线。',
  'S2 distinct在r²升高时误共享上升；复杂共享S4/S6在高r²下H4恢复很低。',
  '只涵盖冻结模拟模板/参数网格；不等于真实人群所有LD情形或经验错误率。',
  '补充稳健性与模拟场景解释，可引用具体source TSV。',
  '2_code/06_intake/r7b1c/07_build_r7b1c_figures.py'),
 ('R7B1C','Figure_R7B1C_3_same_locus_LD_mismatch',3,'22_同位点LD错配模拟_R7B1C',
  '01_R7B1C_S6_PF10到PF50_LD错配与H4扰动','ROBUSTNESS_DIAGNOSTIC',
  '左matched/mismatch的MAF分层H4率；右mean absolute best-H4变化。',
  'MAF0.4/r²0.2：H4 0.4828 vs 0.4803，mean|ΔH4|≈0.005665；仅9个MAF×r²汇总。',
  '同位点PF10→PF50的有边界错配压力测试，不是跨祖源LD基准，也不是所有LD不匹配损害的估计。',
  '保留低成本同位点错配反例；主类别按模拟而非真实数据Fig5。',
  '2_code/06_intake/r7b1c/07_build_r7b1c_figures.py'),
 ('R7B1C','Figure_R7B1C_4_credible_set_coverage',3,'23_可信集全因果覆盖_R7B1C',
  '01_R7B1C_疾病与QTL_95pctCS全因果覆盖','ROBUSTNESS_DIAGNOSTIC',
  '疾病和QTL在六场景的95% credible-set all-causal coverage曲线。',
  'Disease S1/S2≈0.95、复杂场景≈0.40；QTL S1–S3≈0.56、S4–S6≈0.05。',
  '名义95% credible set不是观察到95% all-causal覆盖；all-causal判据和拟合可评价性须保留。',
  '补充可信集发现瓶颈与power界定；配合当前Fig3分母分析。',
  '2_code/06_intake/r7b1c/07_build_r7b1c_figures.py'),
 ('R7B2A','R7B2A_Figure2_attribution_prototype',2,'10_同输入三段归因_R7B2A',
  '01_R7B2A_642_支持集_疾病统计_推断流程转移','STATISTICAL_EVIDENCE',
  '三热图：A0→A1支持集、A1→A2疾病统计、A2→M全推断流程。',
  '三个矩阵各642；状态改变15/19/139；同输入strict H4→H3=8、H3→H4=10、stable H4=79、H3=413。',
  '15+19+139不能简单相加为唯一受影响比较；真实数据无因果真值；A2→M不是只改变因果变异个数的纯对照。',
  '当前Fig2源原型/源表，适合核查同输入分母与18条严格方向变化。',
  '2_code/06_intake/r7b2a/05_build_r7b2a_manuscript_lock_assets.py'),
 ('R7B2A','R7B2A_Figure3_simulation_channels_prototype',3,'10_发现通道与条件分母_R7B2A',
  '01_R7B2A_模拟发现通道_可评价率与条件H4','ROBUSTNESS_DIAGNOSTIC',
  '左六场景pair/no-CS通道占比；右pair-evaluable、H4 unconditional和H4 conditional-on-pair。',
  '486000迭代；160782 pair-evaluable=33.08%；325218 no-CS；场景可评价率13.29%–59.79%。',
  'no-CS不等于软件错误；conditional H4不等于总体检出率；不遗漏共享场景的恢复代价。',
  '当前Fig3的重要源原型；补充方法与审稿分母问答。',
  '2_code/06_intake/r7b2a/05_build_r7b2a_manuscript_lock_assets.py'),
]

CURRENT = {
 1:('研究范围与模型身份门','STUDY_DESIGN','流程、队列柱图、642结局及身份诊断。','6923→5460→642；184/455/3；92/428/59/63；14模型身份行；2568诊断单元。','注册screen是项目内冻结范围，不是外部preregistration；多信号结论仅对642子集。'),
 2:('同输入归因与双向重分类','STATISTICAL_EVIDENCE','支持匹配、三段归因、状态矩阵、A2分母、PF敏感性及signal-pair并存。','15/19/139；H4=113、H3=452；8/10严格转移；491/4/25 PF结局。','不称真实数据的错误修正率；32个H4比较可同时有distinct pair。'),
 3:('模拟校准与可评价性分母','ROBUSTNESS_DIAGNOSTIC','通道占比、发现/推断分母、方法trade-off及no-CS原因。','486000；160782 pair-evaluable；325218 no-CS；0记录技术错误。','跨场景误共享与共享恢复同时呈代价；未证明通用算法优越。'),
 4:('外部疾病与染色质证据边界','MULTILAYER_EVIDENCE','FinnGen R12/R13可信集、R13×OneK、27基因CASCADE覆盖和染色质三角。','17/17 R13 CS variants进入R12 CS；1175共有变异；27→22→1；disease-eQTL/caQTL H4≈0.970。','R12/R13不是两个独立队列；未证实参与者完全无重叠；直接eQTL-caQTL posterior缺失；OMIX仅描述。'),
 5:('细胞上下文与PF10_PF50敏感性','ROBUSTNESS_DIAGNOSTIC','B-cell sharing、跨QTL资源、CD8_ET A0/A1/A2/PF10/PF50对照及claim boundary。','FCRL3 B_IN≈0.9937、B_MEM≈0.9910、TenK≈0.9916；CD8_ET PF10≈0.003636 vs PF50≈0.991894。','独立分子QTL资源复用同一疾病GWAS；PF50高H4不证明恢复真值；FinnGen未返回不等于有power阴性复制。'),
 6:('肝组织供者表达与非显著边界','STATISTICAL_EVIDENCE','FCRL3-B、IL12RB2-NK log1p(CPM)供者点/箱线及组织证据上限。','每组5人；两gene每组5/5检测；P≈0.111/0.063；两者BH q≈0.111。','可检测性支持；校正后疾病富集未支持；不能推断组织介导或新治疗机制。')}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def safe(p):
    p = p.resolve()
    if not p.is_relative_to(ROOT): raise RuntimeError(f'Outside workspace: {p}')
    return p

def dump(path, obj):
    safe(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def tsv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)

def mdlink(label,p,base):
    import os
    return f'[{label}](<{os.path.relpath(p,base).replace(chr(92),chr(47))}>)'

def plan():
    baseline=json.loads((OUT/'before_inventory.json').read_text(encoding='utf-8'))
    specmap={(s[0],s[1]):s for s in SPECS}
    rows=[]
    for rec in baseline:
        old=ROOT/rec['old_relative'];suffix=old.suffix.lower()
        if suffix in IMAGE_EXTS:
            spec=specmap[(old.parent.name,old.stem)]
            new=FIG/f'Fig{spec[2]}'/spec[3]/(spec[4]+suffix)
            kind='ORIGINAL_IMAGE_MOVE';family=spec[2];group=old.parent.name+'/'+old.stem
        elif old.parent==FIG:
            new=BACK/'original_root_docs'/old.name
            kind='ORIGINAL_NAVIGATION_ARCHIVE';family=0;group='root_navigation'
        else:
            stage=old.relative_to(FIG).parts[0]
            family=3 if stage=='R7B1C' or old.name.startswith('Figure3_') else 5 if old.name.startswith('Figure_R7B1B_3_') else 2
            sub='91_阶段状态' if suffix=='.json' else '90_源数据'
            new=FIG/f'Fig{family}'/sub/stage/old.name
            kind='ORIGINAL_SOURCE_OR_STATE_MOVE';group=stage
        rows.append({'old_relative':rec['old_relative'],'new_relative':new.relative_to(ROOT).as_posix(),
                     'kind':kind,'fig_family':family,'group':group,'bytes':rec['bytes'],'sha256':rec['sha256']})
    sources=json.loads((OUT/'submission_reference_sources.json').read_text(encoding='utf-8'))
    for r in sources:
        n=r['figure'];old=ROOT/r['source'];suffix=old.suffix.lower()
        new=FIG/f'Fig{n}'/'00_当前投稿候选_R7C3B_校验副本'/f'R7C3B_Fig{n}_{CURRENT[n][0]}{suffix}'
        rows.append({'old_relative':r['source'],'new_relative':new.relative_to(ROOT).as_posix(),
                     'kind':'CURRENT_SUBMISSION_REFERENCE_COPY','fig_family':n,'group':f'R7C3B/Figure_{n}',
                     'bytes':r['bytes'],'sha256':r['sha256']})
    if len({r['new_relative'].lower() for r in rows})!=len(rows):raise RuntimeError('Destination collision')
    if sum(r['kind']=='ORIGINAL_IMAGE_MOVE' for r in rows)!=34:raise RuntimeError('Expected all 34 original images')
    for r in rows:
        src=safe(ROOT/r['old_relative']);dst=safe(ROOT/r['new_relative'])
        if dst.exists():raise RuntimeError(f'Destination exists: {dst}')
        if digest(src)!=r['sha256']:raise RuntimeError(f'Source changed: {src}')
    dump(REG/'classification_plan.json',rows);tsv(REG/'CLASSIFICATION_MANIFEST.tsv',rows)
    groups=[]
    for s in SPECS:
        gs=[r for r in rows if r['group']==s[0]+'/'+s[1]]
        groups.append({'group_id':s[0]+'/'+s[1], 'fig_family':s[2], 'topic':TOPICS[s[2]],
                       'status':'HISTORICAL_PROTOTYPE' if s[2]<=6 else 'ARCHIVED_DIFFERENT_DISEASE',
                       'role':s[5],'panels':s[6],'anchors':s[7],'boundary':s[8], 'reuse':s[9],
                       'plotting_code':s[10],'files':[r['new_relative'] for r in gs]})
    for n,c in CURRENT.items():
        gs=[r for r in rows if r['group']==f'R7C3B/Figure_{n}']
        groups.append({'group_id':f'R7C3B/Figure_{n}','fig_family':n,'topic':TOPICS[n],
                       'status':'CURRENT_SUBMISSION_CANDIDATE_REFERENCE_COPY','role':c[1],
                       'panels':c[2],'anchors':c[3],'boundary':c[4],
                       'reuse':'当前阅读/核对入口；门户上传仍以5_manuscript中的正式文件为准。',
                       'plotting_code':'5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/07_Reports/02_npj_Production_Source_Conservation_and_Upload_Map.md',
                       'files':[r['new_relative'] for r in gs]})
    for g in groups:
        stage,stem=g['group_id'].split('/',1)
        number=re.search(r'(?:Figure_R7B1[BC]_)(\d)_',stem)
        if stage=='R7B2A':
            prefix='Figure2_' if 'Figure2' in stem else 'Figure3_'
        elif number:
            prefix=f'Figure_{stage.replace("_v2", "")}_{number.group(1)}_'
        else:
            prefix=None
        g['source_tables']=[r['new_relative'] for r in rows if r['kind']=='ORIGINAL_SOURCE_OR_STATE_MOVE'
                            and Path(r['new_relative']).suffix=='.tsv'
                            and Path(r['old_relative']).parts[1]==stage
                            and prefix and Path(r['old_relative']).name.startswith(prefix)]
    groups.sort(key=lambda g:(g['fig_family'],0 if g['status'].startswith('CURRENT') else 1,g['files'][0]))
    dump(REG/'figure_content_catalogue.json',groups)
    return rows,groups

def code_changes():
    stages=sorted({s[0] for s in SPECS},key=len,reverse=True)
    replacements=[(f'4_figures/{s}',f'0_admin/compatibility/figure_stage_view/{s}') for s in stages]
    planned=[]
    # Only runnable canonical project code; ignore this round's scripts, archives,
    # repositories, third-party runtimes and generated bytecode.
    for base in [ROOT/'2_code/06_intake',ROOT/'2_code/09_release',ROOT/'2_code/11_manuscript']:
        for p in base.rglob('*.py'):
            old=p.read_text(encoding='utf-8-sig');new=old
            for src,dst in replacements:new=new.replace(src,dst)
            for s in stages:
                new=new.replace(f'"4_figures" / "{s}"',f'"0_admin/compatibility/figure_stage_view" / "{s}"')
            if p.name=='06_independent_qa_r7b2a.py':
                new=new.replace('import json\n','import json\nimport runpy\n',1)
                anchor='ROOT = Path(r"H:\\SCI2\\YR1")\n'
                loader='resolve_legacy_figure = runpy.run_path(str(ROOT / "2_code/00_workspace_management/R7C3D_20261012/figure_path_adapter.py"))["resolve_legacy_figure"]\n'
                if anchor not in new:raise RuntimeError('QA root anchor changed')
                new=new.replace(anchor,anchor+loader,1)
                new=new.replace('(ROOT / item).exists()', 'resolve_legacy_figure(ROOT, item).exists()')
                new=new.replace('candidate = ROOT / item if item.startswith', 'candidate = resolve_legacy_figure(ROOT, item) if item.startswith')
            if new!=old:
                ast.parse(new)
                class NormalizePaths(ast.NodeTransformer):
                    def visit_Constant(self,node):
                        if isinstance(node.value,str):
                            node.value=node.value.replace('0_admin/compatibility/figure_stage_view','4_figures')
                        return node
                    def visit_Import(self,node):
                        if len(node.names)==1 and node.names[0].name=='runpy':return None
                        return node
                    def visit_Assign(self,node):
                        if any(isinstance(t,ast.Name) and t.id=='resolve_legacy_figure' for t in node.targets):return None
                        return self.generic_visit(node)
                    def visit_Call(self,node):
                        if isinstance(node.func,ast.Name) and node.func.id=='resolve_legacy_figure':
                            return ast.BinOp(left=node.args[0],op=ast.Div(),right=node.args[1])
                        return self.generic_visit(node)
                before=ast.dump(NormalizePaths().visit(ast.parse(old)),include_attributes=False)
                after=ast.dump(NormalizePaths().visit(ast.parse(new)),include_attributes=False)
                if before!=after:raise RuntimeError(f'Non-path AST change rejected: {p}')
                planned.append((p,old,new))
    return planned

def apply(rows,groups):
    # All sources, destinations and code parse before the first move.
    changes=code_changes()
    dump(REG/'code_change_plan.json',[{'file':p.relative_to(ROOT).as_posix(),
         'old_sha256':digest(p),'reason':'Only figure-path adapter; no statistical computation changes.'} for p,o,n in changes])
    # Isolated exact stage copies preserve old filenames/glob contracts. Subsequent
    # legacy reruns write here, never automatically overwrite classified originals.
    for r in rows:
        if r['kind'] not in {'ORIGINAL_IMAGE_MOVE','ORIGINAL_SOURCE_OR_STATE_MOVE'}:continue
        rel=Path(r['old_relative']).relative_to('4_figures')
        dst=safe(BRIDGE/rel)
        if dst.exists():raise RuntimeError(f'Compatibility destination exists: {dst}')
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/r['old_relative'],dst)
        if digest(dst)!=r['sha256']:raise RuntimeError('Compatibility copy hash mismatch')
    moved=[]
    for r in rows:
        src=safe(ROOT/r['old_relative']);dst=safe(ROOT/r['new_relative'])
        dst.parent.mkdir(parents=True,exist_ok=True)
        if r['kind']=='CURRENT_SUBMISSION_REFERENCE_COPY':shutil.copy2(src,dst)
        else:shutil.move(str(src),str(dst))
        if digest(dst)!=r['sha256']:raise RuntimeError(f'Post-operation hash mismatch: {dst}')
        moved.append(r);dump(REG/'executed_operations.json',moved)
    code_rows=[]
    for p,old,new in changes:
        backup=safe(BACK/'original_path_dependent_code'/p.relative_to(ROOT))
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
        raw=p.read_bytes();bom=raw.startswith(b'\xef\xbb\xbf');newline='\r\n' if b'\r\n' in raw else '\n'
        data=new.replace('\r\n','\n').replace('\n',newline).encode('utf-8')
        if bom:data=b'\xef\xbb\xbf'+data
        p.write_bytes(data)
        code_rows.append({'file':p.relative_to(ROOT).as_posix(),'backup':backup.relative_to(ROOT).as_posix(),
                          'old_sha256':digest(backup),'new_sha256':digest(p),
                          'path_normalized_AST_unchanged':True})
    dump(REG/'code_path_changes.json',code_rows)
    # Empty-directory removal only, never recursive deletion.
    for d in sorted(FIG.rglob('*'),key=lambda p:len(p.parts),reverse=True):
        if d.is_dir() and d.name not in {f'Fig{i}' for i in range(1,9)} and not any(d.iterdir()):
            safe(d)
            if not d.is_relative_to(FIG):raise RuntimeError('Directory escape')
            d.rmdir()
    generate_navigation(rows,groups)
    dump(REG/'organization_state.json',{'status':'APPLIED_PENDING_INDEPENDENT_VERIFICATION',
          'original_files_preserved':50,'original_images':34,'original_figure_groups':16,
          'current_reference_copies':12,'all_images_after':46,'all_figure_groups_after':22,
          'code_path_adapters':len(code_rows),'scientific_bytes_changed':0,
          'formal_manuscript_originals_changed':0})
    print(json.dumps({'moved_original_files':50,'current_copies':12,'code_path_adapters':len(code_rows)},ensure_ascii=False))

def generate_navigation(rows,groups):
    intro='''整理日期：2026-10-12。按实际图义、疾病、阶段、分母及证据上限分类。\n\nFig1–Fig6沿当前PBC六图论证顺序；Fig7、Fig8是MG、IgAN历史归档，**不是论文第7、第8张主图**。\n\n`00_当前投稿候选_R7C3B_校验副本`中的PDF/PNG与稿件目录逐字节一致，仅供统一导航。投稿权威原件仍位于 `5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/02_Figures`。这些副本不构成新版作者批准或已投稿。\n\n同组PNG/PDF/SVG保留为栅格预览/矢量导出，不删同图多格式。历史原型不能因归入Fig目录而升级为当前论文结论。\n\n'''
    table='|目录|主题|图组数|图件文件数|\n|---|---|---:|---:|\n'
    for i in range(1,9):
        table+=f'|[Fig{i}](Fig{i}/README.md)|{TOPICS[i]}|{sum(g["fig_family"]==i for g in groups)}|{sum(r["fig_family"]==i and Path(r["new_relative"]).suffix.lower() in IMAGE_EXTS for r in rows)}|\n'
    (FIG/'README.md').write_text('# 图件总导航：Fig1–Fig8\n\n'+intro+table+'\n[逐图详细分析](../7.Report/rounds/R7C3D_20261012/01_全部图件内容分析与复用边界.md)\n\n[原路径—新路径与SHA-256清单](../0_admin/figure_registry/R7C3D_20261012/CLASSIFICATION_MANIFEST.tsv)\n\n[可筛选图册](FIGURE_GALLERY.html)\n',encoding='utf-8')
    (FIG/'README_DIRECTORY.md').write_text('# 4_figures目录说明\n\n已改为Fig1–Fig8分类结构。完整主题、各阶段边界、当前与历史版本见 [README](README.md)。\n\n本次原34图件、12源表、2状态文件全部移入对应Fig子目录；旧两份根导航已归档。原始统计图字节未修改。\n\n旧脚本的路径适配、兼容暂存与回滚详见 [行动记录](../7.Report/rounds/R7C3D_20261012/99_R7C3D_图件逐项核查与分类整理_详细行动记录_20261012.md)。\n',encoding='utf-8')
    paragraphs=[]
    for i in range(1,9):
        base=FIG/f'Fig{i}';texts=[f'# Fig{i}：{TOPICS[i]}\n\n'+intro]
        for g in sorted([g for g in groups if g['fig_family']==i],key=lambda x:0 if x['status'].startswith('CURRENT') else 1):
            block=f'## {g["group_id"]}\n\n状态：`{g["status"]}`；主职责：`{g["role"]}`。\n\n内容：{g["panels"]}\n\n数值锚点：{g["anchors"]}\n\n证据边界：**{g["boundary"]}**\n\n后续价值：{g["reuse"]}\n\n'
            block+='生成代码/来源记录：'+mdlink('来源',ROOT/g['plotting_code'],base)+'\n\n'
            block+='文件：'+' · '.join(mdlink(Path(p).suffix[1:].upper(),ROOT/p,base) for p in g['files'])+'\n\n'
            if g['source_tables']:
                block+='配套源表：'+' · '.join(mdlink(Path(p).name,ROOT/p,base) for p in g['source_tables'])+'\n\n'
            texts.append(block);paragraphs.append(f'## Fig{i} / {g["group_id"]}\n\n'+block.split('\n\n',1)[1])
        source_rows=[r for r in rows if r['fig_family']==i and r['kind']=='ORIGINAL_SOURCE_OR_STATE_MOVE']
        if source_rows:
            texts.append('## 配套源表与状态\n\n'+ '\n'.join('- '+mdlink(Path(r['new_relative']).name,ROOT/r['new_relative'],base) for r in source_rows)+'\n\nR7B1B三图的共同状态保存在Fig2，细胞图与其源表在Fig5；状态文件原文保持不变。\n')
        (base/'README.md').write_text(''.join(texts),encoding='utf-8')
    REPORT.mkdir(parents=True,exist_ok=True)
    analysis='# 全部图件内容分析与复用边界\n\n'+intro
    for i in range(1,9):
        for g in [g for g in groups if g['fig_family']==i]:
            analysis+=f'## Fig{i} / {g["group_id"]}\n\n状态：`{g["status"]}`；图义：`{g["role"]}`。\n\n{g["panels"]}\n\n数值：{g["anchors"]}\n\n边界：**{g["boundary"]}**\n\n复用：{g["reuse"]}\n\n代码/来源：'+mdlink('查看来源',ROOT/g['plotting_code'],REPORT)+'\n\n'
            analysis+='图件：'+' · '.join(mdlink(Path(p).name,ROOT/p,REPORT) for p in g['files'])+'\n\n'
            if g['source_tables']:
                analysis+='配套源表：'+' · '.join(mdlink(Path(p).name,ROOT/p,REPORT) for p in g['source_tables'])+'\n\n'
    (REPORT/'01_全部图件内容分析与复用边界.md').write_text(analysis,encoding='utf-8')
    # Offline gallery; no external requests or CDN. Filter/search affects display only.
    cards=[]
    for g in groups:
        png=next(p for p in g['files'] if p.endswith('.png'))
        rel=Path(png).relative_to('4_figures').as_posix()
        link=' · '.join(f'<a href="{html.escape(Path(p).relative_to("4_figures").as_posix())}">{Path(p).suffix[1:].upper()}</a>' for p in g['files'])
        search=html.escape(' '.join([g['group_id'],str(g['fig_family']),g['topic'],g['panels'],g['boundary']]),quote=True)
        cards.append(f'<article data-fig="Fig{g["fig_family"]}" data-search="{search}"><h2>Fig{g["fig_family"]} · {html.escape(g["group_id"])}</h2><span>{html.escape(g["status"])}</span><a href="{html.escape(rel)}"><img loading="lazy" src="{html.escape(rel)}"></a><p>{html.escape(g["panels"])}</p><p><b>数值：</b>{html.escape(g["anchors"])}</p><p class="boundary">{html.escape(g["boundary"])}</p><p>{link}</p></article>')
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Fig1–8 图件目录</title><style>body{font:16px system-ui;margin:24px;color:#26334b;background:#f5f7fa}header{position:sticky;top:0;background:#f5f7fa;padding:12px;z-index:1}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(540px,1fr));gap:20px}article{padding:20px;border:1px solid #dbe0e8;background:white;border-radius:10px}img{width:100%;height:330px;object-fit:contain}h2{font-size:20px}span{font-size:12px;color:#667}.boundary{border-left:3px solid #b56c45;padding:8px;background:#fff5ee}input,select{font-size:16px;padding:8px;min-width:220px}a{color:#246383}article[hidden]{display:none}</style><header><h1>Fig1–Fig8 图件内容导航</h1><p>46 个图件文件，22 组图。Fig1–6：PBC当前候选与历史原型；Fig7：MG归档；Fig8：IgAN归档。当前论文六张主图。副本不改变稿件批准/投稿状态。</p><input id="q" placeholder="搜索基因、阶段或图义"><select id="f"><option value="">全部目录</option>'''
    doc+=''.join(f'<option>Fig{i}</option>' for i in range(1,9))+'</select></header><main>'+''.join(cards)+'</main>'
    doc+='''<script>const q=document.getElementById('q'),f=document.getElementById('f');function filter(){const s=q.value.toLowerCase();document.querySelectorAll('article').forEach(a=>a.hidden=(f.value&&a.dataset.fig!==f.value)||!a.dataset.search.toLowerCase().includes(s));}q.addEventListener('input',filter);f.addEventListener('change',filter);</script></html>'''
    (FIG/'FIGURE_GALLERY.html').write_text(doc,encoding='utf-8')
    (BRIDGE/'README.md').write_text('# 历史绘图脚本兼容暂存\n\n这些48文件是整理前stage目录的精确副本，保留原命名与glob契约，SHA身份已验证。它们不增加科学证据。分类后的图件权威导航在4_figures/Fig1–8；正式投稿权威仍在5_manuscript。\n\n旧脚本新运行写本暂存区，不会自动覆盖已分类原图；重新生成的图须单独版本核查后才能正式收录。不要把暂存更新当作分类目录自动同步。\n\n旧路径定位优先用0_admin/figure_registry/R7C3D_20261012/classification_plan.json的映射；冻结报告、hash表、ZIP和Git提交未改写。\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    rows,groups=plan()
    if args.apply:apply(rows,groups)
    else:print(json.dumps({'plan_files':len(rows),'originals':50,'original_images':34,'current_reference_copies':12,'groups':len(groups),'planned_code_adapters':len(code_changes())},ensure_ascii=False))
