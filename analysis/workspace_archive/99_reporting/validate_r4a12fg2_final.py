#!/usr/bin/env python3
"""Validate R4A12FG2 workspace state, evidence, tests, catalogs and release."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    checks: list[dict] = []

    def check(name: str, condition: bool, observed=None) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "observed": observed})

    protocol = root / "0_admin/protocol/current"
    amendment_path = protocol / "analysis_manifest_v11_amendment_A1_R4A12FG2.json"
    state_path = protocol / "R4A12FG2_state.json"
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    check("base manifest hash", amendment["base_manifest"]["sha256"] == sha256(protocol / "analysis_manifest_v11.json"))
    check("candidate registry hash", amendment["base_manifest"]["candidate_registry_sha256"] == sha256(protocol / "candidate_registry_v11.tsv"))
    check("amendment hash recorded in state", state["amendment"]["sha256"] == sha256(amendment_path))
    check("project conditional go", state["project"] == "CONDITIONAL_GO", state["project"])
    check("R4B hold", state["R4B"] == "HOLD", state["R4B"])
    check("C1 null", state["C1_count"] is None, state["C1_count"])
    check("primary bytes absent", state["primary_2026_female_summary_statistics"] == state["primary_2026_male_summary_statistics"] == "NOT_OBTAINED")
    check("FG2 status", state["R4A12FG2"]["status"] == "PASS_REGIONAL_INPUT_AND_DESCRIPTIVE_SMOKE_GATE")
    check("formal coloc not tested", state["R4A12FG2"]["formal_disease_molecular_coloc"] == "NOT_TESTED")
    check("next stage FG3", state["next_stage"] == "R4A12FG3_MOLECULAR_QTL_AND_LD_FEASIBILITY_GATE")

    p0 = {}
    for release in ("R12", "R13"):
        p = root / f"3_results/00_audit/R4A12FG2/{release}_IL12RB2_P0.json"
        p0[release] = json.loads(p.read_text(encoding="utf-8"))
        check(f"{release} P0", p0[release]["status"] == "PASS_REGION_STRUCTURAL_READY_FOR_HARMONIZATION", p0[release]["status"])
        check(f"{release} P0 rows", p0[release]["row_count"] == 6855, p0[release]["row_count"])
        check(f"{release} P0 errors", p0[release]["errors"] == [], p0[release]["errors"])

    receipt_dir = root / "1_data/gwas/outcome/ssc_finngen_r12_r13/regional/receipts"
    for release in ("R12", "R13"):
        first = json.loads((receipt_dir / f"{release}_M13_SYSTSLCE_IL12RB2_remote_tabix_receipt.json").read_text(encoding="utf-8"))
        second = json.loads((root / f"3_results/00_audit/R4A12FG2/repro/{release}_requery.receipt.json").read_text(encoding="utf-8"))
        check(f"{release} requery hash", first["result"]["output_sha256"] == second["result"]["output_sha256"], second["result"]["output_sha256"])
        check(f"{release} requery rows", first["result"]["row_count"] == second["result"]["row_count"] == 6855)

    descriptive = json.loads((root / "3_results/00_audit/R4A12FG2/R4A12FG2_IL12RB2_TenK10K_FinnGen_descriptive_audit.json").read_text(encoding="utf-8"))
    check("descriptive audit status", descriptive["status"] == "PASS_REPRODUCIBLE_DESCRIPTIVE_AUDIT")
    check("TenK gene-level cells", descriptive["tenk10k_inventory"]["gene_level_cells_with_IL12RB2"] == 26)
    check("TenK CS cells", descriptive["tenk10k_inventory"]["susie_cells_with_IL12RB2_CS"] == 11)
    check("TenK CS count", descriptive["tenk10k_inventory"]["susie_credible_sets"] == 17)
    check("TenK unique CS variants", descriptive["tenk10k_inventory"]["susie_unique_variant_keys"] == 76)
    check("R12 exact CS overlap", descriptive["finngen_releases"]["R12"]["credible_member_exact_overlap_keys"] == 68)
    check("R13 exact CS overlap", descriptive["finngen_releases"]["R13"]["credible_member_exact_overlap_keys"] == 68)
    check("formal analyses false", not descriptive["method_boundary"]["formal_colocalization_run"] and not descriptive["method_boundary"]["formal_finemapping_run"])

    test_dir = root / "2_code/06_intake/finngen_r12_r13"
    test_proc = subprocess.run(
        ["D:/bioinfor/python.exe", "-m", "unittest", "-v", "test_finngen_r12_r13_intake.py"],
        cwd=test_dir, capture_output=True, text=True,
    )
    check("engineering unit tests", test_proc.returncode == 0 and "Ran 8 tests" in (test_proc.stdout + test_proc.stderr), (test_proc.stdout + test_proc.stderr)[-1000:])
    node_proc = subprocess.run(["node", "--check", str(root / "2_code/06_intake/finngen_fg2_remote/query_finngen_region.mjs")], capture_output=True, text=True)
    check("remote reader syntax", node_proc.returncode == 0, node_proc.stderr)

    workspace = json.loads((root / "0_admin/workspace_paths.json").read_text(encoding="utf-8"))
    check("workspace reports current", workspace["reports_current"].endswith("R4A12FG2"), workspace["reports_current"])
    check("workspace release current", workspace["release_current"].endswith("R4A12FG2"), workspace["release_current"])
    check("workspace next stage", workspace["next_stage"] == state["next_stage"], workspace["next_stage"])

    report_dir = root / "7.Report/current/R4A12FG2"
    check("current report count", len(list(report_dir.glob("*.md"))) == 7, len(list(report_dir.glob("*.md"))))
    check("detailed action record", (report_dir / "99_CMM_R4A12FG2_详细行动记录_2026-09-13.md").is_file())

    validation_paths = list((root / "6_release/current/R4A12FG2").glob("*.zip.validation.json"))
    check("one release validation", len(validation_paths) == 1, len(validation_paths))
    if validation_paths:
        release_validation = json.loads(validation_paths[0].read_text(encoding="utf-8"))
        check("release validation pass", release_validation["status"] == "PASS_9_OF_9", release_validation["status"])
        check("release file count", release_validation["file_count"] == 66, release_validation["file_count"])

    catalogs = [
        "1_data/catalogs/DATA_CATALOG.tsv", "2_code/CODE_CATALOG.tsv", "3_results/RESULT_CATALOG.tsv",
        "7.Report/REPORT_CATALOG.tsv", "6_release/RELEASE_CATALOG.tsv",
    ]
    for rel in catalogs:
        path = root / rel
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        destinations = [row["destination_rel"] for row in rows]
        check(f"catalog unique {path.name}", len(destinations) == len(set(destinations)), len(rows))
        check(f"catalog contains FG2 {path.name}", any(row.get("provenance_round") == "R4A12FG2" for row in rows))

    failed = [item for item in checks if item["status"] != "PASS"]
    output = {
        "schema_version": "CMM_R4A12FG2_FINAL_VALIDATION_1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks": checks,
        "status": f"PASS_{len(checks)}_OF_{len(checks)}" if not failed else "FAIL",
    }
    outdir = root / "0_admin/validation/R4A12FG2"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "R4A12FG2_FINAL_VALIDATION.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (outdir / "R4A12FG2_FINAL_VALIDATION.md").write_text(
        f"# R4A12FG2 final validation\n\nStatus: **{output['status']}**  \n"
        f"Checks: {output['checks_passed']}/{output['checks_total']}\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": output["status"], "checks": len(checks), "failed": [x["name"] for x in failed]}, ensure_ascii=False))
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
