#!/usr/bin/env python3
from __future__ import annotations
import csv,io,json,os,re,zipfile
from pathlib import Path
import pandas as pd, numpy as np

HERE=Path(__file__).resolve()
DEFAULT_ROOT=HERE.parents[2] if (HERE.parents[2]/".git").exists() else HERE.parents[3]
ROOT=Path(os.environ.get("R7_PROJECT_ROOT",DEFAULT_ROOT))
CODE=ROOT/"2_code/06_intake/r7a1a"
OUT=ROOT/"3_results/03_qtl/R7A1A"; OUT.mkdir(parents=True,exist_ok=True)
controls=pd.read_csv(CODE/"R7A1A_frozen_positive_controls.tsv",sep="\t")
targets=set(controls.gene.astype(str))
# OneK1K used an older annotation in which INAVA is named C1orf106.
# Canonicalize the source symbol without changing the frozen control list.
ALIAS_TO_CANON={"C1orf106":"INAVA","C1ORF106":"INAVA"}
def first_existing(*paths):
    for p in paths:
        if p.exists(): return p
    raise FileNotFoundError("No input found among: "+", ".join(map(str,paths)))

# Gene symbol -> Ensembl (GRCh38)
gtf=ROOT/"1_data/reference/gene_annotation/gencode.v50.annotation.gtf.gz"
import gzip
sym2ens={}
pat=re.compile(r'gene_id "([^"]+)".*gene_name "([^"]+)"')
with gzip.open(gtf,"rt",encoding="utf-8",errors="replace") as h:
    for line in h:
        if line.startswith("#") or "\tgene\t" not in line: continue
        m=pat.search(line)
        if m and m.group(2) in targets:
            sym2ens[m.group(2)]=m.group(1).split(".")[0]
if set(sym2ens)!=targets:
    raise RuntimeError(f"GENCODE mapping incomplete: {sorted(targets-set(sym2ens))}")
ens2sym={v:k for k,v in sym2ens.items()}

# OneK top-eQTL
onek=ROOT/"1_data/qtl/OneK1K/OneK1K_TensorQTL_top_eQTL_summary.zip"
one_rows=[]
with zipfile.ZipFile(onek) as z:
    if z.testzip() is not None: raise RuntimeError("OneK zip CRC fail")
    for member in z.namelist():
        if not member.endswith(".csv") or member.startswith("__MACOSX"): continue
        m=re.search(r"OneK1K_(.+?)\.sig_cis_qtl_pairs\.chr",Path(member).name)
        if not m: continue
        cell=m.group(1)
        with z.open(member) as raw, io.TextIOWrapper(raw,encoding="utf-8-sig") as txt:
            for r in csv.DictReader(txt,delimiter="\t"):
                source_gene=str(r["phenotype_id"])
                gene=ALIAS_TO_CANON.get(source_gene,source_gene)
                if gene not in targets: continue
                q=float(r["qval"])
                one_rows.append({"gene":gene,"source_gene_symbol":source_gene,"cell":cell,"variant":r["variant_id"],"p":float(r["pval_nominal"]),"q":q,
                                 "source_significant":q<0.05,"slope":float(r["slope"]),"slope_se":float(r["slope_se"])})
ONE=pd.DataFrame(one_rows)
ONE.to_csv(OUT/"R7A1A_OneK_frozen_control_screen.tsv",sep="\t",index=False)

# TenK gene-level: compute BH within each cell over numeric gene rows.
tenk=first_existing(
    ROOT/"1_data/qtl/TenK10K/common_variant_gene_level_results_with_annotated_fails.zip",
    ROOT/"1_data/qtl/eqtl/tenk10k/raw/common_variant_gene_level_results_with_annotated_fails.zip")
ten_rows=[]
def bh(p):
    p=np.asarray(p,float); n=len(p); order=np.argsort(p); out=np.empty(n); run=1.0
    for j in range(n-1,-1,-1):
        idx=order[j]; run=min(run,p[idx]*n/(j+1)); out[idx]=min(run,1.0)
    return out
with zipfile.ZipFile(tenk) as z:
    if z.testzip() is not None: raise RuntimeError("TenK gene zip CRC fail")
    for member in z.namelist():
        if not member.endswith(".tsv"): continue
        cell=Path(member).name.split("_all_cis",1)[0]
        parsed=[]
        with z.open(member) as raw,io.TextIOWrapper(raw,encoding="utf-8-sig") as txt:
            rdr=csv.DictReader(txt)
            for r in rdr:
                try: p=float(r["ACAT_p"])
                except: continue
                parsed.append((r,p))
        qs=bh([x[1] for x in parsed])
        for (r,p),q in zip(parsed,qs):
            ens=str(r["gene"]).split(".")[0]
            if ens not in ens2sym: continue
            ten_rows.append({"gene":ens2sym[ens],"gene_ensembl":ens,"cell":cell,"ACAT_p":p,"BH_q":float(q),
                             "source_significant":float(q)<0.05,"top_variant":r.get("top_MarkerID",""),"top_p":r.get("top_pval","")})
TEN=pd.DataFrame(ten_rows)
TEN.to_csv(OUT/"R7A1A_TenK_genelevel_frozen_control_screen.tsv",sep="\t",index=False)

# TenK source SuSiE
sus=first_existing(ROOT/"1_data/qtl/TenK10K/susie_summary.zip",
                   ROOT/"1_data/qtl/eqtl/tenk10k/raw/susie_summary.zip")
cs=[]
with zipfile.ZipFile(sus) as z:
    if z.testzip() is not None: raise RuntimeError("TenK SuSiE zip CRC fail")
    for member in z.namelist():
        if not member.endswith(".tsv"): continue
        with z.open(member) as raw,io.TextIOWrapper(raw,encoding="utf-8-sig") as txt:
            for r in csv.DictReader(txt):
                ens=str(r["gene"]).split(".")[0]
                if ens not in ens2sym: continue
                cs.append({"gene":ens2sym[ens],"gene_ensembl":ens,"cell":r["celltype"],
                           "credible_set":r["Credible_Set"],"variant":r["SNP"],"PIP":float(r["PIP"])})
CS=pd.DataFrame(cs)
CS.to_csv(OUT/"R7A1A_TenK_SuSiE_frozen_control_screen.tsv",sep="\t",index=False)

summary=[]
for r in controls.itertuples(index=False):
    o=ONE[ONE.gene==r.gene] if len(ONE) else pd.DataFrame()
    t=TEN[TEN.gene==r.gene] if len(TEN) else pd.DataFrame()
    c=CS[CS.gene==r.gene] if len(CS) else pd.DataFrame()
    ocells=sorted(o.loc[o.source_significant,"cell"].unique()) if len(o) else []
    tcells=sorted(t.loc[t.source_significant,"cell"].unique()) if len(t) else []
    ccells=sorted(c.cell.unique()) if len(c) else []
    byte_testable=bool(len(o)>0 and len(t)>0)
    source_positive=bool(ocells and (tcells or ccells))
    summary.append({
      "candidate":r.candidate,"gene":r.gene,"cytoband":r.cytoband,
      "OneK_observed_cells":int(o.cell.nunique()) if len(o) else 0,
      "OneK_source_sig_cells":len(ocells),"OneK_cells":";".join(ocells),
      "TenK_observed_cells":int(t.cell.nunique()) if len(t) else 0,
      "TenK_source_sig_cells":len(tcells),"TenK_cells":";".join(tcells),
      "TenK_SuSiE_cells":len(ccells),"TenK_SuSiE_cell_names":";".join(ccells),
      "cross_resource_byte_testable":byte_testable,
      "cross_resource_source_positive":source_positive
    })
S=pd.DataFrame(summary)
S.to_csv(OUT/"R7A1A_frozen_control_cross_resource_testability.tsv",sep="\t",index=False)
state={}
for cand,g in S.groupby("candidate"):
    state[cand]={
      "controls":len(g),
      "cross_resource_byte_testable":int(g.cross_resource_byte_testable.sum()),
      "OneK_source_supported":int((g.OneK_source_sig_cells>0).sum()),
      "TenK_source_or_CS_supported":int(((g.TenK_source_sig_cells>0)|(g.TenK_SuSiE_cells>0)).sum()),
      "cross_resource_source_positive":int(g.cross_resource_source_positive.sum()),
      "gate_3_controls_byte_testable":"PASS" if int(g.cross_resource_byte_testable.sum())>=3 else "FAIL",
      "strict_positive_gate_3_of_3":"PASS" if int(g.cross_resource_source_positive.sum())>=3 else "FAIL"
    }
(OUT/"R7A1A_QTL_control_testability_state.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
