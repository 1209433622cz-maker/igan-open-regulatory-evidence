#!/usr/bin/env python3
from pathlib import Path
import os,numpy as np
ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
BASE=ROOT/"3_results/04_integration/R7A1B/sourceLD"
for d in sorted(p for p in BASE.iterdir() if p.is_dir()):
    for mode in ["PF10","PF50"]:
        p=d/f"{mode}_residualized_A1_correlation.npy"
        if p.exists():
            R=np.load(p)
            np.savetxt(d/f"{mode}_residualized_A1_correlation.tsv.gz",R,delimiter="\t",fmt="%.8g")
