#!/usr/bin/env python3
"""Fail-closed spot audit of a fully downloaded HRA008003 BAM before full target scan."""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import pysam

p=argparse.ArgumentParser()
p.add_argument("--bam",type=Path,required=True)
p.add_argument("--run",required=True)
p.add_argument("--out",type=Path,required=True)
p.add_argument("--min-records",type=int,default=500000)
p.add_argument("--max-records",type=int,default=5000000)
p.add_argument("--min-xf8",type=int,default=1000)
p.add_argument("--allow-truncated-test",action="store_true",
               help="QA only: allow a deliberately truncated prefix; production runner never sets this")
a=p.parse_args()

counts=collections.Counter()
examples=[]
with pysam.AlignmentFile(str(a.bam),"rb",check_sq=False,ignore_truncation=a.allow_truncated_test) as bam:
    header=bam.header.to_dict()
    pg=header.get("PG",[])
    for i,rec in enumerate(bam.fetch(until_eof=True),start=1):
        counts["records"]+=1
        if rec.has_tag("xf"):
            counts["has_xf"]+=1
            try:
                xf=int(rec.get_tag("xf"))
            except Exception:
                counts["bad_xf"]+=1
                xf=0
            if xf & 8:
                counts["xf8"]+=1
                if rec.has_tag("CB"): counts["xf8_CB"]+=1
                if rec.has_tag("GN"):
                    counts["xf8_GN"]+=1
                    gn=str(rec.get_tag("GN"))
                    if gn and ";" not in gn: counts["xf8_unambiguous_GN"]+=1
                if rec.has_tag("UB"): counts["xf8_UB"]+=1
                if len(examples)<5:
                    examples.append({
                      "CB": rec.get_tag("CB") if rec.has_tag("CB") else None,
                      "GN": rec.get_tag("GN") if rec.has_tag("GN") else None,
                      "xf": xf
                    })
        # The BAM is coordinate sorted. Its first genomic slice can contain
        # almost no molecule representatives, so a fixed 500k prefix creates
        # false failures. Inspect at least min_records, then stop as soon as
        # enough real xf-bit-8 records have been observed, with a hard cap.
        if i>=a.min_records and counts["xf8"]>=a.min_xf8:
            break
        if i>=a.max_records:
            break

xf8=counts["xf8"]
errors=[]
if counts["records"]<a.min_records:
    errors.append(f"too few records inspected: {counts['records']} < {a.min_records}")
if xf8<a.min_xf8:
    errors.append(f"too few xf bit8 molecule representatives: {xf8}")
for tagkey in ("xf8_CB","xf8_GN"):
    frac=(counts[tagkey]/xf8) if xf8 else 0
    if frac<0.90:
        errors.append(f"{tagkey} fraction among xf8 records <0.90: {frac:.4f}")
unamb=(counts["xf8_unambiguous_GN"]/xf8) if xf8 else 0
if unamb<0.70:
    errors.append(f"unambiguous GN fraction among xf8 records <0.70: {unamb:.4f}")

out={
  "schema":"R7A1C1B1_BAM_SCHEMA_PREFLIGHT_1.1",
  "run":a.run,
  "bam":str(a.bam),
  "records_inspected":counts["records"],
  "sampling_rule":{
    "min_records":a.min_records,
    "max_records":a.max_records,
    "stop_after_min_xf8":a.min_xf8,
    "coordinate_sorted_adaptive_prefix":True
  },
  "counts":dict(counts),
  "fractions":{
    "CB_among_xf8": counts["xf8_CB"]/xf8 if xf8 else 0,
    "GN_among_xf8": counts["xf8_GN"]/xf8 if xf8 else 0,
    "UB_among_xf8": counts["xf8_UB"]/xf8 if xf8 else 0,
    "unambiguous_GN_among_xf8": unamb
  },
  "program_header":pg,
  "examples":examples,
  "errors":errors,
  "status":"PASS" if not errors else "FAIL"
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
if errors: raise SystemExit(2)
