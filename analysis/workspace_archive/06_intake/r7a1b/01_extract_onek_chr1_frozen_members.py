#!/usr/bin/env python3
from pathlib import Path, PurePosixPath
import os, tarfile, hashlib, json, re
import pandas as pd

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
CODE=ROOT/"2_code/06_intake/r7a1b"
F=pd.read_csv(CODE/"R7A1B_frozen_9_combinations.tsv",sep="\t")
TARGETS={(1,str(x)) for x in sorted(F.cell_type.unique())}
ARCHIVE=ROOT/"1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz"
OUT=ROOT/"1_data/qtl/OneK1K/R7A1B_chr1_members"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R7A1B"; AUD.mkdir(parents=True,exist_ok=True)
EXPECTED_BYTES=10344009571
EXPECTED_MD5="e42239480f40abd21f221c0d77c82cc3"
PAT=re.compile(r"OneK1K_(.+?)\.cis_qtl_pairs\.chr(\d+)\.parquet$")

class HR:
    def __init__(self,raw):
        self.raw=raw; self.md5=hashlib.md5(); self.sha=hashlib.sha256(); self.n=0
    def read(self,size=-1):
        b=self.raw.read(size)
        if b: self.md5.update(b); self.sha.update(b); self.n+=len(b)
        return b
    def readable(self): return True

def scientific(name):
    p=PurePosixPath(name.removeprefix("./"))
    return "__MACOSX" not in p.parts and not p.name.startswith("._")

if not ARCHIVE.exists(): raise FileNotFoundError(ARCHIVE)
if ARCHIVE.stat().st_size!=EXPECTED_BYTES: raise RuntimeError("OneK archive byte mismatch")
manifest=[]
with ARCHIVE.open("rb") as raw:
    h=HR(raw)
    with tarfile.open(fileobj=h,mode="r|gz") as tf:
        for m in tf:
            if not m.isfile() or not scientific(m.name): continue
            base=PurePosixPath(m.name).name
            mt=PAT.fullmatch(base)
            reason=None
            if mt and (int(mt.group(2)),mt.group(1)) in TARGETS: reason="FROZEN_CHR1_CELL"
            elif base in {"README","plink_merged.bim"}: reason=base
            if reason is None: continue
            src=tf.extractfile(m); dst=OUT/base
            dig=hashlib.sha256(); n=0
            with dst.open("wb") as w:
                while True:
                    b=src.read(8*1024*1024)
                    if not b: break
                    w.write(b);dig.update(b);n+=len(b)
            if n!=m.size: raise RuntimeError(f"extract size mismatch: {base}")
            manifest.append({"member":m.name,"basename":base,"reason":reason,"bytes":n,"sha256":dig.hexdigest()})
    while h.read(8*1024*1024): pass
df=pd.DataFrame(manifest)
actual=set()
for b in df.loc[df.reason=="FROZEN_CHR1_CELL","basename"]:
    m=PAT.fullmatch(b); actual.add((int(m.group(2)),m.group(1)))
missing=sorted(TARGETS-actual)
state={"archive_bytes":ARCHIVE.stat().st_size,"bytes_read":h.n,"md5":h.md5.hexdigest(),"sha256":h.sha.hexdigest(),
       "expected_md5":EXPECTED_MD5,"required_cell_members":len(TARGETS),"extracted_cell_members":len(actual),
       "missing":missing,"gate":"PASS" if h.n==EXPECTED_BYTES and h.md5.hexdigest()==EXPECTED_MD5 and not missing else "FAIL"}
df.to_csv(AUD/"R7A1B_OneK_extraction_manifest.tsv",sep="\t",index=False)
(AUD/"R7A1B_OneK_archive_gate.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
if state["gate"]!="PASS": raise SystemExit(2)
