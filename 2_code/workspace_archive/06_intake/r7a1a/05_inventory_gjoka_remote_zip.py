#!/usr/bin/env python3
"""Inventory GJOKA_SUMSTATS.zip using HTTP ranges without downloading 1.18 GB.

The central-directory CRC/size inventory proves the published archive exposes a
matched summary-statistics and covariance-matrix pair for each of 56 loci.  The
small summary-statistics members are read to recover locus coordinate ranges;
the large covariance matrices remain remote until a frozen locus is triggered.
"""
from __future__ import annotations
import csv, io, json, os, re
from pathlib import Path
import requests
from remotezip import RemoteZip

URL="https://www.staff.ncl.ac.uk/heather.cordell/GJOKA_SUMSTATS.zip"
HERE=Path(__file__).resolve()
DEFAULT_ROOT=HERE.parents[2] if (HERE.parents[2]/".git").exists() else HERE.parents[3]
ROOT=Path(os.environ.get("R7_PROJECT_ROOT",DEFAULT_ROOT))
OUT=ROOT/"3_results/01_intake/R7A1A"
OUT.mkdir(parents=True,exist_ok=True)

h=requests.head(URL,allow_redirects=True,timeout=60)
h.raise_for_status()
headers={k.lower():v for k,v in h.headers.items()}
rows=[]; loci=[]
with RemoteZip(URL) as z:
    infos=z.infolist()
    for x in infos:
        rows.append({"member":x.filename,"uncompressed_bytes":x.file_size,
                     "compressed_bytes":x.compress_size,"crc32":f"{x.CRC:08x}"})
    for x in infos:
        m=re.search(r"sumstats_(\d+)\.assoc\.logistic$",x.filename)
        if not m: continue
        text=z.read(x.filename).decode("utf-8","replace")
        parsed=list(csv.DictReader(io.StringIO(text),delimiter=" ",skipinitialspace=True))
        parsed=[r for r in parsed if r and r.get("CHR") and r.get("BP")]
        chroms=sorted({int(r["CHR"]) for r in parsed})
        bps=[int(r["BP"]) for r in parsed]
        idx=int(m.group(1))
        ld=next(i for i in infos if i.filename.endswith(f"covmat_{idx}.ld"))
        loci.append({"locus_index":idx,"chromosomes":";".join(map(str,chroms)),
                     "min_bp_grch37":min(bps),"max_bp_grch37":max(bps),
                     "variant_rows":len(parsed),"sumstats_member":x.filename,
                     "sumstats_crc32":f"{x.CRC:08x}","ld_member":ld.filename,
                     "ld_uncompressed_bytes":ld.file_size,"ld_crc32":f"{ld.CRC:08x}"})

def tsv(path,data):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter="\t",lineterminator="\n")
        w.writeheader(); w.writerows(data)
tsv(OUT/"R7A1A_PBC_GJOKA_remote_member_inventory.tsv",rows)
tsv(OUT/"R7A1A_PBC_GJOKA_locus_ranges.tsv",sorted(loci,key=lambda r:r["locus_index"]))
state={
 "url":URL,"http_content_length":int(headers.get("content-length",0)),
 "last_modified":headers.get("last-modified"),"accept_ranges":headers.get("accept-ranges"),
 "members":len(rows),"sumstats_members":sum("sumstats_" in r["member"] for r in rows),
 "ld_members":sum("covmat_" in r["member"] for r in rows),
 "matched_locus_pairs":len(loci),"central_directory_all_members_have_crc":all(r["crc32"] for r in rows),
 "full_archive_downloaded":False,
 "interpretation":"HTTP-range central directory plus all small sumstats members inspected; large LD members were not downloaded because no R7A1B locus is yet triggered."
}
(OUT/"R7A1A_PBC_GJOKA_remote_inventory_state.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
