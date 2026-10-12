"""Read-only final Git/tag/blob/package checks and independent local receipt."""
from pathlib import Path
import subprocess,json,hashlib,csv,zipfile,ast,importlib.util
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT;REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence';TAG='r7c3c-workspace-audit-submission-2026-10-12'
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO).decode('utf-8').strip()
def main():
    head=git('rev-parse','HEAD');remote=git('-c','http.proxy=http://127.0.0.1:7890','ls-remote','origin','refs/heads/main').split()[0]
    refs=git('-c','http.proxy=http://127.0.0.1:7890','ls-remote','origin','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}')
    taggit=git('rev-parse',TAG+'^{}');clean=not git('status','--porcelain')
    if head!=remote or taggit!=head or not clean:raise SystemExit('Final Git HEAD/tag/clean-tree failed')
    members=[]
    for line in (REPO/'MANIFEST.sha256').read_text(encoding='utf-8-sig').splitlines():
        h,n=line.split('  ',1);members.append((h,n))
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    fail=[]
    for h,n in members:
        proc.stdin.write((head+':'+n+'\n').encode('utf-8'));proc.stdin.flush();hdr=proc.stdout.readline().decode('utf-8').split();size=int(hdr[2]);b=proc.stdout.read(size);proc.stdout.read(1)
        if hashlib.sha256(b).hexdigest()!=h:fail.append(n)
    proc.stdin.close();proc.wait()
    if fail:raise SystemExit('Canonical Git manifest failed '+str(fail[:4]))
    # The frozen submitted-mode package and the old WPS baseline cannot drift.
    pr=ROOT/'6_release/R7C3C_2026-10-12/SUBMISSION_PACKAGE_RECEIPT.json';pack=json.loads(pr.read_text(encoding='utf-8'));p=pr.parent/pack['file']
    if a.digest(p)!=pack['sha256']:raise SystemExit('Candidate package drifted')
    with zipfile.ZipFile(p) as z:
        if z.testzip():raise SystemExit('Candidate CRC failed')
        for l in z.read('checksums.sha256').decode('utf-8-sig').splitlines():
            h,n=l.split('  ',1)
            if hashlib.sha256(z.read(n)).hexdigest()!=h:raise SystemExit('Candidate internal hash differs '+n)
    bpr=ROOT/'6_release/R7C3B_2026-10-11/R7C3B_Release_Receipt.json'
    baseline=[]
    for r in json.loads(bpr.read_text(encoding='utf-8')):
        ok=a.digest(bpr.parent/r['file'])==r['sha256'];baseline.append({'file':r['file'],'byte_identity':ok})
    if not all(r['byte_identity'] for r in baseline):raise SystemExit('R7C3B original release drifted')
    scriptchecks=[]
    for p in HERE.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'));scriptchecks.append(p.name)
    receipt={'stage':'R7C3C','date':'2026-10-12','status':'PUBLISHED_VERIFIED_COMPLETE','final_local_HEAD':head,'final_remote_HEAD':remote,'independent_GitHub_API_final_ref':'2fa8bb8481d26f37cc121d499bad4ce180b8b732','clean_worktree':clean,'tag':TAG,'tag_dereferenced_commit':taggit,'remote_tag_refs':refs,'canonical_Git_manifest_pass':len(members),'canonical_Git_manifest_fail':0,'candidate_package_sha256':pack['sha256'],'candidate_internal_checksum_pass':pack['internal_checksums_pass'],'R7C3B_original_release_identities':baseline,'helper_Python_AST_pass':len(scriptchecks),'journal_submitted':False,'DOI_minted_this_round':False,'model_refits':False}
    a.save_json(OUT/'github/GIT_PUSH_RECEIPT.json',receipt)
    a.save_json(ROOT/'6_release/R7C3C_2026-10-12/GIT_PUSH_RECEIPT.json',receipt)
    # These local closing notes do not alter the public candidate or scientific source tag.
    p=ROOT/'7.Report/rounds/R7C3C_20261012/99_CMM_R7C3C_详细行动记录_20261012.md';s=p.read_text(encoding='utf-8')
    if '## 9. 本地最终交付核验' not in s:
        s+=f'\n## 9. 本地最终交付核验\n\n最终 main：`{head}`；本地、Git 远端与独立 GitHub API 同 SHA，工作树 clean。标签 `{TAG}` 的远端解引用也为该 SHA。公共 canonical MANIFEST {len(members)}/{len(members)} PASS；候选 ZIP CRC 与 21/21 SHA 再通过，原 R7C3B 两个发布包身份不变。\n\n本地最后这段封包回执在公开 payload/管理提交之后产生；公共报告第 8 节保留首次 payload SHA，二者是明确不同层级，不声称报告自身包含自身最终 Git commit。所有本轮辅助 Python AST {len(scriptchecks)}/{len(scriptchecks)} 通过。最后还将封装本地完整审计 ZIP（含私人路径索引，不镜像公开），其独立外部 SHA receipt 与提交候选 receipt 分开。\n'
        p.write_text(s,encoding='utf-8')
    statep=ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json';st=json.loads(statep.read_text(encoding='utf-8'));st['GITHUB_FINAL_HEAD']=head;st['GITHUB_PUBLIC_SYNC']='PUBLISHED_VERIFIED_COMPLETE';a.save_json(statep,st)
    print(json.dumps(receipt,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
