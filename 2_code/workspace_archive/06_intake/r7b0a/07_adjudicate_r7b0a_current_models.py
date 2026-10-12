#!/usr/bin/env python3
"""R7B0A current-release dual-model QC and reclassification summary.

This script deliberately separates:
1) model-identity/QC gate; and
2) biological posterior class.
It does not require H4 for G1B PASS.
"""
from pathlib import Path
import os, json
import numpy as np
import pandas as pd

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
BASE=ROOT/"3_results/04_integration/R7B0A/current_release_dualmodel"
COL=BASE/"R7B0A_current_release_dualmodel_coloc_susie.tsv"
FIT=BASE/"R7B0A_current_release_dualmodel_fit_QC.tsv"
IDENTITY=BASE/"R7B0A_current_release_identity_manifest.tsv"

EXPECTED_CONFIGS={"CURPF10_L5","CURPF10_L10","CURPF10_L20","CURPF50_L10"}

def as_bool(series):
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().isin({"true","1","yes"})

def h4ratio(row):
    d=float(row["PP.H3.abf"])+float(row["PP.H4.abf"])
    return float(row["PP.H4.abf"])/d if d>0 else np.nan

def best_for(df, p12):
    d=df[np.isclose(pd.to_numeric(df["p12"]),p12)].copy()
    if d.empty: return None
    d["PP.H4.abf"]=pd.to_numeric(d["PP.H4.abf"],errors="coerce")
    d=d[np.isfinite(d["PP.H4.abf"])]
    if d.empty: return None
    return d.loc[d["PP.H4.abf"].idxmax()]

def class_row(row):
    if row is None: return "NO_COLOC_SUMMARY"
    h3=float(row["PP.H3.abf"]); h4=float(row["PP.H4.abf"]); rr=h4ratio(row)
    if h4>=0.80 and rr>=0.80: return "H4_DOMINANT"
    if h3>h4 and rr<0.50: return "H3_DOMINANT"
    return "AMBIGUOUS"

def main():
    c=pd.read_csv(COL,sep="\t")
    f=pd.read_csv(FIT,sep="\t")
    identity=pd.read_csv(IDENTITY,sep="\t")

    # This hard gate is intentionally independent of H3/H4 posterior class.
    # It requires exact current-release artifact identity plus auditable fits.
    identity_pass=(
        len(identity)==14 and
        identity[["gene","cell_type","mode"]].drop_duplicates().shape[0]==14 and
        as_bool(identity["model_identity_pass"]).all()
    )
    f["disease_s_rss_num"]=pd.to_numeric(f["disease_s_rss"],errors="coerce")
    f["qtl_s_rss_num"]=pd.to_numeric(f["qtl_s_rss"],errors="coerce")
    f["disease_kriging_n_num"]=pd.to_numeric(f["disease_kriging_n"],errors="coerce")
    f["qtl_kriging_n_num"]=pd.to_numeric(f["qtl_kriging_n"],errors="coerce")
    f["common_variants_num"]=pd.to_numeric(f["common_variants"],errors="coerce")
    fit_key_exact=(
        len(f)==28 and
        f[["gene","cell_type","config"]].drop_duplicates().shape[0]==28 and
        set(f["config"].astype(str))==EXPECTED_CONFIGS
    )
    f["s_rss_hard_pass"]=(
        f["disease_s_rss_num"].between(0,1,inclusive="both") &
        f["qtl_s_rss_num"].between(0,1,inclusive="both")
    )
    f["convergence_pass"]=(as_bool(f["disease_converged"]) & as_bool(f["qtl_converged"]))
    f["coverage_pass"]=f["common_variants_num"]>=200

    def purity_ok(prefix):
        cs=pd.to_numeric(f[f"{prefix}_cs"],errors="coerce")
        purity=pd.to_numeric(f[f"{prefix}_cs_min_min_abs_corr"],errors="coerce")
        return (cs==0) | ((cs>0) & purity.notna() & (purity>=0.5-1e-8))

    f["credible_set_purity_pass"]=purity_ok("disease") & purity_ok("qtl")
    f["hard_qc_pass"]=(
        f["qtl_model"].astype(str).str.startswith("CURRENT_RELEASE_") &
        f["coverage_pass"] & f["convergence_pass"] & f["s_rss_hard_pass"] &
        f["credible_set_purity_pass"]
    )
    # Kriging flags are not silently ignored. Any flagged SNP holds G1B for
    # explicit review even when all structural/model checks pass.
    f["diagnostic_review_flag"]=(
        (f["disease_kriging_n_num"].fillna(1)>0) |
        (f["qtl_kriging_n_num"].fillna(1)>0)
    )
    f.to_csv(BASE/"R7B0A_current_release_dualmodel_fit_QC_adjudicated.tsv",sep="\t",index=False)

    summaries=[]
    for gene,cell,cfg in f[["gene","cell_type","config"]].drop_duplicates().itertuples(index=False,name=None):
        d=c[(c.gene==gene)&(c.cell_type==cell)&(c.config==cfg)].copy()
        default=best_for(d,1e-5)
        low=best_for(d,1e-6)
        summaries.append({
            "gene":gene,"cell_type":cell,"config":cfg,
            "default_class":class_row(default),
            "default_PP_H4":np.nan if default is None else float(default["PP.H4.abf"]),
            "default_H4_ratio":np.nan if default is None else h4ratio(default),
            "lowprior_PP_H4":np.nan if low is None else float(low["PP.H4.abf"]),
            "lowprior_H4_ratio":np.nan if low is None else h4ratio(low)
        })
    s=pd.DataFrame(summaries)
    wide=[]
    for (gene,cell),d in s.groupby(["gene","cell_type"]):
        pf10=d[d.config.astype(str).str.startswith("CURPF10_")]
        pf50=d[d.config=="CURPF50_L10"]
        pf10_classes=sorted(set(pf10.default_class.tolist()))
        pf50_class=pf50.default_class.iloc[0] if len(pf50) else "MISSING"
        if set(pf10_classes)=={"H4_DOMINANT"} and pf50_class=="H4_DOMINANT":
            bio="STABLE_H4_ACROSS_CURRENT_PF10_PF50"
        elif "H3_DOMINANT" in pf10_classes and pf50_class=="H4_DOMINANT":
            bio="PF_NUMBER_SENSITIVE_H3_TO_H4"
        elif "H4_DOMINANT" in pf10_classes and pf50_class=="H3_DOMINANT":
            bio="PF_NUMBER_SENSITIVE_H4_TO_H3"
        elif all(x=="H3_DOMINANT" for x in pf10_classes) and pf50_class=="H3_DOMINANT":
            bio="STABLE_H3"
        elif len(set(pf10_classes))>1:
            bio="PF10_L_SENSITIVE"
        else:
            bio="MIXED_OR_UNINFORMATIVE"
        wide.append({
            "gene":gene,"cell_type":cell,
            "current_pf10_classes":";".join(pf10_classes),
            "current_pf50_class":pf50_class,
            "current_dualmodel_biological_class":bio
        })
    W=pd.DataFrame(wide)
    W.to_csv(BASE/"R7B0A_current_release_reclassification.tsv",sep="\t",index=False)
    s.to_csv(BASE/"R7B0A_current_release_config_summary.tsv",sep="\t",index=False)

    expected=7*4
    hard_fit_pass=bool(fit_key_exact and f["hard_qc_pass"].all())
    diagnostic_review_rows=int(f["diagnostic_review_flag"].sum())
    overall=bool(identity_pass and hard_fit_pass and diagnostic_review_rows==0)
    if overall:
        g1b="PASS"
    elif identity_pass and hard_fit_pass and diagnostic_review_rows>0:
        g1b="HOLD_DIAGNOSTIC_REVIEW"
    else:
        g1b="HOLD_HARD_QC"
    bio_counts=W["current_dualmodel_biological_class"].value_counts().to_dict()
    state={
        "schema":"R7B0A_CURRENT_RELEASE_DUALMODEL_1.0",
        "comparisons":7,
        "expected_fit_rows":expected,
        "observed_fit_rows":int(len(f)),
        "identity_manifest_rows":int(len(identity)),
        "identity_manifest_pass_rows":int(as_bool(identity["model_identity_pass"]).sum()),
        "identity_manifest_overall_pass":bool(identity_pass),
        "fit_key_exact":bool(fit_key_exact),
        "hard_fit_qc_pass_rows":int(f["hard_qc_pass"].sum()),
        "diagnostic_review_rows":diagnostic_review_rows,
        "biological_class_counts":bio_counts,
        "G1B_CURRENT_RELEASE_MODEL_IDENTITY":g1b,
        "HISTORICAL_PF10_SOURCE_IDENTITY":"HOLD_UNRESOLVED",
        "R7B1":"GO_ELIGIBILITY_AND_ABF_SCREEN" if overall else "HOLD",
        "note":"G1B is a source/model/QC gate; biological H4/H3 classes do not determine G1B PASS. Kriging flags require explicit review rather than silent passage."
    }
    (BASE/"R7B0A_state.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
    print(json.dumps(state,indent=2))

if __name__=="__main__":
    main()
