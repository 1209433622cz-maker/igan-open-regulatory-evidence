from __future__ import annotations
import os,json,re
from pathlib import Path
import pandas as pd, numpy as np
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
OUT=ROOT/"3_results/04_integration/R6A3A"
CS=pd.read_csv(ROOT/"1_data/qtl/eQTLCatalogue/Sun_2018_QTD000584/QTD000584.credible_sets.tsv.gz",sep="\t",dtype=str)
R=pd.read_csv(OUT/"R6A3A_pqtl_signal_coloc.tsv",sep="\t")
# Source component must correspond to an actual SuSiE credible set.
cskeys=set()
if {"molecular_trait_id","cs_id"}.issubset(CS.columns):
    for r in CS.itertuples(index=False):
        m=re.search(r"_L(\d+)$",str(r.cs_id))
        if m: cskeys.add((str(r.molecular_trait_id),f"L{m.group(1)}"))

rows=[]
for key,g in R.groupby(["locus","gene_symbol","molecular_trait_id","idx2"]):
    loc,gene,mt,idx2=key
    comp=f"L{int(idx2)}"
    d=g[np.isclose(pd.to_numeric(g.p12),1e-5)]
    lo=g[np.isclose(pd.to_numeric(g.p12),1e-6)]
    hi=g[np.isclose(pd.to_numeric(g.p12),1e-4)]
    if d.empty or lo.empty: continue
    d=d.sort_values("PP.H4.abf",ascending=False).iloc[0]
    lo=lo.sort_values("PP.H4.abf",ascending=False).iloc[0]
    has_cs=(str(mt),str(comp)) in cskeys
    robust=(has_cs and d["PP.H4.abf"]>=0.80 and d["H4_over_H3H4"]>=0.80 and lo["H4_over_H3H4"]>=0.50)
    rows.append({"locus":loc,"gene_symbol":gene,"molecular_trait_id":mt,"component":comp,
                 "component_top_variant":str(d["hit2"]),
                 "source_credible_set_present":has_cs,"PP_H4_default":d["PP.H4.abf"],
                 "H4_ratio_default":d["H4_over_H3H4"],"H4_ratio_low_p12":lo["H4_over_H3H4"],
                 "classification":"PASS_PQTL_SHARED_SIGNAL" if robust else "NOT_PASS"})
A=pd.DataFrame(rows)
A.to_csv(OUT/"R6A3A_pqtl_component_adjudication.tsv",sep="\t",index=False)
loci=[]
for loc,g in A.groupby("locus"):
    pg=g[g.classification=="PASS_PQTL_SHARED_SIGNAL"]
    loci.append({"locus":loc,"status":"PASS" if len(pg) else "NO_PASS","n_pass_components":len(pg),
                 "pass_genes":";".join(sorted(set(pg.gene_symbol))) if len(pg) else ""})
L=pd.DataFrame(loci)
L.to_csv(OUT/"R6A3A_pqtl_locus_adjudication.tsv",sep="\t",index=False)
state={"track":"A_pQTL","pass_loci":int((L.status=="PASS").sum()) if len(L) else 0,
       "pass_locus_names":L.loc[L.status=="PASS","locus"].tolist() if len(L) else [],
       "status":"PASS" if len(L) and (L.status=="PASS").any() else "FAIL_NO_ADDITIONAL_SHARED_SIGNAL"}
(OUT/"R6A3A_pqtl_track_state.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
