#!/usr/bin/env python3
"""Independent closure checks for the bounded R7A1B execution."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
BASE = ROOT / "3_results/04_integration/R7A1B"
AUD = ROOT / "3_results/00_audit/R7A1B"
AUD.mkdir(parents=True, exist_ok=True)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

checks = {}
archive_gate = json.loads((AUD / "R7A1B_OneK_archive_gate.json").read_text(encoding="utf-8"))
checks["onek_archive_gate"] = archive_gate.get("gate") == "PASS"
checks["onek_archive_exact_bytes"] = archive_gate.get("bytes_read") == 10_344_009_571
checks["onek_archive_expected_md5"] = archive_gate.get("md5") == "e42239480f40abd21f221c0d77c82cc3"

smoke = pd.read_csv(BASE / "R7A1B_coloc_smoke.tsv", sep="\t")
compare = json.loads((BASE / "R7A1B_Python_vs_R_validation.json").read_text(encoding="utf-8"))
trigger = pd.read_csv(BASE / "R7A1B_multisignal_triggers.tsv", sep="\t")
sig = pd.read_csv(BASE / "multisignal/R7A1B_signal_coloc_susie.tsv", sep="\t")
fits = pd.read_csv(BASE / "multisignal/R7A1B_susie_fit_summary.tsv", sep="\t")
stable = pd.read_csv(BASE / "R7A1B_signal_stability_by_cell.tsv", sep="\t")
final = json.loads((BASE / "R7A1B_final_adjudication.json").read_text(encoding="utf-8"))

checks["nine_frozen_smoke_tests"] = len(smoke) == 9
checks["python_R_abf_match"] = compare.get("gate") == "PASS" and compare.get("max_posterior_abs_diff", 1) <= 1e-10
checks["exact_trigger_set"] = set(map(tuple, trigger[["gene", "cell_type"]].to_numpy())) == {
    ("IL12RB2", "NK"), ("FCRL3", "B_IN"), ("FCRL3", "B_MEM"),
    ("FCRL3", "CD4_NC"), ("FCRL3", "CD8_ET"), ("FCRL3", "NK"), ("FCRL3", "NK_R")
}
checks["only_expected_trigger_genes"] = set(sig.gene) == {"IL12RB2", "FCRL3"}
checks["all_four_configurations"] = set(fits.config) == {"PF10_L5", "PF10_L10", "PF10_L20", "PF50_L10"}
checks["all_28_fits_converged"] = len(fits) == 28 and fits.disease_converged.all() and fits.qtl_converged.all()
checks["all_fits_have_CS"] = (fits.disease_CS >= 1).all() and (fits.qtl_CS >= 1).all()
checks["expected_signal_rows"] = len(sig) == 120
cs_members = pd.read_csv(BASE / "multisignal/R7A1B_susie_credible_set_members.tsv.gz", sep="\t")
checks["credible_set_members_exported"] = len(cs_members) > 0 and set(cs_members.trait) == {"PBC", "OneK_QTL"}
checks["stable_FCRL3_cells"] = set(stable.loc[(stable.gene == "FCRL3") & stable.robust_all_configs, "cell_type"]) == {
    "B_IN", "B_MEM", "CD4_NC", "NK", "NK_R"
}
checks["stable_IL12RB2_cell"] = set(stable.loc[(stable.gene == "IL12RB2") & stable.robust_all_configs, "cell_type"]) == {"NK"}
checks["final_two_gene_gate"] = final.get("signal_specific_pass_genes") == 2
checks["next_stage_exact"] = final.get("decision") == "GO_R7A1C_TENK_REPLICATION_AND_PBC_LIVER_DETECTABILITY"

ld_qc = []
for path in sorted((BASE / "sourceLD").glob("*/*LD_QC.json")):
    item = json.loads(path.read_text(encoding="utf-8"))
    ld_qc.append({"file": path.name, "directory": path.parent.name,
                   "gate": item.get("status", item.get("gate_pass"))})
source = [x for x in ld_qc if x["file"] == "sourceLD_QC.json"]
resid = [x for x in ld_qc if x["file"] == "covariate_residual_LD_QC.json"]
checks["seven_source_LD_gates"] = len(source) == 7 and all(x["gate"] == "PASS" for x in source)
checks["seven_residual_LD_gates"] = len(resid) == 7 and all(x["gate"] is True for x in resid)

gjoka_qc = {}
gjbase = ROOT / "1_data/study_inputs/PBC_GJOKA/R7A1B"
for locus in (2, 4):
    path = gjbase / f"sumstats_{locus}.assoc.logistic"
    data = pd.read_csv(path, sep=r"\s+")
    if "TEST" in data:
        data = data[data.TEST == "ADD"]
    delta = np.abs(data.BETA / data.SE - data.STAT)
    corr = float(np.corrcoef(data.BETA / data.SE, data.STAT)[0, 1])
    gjoka_qc[str(locus)] = {
        "rows": int(len(data)), "max_abs_beta_over_se_minus_stat": float(delta.max()),
        "q99_abs_delta": float(delta.quantile(0.99)), "correlation": corr,
        "summary_bytes": path.stat().st_size, "summary_sha256": sha256(path),
        "ld_bytes": (gjbase / f"covmat_{locus}.ld").stat().st_size,
        "ld_sha256": sha256(gjbase / f"covmat_{locus}.ld"),
    }
checks["gjoka_rounding_gate"] = all(x["max_abs_beta_over_se_minus_stat"] <= 0.01 and x["correlation"] > 0.9999999 for x in gjoka_qc.values())

input_zip = Path(r"C:\Users\Administrator\Downloads\CMM_R7A1B0_PBC_3Control_SignalGate_Hardening_2026-09-15.zip")
package = None
if input_zip.exists():
    with zipfile.ZipFile(input_zip) as zf:
        bad = zf.testzip()
    package = {"bytes": input_zip.stat().st_size, "sha256": sha256(input_zip), "zip_crc": "PASS" if bad is None else f"FAIL:{bad}"}
    checks["input_package_identity"] = package["sha256"] == "3345fa585ccd57d2b36c529ee4c6335169328cda168635d3ee29148565fe1dd0"
    checks["input_package_crc"] = bad is None

outputs = {}
for path in sorted([
    BASE / "R7A1B_coloc_smoke.tsv", BASE / "R7A1B_multisignal_triggers.tsv",
    BASE / "multisignal/R7A1B_signal_coloc_susie.tsv",
    BASE / "multisignal/R7A1B_susie_fit_summary.tsv",
    BASE / "multisignal/R7A1B_susie_credible_set_members.tsv.gz",
    BASE / "R7A1B_gene_adjudication.tsv", BASE / "R7A1B_final_adjudication.json",
]):
    outputs[str(path.relative_to(ROOT)).replace("\\", "/")] = {"bytes": path.stat().st_size, "sha256": sha256(path)}

state = {
    "stage": "R7A1B1",
    "overall_gate": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "gjoka_effect_field_qc": gjoka_qc,
    "input_R7A1B0_package": package,
    "output_files": outputs,
}
encoded = json.dumps(state, indent=2, allow_nan=False,
                     default=lambda value: value.item() if isinstance(value, np.generic) else str(value))
(AUD / "R7A1B_independent_QA.json").write_text(encoded, encoding="utf-8")
print(encoded)
if state["overall_gate"] != "PASS":
    raise SystemExit(2)
