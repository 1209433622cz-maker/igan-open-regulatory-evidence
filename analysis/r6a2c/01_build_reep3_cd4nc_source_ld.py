#!/usr/bin/env python3
"""R6A2C: build exact OneK1K CD4_NC source LD for REEP3 only."""
from pathlib import Path
import hashlib,json,os
import numpy as np,pandas as pd
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT",Path.cwd()))
BED=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bed"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
FAM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.fam"
SAMPLES=ROOT/"3_results/03_qtl/R5A2A2/cell_sample_lists/CD4_NC.samples.txt"
QTL=ROOT/"3_results/03_qtl/R6A2B0/R6A2B0_OneK1K_8locus_QTL.tsv.gz"
OUT=ROOT/"3_results/04_integration/R6A2C/sourceLD/REEP3_REEP3_CD4_NC"; OUT.mkdir(parents=True,exist_ok=True)
LEAD="10:65363048"; SHARED="10:65376395"

def sha256(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while b:=f.read(8*1024*1024): h.update(b)
 return h.hexdigest()

for p in [BED,BIM,FAM,SAMPLES,QTL]:
 if not p.exists(): raise FileNotFoundError(p)
fam=pd.read_csv(FAM,sep=r"\s+",header=None,dtype=str); ids=fam.iloc[:,1].tolist(); idx={x:i for i,x in enumerate(ids)}
keep_ids=[x.strip() for x in SAMPLES.read_text(encoding='utf-8').splitlines() if x.strip()]
missing=[x for x in keep_ids if x not in idx]
if missing: raise RuntimeError(f"sample IDs absent from FAM: {missing[:5]}")
if len(keep_ids)!=980: raise RuntimeError(f"expected 980 CD4_NC donors, got {len(keep_ids)}")
keep=np.array([idx[x] for x in keep_ids],dtype=int)
bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=['chr','variant_id','cm','pos','A1','A2'],dtype=str); bim['gi']=np.arange(len(bim))
q=pd.read_csv(QTL,sep='\t')
q=q[(q.locus=='REEP3')&(q.gene=='REEP3')&(q.cell_type=='CD4_NC')].drop_duplicates('variant_id').copy()
if q.empty: raise RuntimeError('REEP3/CD4_NC QTL rows absent')
v=q.merge(bim[['variant_id','gi','A1','A2']],on='variant_id',how='inner',validate='one_to_one')
if len(v)!=len(q): raise RuntimeError(f"QTL/BIM coverage mismatch {len(v)}/{len(q)}")
if not ((v.A1_effect_allele.astype(str)==v.A1)&(v.A2_other_allele.astype(str)==v.A2)).all(): raise RuntimeError('A1/A2 semantics mismatch')
bps=(len(ids)+3)//4; G=np.empty((len(keep),len(v)),dtype=np.float32); missing_rates=[]
with BED.open('rb') as f:
 if f.read(3).hex()!='6c1b01': raise RuntimeError('BED is not SNP-major PLINK v1')
 for j,gi in enumerate(v.gi.astype(int)):
  f.seek(3+gi*bps); raw=f.read(bps)
  code=np.fromiter(((b>>s)&3 for b in raw for s in (0,2,4,6)),dtype=np.int8,count=bps*4)[:len(ids)][keep]
  miss=(code==1); missing_rates.append(float(miss.mean()))
  dos=np.where(code==0,2,np.where(code==2,1,np.where(code==3,0,np.nan))).astype(float)
  if np.isnan(dos).any(): dos=np.where(np.isnan(dos),np.nanmean(dos),dos)
  G[:,j]=dos
sd=G.std(0,ddof=1); ok=np.isfinite(sd)&(sd>0)
if not ok.all():
 v=v.loc[ok].reset_index(drop=True); G=G[:,ok]; missing_rates=list(np.asarray(missing_rates)[ok])
G=(G-G.mean(0))/G.std(0,ddof=1)
R=(G.T@G)/(G.shape[0]-1); R=(R+R.T)/2; np.fill_diagonal(R,1)
G32=G.astype(np.float32); R32=R.astype(np.float32)
np.save(OUT/'standardized_A1_dosage.npy',G32); np.save(OUT/'raw_signed_A1_correlation.npy',R32); R32.astype('<f4').tofile(OUT/'raw_signed_A1_correlation.float32.bin')
(OUT/'active_donors.txt').write_text('\n'.join(keep_ids)+'\n',encoding='utf-8')
v.insert(0,'LD_order_zero_based',np.arange(len(v),dtype=int)); v['missing_rate']=missing_rates; v.to_csv(OUT/'LD_variants.tsv',sep='\t',index=False)
dual=(G@G.T)/(G.shape[0]-1); dual=(dual+dual.T)/2; eig=np.linalg.eigvalsh(dual.astype(float))
lead_present=bool((v.variant_id==LEAD).any())
nearest_idx=int((pd.to_numeric(v['position_GRCh37'])-int(LEAD.split(':')[1])).abs().idxmin())
qc={'status':'PASS','locus':'REEP3','gene':'REEP3','cell':'CD4_NC','n_samples':len(keep_ids),'n_variants':len(v),
 'disease_lead_present':lead_present,
 'disease_lead_absence_interpretation':None if lead_present else 'Not present in the source QTL/genotype intersection; recorded as a coverage limitation, not an LD-QC failure.',
 'nearest_variant_to_disease_lead':str(v.loc[nearest_idx,'variant_id']),
 'nearest_variant_distance_bp':int(abs(int(v.loc[nearest_idx,'position_GRCh37'])-int(LEAD.split(':')[1]))),
 'smoke_shared_top_present':bool((v.variant_id==SHARED).any()),
 'finite':bool(np.isfinite(R).all()),'max_asymmetry':float(np.max(abs(R-R.T))),'max_diag_dev':float(np.max(abs(np.diag(R)-1))),
 'dual_min_eigenvalue':float(eig.min()),'max_missing_rate':float(max(missing_rates) if missing_rates else 0),
 'LD_variants_sha256':sha256(OUT/'LD_variants.tsv'),'dosage_sha256':sha256(OUT/'standardized_A1_dosage.npy'),'raw_LD_sha256':sha256(OUT/'raw_signed_A1_correlation.npy')}
qc['status']='PASS' if qc['finite'] and qc['max_asymmetry']<1e-5 and qc['max_diag_dev']<1e-5 and qc['smoke_shared_top_present'] else 'HOLD'
(OUT/'sourceLD_QC.json').write_text(json.dumps(qc,indent=2),encoding='utf-8'); print(json.dumps(qc,indent=2))
if qc['status']!='PASS': raise SystemExit(2)
