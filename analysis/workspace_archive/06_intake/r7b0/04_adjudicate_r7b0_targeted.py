#!/usr/bin/env python3
import json
from pathlib import Path
import pandas as pd

ROOT=Path(r"H:\\SCI2\\YR1")
QC=ROOT/"3_results/03_qtl/R7B0/pf50_targeted/R7B0_pf10_reproduction_QC.tsv"
CO=ROOT/"3_results/04_integration/R7B0/multisignal/R7B0_corrected_multisignal_coloc_susie.tsv"
OUT=ROOT/"3_results/04_integration/R7B0"

def cls(r):
 h=float(r['PP.H4.abf']); ratio=float(r.H4_over_H3H4)
 if h>=.8 and ratio>=.8: return 'H4_DOMINANT'
 if ratio>=.5: return 'H4_PREDOMINANT_WEAK'
 if float(r['PP.H3.abf'])>h: return 'H3_DOMINANT'
 return 'UNINFORMATIVE'

qc=pd.read_csv(QC,sep='\t')
co=pd.read_csv(CO,sep='\t')
co=co[co.p12==1e-5].copy()
rows=[]
for (g,c),q in qc.groupby(['gene','cell']):
 x=co[(co.gene==g)&(co.cell_type==c)]
 row={'gene':g,'cell_type':c,'PF10_reproduction':('PASS' if bool(q.pass_tight_reproduction.iloc[0]) else 'FAIL'),'PF10_slope_max_abs_error':q.pf10_slope_max_abs_error.iloc[0],'PF10_z_corr':q.pf10_z_corr_with_frozen_beta_se.iloc[0]}
 for cfg in ['PF10_L10','PF50_L10']:
  xx=x[x.config==cfg].sort_values('PP.H4.abf',ascending=False)
  if xx.empty:
   row.update({f'{cfg}_PPH3':None,f'{cfg}_PPH4':None,f'{cfg}_H4ratio':None,f'{cfg}_class':'NO_COLOC_SUMMARY',f'{cfg}_qtl_s_rss':None,f'{cfg}_qtl_kriging_n':None})
  else:
   z=xx.iloc[0]
   row.update({f'{cfg}_PPH3':z['PP.H3.abf'],f'{cfg}_PPH4':z['PP.H4.abf'],f'{cfg}_H4ratio':z.H4_over_H3H4,f'{cfg}_class':cls(z),f'{cfg}_qtl_s_rss':z.qtl_s_rss,f'{cfg}_qtl_kriging_n':z.qtl_kriging_n})
 row['matched_model_transition']=f"{row['PF10_L10_class']} -> {row['PF50_L10_class']}"
 row['decision']='PF10_PRIMARY_HOLD_SOURCE_AUDIT' if row['PF10_reproduction']=='FAIL' else ('MODEL_SENSITIVITY_REVIEW' if row['PF10_L10_class']!=row['PF50_L10_class'] else 'NO_CLASS_CHANGE')
 rows.append(row)
res=pd.DataFrame(rows)
res.to_csv(OUT/'R7B0_targeted_reclassification.tsv',sep='\t',index=False)
state={'status':'HOLD_PF10_SOURCE_PROVENANCE_PARTIAL','comparisons':len(res),'PF10_reproduction_pass':int((res.PF10_reproduction=='PASS').sum()),'PF10_reproduction_fail':int((res.PF10_reproduction=='FAIL').sum()),'PF10_primary_claim':'historical PF10 results remain the primary archived analysis; formula reproduction is partial against current public PF50 covariate package','corrected_PF50_claim':'targeted model-sensitive analysis; not promoted to final robustness while PF10 covariate identity remains unresolved','class_transitions':res[res.matched_model_transition.str.contains('->')].to_dict('records')}
(OUT/'R7B0_targeted_adjudication.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(state,ensure_ascii=False,indent=2))
