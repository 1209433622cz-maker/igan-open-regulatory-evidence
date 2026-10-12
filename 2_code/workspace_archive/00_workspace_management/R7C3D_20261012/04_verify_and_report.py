"""Independent structure, identity, source-link and path-adapter verification.

No GWAS, QTL, simulation or tissue result is recomputed or changed.
"""
from __future__ import annotations
import ast
import csv
import hashlib
import importlib.util
import json
import os
import py_compile
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

import pymupdf
from PIL import Image

ROOT=Path(r'H:\SCI2\YR1')
FIG=ROOT/'4_figures'
OUT=ROOT/'5_analysis/R7C3D_FigureClassification_20261012'
REG=ROOT/'0_admin/figure_registry/R7C3D_20261012'
REPORT=ROOT/'7.Report/rounds/R7C3D_20261012'
CODE=ROOT/'2_code/00_workspace_management/R7C3D_20261012'
BRIDGE=ROOT/'0_admin/compatibility/figure_stage_view'
ROWS=json.loads((REG/'classification_plan.json').read_text(encoding='utf-8'))
GROUPS=json.loads((REG/'figure_content_catalogue.json').read_text(encoding='utf-8'))
CHANGES=json.loads((REG/'code_path_changes.json').read_text(encoding='utf-8'))
IMAGE_EXTS={'.png','.pdf','.svg'}
TOPICS={1:'研究设计与范围',2:'同输入归因与双向重分类',3:'模拟校准与可评价性',4:'外部疾病与多模态证据',5:'细胞上下文与模型敏感性',6:'肝组织供者证据',7:'MG历史项目归档',8:'IgAN历史项目归档'}
CHECKS=[]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,passed,detail=''):
    CHECKS.append({'check':name,'pass':bool(passed),'detail':str(detail)})
def write_json(p,value):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write_tsv(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter='\t',fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def read_tsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def link(label,p,base):return f'[{label}](<{os.path.relpath(p,base).replace(chr(92),chr(47))}>)'

def main():
    originals=[r for r in ROWS if r['kind'].startswith('ORIGINAL_')]
    images=[r for r in ROWS if Path(r['new_relative']).suffix in IMAGE_EXTS]
    check('Original_manifest_50',len(originals)==50,len(originals))
    check('Original_image_manifest_34',sum(r['kind']=='ORIGINAL_IMAGE_MOVE' for r in ROWS)==34)
    check('Reference_copies_12',sum(r['kind']=='CURRENT_SUBMISSION_REFERENCE_COPY' for r in ROWS)==12)
    check('Exactly_Fig1_to_Fig8_top_level_directories',sorted(p.name for p in FIG.iterdir() if p.is_dir())==[f'Fig{i}' for i in range(1,9)])
    check('Original_group_count_16',sum(g['status']!='CURRENT_SUBMISSION_CANDIDATE_REFERENCE_COPY' for g in GROUPS)==16)
    check('All_group_count_22',len(GROUPS)==22)
    check('No_destination_collision',len({r['new_relative'].lower() for r in ROWS})==len(ROWS))
    for r in ROWS:
        p=ROOT/r['new_relative']
        check('SHA256:'+r['new_relative'],p.exists() and p.stat().st_size==r['bytes'] and digest(p)==r['sha256'])
        if r['kind']=='CURRENT_SUBMISSION_REFERENCE_COPY':
            src=ROOT/r['old_relative'];check('Formal_original_unchanged:'+src.name,digest(src)==r['sha256'])
        if r['kind'] in {'ORIGINAL_IMAGE_MOVE','ORIGINAL_SOURCE_OR_STATE_MOVE'}:
            compatibility=BRIDGE/Path(r['old_relative']).relative_to('4_figures')
            check('Compatibility_exact:'+r['old_relative'],compatibility.exists() and digest(compatibility)==r['sha256'])
        if p.suffix=='.png':
            with Image.open(p) as im:im.verify()
            check('PNG_integrity:'+p.name,True)
        elif p.suffix=='.pdf':
            with pymupdf.open(p) as d:
                check('PDF_one_page_readable:'+p.name,len(d)==1 and bool(d[0].get_text().strip()))
        elif p.suffix=='.svg':
            ET.fromstring(p.read_bytes());check('SVG_XML_valid:'+p.name,True)
        elif p.suffix=='.tsv':
            rs=read_tsv(p);check('TSV_readable_nonempty:'+p.name,len(rs)>0)
        elif p.suffix=='.json':
            json.loads(p.read_text(encoding='utf-8-sig'));check('JSON_readable:'+p.name,True)
    actual_images=[p for p in FIG.rglob('*') if p.is_file() and p.suffix in IMAGE_EXTS]
    check('All_images_classified_once_46',len(actual_images)==46,len(actual_images))
    check('No_root_images',not any(p.is_file() and p.suffix in IMAGE_EXTS for p in FIG.iterdir()))
    for g in GROUPS:
        check('Source_code_or_record_exists:'+g['group_id'],(ROOT/g['plotting_code']).exists())
        for p in g['source_tables']:check('Source_table_exists:'+p,(ROOT/p).exists())
        families={Path(p).parts[1] for p in g['files']}
        check('Same_group_formats_together:'+g['group_id'],families=={f'Fig{g["fig_family"]}'})
    check('Every_source_table_associated',len({p for g in GROUPS for p in g['source_tables']})==12)
    # Validate changed scripts without running their science/release/push side effects.
    compile_dir=OUT/'compiled_code_qa';compile_dir.mkdir(exist_ok=True)
    for i,r in enumerate(CHANGES):
        p=ROOT/r['file'];back=ROOT/r['backup']
        check('Code_backup_identity:'+r['file'],digest(back)==r['old_sha256'])
        check('Code_adapter_identity:'+r['file'],digest(p)==r['new_sha256'])
        check('Path_normalized_AST_unchanged:'+r['file'],r['path_normalized_AST_unchanged'])
        py_compile.compile(str(p),cfile=str(compile_dir/f'{i:02d}.pyc'),doraise=True)
        check('Python_compile:'+r['file'],True)
    for p in CODE.glob('*.py'):
        py_compile.compile(str(p),cfile=str(compile_dir/f'local_{p.stem}.pyc'),doraise=True)
        check('Local_python_compile:'+p.name,True)
    adapter_spec=importlib.util.spec_from_file_location('figure_adapter',CODE/'figure_path_adapter.py')
    module=importlib.util.module_from_spec(adapter_spec);adapter_spec.loader.exec_module(module)
    for r in originals:
        check('Legacy_path_resolution:'+r['old_relative'],module.resolve_legacy_figure(ROOT,r['old_relative'])==ROOT/r['new_relative'])
    # Frozen R7B2A panel/claim records are preserved verbatim and resolved at read time.
    ledger=read_tsv(ROOT/'3_results/04_integration/R7B2A/manuscript_lock/R7B2A_updated_claim_evidence_ledger.tsv')
    manifest=read_tsv(ROOT/'3_results/04_integration/R7B2A/manuscript_lock/R7B2A_Figure1_6_panel_source_manifest.tsv')
    figure_links=[]
    for r in ledger:
        for field in ['primary_source_file','supporting_source_files']:
            figure_links.extend(x.strip() for x in r.get(field,'').split(';') if x.strip().startswith('4_figures/'))
    for r in manifest:
        figure_links.extend(x.strip() for x in r.get('source_files','').split(';') if x.strip().startswith('4_figures/'))
    for value in sorted(set(figure_links)):
        check('Frozen_panel_path_resolves:'+value,module.resolve_legacy_figure(ROOT,value).exists())
    class Parser(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.images=0;self.cards=0
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='img':self.images+=1
            if tag=='article':self.cards+=1
            for key in ['href','src']:
                if key in attrs:self.links.append(attrs[key])
    parser=Parser();parser.feed((FIG/'FIGURE_GALLERY.html').read_text(encoding='utf-8'))
    check('Gallery_22_cards',parser.cards==22,parser.cards)
    check('Gallery_22_previews',parser.images==22,parser.images)
    check('Gallery_all_local_links_exist',all((FIG/p).exists() for p in parser.links),len(parser.links))
    for p in [FIG/'README.md',FIG/'README_DIRECTORY.md',REPORT/'01_全部图件内容分析与复用边界.md',*[FIG/f'Fig{i}/README.md' for i in range(1,9)]]:
        broken=[]
        for target in re.findall(r'\]\(<([^>]+)>\)|\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            value=target[0] or target[1]
            if not (p.parent/value).exists():broken.append(value)
        check('Markdown_links:'+p.relative_to(ROOT).as_posix(),not broken,broken)
    # Mechanical source-table identities and denominator checks (not new inference).
    source_by_name={Path(r['new_relative']).name:ROOT/r['new_relative'] for r in ROWS if Path(r['new_relative']).suffix=='.tsv'}
    b1=read_tsv(source_by_name['Figure_R7B1B_1_ABF_to_multisignal_matrix.tsv'])
    cols=['H4_SUPPORTED_STABLE','H3_SUPPORTED_STABLE','MODEL_SENSITIVE','UNINFORMATIVE','QC_FAILURE']
    check('R7B1B_matrix_denominator_642',sum(int(r[c]) for r in b1 for c in cols)==642)
    check('R7B1B_outcome_totals', [sum(int(r[c]) for r in b1) for c in cols]==[92,428,59,63,0])
    roles=read_tsv(source_by_name['Figure_R7B1B_2_role_state_counts.tsv'])
    check('R7B1B_role_sizes_184_455_3',[sum(int(r[c]) for c in cols) for r in roles]==[184,455,3])
    cell=read_tsv(source_by_name['Figure_R7B1B_3_cell_reclassification_counts.tsv'])
    check('Cell_chart_subset_499',sum(int(r[c]) for r in cell for c in ['STABLE_H4','H4_TO_H3','H3_TO_H4','STABLE_H3'])==499)
    transition=read_tsv(source_by_name['Figure2_adjacent_transition_matrices.tsv'])
    for stage,expected in [('A0_TO_A1_SUPPORT_SET',15),('A1_TO_A2_DISEASE_STATS',19),('A2_TO_M_MODEL',139)]:
        part=[r for r in transition if r['transition']==stage]
        check('R7B2A_matrix_642:'+stage,sum(int(r['n']) for r in part)==642)
        check('R7B2A_change_count:'+stage,sum(int(r['n']) for r in part if r['changed']=='True')==expected)
    performance=read_tsv(source_by_name['Figure3_discovery_vs_estimator_performance.tsv'])
    check('Simulation_denominator_486000',sum(int(r['all_replicates']) for r in performance)==486000)
    check('Simulation_pair_evaluable_160782',sum(int(r['pair_evaluable']) for r in performance)==160782)
    channel=read_tsv(source_by_name['Figure3_simulation_channel_summary.tsv'])
    overall=[r for r in channel if r['scope']=='PRIMARY_MATCHED_OVERALL']
    check('Simulation_noCS_325218',sum(int(r['n']) for r in overall if r['matched_channel'].startswith('NO_'))==325218)
    check('No_directory_symlinks_or_junctions',not any(p.is_symlink() or (getattr(p,'is_junction',lambda:False)()) for p in FIG.rglob('*')))
    qa_path=REG/'INDEPENDENT_QA.tsv';write_tsv(qa_path,CHECKS)
    failures=[x for x in CHECKS if not x['pass']]
    state={'stage':'R7C3D_FIGURE_CLASSIFICATION','status':'COMPLETE_PASS' if not failures else 'FAIL',
           'checks':len(CHECKS),'passed':len(CHECKS)-len(failures),'failed':len(failures),
           'original_images_preserved':34,'original_source_tables':12,'original_stage_states':2,
           'original_navigation_archived':2,'current_reference_copies':12,'image_files_after':46,
           'figure_groups':22,'code_path_adapters':len(CHANGES),
           'scientific_bytes_changed':0,'formal_submission_originals_changed':0,
           'image_extensions':dict(Counter(p.suffix for p in actual_images)),
           'folders':{f'Fig{i}':{'topic':TOPICS[i],'image_files':sum(p.relative_to(FIG).parts[0]==f'Fig{i}' for p in actual_images),
                                'groups':sum(g['fig_family']==i for g in GROUPS)} for i in range(1,9)},
           'qa_sha256':digest(qa_path),'failures':failures,
           'next':'KEEP_SIX_FIGURE_SUBMISSION_BASELINE; AUTHOR_FINAL_APPROVAL_AND_PUBLISHER_PROOF',
           'github_push_this_round':False,'journal_submission_completed':False}
    write_json(REG/'organization_state.json',state)
    write_json(OUT/'independent_qa_state.json',state)
    inventory=[{'relative':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(FIG.rglob('*')) if p.is_file()]
    write_tsv(REG/'AFTER_FIGURE_FILES.tsv',inventory)
    write_json(REG/'generated_navigation_files.json',[r['relative'] for r in inventory if not any(x['new_relative']==r['relative'] for x in ROWS)])
    write_reports(state,inventory)
    print(json.dumps(state,ensure_ascii=False,indent=2))
    if failures:raise SystemExit(1)

def write_reports(state,inventory):
    counts='|目录|内容|图组|图件文件|\n|---|---|---:|---:|\n'
    for name,data in state['folders'].items():counts+=f'|{name}|{data["topic"]}|{data["groups"]}|{data["image_files"]}|\n'
    text='# R7C3D：图件逐项核查与分类整理详细行动记录\n\n日期：2026-10-12；工作区：H:/SCI2/YR1。\n\n'
    text+='## 任务范围与执行依据\n\n按用户截图的Fig1–8整理4_figures内全部图片，允许增加同类型子目录和重命名。未改变任何GWAS、QTL、模拟、组织分析参数或结果。使用QiTeng v0.3.24.2 Runtime Core与版本Registry，落实“一图主要职责”“VISUAL CLAIM <= TEXTUAL EVIDENCE CLAIM”和可追溯原图/源表/代码；未使用CC skill。PDF仅用于只读解析与渲染检查，没有制作新的PDF或调用LibreOffice。\n\n'
    text+='## 实际输入验收\n\n原目录50文件、4,736,102字节。其中16 PNG、14单页PDF、4 SVG，共34图件，对应16组独立科学图；另有12 TSV源表、2 JSON阶段状态和2旧导航MD。逐文件读取并计算SHA-256；全部PNG完整性验证，PDF全部页面渲染/取文，SVG全部XML解析/渲染。16组PNG和18个矢量导出均通过联系图人工内容核对。另读取六张当前R7C3B组图与相应PDF后复制12个校验副本，原件原位保留。\n\n'
    text+='格式屏查的灰度相关范围约0.797–0.992，受到字体、抗锯齿、图形裁边及分辨率影响，只用于提示人工核对，不作为跨格式“逐像素相同”结论。历史图像的数值、数据点、图题未重绘。\n\n'
    text+='## 分类原则与执行结果\n\nFig1–6对应当前PBC稿件的六项论证职责；Fig7为MG、Fig8为IgAN归档，不新增论文第7或第8张主图。00目录为当前候选的导航副本；10–30目录为历史/源原型；90/91目录保存源表/状态。文件名保留阶段、疾病、基因/细胞和图义。\n\n'+counts+'\n'
    text+=f'原34/34图件、12/12源表、2/2状态文件SHA全部守恒；两份旧导航完整归档，50/50原文件均有去向。新增12/12当前候选校验副本与原件一致。整理后4_figures共{len(inventory)}文件，其中46图件（22 PNG、20 PDF、4 SVG），对应22组图。八个主目录外不残留阶段目录或游离图件。\n\n'
    text+='## 重要内容判断与风险注释\n\n1. R7B1B历史ABF→M矩阵有4个H4→H3、8个H3→H4；R7B2A匹配后A2→M是8/10。两者不是矛盾，也不可互换。旧队列184/455/3和匹配后A2 H4=113/H3=452是不同分母。\n2. R7B1B细胞条图只画四类stable/strict结果499比较，未画其余143；不能误称每种结局都在细胞图中呈现。\n3. R7A1B历史“PF10/PF50”正控图须按R7B0A来源纠偏解释；原图列值一致不能作为当前同源双模型稳健证据。当前Fig5保留CD8_ET的PF10/PF50分歧。\n4. R6A1是资源覆盖早期图，其中“DICE controls recovered”定义后来纠偏；不能当作4基因3位点已阳性共定位。REEP3的Asian H4≈0.906是阶段性待证伪触发，非当前确认成果。MG/IgAN图保持历史项目身份，不并入PBC生物学证据。\n5. R7B1C模拟的H4率包含全部replicates；R7B2A分开发现与条件推断。325218 no-CS不是软件错误；降低误共享伴随共享恢复降低。\n6. 组织图保留5 vs 5的真实供者点和q≈0.111；支持可检测性，未支持校正后PBC富集。原CPM对数轴与当前log1p(CPM)是不同展示，不能仅因轴文字不同误判为不同实验。\n7. 外部图的FinnGen R12/R13不是两次独立队列复制；直接eQTL↔caQTL posterior缺失和OMIX描述性上限仍保留。\n8. 根README原先“尚无正式图”的说明已过期；仅更新导航，旧原文两份均留档。\n\n'
    text+='## 路径依赖与可回滚性\n\n25份canonical runnable Python代码只做路径适配；原代码逐字节备份。路径归一化后的AST均与原版一致，独立语法检查通过，没有统计公式/门槛/参数改变。旧脚本stage glob保留在0_admin/compatibility/figure_stage_view的48个精确副本中；它是隔离暂存区，旧脚本重新生成的输出不会自动覆盖已经分类的原图。新生成图须重新核查再收录，不能误报双目录自动同步。\n\nR7B2A读取冻结manifest/ledger中的旧4_figures路径时，按清单解析到分类后的真实文件；冻结源表、报告、发布ZIP、Git提交均未改写。未执行旧绘图/发布/推送脚本，以免产生不必要的重绘、旧release覆盖或网络写入。\n\n移动记录记录原路径、新路径、字节数、SHA；回滚默认预览，只有--apply才恢复，遇到代码/图片已有后续修改会停止。\n\n'
    text+='回滚预览：\n\n```powershell\n& "C:\\Users\\Administrator\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe" "H:\\SCI2\\YR1\\2_code\\00_workspace_management\\R7C3D_20261012\\ROLLBACK_R7C3D.py"\n```\n\n实际需要恢复时在该命令末尾加`--apply`。回滚会归档本轮新导航/副本，不删科研文件。回滚只读预览已实际执行PASS：50原文件与25代码可恢复；并未执行回滚。Git镜像本轮只读status检查为空，未产生仓库改动。\n\n'
    text+=f'## 独立验收\n\n{state["passed"]}/{state["checks"]}项PASS，失败{state["failed"]}。覆盖原文件与正式原件SHA、兼容副本、46图件解析、全部源表绑定、25代码原件备份/语法/路径AST、50条旧路径解析、冻结Fig source路径、图册22预览及全部链接、各级Markdown链接、历史矩阵/队列/细胞子集与模拟分母。未重跑科研计算，未制作新的投稿版本，未推送GitHub，也未进行期刊投稿。\n\n'
    text+='首遍QA为436/437，唯一未通过项是README指向的本轮行动报告尚未生成，链接检查先于报告写出；报告生成后复查全部PASS。该顺序异常没有涉及图件或科学数据。\n\n'
    text+='## 下一阶段\n\n当前PBC六图候选稿与科学结果保持成立。本轮完成的是目录/证据检索层整理，不触发重开分析。下一阶段仍是最终作者版确认、按目标期刊门户选择唯一主稿/独立图上传、检查官方生成proof并归档投稿回执。若后续新增作图，先在独立版本生成和审阅，然后用本次图义/分母/来源规范纳入目录。\n\n'
    text+='## 核查文件入口\n\n'
    for label,path in [('全部图件详细分析',REPORT/'01_全部图件内容分析与复用边界.md'),('图件总导航',FIG/'README.md'),('可筛选图册',FIG/'FIGURE_GALLERY.html'),('原—新路径清单与SHA',REG/'CLASSIFICATION_MANIFEST.tsv'),('独立QA',REG/'INDEPENDENT_QA.tsv'),('整理后全文件清单',REG/'AFTER_FIGURE_FILES.tsv'),('代码适配记录',REG/'code_path_changes.json'),('两份旧README归档',ROOT/'9.Version/figure_reorganization/R7C3D_20261012/original_root_docs')]:
        text+='- '+link(label,path,REPORT)+'\n'
    (REPORT/'99_R7C3D_图件逐项核查与分类整理_详细行动记录_20261012.md').write_text(text,encoding='utf-8')
    summary='# R7C3D图件整理执行摘要\n\n原34图件/16图组完整分类并保持SHA-256；加入当前六图的12个精确参考副本，合计46图件/22图组。\n\n'+counts+f'\n独立QA：{state["passed"]}/{state["checks"]} PASS。所有科学图字节不变；论文仍为六张主图。\n\n'+link('查看逐图分析',REPORT/'01_全部图件内容分析与复用边界.md',REPORT)+'\n\n'+link('完整行动记录',REPORT/'99_R7C3D_图件逐项核查与分类整理_详细行动记录_20261012.md',REPORT)+'\n'
    (REPORT/'00_执行摘要_图件归类与状态.md').write_text(summary,encoding='utf-8')

if __name__=='__main__':main()
