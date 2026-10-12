#!/usr/bin/env python3
"""
Targeted donor-level detectability from a Cell Ranger-like BAM.
Counts unique (cell barcode, UMI, gene) for a predeclared small marker panel.
This is a completion gate, not the manuscript-final clustering workflow.
"""
from pathlib import Path
import argparse, json, collections, sys
import pandas as pd

try:
    import pysam
except ImportError:
    raise SystemExit("Install pysam first: python -m pip install pysam")

ap=argparse.ArgumentParser()
ap.add_argument("--bam",required=True)
ap.add_argument("--run",required=True)
ap.add_argument("--outdir",required=True)
a=ap.parse_args()
out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)

targets={"FCRL3","IL12RB2"}
B={"CD79A","CD79B","MS4A1","CD37","CD74","HLA-DRA","CD19","CD22"}
NK={"NKG7","GNLY","KLRD1","PRF1","GZMB","XCL1","XCL2"}
T={"CD3D","CD3E","TRBC1","TRBC2","IL7R"}
MY={"LST1","TYROBP","FCER1G","CTSS","AIF1","LYZ"}
panel=targets|B|NK|T|MY

# panel_counts[barcode][gene] = set(UMIs)
panel_counts=collections.defaultdict(lambda: collections.defaultdict(set))
tag_qc=collections.Counter()
reads=0
with pysam.AlignmentFile(a.bam,"rb",check_sq=False) as bam:
    for rec in bam.fetch(until_eof=True):
        reads+=1
        if rec.is_unmapped or rec.is_secondary or rec.is_supplementary:
            continue
        if not rec.has_tag("CB") or not rec.has_tag("UB"):
            continue
        cb=rec.get_tag("CB"); ub=rec.get_tag("UB")
        gene=None
        if rec.has_tag("GN"):
            gene=rec.get_tag("GN"); tag_qc["GN"]+=1
        elif rec.has_tag("GX"):
            gene=rec.get_tag("GX"); tag_qc["GX_only"]+=1
        if not gene:
            continue
        # Cell Ranger may list semicolon-separated genes; retain only unambiguous panel hits.
        hits=[g for g in str(gene).split(";") if g in panel]
        if len(hits)!=1:
            continue
        panel_counts[cb][hits[0]].add(ub)

rows=[]
for cb,gdict in panel_counts.items():
    counts={g:len(gdict.get(g,set())) for g in panel}
    b_genes=sum(counts[g]>0 for g in B); nk_genes=sum(counts[g]>0 for g in NK)
    t_genes=sum(counts[g]>0 for g in T); my_genes=sum(counts[g]>0 for g in MY)
    b_umi=sum(counts[g] for g in B); nk_umi=sum(counts[g] for g in NK)
    t_umi=sum(counts[g] for g in T); my_umi=sum(counts[g] for g in MY)
    # Conservative gate labels: target genes are NOT used in classification.
    bcell=(b_genes>=2 and b_umi>=3 and b_umi>max(nk_umi,t_umi,my_umi))
    nkcell=(nk_genes>=2 and nk_umi>=3 and nk_umi>max(b_umi,my_umi) and nk_umi>=t_umi)
    rows.append({
        "run":a.run,"cell_barcode":cb,
        "B_marker_genes":b_genes,"B_marker_UMI":b_umi,
        "NK_marker_genes":nk_genes,"NK_marker_UMI":nk_umi,
        "T_marker_genes":t_genes,"T_marker_UMI":t_umi,
        "MY_marker_genes":my_genes,"MY_marker_UMI":my_umi,
        "B_lineage_gate":bcell,"NK_lineage_gate":nkcell,
        "FCRL3_UMI":counts["FCRL3"],"IL12RB2_UMI":counts["IL12RB2"]
    })
cells=pd.DataFrame(rows)
cells.to_csv(out/f"{a.run}_target_panel_cells.tsv.gz",sep="\t",index=False,compression="gzip")

summary={
    "run":a.run,"bam":str(a.bam),"reads_scanned":reads,
    "barcodes_with_panel_signal":len(cells),
    "B_gate_cells":int(cells.B_lineage_gate.sum()) if len(cells) else 0,
    "NK_gate_cells":int(cells.NK_lineage_gate.sum()) if len(cells) else 0,
    "FCRL3_B_positive_cells":int(((cells.B_lineage_gate)&(cells.FCRL3_UMI>0)).sum()) if len(cells) else 0,
    "FCRL3_B_UMI":int(cells.loc[cells.B_lineage_gate,"FCRL3_UMI"].sum()) if len(cells) else 0,
    "IL12RB2_NK_positive_cells":int(((cells.NK_lineage_gate)&(cells.IL12RB2_UMI>0)).sum()) if len(cells) else 0,
    "IL12RB2_NK_UMI":int(cells.loc[cells.NK_lineage_gate,"IL12RB2_UMI"].sum()) if len(cells) else 0,
    "gene_tag_counts":dict(tag_qc),
    "primary_FCRL3_B_detectable":bool(len(cells) and cells.loc[cells.B_lineage_gate,"FCRL3_UMI"].sum()>0),
    "primary_IL12RB2_NK_detectable":bool(len(cells) and cells.loc[cells.NK_lineage_gate,"IL12RB2_UMI"].sum()>0),
    "sensitivity_FCRL3_B":bool(len(cells) and
       cells.loc[cells.B_lineage_gate,"FCRL3_UMI"].sum()>=3 and
       ((cells.B_lineage_gate)&(cells.FCRL3_UMI>0)).sum()>=2),
    "sensitivity_IL12RB2_NK":bool(len(cells) and
       cells.loc[cells.NK_lineage_gate,"IL12RB2_UMI"].sum()>=3 and
       ((cells.NK_lineage_gate)&(cells.IL12RB2_UMI>0)).sum()>=2),
    "boundary":"target-panel donor detectability only; manuscript-final analysis requires full QC/reclustering/pseudobulk"
}
(out/f"{a.run}_target_panel_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
