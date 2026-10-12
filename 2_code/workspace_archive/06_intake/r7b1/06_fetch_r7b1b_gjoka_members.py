#!/usr/bin/env python3
"""Range-fetch only the exact 50 GJOKA members required by R7B1B."""
from __future__ import annotations

import hashlib
import json
import os
import zlib
from pathlib import Path

import pandas as pd
from remotezip import RemoteZip


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
REQUIRED = ROOT / "3_results/00_audit/R7B1B/R7B1B_required_GJOKA_members.tsv"
OUT = ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B"
AUDIT = ROOT / "3_results/00_audit/R7B1B"
URL = "https://www.staff.ncl.ac.uk/heather.cordell/GJOKA_SUMSTATS.zip"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    required = pd.read_csv(REQUIRED, sep="\t").sort_values("member")
    if len(required) != 50:
        raise RuntimeError("required-member manifest is not exact 50 rows")
    receipts = []
    with RemoteZip(URL) as archive:
        remote = {info.filename: info for info in archive.infolist()}
        for row in required.itertuples(index=False):
            info = remote[str(row.member)]
            destination = OUT / Path(str(row.member)).name
            use_existing = False
            if destination.exists() and destination.stat().st_size == int(row.uncompressed_bytes):
                data = destination.read_bytes()
                use_existing = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}" == str(row.crc32)
            if not use_existing:
                data = archive.read(str(row.member))
                destination.write_bytes(data)
            crc = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
            if len(data) != int(row.uncompressed_bytes) or crc != str(row.crc32):
                raise RuntimeError(f"member identity failure: {row.member}")
            receipts.append(
                {
                    "locus_index": int(row.locus_index),
                    "member": str(row.member),
                    "local_path": str(destination.relative_to(ROOT)),
                    "bytes": len(data),
                    "crc32": crc,
                    "sha256": sha256_bytes(data),
                    "source": "EXISTING_VERIFIED" if use_existing else "REMOTE_RANGE_FETCH",
                }
            )
            print(f"MEMBER_OK {len(receipts)}/50 {row.member}", flush=True)
    receipt = pd.DataFrame(receipts).sort_values("member")
    receipt.to_csv(AUDIT / "R7B1B_GJOKA_member_receipts.tsv", sep="\t", index=False)
    state = {
        "schema": "R7B1B_GJOKA_INTAKE_1.0",
        "status": "PASS" if len(receipt) == 50 else "FAIL",
        "members": len(receipt),
        "loci": int(receipt["locus_index"].nunique()),
        "local_uncompressed_bytes": int(receipt["bytes"].sum()),
        "url": URL,
    }
    (AUDIT / "R7B1B_GJOKA_intake_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2), flush=True)


if __name__ == "__main__":
    main()
