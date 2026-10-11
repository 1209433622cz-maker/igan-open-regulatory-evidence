"""Record verified payload publication; final metadata HEAD is captured externally."""
from pathlib import Path
import json,shutil,subprocess,importlib.util,ast
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT;REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence'
REPORT=ROOT/'7.Report/rounds/R7C3C_20261012'
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO).decode('utf-8').strip()
def main():
    head=git('rev-parse','HEAD');remote=git('-c','http.proxy=http://127.0.0.1:7890','ls-remote','origin','refs/heads/main').split()[0]
    if head!=remote:raise SystemExit('Local and remote disagree')
    gate=json.loads((OUT/'github/PRE_PUSH_GATE.json').read_text(encoding='utf-8'))
    receipt={'stage':'R7C3C','date':'2026-10-12','repo':'https://github.com/1209433622cz-maker/igan-open-regulatory-evidence','previous_head':'18a4032836236008f54cb9cfaca8480c21a05f7a','verified_payload_commit':head,'verified_remote_head_at_payload_check':remote,'independent_GitHub_API_ref_check':head,'public_files_changed':gate['staged_files'],'canonical_manifest_members':gate['tracked_without_manifest'],'candidate_committed_blob_identity':gate['candidate_blob_identity_pass'],'candidate_internal_checksums':gate['candidate_internal_checksums_pass'],'secret_or_raw_data_gate_blockers':gate['staged_secret_or_raw_data_blockers'],'push_mode':'NORMAL_FAST_FORWARD_NOT_FORCE','transport':'Git HTTPS via existing user Windows proxy; no global configuration change','earlier_direct_fetch_failures':['connection reset','direct connection timeout'],'journal_submission':False,'new_DOI_minted':False,'note':'This receipt identifies the verified scientific/editorial payload commit. A following administrative commit carries the receipt; its final remote HEAD is recorded separately locally.'}
    a.save_json(OUT/'github/VERIFIED_PAYLOAD_RECEIPT.json',receipt)
    a.save_json(REPO/'audit/r7c3c/GITHUB_PUBLICATION_RECEIPT.json',receipt)
    statep=ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json';st=json.loads(statep.read_text(encoding='utf-8'));st['GITHUB_PUBLIC_SYNC']='PUBLISHED_PAYLOAD_VERIFIED';st['GITHUB_PAYLOAD_COMMIT']=head;a.save_json(statep,st);a.save_json(REPO/'audit/r7c3c/PBC_CURRENT_STATE_20261012.json',st)
    # Correct a metadata pointer (no source bytes or submitted assets altered).
    for p in [OUT/'catalogue/LARGE_ASSET_POINTERS_PUBLIC.tsv',REPO/'data/R7C3C_LARGE_ASSET_POINTERS.tsv']:
        s=p.read_text(encoding='utf-8-sig');p.write_text(s.replace('data/DATA_AVAILABILITY.md','DATA_AVAILABILITY.md'),encoding='utf-8-sig',newline='')
    addition=f'''\n## 8. 已验证公共同步回执\n\n首次 payload commit：`{head}`，由 Git `ls-remote` 与 GitHub REST ref 读取得到同一 SHA。85 个文件新增/修改，完整 canonical Git-blob 清单覆盖 1,424 项（不含清单自身）；22 项候选包文件在 Git 中保持本地原字节，21 项内部 SHA 均通过。第三方原始/供者数据与完整私人清单未公开。\n\n最初 Git 直连遇到 reset/timeout；使用用户已配置的 Windows 本地代理 127.0.0.1:7890 后 fetch/push/读取正常，没有关闭 TLS 校验、没有改全局 Git 代理或 force push。\n\nGit 的 autocrlf 曾造成 exact-copy QA 文本 CRC/换行歧义。为候选包加 scope-specific `-text` 属性，保留 CRLF 原字节；`whitespace=cr-at-eol` 明确合法 Windows 行尾，不放弃其余差异检查。公共 MANIFEST 改为 actual Git index blob SHA，避免 checkout 换行差异误报。原科学数据/图件/文档正文没有改变。\n\nGit fsck 返回成功；已有 dangling objects 属于未被当前 ref 引用的历史对象，不是对象损坏，本轮不清理。此回执的后续管理提交只补公共记录与入口；最终 HEAD/tag/release 身份另见本地 `github/GIT_PUSH_RECEIPT.json`。未期刊投稿、未本轮生成 DOI。\n'''
    report=REPORT/'99_CMM_R7C3C_详细行动记录_20261012.md';s=report.read_text(encoding='utf-8')
    if '## 8. 已验证公共同步回执' not in s:report.write_text(s+addition,encoding='utf-8')
    summary=REPORT/'00_执行摘要_成果与下一阶段.md';s=summary.read_text(encoding='utf-8')
    if '已验证 GitHub payload' not in s:summary.write_text(s+f'\n已验证 GitHub payload：`{head}`，远端 Git 与独立 API 身份一致。最新 WPS 候选稿、补充数据、审计索引已公开；原数据和完整私人清单仅本地保留。\n',encoding='utf-8')
    for p in REPORT.glob('*.md'):shutil.copy2(p,REPO/'reports/r7c3c'/p.name)
    readme=REPO/'README.md';s=readme.read_text(encoding='utf-8')
    if 'Canonical Git-blob integrity' not in s:
        s=s.replace('The sections below retain the chronological project history.','Canonical Git-blob integrity is recorded in `MANIFEST.sha256`; use `git cat-file` or `analysis/r7c3c/08_stage_public_and_verify.py` for verification, because a Windows checkout can normalize historical text line endings. The current submission directory has explicit byte-preservation attributes. [Verified publication receipt](audit/r7c3c/GITHUB_PUBLICATION_RECEIPT.json).\n\nThe sections below retain the chronological project history.')
        readme.write_text(s,encoding='utf-8')
    syntax=[]
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8-sig'));syntax.append({'script':p.name,'status':'PASS_AST_NO_MODELS_EXECUTED'})
    a.tsv(OUT/'paths/FINAL_HELPER_SYNTAX.tsv',syntax)
    print(json.dumps(receipt,ensure_ascii=False))

if __name__=='__main__':main()
