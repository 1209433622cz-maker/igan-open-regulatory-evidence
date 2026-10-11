#!/usr/bin/env python3
"""Build and independently validate the R4A12FG6 review package."""
from __future__ import annotations
import hashlib, json, os, shutil, zipfile
from pathlib import Path

ROOT=Path(r"H:\SCI2\YR1")
NAME="CMM_R4A12FG6_FullEUR503_ThreeCellGate_2026-09-13"
DEST=ROOT/"6_release/current/R4A12FG6"; STAGE=DEST/NAME

def sha(p: Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(4<<20),b""): h.update(b)
    return h.hexdigest()

def cp(src: Path, rel: str):
    if not src.is_file(): raise FileNotFoundError(src)
    d=STAGE/rel; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,d)

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    if STAGE.exists():
        resolved=STAGE.resolve()
        if DEST.resolve() not in resolved.parents: raise RuntimeError("unsafe staging path")
        shutil.rmtree(STAGE)
    STAGE.mkdir()
    reports=ROOT/"7.Report/current/R4A12FG6"
    for p in reports.glob("*.md"): cp(p,p.name)
    qtl=ROOT/"1_data/qtl/eqtl/tenk10k/derived/IL12RB2_full/three_cells"
    for p in qtl.glob("*.tsv"): cp(p,"data/tenk10k_three_cells/"+p.name)
    for p in qtl.glob("*.json"): cp(p,"receipts/tenk10k_three_cells/"+p.name)
    ld=ROOT/"3_results/02_coloc/ld_finemap/R4A12FG6_external_EUR503_full"
    for p in ld.iterdir():
        if p.is_file(): cp(p,"data/full_EUR503_LD/"+p.name)
    smoke=ROOT/"3_results/01_smoke/R4A12FG6_IL12RB2_three_cells"
    for p in smoke.iterdir():
        if p.is_file(): cp(p,"results/three_cell_adjudication/"+p.name)
    audit=ROOT/"3_results/00_audit/R4A12FG6"
    for p in audit.rglob("*.json"): cp(p,"audit/"+p.relative_to(audit).as_posix())
    cp(ROOT/"0_admin/protocol/current/R4A12FG6_state.json","results/R4A12FG6_state.json")
    cp(ROOT/"0_admin/protocol/current/analysis_manifest_v11_amendment_A3_R4A12FG6.json","protocol/analysis_manifest_v11_amendment_A3_R4A12FG6.json")
    scripts=[
      ROOT/"2_code/06_intake/tenk10k_il12rb2/download_extract_tenk10k_three_cells_resume.py",
      ROOT/"2_code/07_analysis/R4A12FG6/build_full_EUR503_LD_for_current_891.py",
      ROOT/"2_code/07_analysis/R4A12FG6/harmonize_three_cell_il12rb2.py",
      ROOT/"2_code/07_analysis/R4A12FG6/run_three_cell_coloc_abf.R",
      ROOT/"2_code/07_analysis/R4A12FG6/RUN_R4A12FG6_INPUT_COMPLETION.ps1",
    ]
    for p in scripts: cp(p,"scripts/"+p.name)
    # Never release bytecode or range caches.
    forbidden=[p for p in STAGE.rglob("*") if p.is_file() and (p.suffix==".pyc" or "__pycache__" in p.parts or "chunk_" in p.name)]
    if forbidden: raise RuntimeError(f"forbidden files: {forbidden}")
    files=sorted(p for p in STAGE.rglob("*") if p.is_file() and p.name!="checksums.sha256")
    manifest="".join(f"{sha(p)}  {p.relative_to(STAGE).as_posix()}\n" for p in files)
    (STAGE/"checksums.sha256").write_text(manifest,encoding="utf-8")
    zip_path=DEST/(NAME+".zip")
    if zip_path.exists(): zip_path.unlink()
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(STAGE.rglob("*")):
            if p.is_file(): z.write(p,(Path(NAME)/p.relative_to(STAGE)).as_posix())
    # Independent archive CRC and manifest verification.
    with zipfile.ZipFile(zip_path) as z:
        bad=z.testzip(); names=z.namelist(); extracted={n:z.read(n) for n in names}
    if bad: raise RuntimeError(f"ZIP CRC fail: {bad}")
    base=NAME+"/"; checks=(STAGE/"checksums.sha256").read_text(encoding="utf-8").splitlines(); failures=[]
    for line in checks:
        expected,rel=line.split("  ",1); actual=hashlib.sha256(extracted[base+rel]).hexdigest()
        if actual!=expected: failures.append(rel)
    validation={"schema_version":"CMM_RELEASE_VALIDATION_1.0","status":"PASS" if not failures else "FAIL","zip":str(zip_path),
       "zip_sha256":sha(zip_path),"zip_entries":len(names),"manifest_entries":len(checks),"manifest_pass":len(checks)-len(failures),
       "manifest_fail":failures,"zip_crc":"PASS","forbidden_entries":[],"office_rendering":"NOT_APPLICABLE_NO_OFFICE_ARTIFACTS_WPS_RESERVED"}
    val=DEST/"R4A12FG6_release_validation.json"; val.write_text(json.dumps(validation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (Path(str(zip_path)+".sha256")).write_text(f"{validation['zip_sha256']}  {zip_path.name}\n",encoding="ascii")
    # Frozen snapshot of executable source, without bytecode.
    snap=ROOT/"2_code/snapshots/R4A12FG6"; snap.mkdir(parents=True,exist_ok=True)
    for p in scripts: shutil.copy2(p,snap/p.name)
    workspace={"stage":"R4A12FG6_FULL_EUR503_AND_THREE_CELL_GATE","updated":"2026-09-13","reports":str(reports),
      "release_zip":str(zip_path),"release_validation":str(val),"state":str(ROOT/"0_admin/protocol/current/R4A12FG6_state.json"),
      "next_stage":"R4A12FG7_SOURCE_MATCHED_LD_ACCESS_PACKAGE_AND_PRIMARY_TRIGGER"}
    (ROOT/"0_admin/protocol/current/workspace_paths.json").write_text(json.dumps(workspace,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(validation,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
