"""Close the round with an explicit self-excluded complete workspace manifest."""
from pathlib import Path
from collections import Counter
import csv, json, os, stat, re, time, py_compile, subprocess, importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scan',HERE/'01_scan_and_plan.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
ROOT,OUT,REG,BACK=S.ROOT,S.OUT,S.REG,S.BACK
REPORT=ROOT/'7.Report/rounds/R7C3E_20261012/99_R7C3E_十二目录子文件夹分类整理_详细行动记录_20261012.md'

def link(rel,label=None):return f'[{label or Path(rel).name}](<{(ROOT/rel).as_posix()}>)'

def main():
    if (OUT/'CLOSING_STATE.json').exists():raise SystemExit('Round already closed; preserve closing manifest identity.')
    qa=json.loads((REG/'INDEPENDENT_QA_STATE.json').read_text(encoding='utf-8'))
    dry=json.loads((REG/'ROLLBACK_DRY_RUN.json').read_text(encoding='utf-8'))
    nav=json.loads((REG/'navigation_state.json').read_text(encoding='utf-8'))
    receipt=json.loads((REG/'execution_receipt.json').read_text(encoding='utf-8'))
    if qa['status']!='PASS' or dry['status']!='PASS_DRY_RUN':raise SystemExit('Finalization requires independent QA and rollback dry-run PASS')
    before=list(csv.DictReader((OUT/'BEFORE_FILES.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    fresh=list(csv.DictReader((OUT/'FRESH_AFTER_HASH_CONSERVATION.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    after_by_path={r['current_path']:r for r in fresh}
    moved={r['source']:r['destination'] for r in receipt['moves']}
    original_by_current={moved.get(r['relative_path'],r['relative_path']):r for r in before}
    manuscript='6_release/R7C3C_2026-10-12/CMM_R7C3C_npj_Submission_Candidate_20261012.zip'
    expected='befaf850f4fcfab9671b01fcab023a1571f228d87bd076f99ffad72053123f3c'
    if S.U.digest(ROOT/manuscript)!=expected:raise SystemExit('Submission bundle identity mismatch')
    supplemental=[]
    for name,ok in [('INDEPENDENT_QA_PASS',qa['failed']==0),('ROLLBACK_DRY_RUN',not dry['errors']),('CURRENT_SUBMISSION_ORIGINAL_SHA256',True)]:supplemental.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    for i,p in enumerate([HERE/'ROLLBACK_R7C3E.py',HERE/'05_finalize_and_report.py',HERE/'workspace_path_lookup.py']):
        out=OUT/'code_compile'/f'final_{i}_{p.name}.pyc';py_compile.compile(str(p),cfile=str(out),doraise=True)
        supplemental.append({'check':'FINAL_TOOL_COMPILE:'+p.name,'status':'PASS'})
    node=Path(r'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe')
    check=subprocess.run([str(node),'--check',str(OUT/'navigation_script_check.js')],capture_output=True,text=True)
    supplemental.append({'check':'OFFLINE_NAVIGATOR_JAVASCRIPT_SYNTAX','status':'PASS' if check.returncode==0 else 'FAIL'})
    smoke=json.loads((OUT/'NAVIGATION_RUNTIME_SMOKE.json').read_text(encoding='utf-8'))
    supplemental.extend(smoke['results'])
    if any(x['status']!='PASS' for x in supplemental):raise SystemExit('Supplemental check failed')
    S.U.tsv(REG/'FINAL_SUPPLEMENTAL_QA.tsv',supplemental,['check','status'])
    # Draft is retained before final closure; this is newly generated audit prose.
    draft=OUT/'report_drafts/99_action_record_before_final_QA.md';draft.parent.mkdir(parents=True,exist_ok=True)
    if not draft.exists():draft.write_bytes(REPORT.read_bytes())
    text=REPORT.read_text(encoding='utf-8')
    text=text.replace('本记录的最终 QA 数字将在独立核验完成后补齐；此版本为执行记录，不能据此认为已通过最终核验。',f'最终状态：`COMPLETE_PASS`。独立 QA：**{qa["passed"]:,}/{qa["checks"]:,} PASS**。全部 {qa["preexisting_user_files_checked"]:,} 个整理前用户原件已重新读取完整 SHA-256；当前稿件、投稿包和 Fig1–8 保持原身份。')
    text=text.replace('独立核验进行中。将检查全部原件的完整哈希、移动源路径消失/目标身份、保留接口、ZIP CRC、外部哈希配对、所有目录索引、导航链接、Python 编译、动态输入读取、旧路径解析及当前稿件/图件身份。',f'独立核验完成：{qa["passed"]:,}/{qa["checks"]:,} PASS，失败 0。核验包括全部原件的完整哈希、移动源路径消失/目标身份、73 个保留接口、移动 ZIP CRC、外部哈希配对、十二目录索引、导航链接、Python 编译、5 个对照 donor 的缓存 schema、旧路径解析和当前稿件/图件身份。\n\n首次独立验证在完成原件哈希读取后因环境未装 `bs4` 而停止，没有输出最终 PASS。采用现有 `lxml` 完成独立 HTML DOM 验证，并增加哈希检查点保存，完整重跑后获得上述有效结果。没有为本轮目录任务额外安装依赖或执行旧 writer。')
    text=text.replace('回滚工具将默认只检查并输出计划；显式 apply 才反向搬迁。', '回滚工具默认只检查并输出计划；显式 apply 才反向搬迁。本轮默认 dry-run 已 PASS：143 个移动原件、713 项导航和 1 个代码适配均无冲突。未执行回滚。')
    text=text.replace('记录关闭状态：`INDEPENDENT_QA_RUNNING`。','记录关闭状态：`COMPLETE_PASS_NO_SCIENTIFIC_REANALYSIS_NO_PUBLIC_PUSH`。')
    moved_counts=Counter(x['source'].split('/')[0] for x in receipt['moves'])
    text+='\n## 12. 十二目录的精确原有资产与移动数量\n\n| 目录 | 原清单文件数 | 原清单 bytes | 实际移动文件数 |\n|---|---:|---:|---:|\n'
    for top in S.TOPS:
        rows=[r for r in before if r['top_level']==top]
        text+=f'| {top} | {len(rows):,} | {sum(int(r["size_bytes"]) for r in rows):,} | {moved_counts[top]} |\n'
    text+='\n2_code 的原清单含本轮新建的一个审计工具，故十二目录原有资产索引为 35,371 条，而实际整理前用户资产为 35,370 条；加上独立保持身份的 71 个 Fig1–8 文件，完整原件守恒核对为 35,441 个。标准软件目录和原始数据已经具有规范用途分类，保持原接口，通过索引完整注释，并非强行把所有文件重新搬一次。\n'
    text+='\n## 13. 额外查找、公开边界与明确限制\n\n原 54-paper 矩阵中列出的独立报告文件名，未在现行物理文件清单找到同名原件；另对 9.Version 的 37 个 ZIP 中央目录进行名称检索，未发现这些 P01–P54 命名的 MD 成员。未据此推断历史文件永久丢失，也未生成冒充原件的单篇分析。原矩阵、综合母版和当前 54/54 PDF 均保留；检索结果已保存。\n\n713 项导航文件只用于本地。其文件名/大小/来源接口可能涉及 donor/covariate 信息，不能把全量索引直接推到公共 GitHub。与先前已批准公共发布的精简成果包是不同对象。\n\n历史 frozen 文本里的旧绝对路径和相对链接保持原字节；本轮提供去向表与解析器，并未宣称所有历史正文链接都已原位改写。现行新导航链接已独立核查。\n'
    text+=f'\n补充验收 {len(supplemental)}/{len(supplemental)} PASS，包含收尾工具编译、现行投稿包固定 SHA-256、离线页面 JS 语法和 9 项 DOM 行为检查。后者核对原路径搜索、当前稿件、六类论文入口、分页、环境隐藏和大小排序；它不是浏览器逐页视觉验收。\n'
    text+='\n## 14. 当前投稿包身份与下一阶段\n\n当前原字节投稿包：'+link(manuscript)+'。\n\nSHA-256：`'+expected+'`。本轮实际读字节复核一致，没有新增 ZIP 或替换作者稿件。\n\n下一阶段维持 `R7C4_AUTHOR_FINAL_VERSION_CONFIRMATION_REPORTING_FORMS_PORTAL_PROOF_AND_SUBMISSION_RECEIPT`。如果先处理目录查找，使用全局离线导航与每目录的索引，不重新打开旧项目筛选。\n'
    REPORT.write_text(text,encoding='utf-8')
    summary='# R7C3E 执行摘要：十二目录子文件夹分类完成\n\n2026-10-12。按 RP v4 保留 PBC 主线。本轮完成目录治理，没有新科学分析、GitHub 推送、DOI 或投稿。\n\n'
    summary+=f'十二目录原有资产索引 {nav["classified_original_files"]:,} 条；实际移动 {qa["moved_files"]} 个原件，{qa["moved_bytes"]:,} bytes；660 份业务子文件夹说明；54 篇参考论文分为六类。独立原件检查 {qa["preexisting_user_files_checked"]:,} 个，QA {qa["passed"]:,}/{qa["checks"]:,} PASS。\n\n'
    summary+='规范数据/软件包、固定阶段接口和当前投稿稿件维持原路径。73 个被引用候选保留原位并明确注释。旧 current 标签不再当作最新状态。\n\n'
    summary+=link('0_admin/navigation/R7C3E_20261012/WORKSPACE_NAVIGATOR.html','全工作区离线检索')+' · '+link('0_admin/navigation/CURRENT_PROJECT_AND_FILES.md','当前项目与十二目录入口')+' · '+link('0_admin/navigation/R7C3E_20261012/VALUABLE_ASSETS_AND_REUSE.md','成果和未来复用')+' · '+link(REPORT.relative_to(ROOT).as_posix(),'完整行动记录')+'\n\n下一阶段仍为最终版本核对、官方表格、门户 proof 与投稿回执。\n'
    (REPORT.parent/'00_R7C3E_执行摘要_十二目录分类.md').write_text(summary,encoding='utf-8')
    nav['status']='COMPLETE_PASS';nav['independent_QA_passed']=qa['passed'];nav['independent_QA_total']=qa['checks'];nav['rollback_dry_run']='PASS';nav['scientific_source_data_changed']=False;nav['scientific_reanalysis_executed']=False;S.dump(REG/'navigation_state.json',nav)
    # Count and classify every CURRENT physical file, including all this-round audit outputs.
    # Two self-referential closing outputs are explicitly excluded and declared below.
    excluded={str(OUT/'ALL_CURRENT_FILES_CLOSING.tsv').lower(),str(OUT/'CLOSING_STATE.json').lower()}
    closing=[];links=[];fresh_new=0;cache_used=0
    for base,dirs,files in os.walk(S.U.extended(ROOT),followlinks=False):
        base=Path(str(base)[4:])
        for d in list(dirs):
            p=base/d
            if os.lstat(S.U.extended(p)).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                dirs.remove(d);links.append(p.relative_to(ROOT).as_posix())
        for name in files:
            p=base/name
            if str(p).lower() in excluded:continue
            rel=p.relative_to(ROOT).as_posix();st=os.stat(S.U.extended(p));old=original_by_current.get(rel);a=after_by_path.get(rel)
            if old and a and int(old['mtime_ns'])==st.st_mtime_ns and int(a['size_bytes'])==st.st_size:
                h=a['after_sha256'];basis='THIS_ROUND_FRESH_AFTER_QA_HASH_MATCHED_ORIGINAL_MTIME_CURRENT_SIZE';cache_used+=1
            else:h=S.U.digest(p);basis='FRESH_CLOSING_NEW_OR_CHANGED';fresh_new+=1
            r={'relative_path':rel,'top_level':rel.split('/')[0],'size_bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':h,'hash_basis':basis}
            r['role'],r['handling'],r['future_use']=S.role(rel);r['project'],r['primary_stage']=S.project(rel)
            if rel.startswith('4_figures/'):
                r['role']='既有 Fig1–8 图件/来源/导航（本轮保持身份）';r['project']='MG 历史' if '/Fig7/' in rel else 'IgAN 历史' if '/Fig8/' in rel else 'PBC 与图件治理'
            if old and old['sha256']==h:
                r['content_status']=old.get('content_status','');r['title']=old.get('title','');r['content_detail']=old.get('content_detail','')
            elif rel.endswith(('.tsv','.html','.js')) and st.st_size>5*1024*1024:
                r['content_status']='GENERATED_INDEX_SCHEMA_AND_IDENTITY';r['title']='本地索引/核验脚本；完整字节哈希已记录';r['content_detail']='large generated local index; no scientific recomputation'
            else:
                s=S.U.summarize(p,rel,st.st_size);r.update({k:s.get(k,'') for k in ['content_status','title','content_detail']})
            r['publication_policy']=S.U.classify(rel)[1];closing.append(r)
    closing.sort(key=lambda r:r['relative_path'].lower())
    S.U.tsv(OUT/'ALL_CURRENT_FILES_CLOSING.tsv',closing,list(closing[0]))
    closing_state={'status':'COMPLETE_PASS','date':'2026-10-12','current_physical_files_in_snapshot':len(closing),'current_bytes_in_snapshot':sum(r['size_bytes'] for r in closing),'roots':dict(Counter(r['top_level'] for r in closing)),'fresh_closing_new_or_changed_hashes':fresh_new,'this_round_after_QA_hashes_reused_with_size_mtime':cache_used,'skipped_preexisting_directory_links':links,'excluded_self_referential_outputs':[str(OUT/'ALL_CURRENT_FILES_CLOSING.tsv'),str(OUT/'CLOSING_STATE.json')],'original_user_files_freshly_verified':qa['preexisting_user_files_checked'],'independent_QA':f'{qa["passed"]}/{qa["checks"]} PASS','moves':qa['moved_files'],'navigation_files':nav['navigation_files'],'business_subfolder_annotations':nav['annotated_business_subfolders'],'public_push':False,'new_scientific_analysis':False,'submission_completed':False,'next':'R7C4_AUTHOR_FINAL_VERSION_CONFIRMATION_REPORTING_FORMS_PORTAL_PROOF_AND_SUBMISSION_RECEIPT'}
    S.dump(OUT/'CLOSING_STATE.json',closing_state)
    print(json.dumps(closing_state,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
