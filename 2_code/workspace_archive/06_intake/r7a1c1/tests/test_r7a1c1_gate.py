#!/usr/bin/env python3
from __future__ import annotations

import collections
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


CODE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("panel_v2", CODE / "02_hra_bam_target_panel_v2.py")
panel = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(panel)


# High-UMI cells plus low-UMI background droplets.  The called-cell result must
# exclude the background and stay in the liver-study plausibility interval.
counts = collections.Counter({f"CELL{i:05d}-1": 6000 for i in range(5000)})
counts.update({f"EMPTY{i:05d}-1": 50 for i in range(10000)})
for i in range(100):
    counts[f"CELL{i:05d}-1"] = 10000
called, qc = panel.call_cells(counts, expected_cells=6000)
assert len(called) == 5000
assert all(x.startswith("CELL") for x in called)
assert qc["called_cell_UMI_threshold"] == 1000


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    runs = ["HRR1849459", "HRR1849460", "HRR1849461", "HRR1849462", "HRR1849463"]
    for index, run in enumerate(runs):
        value = {
            "schema_version": "CMM_R7A1C1_TARGET_PANEL_2.0",
            "run": run,
            "technical_QC": "PASS",
            "primary_FCRL3_B_detectable": index < 3,
            "primary_IL12RB2_NK_detectable": False,
            "promotion_eligible_FCRL3_B": index < 3,
            "promotion_eligible_IL12RB2_NK": False,
        }
        (tmp / f"{run}_target_panel_summary.json").write_text(json.dumps(value), encoding="utf-8")
    final = tmp / "final.json"
    subprocess.run(
        ["python3", str(CODE / "03_adjudicate_HRA008003_liver_gate_v2.py"),
         "--summary-dir", str(tmp), "--out", str(final)],
        check=True,
    )
    state = json.loads(final.read_text(encoding="utf-8"))
    assert state["promotion_gate"] == "PASS"
    assert state["next_stage"] == "GO_R7A2_PBC_MANUSCRIPT_SCALE"

print("R7A1C1_TESTS_PASS")
