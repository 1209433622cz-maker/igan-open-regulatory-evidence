#!/usr/bin/env python3
"""Compare the Python ABF smoke matrix with official R coloc output."""

import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "3_results/04_integration/R5A2B"
AUDIT = ROOT / "3_results/00_audit/R5A2B"
p = pd.read_csv(OUT / "chr5_coloc_abf_smoke.tsv", sep="\t")
r = pd.read_csv(OUT / "chr5_coloc_official_R_validation.tsv", sep="\t")
keys = ["trait", "cell_type", "phenotype_id"]

columns = {
    1e-6: ("H4_p12_1e-6", "H4ratio_p12_1e-6"),
    1e-5: ("PP_H4_p12_1e-5", "H4_over_H3H4_p12_1e-5"),
    1e-4: ("H4_p12_1e-4", "H4ratio_p12_1e-4"),
}
details = []
max_h4 = 0.0
max_ratio = 0.0
for p12, (h4_col, ratio_col) in columns.items():
    x = p.merge(r[np.isclose(r["p12"], p12)], on=keys, validate="one_to_one")
    h4_diff = float(np.max(np.abs(x[h4_col] - x["PP_H4"])))
    ratio_diff = float(np.max(np.abs(x[ratio_col] - x["H4_over_H3H4"])))
    max_h4 = max(max_h4, h4_diff)
    max_ratio = max(max_ratio, ratio_diff)
    details.append({"p12": p12, "rows": len(x), "max_H4_abs_difference": h4_diff, "max_H4ratio_abs_difference": ratio_diff})

default = p.merge(r[np.isclose(r["p12"], 1e-5)], on=keys, validate="one_to_one")
audit = {
    "schema_version": "1.0",
    "python_comparisons": len(p),
    "official_R_comparisons": len(default),
    "official_R_runs": len(r),
    "p12_comparisons": details,
    "max_H4_absolute_difference": max_h4,
    "max_H4ratio_absolute_difference": max_ratio,
    "default_H0_H4_max_absolute_difference": float(max(
        np.max(np.abs(default[f"PP_H{i}_p12_1e-5"] - default[f"PP_H{i}"])) for i in range(5)
    )),
    "top_SNP_exact_match": bool((default["shared_top_variant"] == default["top_SNP"]).all()),
    "top_SNP_PP_max_absolute_difference": float(np.max(np.abs(default["shared_top_SNP_PP_H4_conditional"] - default["top_SNP_PP_H4"]))),
    "validation_pass": bool(
        len(p) == len(default) == 96
        and max_h4 < 1e-12
        and max_ratio < 1e-12
        and (default["shared_top_variant"] == default["top_SNP"]).all()
    ),
}
(AUDIT / "chr5_python_vs_official_R_coloc_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(json.dumps(audit, indent=2))
