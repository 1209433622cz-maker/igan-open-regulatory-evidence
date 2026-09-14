#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import os
import numpy as np, pandas as pd
ap=argparse.ArgumentParser()
ap.add_argument("--locus",required=True); ap.add_argument("--gene",required=True); ap.add_argument("--cell",required=True)
a=ap.parse_args()
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
BED=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bed"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
FAM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.fam"
S=ROOT/f"3_results/03_qtl/R5A2A2/cell_sample_lists/{a.cell}.samples.txt"
Q=ROOT/"3_results/03_qtl/R6A2B0/R6A2B0_OneK1K_8locus_QTL.tsv.gz"
OUT=ROOT/f"3_results/04_integration/R6A2B0/sourceLD/{a.locus.replace('/','_')}_{a.gene}_{a.cell}"
OUT.mkdir(parents=True,exist_ok=True)
fam=pd.read_csv(FAM,sep=r"\s+",header=None,dtype=str); ids=fam.iloc[:,1].tolist(); idx={x:i for i,x in enumerate(ids)}
keep_ids=[x for x in S.read_text(encoding="utf-8").splitlines() if x]; keep=np.array([idx[x] for x in keep_ids],dtype=int)
bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["chr","variant_id","cm","pos","A1","A2"],dtype=str); bim["gi"]=np.arange(len(bim))
q=pd.read_csv(Q,sep="\t"); q=q[(q.locus==a.locus)&(q.gene==a.gene)&(q.cell_type==a.cell)].drop_duplicates("variant_id")
v=q.merge(bim[["variant_id","gi","A1","A2"]],on="variant_id",how="inner",validate="one_to_one")
if len(v)!=len(q): raise RuntimeError(f"QTL/BIM mismatch {len(v)}/{len(q)}")
bps=(len(ids)+3)//4; G=np.empty((len(keep),len(v)),dtype=np.float32)
with BED.open("rb") as f:
    if f.read(3).hex()!="6c1b01": raise RuntimeError("BED magic failure")
    for j,gi in enumerate(v.gi.astype(int)):
        f.seek(3+gi*bps); raw=f.read(bps)
        code=np.fromiter(((b>>s)&3 for b in raw for s in (0,2,4,6)),dtype=np.int8,count=bps*4)[:len(ids)][keep]
        dos=np.where(code==0,2,np.where(code==2,1,np.where(code==3,0,np.nan))).astype(float)
        if np.isnan(dos).any(): dos=np.where(np.isnan(dos),np.nanmean(dos),dos)
        G[:,j]=dos
sd=G.std(0,ddof=1); ok=np.isfinite(sd)&(sd>0); G=G[:,ok]; v=v.loc[ok].reset_index(drop=True)
G=(G-G.mean(0))/G.std(0,ddof=1); R=(G.T@G)/(G.shape[0]-1); R=(R+R.T)/2; np.fill_diagonal(R,1)
G32=G.astype(np.float32); R32=R.astype(np.float32)
np.save(OUT/"standardized_A1_dosage.npy",G32)
np.save(OUT/"signed_A1_correlation.npy",R32)
R32.astype("<f4",copy=False).tofile(OUT/"signed_A1_correlation.float32.bin")
(OUT/"active_donors.txt").write_text("\n".join(keep_ids)+"\n",encoding="utf-8")
v.insert(0,"LD_order_zero_based",np.arange(len(v),dtype=int))
v.to_csv(OUT/"LD_variants.tsv",sep="\t",index=False)
qc={"locus":a.locus,"gene":a.gene,"cell":a.cell,"n_samples":len(keep),"n_variants":len(v),
    "finite":bool(np.isfinite(R).all()),"max_asymmetry":float(np.max(abs(R-R.T))),
    "max_diag_dev":float(np.max(abs(np.diag(R)-1))),"min_eigenvalue":float(np.linalg.eigvalsh(R.astype(float)).min())}
qc["status"]="PASS" if qc["finite"] and qc["max_asymmetry"]<1e-5 and qc["max_diag_dev"]<1e-5 else "HOLD"
(OUT/"sourceLD_QC.json").write_text(json.dumps(qc,indent=2),encoding="utf-8")
print(json.dumps(qc,indent=2))
