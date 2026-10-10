#!/usr/bin/env python3
"""Freeze all 92 stable-H4 comparisons, then audit current CASCADE coverage.

The freeze is produced and hashed before the first network request.  CASCADE
queries therefore cannot alter which genes or cell contexts are inspected.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(r"H:\SCI2\YR1")
REPO = ROOT / "github/igan-open-regulatory-evidence"
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
OUT = WORK / "results"
RAW = WORK / "external_metadata/cascade_27gene_20261011"
SOURCE = REPO / "results/r7b3a/supplements/S5/S5_642_PF10_PF50_classifications.tsv"
BASE = "https://cascade.finngen.fi"


CELL_TO_L1 = {
    "B_IN": "l1.B", "B_MEM": "l1.B",
    "CD4_ET": "l1.CD4_T", "CD4_NC": "l1.CD4_T",
    "CD8_ET": "l1.CD8_T", "CD8_NC": "l1.CD8_T", "CD8_S100B": "l1.CD8_T",
    "DC": "l1.DC", "Mono_C": "l1.Mono", "Mono_NC": "l1.Mono",
    "NK": "l1.NK", "NK_R": "l1.NK",
}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def get_json(session: requests.Session, name: str, url: str) -> tuple[dict, dict]:
    response = session.get(url, timeout=180)
    payload = response.content
    path = RAW / f"{name}.json"
    path.write_bytes(payload)
    receipt = {
        "name": name, "url": url, "status_code": response.status_code,
        "bytes": len(payload), "sha256": digest_bytes(payload),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    }
    response.raise_for_status()
    return response.json(), receipt


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    master = pd.read_csv(SOURCE, sep="\t")
    freeze = master.loc[
        master["PF10_multisignal_state"].eq("H4_SUPPORTED_STABLE"),
        ["comparison_id", "locus_index", "gene", "cell_type", "PF10_multisignal_state", "pf10_l10_best_h4", "pf10_l10_best_h4_ratio"],
    ].sort_values(["locus_index", "gene", "cell_type"]).reset_index(drop=True)
    if len(freeze) != 92 or freeze["gene"].nunique() != 27:
        raise RuntimeError(f"Unexpected stable-H4 universe: rows={len(freeze)}, genes={freeze['gene'].nunique()}")
    freeze_path = OUT / "R7C0_frozen_92_stableH4_comparisons.tsv"
    freeze.to_csv(freeze_path, sep="\t", index=False)
    freeze_receipt = {
        "created_before_network_queries": True,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE), "source_sha256": digest_path(SOURCE),
        "path": str(freeze_path), "sha256": digest_path(freeze_path),
        "rows": len(freeze), "genes": freeze["gene"].nunique(),
        "cells": freeze["cell_type"].nunique(), "loci": freeze["locus_index"].nunique(),
    }
    (OUT / "R7C0_frozen_92_receipt.json").write_text(json.dumps(freeze_receipt, indent=2), encoding="utf-8")

    session = requests.Session()
    session.headers["User-Agent"] = "CMM-R7C0-prespecified-27gene-CASCADE-audit/1.0"
    receipts, gene_rows, coloc_rows = [], [], []
    for gene in sorted(freeze["gene"].unique()):
        encoded_gene = urllib.parse.quote(str(gene), safe="")
        try:
            gj, receipt = get_json(session, f"gene_{gene}", f"{BASE}/api/cascade/gene/{encoded_gene}")
            receipts.append(receipt)
        except Exception as exc:
            gene_rows.append({"gene": gene, "gene_endpoint_status": "FAIL", "error": repr(exc)})
            continue
        g = gj.get("gene") or {}
        eqtl_q = gj.get("eqtl_q") or {}
        caqtl_q = gj.get("caqtl_q") or {}
        target = freeze[freeze["gene"].eq(gene)]
        mapped = sorted({CELL_TO_L1[c] for c in target["cell_type"]})
        relevant_eqtl = {c: eqtl_q.get(c) for c in mapped}
        relevant_eqtl_pass = {c: (q is not None and q < 0.05) for c, q in relevant_eqtl.items()}
        gene_rows.append({
            "gene": gene,
            "gene_endpoint_status": "PASS",
            "ensg": g.get("ensembl"), "chrom": g.get("chrom"), "start": g.get("start"), "end": g.get("end"),
            "stable_h4_comparisons": len(target), "onek_cells": ",".join(sorted(target["cell_type"].unique())),
            "mapped_cascade_l1_cells": ",".join(mapped),
            "cascade_eqtl_cell_count": len(eqtl_q), "cascade_caqtl_cell_count": len(caqtl_q),
            "relevant_l1_eqtl_q_lt_0_05": sum(relevant_eqtl_pass.values()),
            "relevant_l1_eqtl_q_json": json.dumps(relevant_eqtl, sort_keys=True),
            "top_variant_count": len(gj.get("top_variants") or []),
            "linked_peak_count": len(gj.get("peaks") or []),
        })
        chrom, start, end = g.get("chrom"), g.get("start"), g.get("end")
        if chrom and start and end:
            region = f"{chrom}:{max(1, int(start)-1_000_000)}-{int(end)+1_000_000}"
            try:
                cj, receipt = get_json(session, f"coloc_region_{gene}", f"{BASE}/api/cascade/coloc/by_region/{region}")
                receipts.append(receipt)
                all_pairs = cj.get("pairs") or []
                pairs = [p for p in all_pairs if p.get("trait1") == "CHIRBIL_PRIM" and p.get("trait2_symbol") == gene]
                for p in pairs:
                    coloc_rows.append({
                        "gene": gene, "cell_type": p.get("cell_type2"), "gwas_release": p.get("version1"),
                        "gwas_lead": p.get("hit1"), "eqtl_lead": p.get("hit2"),
                        "PP_H4_abf": p.get("PP.H4.abf"), "clpp": p.get("clpp"), "clpa": p.get("clpa"),
                        "cs_gwas_size": p.get("cs1_size"), "cs_eqtl_size": p.get("cs2_size"),
                        "cs_overlap": p.get("cs_overlap"), "nsnps": p.get("nsnps"),
                    })
            except Exception as exc:
                receipts.append({"name": f"coloc_region_{gene}", "url": region, "error": repr(exc)})
        time.sleep(0.10)

    genes_df = pd.DataFrame(gene_rows)
    coloc_df = pd.DataFrame(coloc_rows)
    genes_df.to_csv(OUT / "R7C0_CASCADE_27gene_coverage.tsv", sep="\t", index=False)
    coloc_df.to_csv(OUT / "R7C0_CASCADE_PBC_coloc_in_fixed_27genes.tsv", sep="\t", index=False)
    pd.DataFrame(receipts).to_csv(OUT / "R7C0_CASCADE_API_receipts.tsv", sep="\t", index=False)
    summary = {
        "stage": "R7C0_G3",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "prespecified_comparisons": 92,
        "prespecified_genes": 27,
        "gene_endpoint_pass": int(genes_df["gene_endpoint_status"].eq("PASS").sum()),
        "genes_with_relevant_broad_cell_eqtl_q_lt_0_05": int((genes_df.get("relevant_l1_eqtl_q_lt_0_05", 0) > 0).sum()),
        "fixed_genes_with_PBC_eQTL_coloc_records": int(coloc_df["gene"].nunique()) if not coloc_df.empty else 0,
        "PBC_eQTL_coloc_record_count": len(coloc_df),
        "genes_with_PBC_eQTL_PP_H4_ge_0_8": int(coloc_df.loc[coloc_df["PP_H4_abf"].ge(0.8), "gene"].nunique()) if not coloc_df.empty else 0,
        "freeze_receipt": freeze_receipt,
        "interpretation_boundary": (
            "CASCADE current integration uses FinnGen R12 disease statistics and its molecular-QTL resource. "
            "Coverage and PBC-eQTL records are prespecified external-context evidence; they do not create participant-independent disease replication."
        ),
    }
    (OUT / "R7C0_CASCADE_27gene_coverage_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
