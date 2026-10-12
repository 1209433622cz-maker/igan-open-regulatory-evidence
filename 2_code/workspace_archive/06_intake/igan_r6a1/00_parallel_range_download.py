from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import time
from pathlib import Path

import requests


parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--bytes", required=True, type=int)
parser.add_argument("--workers", type=int, default=8)
parser.add_argument("--part-mib", type=int, default=4)
args = parser.parse_args()

dest = Path(args.output)
dest.parent.mkdir(parents=True, exist_ok=True)
part_dir = dest.parent / f".{dest.name}.parts"
part_dir.mkdir(parents=True, exist_ok=True)
part_size = args.part_mib * 1024 * 1024
parts = [(i, start, min(start + part_size - 1, args.bytes - 1)) for i, start in enumerate(range(0, args.bytes, part_size))]


def fetch(part: tuple[int, int, int]) -> dict:
    idx, start, end = part
    path = part_dir / f"part_{idx:04d}.bin"
    expected = end - start + 1
    if path.exists() and path.stat().st_size == expected:
        return {"part": idx, "bytes": expected, "status": "EXISTS"}
    headers = {"Range": f"bytes={start}-{end}", "User-Agent": "R6A1-open-data-intake/1.0"}
    for attempt in range(8):
        try:
            with requests.get(args.url, headers=headers, stream=True, timeout=(30, 300)) as response:
                response.raise_for_status()
                if response.status_code != 206:
                    raise RuntimeError(f"expected HTTP 206; got {response.status_code}")
                with path.open("wb") as handle:
                    for block in response.iter_content(512 * 1024):
                        if block:
                            handle.write(block)
            if path.stat().st_size != expected:
                raise RuntimeError(f"{path.stat().st_size} != {expected}")
            print(f"PART_OK {idx} {expected}", flush=True)
            return {"part": idx, "bytes": expected, "status": "DOWNLOADED"}
        except Exception:
            path.unlink(missing_ok=True)
            if attempt == 7:
                raise
            time.sleep(2 ** min(attempt, 5))


with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
    results = list(pool.map(fetch, parts))

with dest.open("wb") as out:
    for idx, _, _ in parts:
        with (part_dir / f"part_{idx:04d}.bin").open("rb") as handle:
            for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
                out.write(block)
if dest.stat().st_size != args.bytes:
    raise RuntimeError("assembled byte mismatch")
h = hashlib.sha256()
with dest.open("rb") as handle:
    for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
        h.update(block)
audit = {"url": args.url, "path": str(dest), "bytes": dest.stat().st_size, "sha256": h.hexdigest(), "parts": results, "status": "PASS"}
(dest.with_name(dest.name + ".download_audit.json")).write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in audit.items() if k != "parts"}, indent=2), flush=True)
