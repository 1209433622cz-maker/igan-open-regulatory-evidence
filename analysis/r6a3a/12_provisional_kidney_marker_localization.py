from __future__ import annotations
import os,gzip,json
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
DATA=ROOT/"1_data/scrna/IgAN/GSE127136"
OUT=ROOT/"3_results/05_tissue/R6A3A"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A3A"; AUD.mkdir(parents=True,exist_ok=True)

markers={
"Mesangial":["MGP","PDGFRB"],"Endothelial":["PECAM1","VWF","CLDN5"],"Podocyte":["NPHS2","PODXL","PTPRO"],
"Proximal_tubule":["CUBN","SLC13A1","LRP2"],"VCAM1_PT":["VCAM1"],"TAL":["UMOD","SLC12A1"],
"Principal":["AQP2","AQP3"],"Intercalated":["ATP6V1G3"],"Neutrophil":["CXCR2","IL1B"],
"T_cell":["CD3D"],"Macrophage":["C1QC"],"Monocyte":["CD68"]}
allm=set(sum(markers.values(),[]))|{"ZMIZ1"}

def kidney_titles_from_soft(path):
    rows=[]; cur=None
    with gzip.open(path,"rt",encoding="utf-8",errors="replace") as h:
        for line in h:
            line=line.rstrip()
            if line.startswith("^SAMPLE = "):
                if cur: rows.append(cur)
                cur={}
            elif cur is not None and line.startswith("!Sample_title = "):
                cur["title"]=line.split(" = ",1)[1]
            elif cur is not None and line.startswith("!Sample_characteristics_ch1 = "):
                value=line.split(" = ",1)[1]
                if ": " in value:
                    key,val=value.split(": ",1)
                    cur[key.strip().lower().replace(" ","_")]=val.strip()
        if cur: rows.append(cur)
    meta=pd.DataFrame(rows)
    if not {"title","patients"}.issubset(meta.columns):
        raise RuntimeError(f"Cannot identify kidney cells from SOFT columns {list(meta.columns)}")
    return set(meta.loc[~meta.patients.astype(str).str.startswith("PBM_"),"title"].astype(str))

counts=DATA/"GSE127136_project_IgA_nephropathy_counts.csv.gz"
with gzip.open(counts,"rt",encoding="utf-8") as h:
    header=h.readline().rstrip().split(","); cells=header[1:]
    lib=np.zeros(len(cells)); expr={}
    for line in h:
        gene,vals=line.rstrip().split(",",1); x=np.fromstring(vals,dtype=float,sep=","); lib+=x
        if gene in allm: expr[gene]=x
missing=sorted(allm-set(expr))
# Missing one optional marker does not abort; scores use available markers.
norm={g:np.log1p(expr[g]/(lib+1)*1e6) for g in expr}
kidney_titles=kidney_titles_from_soft(DATA/"GSE127136_family.soft.gz")
kidney_mask=np.asarray([cell in kidney_titles for cell in cells])
if kidney_mask.sum()!=len(kidney_titles) or kidney_mask.sum()==0:
    raise RuntimeError(f"Kidney cell-title mismatch: matrix={kidney_mask.sum()} SOFT={len(kidney_titles)}")
cells=np.asarray(cells)[kidney_mask]
norm={gene:values[kidney_mask] for gene,values in norm.items()}
scores={}
for ct,gs in markers.items():
    av=[norm[g] for g in gs if g in norm]
    scores[ct]=np.vstack(av).mean(0) if av else np.zeros(len(cells))
names=list(scores); mat=np.vstack([scores[x] for x in names]).T
best=np.argmax(mat,axis=1); srt=np.sort(mat,axis=1)
margin=srt[:,-1]-srt[:,-2] if mat.shape[1]>1 else srt[:,-1]
mx=srt[:,-1]
labels=np.array([names[i] for i in best],dtype=object)
labels[(mx<0.10)|(margin<0.05)]="Unresolved"
res=pd.DataFrame({"title":cells,"marker_label":labels,"top_score":mx,"score_margin":margin,
                  "ZMIZ1_log1pCPM":norm.get("ZMIZ1",np.zeros(len(cells)))})
res.to_csv(OUT/"R6A3A_GSE127136_provisional_marker_annotation.tsv.gz",sep="\t",index=False,compression="gzip")
localization=(res.groupby("marker_label",as_index=False)
              .agg(cells=("title","size"),ZMIZ1_detection_fraction=("ZMIZ1_log1pCPM",lambda x: float((x>0).mean())),
                   ZMIZ1_mean_log1pCPM=("ZMIZ1_log1pCPM","mean"),ZMIZ1_median_log1pCPM=("ZMIZ1_log1pCPM","median"))
              .sort_values("ZMIZ1_mean_log1pCPM",ascending=False))
localization.to_csv(OUT/"R6A3A_GSE127136_ZMIZ1_provisional_localization_summary.tsv",sep="\t",index=False)
audit={"kidney_cells":len(cells),"excluded_peripheral_monocytes":int((~kidney_mask).sum()),
       "marker_labels":pd.Series(labels).value_counts().to_dict(),"missing_marker_genes":missing,
       "status":"PASS_PROVISIONAL" if (labels!="Unresolved").mean()>=0.50 else "HOLD_LOW_ASSIGNMENT",
       "boundary":"marker-based provisional localization only; not a substitute for a full Seurat/Scanpy re-clustering"}
(AUD/"R6A3A_kidney_marker_annotation_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
