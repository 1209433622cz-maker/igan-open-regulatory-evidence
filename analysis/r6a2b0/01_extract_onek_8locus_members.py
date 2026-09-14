#!/usr/bin/env python3
from pathlib import Path
import os, PurePosixPath
import tarfile, hashlib, json, re
import pandas as pd

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
CODE=Path(__file__).resolve().parent
REQ=pd.read_csv(CODE/"R6A2B0_required_OneK_chr_cell_members.tsv",sep="\t")
TARGETS={(int(r.chromosome),str(r.cell_type_OneK1K)) for r in REQ.itertuples(index=False)}
ARCHIVE=ROOT/"1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz"
OUT=ROOT/"1_data/qtl/OneK1K/R6A2B0_members"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A2B0"; AUD.mkdir(parents=True,exist_ok=True)
EXPECTED_BYTES=10344009571
EXPECTED_MD5="e42239480f40abd21f221c0d77c82cc3"
PAT=re.compile(r"OneK1K_(.+?)\.cis_qtl_pairs\.chr(\d+)\.parquet$")

class HashReader:
    def __init__(self,raw):
        self.raw=raw; self.md5=hashlib.md5(); self.sha=hashlib.sha256(); self.n=0
    def read(self,size=-1):
        b=self.raw.read(size)
        if b:
            self.md5.update(b); self.sha.update(b); self.n+=len(b)
        return b
    def readable(self): return True

def scientific(name):
    p=PurePosixPath(name.removeprefix("./"))
    return "__MACOSX" not in p.parts and not p.name.startswith("._")

if ARCHIVE.stat().st_size!=EXPECTED_BYTES:
    raise RuntimeError(f"OneK archive byte mismatch {ARCHIVE.stat().st_size} != {EXPECTED_BYTES}")

manifest=[]
with ARCHIVE.open("rb") as raw:
    hr=HashReader(raw)
    with tarfile.open(fileobj=hr,mode="r|gz") as tf:
        for m in tf:
            if not m.isfile() or not scientific(m.name): continue
            base=PurePosixPath(m.name).name
            mt=PAT.fullmatch(base)
            select=False; reason=""
            if mt and (int(mt.group(2)),mt.group(1)) in TARGETS:
                select=True; reason="FROZEN_CHR_CELL_PARQUET"
            elif base in {"README","plink_merged.bim"}:
                select=True; reason=base
            if not select: continue
            src=tf.extractfile(m); dst=OUT/base
            dig=hashlib.sha256(); n=0
            with dst.open("wb") as w:
                while True:
                    b=src.read(8*1024*1024)
                    if not b: break
                    w.write(b); dig.update(b); n+=len(b)
            if n!=m.size: raise RuntimeError(f"size mismatch {base}")
            manifest.append({"member":m.name,"basename":base,"reason":reason,"bytes":n,"sha256":dig.hexdigest()})
    while hr.read(8*1024*1024): pass

df=pd.DataFrame(manifest)
actual=set()
for x in df[df.reason=="FROZEN_CHR_CELL_PARQUET"].basename:
    mt=PAT.fullmatch(x); actual.add((int(mt.group(2)),mt.group(1)))
missing=sorted(TARGETS-actual)
audit={
  "archive_bytes":ARCHIVE.stat().st_size,
  "compressed_bytes_read":hr.n,
  "md5":hr.md5.hexdigest(),
  "sha256":hr.sha.hexdigest(),
  "required_chr_cell_members":len(TARGETS),
  "extracted_chr_cell_members":len(actual),
  "missing_targets":missing,
  "gate":"PASS" if hr.n==EXPECTED_BYTES and hr.md5.hexdigest()==EXPECTED_MD5 and not missing else "FAIL"
}
df.to_csv(AUD/"R6A2B0_OneK_extracted_manifest.tsv",sep="\t",index=False)
(AUD/"R6A2B0_OneK_archive_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
if audit["gate"]!="PASS": raise SystemExit(2)
