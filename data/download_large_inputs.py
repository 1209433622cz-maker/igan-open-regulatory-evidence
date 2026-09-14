#!/usr/bin/env python3
"""Download selected public inputs with resume, byte count and checksum gates."""

from __future__ import annotations
import argparse
import csv
import hashlib
import os
from pathlib import Path
import requests


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def download(url: str, destination: Path, expected_bytes: int) -> None:
    part = destination.with_suffix(destination.suffix + ".part")
    have = part.stat().st_size if part.exists() else 0
    headers = {"Accept-Encoding": "identity"}
    if have:
        headers["Range"] = f"bytes={have}-"
    with requests.get(url, headers=headers, stream=True, timeout=(30, 300)) as response:
        if have and response.status_code != 206:
            have = 0
            mode = "wb"
        else:
            response.raise_for_status()
            mode = "ab" if have else "wb"
        with part.open(mode) as output:
            for block in response.iter_content(8 * 1024 * 1024):
                if block:
                    output.write(block)
    if part.stat().st_size != expected_bytes:
        raise RuntimeError(f"byte mismatch for {destination.name}: {part.stat().st_size} != {expected_bytes}")
    part.replace(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="*", help="Manifest IDs; omit to download every row")
    parser.add_argument("--root", default=os.environ.get("IGAN_PROJECT_ROOT", str(Path.cwd())))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest = Path(__file__).with_name("LARGE_DATA_MANIFEST.tsv")
    with manifest.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    selected = [row for row in rows if not args.ids or row["id"] in set(args.ids)]
    unknown = set(args.ids or []) - {row["id"] for row in rows}
    if unknown:
        raise SystemExit(f"Unknown IDs: {sorted(unknown)}")
    for row in selected:
        destination = root / row["expected_relative_path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        algorithm = "md5" if row["checksum_type"].startswith("md5") else "sha256"
        expected_hash = row["checksum"].strip().lower()
        expected_bytes = int(row["expected_bytes"])
        if destination.exists() and destination.stat().st_size == expected_bytes and digest(destination, algorithm) == expected_hash:
            print(f"PASS_EXISTING\t{row['id']}\t{destination}")
            continue
        print(f"DOWNLOAD\t{row['id']}\t{expected_bytes}\t{destination}")
        download(row["url"], destination, expected_bytes)
        actual = digest(destination, algorithm)
        if actual != expected_hash:
            raise RuntimeError(f"checksum mismatch for {row['id']}: {actual} != {expected_hash}")
        print(f"PASS_DOWNLOADED\t{row['id']}\t{actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

