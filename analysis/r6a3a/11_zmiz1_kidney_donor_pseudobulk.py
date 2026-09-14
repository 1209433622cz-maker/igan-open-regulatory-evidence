from __future__ import annotations
import os,gzip,json,itertools,math
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import ttest_ind, mannwhitneyu

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
DATA=ROOT/"1_data/scrna/IgAN/GSE127136"
OUT=ROOT/"3_results/05_tissue/R6A3A"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A3A"; AUD.mkdir(parents=True,exist_ok=True)

def parse_soft(path):
    rows=[]; cur=None
    with gzip.open(path,"rt",encoding="utf-8",errors="replace") as h:
        for line in h:
            line=line.rstrip()
            if line.startswith("^SAMPLE = "):
                if cur: rows.append(cur)
                cur={"accession":line.split(" = ",1)[1]}
            elif cur is not None and line.startswith("!Sample_title = "):
                cur["title"]=line.split(" = ",1)[1]
            elif cur is not None and line.startswith("!Sample_characteristics_ch1 = "):
                v=line.split(" = ",1)[1]
                if ": " in v:
                    k,val=v.split(": ",1); cur[k.strip().lower().replace(" ","_")]=val.strip()
        if cur: rows.append(cur)
    return pd.DataFrame(rows)

meta=parse_soft(DATA/"GSE127136_family.soft.gz")
if "patients" not in meta or "disease_state" not in meta:
    raise RuntimeError(f"Expected patients/disease_state in SOFT characteristics; columns={list(meta.columns)}")
meta["compartment"]=np.where(meta.patients.astype(str).str.startswith("PBM_"),"peripheral_CD14_monocytes","kidney")
counts=DATA/"GSE127136_project_IgA_nephropathy_counts.csv.gz"
with gzip.open(counts,"rt",encoding="utf-8") as h:
    header=h.readline().rstrip().split(","); cells=header[1:]
    lib=np.zeros(len(cells),dtype=np.float64); z=np.zeros(len(cells),dtype=np.float64); zrows=0
    for line in h:
        gene,vals=line.rstrip().split(",",1)
        x=np.fromstring(vals,dtype=np.float64,sep=",")
        if len(x)!=len(cells): raise RuntimeError(f"width mismatch {gene}")
        lib += x
        if gene=="ZMIZ1": z += x; zrows += 1
if zrows!=1: raise RuntimeError(f"Expected exactly one ZMIZ1 row, observed {zrows}")
if set(cells)!=set(meta.title.astype(str)): raise RuntimeError("matrix/SOFT cell-title set mismatch")
idx=meta.set_index("title").loc[cells].reset_index()
idx["library"]=lib; idx["ZMIZ1"]=z
kid=idx[idx.compartment=="kidney"].copy()
# Preserve source disease labels, but only IgAN vs paracancer-control are inferential groups.
kid["analysis_group"]=np.where(kid.disease_state.astype(str).str.contains("IgAN",case=False,na=False),"IgAN","paracancer_control")
if set(kid.analysis_group)!={"IgAN","paracancer_control"}: raise RuntimeError("Could not resolve two kidney groups")
don=kid.groupby(["patients","analysis_group"],as_index=False).agg(cells=("title","size"),library=("library","sum"),ZMIZ1_counts=("ZMIZ1","sum"))
don["ZMIZ1_CPM"]=(don.ZMIZ1_counts+0.5)/(don.library+1.0)*1e6
don["ZMIZ1_log2CPM"]=np.log2(don.ZMIZ1_CPM+1)
a=don.loc[don.analysis_group=="IgAN","ZMIZ1_log2CPM"].to_numpy()
b=don.loc[don.analysis_group=="paracancer_control","ZMIZ1_log2CPM"].to_numpy()
if (len(a),len(b))!=(13,6): raise RuntimeError(f"Unexpected kidney donors cases/controls = {len(a)}/{len(b)}")
obs=float(a.mean()-b.mean())

# exact label permutation for 19 donors choose 13 cases = 27,132 assignments
v=don.ZMIZ1_log2CPM.to_numpy(); ncase=len(a); diffs=[]
for comb in itertools.combinations(range(len(v)),ncase):
    mask=np.zeros(len(v),dtype=bool); mask[list(comb)]=True
    diffs.append(v[mask].mean()-v[~mask].mean())
diffs=np.asarray(diffs)
p_exact=float((np.abs(diffs)>=abs(obs)-1e-15).mean())

rng=np.random.default_rng(20260914)
boot=np.empty(10000)
for i in range(len(boot)):
    aa=rng.choice(a,len(a),replace=True); bb=rng.choice(b,len(b),replace=True)
    boot[i]=aa.mean()-bb.mean()
ci=np.quantile(boot,[0.025,0.975])
tt=ttest_ind(a,b,equal_var=False)
mw=mannwhitneyu(a,b,alternative="two-sided")
detect_frac=float((don.ZMIZ1_counts>0).mean())
direction="CASE_LOWER" if obs<0 else "CASE_HIGHER" if obs>0 else "NO_SHIFT"
if detect_frac>=0.80 and p_exact<0.05 and obs<0:
    status="PASS_SUPPORTIVE_CASE_LOWER"
elif detect_frac>=0.80:
    status="INTERPRETABLE_DONOR_LEVEL"
else:
    status="FAIL_LOW_DETECTION"
summary={"cases":len(a),"paracancer_controls":len(b),"donor_detection_fraction":detect_frac,
         "mean_log2CPM_difference_case_minus_control":obs,"bootstrap95CI":[float(ci[0]),float(ci[1])],
         "exact_permutation_p":p_exact,"welch_p":float(tt.pvalue),"mannwhitney_p":float(mw.pvalue),
         "direction":direction,"status":status,
         "interpretation_boundary":"aggregate kidney pseudobulk; cell-composition sensitive; paracancer controls are not healthy kidney"}
don.to_csv(OUT/"R6A3A_ZMIZ1_kidney_donor_pseudobulk.tsv",sep="\t",index=False)
(AUD/"R6A3A_ZMIZ1_kidney_primary_gate.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
