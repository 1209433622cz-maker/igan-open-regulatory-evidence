from pathlib import Path
import json,hashlib,zipfile,io,gzip,csv,itertools
import pandas as pd,numpy as np
from repo_layout import CURRENT_PACKAGE, REPO_ROOT, RESULTS_ROOT, runtime_output
R=REPO_ROOT;O=runtime_output('R7C3G_evidence_audit');B=CURRENT_PACKAGE;M=REPO_ROOT
checks=[];sources=[];frames={};objects={}
def check(n,v,d=''):
 checks.append({'check':n,'status':'PASS' if bool(v) else 'FAIL','detail':str(d)})
def sha(b):return hashlib.sha256(b).hexdigest()
for zpath in (B/'05_Source_Data').glob('*.zip'):
 with zipfile.ZipFile(zpath) as z:
  check('ZIP CRC '+zpath.name,z.testzip() is None)
  for n in z.namelist():
   if n.endswith('/'):continue
   b=z.read(n); entry={'archive':zpath.name,'member':n,'bytes':len(b),'sha256':sha(b),'semantic_review':'METADATA'}
   if n.endswith(('.tsv','.tsv.gz')):
    f=pd.read_csv(io.BytesIO(gzip.decompress(b) if n.endswith('.gz') else b),sep='\t');frames[n]=f;entry.update(rows=len(f),columns=len(f.columns),semantic_review='PARSED_SCHEMA_AND_CENTRAL_ENDPOINTS')
   elif n.endswith('.json'):
    objects[n]=json.loads(b.decode('utf-8-sig'));entry['semantic_review']='PARSED_STATE_AND_INFERENCE_BOUNDARY'
   sources.append(entry)
T=frames['S3/S3_642_A0_A1_A2_M_trajectories.tsv']; C=frames['S5/S5_642_PF10_PF50_classifications.tsv'];S=frames['S6/S6_signal_semantics_642.tsv'];G=frames['S2/S2_PBCwide_6923_screening_registry.tsv.gz']
check('Frozen 642 exact unique identities',len(T)==642 and T.comparison_id.nunique()==642)
check('Classification and semantics identity closure',set(T.comparison_id)==set(C.comparison_id)==set(S.comparison_id))
check('Screen registry 6923',len(G)==6923 and G.comparison_id.nunique()==6923)
check('Eligible variants threshold >=200',int((G.n_variants>=200).sum())==5460)
check('47 loci 200 genes 14 cells',T.locus_index.nunique()==47 and T.gene.nunique()==200 and T.cell_type.nunique()==14)
check('286 blocks',len(T[['locus_index','cell_type']].drop_duplicates())==286)
check('184 455 3 roles',sorted(T.R7B1B_v2_role.value_counts().tolist())==[3,184,455],T.R7B1B_v2_role.value_counts().to_dict())
states=T.M_simple_state.value_counts().to_dict();check('92 428 59 63 outcomes',states=={'H3':428,'H4':92,'UNINFORMATIVE':63,'MODEL_SENSITIVE':59},states)
check('Support differences 19-114 median65',(T.removed_n.min(),T.removed_n.max(),T.removed_n.median())==(19,114,65))
check('15 support changes',(T.A0_simple_state!=T.A1_simple_state).sum()==15)
check('19 statistic changes',(T.A1_simple_state!=T.A2_simple_state).sum()==19)
check('139 full procedure changes',(T.A2_simple_state!=T.M_simple_state).sum()==139)
check('8 H4 to H3',((T.A2_simple_state=='H4')&(T.M_simple_state=='H3')).sum()==8)
check('10 H3 to H4',((T.A2_simple_state=='H3')&(T.M_simple_state=='H4')).sum()==10)
check('A2 denominators113 452',int((T.A2_simple_state=='H4').sum())==113 and int((T.A2_simple_state=='H3').sum())==452)
check('No sensitivity category changes',all((T[a]==T[b]).all() for a,b in [('A1_simple_state','A1_NATIVE_simple_state'),('A2_simple_state','A2_NATIVE_simple_state'),('A2_simple_state','A2_ROUNDED_simple_state')]))
H=T[T.M_simple_state=='H4'];check('92 comparison 27gene 19locus',len(H)==92 and H.gene.nunique()==27 and H.locus_index.nunique()==19)
K=S.merge(T[['comparison_id','M_simple_state']],on='comparison_id',validate='one_to_one');check('32 H4 with distinct pairs',int(((K.M_simple_state=='H4')&K.mixed_h4_h3_within_any_config).sum())==32)
check('520 same-pair confirmations',K[K.M_simple_state.isin(['H4','H3'])].same_signal_pair_confirmed.all())
D=C[C.PF10_multisignal_state.isin(['H4_SUPPORTED_STABLE','H3_SUPPORTED_STABLE'])];pf=D.PF10_PF50_sensitivity.value_counts().to_dict();check('PF50 conditional491 4 25',len(D)==520 and sorted(pf.values())==[4,25,491],pf)
cd=T[T.comparison_id=='R7B1_000414'].iloc[0];cdm=C[C.comparison_id=='R7B1_000414'].iloc[0]
check('FCRL3 current PF10 .0036 PF50 .9919',abs(cd.pf10_l10_best_h4-.0036361957364122)<1e-12 and abs(cdm.pf50_l10_best_h4-.991894292309108)<1e-12)
I=frames['S7/S7_iteration_channels_486000.tsv.gz'];check('486000 simulation rows',len(I)==486000);(O/'simulation_iteration_schema.txt').write_text(','.join(I.columns),encoding='utf-8')
chan=frames['S7/S7_channel_summary.tsv'];overall=chan[chan.scope=='PRIMARY_MATCHED_OVERALL'];check('Channel conservation',overall.n.sum()==486000,overall[['matched_channel','n']].to_dict('records'))
ic=I.matched_channel.value_counts().to_dict();cc=dict(zip(overall.matched_channel,overall.n));check('486000 iteration channel replay',all(ic.get(k,0)==v for k,v in cc.items()) and sum(ic.values())==sum(cc.values()),ic)
scen=frames['S7/S7_scenario_summary.tsv'];perf=frames['S7/S7_discovery_vs_estimator.tsv'];check('Simulation six81000 designs',len(scen)==6 and (scen.replicates==81000).all())
check('160782 pair-evaluable',int(perf.pair_evaluable.sum())==160782)
fa=scen.loc[~scen.true_shared,['abf_h4_rate','matched_h4_rate']].mean().to_dict();se=scen.loc[scen.true_shared,['abf_h4_rate','matched_h4_rate']].mean().to_dict();check('False-sharing and recovery tradeoff',fa['matched_h4_rate']<fa['abf_h4_rate'] and se['matched_h4_rate']<se['abf_h4_rate'],{'false_H4':fa,'shared_recovery':se})
donor=frames['S9/S9_donor_target_panel.tsv'];summ=frames['S9/S9_exact_5vs5_tissue.tsv'];tissue=[]
for axis in ['FCRL3_B','IL12RB2_NK']:
 d=donor[donor.target_lineage==axis]; y=np.log1p(d.target_lineage_CPM.to_numpy());lab=(d.group=='PBC').to_numpy();obs=float(y[lab].mean()-y[~lab].mean());dif=[]
 for comb in itertools.combinations(range(10),5):
  m=np.zeros(10,dtype=bool);m[list(comb)]=True;dif.append(float(y[m].mean()-y[~m].mean()))
 p=float((np.abs(dif)>=abs(obs)-1e-12).mean());s=summ[summ.axis==axis].iloc[0]
 check(axis+' exact252 replay',len(d)==10 and d.run.nunique()==10 and abs(obs-s.mean_log1p_CPM_difference_PBC_minus_control)<1e-12 and abs(p-s.exact_label_permutation_p)<1e-12)
 check(axis+' detection ten donors',((d.gate_cells>=10)&(d.target_umi>=3)&(d.positive_cells>=2)).all())
 tissue.append({'axis':axis,'effect':obs,'p':p,'q':float(s.BH_q_two_prespecified_targets)})
fg=frames['data/R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv'];cs=frames['data/R7C0_OneK_NK_IL12RB2_CS_in_FinnGenR13_disease_CS.tsv'];check('External threepriors 1175variants',len(fg)==3 and objects['data/R7C0_FinnGenR13_x_OneK_IL12RB2_external_coloc_state.json']['n_variants']==1175)
check('External2 of2 QTL CS membership',len(cs)==2 and cs.in_finngen_r13_disease_cs.all())
tri=objects['data/R7C0_IL12RB2_chromatin_triangle_adjudication.json'];check('Triangle direct mediation unavailable','unavailable' in tri['remaining_gap'] or 'does not provide' in tri['remaining_gap'])
# This portable audit deliberately avoids unpublished local-workspace receipts.
(O/'PORTABLE_AUDIT_SCOPE.json').write_text(json.dumps({'repository_root':str(R),'semantic_scope':'Current public Source Data and compact aggregate results; raw scientific fits and large upstream inputs are outside this portable replay.','source_package':str(B.relative_to(R))},ensure_ascii=False,indent=2),encoding='utf-8')
# Read and identify every portable result object; no binary/raw inference is fabricated.
result_inventory=[]
for p in sorted(RESULTS_ROOT.rglob('*')):
 if p.is_file() and p.suffix in ['.json','.tsv','.csv']:
  b=p.read_bytes();v={'path':str(p.relative_to(M)),'bytes':len(b),'sha256':sha(b)}
  try:
   if not b and 'r6a2b0' in str(p):
    v.update(parse='DECLARED_ARCHIVAL_EMPTY_NO_RESULT',semantic_keys='Historical IgAN target stage; no signal/CS rows; not current PBC evidence')
    result_inventory.append(v);continue
   if p.suffix=='.json':obj=json.loads(b.decode('utf-8-sig'));v['semantic_keys']=';'.join(obj.keys()) if isinstance(obj,dict) else 'LIST'
   else:f=pd.read_csv(io.BytesIO(b),sep='\t' if p.suffix=='.tsv' else ',');v['rows']=len(f);v['semantic_keys']=';'.join(f.columns)
   v['parse']='PASS'
  except Exception as e:v.update(parse='FAIL',error=str(e))
  result_inventory.append(v)
check('Portable objects parse or explicit archival empty',all(x['parse'] in ['PASS','DECLARED_ARCHIVAL_EMPTY_NO_RESULT'] for x in result_inventory),{'total':len(result_inventory),'nonempty_parse_pass':sum(x['parse']=='PASS' for x in result_inventory),'archival_empty':sum(x['parse']=='DECLARED_ARCHIVAL_EMPTY_NO_RESULT' for x in result_inventory)})
def tsv(name,rows):
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with (O/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=keys,delimiter='\t');w.writeheader();w.writerows(rows)
tsv('SCIENTIFIC_ENDPOINT_REPLAY_QA.tsv',checks);tsv('SOURCE_ARCHIVE_FULL_INVENTORY.tsv',sources);tsv('ALL_PORTABLE_RESULT_CONTENT_INDEX.tsv',result_inventory)
co=T.groupby(['R7B1B_v2_role','M_simple_state']).size().unstack(fill_value=0);co.to_csv(O/'COHORT_OUTCOMES_RECOMPUTED.tsv',sep='\t')
pd.crosstab(T.A2_simple_state,T.M_simple_state).to_csv(O/'A2_TO_M_RECOMPUTED.tsv',sep='\t')
payload={'states':states,'roles':T.R7B1B_v2_role.value_counts().to_dict(),'false_H4':fa,'shared_recovery':se,'tissue':tissue,'pf50':pf,'source_members':len(sources),'portable_result_objects':len(result_inventory),'checks_pass':sum(x['status']=='PASS' for x in checks),'checks_fail':sum(x['status']=='FAIL' for x in checks)}
(O/'EVIDENCE_AUDIT_STATE.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(payload,ensure_ascii=False))
if payload['checks_fail']:raise SystemExit(1)
