#!/usr/bin/env python3
"""Build the R7B1E claim ledger and Figure 1–6 source-data freeze."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT=Path(r"H:\SCI2\YR1")
OUT=ROOT/"3_results/04_integration/R7B1E"
SRC=OUT/"figure_source_data"

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def claim(cid,section,text,tier,status,anchor,primary,support,allowed,prohibited,limit,figure,panel):
    return dict(claim_id=cid,manuscript_section=section,claim_text=text,evidence_tier=tier,status=status,
      quantitative_anchor=anchor,primary_source_file=primary,supporting_source_files=support,
      allowed_verbs=allowed,prohibited_verbs=prohibited,limitation=limit,figure=figure,panel=panel)

def main()->None:
    OUT.mkdir(parents=True,exist_ok=True); SRC.mkdir(parents=True,exist_ok=True)
    p=lambda x: ROOT/x
    abf_state=json.loads(p("3_results/04_integration/R7B1/R7B1_current_PF10_ABF_state.json").read_text(encoding="utf-8"))
    rec=pd.read_csv(p("3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"),sep="\t")
    sem=pd.read_csv(p("3_results/04_integration/R7B1E0/signal_semantics/R7B1E0_signal_semantics_642.tsv"),sep="\t")
    diag=json.loads(p("3_results/04_integration/R7B1E0/diagnostic_adjudication/R7B1E0_diagnostic_adjudication_state.json").read_text(encoding="utf-8"))
    sim=pd.read_csv(p("3_results/05_simulation/R7B1C/aggregate/R7B1C_scenario_summary.tsv"),sep="\t")
    ext=json.loads(p("3_results/04_integration/R7B1D/R7B1D_external_gate_state.json").read_text(encoding="utf-8"))
    tissue=json.loads(p("3_results/04_integration/R7A2A1/R7A2A1_final_adjudication.json").read_text(encoding="utf-8"))
    trans=pd.crosstab(rec.ABF_classification,rec.PF10_multisignal_state).reindex(
      index=["ROBUST_H4_TRIGGER","H3_H4_AMBIGUITY_TRIGGER","H3_DISTINCT_SIGNAL","NO_TRIGGER_OR_UNINFORMATIVE"],
      columns=["H4_SUPPORTED_STABLE","H3_SUPPORTED_STABLE","MODEL_SENSITIVE","UNINFORMATIVE"],fill_value=0)
    if trans.to_numpy().sum()!=642: raise RuntimeError("transition matrix drift")

    scope=pd.DataFrame([
      ["PBC-wide frozen comparisons",6923],["ABF eligible",5460],["insufficient overlap",1463],
      ["primary ABF triggers",184],["H3 rescue layer",455],["borderline calibration",3],
      ["multi-signal high-information subset",642],["PF10 H4-supported",92],["PF10 H3-supported",428],
      ["model-sensitive",59],["uninformative",63]
    ],columns=["denominator","n"])
    scope.to_csv(SRC/"Figure1_study_scope_counts.tsv",sep="\t",index=False)
    trans.rename_axis("ABF_classification").reset_index().to_csv(SRC/"Figure2_bidirectional_transition.tsv",sep="\t",index=False)
    sim.to_csv(SRC/"Figure3_simulation_scenario_summary.tsv",sep="\t",index=False)
    il12=pd.read_csv(p("3_results/04_integration/R7B1D/R7B1D_FinnGen_PBC_molQTL_coloc.tsv"),sep="\t")
    direction=pd.read_csv(p("3_results/04_integration/R7B1D/R7B1D_direction_summary.tsv"),sep="\t")
    cascade=pd.read_csv(p("3_results/04_integration/R7B1D/R7B1D_IL12RB2_FinnGen_positional_cascade.tsv"),sep="\t")
    il12.to_csv(SRC/"Figure4_IL12RB2_FinnGen_coloc.tsv",sep="\t",index=False)
    pd.concat([direction,direction.iloc[0:0]],ignore_index=True).to_csv(SRC/"Figure4_5_risk_allele_direction.tsv",sep="\t",index=False)
    cascade.to_csv(SRC/"Figure4_IL12RB2_positional_chromatin.tsv",sep="\t",index=False)
    reps=["R7B1_000258","R7B1_000410","R7B1_000411","R7B1_000414"]
    rec[rec.comparison_id.isin(reps)].merge(sem[["comparison_id","semantic_state","same_signal_pair_confirmed","mixed_h4_h3_within_any_config"]],on="comparison_id").to_csv(SRC/"Figure5_representative_signal_axes.tsv",sep="\t",index=False)
    trows=[]
    for axis,d in tissue["tissue_result"].items():
        if not isinstance(d,dict): continue
        if "PBC_n" in d:
            trows.append({"axis":axis,**d})
    pd.DataFrame(trows).to_csv(SRC/"Figure6_exact_5vs5_tissue.tsv",sep="\t",index=False)
    sem.groupby(["historical_PF10_multisignal_state","semantic_state"]).size().rename("n").reset_index().to_csv(SRC/"Figure5_signal_semantics_counts.tsv",sep="\t",index=False)

    reclass_source="3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
    claims=[
      claim("C01","Results 1","The frozen PBC-wide screen contained 6,923 locus–gene–cell comparisons; 5,460 met the ABF overlap threshold.","T1_DIRECT","SUPPORTED","6923 total; 5460 eligible","3_results/04_integration/R7B1/R7B1_current_PF10_ABF_state.json","","contained; screened","exhaustively tested by multi-signal analysis","Multi-signal inference was restricted to a high-information subset.",1,"A-B"),
      claim("C02","Results 1","The source-matched multi-signal workload comprised a prespecified 642-comparison high-information subset.","T1_DIRECT","SUPPORTED","184+455+3=642",reclass_source,"3_results/00_audit/R7B1B_v2/R7B1B_v2_exact_642_high_information_comparisons.tsv","comprised; evaluated","all 6923 received SuSiE","Subset was selected from ABF high-information states before multi-signal results.",1,"C"),
      claim("C03","Results 2","Multi-signal analysis produced bidirectional reclassification between ABF H4- and H3-dominant states.","T1_DIRECT","SUPPORTED","H4→H3=4; H3→H4=8",reclass_source,"3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_reclassification_counts.tsv","reclassified; supported","proved correct/incorrect","Real data do not provide causal truth.",2,"A"),
      claim("C04","Results 2","Among 112 ABF H4 triggers, 78 retained stable H4 support and 4 changed to stable H3.","T1_DIRECT","SUPPORTED","78/112=69.64%; 4/112=3.57%",reclass_source,"","retained; changed","all remaining 30 were false positives","Six were model-sensitive and 24 uninformative.",2,"B"),
      claim("C05","Results 2","Among 455 ABF H3 comparisons, 8 changed to stable H4 and 409 retained stable H3-pair support.","T1_DIRECT","SUPPORTED","8/455=1.76%; 409/455=89.89%",reclass_source,"","changed; retained","global absence of shared signals","H3-pair support can coexist with other shared pairs.",2,"C"),
      claim("C06","Results 2","PF50 matched 491 of the 520 comparisons with a definite PF10 H4/H3 state.","T1_DIRECT","SUPPORTED","491/520=94.42%; sensitive=4; PF50-uninformative=25",reclass_source,"3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_PF10_PF50_sensitivity_counts.tsv","matched","642 comparisons were concordant","122 model-sensitive/uninformative PF10 outcomes were not comparable.",2,"D"),
      claim("C07","Results 2","All 92 stable-H4 comparisons and all 428 stable-H3 comparisons retained the same signal-pair identity across L10 and at least one other PF10 L setting.","T1_DIAGNOSTIC","SUPPORTED","92/92 H4; 428/428 H3", "3_results/04_integration/R7B1E0/signal_semantics/R7B1E0_signal_semantics_state.json","3_results/04_integration/R7B1E0/signal_semantics/R7B1E0_signal_pair_match_details.tsv.gz","retained signal-pair identity","biological mechanism was stable","Identity is based on exact leads or two-trait CS Jaccard ≥0.50.",2,"E"),
      claim("C08","Results 2","Thirty-two stable-H4 comparisons also contained an H3-qualifying pair.","T1_DIAGNOSTIC","SUPPORTED","32 comparisons","3_results/04_integration/R7B1E0/signal_semantics/R7B1E0_signal_semantics_state.json","","coexisted","the locus had only one shared signal","Shared and distinct pairs can coexist within a comparison.",2,"F"),
      claim("C09","Methods/QC","Corrected kriging diagnostics were evaluated for every disease and QTL comparison–model unit.","T1_DIAGNOSTIC","SUPPORTED","2568/2568 PASS; 0 HOLD","3_results/04_integration/R7B1E0/diagnostic_adjudication/R7B1E0_diagnostic_adjudication_state.json","3_results/00_audit/R7B1E0/R7B1E0_independent_QA.json","evaluated","historical runner already evaluated all diagnostics","This is a post-result diagnostic repair with preserved classifications.",1,"D"),
      claim("C10","Methods/QC","One unique official-rule kriging event was reviewed and did not enter any credible set.","T1_DIAGNOSTIC","SUPPORTED","rs1800378; 1 unique event; 0 CS membership","3_results/04_integration/R7B1E0/diagnostic_adjudication/R7B1E0_official_kriging_flags_review.tsv","","reviewed; retained","no z–LD discrepancies existed","The affected stable-H3 comparison is not claim-bearing.",1,"D"),
      claim("C11","Results 3","In the frozen distinct-signal scenarios, matched multi-signal inference reduced average false-H4 decisions relative to ABF.","T2_SIMULATION","SUPPORTED","12.41%→8.56%; relative reduction 31.02%","3_results/05_simulation/R7B1C/aggregate/R7B1C_scenario_summary.tsv","","reduced in frozen scenarios","was generally superior","Only S2 and S5 under two empirical templates.",3,"A"),
      claim("C12","Results 3","The reduction in false-H4 decisions was accompanied by lower shared-signal recovery.","T2_SIMULATION","SUPPORTED","32.99%→26.66%; relative loss 19.20%","3_results/05_simulation/R7B1C/aggregate/R7B1C_scenario_summary.tsv","","was accompanied by","improved sensitivity","Many complex shared simulations were uninformative.",3,"B"),
      claim("C13","Results 3","Performance gains were scenario-dependent: matched false H4 remained 16.0% in S2 and fell from 4.32% to 1.12% in S5.","T2_SIMULATION","SUPPORTED","S2=16.00%; S5 4.32%→1.12%","3_results/05_simulation/R7B1C/aggregate/R7B1C_scenario_summary.tsv","","varied; remained; fell","eliminated false colocalization","High-LD correlated distinct variants remained difficult.",3,"C"),
      claim("C14","Discussion","The simulation did not establish general method superiority or general safety of LD mismatch.","T3_INTERPRETIVE","SUPPORTED_BOUNDARY","general superiority=not demonstrated","3_results/00_audit/R7B1C/R7B1C_scientific_interpretation_state.json","","did not establish","proved no mismatch effect","S6 used only similar within-locus PF10/PF50 templates.",3,"D"),
      claim("C15","Results 4","IL12RB2–NK retained source-matched OneK support, TenK molecular-QTL replication and three FinnGen PBC–eQTL coloc records.","T2_CROSS_RESOURCE","SUPPORTED","FinnGen PP.H4 0.9698–0.9706; CS overlap 5–9","3_results/04_integration/R7B1D/R7B1D_external_gate_state.json","3_results/04_integration/R7B1D/R7B1D_FinnGen_PBC_molQTL_coloc.tsv","supported; replicated across QTL resources","three independent disease replications","FinnGen records are strata from one resource.",4,"A-B"),
      claim("C16","Results 4","The PBC risk allele was associated with higher IL12RB2 expression across OneK, TenK and FinnGen contexts.","T2_DIRECTION","SUPPORTED","3 resource families; all HIGHER","3_results/04_integration/R7B1D/R7B1D_direction_summary.tsv","","was associated with","mediated; caused","Effect-size scales are not directly comparable.",4,"C"),
      claim("C17","Results 4","IL12RB2 had a linked positional chromatin layer, but a complete variant-level cascade was not supported.","T2_CHROMATIN","SUPPORTED_BOUNDARY","peak caQTL q=3.93e-13/6.02e-15; anchor not in caQTL CS","3_results/04_integration/R7B1D/R7B1D_IL12RB2_FinnGen_positional_cascade.tsv","","linked; positional","disease→caQTL→expression cascade proved","PBC–caQTL signal colocalization was not established.",4,"D"),
      claim("C18","Results 5","FCRL3 B-cell sharing was supported in OneK and replicated in TenK molecular-QTL data.","T2_CROSS_RESOURCE","SUPPORTED","OneK stable B_IN/B_MEM; TenK B_intermediate PP.H4=0.9916","3_results/04_integration/R7B1E/figure_source_data/Figure5_representative_signal_axes.tsv","3_results/04_integration/R7A2A1/R7A2A2_claim_evidence_matrix.tsv","supported; replicated across QTL resources","independent disease replication","The same PBC GWAS was reused across OneK/TenK layers.",5,"A"),
      claim("C19","Results 5","The PBC risk allele was associated with lower FCRL3 expression in OneK and TenK B-cell contexts.","T2_DIRECTION","SUPPORTED","OneK+TenK all LOWER","3_results/04_integration/R7B1D/R7B1D_direction_summary.tsv","","was associated with","caused lower expression","FinnGen PBC direction was unavailable.",5,"B"),
      claim("C20","Results 5","FCRL3–CD8_ET changed from single-causal H4 support to source-matched H3 support and remained a counterexample.","T1_DIRECT","SUPPORTED","ABF≈0.941; PF10 multi H4≈0.004","3_results/04_integration/R7B1E/figure_source_data/Figure5_representative_signal_axes.tsv","","changed; illustrated","FCRL3 was disproved in CD8 cells","Strong eQTL does not alone establish disease sharing.",5,"C"),
      claim("C21","Results 5","Current FinnGen public output did not return a PBC–FCRL3 coloc pair.","T2_COVERAGE","SUPPORTED_BOUNDARY","0 returned PBC–FCRL3 records","3_results/04_integration/R7B1D/R7B1D_FinnGen_coloc_coverage.tsv","","did not return","proved no colocalization","Non-return is not a powered biological negative.",5,"D"),
      claim("C22","Results 6","Both target-lineage pairs were detectable in 5/5 PBC and 5/5 control liver donors, without corrected evidence of PBC-specific enrichment.","T2_TISSUE","SUPPORTED_BOUNDARY","FCRL3 q=0.111; IL12RB2 q=0.111","3_results/04_integration/R7A2A1/R7A2A1_final_adjudication.json","3_results/04_integration/R7B1E/figure_source_data/Figure6_exact_5vs5_tissue.tsv","detected; directionally lower/higher","PBC-specific upregulation; tissue mediation","Bounded marker panel, n=5 vs 5, not full-transcriptome cell-state analysis.",6,"A-C"),
    ]
    ledger=pd.DataFrame(claims); ledger.to_csv(OUT/"R7B1E_integrated_claim_evidence_ledger.tsv",sep="\t",index=False)

    panels=[
      [1,"A","Frozen universe","figure_source_data/Figure1_study_scope_counts.tsv","6,923→5,460→642","PBC-wide screening and bounded high-information follow-up","all comparisons received multi-signal analysis"],
      [1,"B","Model identity and diagnostic closure","../R7B0A/current_release_dualmodel/R7B0A_state.json; ../R7B1E0/diagnostic_adjudication/R7B1E0_diagnostic_adjudication_state.json","14/14 identity; 2,568/2,568 diagnostic units","model/diagnostic gates passed","historical kriging was already complete"],
      [2,"A-D","Bidirectional transition and PF sensitivity","figure_source_data/Figure2_bidirectional_transition.tsv; ../R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv","78 stable H4; 409 stable H3; 4 H4→H3; 8 H3→H4","bidirectional reclassification in subset","truth-proven correction"],
      [2,"E-F","Signal identity and coexistence","../R7B1E0/signal_semantics/R7B1E0_signal_semantics_642.tsv","92/92 H4; 428/428 H3; 32 mixed","signal-pair identity retained","H3 means no shared pair exists"],
      [3,"A-D","Truth-known calibration","figure_source_data/Figure3_simulation_scenario_summary.tsv","false H4 reduction with recovery cost","scenario-dependent trade-off","general superiority"],
      [4,"A-D","IL12RB2 external layers","figure_source_data/Figure4_IL12RB2_FinnGen_coloc.tsv; figure_source_data/Figure4_5_risk_allele_direction.tsv; figure_source_data/Figure4_IL12RB2_positional_chromatin.tsv","PP.H4 0.9698–0.9706; risk allele→higher expression","bounded external support","complete causal cascade"],
      [5,"A-D","FCRL3 support and counterexample","figure_source_data/Figure5_representative_signal_axes.tsv; figure_source_data/Figure5_signal_semantics_counts.tsv","B-cell stable H4; CD8_ET H3 counterexample","cross-QTL support and model counterexample","FinnGen negative replication"],
      [6,"A-C","Liver tissue boundary","figure_source_data/Figure6_exact_5vs5_tissue.tsv","5 vs 5; both q=0.111","lineage detectability; no corrected enrichment","tissue mediation/upregulation"],
    ]
    panel=pd.DataFrame(panels,columns=["figure","panel","purpose","source_files","quantitative_anchor","allowed_caption","prohibited_inference"])
    panel["status"]="FROZEN_SOURCE_READY"; panel.to_csv(OUT/"R7B1E_Figure1_6_panel_source_manifest.tsv",sep="\t",index=False)

    assets=[]
    for path in sorted(SRC.glob("*")):
        assets.append({"file":str(path.relative_to(ROOT)).replace("\\","/"),"bytes":path.stat().st_size,"sha256":sha256(path)})
    pd.DataFrame(assets).to_csv(OUT/"R7B1E_figure_source_asset_hashes.tsv",sep="\t",index=False)
    state={"schema":"R7B1E_EVIDENCE_FREEZE_1.0","status":"COMPLETE_PENDING_INDEPENDENT_QA","claims":len(ledger),"figures":6,"panels":len(panel),
      "new_gene_cell_locus_selection":False,"general_method_superiority":"NOT_ESTABLISHED",
      "diagnostic_closure":diag["status"],"external_gate":ext["G6_EXTERNAL_REPLICATION"],
      "tissue_enrichment":tissue["tissue_result"]["disease_specific_enrichment"],"next":"R7B2_MANUSCRIPT_V1_AFTER_QA"}
    (OUT/"R7B1E_evidence_freeze_state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2))

if __name__=="__main__": main()
