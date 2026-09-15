#!/usr/bin/env python3
from pathlib import Path
import os,json
import pandas as pd,numpy as np
ROOT=Path(os.environ.get('R7_PROJECT_ROOT',r'H:\SCI2\YR1'))
OUT=ROOT/'3_results/04_integration/R7A1B'
M=OUT/'multisignal'
smoke=pd.read_csv(OUT/'R7A1B_coloc_smoke.tsv',sep='\t')
sig=pd.read_csv(M/'R7A1B_signal_coloc_susie.tsv',sep='\t') if (M/'R7A1B_signal_coloc_susie.tsv').exists() else pd.DataFrame()
fit=pd.read_csv(M/'R7A1B_susie_fit_summary.tsv',sep='\t') if (M/'R7A1B_susie_fit_summary.tsv').exists() else pd.DataFrame()
CONFIGS=['PF10_L5','PF10_L10','PF10_L20','PF50_L10']

def robust_pairs(sg,config):
    d=sg[(sg.config==config)&np.isclose(pd.to_numeric(sg.p12),1e-5)].copy()
    l=sg[(sg.config==config)&np.isclose(pd.to_numeric(sg.p12),1e-6)][['cell_type','hit1','hit2','H4_over_H3H4']].rename(columns={'H4_over_H3H4':'low_ratio'})
    if d.empty:return d
    x=d.merge(l,on=['cell_type','hit1','hit2'],how='left')
    x['robust']=(x['PP.H4.abf']>=.8)&(x.H4_over_H3H4>=.8)&(x.low_ratio>=.5)
    return x

rows=[]
for gene,g in smoke.groupby('gene'):
    sg=sig[sig.gene==gene].copy() if len(sig) else pd.DataFrame()
    fg=fit[fit.gene==gene].copy() if len(fit) else pd.DataFrame()
    best_h4=np.nan;best_ratio=np.nan;best_cell='';stable_cells=[]
    if len(sg):
        main=robust_pairs(sg,'PF10_L10')
        if len(main):
            b=main.sort_values('PP.H4.abf',ascending=False).iloc[0]
            best_h4=float(b['PP.H4.abf']);best_ratio=float(b.H4_over_H3H4);best_cell=str(b.cell_type)
        for cell in sorted(sg.cell_type.unique()):
            ok=True
            for cfg in CONFIGS:
                x=robust_pairs(sg[(sg.cell_type==cell)],cfg)
                if x.empty or not bool(x.robust.any()): ok=False;break
                fc=fg[(fg.cell_type==cell)&(fg.config==cfg)]
                if fc.empty or not bool((fc.disease_converged==True).all()) or not bool((fc.qtl_converged==True).all()): ok=False;break
                if not bool((pd.to_numeric(fc.disease_CS,errors='coerce')>=1).all()) or not bool((pd.to_numeric(fc.qtl_CS,errors='coerce')>=1).all()): ok=False;break
            if ok:stable_cells.append(cell)
    stable=bool(stable_cells)
    if stable:status='PASS_SIGNAL_SPECIFIC_SHARED_GENE'
    elif (g.classification=='DISTINCT_SIGNAL_SMOKE').all():status='FAIL_DISTINCT_OR_NO_SHARED_SIGNAL'
    elif gene=='INAVA' and (pd.to_numeric(g.qtl_min_p,errors='coerce')>1e-6).all():status='UNINFORMATIVE_WEAK_ONEK_QTL'
    else:status='FAIL_OR_UNRESOLVED_AFTER_MULTISIGNAL'
    rows.append({'gene':gene,'status':status,'stable_pass_cells':';'.join(stable_cells),'best_cell':best_cell,
                 'best_signal_PP_H4':best_h4,'best_signal_H4_ratio':best_ratio,
                 'required_sensitivity_configs':';'.join(CONFIGS)})
A=pd.DataFrame(rows);A.to_csv(OUT/'R7A1B_gene_adjudication.tsv',sep='\t',index=False)
passes=int((A.status=='PASS_SIGNAL_SPECIFIC_SHARED_GENE').sum())
if passes>=2:decision='GO_R7A1C_TENK_REPLICATION_AND_PBC_LIVER_DETECTABILITY'
else:decision='PBC_REGULATORY_MAIN_FROZEN_FAIL__NO_CED_AUTO_RESUME'
state={'signal_specific_pass_genes':passes,'gene_results':A.to_dict('records'),'decision':decision,
       'pass_definition':'same cell robust in PF10_L5/PF10_L10/PF10_L20/PF50_L10; both SuSiE fits converged; >=1 disease and QTL CS in each config'}
# Emit strict JSON so unavailable numeric summaries are represented as null.
state['gene_results']=A.astype(object).where(pd.notna(A),None).to_dict('records')
(OUT/'R7A1B_final_adjudication.json').write_text(json.dumps(state,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps(state,indent=2))
