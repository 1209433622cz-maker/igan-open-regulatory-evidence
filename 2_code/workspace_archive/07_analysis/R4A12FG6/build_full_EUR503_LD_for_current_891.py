#!/usr/bin/env python3
"""Build signed ALT-dosage LD for the current 891 exact-overlap variants.

The reader decodes the frozen PLINK1 BED directly, so no unrecorded PLINK
binary or allele-export convention is involved.  BED genotype values count BIM
A2; they are flipped when the current GRCh38 ALT equals BIM A1.  Cross-build
matching is rsID plus unordered allele identity.  Ambiguous/multi rsID rows and
duplicate rsIDs are retained in the mapping audit but never guessed.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path
import numpy as np
import pandas as pd

ANCHORS=("rs17129789","rs6662198","rs1954118")

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(4<<20),b""): h.update(b)
    return h.hexdigest()

def pearson(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float); good=np.isfinite(x)&np.isfinite(y)
    return float(np.corrcoef(x[good],y[good])[0,1]) if good.sum()>2 else None

def read_bed_selected(path: Path, n_samples: int, n_variants: int, indices: list[int]) -> dict[int,np.ndarray]:
    bytes_per=(n_samples+3)//4; expected=3+bytes_per*n_variants
    if path.stat().st_size!=expected: raise RuntimeError(f"BED bytes {path.stat().st_size} != {expected}")
    code=np.array([0.0,np.nan,1.0,2.0])  # two-bit 00=A1/A1, 10=het, 11=A2/A2; value counts A2
    out={}
    with path.open("rb") as f:
        if f.read(3)!=b"\x6c\x1b\x01": raise RuntimeError("PLINK BED magic/mode mismatch")
        for idx in indices:
            f.seek(3+idx*bytes_per); b=np.frombuffer(f.read(bytes_per),dtype=np.uint8)
            raw=np.empty(bytes_per*4,dtype=np.uint8)
            raw[0::4]=b&3; raw[1::4]=(b>>2)&3; raw[2::4]=(b>>4)&3; raw[3::4]=(b>>6)&3
            out[idx]=code[raw[:n_samples]]
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument("--harmonized",type=Path,required=True)
    p.add_argument("--bfile-prefix",type=Path,required=True); p.add_argument("--source-cs",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True); a=p.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(a.harmonized,sep="\t",dtype=str); required={"variant_key","ref","alt","gwas_rsids","gwas_z","qtl_z","gwas_af_alt","qtl_af_alt"}
    if not required.issubset(d.columns): raise RuntimeError(f"missing columns {sorted(required-set(d.columns))}")
    d["input_index"]=np.arange(len(d)); d["single_rsid"]=d.gwas_rsids.fillna("").str.fullmatch(r"rs\d+")
    d["valid_rsid_duplicate"]=d.loc[d.single_rsid,"gwas_rsids"].duplicated(False).reindex(d.index,fill_value=False)
    prefix=str(a.bfile_prefix); bim_path=Path(prefix+".bim"); bed_path=Path(prefix+".bed"); fam_path=Path(prefix+".fam")
    bim=pd.read_csv(bim_path,sep=r"\s+",header=None,names=["bim_chr","rsid","cm","bim_pos","a1","a2"],dtype=str)
    bim["bim_index"]=np.arange(len(bim)); bim["bim_rsid_duplicate"]=bim.rsid.duplicated(False)
    n_samples=sum(1 for _ in fam_path.open(encoding="utf-8")); valid=d[d.single_rsid & ~d.valid_rsid_duplicate].copy()
    mapped=valid.merge(bim[~bim.bim_rsid_duplicate],left_on="gwas_rsids",right_on="rsid",how="left",validate="one_to_one")
    mapped["allele_set_match"]=mapped.apply(lambda r: False if pd.isna(r.a1) else {r.ref.upper(),r.alt.upper()}=={r.a1.upper(),r.a2.upper()},axis=1)
    mapped["alt_is_bim_a2"]=mapped.apply(lambda r: bool(r.allele_set_match and r.alt.upper()==r.a2.upper()),axis=1)
    mapped["alt_is_bim_a1"]=mapped.apply(lambda r: bool(r.allele_set_match and r.alt.upper()==r.a1.upper()),axis=1)
    good=mapped[mapped.allele_set_match].sort_values("input_index").copy()
    dosage=read_bed_selected(bed_path,n_samples,len(bim),good.bim_index.astype(int).tolist())
    cols=[]; keep=[]
    for r in good.itertuples():
        x=dosage[int(r.bim_index)].copy()
        if r.alt_is_bim_a1: x=2-x
        missing=int(np.isnan(x).sum()); mean=float(np.nanmean(x))
        if not np.isfinite(mean) or float(np.nanstd(x))==0: continue
        x[np.isnan(x)]=mean; cols.append(x); keep.append((r,missing))
    if not cols: raise RuntimeError("no polymorphic allele-matched variants")
    G=np.column_stack(cols); R=np.corrcoef(G,rowvar=False)
    rows=pd.DataFrame([r._asdict() for r,_ in keep]); rows["missing_genotypes"]=[m for _,m in keep]
    rows["eur503_alt_af"]=G.mean(0)/2; rows["ld_order_index"]=np.arange(len(rows))
    rows.to_csv(a.out_dir/"EUR503_current891_retained_variants.tsv",sep="\t",index=False)
    np.save(a.out_dir/"EUR503_current891_ALT_dosage.npy",G); np.save(a.out_dir/"EUR503_current891_signed_r.npy",R)
    np.savetxt(a.out_dir/"EUR503_current891_signed_r.tsv",R,delimiter="\t",fmt="%.10g")
    # Full source-CS denominators; numerator requires disease/QTL exact overlap and LD retention.
    cs=pd.read_csv(a.source_cs,sep="\t",dtype=str); cs=cs[(cs.gene=="ENSG00000081985")&(cs.celltype=="NK")].copy(); cs["PIP"]=pd.to_numeric(cs.PIP)
    retained_keys=set(rows.variant_key); csrows=[]
    for sig,g in cs.groupby("Credible_Set"):
        hit=g[g.SNP.isin(retained_keys)]; total=float(g.PIP.sum()); captured=float(hit.PIP.sum())
        csrows.append({"source_cs":str(sig),"members_total":len(g),"members_retained":len(hit),"pip_total":total,
                       "pip_retained":captured,"pip_mass_fraction":captured/total if total else None})
    coverage=len(rows)/len(d); evals=np.linalg.eigvalsh(R); anchors={x:x in set(rows.gwas_rsids) for x in ANCHORS}
    af_g=pd.to_numeric(rows.gwas_af_alt); af_q=pd.to_numeric(rows.qtl_af_alt); af_e=rows.eur503_alt_af
    afd_g=np.abs(af_g-af_e); afd_q=np.abs(af_q-af_e)
    # A transparent global precision diagnostic. It is descriptive; no variant is removed by residual size.
    ridge=1e-4; precision=np.linalg.pinv(R+ridge*np.eye(len(R))); zdiag=[]
    for label,z in [("gwas",pd.to_numeric(rows.gwas_z).to_numpy()),("qtl",pd.to_numeric(rows.qtl_z).to_numpy())]:
        resid=(precision@z)/np.sqrt(np.maximum(np.diag(precision),1e-12))
        for i,val in enumerate(resid): zdiag.append({"trait":label,"variant_key":rows.variant_key.iloc[i],"standardized_precision_residual":float(val)})
    zd=pd.DataFrame(zdiag); zd.to_csv(a.out_dir/"EUR503_current891_zLD_precision_diagnostic.tsv",sep="\t",index=False)
    rules={"coverage_fraction_min":0.80,"each_source_cs_pip_mass_fraction_min":0.95,"all_three_anchors_required":True,
           "max_asymmetry":1e-10,"max_diag_deviation":1e-10,"min_eigenvalue_tolerance":-1e-7}
    metrics={"target_variants":len(d),"single_rsids":int(d.single_rsid.sum()),"duplicate_single_rsid_rows":int(d.valid_rsid_duplicate.sum()),
             "retained_variants":len(rows),"coverage_fraction":coverage,"samples":n_samples,"source_cs":csrows,"anchors":anchors,
             "max_asymmetry":float(np.abs(R-R.T).max()),"max_diag_deviation":float(np.abs(np.diag(R)-1).max()),
             "min_eigenvalue":float(evals.min()),"rank_tol_1e_10":int(np.linalg.matrix_rank(R,tol=1e-10)),
             "gwas_vs_eur503_af_pearson":pearson(af_g,af_e),"qtl_vs_eur503_af_pearson":pearson(af_q,af_e),
             "gwas_vs_eur503_af_median_abs_diff":float(np.median(afd_g)),"gwas_vs_eur503_af_p95_abs_diff":float(np.quantile(afd_g,.95)),
             "qtl_vs_eur503_af_median_abs_diff":float(np.median(afd_q)),"qtl_vs_eur503_af_p95_abs_diff":float(np.quantile(afd_q,.95)),
             "gwas_zLD_max_abs_precision_residual":float(zd[zd.trait=="gwas"].standardized_precision_residual.abs().max()),
             "qtl_zLD_max_abs_precision_residual":float(zd[zd.trait=="qtl"].standardized_precision_residual.abs().max())}
    checks={"coverage":coverage>=rules["coverage_fraction_min"],
            "source_cs_pip":all(x["pip_mass_fraction"]>=rules["each_source_cs_pip_mass_fraction_min"] for x in csrows),
            "anchors":all(anchors.values()),"symmetry":metrics["max_asymmetry"]<=rules["max_asymmetry"],
            "diagonal":metrics["max_diag_deviation"]<=rules["max_diag_deviation"],
            "psd":metrics["min_eigenvalue"]>=rules["min_eigenvalue_tolerance"]}
    gate={"schema_version":"CMM_R4A12FG6_EXTERNAL_LD_GATE_1.0","status":"PASS" if all(checks.values()) else "FAIL_INPUT_COVERAGE_FOR_MULTISIGNAL",
          "pass":all(checks.values()),"rules":rules,"checks":checks,"metrics":metrics,
          "input_sha256":{"harmonized":sha(a.harmonized),"source_cs":sha(a.source_cs),"bed":sha(bed_path),"bim":sha(bim_path),"fam":sha(fam_path)},
          "notes":["z-LD residuals are reported only; no variant was deleted or reweighted by residual size.","LD counts current ALT and is signed."]}
    (a.out_dir/"R4A12FG6_full_EUR503_LD_gate.json").write_text(json.dumps(gate,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Complete mapping audit includes every input row.
    audit=d.merge(mapped[["input_index","bim_index","a1","a2","allele_set_match","alt_is_bim_a2","alt_is_bim_a1"]],on="input_index",how="left")
    audit["retained_in_LD"]=audit.variant_key.isin(retained_keys); audit.to_csv(a.out_dir/"EUR503_current891_mapping_audit.tsv",sep="\t",index=False)
    print(json.dumps(gate,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
