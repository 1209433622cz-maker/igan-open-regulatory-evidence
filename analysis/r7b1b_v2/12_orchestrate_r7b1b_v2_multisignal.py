#!/usr/bin/env python3
"""Resumable locus-parallel orchestrator for R7B1B v2 SuSiE/coloc.susie."""
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
WORK = ROOT / "3_results/00_audit/R7B1B_v2/R7B1B_v2_exact_642_high_information_comparisons.tsv"
SCRIPT = ROOT / "2_code/06_intake/r7b1/11_run_r7b1b_v2_multisignal_locus.R"
RSCRIPT = ROOT / "tools/R/R-4.6.1/bin/x64/Rscript.exe"
OUT = ROOT / "3_results/04_integration/R7B1B_v2/multisignal"
LOGS = OUT / "logs"


def run_locus(locus: int) -> dict[str, object]:
    directory = OUT / f"locus_{locus:02d}"
    state_path = directory / "locus_state.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            if state.get("status") == "COMPLETE":
                return {"locus": locus, "returncode": 0, "resumed": True, "state": state}
        except Exception:
            pass
    env = os.environ.copy()
    env["R7_PROJECT_ROOT"] = str(ROOT)
    env["R7B1B_LOCUS"] = str(locus)
    temp_dir = ROOT / "3_results/00_audit/R7B1B_v2/tmp" / f"locus_{locus:02d}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(temp_dir)
    env["TMP"] = str(temp_dir)
    env["TEMP"] = str(temp_dir)
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"locus_{locus:02d}.log"
    started = time.time()
    with log_path.open("w", encoding="utf-8", newline="") as log:
        proc = subprocess.run(
            [str(RSCRIPT), "--vanilla", str(SCRIPT)],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )
    state = None
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            state = None
    return {
        "locus": locus,
        "returncode": proc.returncode,
        "resumed": False,
        "runtime_seconds": round(time.time() - started, 3),
        "log": str(log_path),
        "state": state,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--loci", nargs="*", type=int)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 8:
        raise SystemExit("--workers must be 1..8")
    work = pd.read_csv(WORK, sep="\t")
    requested = set(args.loci or work["locus_index"].astype(int).tolist())
    sizes = work.groupby("locus_index").size().to_dict()
    loci = sorted(requested, key=lambda value: (-int(sizes[value]), int(value)))
    expected = sorted(work["locus_index"].astype(int).unique().tolist())
    if args.loci is None and sorted(loci) != expected:
        raise RuntimeError("locus universe drift")
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"START loci={len(loci)} workers={args.workers}", flush=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(run_locus, locus): locus for locus in loci}
        for future in concurrent.futures.as_completed(pending):
            result = future.result()
            results.append(result)
            state = result.get("state") or {}
            print(
                f"LOCUS_DONE {len(results)}/{len(loci)} locus={result['locus']} rc={result['returncode']} "
                f"status={state.get('status','MISSING')} complete={state.get('complete','NA')} failures={state.get('qc_failures','NA')}",
                flush=True,
            )
    results.sort(key=lambda x: int(x["locus"]))
    state = {
        "schema": "R7B1B_V2_MULTISIGNAL_ORCHESTRATOR_1.0",
        "status": "COMPLETE" if all(r["returncode"] == 0 and r.get("state") for r in results) else "FAILED",
        "workers": args.workers,
        "loci": len(results),
        "comparison_complete": sum(int((r.get("state") or {}).get("complete", 0)) for r in results),
        "comparison_qc_failures": sum(int((r.get("state") or {}).get("qc_failures", 0)) for r in results),
        "results": results,
    }
    path = OUT / "orchestrator_state.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in state.items() if k != "results"}, indent=2), flush=True)
    if state["status"] != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
