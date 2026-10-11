"""Resumable multi-connection HTTP byte-range downloader for immutable public files."""
from __future__ import annotations

import argparse
import os
import shutil
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def remote_size(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as response:
        if response.headers.get("Accept-Ranges", "").lower() != "bytes":
            raise RuntimeError("Server does not advertise byte-range support")
        return int(response.headers["Content-Length"])


def fetch_range(url: str, path: Path, start: int, end: int, retries: int = 10) -> None:
    expected = end - start + 1
    existing = path.stat().st_size if path.exists() else 0
    if existing == expected:
        return
    if existing > expected:
        path.unlink()
        existing = 0
    for attempt in range(retries):
        request_start = start + existing
        req = urllib.request.Request(url, headers={"Range": f"bytes={request_start}-{end}"})
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                if response.status != 206:
                    raise RuntimeError(f"Expected HTTP 206, received {response.status}")
                mode = "ab" if existing else "wb"
                with path.open(mode) as handle:
                    shutil.copyfileobj(response, handle, length=1024 * 1024)
            existing = path.stat().st_size
            if existing == expected:
                return
            raise RuntimeError(f"Range size {existing} != {expected}")
        except Exception:
            if attempt + 1 == retries:
                raise
            time.sleep(min(30, 2 ** attempt))
            existing = path.stat().st_size if path.exists() else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("destination")
    parser.add_argument("--connections", type=int, default=8)
    args = parser.parse_args()
    destination = Path(args.destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    total = remote_size(args.url)
    if destination.exists() and destination.stat().st_size == total:
        print(f"EXISTS {destination} bytes={total}")
        return
    prefix = Path(str(destination) + ".part")
    prefix_size = prefix.stat().st_size if prefix.exists() else 0
    if prefix_size > total:
        raise RuntimeError(f"Existing prefix exceeds remote file: {prefix_size}>{total}")
    remaining = total - prefix_size
    if remaining:
        n = max(1, min(args.connections, remaining))
        chunk = (remaining + n - 1) // n
        ranges = []
        for i in range(n):
            start = prefix_size + i * chunk
            if start >= total:
                break
            end = min(total - 1, start + chunk - 1)
            ranges.append((i, start, end, Path(f"{destination}.range{i:02d}")))
        with ThreadPoolExecutor(max_workers=len(ranges)) as executor:
            jobs = {executor.submit(fetch_range, args.url, p, s, e): (i, s, e, p)
                    for i, s, e, p in ranges}
            for job in as_completed(jobs):
                i, start, end, _ = jobs[job]
                job.result()
                print(f"RANGE_OK {i} bytes={end-start+1}", flush=True)
        assembling = Path(str(destination) + ".assembling")
        with assembling.open("wb") as output:
            if prefix_size:
                with prefix.open("rb") as source:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
            for _, _, _, part in sorted(ranges):
                with part.open("rb") as source:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
        if assembling.stat().st_size != total:
            raise RuntimeError("Assembled byte count mismatch")
        os.replace(assembling, destination)
        if prefix.exists():
            prefix.unlink()
        for _, _, _, part in ranges:
            part.unlink()
    print(f"DOWNLOAD_OK {destination} bytes={total}")


if __name__ == "__main__":
    main()
