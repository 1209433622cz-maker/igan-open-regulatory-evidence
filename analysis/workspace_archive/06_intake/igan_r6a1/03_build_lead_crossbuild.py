from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(r"H:\SCI2\YR1")
INPUT = ROOT / "3_results/04_integration/R6A1/IgAN_24_non_HLA_locus_leads.tsv"
OUT_TSV = ROOT / "3_results/04_integration/R6A1/IgAN_24_non_HLA_locus_leads_crossbuild.tsv"
OUT_JSON = ROOT / "3_results/00_audit/R6A1/IgAN_lead_NCBI_RefSNP_crossbuild_audit.json"
CACHE = ROOT / "1_data/reference/variant_identity/IgAN_R6A1_NCBI_RefSNP"
CACHE.mkdir(parents=True, exist_ok=True)


def assembly_spdi(record: dict, name: str) -> dict | None:
    placements = record.get("primary_snapshot_data", {}).get("placements_with_allele", [])
    # Prefer the assembled chromosome (NC_) over alternate/patch scaffolds.
    placements = sorted(placements, key=lambda p: (not str(p.get("seq_id", "")).startswith("NC_"), str(p.get("seq_id", ""))))
    for placement in placements:
        assemblies = [x.get("assembly_name") for x in placement.get("placement_annot", {}).get("seq_id_traits_by_assembly", [])]
        if any(x and x.startswith(name) for x in assemblies):
            spdis = [a.get("allele", {}).get("spdi", {}) for a in placement.get("alleles", [])]
            if not spdis:
                continue
            positions = {int(x["position"]) + 1 for x in spdis if "position" in x}
            return {"seq_id": placement.get("seq_id"), "position_1based": min(positions), "spdis": spdis}
    return None


df = pd.read_csv(INPUT, sep="\t")
session = requests.Session()
session.headers["User-Agent"] = "CMM-R6A1/1.0 open-data scientific audit"
details = []
rows = []
for row in df.itertuples(index=False):
    rsnum = str(row.rsid).lower().removeprefix("rs")
    cache = CACHE / f"rs{rsnum}.json"
    url = f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{rsnum}"
    if cache.exists():
        record = json.loads(cache.read_text(encoding="utf-8"))
        source = "cache"
    else:
        response = session.get(url, timeout=60)
        response.raise_for_status()
        record = response.json()
        cache.write_text(json.dumps(record), encoding="utf-8")
        source = "download"
        time.sleep(0.12)
    resolved_rsid = str(row.rsid)
    merged_into = record.get("merged_snapshot_data", {}).get("merged_into", [])
    if not record.get("primary_snapshot_data") and merged_into:
        resolved_rsid = f"rs{merged_into[0]}"
        resolved_url = f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{merged_into[0]}"
        resolved_cache = CACHE / f"{resolved_rsid}.json"
        if resolved_cache.exists():
            record = json.loads(resolved_cache.read_text(encoding="utf-8"))
        else:
            response = session.get(resolved_url, timeout=60)
            response.raise_for_status()
            record = response.json()
            resolved_cache.write_text(json.dumps(record), encoding="utf-8")
            time.sleep(0.12)
    b37 = assembly_spdi(record, "GRCh37")
    b38 = assembly_spdi(record, "GRCh38")
    delta37 = abs(b37["position_1based"] - int(row.position_GRCh37)) if b37 else None
    # The withdrawn chr14 indel rs751081288 was merged into rs57707137 and
    # normalized one base to the right. This is an allowed representation shift.
    matched = bool(b37 and delta37 <= (1 if resolved_rsid != str(row.rsid) else 0))
    item = row._asdict()
    item.update({
        "position_GRCh38": b38["position_1based"] if b38 else None,
        "GRCh37_NCBI_position": b37["position_1based"] if b37 else None,
        "GRCh37_matches_published": matched,
        "GRCh37_position_delta": delta37,
        "resolved_rsid": resolved_rsid,
        "NCBI_source": url,
    })
    rows.append(item)
    details.append({"rsid": row.rsid, "resolved_rsid": resolved_rsid, "url": url, "cache": str(cache), "source": source, "GRCh37": b37, "GRCh38": b38, "published_GRCh37": int(row.position_GRCh37), "GRCh37_position_delta": delta37, "GRCh37_matches_published": matched})
    print(row.rsid, row.position_GRCh37, item["position_GRCh38"], matched, flush=True)

out = pd.DataFrame(rows)
out.to_csv(OUT_TSV, sep="\t", index=False)
audit = {
    "service": "NCBI Variation Services RefSNP API",
    "n_loci": len(details),
    "GRCh38_positions_resolved": sum(x["GRCh38"] is not None for x in details),
    "GRCh37_positions_matching_published": sum(x["GRCh37_matches_published"] for x in details),
    "status": "PASS" if all(x["GRCh38"] and x["GRCh37_matches_published"] for x in details) else "FAIL",
    "rows": details,
}
OUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in audit.items() if k != "rows"}, indent=2), flush=True)
