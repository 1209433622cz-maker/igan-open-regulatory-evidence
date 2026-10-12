#!/usr/bin/env python3
from pathlib import Path, PurePosixPath
import tarfile, hashlib, json, re, csv

ROOT=Path(r"H:\SCI2\YR1")
ARCHIVE=ROOT/"1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz"
OUT=ROOT/"1_data/qtl/OneK1K/R6A2A_benchmark_members"
AUDIT=ROOT/"3_results/00_audit/R6A2A"
EXPECTED_BYTES=10344009571
EXPECTED_MD5="e42239480f40abd21f221c0d77c82cc3"
PAT=re.compile(r"OneK1K_(.+?)\.cis_qtl_pairs\.chr(\d+)\.parquet$")
TARGETS={(6,"Mono_C"),(6,"Mono_NC"),(6,"CD4_NC"),(10,"NK"),(16,"Mono_C"),(16,"Mono_NC"),(16,"NK")}

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

OUT.mkdir(parents=True,exist_ok=True); AUDIT.mkdir(parents=True,exist_ok=True)
if ARCHIVE.stat().st_size!=EXPECTED_BYTES: raise RuntimeError("OneK1K archive byte mismatch")
manifest=[]
with ARCHIVE.open("rb") as raw:
    h=HR(raw)
    with tarfile.open(fileobj=h,mode="r|gz") as tf:
        for m in tf:
            if not scientific(m.name) or not m.isfile(): continue
            name=PurePosixPath(m.name).name
            mt=PAT.fullmatch(name)
            select=False; reason=""
            if mt and (int(mt.group(2)),mt.group(1)) in TARGETS:
                select=True; reason="BENCHMARK_PARQUET"
            elif name in {"README","plink_merged.bim"}:
                select=True; reason=name
            if select:
                src=tf.extractfile(m)
                dst=OUT/name
                dig=hashlib.sha256(); n=0
                with dst.open("wb") as w:
                    while True:
                        b=src.read(8*1024*1024)
                        if not b: break
                        w.write(b); dig.update(b); n+=len(b)
                if n!=m.size: raise RuntimeError(f"extract size mismatch {name}")
                manifest.append({"member":m.name,"basename":name,"reason":reason,"bytes":n,"sha256":dig.hexdigest()})
    while h.read(8*1024*1024): pass
audit={
 "archive_bytes":ARCHIVE.stat().st_size,"compressed_bytes_read":h.n,
 "md5":h.md5.hexdigest(),"sha256":h.sha.hexdigest(),
 "expected_md5":EXPECTED_MD5,"selected_files":len(manifest),
 "target_parquet_count":sum(x["reason"]=="BENCHMARK_PARQUET" for x in manifest),
 "gate":"PASS" if h.n==EXPECTED_BYTES and h.md5.hexdigest()==EXPECTED_MD5 and sum(x["reason"]=="BENCHMARK_PARQUET" for x in manifest)==7 else "FAIL"
}
pd=__import__("pandas")
pd.DataFrame(manifest).to_csv(AUDIT/"R6A2A_OneK1K_extracted_manifest.tsv",sep="\t",index=False)
(AUDIT/"R6A2A_OneK1K_archive_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
if audit["gate"]!="PASS": raise SystemExit(2)
