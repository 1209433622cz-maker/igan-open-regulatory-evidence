#!/usr/bin/env python3
"""Independently verify the R7C1 ZIP CRC and embedded manifest."""

import hashlib
import json
import zipfile
from pathlib import Path


ZIP = Path(r"H:\SCI2\YR1\6_release\R7C1_2026-10-11\CMM_R7C1_IL12RB2_ExternalValidation_ManuscriptFork_2026-10-11.zip")
ROOT = "CMM_R7C1_IL12RB2_ExternalValidation_ManuscriptFork_2026-10-11/"


def main() -> None:
    with zipfile.ZipFile(ZIP) as archive:
        rows = archive.read(ROOT + "checksums.sha256.tsv").decode("utf-8").splitlines()[1:]
        failures = []
        for row in rows:
            expected_hash, expected_bytes, relative = row.split("\t")
            payload = archive.read(ROOT + relative)
            if hashlib.sha256(payload).hexdigest() != expected_hash or len(payload) != int(expected_bytes):
                failures.append(relative)
        crc_member = archive.testzip()
    result = {
        "manifest_pass": len(rows) - len(failures),
        "manifest_fail": len(failures),
        "manifest_total": len(rows),
        "zip_crc": "PASS" if crc_member is None else f"FAIL:{crc_member}",
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    if failures or crc_member is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
