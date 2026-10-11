#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd, json
ROOT = Path(r"H:\SCI2\YR1")
PLINK = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors"
BED=PLINK/"plink_merged_980_donors.bed"; BIM=PLINK/"plink_merged_980_donors.bim"; FAM=PLINK/"plink_merged_980_donors.fam"
SAMPLES=ROOT/"3_results/03_qtl/R5A2A2/cell_sample_lists/NK_R.samples.txt"
QTL=ROOT/"3_results/03_qtl/R5A2A2/OneK1K_chr18_fixed_1Mb_region_pairs.tsv.gz"
OUT=ROOT/"3_results/04_integration/R5A2A4/NK_R_ZCCHC2_sourceLD"; OUT.mkdir(parents=True,exist_ok=True)
fam=pd.read_csv(FAM,sep=r"\s+",header=None,dtype=str); ids=fam.iloc[:,1].tolist(); idx={x:i for i,x in enumerate(ids)}
keep_ids=[x.strip() for x in SAMPLES.read_text(encoding="utf-8").splitlines() if x.strip()]
keep=np.array([idx[x] for x in keep_ids],dtype=int)
bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["chr","variant_id","cm","pos","A1","A2"],dtype={"chr":str,"variant_id":str,"A1":str,"A2":str})
bim["global_index"]=np.arange(len(bim))
q=pd.read_csv(QTL,sep="\t",compression="gzip")
q=q[(q.cell_type=="NK_R")&(q.phenotype_id=="ZCCHC2")].drop_duplicates("variant_id")
v=q[["variant_id","position_GRCh37","A1_effect_allele","A2_other_allele","af_A1","slope_A1","slope_se","pval_nominal"]].merge(
    bim[["variant_id","global_index","A1","A2"]],on="variant_id",how="inner",validate="one_to_one")
if len(v)!=len(q): raise RuntimeError(f"QTL/BIM coverage mismatch {len(v)}/{len(q)}")
if not ((v.A1_effect_allele==v.A1)&(v.A2_other_allele==v.A2)).all(): raise RuntimeError("A1/A2 mismatch")
bps=(len(ids)+3)//4
G=np.empty((len(keep),len(v)),dtype=np.float32)
with BED.open("rb") as f:
    if f.read(3).hex()!="6c1b01": raise RuntimeError("BED is not SNP-major PLINK v1")
    for j,gi in enumerate(v.global_index.astype(int)):
        f.seek(3+gi*bps); raw=f.read(bps)
        codes=np.fromiter(((b>>s)&3 for b in raw for s in (0,2,4,6)),dtype=np.int8,count=bps*4)[:len(ids)][keep]
        dosage=np.where(codes==0,2,np.where(codes==2,1,np.where(codes==3,0,np.nan))).astype(np.float32)
        if np.isnan(dosage).any(): dosage=np.where(np.isnan(dosage),np.nanmean(dosage),dosage)
        G[:,j]=dosage
sd=G.std(axis=0,ddof=1); ok=np.isfinite(sd)&(sd>0); G=G[:,ok]; v=v.loc[ok].reset_index(drop=True)
G=(G-G.mean(axis=0))/G.std(axis=0,ddof=1); R=(G.T@G)/(G.shape[0]-1); R=(R+R.T)/2; np.fill_diagonal(R,1)
np.save(OUT/"NK_R_ZCCHC2_signed_A1_correlation.npy",R.astype(np.float32))
v.to_csv(OUT/"NK_R_ZCCHC2_LD_variants.tsv",sep="\t",index=False)
qc={"status":"PASS" if np.isfinite(R).all() and np.max(np.abs(R-R.T))<1e-5 and np.max(np.abs(np.diag(R)-1))<1e-5 else "HOLD",
    "n_samples":int(G.shape[0]),"n_variants":int(G.shape[1]),"max_asymmetry":float(np.max(np.abs(R-R.T))),
    "max_diag_deviation":float(np.max(np.abs(np.diag(R)-1))),"min_eigenvalue":float(np.linalg.eigvalsh(R.astype(np.float64)).min()),
    "rs7239261_present":bool((v.variant_id=="18:60005046").any())}
(OUT/"NK_R_ZCCHC2_sourceLD_QC.json").write_text(json.dumps(qc,indent=2),encoding="utf-8"); print(json.dumps(qc,indent=2))
