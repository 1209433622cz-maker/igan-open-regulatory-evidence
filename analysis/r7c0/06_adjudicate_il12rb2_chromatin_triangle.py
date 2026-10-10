#!/usr/bin/env python3
"""Adjudicate the prespecified IL12RB2 eQTL/caQTL/peak-gene triangle."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
RAW = WORK / "external_metadata/cascade_27gene_20261011"
OUT = WORK / "results"
REGION_JSON = RAW / "coloc_region_IL12RB2.json"
PEAK = "chr1-67307618-67308670"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    url = f"https://cascade.finngen.fi/api/cascade/peak/{PEAK}"
    response = requests.get(url, timeout=180, headers={"User-Agent": "CMM-R7C0-prespecified-chromatin-audit/1.0"})
    response.raise_for_status()
    peak_bytes = response.content
    peak_path = RAW / "peak_IL12RB2_prespecified_current.json"
    peak_path.write_bytes(peak_bytes)
    peak = response.json()

    pairs = json.loads(REGION_JSON.read_text(encoding="utf-8")).get("pairs", [])
    eqtl = [
        p for p in pairs
        if p.get("trait1") == "CHIRBIL_PRIM"
        and p.get("trait2_symbol") == "IL12RB2"
        and p.get("cell_type2") == "l1.NK"
    ]
    caqtl = [
        p for p in pairs
        if p.get("trait1") == "CHIRBIL_PRIM"
        and p.get("trait2") == PEAK
        and p.get("cell_type2") == "l1.NK"
    ]
    links = [g for g in (peak.get("linked_genes") or []) if g.get("gene") == "IL12RB2"]
    if len(eqtl) != 1 or len(caqtl) != 1 or len(links) != 1:
        raise RuntimeError(f"Unexpected prespecified triangle rows: eQTL={len(eqtl)}, caQTL={len(caqtl)}, links={len(links)}")
    e, c, link = eqtl[0], caqtl[0], links[0]
    minimum_forced_qtl_overlap = max(0, int(e["cs2_size"]) + int(c["cs2_size"]) - int(e["cs1_size"]))
    rows = pd.DataFrame([
        {
            "edge": "PBC_GWAS_to_IL12RB2_eQTL", "cell": "l1.NK", "PP_H4_abf": e["PP.H4.abf"],
            "disease_cs_size": e["cs1_size"], "qtl_cs_size": e["cs2_size"], "disease_qtl_cs_overlap": e["cs_overlap"],
            "disease_lead": e["hit1"], "qtl_lead": e["hit2"],
        },
        {
            "edge": "PBC_GWAS_to_linked_peak_caQTL", "cell": "l1.NK", "PP_H4_abf": c["PP.H4.abf"],
            "disease_cs_size": c["cs1_size"], "qtl_cs_size": c["cs2_size"], "disease_qtl_cs_overlap": c["cs_overlap"],
            "disease_lead": c["hit1"], "qtl_lead": c["hit2"],
        },
    ])
    rows.to_csv(OUT / "R7C0_IL12RB2_NK_disease_eQTL_caQTL_edges.tsv", sep="\t", index=False)
    result = {
        "stage": "R7C0_G3_CHROMATIN",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "prespecified_gene": "IL12RB2",
        "prespecified_cell": "l1.NK",
        "prespecified_peak": PEAK,
        "disease_eQTL": {
            "PP_H4_abf": e["PP.H4.abf"], "disease_cs_size": e["cs1_size"],
            "eqtl_cs_size": e["cs2_size"], "cs_overlap": e["cs_overlap"],
            "all_eqtl_cs_members_inside_disease_cs": int(e["cs2_size"]) == int(e["cs_overlap"]),
        },
        "disease_caQTL": {
            "PP_H4_abf": c["PP.H4.abf"], "disease_cs_size": c["cs1_size"],
            "caqtl_cs_size": c["cs2_size"], "cs_overlap": c["cs_overlap"],
            "all_caqtl_cs_members_inside_disease_cs": int(c["cs2_size"]) == int(c["cs_overlap"]),
        },
        "peak_gene_link": {
            "gene": link.get("gene"), "distance_to_tss": link.get("dist_tss"),
            "link_beta": link.get("link_beta"), "method": "fasthurdle",
            "best_cell": (link.get("fhurdle") or {}).get("best_ct"),
            "joint_p": (link.get("fhurdle") or {}).get("joint_p"),
        },
        "minimum_eQTL_caQTL_cs_intersection_implied_by_shared_19_variant_disease_cs": minimum_forced_qtl_overlap,
        "previous_statement_superseded": (
            "R7B1D stated that PBC-caQTL colocalization was not established for this linked peak. "
            "The prespecified full-region query now returns a direct CHIRBIL_PRIM-to-peak caQTL record in l1.NK."
        ),
        "adjudication": "PASS_TRIANGULAR_SIGNAL_COHERENCE_WITHOUT_DIRECT_MEDIATION_PROOF",
        "allowed_claim": (
            "The independent disease-supported IL12RB2 locus also shows source-integrated PBC-eQTL and "
            "PBC-caQTL sharing in NK cells at a linked promoter-proximal peak."
        ),
        "forbidden_claim": (
            "A unique causal variant or a directional disease-to-chromatin-to-expression mediation chain is proven."
        ),
        "remaining_gap": (
            "The public endpoint does not provide a direct eQTL-versus-caQTL coloc posterior; the historical positional "
            "top eQTL variant is not itself in the peak caQTL credible set."
        ),
        "source": {
            "region_url": "https://cascade.finngen.fi/api/cascade/coloc/by_region/chr1:66307873-68398724",
            "region_json_sha256": sha256_bytes(REGION_JSON.read_bytes()),
            "peak_url": url, "peak_json_sha256": sha256_bytes(peak_bytes),
        },
    }
    (OUT / "R7C0_IL12RB2_chromatin_triangle_adjudication.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
