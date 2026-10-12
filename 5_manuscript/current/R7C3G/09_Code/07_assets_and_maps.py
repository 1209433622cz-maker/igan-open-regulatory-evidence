from pathlib import Path
from collections import Counter,defaultdict
import os,json,csv,hashlib,datetime
R=Path(r'H:\SCI2\YR1');A=R/'5_analysis/R7C3G_ExpertNarrative_20261012';O=R/'5_manuscript/R7C3G_ExpertNarrative_20261012';Q=O/'06_QA'
def dump(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
prev=R/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012/ALL_CURRENT_FILES_CLOSING.tsv'
with prev.open(encoding='utf-8-sig',newline='') as f:old={x['relative_path']:x for x in csv.DictReader(f,delimiter='\t')}
files=[];skips=[];errors=[];top=defaultdict(lambda:[0,0]);stack=[str(R)];fresh_bytes=0
while stack:
 folder=stack.pop()
 try:
  with os.scandir('\\\\?\\'+folder) as it:
   for ent in it:
    st=ent.stat(follow_symlinks=False);path=ent.path.removeprefix('\\\\?\\');rel=str(Path(path).relative_to(R)).replace('\\','/')
    if st.st_file_attributes&0x400:skips.append(rel);continue
    if ent.is_dir(follow_symlinks=False):stack.append(path);continue
    before=old.get(rel)
    if before and int(before['size_bytes'])==st.st_size and int(before['mtime_ns'])==st.st_mtime_ns and before['sha256']:
     h=before['sha256'];basis='SAME_DAY_FRESH_HASH_REUSED_SIZE_MTIME_UNCHANGED'
    else:
     hh=hashlib.sha256()
     with open(ent.path,'rb') as f:
      for buf in iter(lambda:f.read(1024*1024),b''):hh.update(buf)
     h=hh.hexdigest();basis='NEW_OR_MODIFIED_FRESH_SHA256';fresh_bytes+=st.st_size
    root=rel.split('/')[0];top[root][0]+=1;top[root][1]+=st.st_size
    files.append({'relative_path':rel,'top_level':root,'size_bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':h,'hash_basis':basis})
 except Exception as e:errors.append({'path':folder,'error':str(e)})
dump(A/'ALL_LOCAL_CURRENT_IDENTITY.tsv',sorted(files,key=lambda x:x['relative_path'].casefold()))
dump(A/'ALL_LOCAL_TOP_LEVEL_SUMMARY.tsv',[{'folder':k,'files':v[0],'bytes':v[1],'GiB':v[1]/2**30} for k,v in sorted(top.items())])
(A/'LOCAL_CURRENT_IDENTITY_STATE.json').write_text(json.dumps({'snapshot_at':datetime.datetime.now().astimezone().isoformat(),'files':len(files),'bytes':sum(x['size_bytes'] for x in files),'GiB':sum(x['size_bytes'] for x in files)/2**30,'fresh_files':sum(x['hash_basis']=='NEW_OR_MODIFIED_FRESH_SHA256' for x in files),'fresh_bytes':fresh_bytes,'hash_reuse_contract':'Prior same-day SHA256 only when exact size and mtime are unchanged; not a new independent rehash of unchanged raw bytes.','skipped_reparse_points':skips,'errors':errors,'previous_identity_inventory':str(prev)},ensure_ascii=False,indent=2),encoding='utf-8')
assert not errors,errors
# Every existing figure object receives a bounded editorial disposition.
roles={
 (1,2):('RECOMPOSE_MAIN_FIG1','Current scope and outcomes are retained; identity/kriging details move to S1.'),
 (3,4):('SPLIT_MAIN_FIG2_AND_FIG3','Old six-panel Figure2 mixed input attribution with pair semantics; redistribute into two questions.'),
 (5,6,7):('SUPPLEMENT_FIG_S1','Full adjacent matrices support attribution; not an additional independent analysis.'),
 (8,9):('HISTORICAL_DENOMINATOR_ONLY','Original A0 trigger counts must not replace matched A2 113/452 denominators.'),
 (10,11):('RECOMPOSE_MAIN_FIG1D','Preserve the 184/455/3 roles; do not select only favorable triggers.'),
 (12,13):('RECOMPOSE_MAIN_FIG4','Discovery channels, estimands and recovery trade-off belong in a single simulation figure.'),
 (14,15,16):('SOURCE_QA_SUPPORT_MAIN_FIG4','Channel audit supports truth-known simulation; duplicated export rather than new evidence.'),
 (17,18):('MAIN_FIG4_SOURCE_CONTEXT','Scenario definitions remain in Methods and figure legend; no separate redundant schematic.'),
 (19,20):('SUPPLEMENT_FIG_S2','LD dependence adds a useful generalization boundary; retain all six scenarios.'),
 (21,22):('ARCHIVE_FINITE_SIMULATION_SENSITIVITY','Bounded S6 mismatch result is already included in main Figure4 and limitations; no universal claim.'),
 (23,24):('ARCHIVE_SECONDARY_GRID_DIAGNOSTIC','Credible-set coverage supports QA; channel adequacy is the main claim and already shown.'),
 (25,26):('RECOMPOSE_MAIN_FIG5_AND_SUPPLEMENT_S3','Prefer external study and CS identity in main; sequential release concordance goes to S3.'),
 (27,28):('RECOMPOSE_MAIN_FIG3','FCRL3 exemplifies cell context and near-complete PF10/PF50 reversal before external support.'),
 (29,30):('SUPPORT_MAIN_FIG3D','B-cell context reproduced across molecular resources; repeated PBC GWAS is not independent disease replication.'),
 (31,):('ARCHIVE_SUPERSEDED_PF_MODEL_DISPLAY','Early positive-control figure shows approximately 0.004 PF50 for CD8_ET; current source gives approximately 0.992. Never combine as current evidence.'),
 (32,33):('RECOMPOSE_MAIN_FIG6','Keep all donors and corrected null; remove redundant detectability-to-mechanism schematic.'),
 (34,35,36):('MAIN_FIG6_DONOR_SOURCE','Original CPM plot remains archival source; current mean-difference test is on log1p CPM and is displayed on that scale.'),
 (37,38,39,40):('ARCHIVE_MG_PROJECT_NOT_PBC_VALIDATION','MG pilots are reusable methodology and failure records, not validation evidence for the current PBC manuscript.'),
 (41,42,43,44,45,46):('ARCHIVE_IGAN_PROJECT_NOT_PBC_VALIDATION','IgAN preflights, ZMIZ1 and REEP3 bounded pilots remain separate archived scientific projects.')}
entries=json.loads((A/'ALL_FIGURE_CONTENT.json').read_text(encoding='utf-8'));out=[]
for x in entries:
 n=int(x['id'][1:]);match=[v for k,v in roles.items() if n in k];assert len(match)==1
 out.append({'image_id':x['id'],'relative_path':x['relative'],'bytes':x['bytes'],'sha256':x['sha256'],'disposition':match[0][0],'rationale':match[0][1],'visual_status':'REVIEWED_CONTACT_SHEETS_AND_CURRENT_FULL_FIGURES','independent_experiment':'NO_FORMATS_AND_DERIVATIVES_ARE_NOT_NEW_EXPERIMENTS'})
dump(Q/'ALL_46_IMAGE_SELECTION_LEDGER.tsv',out)
claims=[
 ('C01','Bounded screening universe','6923;5460;642;47 loci/200 genes/14 cell types','Figure1a;1c','S2/S3/S5','Conditional selected cohort, not PBC-wide prevalence'),
 ('C02','Prespecified symmetric workloads','184 primary;455 H3 layer;3 borderline','Figure1d','S3','No post-SuSiE candidate expansion'),
 ('C03','Input coordination changes labels','15 support-set and19 statistic-definition changes','Figure2a,b;S1','S3/S4','Nonadditive category changes; not known-truth error attribution'),
 ('C04','Reclassification persists with exact shared inputs','8 H4-to-H3;10 H3-to-H4;113/452 starting denominators','Figure2c,d','S3','Complete-procedure contrast; no causal-number-only isolation'),
 ('C05','A comparison can support shared and distinct pairs','32/92 coexisting;92/92 and428/428 same-pair stability','Figure3a','S6','H3 pair is not global absence of a shared pair'),
 ('C06','High model agreement is conditional','491 same;4 changed;25 uninformative of520 definite PF10','Figure3b','S5','Excludes122 PF10-sensitive/uninformative comparisons'),
 ('C07','FCRL3 T-cell assignment is model qualified','ABF .941/.941/.949;PF10 .003636;PF50 .991894','Figure3c','S3/S5','Factor number changes QTL phenotype and residualized LD, not an LD-only experiment'),
 ('C08','FCRL3 B-cell support crosses QTL resources','OneK B_IN/B_MEM .9937/.9910;TenK .9916','Figure3d','S8/current R7A1C source','Same disease GWAS reused; TenK single-causal; not new gene discovery'),
 ('C09','Simulation separates adequacy and pair decisions','486000;160782 pair-evaluable;33.08%','Figure4a,b,d','S7','Finite grid; no end-to-end composite-gate calibration'),
 ('C10','Lower false sharing trades off with recovery','12.41→8.56%;32.99→26.66%','Figure4c;S2','S7','No universal superiority; no observed-truth claims for real-data transitions'),
 ('C11','External disease-study support strengthens IL12RB2 association','795 cases;1175 variants;H4 .9772/.9977/.9998;CS2/2 in17','Figure5a,b','S11','Participant non-overlap unknown; single-causal external test'),
 ('C12','Fixed source coverage is reported without negative overreach','27 queried;22 covered;1 returned disease-eQTL gene','Figure5c','S11','Non-return is unavailable evidence, not failed mechanism'),
 ('C13','Chromatin increases coherence without establishing mediation','H4 eQTL .9703;caQTL .9695;link beta .140574','Figure5d','S11','Best peak-gene context PBMC; no direct eQTL-caQTL posterior or intervention'),
 ('C14','Tissue establishes detectability without corrected enrichment','10 donors;252 assignments;both q=.1111','Figure6','S9','5 surgical controls, small target panel; non-significance is not absence'),
 ('C15','Release stability is supporting identity evidence','R12 CS19;R13 CS17;intersection17;Jaccard17/19','FigureS3','S11 identity JSON and17-row intersection TSV','Sequential releases are correlated, not independent replications')]
dump(Q/'CENTRAL_CLAIM_EVIDENCE_CEILING_MAP.tsv',[dict(zip(['claim_id','claim','evidence','panels','source_family','ceiling'],('E'+c[0][1:],*c[1:]))) for c in claims])
print(json.dumps({'files':len(files),'GiB':sum(x['size_bytes'] for x in files)/2**30,'fresh_hashed':sum(x['hash_basis']=='NEW_OR_MODIFIED_FRESH_SHA256' for x in files),'reparse_skips':len(skips),'image_ledger':len(out),'claims':len(claims)}))
