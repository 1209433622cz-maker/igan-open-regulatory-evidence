#!/usr/bin/env python3
"""Run the frozen R7B1E0 kriging replay by locus with deterministic closeout."""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import subprocess
import time
from pathlib import Path

import pandas as pd

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
R=Path(r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe")
SCRIPT=ROOT/"2_code/06_intake/r7b1e0/01_replay_kriging_locus.R"
WORK=ROOT/"3_results/00_audit/R7B1B_v2/R7B1B_v2_exact_642_high_information_comparisons.tsv"
OUT=ROOT/"3_results/04_integration/R7B1E0/kriging_replay"
LOG=OUT/"logs"

def run_locus(locus:int)->dict:
    target=OUT/f"locus_{locus:02d}"/"locus_state.json"
    if target.exists():
        old=json.loads(target.read_text(encoding="utf-8"))
        if old.get("status")=="PASS": return {"locus":locus,"status":"RESUME_PASS"}
    env=os.environ.copy(); env["R7_PROJECT_ROOT"]=str(ROOT); env["R7B1E0_LOCUS"]=str(locus)
    started=time.time()
    proc=subprocess.run([str(R),"--vanilla",str(SCRIPT)],env=env,capture_output=True)
    LOG.mkdir(parents=True,exist_ok=True)
    (LOG/f"locus_{locus:02d}.stdout.log").write_bytes(proc.stdout)
    (LOG/f"locus_{locus:02d}.stderr.log").write_bytes(proc.stderr)
    return {"locus":locus,"status":"PASS" if proc.returncode==0 else "FAIL","returncode":proc.returncode,"runtime_seconds":time.time()-started}

def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    work=pd.read_csv(WORK,sep="\t")
    loci=sorted(work.locus_index.unique().astype(int).tolist())
    started=time.time(); rows=[]
    with cf.ThreadPoolExecutor(max_workers=min(8,len(loci))) as pool:
        futures={pool.submit(run_locus,l):l for l in loci}
        for fut in cf.as_completed(futures):
            row=fut.result(); rows.append(row); print(json.dumps(row),flush=True)
    pd.DataFrame(rows).sort_values("locus").to_csv(OUT/"orchestrator_loci.tsv",sep="\t",index=False)
    states=[]
    for locus in loci:
        p=OUT/f"locus_{locus:02d}"/"locus_state.json"
        if not p.exists(): raise RuntimeError(f"missing locus state {locus}")
        states.append(json.loads(p.read_text(encoding="utf-8")))
    status="PASS" if all(s["status"]=="PASS" for s in states) else "HOLD"
    state={"schema":"R7B1E0_KRIGING_ORCHESTRATOR_1.0","status":status,"loci":len(loci),
           "comparisons":int(work.comparison_id.nunique()),"diagnostic_units":sum(s["diagnostic_units"] for s in states),
           "diagnostic_pass":sum(s["diagnostic_pass"] for s in states),"diagnostic_hold":sum(s["diagnostic_hold"] for s in states),
           "historical_flags":sum(s["historical_flags"] for s in states),"official_flags":sum(s["official_flags"] for s in states),
           "runtime_seconds":time.time()-started}
    (OUT/"orchestrator_state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2))
    if status!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
