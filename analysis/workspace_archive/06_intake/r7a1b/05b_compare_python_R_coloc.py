#!/usr/bin/env python3
from pathlib import Path
import os,json
import numpy as np,pandas as pd
ROOT=Path(os.environ.get('R7_PROJECT_ROOT',r'H:\SCI2\YR1'))
OUT=ROOT/'3_results/04_integration/R7A1B'
py=pd.read_csv(OUT/'R7A1B_coloc_smoke.tsv',sep='\t')
r=pd.read_csv(OUT/'R7A1B_official_R_coloc_validation.tsv',sep='\t')
r0=r[np.isclose(pd.to_numeric(r.p12),1e-5)].copy()
m=py.merge(r0,on=['gene','cell_type'],suffixes=('_py','_r'))
diffs={}
for h in ['PP_H0','PP_H1','PP_H2','PP_H3','PP_H4']:
    diffs[h]=float((m[h+'_py']-m[h+'_r']).abs().max()) if len(m) else None
vals=[v for v in diffs.values() if v is not None and np.isfinite(v)]
maxdiff=max(vals) if vals else None
state={'merged_comparisons':int(len(m)),'python_comparisons':int(len(py)),'R_default_prior_comparisons':int(len(r0)),
       'posterior_abs_diff_by_H':diffs,'max_posterior_abs_diff':maxdiff,
       'tolerance':1e-10,'gate':'PASS' if maxdiff is not None and maxdiff<=1e-10 and len(m)==len(py) else 'FAIL'}
(OUT/'R7A1B_Python_vs_R_validation.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
print(json.dumps(state,indent=2))
if state['gate']!='PASS': raise SystemExit(2)
