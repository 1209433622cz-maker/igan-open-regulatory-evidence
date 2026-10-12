#!/usr/bin/env python3
"""Create R7B0's pre-result benchmark, FinnGen, and simulation freeze files."""
from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
import pandas as pd

ROOT=Path(r"H:\\SCI2\\YR1")
AUD=ROOT/"3_results/00_audit/R7B0"; AUD.mkdir(parents=True,exist_ok=True)
QTL=ROOT/"3_results/03_qtl/R7B0"; QTL.mkdir(parents=True,exist_ok=True)
FIN=ROOT/"3_results/01_intake/R7B0/finngen_cascade"
RANGES=ROOT/"3_results/01_intake/R7A1A/R7A1A_PBC_GJOKA_locus_ranges.tsv"
INV=ROOT/"3_results/01_intake/R7A1A/R7A1A_PBC_GJOKA_remote_member_inventory.tsv"
COV=ROOT/"1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"
SAMP=ROOT/"3_results/03_qtl/R5A2A2/cell_sample_lists"

cells=["B_IN","B_MEM","CD4_ET","CD4_NC","CD4_SOX4","CD8_ET","CD8_NC","CD8_S100B","DC","Mono_C","Mono_NC","NK","NK_R","Plasma"]
fg_map={"B_IN":"B_intermediate","B_MEM":"B_memory","CD4_ET":"CD4_TEM","CD4_NC":"CD4_Naive","CD4_SOX4":"CD4_TCM","CD8_ET":"CD8_TEM","CD8_NC":"CD8_Naive","CD8_S100B":"CD8_TEM","DC":"cDC2","Mono_C":"CD14_Mono","Mono_NC":"CD16_Mono","NK":"NK","NK_R":"NK_CD56bright","Plasma":"Plasmablast"}
uncertain={"CD4_SOX4","CD8_S100B","DC","Plasma"}

def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def build_universe():
 ranges=pd.read_csv(RANGES,sep='\t'); inv=pd.read_csv(INV,sep='\t')
 im=inv.set_index('member').to_dict('index')
 rows=[]
 for r in ranges.itertuples(index=False):
  for cell in cells:
   sf=SAMP/f'{cell}.samples.txt'; donors=[x for x in sf.read_text().splitlines() if x]
   cov=COV/f'{cell}_mx_pf50.txt'
   rows.append({"locus_index":int(r.locus_index),"chromosomes":r.chromosomes,"min_bp_GRCh37":int(r.min_bp_grch37),"max_bp_GRCh37":int(r.max_bp_grch37),"cell_type":cell,"active_donor_N":len(donors),"covariate_file":str(cov.relative_to(ROOT)),"covariate_file_bytes":cov.stat().st_size,"covariate_file_sha256":sha(cov),"oneK_active_donor_file":str(sf.relative_to(ROOT)),"oneK_active_donor_sha256":sha(sf),"qtl_member_status":"PENDING_FULL_56_LOCUS_SCAN","gene_rule":"source cis-eQTL gene with q<0.05 in >=1 cell; test every eligible cell-gene","variant_rule":"GRCh37 BIM A1/A2 identity; MAF>0.05 source; >=200 disease-QTL overlap; palindromic unresolved excluded","LD_rule":"cell-active-donor genotype with PF10 primary and corrected PF50 sensitivity; no cross-cell donor substitution","finngen_level2_mapping":fg_map[cell],"finngen_mapping_status":"label_based_prespecified_uncertain" if cell in uncertain else "label_based_prespecified"})
 pd.DataFrame(rows).to_csv(QTL/'R7B0_PBCwide_56x14_universe_scaffold.tsv',sep='\t',index=False)
 (AUD/'R7B0_PBCwide_universe_freeze.json').write_text(json.dumps({"status":"FROZEN_SCAFFOLD_PENDING_FULL_QTL_ELIGIBILITY","loci":len(ranges),"cells":len(cells),"rows":len(rows),"rows_expected":56*14,"gene_inclusion":"q<0.05 in at least one cell, then all available eligible cell-gene pairs","screen":"coloc.abf with p1=p2=1e-4 and p12 in 1e-6,1e-5,1e-4","multi_signal_trigger":"default PP.H4>=0.80 and H4/(H3+H4)>=0.80, or prespecified H3/H4 ambiguity with PP.H3+PP.H4>=0.80 and ratio in [0.20,0.80]","reclassification":{"STABLE_H4":"default gate plus low-p12 ratio>=0.50 and corrected PF50 does not reverse","WEAKENED_H4":"H4 predominant but misses strict robustness","REVERSED_TO_H3":"default PP.H3>PP.H4 or H4/(H3+H4)<0.50","UNINFORMATIVE":"weak QTL/low overlap/no eligible CS","QC_FAIL":"identity, LD, convergence or coverage failure"},"source_inventory_sha256":sha(INV),"source_ranges_sha256":sha(RANGES)},ensure_ascii=False,indent=2),encoding='utf-8')

def build_finngen():
 out=[]
 for gene in ['FCRL3','IL12RB2']:
  j=json.loads((FIN/f'gene_{gene.lower()}.response').read_text())
  eq=j.get('eqtl_q',{}); ca=j.get('caqtl_q',{})
  for cell in ['B_IN','B_MEM','NK','NK_R']:
   ct=fg_map[cell]; out.append({"gene":gene,"OneK_cell":cell,"FinnGen_primary_level2":ct,"FinnGen_eqtl_q":eq.get('l2.'+ct),"FinnGen_caqtl_q":ca.get('l2.'+ct),"FinnGen_level1_B_or_NK_eqtl_q":eq.get('l1.B' if ct.startswith('B_') else 'l1.NK'),"mapping_status":"label_based_prespecified_uncertain" if cell in uncertain else "label_based_prespecified","source":"CASCADE public gene API","data_build":"GRCh38 API coordinates/variant IDs","individual_level_LD":"RESTRICTED_NOT_USED"})
  top=j.get('top_variants',[]); peaks=j.get('peaks',[])
  out[-1]['top_variant_count']=len(top); out[-1]['linked_peak_count']=len(peaks)
 pd.DataFrame(out).to_csv(AUD/'R7B0_FinnGen_FCRL3_IL12RB2_feasibility.tsv',sep='\t',index=False)
 phen=json.loads((FIN/'phenos_chirbil.response').read_text())
 direct=[]
 for p in sorted(FIN.glob('*_coloc.response')):
  j=json.loads(p.read_text()); pairs=j.get('pairs',[])
  hit=[x for x in pairs if x.get('trait1')=='CHIRBIL_PRIM' or x.get('trait2')=='CHIRBIL_PRIM']
  direct.append({"receipt":p.name,"pair_count":len(pairs),"CHIRBIL_pair_count":len(hit),"CHIRBIL_pairs":hit})
 decision={"phenotype_search":"CHIRBIL_PRIM","public_record":phen,"public_PBC_GWAS_molQTL_coloc":"DIRECT_PUBLIC_ENDPOINT_FOUND_FOR_IL12RB2_TOP_VARIANT","direct_coloc_receipts":direct,"fig5_filter_context":"The published Fig5 code filters the 439-trait overview at H2_Z>2 and num_gw_significant>10; that filter is not the same as the direct by_variant endpoint and must not be used to claim that PBC is absent.","molecular_layer_FCRL3_IL12RB2":"FEASIBLE_PUBLIC_API","independent_PBC_disease_replication":"PUBLIC_FINNGEN_R12_CHIRBIL_IL12RB2_COLOC_AVAILABLE; external QTL replication remains resource-dependent","restricted_individual_level_data":"EXCLUDED"}
 (AUD/'R7B0_FinnGen_PBC_presence_adjudication.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2),encoding='utf-8')

def build_sim():
 scenarios=[("S1_one_shared",1,1,"one shared causal",1000),("S2_distinct_correlated",1,1,"distinct correlated causal",1000),("S3_disease2_qtl1_partial",2,1,"two disease signals one partly shared",1000),("S4_two_by_two_one_shared",2,2,"one of two signals shared",1000),("S5_two_by_two_none_highLD",2,2,"no shared signal under high LD",1000),("S6_matched_vs_mismatched_LD",2,2,"matched versus deliberately mismatched LD",1000)]
 rows=[]
 for name,nd,nq,desc,n in scenarios:
  for maf in [0.05,0.2,0.4]:
   for r2 in [0.2,0.5,0.8]:
    for L in [5,10,20]:
     for p12 in [1e-6,1e-5,1e-4]:
      rows.append({"scenario":name,"description":desc,"disease_causal_signals":nd,"qtl_causal_signals":nq,"replicates":n,"seed":20261002+len(rows)*17,"disease_N":24510,"qtl_N":750,"maf":maf,"causal_r2":r2,"susie_L":L,"p12":p12,"LD_template":"GJOKA_locus2_or_locus4_or_OneK_sourceLD","primary_method":"coloc.susie matched source LD","sensitivity":"mismatched LD only in S6; coloc.abf for screen"})
 pd.DataFrame(rows).to_csv(AUD/'R7B0_simulation_grid.tsv',sep='\t',index=False)
 (AUD/'R7B0_simulation_freeze.json').write_text(json.dumps({"status":"PROTOCOL_FROZEN_BEFORE_RESULTS","core_replicates":1000,"secondary_replicates":500,"scenarios":[x[0] for x in scenarios],"random_seed_base":20261002,"no_result_adaptation":True,"decision_outputs":["signal_classification","H4_bias_under_LD_mismatch","coverage","convergence","false_stability_rate"]},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
 build_universe(); build_finngen(); build_sim(); print(json.dumps({"universe":"FROZEN_SCAFFOLD","finngen":"IL12RB2_PUBLIC_PBC_COLOC_SUPPORT__FCRL3_NO_DIRECT_PBC_PAIR","simulation":"PROTOCOL_FROZEN"},ensure_ascii=False,indent=2))
