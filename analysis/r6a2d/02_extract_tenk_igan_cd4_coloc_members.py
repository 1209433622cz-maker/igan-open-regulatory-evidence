#!/usr/bin/env python3
"""Range-extract frozen IgAN/CD4 chr10 members from the TenK10K coloc ZIP.

The full archive is not downloaded.  The script fetches and parses the ZIP
central directory, then downloads only the compressed byte ranges of the two
prespecified chr10 NK members.  Each HTTP range has retries; member CRC32,
uncompressed length, and local SHA-256 are verified.
"""
from __future__ import annotations

import binascii
import concurrent.futures
import hashlib
import json
import os
import struct
import time
import zlib
from pathlib import Path

import requests


ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
URL = "https://zenodo.org/api/records/18221260/files/coloc_100kb.zip/content"
ARCHIVE_BYTES = 626_505_208
OFFICIAL_MD5 = "c627f1c4bc47706e331039d1e9e6e7d1"
TAILS = [
    "DiseaseTraits/kiryluk_IgAN/CD4_Naive/chr10.csv",
    "DiseaseTraits/kiryluk_IgAN/CD4_TCM/chr10.csv",
    "DiseaseTraits/kiryluk_IgAN/Treg/chr10.csv",
]
OUT = ROOT / "1_data/qtl/TenK10K/R6A2D_REEP3_precomputed_coloc"
OUT.mkdir(parents=True, exist_ok=True)


def fetch(start: int, end: int) -> bytes:
    expected = end - start + 1
    for attempt in range(10):
        try:
            response = requests.get(
                URL,
                headers={"Range": f"bytes={start}-{end}", "User-Agent": "R6A2D-targeted-range/1.0"},
                timeout=(30, 180),
            )
            response.raise_for_status()
            data = response.content
            if response.status_code != 206 or len(data) != expected:
                raise RuntimeError(f"range {start}-{end}: HTTP {response.status_code}, {len(data)}/{expected}")
            return data
        except Exception:
            if attempt == 9:
                raise
            time.sleep(min(2 ** attempt, 30))
    raise AssertionError("unreachable")


tail_start = max(0, ARCHIVE_BYTES - 131_072)
tail = fetch(tail_start, ARCHIVE_BYTES - 1)
eocd_pos = tail.rfind(b"PK\x05\x06")
if eocd_pos < 0:
    raise RuntimeError("EOCD not found")
eocd = tail[eocd_pos : eocd_pos + 22]
(_, disk, cd_disk, disk_entries, entries, cd_size, cd_offset, comment_len) = struct.unpack("<4s4H2IH", eocd)
if disk != 0 or cd_disk != 0 or entries != disk_entries:
    raise RuntimeError("multi-disk or Zip64 archive is outside frozen parser scope")

chunk_size = 1_048_576
ranges = [(s, min(s + chunk_size - 1, cd_offset + cd_size - 1)) for s in range(cd_offset, cd_offset + cd_size, chunk_size)]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    central = b"".join(pool.map(lambda x: fetch(*x), ranges))
if len(central) != cd_size:
    raise RuntimeError("central directory length mismatch")

records = []
pos = 0
while pos < len(central):
    if central[pos : pos + 4] != b"PK\x01\x02":
        raise RuntimeError(f"central directory signature mismatch at {pos}")
    fields = struct.unpack("<4s6H3I5H2I", central[pos : pos + 46])
    flag, method, crc32, compressed, uncompressed = fields[3], fields[4], fields[7], fields[8], fields[9]
    fn_len, extra_len, comment_len = fields[10], fields[11], fields[12]
    local_offset = fields[16]
    raw_name = central[pos + 46 : pos + 46 + fn_len]
    name = raw_name.decode("utf-8" if flag & 0x800 else "cp437")
    records.append(
        {
            "name": name,
            "method": method,
            "crc32": crc32,
            "compressed": compressed,
            "uncompressed": uncompressed,
            "local_offset": local_offset,
        }
    )
    pos += 46 + fn_len + extra_len + comment_len
if len(records) != entries:
    raise RuntimeError(f"central directory records {len(records)} != EOCD {entries}")

manifest = []
for tail_name in TAILS:
    hits = [x for x in records if x["name"].endswith(tail_name)]
    if len(hits) != 1:
        raise RuntimeError(f"target {tail_name}: {len(hits)} matches")
    record = hits[0]
    header = fetch(record["local_offset"], record["local_offset"] + 29)
    local = struct.unpack("<4s5H3I2H", header)
    if local[0] != b"PK\x03\x04":
        raise RuntimeError("local header signature mismatch")
    fn_len, extra_len = local[9], local[10]
    data_start = record["local_offset"] + 30 + fn_len + extra_len
    data_end = data_start + record["compressed"] - 1
    compressed = fetch(data_start, data_end) if record["compressed"] else b""
    if record["method"] == 0:
        data = compressed
    elif record["method"] == 8:
        data = zlib.decompress(compressed, -15)
    else:
        raise RuntimeError(f"unsupported compression method {record['method']}")
    if len(data) != record["uncompressed"]:
        raise RuntimeError("uncompressed length mismatch")
    actual_crc = binascii.crc32(data) & 0xFFFFFFFF
    if actual_crc != record["crc32"]:
        raise RuntimeError("member CRC32 mismatch")
    cell = tail_name.split("/")[-2]
    path = OUT / f"{cell}_chr10.csv"
    path.write_bytes(data)
    manifest.append(
        {
            "archive_url": URL,
            "official_archive_bytes": ARCHIVE_BYTES,
            "official_archive_md5_not_locally_recomputed": OFFICIAL_MD5,
            "central_directory_entries": entries,
            "member": record["name"],
            "member_compressed_bytes": record["compressed"],
            "member_uncompressed_bytes": record["uncompressed"],
            "member_crc32": f"{record['crc32']:08x}",
            "local_path": str(path),
            "local_sha256": hashlib.sha256(data).hexdigest(),
            "range_member_gate": "PASS",
        }
    )

(OUT / "R6A2D_TenK_precomputed_coloc_member_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(manifest, indent=2, ensure_ascii=False))
