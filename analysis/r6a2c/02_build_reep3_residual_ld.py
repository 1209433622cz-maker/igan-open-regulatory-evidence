#!/usr/bin/env python3
"""R6A2C: PF10/PF50 residualized LD for REEP3/CD4_NC."""
from pathlib import Path
import hashlib,json,os
import numpy as np,pandas as pd
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT",Path.cwd()))
BASE=ROOT/"3_results/04_integration/R6A2C/sourceLD/REEP3_REEP3_CD4_NC"
COV=ROOT/"1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors/CD4_NC_mx_pf50.txt"

def sha256(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while b:=f.read(8*1024*1024): h.update(b)
 return h.hexdigest()

def residual_corr(G,C):
 C=np.asarray(C,float); C=(C-C.mean(0))/C.std(0,ddof=1); X=np.column_stack([np.ones(len(C)),C])
 q,r=np.linalg.qr(X,mode='reduced'); rank=int(np.linalg.matrix_rank(r))
 if rank!=X.shape[1]: raise RuntimeError(f"rank deficient {rank}/{X.shape[1]}")
 E=G.astype(float)-q@(q.T@G.astype(float)); sd=E.std(0,ddof=1)
 if (sd<=0).any() or not np.isfinite(sd).all(): raise RuntimeError('non-variable residual genotype')
 Z=(E-E.mean(0))/sd; R=(Z.T@Z)/(len(Z)-1); R=(R+R.T)/2; np.fill_diagonal(R,1)
 dual=(Z@Z.T)/(len(Z)-1); dual=(dual+dual.T)/2; eig=np.linalg.eigvalsh(dual)
 return R,{'design_columns':X.shape[1],'design_rank':rank,'residual_df':len(Z)-rank,'dual_min_eigenvalue':float(eig.min()),
          'dual_neg_eigs_lt_m1e8':int((eig < -1e-8).sum()),'max_asymmetry':float(np.max(abs(R-R.T))),'max_diag_dev':float(np.max(abs(np.diag(R)-1)))}

src=json.loads((BASE/'sourceLD_QC.json').read_text(encoding='utf-8'))
if src.get('status')!='PASS': raise RuntimeError('source LD gate not PASS')
samples=[x for x in (BASE/'active_donors.txt').read_text(encoding='utf-8').splitlines() if x]; G=np.load(BASE/'standardized_A1_dosage.npy').astype(float)
if G.shape[0]!=len(samples): raise RuntimeError('sample/dosage dimension mismatch')
cov=pd.read_csv(COV,sep=r"\s+",dtype={'sampleid':str}).set_index('sampleid'); missing=sorted(set(samples)-set(cov.index))
if missing: raise RuntimeError(f"covariates missing {len(missing)} donors")
cov=cov.loc[samples]
base=['sex']+[f'pc{i}' for i in range(1,7)]+['age']; modes={'PF10':base+[f'pf{i}' for i in range(1,11)],'PF50':base+[f'pf{i}' for i in range(1,51)]}
mat={}; details={}
for mode,cols in modes.items():
 vals=cov[cols].apply(pd.to_numeric,errors='raise').to_numpy(float); R,d=residual_corr(G,vals); R32=R.astype(np.float32)
 npy=BASE/f'{mode}_residualized_A1_correlation.npy'; binp=BASE/f'{mode}_residualized_A1_correlation.float32.bin'
 np.save(npy,R32); R32.astype('<f4').tofile(binp); d.update({'covariates':cols,'npy_sha256':sha256(npy),'binary_sha256':sha256(binp)})
 d['gate_pass']=bool(d['design_rank']==d['design_columns'] and d['dual_neg_eigs_lt_m1e8']==0 and d['max_asymmetry']<=1e-12 and d['max_diag_dev']<=1e-12 and np.isfinite(R).all())
 details[mode]=d; mat[mode]=R
D=np.abs(mat['PF10']-mat['PF50'])
audit={'status':'PASS' if all(x['gate_pass'] for x in details.values()) else 'HOLD','locus':'REEP3','gene':'REEP3','cell':'CD4_NC','active_donors':len(samples),'variants':G.shape[1],
       'primary':'PF10','sensitivity':'PF50','PF10_vs_PF50_max_abs_change':float(D.max()),'PF10_vs_PF50_median_abs_change':float(np.median(D)),'results':details}
(BASE/'covariate_residual_LD_QC.json').write_text(json.dumps(audit,indent=2),encoding='utf-8'); print(json.dumps(audit,indent=2))
if audit['status']!='PASS': raise SystemExit(2)
