#!/usr/bin/env python3
"""Exact REF/ALT harmonization for one TenK10K IL12RB2 cell and FinnGen SSc."""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import pandas as pd

GENE="ENSG00000081985"

def sha(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(chrom,pos,ref,alt):
    chrom=str(chrom).removeprefix("chr").upper(); pos=int(pos); ref=str(ref).upper(); alt=str(alt).upper()
    while len(ref)>1 and len(alt)>1 and ref[-1]==alt[-1]: ref=ref[:-1]; alt=alt[:-1]
    while len(ref)>1 and len(alt)>1 and ref[0]==alt[0]: ref=ref[1:]; alt=alt[1:]; pos+=1
    return f"{chrom}:{pos}:{ref}:{alt}"

def main():
    p=argparse.ArgumentParser(); p.add_argument("--qtl",type=Path,required=True); p.add_argument("--gwas",type=Path,required=True)
    p.add_argument("--source-cs",type=Path,required=True); p.add_argument("--cell",required=True); p.add_argument("--release",required=True)
    p.add_argument("--out-tsv",type=Path,required=True); p.add_argument("--out-json",type=Path,required=True); a=p.parse_args()
    q=pd.read_csv(a.qtl,sep="\t",dtype=str); g=pd.read_csv(a.gwas,sep="\t",dtype=str); cs=pd.read_csv(a.source_cs,sep="\t",dtype=str)
    qr={"CHR","POS","MarkerID","Allele1","Allele2","AF_Allele2","BETA","SE","p.value","N","gene"}
    gr={"#chrom","pos","ref","alt","rsids","pval","beta","sebeta","af_alt"}
    if not qr.issubset(q.columns) or not gr.issubset(g.columns): raise RuntimeError("required input fields absent")
    if set(q.gene)!={GENE}: raise RuntimeError("QTL extract contains non-target gene")
    q["variant_key"]=[canon(*x) for x in zip(q.CHR,q.POS,q.Allele1,q.Allele2)]
    marker_key=[canon(*str(x).split(":")) for x in q.MarkerID]
    if marker_key!=q.variant_key.tolist(): raise RuntimeError("MarkerID and allele fields disagree")
    g["variant_key"]=[canon(*x) for x in zip(g["#chrom"],g.pos,g.ref,g.alt)]
    if q.variant_key.duplicated().any() or g.variant_key.duplicated().any(): raise RuntimeError("duplicate canonical variant key")
    qnum={"BETA":"qtl_beta","SE":"qtl_se","p.value":"qtl_p","AF_Allele2":"qtl_af_alt","N":"qtl_n"}
    gnum={"beta":"gwas_beta","sebeta":"gwas_se","pval":"gwas_p","af_alt":"gwas_af_alt"}
    for old,new in qnum.items(): q[new]=pd.to_numeric(q[old],errors="raise")
    for old,new in gnum.items(): g[new]=pd.to_numeric(g[old],errors="raise")
    q["qtl_marker"]=q.MarkerID; q["chrom"]=q.CHR.str.removeprefix("chr"); q["pos_out"]=q.POS.astype(int); q["ref_out"]=q.Allele1.str.upper(); q["alt_out"]=q.Allele2.str.upper()
    g["gwas_rsids"]=g.rsids; g["gwas_source_line"]=range(2,len(g)+2)
    out=q[["variant_key","chrom","pos_out","ref_out","alt_out","qtl_marker",*qnum.values(),"source_line"]].merge(
        g[["variant_key",*gnum.values(),"gwas_rsids","gwas_source_line"]],on="variant_key",how="inner",validate="one_to_one")
    out=out.rename(columns={"pos_out":"pos","ref_out":"ref","alt_out":"alt","source_line":"qtl_source_line"})
    cs=cs[(cs.gene==GENE)&(cs.celltype==a.cell)].copy(); cs["PIP"]=pd.to_numeric(cs.PIP)
    cmap={}
    for key,x in cs.groupby("SNP"):
        cmap[key]={"source_cs":",".join(sorted(set(x.Credible_Set))),"source_cs_pip":float(x.PIP.sum())}
    out["release"]=a.release; out["celltype"]=a.cell; out["alignment"]="EXACT_REF_ALT"
    out["qtl_z"]=out.qtl_beta/out.qtl_se; out["gwas_z"]=out.gwas_beta/out.gwas_se
    out["af_abs_diff"]=(out.qtl_af_alt-out.gwas_af_alt).abs(); out["source_cs"]=out.variant_key.map(lambda x:cmap.get(x,{}).get("source_cs","")); out["source_cs_pip"]=out.variant_key.map(lambda x:cmap.get(x,{}).get("source_cs_pip",0.0))
    order=["release","celltype","variant_key","chrom","pos","ref","alt","alignment","qtl_marker","qtl_beta","qtl_se","qtl_p","qtl_af_alt","qtl_n","qtl_source_line","gwas_beta","gwas_se","gwas_p","gwas_af_alt","gwas_rsids","gwas_source_line","qtl_z","gwas_z","af_abs_diff","source_cs","source_cs_pip"]
    out=out[order].sort_values(["pos","ref","alt"]); a.out_tsv.parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.out_tsv,sep="\t",index=False)
    reverse=sum(k not in set(g.variant_key) and canon(str(k).split(":")[0],str(k).split(":")[1],str(k).split(":")[3],str(k).split(":")[2]) in set(g.variant_key) for k in q.variant_key)
    covered=set(out.variant_key); csmetrics=[]
    for sig,x in cs.groupby("Credible_Set"):
        hit=x[x.SNP.isin(covered)]; total=float(x.PIP.sum()); got=float(hit.PIP.sum())
        csmetrics.append({"source_cs":str(sig),"members_total":len(x),"members_disease_exact":len(hit),"pip_total":total,"pip_disease_exact":got,"pip_mass_fraction":got/total if total else None})
    top=q.loc[q.qtl_p.idxmin()]; lead=g.loc[g.gwas_p.idxmin()]
    af=out.af_abs_diff
    checks={"qtl_rows_ge_100":len(q)>=100,"overlap_ge_100":len(out)>=100,"qtl_overlap_fraction_ge_0_80":len(out)/len(q)>=.8,
            "af_median_le_0_10":float(af.median())<=.10,"af_p95_le_0_20":float(af.quantile(.95))<=.20,
            "qtl_top_covered":top.variant_key in covered,"disease_lead_covered":lead.variant_key in covered,
            "each_source_cs_disease_pip_fraction_ge_0_95":all(x["pip_mass_fraction"]>=.95 for x in csmetrics)}
    result={"schema_version":"CMM_R4A12FG6_THREE_CELL_HARMONIZATION_1.0","release":a.release,"celltype":a.cell,
            "status":"PASS_EXACT_HARMONIZATION" if all(checks.values()) else "HOLD_EXACT_COVERAGE","checks":checks,
            "metrics":{"qtl_rows":len(q),"gwas_rows":len(g),"harmonized_rows":len(out),"qtl_overlap_fraction":len(out)/len(q),
            "reverse_allele_pairs_excluded":int(reverse),"af_median_abs_diff":float(af.median()),"af_p95_abs_diff":float(af.quantile(.95)),
            "qtl_top":{"variant_key":top.variant_key,"p":float(top.qtl_p),"covered":top.variant_key in covered},
            "disease_lead":{"variant_key":lead.variant_key,"rsids":lead.gwas_rsids,"p":float(lead.gwas_p),"covered":lead.variant_key in covered},"source_cs":csmetrics},
            "input_sha256":{"qtl":sha(a.qtl),"gwas":sha(a.gwas),"source_cs":sha(a.source_cs)},"output_sha256":sha(a.out_tsv)}
    a.out_json.parent.mkdir(parents=True,exist_ok=True); a.out_json.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
