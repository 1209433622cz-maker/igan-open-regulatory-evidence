#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("path", type=Path)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()

md5 = hashlib.md5()
sha256 = hashlib.sha256()
size = 0
with args.path.open("rb") as handle:
    for block in iter(lambda: handle.read(16 << 20), b""):
        size += len(block)
        md5.update(block)
        sha256.update(block)
value = {
    "path": str(args.path),
    "bytes": size,
    "md5": md5.hexdigest(),
    "sha256": sha256.hexdigest(),
}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
print(json.dumps(value, indent=2))
