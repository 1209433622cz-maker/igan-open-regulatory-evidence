#!/usr/bin/env python3
"""Build a deduplicated ledger of action records and retained project stages."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11"
OUT = AUDIT / "records"
OUT.mkdir(parents=True, exist_ok=True)

EXCLUDE = (".qiteng_v03242_runtime", "tools", ".git")
PAT = re.compile(r"(?:^|[/\\])99_[^/\\]*(?:行动记录|Action|记录)[^/\\]*\.md$", re.I)
STAGE = re.compile(r"(R\d+(?:[A-Z]+\d*)*(?:_v\d+)?)", re.I)
DATE = re.compile(r"(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def preference(rel: str) -> tuple[int, int, str]:
    p = rel.replace("\\", "/").lower()
    if p.startswith("7.report/rounds/"): rank = 0
    elif p.startswith("7.report/current/"): rank = 1
    elif p.startswith("7.report/"): rank = 2
    elif p.startswith("5_manuscript/") or p.startswith("5_analysis/"): rank = 3
    elif p.startswith("6_release/"): rank = 4
    elif p.startswith("9.version/"): rank = 5
    elif p.startswith("github/"): rank = 6
    else: rank = 7
    return (rank, len(rel), rel.lower())


items = []
for p in ROOT.rglob("*.md"):
    try:
        rel = p.relative_to(ROOT).as_posix()
    except ValueError:
        continue
    if any(part in EXCLUDE for part in p.parts):
        continue
    if not PAT.search(rel):
        continue
    raw = p.read_text(encoding="utf-8", errors="replace")
    title = next((ln.lstrip("# ").strip() for ln in raw.splitlines() if ln.startswith("#")), p.stem)
    stage_match = STAGE.search(p.name) or STAGE.search(rel)
    date_match = DATE.search(p.name) or DATE.search(rel)
    items.append({
        "sha256": sha256(p),
        "stage": stage_match.group(1).upper() if stage_match else "UNRESOLVED",
        "date": "-".join(date_match.groups()) if date_match else "",
        "title": title,
        "relative_path": rel,
        "size_bytes": p.stat().st_size,
        "modified_local": p.stat().st_mtime,
    })

by_hash = defaultdict(list)
for x in items: by_hash[x["sha256"]].append(x)
canonical = []
members = []
for h, grp in by_hash.items():
    grp = sorted(grp, key=lambda x: preference(x["relative_path"]))
    lead = dict(grp[0])
    lead["exact_copies"] = len(grp)
    lead["alternate_paths"] = ";".join(x["relative_path"] for x in grp[1:]) or "NONE"
    canonical.append(lead)
    for x in grp:
        members.append({**x, "canonical_relative_path": lead["relative_path"], "exact_copies": len(grp)})

canonical.sort(key=lambda x: (x["date"], x["stage"], x["relative_path"]))
members.sort(key=lambda x: (x["canonical_relative_path"], x["relative_path"]))

def write_tsv(path: Path, data: list[dict]):
    if not data: return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(data)

write_tsv(OUT / "R7C3_action_record_canonical_ledger.tsv", canonical)
write_tsv(OUT / "R7C3_action_record_all_copies.tsv", members)

stage_summary = defaultdict(lambda: {"canonical_records": 0, "first_date": "", "last_date": "", "canonical_paths": []})
for x in canonical:
    s = stage_summary[x["stage"]]
    s["canonical_records"] += 1
    s["canonical_paths"].append(x["relative_path"])
    if x["date"]:
        s["first_date"] = min(filter(None, [s["first_date"], x["date"]])) if s["first_date"] else x["date"]
        s["last_date"] = max(filter(None, [s["last_date"], x["date"]])) if s["last_date"] else x["date"]
stage_rows = [{"stage": k, "canonical_records": v["canonical_records"], "first_date": v["first_date"], "last_date": v["last_date"], "canonical_paths": ";".join(v["canonical_paths"])} for k, v in sorted(stage_summary.items())]
write_tsv(OUT / "R7C3_stage_record_summary.tsv", stage_rows)

state = {
    "action_record_files_found": len(items),
    "unique_action_record_contents": len(canonical),
    "exact_duplicate_action_record_copies": len(items) - len(canonical),
    "resolved_stage_tokens": len({x["stage"] for x in canonical if x["stage"] != "UNRESOLVED"}),
    "unresolved_records": sum(x["stage"] == "UNRESOLVED" for x in canonical),
}
(OUT / "R7C3_action_record_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
