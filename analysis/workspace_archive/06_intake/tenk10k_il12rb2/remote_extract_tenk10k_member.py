#!/usr/bin/env python3
"""Selectively read a large remote ZIP and extract one gene from named members.

The implementation uses HTTP byte ranges. It reads the ZIP central directory,
then transfers only the compressed bytes required for the selected members.
Reading every selected member to EOF makes Python's zipfile verify its CRC32.
It does not claim to verify the provider MD5 for the full remote ZIP.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import zipfile
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import requests


DEFAULT_URL = "https://zenodo.org/api/records/18221260/files/common_all_cis_pvalues_100kb.zip/content"
DEFAULT_SIZE = 16_559_137_990
DEFAULT_MD5 = "dd54714b2effb91160ac171ccb941534"
TARGETS = (b"ENSG00000081985", b"IL12RB2")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class HttpRangeFile(io.RawIOBase):
    def __init__(self, url: str, size: int, block_size: int, retries: int = 6):
        self.url = url
        self.size = size
        self.block_size = block_size
        self.retries = retries
        self.pos = 0
        self.cache: OrderedDict[int, bytes] = OrderedDict()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "CMM-R4A12FG4-remote-zip/1.0"})
        self.range_requests: list[dict] = []
        self.transferred_bytes = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new_pos = offset
        elif whence == io.SEEK_CUR:
            new_pos = self.pos + offset
        elif whence == io.SEEK_END:
            new_pos = self.size + offset
        else:
            raise ValueError(f"invalid whence: {whence}")
        if new_pos < 0:
            raise ValueError("negative seek position")
        self.pos = new_pos
        return self.pos

    def _fetch(self, block_index: int) -> bytes:
        if block_index in self.cache:
            data = self.cache.pop(block_index)
            self.cache[block_index] = data
            return data
        start = block_index * self.block_size
        end = min(self.size - 1, start + self.block_size - 1)
        last_error = None
        for attempt in range(1, self.retries + 1):
            response = None
            try:
                response = self.session.get(
                    self.url,
                    headers={"Range": f"bytes={start}-{end}"},
                    timeout=(30, 180),
                    stream=True,
                )
                if response.status_code != 206:
                    raise RuntimeError(f"expected HTTP 206, got {response.status_code}")
                content_range = response.headers.get("Content-Range", "")
                expected_prefix = f"bytes {start}-{end}/{self.size}"
                if content_range != expected_prefix:
                    raise RuntimeError(f"Content-Range mismatch: {content_range!r} != {expected_prefix!r}")
                data = response.content
                if len(data) != end - start + 1:
                    raise RuntimeError(f"range length mismatch: {len(data)}")
                self.range_requests.append(
                    {"start": start, "end": end, "bytes": len(data), "attempt": attempt}
                )
                self.transferred_bytes += len(data)
                self.cache[block_index] = data
                while len(self.cache) > 2:
                    self.cache.popitem(last=False)
                if self.transferred_bytes // (128 * 1024 * 1024) != (
                    self.transferred_bytes - len(data)
                ) // (128 * 1024 * 1024):
                    print(
                        f"remote_transfer={self.transferred_bytes / (1024**2):.1f} MiB "
                        f"requests={len(self.range_requests)}",
                        flush=True,
                    )
                return data
            except Exception as exc:
                last_error = exc
                retry_after = 2 ** (attempt - 1)
                if response is not None:
                    try:
                        retry_after = min(60, max(retry_after, int(response.headers.get("Retry-After", 0))))
                    except ValueError:
                        pass
                    response.close()
                if attempt < self.retries:
                    time.sleep(retry_after)
        raise RuntimeError(f"range fetch failed after {self.retries} attempts: {last_error}")

    def read(self, size: int = -1) -> bytes:
        if self.pos >= self.size:
            return b""
        if size < 0:
            remaining = self.size - self.pos
            if remaining > self.block_size:
                raise RuntimeError("refusing an unbounded remote read larger than one block")
            size = remaining
        size = min(size, self.size - self.pos)
        output = bytearray()
        while size > 0:
            block_index = self.pos // self.block_size
            block_start = block_index * self.block_size
            block = self._fetch(block_index)
            within = self.pos - block_start
            take = min(size, len(block) - within)
            if take <= 0:
                raise RuntimeError("range block did not cover requested position")
            output.extend(block[within : within + take])
            self.pos += take
            size -= take
        return bytes(output)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--remote-size", type=int, default=DEFAULT_SIZE)
    parser.add_argument("--provider-md5", default=DEFAULT_MD5)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--cells", nargs="+", default=["NK"])
    parser.add_argument("--block-mib", type=int, default=32)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    remote = HttpRangeFile(args.url, args.remote_size, args.block_mib * 1024 * 1024)
    started = time.monotonic()
    receipt = {
        "schema_version": "CMM_TENK10K_REMOTE_ZIP_GENE_EXTRACT_1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "record": "https://zenodo.org/records/18221260",
            "url": args.url,
            "remote_size": args.remote_size,
            "provider_md5": args.provider_md5,
            "provider_md5_verification": "NOT_RUN_FULL_OBJECT_NOT_DOWNLOADED",
        },
        "target": {"gene_id": "ENSG00000081985", "symbol": "IL12RB2"},
        "members": [],
    }
    try:
        with zipfile.ZipFile(remote) as archive:
            infos = {info.filename: info for info in archive.infolist()}
            receipt["zip_inventory"] = {
                "member_count": len(infos),
                "central_directory_read": True,
            }
            for cell in args.cells:
                expected = f"{cell}_common_all_cis_raw_pvalues.tsv"
                matches = [name for name in infos if name == expected or name.endswith("/" + expected)]
                if len(matches) != 1:
                    receipt["members"].append(
                        {"celltype": cell, "status": "HOLD_MEMBER_NOT_UNIQUE", "matches": matches}
                    )
                    continue
                name = matches[0]
                info = infos[name]
                output = args.outdir / f"{cell}_IL12RB2_full_variant_eqtl.tsv"
                partial = output.with_name(output.name + ".part")
                if output.exists() or partial.exists():
                    raise FileExistsError(f"refusing to overwrite output or partial file: {output}")
                rows = 0
                malformed = 0
                header_text = None
                with archive.open(info) as source, partial.open("wb") as target:
                    header = source.readline().rstrip(b"\r\n")
                    header_text = header.decode("utf-8-sig")
                    header_fields = header_text.split("\t")
                    target.write((header_text + "\tsource_zip_member\tsource_line\n").encode("utf-8"))
                    for source_line, line in enumerate(source, start=2):
                        if any(token in line for token in TARGETS):
                            clean = line.rstrip(b"\r\n")
                            if len(clean.split(b"\t")) != len(header_fields):
                                malformed += 1
                                continue
                            target.write(clean + b"\t" + name.encode("utf-8") + b"\t" + str(source_line).encode("ascii") + b"\n")
                            rows += 1
                if malformed:
                    raise RuntimeError(f"{name}: {malformed} matched rows were malformed")
                partial.replace(output)
                receipt["members"].append(
                    {
                        "celltype": cell,
                        "status": "PASS_MEMBER_CRC_AND_TARGET_EXTRACT",
                        "member": name,
                        "member_uncompressed_bytes": info.file_size,
                        "member_compressed_bytes": info.compress_size,
                        "member_crc32": f"{info.CRC:08x}",
                        "member_crc_verification": "PASS_READ_TO_EOF",
                        "header": header_text,
                        "target_rows": rows,
                        "output": str(output),
                        "output_bytes": output.stat().st_size,
                        "output_sha256": file_sha256(output),
                    }
                )
    finally:
        receipt["transfer"] = {
            "block_mib": args.block_mib,
            "range_request_count": len(remote.range_requests),
            "range_bytes_transferred": remote.transferred_bytes,
            "full_remote_object_downloaded": False,
            "ranges": remote.range_requests,
        }
        receipt["elapsed_seconds"] = time.monotonic() - started
        statuses = [item["status"] for item in receipt["members"]]
        receipt["status"] = (
            "PASS_ALL_SELECTED_MEMBERS" if statuses and all(s.startswith("PASS") for s in statuses)
            else "HOLD_OR_INCOMPLETE"
        )
        receipt_path = args.outdir / "IL12RB2_remote_extract_receipt.json"
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": receipt["status"],
            "members": receipt["members"],
            "range_bytes_transferred": remote.transferred_bytes,
            "receipt": str(receipt_path),
        }, ensure_ascii=False, indent=2), flush=True)
    return 0 if receipt["status"] == "PASS_ALL_SELECTED_MEMBERS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
