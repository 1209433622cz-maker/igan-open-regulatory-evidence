import pandas as pd, numpy as np, gzip, math, json
from pathlib import Path
from scipy.special import logsumexp

ROOT=Path(r'H:\SCI2\YR1')
QTL=ROOT/'3_results/03_qtl/R5A2B/OneK1K_chr5_bounded_region_pairs.tsv.gz'
GWAS={
'MG_overall':ROOT/'3_results/01_gwas/R5A2B/GCST90432156_MG_overall_chr5_GRCh37_fixed_1Mb.tsv.gz',
'EOMG':ROOT/'3_results/01_gwas/R5A2B/GCST90432157_EOMG_chr5_GRCh37_fixed_1Mb.tsv.gz',
'LOMG':ROOT/'3_results/01_gwas/R5A2B/GCST90432158_LOMG_chr5_GRCh37_fixed_1Mb.tsv.gz',
}
OUT=ROOT/'3_results/04_integration/R5A2B'; OUT.mkdir(parents=True,exist_ok=True)

def logdiff(a,b):
    # log(exp(a)-exp(b)), expect a>=b
    if b>=a:
        # numerical equality can occur from underflow/rounding; return -inf
        return -np.inf
    return a + np.log1p(-np.exp(b-a))

def sdY_est(vbeta, maf, n):
    oneover=1.0/vbeta
    nvx=2.0*n*maf*(1-maf)
    # lm(nvx ~ oneover - 1)
    cf=np.sum(oneover*nvx)/np.sum(oneover*oneover)
    if not np.isfinite(cf) or cf<=0:
        raise ValueError(f'bad sdY coefficient {cf}')
    return math.sqrt(cf)

def labf(beta,se,trait_type,sdY=1.0):
    V=np.asarray(se,float)**2
    z=np.asarray(beta,float)/np.asarray(se,float)
    sdprior=(0.15*sdY) if trait_type=='quant' else 0.2
    r=sdprior**2/(sdprior**2+V)
    return 0.5*(np.log1p(-r)+r*z*z)

def combine(l1,l2,p1=1e-4,p2=1e-4,p12=1e-5):
    lsum=l1+l2
    a1=logsumexp(l1); a2=logsumexp(l2); a12=logsumexp(lsum)
    lH=np.array([0.0,
                  math.log(p1)+a1,
                  math.log(p2)+a2,
                  math.log(p1)+math.log(p2)+logdiff(a1+a2,a12),
                  math.log(p12)+a12])
    pp=np.exp(lH-logsumexp(lH))
    return pp, lsum

# Read QTL and GWAS
q=pd.read_csv(QTL,sep='\t',compression='gzip')
TARGETS=ROOT/'2_code/06_intake/mg_r5a2b/chr5_source_significant_smoke_targets.tsv'
t=pd.read_csv(TARGETS,sep='\t')
allowed=set(zip(t['cell_type'].astype(str),t['gene_symbol'].astype(str)))
q=q[q.apply(lambda r:(str(r['cell_type']),str(r['phenotype_id'])) in allowed,axis=1)].copy()
if not allowed:
    raise RuntimeError('No frozen chr5 source-significant targets')
g={k:pd.read_csv(v,sep='\t',compression='gzip') for k,v in GWAS.items()}
for k,df in g.items():
    df=df[df['inference_eligible']==True].copy()
    g[k]=df.set_index('variant_id',drop=False)

rows=[]; snprows=[]
for (cell,gene),qd in q.groupby(['cell_type','phenotype_id'],sort=True):
    qd=qd.drop_duplicates('variant_id').set_index('variant_id',drop=False)
    n=int(qd['n_expression_donors'].iloc[0])
    for trait,gd in g.items():
        # Use a platform-independent order so tied posterior ranks are reproducible.
        ids=pd.Index(sorted(set(qd.index).intersection(gd.index)))
        m=qd.loc[ids].join(gd.loc[ids].add_prefix('g_'),how='inner')
        # finite + positive SE
        m=m[np.isfinite(m['slope_A1']) & np.isfinite(m['slope_se']) & (m['slope_se']>0) &
            np.isfinite(m['g_beta_logOR_A1']) & np.isfinite(m['g_standard_error']) & (m['g_standard_error']>0)]
        if len(m)<500: continue
        maf=np.minimum(m['af_A1'].to_numpy(float),1-m['af_A1'].to_numpy(float))
        sdY=sdY_est(m['slope_se'].to_numpy(float)**2,maf,n)
        lq=labf(m['slope_A1'],m['slope_se'],'quant',sdY)
        lg=labf(m['g_beta_logOR_A1'],m['g_standard_error'],'cc',1.0)
        p12s=[1e-6,1e-5,1e-4]
        ppdict={}
        lsum_default=None
        for p12 in p12s:
            pp,lsum=combine(lg,lq,1e-4,1e-4,p12)
            ppdict[p12]=pp
            if p12==1e-5: lsum_default=lsum
        pp=ppdict[1e-5]
        ratio=pp[4]/(pp[3]+pp[4]) if pp[3]+pp[4]>0 else np.nan
        ratios={p:ppdict[p][4]/(ppdict[p][3]+ppdict[p][4]) if ppdict[p][3]+ppdict[p][4]>0 else np.nan for p in p12s}
        maxidx=int(np.argmax(lsum_default)); maxvid=m.index[maxidx]
        snppp=np.exp(lsum_default-logsumexp(lsum_default))
        top_snp_pp=float(snppp[maxidx])
        qmin=float(m['pval_nominal'].min()); qtop=m['pval_nominal'].idxmin()
        gpcol='g_p_value'
        gmin=float(m[gpcol].min()); gtop=m[gpcol].idxmin()
        # descriptive/frozen-ish classification
        robust=(pp[4]>=0.8 and ratio>=0.8 and all(ratios[p]>=0.5 for p in p12s))
        prior_flip=(ratios[1e-6]<0.5 and ratios[1e-4]>0.5) or (ratios[1e-6]>0.5 and ratios[1e-4]<0.5)
        h34=pp[3]+pp[4]
        if robust:
            cls='PASS_ROBUST_SHARED_SIGNAL'
        elif h34>=0.8 and (prior_flip or ratio>=0.2):
            cls='HOLD_LD_REQUIRED'
        elif gmin<=5e-8 and qmin<=1e-4 and max(ppdict[p][4] for p in p12s)<0.2:
            cls='FAIL_SUFFICIENT_COVERAGE_SINGLE_CAUSAL'
        else:
            cls='UNINFORMATIVE_OR_LOW_QTL_SIGNAL'
        rows.append({
            'trait':trait,'cell_type':cell,'phenotype_id':gene,'n_snps':len(m),'qtl_N':n,'qtl_sdY_est':sdY,
            'gwas_min_p':gmin,'gwas_top_variant':gtop,'qtl_min_p':qmin,'qtl_top_variant':qtop,
            'PP_H0_p12_1e-5':pp[0],'PP_H1_p12_1e-5':pp[1],'PP_H2_p12_1e-5':pp[2],
            'PP_H3_p12_1e-5':pp[3],'PP_H4_p12_1e-5':pp[4],'H4_over_H3H4_p12_1e-5':ratio,
            'H4_p12_1e-6':ppdict[1e-6][4],'H4ratio_p12_1e-6':ratios[1e-6],
            'H4_p12_1e-4':ppdict[1e-4][4],'H4ratio_p12_1e-4':ratios[1e-4],
            'shared_top_variant':maxvid,'shared_top_SNP_PP_H4_conditional':top_snp_pp,
            'prior_flip_H3H4':prior_flip,'classification':cls
        })
        # top 10 SNPs default conditional H4
        # Break exact SNP-PP ties by variant ID instead of relying on input order.
        topidx=np.lexsort((m.index.to_numpy(dtype=str), -snppp))[:10]
        for rank,j in enumerate(topidx,1):
            r=m.iloc[j]
            snprows.append({'trait':trait,'cell_type':cell,'phenotype_id':gene,'rank':rank,'variant_id':m.index[j],
                            'SNP_PP_H4_conditional':float(snppp[j]),'gwas_beta_A1':float(r['g_beta_logOR_A1']),
                            'gwas_se':float(r['g_standard_error']),'gwas_p':float(r['g_p_value']),
                            'qtl_slope_A1':float(r['slope_A1']),'qtl_se':float(r['slope_se']),'qtl_p':float(r['pval_nominal'])})

res=pd.DataFrame(rows).sort_values(['trait','PP_H4_p12_1e-5'],ascending=[True,False])
snps=pd.DataFrame(snprows)
res.to_csv(OUT/'chr5_coloc_abf_smoke.tsv',sep='\t',index=False)
snps.to_csv(OUT/'chr5_coloc_abf_top_snps.tsv',sep='\t',index=False)
summary={
    'n_tests':len(res),
    'by_trait':res.groupby('trait').size().to_dict(),
    'classification_counts':res['classification'].value_counts().to_dict(),
    'top_default_H4':res.nlargest(20,'PP_H4_p12_1e-5')[['trait','cell_type','phenotype_id','n_snps','gwas_min_p','qtl_min_p','PP_H3_p12_1e-5','PP_H4_p12_1e-5','H4_over_H3H4_p12_1e-5','H4_p12_1e-6','H4_p12_1e-4','classification','shared_top_variant','shared_top_SNP_PP_H4_conditional']].to_dict('records'),
}
(OUT/'chr5_coloc_abf_smoke_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2)[:15000])
