from __future__ import annotations

import concurrent.futures
import hashlib
import json
import time
from pathlib import Path

import requests


URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE127nnn/GSE127136/suppl/GSE127136_project_IgA_nephropathy_counts.csv.gz"
DEST = Path(r"H:\SCI2\YR1\1_data\scrna\IgAN\GSE127136\GSE127136_project_IgA_nephropathy_counts.csv.gz")
EXPECTED = 15_703_242
PART_SIZE = 1_048_576
PART_DIR = DEST.parent / ".parts_counts"
PART_DIR.mkdir(parents=True, exist_ok=True)


def fetch(part: tuple[int, int, int]) -> dict:
    idx, start, end = part
    path = PART_DIR / f"part_{idx:03d}.bin"
    expected = end - start + 1
    if path.exists() and path.stat().st_size == expected:
        return {"part": idx, "start": start, "end": end, "bytes": expected, "status": "EXISTS"}
    headers = {"Range": f"bytes={start}-{end}", "User-Agent": "R6A1-open-data-intake/1.0"}
    for attempt in range(8):
        try:
            with requests.get(URL, headers=headers, stream=True, timeout=(30, 300)) as response:
                response.raise_for_status()
                if response.status_code != 206:
                    raise RuntimeError(f"part {idx}: expected HTTP 206, got {response.status_code}")
                with path.open("wb") as handle:
                    for block in response.iter_content(256 * 1024):
                        if block:
                            handle.write(block)
            break
        except Exception:
            if attempt == 7:
                raise
            time.sleep(2 ** min(attempt, 5))
    if path.stat().st_size != expected:
        raise RuntimeError(f"part {idx}: {path.stat().st_size} != {expected}")
    print(f"PART_OK {idx} {expected}", flush=True)
    return {"part": idx, "start": start, "end": end, "bytes": expected, "status": "DOWNLOADED"}


parts = []
for idx, start in enumerate(range(0, EXPECTED, PART_SIZE)):
    parts.append((idx, start, min(start + PART_SIZE - 1, EXPECTED - 1)))

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(fetch, parts))

with DEST.open("wb") as out:
    for idx, _, _ in parts:
        with (PART_DIR / f"part_{idx:03d}.bin").open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                out.write(block)

if DEST.stat().st_size != EXPECTED:
    raise RuntimeError("assembled byte mismatch")
h = hashlib.sha256()
with DEST.open("rb") as handle:
    for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
        h.update(block)

audit = {"url": URL, "path": str(DEST), "bytes": DEST.stat().st_size, "sha256": h.hexdigest(), "parts": results, "status": "PASS"}
out = Path(r"H:\SCI2\YR1\3_results\00_audit\R6A1\GSE127136_counts_byte_audit.json")
out.write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in audit.items() if k != "parts"}, indent=2), flush=True)
