#!/usr/bin/env python3
"""Run/resume the 486-row R7B1C grid across bounded local workers."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
GRID = ROOT / "3_results/00_audit/R7B1C/R7B1C_implementation_grid_486.tsv"
PILOT = ROOT / "3_results/00_audit/R7B1C/R7B1C_pilot_gate_state.json"
OUT = ROOT / "3_results/05_simulation/R7B1C/full"
R_SCRIPT = ROOT / "2_code/06_intake/r7b1c/02_run_r7b1c_simulation_shard.R"
R_EXE = Path(r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe")


def complete(gid: str) -> bool:
    state_path = OUT / f"{gid}.state.json"
    result_path = OUT / f"{gid}.tsv.gz"
    if not state_path.exists() or not result_path.exists():
        return False
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return state.get("status") == "COMPLETE" and state.get("replicates") == 1000 and result_path.stat().st_size > 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    if pilot.get("status") != "PASS" or not pilot.get("formal_grid_authorized"):
        raise RuntimeError("pilot gate is not PASS")
    grid = pd.read_csv(GRID, sep="\t")
    if len(grid) != 486 or int(grid["replicates"].sum()) != 486000:
        raise RuntimeError("formal grid identity failed")
    OUT.mkdir(parents=True, exist_ok=True)
    pending = [gid for gid in grid["grid_id"] if not complete(gid)]
    if not pending:
        print(json.dumps({"status": "ALREADY_COMPLETE", "rows": 486, "replicates": 486000}, indent=2))
        return
    workers = max(1, min(args.workers, len(pending), 14))
    shards = [pending[i::workers] for i in range(workers)]
    started = time.time()
    processes = []
    for i, shard in enumerate(shards, 1):
        env = os.environ.copy()
        env.update(
            {
                "R7_PROJECT_ROOT": str(ROOT),
                "R7B1C_GRID_IDS": ",".join(shard),
                "R7B1C_OUTDIR": str(OUT),
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
            }
        )
        env.pop("R7B1C_REPS_OVERRIDE", None)
        stdout = (OUT / f"worker_{i:02d}.stdout.log").open("w", encoding="utf-8")
        stderr = (OUT / f"worker_{i:02d}.stderr.log").open("w", encoding="utf-8")
        proc = subprocess.Popen([str(R_EXE), str(R_SCRIPT)], env=env, stdout=stdout, stderr=stderr)
        processes.append((i, proc, stdout, stderr))
    last = -1
    while any(proc.poll() is None for _, proc, _, _ in processes):
        done = sum(complete(gid) for gid in grid["grid_id"])
        if done != last:
            print(f"FULL_GRID_PROGRESS {done}/486 elapsed_seconds={time.time()-started:.1f}", flush=True)
            last = done
        time.sleep(15)
    exit_codes = {}
    for i, proc, stdout, stderr in processes:
        stdout.close(); stderr.close(); exit_codes[f"worker_{i:02d}"] = proc.returncode
    done = sum(complete(gid) for gid in grid["grid_id"])
    state = {
        "schema": "R7B1C_ORCHESTRATOR_1.0",
        "status": "COMPLETE" if done == 486 and all(v == 0 for v in exit_codes.values()) else "INCOMPLETE",
        "grid_rows_complete": done,
        "grid_rows_expected": 486,
        "replicates_expected": 486000,
        "workers": workers,
        "exit_codes": exit_codes,
        "runtime_seconds": time.time() - started,
    }
    (OUT / "orchestrator_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2))
    if state["status"] != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
