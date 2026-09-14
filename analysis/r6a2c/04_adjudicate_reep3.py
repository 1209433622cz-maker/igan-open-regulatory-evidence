#!/usr/bin/env python3
"""R6A2C final falsification adjudication."""
from pathlib import Path
import json, os, numpy as np, pandas as pd
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT",Path.cwd())); BASE=ROOT/"3_results/04_integration/R6A2C"; MS=BASE/"multisignal"; LD=BASE/"sourceLD/REEP3_REEP3_CD4_NC"

def jacc(a,b):
 a=set(a);b=set(b); return len(a&b)/len(a|b) if a|b else 0.0

ld=json.loads((LD/'covariate_residual_LD_QC.json').read_text(encoding='utf-8'))
s=pd.read_csv(MS/'R6A2C_susie_summary.tsv',sep='\t'); cs_path=MS/'R6A2C_susie_credible_sets.tsv'; c=pd.read_csv(cs_path,sep='\t') if cs_path.exists() and cs_path.stat().st_size else pd.DataFrame(); coloc_path=MS/'R6A2C_signal_coloc.tsv'; co=pd.read_csv(coloc_path,sep='\t') if coloc_path.exists() and coloc_path.stat().st_size else pd.DataFrame()
primary=s[s.config.eq('PF10_L10')]
if len(primary)!=1: raise RuntimeError('missing unique PF10_L10')
pr=primary.iloc[0]; stable=[]
if len(c):
 pcs=c[c.config.eq('PF10_L10')]
 for csname,g in pcs.groupby('credible_set'):
  pm=set(g.variant_id); matches={}
  for cfg in ['PF10_L5','PF10_L20','PF50_L10']:
   best=0.0; best_name=None
   for other,og in c[c.config.eq(cfg)].groupby('credible_set'):
    x=jacc(pm,set(og.variant_id))
    if x>best: best=x; best_name=other
   matches[cfg]={'best_jaccard':best,'credible_set':best_name}
  is_stable=all(matches[cfg]['best_jaccard']>=0.50 for cfg in matches)
  stable.append({'primary_credible_set':csname,'primary_component':int(g.component.iloc[0]),'members':len(pm),'stable':bool(is_stable),'matches':matches})
stable_n=sum(x['stable'] for x in stable)
passes=[]
if len(co):
 for st in stable:
  if not st['stable']: continue
  comp=st['primary_component']; asi=co[(co.dataset=='asian')&(co.config=='PF10_L10')&(co.component==comp)]
  if len(asi):
   de=asi[np.isclose(asi.p12,1e-5)]; lo=asi[np.isclose(asi.p12,1e-6)]
   if len(de)==1 and len(lo)==1:
    d=de.iloc[0]; l=lo.iloc[0]
    pass_signal=bool(d.PP_H4>=0.80 and d.H4_over_H3H4>=0.80 and l.H4_over_H3H4>=0.50)
    passes.append({'component':comp,'credible_set':st['primary_credible_set'],'pass':pass_signal,'asian_PP_H4':float(d.PP_H4),'asian_H4_ratio':float(d.H4_over_H3H4),'asian_low_prior_ratio':float(l.H4_over_H3H4)})
signal_pass=any(x['pass'] for x in passes)
# Contrast summaries only; they do not rescue/fail the Asian gate.
contrast={}
if len(co):
 for ds in ['combined','european','asian']:
  x=co[(co.dataset==ds)&(co.config=='PF10_L10')&np.isclose(co.p12,1e-5)]
  contrast[ds]={'max_PP_H4':None if x.empty else float(x.PP_H4.max()),'max_H4_ratio':None if x.empty else float(x.H4_over_H3H4.max())}
if ld.get('status')!='PASS': status='HOLD_TECHNICAL_LD'
elif not bool(pr.converged): status='FAIL_PRIMARY_SUSIE_NOT_CONVERGED'
elif stable_n<1: status='FAIL_NO_STABLE_95PCT_QTL_CREDIBLE_SIGNAL'
elif not signal_pass: status='FAIL_ASIAN_SIGNAL_SPECIFIC_COLOC'
else: status='PASS_ASIAN_SPECIFIC_DISCOVERY_CANDIDATE'
if status.startswith('PASS'):
 next_stage='R6A2D_TENK_REEP3_CD4_REPLICATION'
 project='CONDITIONAL_GO_ANCESTRY_AWARE_TWO_LOCUS_REASSESSMENT'
else:
 next_stage='R6A3_IGAN_DESIGN_REASSESSMENT_KIDNEY_PQTL_TISSUE'
 project='STOP_FURTHER_IMMUNE_CISEQTL_LOCUS_EXPANSION'
state={'status':status,'claim_ceiling':'ANCESTRY_SPECIFIC_DISCOVERY_CANDIDATE_ONLY','LD_QC':ld.get('status'),'PF10_L10_converged':bool(pr.converged),'PF10_L10_credible_sets_95':int(pr.credible_sets_95),'stable_95pct_CS':stable_n,'stable_CS_details':stable,'asian_signal_tests':passes,'contrast':contrast,'disease_strength_note':'Asian regional disease min P was ~4.55e-6 in frozen R6A2B0 smoke; not genome-wide significant.','project_decision':project,'next_stage':next_stage,'tenk_triggered':bool(status.startswith('PASS'))}
(BASE/'R6A2C_final_adjudication.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
pd.DataFrame(passes).to_csv(BASE/'R6A2C_asian_signal_gate.tsv',sep='\t',index=False)
if status.startswith('PASS'):
 pd.DataFrame([{'gene':'REEP3','gene_ensembl':'ENSG00000165476','OneK_cell':'CD4_NC','TenK_cell':'CD4_Naive','priority':1,'support_required':'independent disease-QTL coloc or source SuSiE-compatible evidence'},{'gene':'REEP3','gene_ensembl':'ENSG00000165476','OneK_cell':'CD4_NC','TenK_cell':'CD4_TCM','priority':2,'support_required':'independent disease-QTL coloc or source SuSiE-compatible evidence'}]).to_csv(BASE/'R6A2C_TenK_trigger.tsv',sep='\t',index=False)
print(json.dumps(state,indent=2))
