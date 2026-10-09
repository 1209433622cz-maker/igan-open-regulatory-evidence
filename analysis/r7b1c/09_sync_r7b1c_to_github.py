#!/usr/bin/env python3
"""Publish lightweight R7B1C assets, with an authenticated API fallback."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT=Path(r"H:\SCI2\YR1")
REPO=ROOT/"github/igan-open-regulatory-evidence"
CODE=ROOT/"2_code/06_intake/r7b1c"
AUDIT=ROOT/"3_results/00_audit/R7B1C"
AGG=ROOT/"3_results/05_simulation/R7B1C/aggregate"
FIG=ROOT/"4_figures/R7B1C"
REPORT=ROOT/"7.Report/rounds/R7B1C"
PROTOCOL=ROOT/"0_admin/protocols/R7B1C"
API_REPO="repos/1209433622cz-maker/igan-open-regulatory-evidence"


def run(*args:str,check:bool=True,input_bytes:bytes|None=None)->subprocess.CompletedProcess:
    p=subprocess.run(args,cwd=REPO,input=input_bytes,capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"failed {args}:\n{p.stdout.decode('utf-8','replace')}\n{p.stderr.decode('utf-8','replace')}")
    return p


def text(*args:str)->str:
    return run(*args).stdout.decode("utf-8","replace").strip()


def gh(method:str,endpoint:str,payload:dict|None=None)->dict:
    args=["gh","api","--method",method,endpoint]
    raw=None
    if payload is not None:
        args += ["--input","-"]; raw=json.dumps(payload,ensure_ascii=False).encode()
    return json.loads(run(*args,input_bytes=raw).stdout.decode())


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def copy(src:Path,rel:str|Path)->None:
    dst=REPO/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)


def api_push(parent:str,local_head:str)->tuple[str,str]:
    changed=[x for x in text("git","-c","core.quotepath=false","diff","--name-only",f"{parent}..{local_head}").splitlines() if x]
    entries=[]
    for rel in changed:
        parts=text("git","ls-tree",local_head,"--",rel).split()
        if len(parts)<3: raise RuntimeError(f"cannot resolve object for {rel}")
        mode,_,oid=parts[:3]
        raw=run("git","cat-file","blob",oid).stdout
        blob=gh("POST",f"{API_REPO}/git/blobs",{"content":base64.b64encode(raw).decode(),"encoding":"base64"})
        if blob["sha"]!=oid: raise RuntimeError(f"blob identity mismatch: {rel}")
        entries.append({"path":rel,"mode":mode,"type":"blob","sha":oid})
    tree=gh("POST",f"{API_REPO}/git/trees",{"base_tree":parent,"tree":entries})
    local_tree=text("git","rev-parse",f"{local_head}^{{tree}}")
    if tree["sha"]!=local_tree: raise RuntimeError("API tree differs from local committed tree")
    raw_commit=run("git","cat-file","commit",local_head).stdout.decode("utf-8")
    lines=raw_commit.splitlines(); author=next(x for x in lines if x.startswith("author ")); committer=next(x for x in lines if x.startswith("committer "))
    def parse_person(line:str)->dict:
        m=re.match(r"^(?:author|committer) (.*) <(.*)> (\d+) ([+-]\d{4})$",line)
        if not m: raise RuntimeError("cannot parse commit identity")
        name,email,stamp,offset=m.groups()
        from datetime import datetime,timezone,timedelta
        sign=1 if offset[0]=='+' else -1; delta=timedelta(hours=int(offset[1:3]),minutes=int(offset[3:5]))*sign
        dt=datetime.fromtimestamp(int(stamp),timezone(delta)).isoformat()
        return {"name":name,"email":email,"date":dt}
    message=text("git","show","-s","--format=%B",local_head).rstrip("\n")
    commit=gh("POST",f"{API_REPO}/git/commits",{"message":message,"tree":local_tree,"parents":[parent],
                                                  "author":parse_person(author),"committer":parse_person(committer)})
    gh("PATCH",f"{API_REPO}/git/refs/heads/main",{"sha":commit["sha"],"force":False})
    remote=gh("GET",f"{API_REPO}/git/ref/heads/main")["object"]["sha"]
    remote_tree=gh("GET",f"{API_REPO}/git/commits/{remote}")["tree"]["sha"]
    if remote_tree!=local_tree: raise RuntimeError("remote tree verification failed")
    # Recreate the API commit locally. GitHub's Git Database API omits the final
    # message newline while retaining the submitted author/committer offsets.
    header=raw_commit.split("\n\n",1)[0]
    api_raw=(header+"\n\n"+message).encode()
    rebuilt=run("git","hash-object","-t","commit","-w","--stdin",input_bytes=api_raw).stdout.decode().strip()
    if rebuilt==remote:
        run("git","update-ref","refs/heads/main",remote,local_head)
        run("git","update-ref","refs/remotes/origin/main",remote,parent)
    return remote,remote_tree


def main()->None:
    if text("git","status","--porcelain"): raise RuntimeError("repository must be clean")
    local=text("git","rev-parse","HEAD")
    remote=gh("GET",f"{API_REPO}/git/ref/heads/main")["object"]["sha"]
    if local!=remote: raise RuntimeError(f"local {local} differs from remote {remote}")
    for p in CODE.glob("*"):
        if p.is_file() and p.suffix.lower() in {".py",".r",".ps1"}: copy(p,Path("analysis/r7b1c")/p.name)
    for p in PROTOCOL.glob("*.md"): copy(p,Path("protocols/R7B1C")/p.name)
    for p in REPORT.glob("*.md"): copy(p,Path("reports/R7B1C")/p.name)
    for p in FIG.rglob("*"):
        if p.is_file(): copy(p,Path("figures/R7B1C")/p.relative_to(FIG))
    for p in AGG.glob("*"):
        if p.is_file() and p.name!="R7B1C_all_486000_replicates.tsv.gz": copy(p,Path("results/r7b1c")/p.name)
    audit_files=["R7B1C_implementation_grid_486.tsv","R7B1C_template_freeze_state.json","R7B1C_pilot_summary.tsv",
                 "R7B1C_pilot_gate_checks.tsv","R7B1C_pilot_gate_state.json","R7B1C_large_raw_asset_manifest.tsv",
                 "R7B1C_scientific_interpretation_state.json"]
    for name in audit_files: copy(AUDIT/name,Path("results/r7b1c/audit")/name)
    for p in (AUDIT/"independent_QA").glob("*"):
        if p.is_file(): copy(p,Path("results/r7b1c/independent_QA")/p.name)
    copy(AUDIT/"templates/R7B1C_causal_index_map.tsv","results/r7b1c/audit/R7B1C_causal_index_map.tsv")

    readme=REPO/"README.md"; content=readme.read_text(encoding="utf-8")
    marker="## R7B1C truth-known simulation calibration"
    section=f"""{marker}

R7B1C completes the frozen six-scenario, 486-row, 486,000-replicate simulation benchmark using two empirical 128-variant GJOKA/OneK LD templates. It compares single-causal ABF with source-matched SuSiE/coloc and a bounded same-locus PF10-to-PF50 QTL-LD mismatch. Source-matched multi-signal inference reduced false-H4 decisions in the frozen distinct-signal scenarios, but also reduced shared-signal recovery and left many complex low-power replicates uninformative. The two-template PF10-to-PF50 mismatch had little effect. These are bounded calibration trade-offs, not evidence of general method superiority.

The public repository includes code, protocols, aggregate results, figure source data, independent QA and a SHA-256 manifest for the local per-grid truth tables. The simulation calibrates inference under the frozen templates and fixed effects; it does not validate a biological mechanism or represent every ancestry and locus architecture.

![R7B1C scenario decisions](figures/R7B1C/Figure_R7B1C_1_scenario_H4_decisions.png)
"""
    if marker in content:
        start=content.index(marker); nxt=content.find("\n## ",start+len(marker)); content=content[:start]+section.rstrip()+"\n"+(content[nxt:] if nxt!=-1 else "")
    else: content=content.rstrip()+"\n\n"+section
    readme.write_text(content,encoding="utf-8")

    files=[p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts]
    big=[str(p.relative_to(REPO)) for p in files if p.stat().st_size>10*1024*1024]
    if big: raise RuntimeError(f"files over 10 MiB: {big}")
    secret=re.compile(r"(?i)(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
    hits=[]
    for p in files:
        if p.suffix.lower() in {".png",".pdf",".gz",".zip",".bin"}: continue
        try: s=p.read_text(encoding="utf-8")
        except Exception: continue
        if secret.search(s): hits.append(str(p.relative_to(REPO)))
    if hits: raise RuntimeError(f"secret-pattern hits: {hits}")
    manifest=REPO/"MANIFEST.sha256"
    manifest.write_text("\n".join(f"{sha256(p)}  {p.relative_to(REPO).as_posix()}" for p in sorted(x for x in REPO.rglob('*') if x.is_file() and '.git' not in x.parts and x!=manifest))+"\n",encoding="utf-8")
    run("git","add","analysis/r7b1c","protocols/R7B1C","reports/R7B1C","figures/R7B1C","results/r7b1c","README.md","MANIFEST.sha256")
    run("git","diff","--cached","--check")
    changed=text("git","diff","--cached","--name-only").splitlines()
    if not changed:
        print(json.dumps({"status":"NO_CHANGES","head":local},indent=2)); return
    run("git","commit","-m","Complete R7B1C truth-known simulation calibration")
    local_commit=text("git","rev-parse","HEAD")
    pushed=run("git","push","origin","main",check=False)
    transport="git_https"
    if pushed.returncode:
        transport="github_git_database_api"
        remote_commit,remote_tree=api_push(remote,local_commit)
    else:
        remote_commit=local_commit; remote_tree=text("git","rev-parse","HEAD^{tree}")
    verify=gh("GET",f"{API_REPO}/git/ref/heads/main")["object"]["sha"]
    if verify!=remote_commit: raise RuntimeError("remote HEAD verification failed")
    state={"schema":"R7B1C_GITHUB_SYNC_1.0","status":"PASS","previous_head":remote,"remote_commit":remote_commit,
           "remote_tree":remote_tree,"transport":transport,"files_changed":len(changed),"large_assets_committed":False}
    (AUDIT/"R7B1C_GitHub_sync_state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2))


if __name__=="__main__": main()
