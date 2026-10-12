from pathlib import Path
import io,gzip,json,zipfile,hashlib,csv,textwrap
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import PercentFormatter
R=Path(r'H:\SCI2\YR1');B=R/'5_manuscript/R7C3F_SubmissionCandidate_20261012';O=R/'5_manuscript/R7C3G_ExpertNarrative_20261012';F=O/'02_Figures';F.mkdir(parents=True,exist_ok=True);Q=O/'06_QA';Q.mkdir(parents=True,exist_ok=True)
frames={};objs={};src=[]
for zp in (B/'05_Source_Data').glob('*.zip'):
 with zipfile.ZipFile(zp) as z:
  for n in z.namelist():
   b=z.read(n)
   if n.endswith(('.tsv','.tsv.gz')):frames[n]=pd.read_csv(io.BytesIO(gzip.decompress(b) if n.endswith('.gz') else b),sep='\t')
   elif n.endswith('.json'):objs[n]=json.loads(b.decode('utf-8-sig'))
   src.append({'archive':zp.name,'member':n,'sha256':hashlib.sha256(b).hexdigest()})
T=frames['S3/S3_642_A0_A1_A2_M_trajectories.tsv'];C=frames['S5/S5_642_PF10_PF50_classifications.tsv'];S=frames['S6/S6_signal_semantics_642.tsv']
BLUE='#2166AC';TEAL='#16857B';ORANGE='#C66A23';PURPLE='#8064A2';GREY='#8C95A3';DARK='#26313E';COL={'H4':TEAL,'H3':ORANGE,'MODEL_SENSITIVE':PURPLE,'UNINFORMATIVE':GREY}
plt.rcParams.update({'font.family':'Arial','font.size':8,'axes.titlesize':9,'axes.titleweight':'bold','axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':300})
panel_rows=[];values={}
def panel(ax,letter,title):
 ax.set_title('\n'.join(textwrap.wrap(title,width=38)),loc='left',pad=10);ax.text(-.16,1.14,letter+')',transform=ax.transAxes,fontsize=10,fontweight='bold',va='top')
def layout(title):
 fig,axs=plt.subplots(2,2,figsize=(7.05,6.25));fig.suptitle(title,fontsize=10.5,fontweight='bold',y=.98);fig.subplots_adjust(left=.15,right=.97,bottom=.14,top=.85,wspace=.53,hspace=.79);return fig,axs.flat
def save(fig,n,title):
 for ext in ['pdf','svg','png']:fig.savefig(F/f'Figure_{n}.{ext}',facecolor='white')
 plt.close(fig);values[str(n)]['title']=title
def one(d,mask):
 f=d.loc[mask];assert len(f)==1;return f.iloc[0]
def bars(ax,labs,vals,cols,ylim=1.08,fmt='.3f'):
 bb=ax.bar(labs,vals,color=cols,width=.62)
 for b,v in zip(bb,vals):ax.text(b.get_x()+b.get_width()/2,v+ylim*.025,format(v,fmt),ha='center',fontsize=7)
 ax.set_ylim(0,ylim)
def sources(n,letter,job,source):panel_rows.append({'figure':n,'panel':letter,'job':job,'source_member':source,'interpretation_ceiling':'Statistical association / sensitivity; no causal mechanism','display_values':'FIGURE_VALUES.json'})

# Figure 1: scope, exact input contract, overall and prespecified-cohort outcomes.
fig,axs=layout('A bounded PBC screen with an explicit input contract');a,b,c,d=axs
panel(a,'a','Screen and follow-up');a.axis('off')
for y,lab,count,col in [(.78,'Frozen registry',6923,BLUE),(.49,'ABF eligible',5460,TEAL),(.20,'High-information follow-up',642,PURPLE)]:
 a.add_patch(Rectangle((.05,y),.92,.18,facecolor=col,edgecolor='none'));a.text(.51,y+.12,lab,ha='center',color='white',fontsize=8,fontweight='bold');a.text(.51,y+.035,f'n = {count:,}',ha='center',color='white',fontsize=8)
for y in [.74,.45]:a.annotate('',xy=(.51,y-.06),xytext=(.51,y+.02),arrowprops={'arrowstyle':'->','color':GREY})
a.text(.51,.02,'1,463 coverage-insufficient; not negative',ha='center',fontsize=7)
panel(b,'b','Four arms distinguish input changes');b.axis('off')
rows=[['Arm','Support','Disease','Procedure'],['A0','S_A','GCST','ABF'],['A1','S_M','GCST','ABF'],['A2','S_M','GJOKA z','ABF'],['M','S_M','GJOKA z','Multi-signal']]
table=b.table(cellText=rows[1:],colLabels=rows[0],cellLoc='center',colWidths=[.15,.22,.27,.36],bbox=[-.04,.19,1.06,.77]);table.auto_set_font_size(False);table.set_fontsize(7.2)
for (rr,cc),cell in table.get_celld().items():cell.set_edgecolor('#D8DEE5');cell.set_facecolor('#EDF2F7' if rr==0 else 'white')
b.text(.50,.06,'A2 versus M compares complete procedures,\nnot only the number of causal variants.',ha='center',fontsize=7)
panel(c,'c','Frozen PF10 outcomes');left=0;states=['H4','H3','MODEL_SENSITIVE','UNINFORMATIVE'];cnt=T.M_simple_state.value_counts().to_dict()
for state in states:
 n=cnt[state];c.barh(0,n,left=left,color=COL[state],height=.5,label=state.replace('_',' ').title());c.text(left+n/2,0,str(n),ha='center',va='center',color='white',fontsize=8,fontweight='bold');left+=n
c.set(yticks=[],xlim=(0,642),ylim=(-.7,.8),xlabel='Comparisons');c.legend(loc='upper center',bbox_to_anchor=(.5,-.28),ncol=2,frameon=False,fontsize=7)
c.text(.5,.88,'92 H4 comparisons = 27 genes at 19 loci',transform=c.transAxes,ha='center',fontsize=6.5)
panel(d,'d','Prespecified cohorts remain separate');co=T.groupby(['R7B1B_v2_role','M_simple_state']).size().unstack(fill_value=0)
roles=['PRIMARY_184_TRIGGER_VERIFICATION','H3_RESCUE_FALSIFICATION','BORDERLINE_HIGH_INFORMATION_CALIBRATION'];names=['Primary (184)','H3 layer (455)','Borderline (3)'];left=np.zeros(3)
for state in states:
 v=co.loc[roles,state].to_numpy();d.barh(np.arange(3),v,left=left,color=COL[state],height=.6)
 for i,n in enumerate(v):
  if n>=19:d.text(left[i]+n/2,i,str(n),ha='center',va='center',color='white',fontsize=7)
 left+=v
d.set(yticks=np.arange(3),yticklabels=names,xlabel='Comparisons',xlim=(0,470));d.invert_yaxis()
d.text(20,2,'1 H4; 2 uninformative',va='center',fontsize=6.5)
values['1']={'scope':[6923,5460,642],'states':cnt,'cohorts':co.to_dict()};save(fig,1,'A bounded PBC screen with an explicit input contract')
for l,j,s in [('a','Define eligible denominator','S2/S2_PBCwide_6923_screening_registry.tsv.gz'),('b','Expose A0 A1 A2 M contract','S3/S3_642_A0_A1_A2_M_trajectories.tsv'),('c','Overall frozen state distribution','S5/S5_642_PF10_PF50_classifications.tsv'),('d','Separate original184 from455 rescue','S3/S3_642_A0_A1_A2_M_trajectories.tsv')]:sources(1,l,j,s)

# Figure 2: only input attribution and matched reclassification.
fig,axs=layout('Matched inputs retain bidirectional reclassification');a,b,c,d=axs
panel(a,'a','Support matching removes variants');a.hist(T.removed_n,bins=18,color=BLUE);a.axvline(T.removed_n.median(),color=ORANGE,linestyle='--');a.set(xlabel='Variants removed from S_A',ylabel='Comparisons');a.text(.97,.92,'19–114; median 65\nMedian fraction 7.67%',transform=a.transAxes,ha='right',va='top',fontsize=7)
panel(b,'b','Adjacent state changes');cv=[int((T.A0_simple_state!=T.A1_simple_state).sum()),int((T.A1_simple_state!=T.A2_simple_state).sum()),int((T.A2_simple_state!=T.M_simple_state).sum())];bars(b,['A0→A1','A1→A2','A2→M'],cv,[BLUE,TEAL,PURPLE],160,'.0f');b.set_ylabel('Changed states / 642');b.text(.5,.82,'Affected sets can overlap;\ncounts are not additive.',transform=b.transAxes,ha='center',fontsize=7)
panel(c,'c','Full A2 to M transition matrix');ct=pd.crosstab(T.A2_simple_state,T.M_simple_state).reindex(index=['H4','H3','AMBIGUOUS','H4_BORDERLINE','UNINFORMATIVE'],columns=states,fill_value=0);c.imshow(ct,cmap='Blues',aspect='auto',vmin=0,vmax=428)
for i in range(len(ct)):
 for j in range(4):c.text(j,i,str(ct.iloc[i,j]),ha='center',va='center',color='white' if ct.iloc[i,j]>200 else DARK,fontsize=8)
c.set(xticks=range(4),xticklabels=['H4','H3','Sensitive','Uninform.'],yticks=range(5),yticklabels=['H4','H3','Ambiguous','Borderline','Uninform.'],xlabel='M state',ylabel='A2 state');c.tick_params(axis='y',labelsize=6.7)
panel(d,'d','Transitions use the A2 denominator');mat=ct.loc[['H4','H3']].to_numpy();den=mat.sum(axis=1);base=np.zeros(2)
for j,state in enumerate(states):
 v=mat[:,j]/den;d.bar(['A2 H4\n(n=113)','A2 H3\n(n=452)'],v,bottom=base,color=COL[state],width=.65)
 for i,n in enumerate(mat[:,j]):
  if n>=8 and v[i]>.03:d.text(i,base[i]+v[i]/2,str(n),color='white' if v[i]>.08 else DARK,ha='center',va='center',fontsize=7)
 base+=v
d.set(ylim=(0,1),ylabel='Fraction within starting state');d.yaxis.set_major_formatter(PercentFormatter(1));d.text(.5,-.29,'8 H4→H3 and 10 H3→H4; not error corrections',transform=d.transAxes,ha='center',fontsize=7)
values['2']={'removed_min':int(T.removed_n.min()),'removed_max':int(T.removed_n.max()),'median':float(T.removed_n.median()),'state_changes':cv,'matrix':ct.to_dict()};save(fig,2,'Matched inputs retain bidirectional reclassification')
for l,j in [('a','Exact support'),('b','Nonadditive input attribution'),('c','Exhaustive642 state transitions'),('d','Two distinct starting denominators')]:sources(2,l,j,'S3/S3_642_A0_A1_A2_M_trajectories.tsv')

# Figure 3: signal semantics, model sensitivity, and a concrete cell-context contrast.
fig,axs=layout('Signal identity and model context limit regulatory labels');a,b,c,d=axs
panel(a,'a','Shared and distinct pairs can coexist');ks=S.merge(T[['comparison_id','M_simple_state']],validate='one_to_one');h=ks[ks.M_simple_state=='H4'];mixed=int(h.mixed_h4_h3_within_any_config.sum());bars(a,['No qualifying\nH3 pair','Shared +\ndistinct pairs'],[len(h)-mixed,mixed],[TEAL,BLUE],105,'.0f');a.set_ylabel('H4-supported comparisons (n=92)');a.text(.5,.87,'Same-pair stability: 92/92 H4, 428/428 H3',transform=a.transAxes,ha='center',fontsize=6.8)
panel(b,'b','PF50 sensitivity is conditional on PF10');pc=C[C.PF10_multisignal_state.isin(['H4_SUPPORTED_STABLE','H3_SUPPORTED_STABLE'])].PF10_PF50_sensitivity.value_counts();pp=[int(pc[k]) for k in ['MATCH','PF10_PF50_SENSITIVE','PF50_UNINFORMATIVE']];bars(b,['Same','Changed','Uninform.'],pp,[TEAL,PURPLE,GREY],570,'.0f');b.set_ylabel('Definite PF10 comparisons (n=520)')
cd=one(T,T.comparison_id=='R7B1_000414');cdm=one(C,C.comparison_id=='R7B1_000414');vv=[float(cd.A0_PP_H4),float(cd.A1_PP_H4),float(cd.A2_PP_H4),float(cd.pf10_l10_best_h4),float(cdm.pf50_l10_best_h4)]
panel(c,'c','FCRL3 in CD8 effector T cells');bars(c,['A0','A1','A2','M\nPF10','M\nPF50'],vv,[GREY,GREY,BLUE,ORANGE,PURPLE],1.12,'.3f');c.axhline(.8,color=ORANGE,ls='--',lw=.8);c.set_ylabel('PP.H4 or best signal-pair PP.H4')
panel(d,'d','FCRL3 B-cell support across QTL resources');rep=C[(C.gene=='FCRL3')&C.cell_type.isin(['B_IN','B_MEM'])];binval=float(one(rep,rep.cell_type=='B_IN').pf10_l10_best_h4);bmval=float(one(rep,rep.cell_type=='B_MEM').pf10_l10_best_h4)
ten=R/'3_results/04_integration/R7B1E/figure_source_data/Figure4_TenK_replication.tsv'
matches=[p for p in (R/'3_results').rglob('*.tsv') if 'TenK' in p.name and 'replication' in p.name]
# TenK default is traceable through the frozen source record, not a display fallback.
reg=frames['S8/S8_external_target_registry.tsv']; records=reg.to_dict('records');(Q/'TENK_SOURCE_SCHEMA.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'3_results/04_integration/R7A1C/R7A1C_FCRL3_TenK_Bintermediate_coloc.tsv';fd=pd.read_csv(p,sep='\t');rr=one(fd,fd.p12==1e-5);tv=float(rr.PP_H4);assert abs(tv-.9916)<.0001
bars(d,['OneK\nB_IN','OneK\nB_MEM','TenK\nB intermed.'],[binval,bmval,tv],[TEAL,TEAL,BLUE],1.12,'.4f');d.axhline(.8,color=ORANGE,ls='--',lw=.8);d.set_ylabel('Default PP.H4')
values['3']={'H4_with_H3_pair':mixed,'H4_without_qualifying_H3_pair':len(h)-mixed,'pf50':pp,'CD8_ET':vv,'B_context':[binval,bmval,tv],'TenK_source':str(p)};save(fig,3,'Signal identity and model context limit regulatory labels')
for l,j,s in [('a','Replace global H4 mechanism label','S6/S6_signal_semantics_642.tsv'),('b','Conditional PF50 sensitivity','S5/S5_642_PF10_PF50_classifications.tsv'),('c','Concrete near-complete model reversal','S3/S3_642_A0_A1_A2_M_trajectories.tsv + S5'),('d','Separate cell context from gene identity',str(p))]:sources(3,l,j,s)

# Figure 4: distinguish credible-set discovery from pair-conditional inference.
sc=frames['S7/S7_scenario_summary.tsv'];perf=frames['S7/S7_discovery_vs_estimator.tsv'];ch=frames['S7/S7_channel_summary.tsv'];fig,axs=layout('Simulation separates discovery from shared-signal decisions');a,b,c,d=axs;labs=['S1','S2','S3','S4','S5','S6'];xx=np.arange(6)
panel(a,'a','Outcome channels in each scenario');bottom=np.zeros(6);cats=['NO_CS_BOTH','NO_DISEASE_CS','NO_QTL_CS','PAIR_H3','PAIR_H4','PAIR_UNINFORMATIVE'];cols=['#DBE1EA','#B8C3D0',GREY,ORANGE,TEAL,PURPLE];by=ch[ch.scope=='PRIMARY_MATCHED_BY_SCENARIO']
for cat,col in zip(cats,cols):
 v=[float(by[(by.scenario==s)&(by.matched_channel==cat)].n.sum())/81000 for s in perf.scenario];a.bar(labs,v,bottom=bottom,color=col,label=cat.replace('_',' ').title(),width=.7);bottom+=v
a.set(ylim=(0,1),ylabel='Fraction of 81,000 / scenario');a.legend(loc='upper center',bbox_to_anchor=(.5,-.19),ncol=2,fontsize=6,frameon=False)
panel(b,'b','Discovery and estimator denominators');w=.24
for off,col,series,lab in [(-w,BLUE,perf.pair_evaluable_rate,'Pair evaluable'),(0,TEAL,perf.H4_rate_unconditional,'H4 / all'),(w,PURPLE,perf.H4_rate_conditional_on_pair,'H4 / evaluable')]:b.bar(xx+off,series,width=w,color=col,label=lab)
b.set(xticks=xx,xticklabels=labs,ylim=(0,1),ylabel='Rate');b.legend(fontsize=6.5,frameon=False,loc='upper right')
panel(c,'c','False sharing and recovery trade off');c.bar(xx-.18,sc.abf_h4_rate,width=.35,color=GREY,label='Single-causal ABF');c.bar(xx+.18,sc.matched_h4_rate,width=.35,color=TEAL,label='Matched multi-signal');c.set(xticks=xx,xticklabels=labs,ylim=(0,.82),ylabel='Unconditional H4 rate');c.legend(frameon=False,fontsize=6.5,loc='upper right');c.text(.03,.95,'Distinct: S2, S5\nShared: S1, S3, S4, S6',transform=c.transAxes,va='top',fontsize=6.5)
panel(d,'d','No credible set is not a technical error');ov=ch[ch.scope=='PRIMARY_MATCHED_OVERALL'];oc=dict(zip(ov.matched_channel,ov.n));vv=[int(oc['NO_CS_BOTH']),int(oc['NO_DISEASE_CS']),int(oc['NO_QTL_CS']),int(perf.pair_evaluable.sum())];bars(d,['Both\nno CS','Disease\nno CS','QTL\nno CS','Pair\nevaluable'],vv,[cols[0],cols[1],GREY,BLUE],220000,',.0f');d.set_ylabel('Iterations (total 486,000)');d.ticklabel_format(axis='y',style='sci',scilimits=(3,3));d.text(.5,.93,'33.08% pair-evaluable; 0 technical errors',transform=d.transAxes,ha='center',fontsize=6.5)
values['4']={'channels':oc,'pair_evaluable':vv[-1],'scenario_abf_h4':sc.abf_h4_rate.tolist(),'scenario_multisignal_h4':sc.matched_h4_rate.tolist()};save(fig,4,'Simulation separates discovery from shared-signal decisions')
for l,j,s in [('a','Outcome partition not all-uninformative','S7/S7_channel_summary.tsv'),('b','Do not mix conditional/unconditional rates','S7/S7_discovery_vs_estimator.tsv'),('c','Balanced truth-known benefit and cost','S7/S7_scenario_summary.tsv'),('d','End-to-end discovery adequacy','S7/S7_channel_summary.tsv')]:sources(4,l,j,s)

# Figure 5: external disease support and explicitly noncausal association edges.
fg=frames['data/R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv'];tri=objs['data/R7C0_IL12RB2_chromatin_triangle_adjudication.json'];cs=frames['data/R7C0_OneK_NK_IL12RB2_CS_in_FinnGenR13_disease_CS.tsv'];cov=frames['data/R7C0_CASCADE_27gene_coverage.tsv'];fgstate=objs['data/R7C0_FinnGenR13_x_OneK_IL12RB2_external_coloc_state.json'];fig,axs=layout('IL12RB2 receives bounded external disease and chromatin support');a,b,c,d=axs
panel(a,'a','FinnGen R13 × OneK NK/IL12RB2');xx=np.arange(3);hh=[float(fgstate['low_prior_PP_H4']),float(fgstate['default_PP_H4']),float(fg.loc[fg.p12==1e-4,'PP_H4'].iloc[0])];bars(a,[r'$10^{-6}$',r'$10^{-5}$',r'$10^{-4}$'],hh,[BLUE,TEAL,PURPLE],1.13,'.4f');a.set(xlabel='Shared-association prior p12',ylabel='Single-causal PP.H4');a.axhline(.8,color=ORANGE,ls='--',lw=.8)
panel(b,'b','Source credible-set membership');b.axis('off');b.text(.5,.83,'2/2 OneK QTL CS variants\noccur in the 17-member FinnGen R13 disease CS',ha='center',fontsize=8,fontweight='bold')
for y,(_,rr) in zip([.51,.31],cs.iterrows()):b.text(.04,y,rr.SNP,fontsize=7.5);b.text(.47,y,f'PIP {rr.PIP:.3f}',fontsize=7.5);b.text(.99,y,'Included',ha='right',fontsize=7.5,color=TEAL)
b.text(.5,.09,'CS membership supports signal compatibility,\nnot a unique causal variant or mediation.',ha='center',fontsize=7)
panel(c,'c','Fixed CASCADE query defines coverage');summ=objs['data/R7C0_CASCADE_27gene_coverage_summary.json'];(Q/'CASCADE_SUMMARY_SCHEMA.json').write_text(json.dumps(summ,indent=2),encoding='utf-8')
# Counts independently audited in the source summary and exact 27-row inventory.
assert len(cov)==27
cov_counts=[int(summ['prespecified_genes']),int(summ['genes_with_relevant_broad_cell_eqtl_q_lt_0_05']),int(summ['fixed_genes_with_PBC_eQTL_coloc_records'])];assert cov_counts==[27,22,1]
bars(c,['Fixed\ngenes','eQTL\ncovered','PBC coloc\nreturned'],cov_counts,[GREY,TEAL,BLUE],33,'.0f');c.set_ylabel('Genes')
panel(d,'d','Observed edges do not establish mediation');d.axis('off')
coords={'Disease':(.16,.79),'eQTL':(.81,.79),'caQTL':(.16,.25),'Gene link':(.81,.25)}
for label,(x,y) in coords.items():d.text(x,y,label,ha='center',va='center',fontsize=8,fontweight='bold',bbox={'boxstyle':'round,pad=.4','facecolor':'#F0F4F7','edgecolor':GREY})
for p1,p2,lab in [('Disease','eQTL','H4 = 0.9703'),('Disease','caQTL','H4 = 0.9695'),('caQTL','Gene link','Link β = 0.141')]:
 x1,y1=coords[p1];x2,y2=coords[p2];d.plot([x1,x2],[y1,y2],color=BLUE,lw=1.2,zorder=0)
 if p1=='Disease' and p2=='caQTL':d.text(.05,.51,lab,rotation=90,fontsize=6.5,ha='center',va='center')
 else:d.text((x1+x2)/2,(y1+y2)/2+.075,lab,ha='center',fontsize=6.5)
d.plot([.81,.16],[.73,.32],color=ORANGE,ls='--',lw=1);d.text(.55,.54,'Direct eQTL–caQTL\nposterior unavailable',ha='center',fontsize=6.5,color=ORANGE,bbox={'facecolor':'white','edgecolor':'none','pad':1.5});d.set(xlim=(-.01,1.01),ylim=(0,1));d.text(.5,.03,'Links have no causal direction',ha='center',fontsize=6.5)
values['5']={'fg_h4':hh,'source_cs':cs[['SNP','PIP','in_finngen_r13_disease_cs']].to_dict('records'),'coverage':[27,22,1],'triangle':tri};save(fig,5,'IL12RB2 receives bounded external disease and chromatin support')
for l,j,s in [('a','Separate disease study single-causal support','data/R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv'),('b','CS identity instead of regional gene label','data/R7C0_OneK_NK_IL12RB2_CS_in_FinnGenR13_disease_CS.tsv'),('c','Source availability denominator','data/R7C0_CASCADE_27gene_coverage.tsv'),('d','Association edges without causal arrowheads','data/R7C0_IL12RB2_chromatin_triangle_adjudication.json')]:sources(5,l,j,s)

# Figure 6: every donor visible; effects and exact inferential status visible.
don=frames['S9/S9_donor_target_panel.tsv'];sm=frames['S9/S9_exact_5vs5_tissue.tsv'];fig,axs=plt.subplots(1,2,figsize=(7.05,3.45));fig.suptitle('Liver detectability does not establish disease enrichment',fontsize=11,fontweight='bold',y=.98);fig.subplots_adjust(left=.12,right=.98,bottom=.17,top=.78,wspace=.42)
for i,axis in enumerate(['FCRL3_B','IL12RB2_NK']):
 ax=axs[i];dd=don[don.target_lineage==axis];row=one(sm,sm.axis==axis);panel(ax,chr(97+i),'FCRL3 in B-lineage cells' if i==0 else 'IL12RB2 in NK-lineage cells')
 for j,g in enumerate(['Control','PBC']):
  group_mask=(dd.group=='PBC') if g=='PBC' else (dd.group!='PBC')
  y=np.sort(np.log1p(dd.loc[group_mask,'target_lineage_CPM'].to_numpy()));assert len(y)==5;ax.boxplot([y],positions=[j],widths=.36,showfliers=False,patch_artist=True,boxprops={'facecolor':'white','edgecolor':GREY},medianprops={'color':DARK},whiskerprops={'color':GREY},capprops={'color':GREY});ax.scatter(j+np.linspace(-.12,.12,5),y,s=22,color=BLUE if j==0 else ORANGE,zorder=5)
 ax.set(xticks=[0,1],xticklabels=['Control (5)','PBC (5)'],ylabel='log1p target-lineage CPM');low,high=ax.get_ylim();ax.set_ylim(low,high+(high-low)*.15);ax.text(.5,.98,f'Δ = {row.mean_log1p_CPM_difference_PBC_minus_control:+.3f}; P = {row.exact_label_permutation_p:.4f}; q = {row.BH_q_two_prespecified_targets:.4f}',transform=ax.transAxes,ha='center',va='top',fontsize=7)
fig.text(.5,.025,'Each point is one donor. Both targets detected in 5/5 donors per group; controls are non-lesion surgical liver.',ha='center',fontsize=7)
values['6']={'donors':20,'summary':sm.to_dict('records')};save(fig,6,'Liver detectability does not establish disease enrichment')
sources(6,'a','Boundary-changing donor-level null','S9/S9_donor_target_panel.tsv + S9/S9_exact_5vs5_tissue.tsv');sources(6,'b','Different endpoint from a genotype eQTL','S9/S9_donor_target_panel.tsv + S9/S9_exact_5vs5_tissue.tsv')

# Exhaustive supporting displays retain material details outside the main story.
fig,axs=layout('Complete adjacent-arm transitions in the frozen 642');a,b,c,d=axs
for ax,letter,aa,bb,title in [(a,'a','A0_simple_state','A1_simple_state','A0 to A1: support restriction'),(b,'b','A1_simple_state','A2_simple_state','A1 to A2: disease-statistic definition'),(c,'c','A2_simple_state','M_simple_state','A2 to M: complete procedure contrast')]:
 panel(ax,letter,title);ct=pd.crosstab(T[aa],T[bb]);ax.imshow(ct,cmap='Blues',aspect='auto',vmin=0,vmax=455)
 for i in range(len(ct)):
  for j in range(len(ct.columns)):ax.text(j,i,str(ct.iloc[i,j]),ha='center',va='center',fontsize=7,color='white' if ct.iloc[i,j]>230 else DARK)
 labels=lambda x:[v.replace('UNINFORMATIVE','Uninform.').replace('MODEL_SENSITIVE','Sensitive').replace('AMBIGUOUS','Ambig.').replace('H4_BORDERLINE','Borderline') for v in x]
 ax.set(xticks=range(len(ct.columns)),xticklabels=labels(ct.columns),yticks=range(len(ct.index)),yticklabels=labels(ct.index),xlabel='To state',ylabel='From state');ax.tick_params(axis='x',labelrotation=30,labelsize=6)
panel(d,'d','Audit units retain distinct identities');d.axis('off');d.text(.01,.9,'14 targeted comparison-model identity rows\n= 7 comparisons × 2 factor models\n\n2,568 SuSiE fit rows\n= 642 comparisons × 4 configurations\n\n2,568 kriging diagnostic units\n= 642 comparisons × 2 models × 2 traits\n\nEqual counts do not imply equal objects.\nOne reviewed kriging variant was outside CSs.',fontsize=7.5,va='top',linespacing=1.6)
values['S1']={'n':642,'fit_rows':len(frames['S5/S5_2568_PF10_PF50_SuSiE_fit_QC.tsv.gz'])};save(fig,'S1','Complete adjacent-arm transitions in the frozen 642')
for l,j in [('a','Full support-matching transition'),('b','Full statistic transition'),('c','Full procedure transition'),('d','Disambiguate equal diagnostic counts')]:sources('S1',l,j,'S3/S3_642_A0_A1_A2_M_trajectories.tsv; S5; frozen diagnostic audit')

fac=frames['S7/S7_factor_stratified_summary.tsv'];(Q/'SIMULATION_FACTOR_SCHEMA.json').write_text(json.dumps({'columns':list(fac.columns),'first_rows':fac.head(3).to_dict('records')},indent=2),encoding='utf-8')
fig,axs=plt.subplots(2,3,figsize=(7.05,5.3));fig.suptitle('Decision rates depend on LD architecture',fontsize=11,fontweight='bold',y=.98);fig.subplots_adjust(left=.10,right=.97,bottom=.12,top=.84,wspace=.43,hspace=.64)
ldvals=[]
for i,(ax,scenario) in enumerate(zip(axs.flat,sc.scenario)):
 panel(ax,chr(97+i),f'S{i+1}: '+('shared signal present' if bool(sc.iloc[i].true_shared) else 'no shared signal'))
 dd=fac[fac.scenario==scenario];tab=[]
 for rr,group in dd.groupby('causal_r2'):
  vals={k:float(np.average(group[k],weights=group.replicates)) for k in ['abf_h4_rate','matched_h4_rate']};vals.update(scenario=scenario,causal_r2=float(rr));tab.append(vals);ldvals.append(vals)
 ax.plot([v['causal_r2'] for v in tab],[v['abf_h4_rate'] for v in tab],'o-',color=GREY,markersize=3,label='ABF');ax.plot([v['causal_r2'] for v in tab],[v['matched_h4_rate'] for v in tab],'o-',color=TEAL,markersize=3,label='Multi-signal');ax.set(ylim=(0,.8),xticks=[.2,.5,.8],xlabel='Target causal-pair r²',ylabel='H4 decision rate')
 if i==0:ax.legend(frameon=False,fontsize=6)
values['S2']={'rates':ldvals};save(fig,'S2','Decision rates depend on LD architecture')
for i in range(6):sources('S2',chr(97+i),'Grid-weighted LD dependence within frozen scenario','S7/S7_factor_stratified_summary.tsv')
csrel=frames['data/R7C0_FinnGen_R12_R13_IL12RB2_CS_members.tsv'];(Q/'FINNGEN_RELEASE_CS_SCHEMA.json').write_text(json.dumps({'columns':list(csrel.columns),'first_rows':csrel.head(3).to_dict('records')},indent=2),encoding='utf-8')
fig,axs=plt.subplots(1,2,figsize=(7.05,3.5));fig.suptitle('FinnGen release stability is not a new independent cohort',fontsize=10.5,fontweight='bold',y=.98);fig.subplots_adjust(left=.12,right=.97,bottom=.18,top=.77,wspace=.45)
a,b=axs;panel(a,'a','Shared-CS probability by release');x=csrel.cs_specific_prob_R12;y=csrel.cs_specific_prob_R13;assert len(csrel)==17 and x.notna().all() and y.notna().all();a.scatter(x,y,s=17,color=BLUE);maxp=max(x.max(),y.max())*1.08;a.plot([0,maxp],[0,maxp],ls='--',color=GREY,lw=.8);a.set(xlabel='R12 CS probability',ylabel='R13 CS probability',xlim=(0,maxp),ylim=(0,maxp));panel(b,'b','Membership across sequential releases');identity=objs['data/R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json'];sizes=[identity['r12_cs_size'],identity['r13_cs_size']];assert sizes==[19,17] and identity['intersection_size']==len(csrel);bars(b,['R12','R13'],sizes,[BLUE,TEAL],24,'.0f');b.set_ylabel('Disease-CS variants');b.text(.5,.4,'17/17 R13 members retained in R12\nJaccard = 17/19 = 0.895',transform=b.transAxes,ha='center',fontsize=7)
values['S3']={'sizes':sizes,'members':csrel.v.tolist()};save(fig,'S3','FinnGen release stability is not a new independent cohort')
sources('S3','a','Release probability concordance among 17 shared members only','data/R7C0_FinnGen_R12_R13_IL12RB2_CS_members.tsv');sources('S3','b','Full source CS sizes distinct from intersection table','data/R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json')
(Q/'FIGURE_VALUES.json').write_text(json.dumps(values,ensure_ascii=False,indent=2),encoding='utf-8')
with (Q/'PANEL_EVIDENCE_MAP.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=panel_rows[0].keys(),delimiter='\t');w.writeheader();w.writerows(panel_rows)
(Q/'FIGURE_SOURCE_MEMBER_HASHES.json').write_text(json.dumps(src,ensure_ascii=False,indent=2),encoding='utf-8')
print('BUILT_SIX_SOURCE_BOUND_FIGURES',len(panel_rows),'panels')
