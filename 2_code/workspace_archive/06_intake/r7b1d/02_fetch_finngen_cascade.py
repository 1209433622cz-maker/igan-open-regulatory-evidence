#!/usr/bin/env python3
"""Fetch current public FinnGen/CASCADE aggregate bytes for R7B1D."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "3_results/01_intake/R7B1D/finngen_cascade_20261009"
BASE = "https://cascade.finngen.fi"


def region_filter(start: int, end: int) -> str:
    return f"chromosome in '1' and position ge {start} and position le {end}"


def eqtl_url(gene: str, cells: str, start: int, end: int) -> str:
    query = urllib.parse.urlencode({
        "filter": region_filter(start, end), "traits": gene, "cts": cells, "pmax": "1"
    })
    return f"{BASE}/api/cascade/region/eqtl/lz-multi/?{query}"


def caqtl_url(peak: str, cells: str, start: int, end: int) -> str:
    query = urllib.parse.urlencode({
        "filter": region_filter(start, end), "traits": peak, "cts": cells, "pmax": "1"
    })
    return f"{BASE}/api/cascade/region/caqtl/lz-multi/?{query}"


def gwas_url(start: int, end: int) -> str:
    return (
        f"{BASE}/api/finngen/region/CHIRBIL_PRIM/lz-results/?filter="
        + urllib.parse.quote(region_filter(start, end))
    )


QUERIES = {
    "me": f"{BASE}/api/v1/me",
    "phenos_pbc": f"{BASE}/api/finngen/phenos?q=PBC&limit=200",
    "phenos_chirbil": f"{BASE}/api/finngen/phenos?q=CHIRBIL&limit=200",
    "autocomplete_pbc_phenotype": f"{BASE}/api/cascade/autocomplete?q=CHIRBIL_PRIM&limit=20",
    "manhattan_pbc": f"{BASE}/api/finngen/manhattan/CHIRBIL_PRIM",
    "gene_il12rb2": f"{BASE}/api/cascade/gene/IL12RB2",
    "gene_fcrl3": f"{BASE}/api/cascade/gene/FCRL3",
    "peak_il12rb2_anchor": f"{BASE}/api/cascade/peak/chr1-67307618-67308670",
    "coloc_il12rb2_variant1": f"{BASE}/api/cascade/coloc/by_variant/1-67307966-T-C?include_variants=true",
    "coloc_il12rb2_variant2": f"{BASE}/api/cascade/coloc/by_variant/1-67308980-A-G?include_variants=true",
    "coloc_fcrl3_marginal": f"{BASE}/api/cascade/coloc/by_variant/1-157701026-A-G?include_variants=true",
    "coloc_fcrl3_anchor": f"{BASE}/api/cascade/coloc/by_variant/1-157699488-C-T?include_variants=true",
    "coloc_fcrl3_region": f"{BASE}/api/cascade/coloc/by_region/chr1:156676481-158700769",
    "eqtl_il12rb2_nk": eqtl_url("ENSG00000081985", "l1.NK,l2.NK,l1.PBMC", 67200000, 67500000),
    "eqtl_fcrl3_b_cd8": eqtl_url(
        "ENSG00000160856", "l1.B,l2.B_intermediate,l2.B_memory,l1.CD8_T,l2.CD8_TEM", 157500000, 157900000
    ),
    "caqtl_il12rb2_anchor": caqtl_url(
        "chr1-67307618-67308670", "l1.NK,l2.NK,l1.PBMC,l2.CD8_TEM", 67200000, 67500000
    ),
    "gwas_pbc_il12rb2_region": gwas_url(67200000, 67500000),
    "gwas_pbc_fcrl3_region": gwas_url(157500000, 157900000),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "CMM-R7B1D-public-reproducibility-audit/1.0"
    receipts = []
    for name, url in QUERIES.items():
        response = session.get(url, timeout=180)
        payload = response.content
        path = OUT / f"{name}.json"
        path.write_bytes(payload)
        valid_json = True
        try:
            response.json()
        except Exception:
            valid_json = False
        receipts.append({
            "name": name,
            "url": url,
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
            "valid_json": valid_json,
            "local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
        })
        if response.status_code != 200 or not valid_json:
            raise RuntimeError(f"Public API retrieval failed: {name} status={response.status_code}")
        time.sleep(0.15)
    receipt = pd.DataFrame(receipts)
    receipt.to_csv(OUT / "R7B1D_finngen_api_receipts.tsv", sep="\t", index=False)
    (OUT / "R7B1D_finngen_api_receipts.json").write_text(
        json.dumps(receipts, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(receipt[["name", "status_code", "bytes", "sha256"]].to_string(index=False))


if __name__ == "__main__":
    main()
