#!/usr/bin/env python3
"""Plot the frozen Figure 1–6 evidence architecture."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(r"H:\SCI2\YR1")
OUT=ROOT/"5_analysis/figures/R7B1E"; OUT.mkdir(parents=True,exist_ok=True)
titles=["Figure 1\nScope & gates","Figure 2\nReclassification","Figure 3\nCalibration trade-off","Figure 4\nIL12RB2 external","Figure 5\nFCRL3 contrast","Figure 6\nTissue boundary"]
sub=["6,923 → 5,460 → 642\n2,568 diagnostics PASS","H4↔H3\n92 H4 / 428 H3\n32 mixed-pair","False-H4 ↓\nRecovery also ↓\nNo general superiority","OneK + TenK + FinnGen\nRisk allele → higher\nPositional chromatin only","B-cell support\nCD8_ET counterexample\nFinnGen non-return","5 PBC vs 5 control\nBoth q=0.111\nDetectability only"]
colors=["#4472C4","#5B9BD5","#70AD47","#ED7D31","#A64D79","#7F7F7F"]
fig,ax=plt.subplots(figsize=(14,4.8)); ax.set_xlim(0,6); ax.set_ylim(0,2.2); ax.axis("off")
for i,(t,s,c) in enumerate(zip(titles,sub,colors)):
    x=i+.08
    box=FancyBboxPatch((x,.45),.84,1.25,boxstyle="round,pad=0.03,rounding_size=0.04",facecolor=c,edgecolor="white",linewidth=1.5,alpha=.95)
    ax.add_patch(box); ax.text(x+.42,1.42,t,ha="center",va="center",fontsize=11,fontweight="bold",color="white")
    ax.text(x+.42,.88,s,ha="center",va="center",fontsize=9,color="white",linespacing=1.35)
    if i<5: ax.annotate("",xy=(i+1.04,1.08),xytext=(i+.94,1.08),arrowprops=dict(arrowstyle="->",color="#555555",lw=1.5))
ax.text(.08,2.03,"R7B1E frozen manuscript evidence architecture",fontsize=16,fontweight="bold",ha="left")
ax.text(.08,.12,"Claim ceiling: systematic PBC screening + high-information multi-signal reclassification + bounded external/tissue validation",fontsize=10,ha="left",color="#333333")
fig.tight_layout();
for ext in ("png","pdf","svg"): fig.savefig(OUT/f"R7B1E_figure_source_architecture.{ext}",dpi=300,bbox_inches="tight")
plt.close(fig)
