#!/usr/bin/env python3
from pathlib import Path
import os,json,hashlib
import numpy as np,pandas as pd
ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
BASE=ROOT/"3_results/04_integration/R7A1B/sourceLD"
COV=ROOT/"1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"
def residual_corr(G,C):
    C=(C-C.mean(0))/C.std(0,ddof=1);X=np.column_stack([np.ones(len(C)),C]);q,r=np.linalg.qr(X,mode="reduced")
    rank=int(np.linalg.matrix_rank(r))
    if rank!=X.shape[1]:raise RuntimeError("rank deficient covariates")
    E=G-q@(q.T@G);sd=E.std(0,ddof=1)
    if (~np.isfinite(sd)).any() or (sd<=0).any():raise RuntimeError("nonvariable residual genotype")
    Z=(E-E.mean(0))/sd;R=(Z.T@Z)/(len(Z)-1);R=(R+R.T)/2;np.fill_diagonal(R,1)
    dual=(Z@Z.T)/(len(Z)-1);eig=np.linalg.eigvalsh((dual+dual.T)/2)
    return R,{"design_columns":X.shape[1],"design_rank":rank,"residual_df":len(Z)-rank,
              "dual_min_eigenvalue":float(eig.min()),"dual_negative_lt_1e8":int((eig<-1e-8).sum()),
              "max_asymmetry":float(np.max(abs(R-R.T))),"max_diag_dev":float(np.max(abs(np.diag(R)-1)))}
rows=[]
for d in sorted(p for p in BASE.iterdir() if p.is_dir()):
    qc=json.loads((d/"sourceLD_QC.json").read_text());samples=[x for x in (d/"active_donors.txt").read_text().splitlines() if x]
    G=np.load(d/"standardized_A1_dosage.npy").astype(float)
    cov=pd.read_csv(COV/f"{qc['cell']}_mx_pf50.txt",sep=r"\s+",dtype={"sampleid":str}).set_index("sampleid").loc[samples]
    base=["sex"]+[f"pc{i}" for i in range(1,7)]+["age"]
    modes={"PF10":base+[f"pf{i}" for i in range(1,11)],"PF50":base+[f"pf{i}" for i in range(1,51)]}
    details={}
    for mode,cols in modes.items():
        R,det=residual_corr(G,cov[cols].apply(pd.to_numeric).to_numpy(float))
        np.save(d/f"{mode}_residualized_A1_correlation.npy",R.astype(np.float32))
        det["gate_pass"]=bool(det["design_rank"]==det["design_columns"] and det["dual_negative_lt_1e8"]==0 and det["max_asymmetry"]<1e-12 and det["max_diag_dev"]<1e-12)
        details[mode]=det
    state={"gene":qc["gene"],"cell":qc["cell"],"n_samples":len(samples),"n_variants":G.shape[1],"results":details,
           "gate_pass":all(v["gate_pass"] for v in details.values())}
    (d/"covariate_residual_LD_QC.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
    rows.append({k:state[k] for k in ["gene","cell","n_samples","n_variants","gate_pass"]})
pd.DataFrame(rows).to_csv(BASE/"R7A1B_covariate_residual_LD_summary.tsv",sep="\t",index=False)
print(json.dumps(rows,indent=2))
