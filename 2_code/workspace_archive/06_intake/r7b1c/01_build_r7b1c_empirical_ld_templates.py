#!/usr/bin/env python3
"""Build the two pre-result-frozen empirical LD templates for R7B1C."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "3_results/00_audit/R7B1C/templates"
GRID = ROOT / "3_results/00_audit/R7B0/R7B0_simulation_grid.tsv"
PROTOCOL = ROOT / "0_admin/protocols/R7B1C/R7B1C_simulation_implementation_freeze_v1.1.md"
TEMPLATES = [(2, "NK"), (4, "B_IN")]
TARGETS = (0.2, 0.5, 0.8)
WINDOW = 128


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def nearest_psd_correlation(matrix: np.ndarray) -> tuple[np.ndarray, dict]:
    raw = (matrix + matrix.T) / 2.0
    np.fill_diagonal(raw, 1.0)
    values, vectors = np.linalg.eigh(raw)
    clipped = np.maximum(values, 1e-6)
    fixed = (vectors * clipped) @ vectors.T
    scale = np.sqrt(np.diag(fixed))
    fixed = fixed / np.outer(scale, scale)
    fixed = (fixed + fixed.T) / 2.0
    np.fill_diagonal(fixed, 1.0)
    return fixed, {
        "raw_min_eigenvalue": float(values.min()),
        "clipped_eigenvalues": int((values < 1e-6).sum()),
        "relative_frobenius_change": float(np.linalg.norm(fixed - raw) / np.linalg.norm(raw)),
        "final_min_eigenvalue": float(np.linalg.eigvalsh(fixed).min()),
    }


def find_window(disease: np.ndarray, qtl: np.ndarray, common_n: int) -> tuple[int, dict]:
    tri = np.triu_indices(WINDOW, k=5)
    best = None
    for start in range(common_n - WINDOW + 1):
        rd = disease[start : start + WINDOW, start : start + WINDOW]
        rq = qtl[start : start + WINDOW, start : start + WINDOW]
        avg = (np.square(rd[tri]) + np.square(rq[tri])) / 2.0
        deviations = [float(np.min(np.abs(avg - target))) for target in TARGETS]
        key = (max(deviations), sum(deviations), start)
        if best is None or key < best[0]:
            best = (key, start, deviations)
    assert best is not None
    return int(best[1]), {"max_target_deviation": best[0][0], "target_deviations": best[2]}


def best_pair(avg_r2: np.ndarray, target: float, excluded: set[int] | None = None) -> tuple[int, int, float]:
    excluded = excluded or set()
    candidates = []
    for i in range(WINDOW):
        for j in range(i + 5, WINDOW):
            if i in excluded or j in excluded:
                continue
            candidates.append((abs(float(avg_r2[i, j]) - target), i, j, float(avg_r2[i, j])))
    if not candidates:
        raise RuntimeError("no causal pair candidates")
    _, i, j, achieved = min(candidates)
    return i, j, achieved


def best_relative(avg_r2: np.ndarray, anchor: int, target: float, excluded: set[int]) -> tuple[int, float]:
    candidates = []
    for j in range(WINDOW):
        if j in excluded or abs(j - anchor) < 5:
            continue
        candidates.append((abs(float(avg_r2[anchor, j]) - target), j, float(avg_r2[anchor, j])))
    if not candidates:
        raise RuntimeError("no relative causal candidates")
    _, j, achieved = min(candidates)
    return j, achieved


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    causal_rows: list[dict] = []
    manifests: list[dict] = []
    for locus, cell in TEMPLATES:
        template_id = f"T_L{locus:02d}_{cell}_PF10"
        source = ROOT / f"1_data/study_inputs/PBC_GJOKA/R7B1B_v2"
        block = ROOT / f"3_results/04_integration/R7B1B_v2/sourceLD_blocks/L{locus:02d}_{cell}"
        sum_path = source / f"sumstats_{locus}.assoc.logistic"
        disease_path = source / f"covmat_{locus}.ld"
        variants_path = block / "variants.tsv.gz"
        qtl_path = block / "PF10_residualized_A1_correlation.float32.bin"
        qtl_mismatch_path = block / "PF50_residualized_A1_correlation.float32.bin"

        sums = pd.read_csv(sum_path, sep=r"\s+").reset_index(names="disease_index")
        variants = pd.read_csv(variants_path, sep="\t").reset_index(names="qtl_index")
        common = (
            variants.merge(
                sums[["disease_index", "SNP", "BP"]],
                left_on=["rsid", "position_GRCh37"],
                right_on=["SNP", "BP"],
                how="inner",
                validate="one_to_one",
            )
            .sort_values(["position_GRCh37", "variant_id"])
            .reset_index(drop=True)
        )
        disease_full = np.loadtxt(disease_path, dtype=np.float64)
        if disease_full.shape != (len(sums), len(sums)):
            raise RuntimeError(f"disease LD dimension mismatch for {template_id}")
        qtl_full = np.fromfile(qtl_path, dtype="<f4").reshape(len(variants), len(variants)).astype(np.float64)
        qtl_mismatch_full = np.fromfile(qtl_mismatch_path, dtype="<f4").reshape(len(variants), len(variants)).astype(np.float64)
        di = common["disease_index"].to_numpy(int)
        qi = common["qtl_index"].to_numpy(int)
        disease_common = disease_full[np.ix_(di, di)]
        qtl_common = qtl_full[np.ix_(qi, qi)]
        start, window_qc = find_window(disease_common, qtl_common, len(common))
        selected = common.iloc[start : start + WINDOW].copy().reset_index(drop=True)
        disease_raw = disease_common[start : start + WINDOW, start : start + WINDOW]
        qtl_raw = qtl_common[start : start + WINDOW, start : start + WINDOW]
        qtl_mismatch_common = qtl_mismatch_full[np.ix_(qi, qi)]
        qtl_mismatch_raw = qtl_mismatch_common[start : start + WINDOW, start : start + WINDOW]
        disease, disease_qc = nearest_psd_correlation(disease_raw)
        qtl, qtl_qc = nearest_psd_correlation(qtl_raw)
        qtl_mismatch, qtl_mismatch_qc = nearest_psd_correlation(qtl_mismatch_raw)
        avg_r2 = (np.square(disease) + np.square(qtl)) / 2.0

        tdir = OUT / template_id
        tdir.mkdir(exist_ok=True)
        d_out = tdir / "disease_ld.float64.bin"
        q_out = tdir / "qtl_ld.float64.bin"
        qm_out = tdir / "qtl_ld_mismatch_PF50.float64.bin"
        disease.astype("<f8").tofile(d_out)
        qtl.astype("<f8").tofile(q_out)
        qtl_mismatch.astype("<f8").tofile(qm_out)
        selected.insert(0, "simulation_index_zero_based", np.arange(WINDOW))
        selected.to_csv(tdir / "variants.tsv", sep="\t", index=False)

        for target in TARGETS:
            a, b, ab_r2 = best_pair(avg_r2, target)
            c_s4, ac_r2 = best_relative(avg_r2, a, target, {a, b})
            c_s5, d_s5, cd_r2 = best_pair(avg_r2, target, {a, b})
            causal_rows.append(
                {
                    "template_id": template_id,
                    "causal_r2_target": target,
                    "a": a,
                    "b": b,
                    "c_s4": c_s4,
                    "c_s5": c_s5,
                    "d_s5": d_s5,
                    "ab_achieved_mean_r2": ab_r2,
                    "ac_achieved_mean_r2": ac_r2,
                    "cd_achieved_mean_r2": cd_r2,
                    "a_variant": selected.loc[a, "variant_id"],
                    "b_variant": selected.loc[b, "variant_id"],
                    "c_s4_variant": selected.loc[c_s4, "variant_id"],
                    "c_s5_variant": selected.loc[c_s5, "variant_id"],
                    "d_s5_variant": selected.loc[d_s5, "variant_id"],
                }
            )

        manifest = {
            "template_id": template_id,
            "locus_index": locus,
            "cell_type": cell,
            "common_variants_full": len(common),
            "window_start_zero_based": start,
            "window_variants": WINDOW,
            "window_bp_min": int(selected["position_GRCh37"].min()),
            "window_bp_max": int(selected["position_GRCh37"].max()),
            "window_selection": window_qc,
            "disease_psd": disease_qc,
            "qtl_psd": qtl_qc,
            "qtl_mismatch_pf50_psd": qtl_mismatch_qc,
            "source_sha256": {
                "sumstats": sha256(sum_path),
                "disease_ld": sha256(disease_path),
                "variants": sha256(variants_path),
                "qtl_ld": sha256(qtl_path),
                "qtl_ld_mismatch_pf50": sha256(qtl_mismatch_path),
            },
            "output_sha256": {
                "disease_ld": sha256(d_out),
                "qtl_ld": sha256(q_out),
                "qtl_ld_mismatch_pf50": sha256(qm_out),
                "variants": sha256(tdir / "variants.tsv"),
            },
        }
        (tdir / "template_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        manifests.append(manifest)

    causal = pd.DataFrame(causal_rows).sort_values(["template_id", "causal_r2_target"])
    causal_path = OUT / "R7B1C_causal_index_map.tsv"
    causal.to_csv(causal_path, sep="\t", index=False)
    grid = pd.read_csv(GRID, sep="\t")
    if len(grid) != 486 or int(grid["replicates"].sum()) != 486000:
        raise RuntimeError("upstream grid identity failed")
    grid.insert(0, "grid_id", [f"R7B1C_G{i:03d}" for i in range(1, len(grid) + 1)])
    grid["template_allocation"] = "odd_rep=T_L02_NK_PF10;even_rep=T_L04_B_IN_PF10"
    grid["disease_beta1"] = float(np.log(1.12))
    grid["disease_beta2_multiplier"] = -0.8
    grid["qtl_beta1"] = 0.30
    grid["qtl_beta2_multiplier"] = -0.8
    grid_path = OUT.parent / "R7B1C_implementation_grid_486.tsv"
    grid.to_csv(grid_path, sep="\t", index=False)
    state = {
        "schema": "R7B1C_TEMPLATE_FREEZE_1.1",
        "status": "PASS",
        "protocol_sha256": sha256(PROTOCOL),
        "upstream_grid_sha256": sha256(GRID),
        "implementation_grid_sha256": sha256(grid_path),
        "causal_map_sha256": sha256(causal_path),
        "templates": manifests,
        "rows": len(grid),
        "replicates": int(grid["replicates"].sum()),
    }
    state_path = OUT.parent / "R7B1C_template_freeze_state.json"
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
