#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path
from urllib.parse import urlparse

EXPECTED = ["HRR1849459","HRR1849460","HRR1849461","HRR1849462","HRR1849463"]
EXPECTED_TOTAL_BYTES = 152_488_497_199
MD5_RE = re.compile(r"^[0-9a-f]{32}$")

p=argparse.ArgumentParser()
p.add_argument("--manifest",type=Path,required=True)
p.add_argument("--out",type=Path,required=True)
a=p.parse_args()

rows=list(csv.DictReader(a.manifest.open(encoding="utf-8-sig"), delimiter="\t"))
errors=[]
runs=[r.get("run_accession","") for r in rows]
if sorted(runs)!=sorted(EXPECTED) or len(rows)!=5:
    errors.append(f"run set mismatch: {runs}")
if len(set(runs))!=5:
    errors.append("duplicate run accession")

total=0
for r in rows:
    run=r.get("run_accession","")
    try:
        b=int(r["expected_bytes"])
        if b<=0: raise ValueError()
        total+=b
    except Exception:
        errors.append(f"{run}: invalid expected_bytes")
    md5=r.get("official_md5","").lower()
    if not MD5_RE.match(md5):
        errors.append(f"{run}: invalid official_md5")
    fn=r.get("archived_file_name","")
    if fn != f"{run}.bam":
        errors.append(f"{run}: archived_file_name mismatch {fn}")
    url=r.get("direct_url","")
    parsed=urlparse(url)
    expected=f"/gsa-human/HRA008003/{run}/{run}.bam"
    if parsed.scheme!="https" or parsed.netloc!="download.cncb.ac.cn" or parsed.path!=expected:
        errors.append(f"{run}: unexpected direct_url {url}")
    if r.get("group")!="PBC" or r.get("tissue")!="liver":
        errors.append(f"{run}: group/tissue mismatch")

if total!=EXPECTED_TOTAL_BYTES:
    errors.append(f"total bytes {total} != {EXPECTED_TOTAL_BYTES}")

state={
  "schema":"R7A1C1B0_MANIFEST_PREFLIGHT_1.0",
  "rows":len(rows),
  "runs":runs,
  "total_expected_bytes":total,
  "total_expected_GiB":total/(1024**3),
  "errors":errors,
  "status":"PASS" if not errors else "FAIL"
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
print(json.dumps(state,indent=2))
if errors: raise SystemExit(2)
