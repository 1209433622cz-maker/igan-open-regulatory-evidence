#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--cell",required=True)
ap.add_argument("--gene",required=True)
ap.add_argument("--root",default=r"H:\SCI2\YR1")
args=ap.parse_args()
ROOT=Path(args.root)
BED=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bed"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
FAM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.fam"
SAMPLES=ROOT/f"3_results/03_qtl/R5A2A2/cell_sample_lists/{args.cell}.samples.txt"
QTL=ROOT/"3_results/03_qtl/R5A2B/OneK1K_chr5_bounded_region_pairs.tsv.gz"
OUT=ROOT/f"3_results/04_integration/R5A2B/sourceLD/{args.cell}_{args.gene}"
OUT.mkdir(parents=True,exist_ok=True)

fam=pd.read_csv(FAM,sep=r"\s+",header=None,dtype=str); ids=fam.iloc[:,1].tolist(); idx={x:i for i,x in enumerate(ids)}
keep_ids=[x.strip() for x in SAMPLES.read_text(encoding="utf-8").splitlines() if x.strip()]
missing=[x for x in keep_ids if x not in idx]
if missing: raise RuntimeError(f"Samples missing from FAM: {missing[:5]}")
keep=np.array([idx[x] for x in keep_ids],dtype=int)

bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["chr","variant_id","cm","pos","A1","A2"],dtype=str)
bim["global_index"]=np.arange(len(bim))
q=pd.read_csv(QTL,sep="\t",compression="gzip")
q=q[(q.cell_type==args.cell)&(q.phenotype_id==args.gene)].drop_duplicates("variant_id")
v=q.merge(bim[["variant_id","global_index","A1","A2"]],on="variant_id",how="inner",validate="one_to_one")
if len(v)!=len(q): raise RuntimeError(f"QTL/BIM coverage mismatch {len(v)}/{len(q)}")
bps=(len(ids)+3)//4
G=np.empty((len(keep),len(v)),dtype=np.float32)
with BED.open("rb") as f:
    if f.read(3).hex()!="6c1b01": raise RuntimeError("BED magic failure")
    for j,gi in enumerate(v.global_index.astype(int)):
        f.seek(3+gi*bps); raw=f.read(bps)
        codes=np.fromiter(((b>>s)&3 for b in raw for s in (0,2,4,6)),dtype=np.int8,count=bps*4)[:len(ids)][keep]
        dosage=np.where(codes==0,2,np.where(codes==2,1,np.where(codes==3,0,np.nan))).astype(np.float32)
        if np.isnan(dosage).any():
            dosage=np.where(np.isnan(dosage),np.nanmean(dosage),dosage)
        G[:,j]=dosage
sd=G.std(axis=0,ddof=1); ok=np.isfinite(sd)&(sd>0)
G=G[:,ok]; v=v.loc[ok].reset_index(drop=True)
G=(G-G.mean(axis=0))/G.std(axis=0,ddof=1)
R=(G.T@G)/(G.shape[0]-1); R=(R+R.T)/2; np.fill_diagonal(R,1)
np.save(OUT/"signed_A1_correlation.npy",R.astype(np.float32))
v.to_csv(OUT/"LD_variants.tsv",sep="\t",index=False)
qc={"cell":args.cell,"gene":args.gene,"n_samples":len(keep),"n_variants":len(v),
    "lead_present":bool((v.variant_id=="5:150447128").any()),"finite":bool(np.isfinite(R).all()),
    "max_asymmetry":float(np.max(np.abs(R-R.T))),"max_diag_deviation":float(np.max(np.abs(np.diag(R)-1))),
    "min_eigenvalue":float(np.linalg.eigvalsh(R.astype(np.float64)).min())}
qc["status"]="PASS" if qc["finite"] and qc["max_asymmetry"]<1e-5 and qc["max_diag_deviation"]<1e-5 else "HOLD"
(OUT/"sourceLD_QC.json").write_text(json.dumps(qc,indent=2),encoding="utf-8")
print(json.dumps(qc,indent=2))
