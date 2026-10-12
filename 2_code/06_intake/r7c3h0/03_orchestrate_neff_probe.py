#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import time
from pathlib import Path

import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
WORK = ROOT / "3_results/00_audit/R7C3H0/R7C3H0_neff_probe_comparisons.tsv"
SCRIPT = ROOT / "2_code/06_intake/r7c3h0/02_run_neff_probe_locus.R"
RSCRIPT = ROOT / "0_admin/tooling/R/R-4.6.1/bin/x64/Rscript.exe"
OUT = ROOT / "3_results/04_integration/R7C3H0/neff_probe/multisignal"
LOGS = OUT / "logs"
DISEASE_N = "21584.376825785395"


def run_locus(locus: int) -> dict[str, object]:
    directory = OUT / f"locus_{locus:02d}"
    state_path = directory / "locus_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("status") == "COMPLETE" and abs(float(state.get("disease_n")) - float(DISEASE_N)) < 1e-8:
            return {"locus": locus, "returncode": 0, "resumed": True, "state": state}
    env = os.environ.copy()
    env.update(R7_PROJECT_ROOT=str(ROOT), R7B1B_LOCUS=str(locus), R7C3H_DISEASE_N=DISEASE_N)
    temp = ROOT / "3_results/00_audit/R7C3H0/tmp" / f"locus_{locus:02d}"
    temp.mkdir(parents=True, exist_ok=True)
    env.update(TMPDIR=str(temp), TMP=str(temp), TEMP=str(temp))
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"locus_{locus:02d}.log"
    started = time.time()
    with log_path.open("w", encoding="utf-8", newline="") as log:
        proc = subprocess.run([str(RSCRIPT), "--vanilla", str(SCRIPT)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, text=True)
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else None
    return {"locus": locus, "returncode": proc.returncode, "resumed": False, "runtime_seconds": round(time.time()-started, 3), "log": str(log_path), "state": state}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if args.workers not in range(1, 5):
        raise SystemExit("workers must be 1..4")
    work = pd.read_csv(WORK, sep="\t")
    sizes = work.groupby("locus_index").size().to_dict()
    loci = sorted(map(int, sizes), key=lambda x: (-sizes[x], x))
    print(f"START comparisons={len(work)} loci={len(loci)} workers={args.workers}", flush=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(run_locus, locus): locus for locus in loci}
        for future in concurrent.futures.as_completed(pending):
            result = future.result()
            results.append(result)
            state = result.get("state") or {}
            print(f"LOCUS_DONE {len(results)}/{len(loci)} locus={result['locus']} rc={result['returncode']} status={state.get('status','MISSING')} complete={state.get('complete','NA')}", flush=True)
    results.sort(key=lambda x: int(x["locus"]))
    state = {
        "schema": "R7C3H0_NEFF_PROBE_ORCHESTRATOR_1.0",
        "status": "COMPLETE" if all(r["returncode"] == 0 and (r.get("state") or {}).get("status") == "COMPLETE" for r in results) else "FAILED",
        "disease_n": float(DISEASE_N),
        "workers": args.workers,
        "loci": len(results),
        "comparison_complete": sum(int((r.get("state") or {}).get("complete", 0)) for r in results),
        "comparison_qc_failures": sum(int((r.get("state") or {}).get("qc_failures", 0)) for r in results),
        "results": results,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "orchestrator_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in state.items() if k != "results"}, indent=2), flush=True)
    if state["status"] != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
