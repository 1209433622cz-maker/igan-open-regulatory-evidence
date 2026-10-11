#!/usr/bin/env python3
from pathlib import Path
import os,json,hashlib,zlib
import pandas as pd
from remotezip import RemoteZip

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
TR=ROOT/"3_results/04_integration/R7A1B/R7A1B_multisignal_triggers.tsv"
OUT=ROOT/"1_data/study_inputs/PBC_GJOKA/R7A1B";OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R7A1B";AUD.mkdir(parents=True,exist_ok=True)
URL="https://www.staff.ncl.ac.uk/heather.cordell/GJOKA_SUMSTATS.zip"
t=pd.read_csv(TR,sep="\t")
idxs=sorted(set(map(int,t.gjoka_locus_index)))
rows=[]
with RemoteZip(URL) as z:
    infos={i.filename:i for i in z.infolist()}
    for idx in idxs:
        for name in [f"GJOKA_SUMSTATS/sumstats_{idx}.assoc.logistic",f"GJOKA_SUMSTATS/covmat_{idx}.ld"]:
            inf=infos[name];data=z.read(name);dest=OUT/Path(name).name;dest.write_bytes(data)
            crc=f"{zlib.crc32(data)&0xffffffff:08x}"
            if crc!=f"{inf.CRC:08x}" or len(data)!=inf.file_size: raise RuntimeError(f"member identity fail {name}")
            rows.append({"locus_index":idx,"member":name,"bytes":len(data),"crc32":crc,"sha256":hashlib.sha256(data).hexdigest()})
pd.DataFrame(rows).to_csv(AUD/"R7A1B_GJOKA_target_member_receipt.tsv",sep="\t",index=False)
print(json.dumps({"loci":idxs,"members":len(rows),"status":"PASS"},indent=2))
