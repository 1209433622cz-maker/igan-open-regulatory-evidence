#!/usr/bin/env python3
"""Resumably range-fetch the exact 94 GJOKA members frozen for R7B1B v2."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import zlib
from pathlib import Path

import pandas as pd
from remotezip import RemoteZip


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
REQUIRED = ROOT / "3_results/00_audit/R7B1B_v2/R7B1B_v2_required_94_GJOKA_members.tsv"
OUT = ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B_v2"
AUDIT = ROOT / "3_results/00_audit/R7B1B_v2"
URL = "https://www.staff.ncl.ac.uk/heather.cordell/GJOKA_SUMSTATS.zip"
REUSE_DIRS = [
    ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B_v2",
    ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B",
    ROOT / "1_data/study_inputs/PBC_GJOKA/R7A1B",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verified(path: Path, expected_bytes: int, expected_crc: str) -> bool:
    if not path.is_file() or path.stat().st_size != expected_bytes:
        return False
    crc = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            crc = zlib.crc32(block, crc)
    return f"{crc & 0xFFFFFFFF:08x}" == expected_crc.lower()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    required = pd.read_csv(REQUIRED, sep="\t").sort_values(["locus_index", "member"])
    if len(required) != 94 or required["locus_index"].nunique() != 47:
        raise RuntimeError("required manifest is not the exact 94-member/47-locus freeze")

    receipts: list[dict[str, object]] = []
    pending: list[object] = []
    for row in required.itertuples(index=False):
        filename = Path(str(row.member)).name
        destination = OUT / filename
        source = None
        for directory in REUSE_DIRS:
            candidate = directory / filename
            if verified(candidate, int(row.uncompressed_bytes), str(row.crc32)):
                source = candidate
                break
        if source is None:
            pending.append(row)
            continue
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        receipts.append(
            {
                "locus_index": int(row.locus_index),
                "member": str(row.member),
                "local_path": str(destination.relative_to(ROOT)),
                "bytes": destination.stat().st_size,
                "crc32": str(row.crc32).lower(),
                "sha256": sha256(destination),
                "source": "EXISTING_VERIFIED",
            }
        )
        print(f"MEMBER_OK {len(receipts)}/94 EXISTING {row.member}", flush=True)

    if pending:
        with RemoteZip(URL) as archive:
            remote = {info.filename: info for info in archive.infolist()}
            for row in pending:
                info = remote.get(str(row.member))
                if info is None:
                    raise RuntimeError(f"remote member missing: {row.member}")
                if info.file_size != int(row.uncompressed_bytes) or f"{info.CRC:08x}" != str(row.crc32).lower():
                    raise RuntimeError(f"remote central-directory identity mismatch: {row.member}")
                data = archive.read(str(row.member))
                crc = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
                if len(data) != int(row.uncompressed_bytes) or crc != str(row.crc32).lower():
                    raise RuntimeError(f"downloaded member identity failure: {row.member}")
                destination = OUT / Path(str(row.member)).name
                temporary = destination.with_suffix(destination.suffix + ".partial")
                temporary.write_bytes(data)
                temporary.replace(destination)
                receipts.append(
                    {
                        "locus_index": int(row.locus_index),
                        "member": str(row.member),
                        "local_path": str(destination.relative_to(ROOT)),
                        "bytes": len(data),
                        "crc32": crc,
                        "sha256": sha256(destination),
                        "source": "REMOTE_RANGE_FETCH",
                    }
                )
                pd.DataFrame(receipts).sort_values("member").to_csv(AUDIT / "R7B1B_v2_GJOKA_member_receipts.partial.tsv", sep="\t", index=False)
                print(f"MEMBER_OK {len(receipts)}/94 FETCHED {row.member}", flush=True)

    receipt = pd.DataFrame(receipts).sort_values("member")
    if len(receipt) != 94 or receipt["member"].nunique() != 94:
        raise RuntimeError("final receipt is not exact 94 members")
    receipt_path = AUDIT / "R7B1B_v2_GJOKA_member_receipts.tsv"
    receipt.to_csv(receipt_path, sep="\t", index=False)
    partial = AUDIT / "R7B1B_v2_GJOKA_member_receipts.partial.tsv"
    if partial.exists():
        partial.unlink()
    state = {
        "schema": "R7B1B_V2_GJOKA_INTAKE_1.0",
        "status": "PASS",
        "members": len(receipt),
        "loci": int(receipt["locus_index"].nunique()),
        "local_uncompressed_bytes": int(receipt["bytes"].sum()),
        "existing_reused": int((receipt["source"] == "EXISTING_VERIFIED").sum()),
        "remote_fetched": int((receipt["source"] == "REMOTE_RANGE_FETCH").sum()),
        "receipt_sha256": sha256(receipt_path),
        "url": URL,
    }
    (AUDIT / "R7B1B_v2_GJOKA_intake_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2), flush=True)


if __name__ == "__main__":
    main()
