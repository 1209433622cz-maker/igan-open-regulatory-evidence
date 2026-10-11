#!/usr/bin/env python3
"""Resume-safe selective download and extraction of TenK10K NK IL12RB2 eQTLs.

Only the compressed bytes of ``NK_common_all_cis_raw_pvalues.tsv`` are fetched
from the 16.6 GB Zenodo ZIP.  Range chunks are written to ``.part`` files and
atomically renamed.  The complete DEFLATE stream, uncompressed byte count, and
ZIP member CRC32 are verified before the IL12RB2 extract is promoted.

This establishes member-level integrity.  It intentionally does not claim the
provider MD5 of the full 16.6 GB archive, because the other 27 members are not
downloaded.
"""

from __future__ import annotations

import argparse
import binascii
import concurrent.futures
import csv
import hashlib
import json
import math
import os
import shutil
import struct
import sys
import tempfile
import threading
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

import requests


SOURCE_RECORD = "https://zenodo.org/records/18221260"
SOURCE_URL = "https://zenodo.org/api/records/18221260/files/common_all_cis_pvalues_100kb.zip/content"
ARCHIVE_NAME = "common_all_cis_pvalues_100kb.zip"
ARCHIVE_SIZE = 16_559_137_990
ARCHIVE_PROVIDER_MD5 = "dd54714b2effb91160ac171ccb941534"

MEMBER_NAME = "NK_common_all_cis_raw_pvalues.tsv"
MEMBER_LOCAL_HEADER_OFFSET = 11_749_190_239
MEMBER_DATA_OFFSET = 11_749_190_330
MEMBER_COMPRESSED_SIZE = 556_881_415
MEMBER_UNCOMPRESSED_SIZE = 2_272_841_254
MEMBER_CRC32 = 0x25F9B199
MEMBER_COMPRESSION_METHOD = 8

TARGET_GENE_ID = "ENSG00000081985"
TARGET_GENE_SYMBOL = "IL12RB2"
REQUIRED_FIELDS = {
    "CHR",
    "POS",
    "MarkerID",
    "Allele1",
    "Allele2",
    "AF_Allele2",
    "BETA",
    "SE",
    "p.value",
    "N",
    "gene",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def chunk_path(cache: Path, index: int) -> Path:
    return cache / f"chunk_{index:04d}.bin"


def validate_local_header(blob: bytes) -> dict:
    if len(blob) != MEMBER_DATA_OFFSET - MEMBER_LOCAL_HEADER_OFFSET:
        raise RuntimeError("local-header probe length mismatch")
    if blob[:4] != b"PK\x03\x04":
        raise RuntimeError("ZIP local-header signature mismatch")
    (
        _signature,
        version_needed,
        flags,
        method,
        _mtime,
        _mdate,
        crc32,
        compressed_size,
        uncompressed_size,
        filename_length,
        extra_length,
    ) = struct.unpack_from("<IHHHHHIIIHH", blob, 0)
    name = blob[30 : 30 + filename_length].decode("utf-8" if flags & 0x800 else "cp437")
    expected = {
        "name": MEMBER_NAME,
        "method": MEMBER_COMPRESSION_METHOD,
        "crc32": MEMBER_CRC32,
        "compressed_size": MEMBER_COMPRESSED_SIZE,
        "uncompressed_size": MEMBER_UNCOMPRESSED_SIZE,
    }
    observed = {
        "name": name,
        "method": method,
        "crc32": crc32,
        "compressed_size": compressed_size,
        "uncompressed_size": uncompressed_size,
    }
    if observed != expected:
        raise RuntimeError(f"local-header metadata mismatch: {observed!r}")
    if 30 + filename_length + extra_length != len(blob):
        raise RuntimeError("local-header data offset mismatch")
    return {
        "member_name": name,
        "version_needed": version_needed,
        "flag_bits": flags,
        "compression_method": method,
        "crc32": f"{crc32:08x}",
        "compressed_size": compressed_size,
        "uncompressed_size": uncompressed_size,
        "data_offset": MEMBER_DATA_OFFSET,
    }


def fetch_range(url: str, start: int, end: int, destination: Path, retries: int) -> dict:
    expected_bytes = end - start + 1
    partial = destination.with_name(destination.name + ".part")
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            if partial.exists():
                partial.unlink()
            started = time.monotonic()
            with requests.get(
                url,
                headers={
                    "Range": f"bytes={start}-{end}",
                    "Accept-Encoding": "identity",
                    "User-Agent": "CMM-R4A12FG4-selective-member/2.0",
                },
                timeout=(30, 600),
                stream=True,
            ) as response:
                if response.status_code != 206:
                    raise RuntimeError(f"expected HTTP 206, got {response.status_code}")
                expected_range = f"bytes {start}-{end}/{ARCHIVE_SIZE}"
                if response.headers.get("Content-Range") != expected_range:
                    raise RuntimeError(
                        f"Content-Range mismatch: {response.headers.get('Content-Range')!r}"
                    )
                digest = hashlib.sha256()
                observed = 0
                with partial.open("wb") as target:
                    for block in response.iter_content(chunk_size=1024 * 1024):
                        if not block:
                            continue
                        target.write(block)
                        digest.update(block)
                        observed += len(block)
            if observed != expected_bytes:
                raise RuntimeError(f"range length mismatch: {observed} != {expected_bytes}")
            os.replace(partial, destination)
            return {
                "status": "DOWNLOADED",
                "start": start,
                "end": end,
                "bytes": observed,
                "sha256": digest.hexdigest(),
                "attempt": attempt,
                "seconds": round(time.monotonic() - started, 3),
            }
        except Exception as error:  # keep exact error for the receipt
            last_error = error
            if partial.exists():
                partial.unlink()
            if attempt < retries:
                time.sleep(min(60, 2 ** (attempt - 1)))
    raise RuntimeError(f"range {start}-{end} failed after {retries} attempts: {last_error}")


def download_member_chunks(
    *, url: str, cache: Path, chunk_bytes: int, workers: int, retries: int, manifest_path: Path
) -> tuple[list[Path], dict]:
    cache.mkdir(parents=True, exist_ok=True)
    chunk_count = math.ceil(MEMBER_COMPRESSED_SIZE / chunk_bytes)
    lock = threading.Lock()
    chunks: list[dict | None] = [None] * chunk_count
    pending: list[tuple[int, int, int, Path]] = []
    reused_bytes = 0
    for index in range(chunk_count):
        relative_start = index * chunk_bytes
        length = min(chunk_bytes, MEMBER_COMPRESSED_SIZE - relative_start)
        start = MEMBER_DATA_OFFSET + relative_start
        end = start + length - 1
        destination = chunk_path(cache, index)
        if destination.exists() and destination.stat().st_size == length:
            item = {
                "status": "REUSED_BY_EXACT_SIZE",
                "start": start,
                "end": end,
                "bytes": length,
                "sha256": sha256_file(destination),
            }
            chunks[index] = item
            reused_bytes += length
        else:
            if destination.exists():
                destination.unlink()
            pending.append((index, start, end, destination))

    started = time.monotonic()

    def task(spec: tuple[int, int, int, Path]):
        index, start, end, destination = spec
        result = fetch_range(url, start, end, destination, retries)
        result["index"] = index
        return index, result

    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(task, spec): spec[0] for spec in pending}
            completed = sum(item is not None for item in chunks)
            for future in concurrent.futures.as_completed(futures):
                index, result = future.result()
                with lock:
                    chunks[index] = result
                    completed += 1
                    atomic_json(
                        manifest_path,
                        {
                            "schema_version": "CMM_TENK10K_MEMBER_CHUNKS_1.0",
                            "source_url": url,
                            "member": MEMBER_NAME,
                            "member_data_offset": MEMBER_DATA_OFFSET,
                            "member_compressed_size": MEMBER_COMPRESSED_SIZE,
                            "chunk_bytes": chunk_bytes,
                            "chunk_count": chunk_count,
                            "completed_chunks": completed,
                            "chunks": chunks,
                        },
                    )
                    print(
                        f"chunks={completed}/{chunk_count} "
                        f"downloaded_or_reused={sum(x['bytes'] for x in chunks if x) / (1024**2):.1f} MiB",
                        flush=True,
                    )
    assert all(item is not None for item in chunks)
    result = {
        "chunk_bytes": chunk_bytes,
        "chunk_count": chunk_count,
        "worker_count": workers,
        "reused_bytes": reused_bytes,
        "network_bytes_this_run": sum(
            item["bytes"] for item in chunks if item and item["status"] == "DOWNLOADED"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "chunks_manifest": str(manifest_path),
        "chunks": chunks,
    }
    atomic_json(manifest_path, {"schema_version": "CMM_TENK10K_MEMBER_CHUNKS_1.0", **result})
    return [chunk_path(cache, index) for index in range(chunk_count)], result


def extract_target(chunks: list[Path], output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + ".part")
    if partial.exists():
        partial.unlink()
    decompressor = zlib.decompressobj(-15)
    crc = 0
    uncompressed_bytes = 0
    source_lines = 0
    target_rows = 0
    malformed_rows = 0
    header: list[str] | None = None
    gene_index: int | None = None
    buffer = b""

    with partial.open("wb") as target:
        for path in chunks:
            data = decompressor.decompress(path.read_bytes())
            crc = binascii.crc32(data, crc)
            uncompressed_bytes += len(data)
            buffer += data
            complete = buffer.split(b"\n")
            buffer = complete.pop()
            for raw_line in complete:
                source_lines += 1
                raw_line = raw_line.rstrip(b"\r")
                if header is None:
                    header = raw_line.decode("utf-8-sig").split("\t")
                    missing = sorted(REQUIRED_FIELDS.difference(header))
                    if missing:
                        raise RuntimeError(f"required fields absent: {missing}")
                    gene_index = header.index("gene")
                    target.write(
                        ("\t".join(header) + "\tsource_zip_member\tsource_line\n").encode("utf-8")
                    )
                    continue
                fields = raw_line.split(b"\t")
                if len(fields) != len(header):
                    malformed_rows += 1
                    continue
                assert gene_index is not None
                if fields[gene_index].decode("utf-8", "replace") == TARGET_GENE_ID:
                    target.write(
                        raw_line
                        + b"\t"
                        + MEMBER_NAME.encode("utf-8")
                        + b"\t"
                        + str(source_lines).encode("ascii")
                        + b"\n"
                    )
                    target_rows += 1
        final = decompressor.flush()
        crc = binascii.crc32(final, crc)
        uncompressed_bytes += len(final)
        buffer += final
        if buffer:
            source_lines += 1
            raw_line = buffer.rstrip(b"\r")
            if header is None:
                raise RuntimeError("member contained no header")
            fields = raw_line.split(b"\t")
            if len(fields) != len(header):
                malformed_rows += 1
            elif gene_index is not None and fields[gene_index].decode("utf-8", "replace") == TARGET_GENE_ID:
                target.write(
                    raw_line
                    + b"\t"
                    + MEMBER_NAME.encode("utf-8")
                    + b"\t"
                    + str(source_lines).encode("ascii")
                    + b"\n"
                )
                target_rows += 1

    if not decompressor.eof:
        raise RuntimeError("DEFLATE stream did not reach EOF")
    if decompressor.unused_data:
        raise RuntimeError("unexpected bytes after DEFLATE member stream")
    if uncompressed_bytes != MEMBER_UNCOMPRESSED_SIZE:
        raise RuntimeError(
            f"uncompressed size mismatch: {uncompressed_bytes} != {MEMBER_UNCOMPRESSED_SIZE}"
        )
    if crc & 0xFFFFFFFF != MEMBER_CRC32:
        raise RuntimeError(f"member CRC32 mismatch: {crc & 0xFFFFFFFF:08x} != {MEMBER_CRC32:08x}")
    if malformed_rows:
        raise RuntimeError(f"member contained {malformed_rows} malformed rows")
    if target_rows == 0:
        raise RuntimeError(f"no exact {TARGET_GENE_ID} rows were found")
    os.replace(partial, output)
    return {
        "status": "PASS_MEMBER_CRC_AND_EXACT_GENE_EXTRACT",
        "source_lines_including_header": source_lines,
        "target_rows": target_rows,
        "member_uncompressed_bytes_observed": uncompressed_bytes,
        "member_crc32_observed": f"{crc & 0xFFFFFFFF:08x}",
        "header": header,
        "output": str(output),
        "output_bytes": output.stat().st_size,
        "output_sha256": sha256_file(output),
    }


def run_self_test() -> int:
    rows = (
        "\tCHR\tPOS\tMarkerID\tAllele1\tAllele2\tAF_Allele2\tBETA\tSE\tp.value\tN\tgene\n"
        "0\t1\t1\t1:1:A:G\tA\tG\t0.1\t0.2\t0.1\t0.05\t100\tENSG00000000001\n"
        "1\t1\t2\t1:2:C:T\tC\tT\t0.2\t-0.3\t0.1\t0.003\t100\tENSG00000081985\n"
    ).encode()
    compressor = zlib.compressobj(level=6, wbits=-15)
    compressed = compressor.compress(rows) + compressor.flush()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        parts = []
        for index in range(0, len(compressed), 7):
            path = root / f"chunk_{index // 7:04d}.bin"
            path.write_bytes(compressed[index : index + 7])
            parts.append(path)
        # Exercise the streaming/filtering algorithm using test-specific metadata.
        decompressor = zlib.decompressobj(-15)
        rebuilt = b"".join(decompressor.decompress(p.read_bytes()) for p in parts) + decompressor.flush()
        if rebuilt != rows or not decompressor.eof:
            raise RuntimeError("self-test DEFLATE reconstruction failed")
        header, first, second = rebuilt.decode().splitlines()
        if TARGET_GENE_ID not in second or TARGET_GENE_ID in first or "BETA" not in header:
            raise RuntimeError("self-test exact-gene filtering assumptions failed")
    print("PASS_SELF_TEST")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--url", default=SOURCE_URL)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--chunk-mib", type=int, default=8)
    parser.add_argument("--retries", type=int, default=6)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.outdir is None:
        raise SystemExit("--outdir is required unless --self-test is used")
    if not 1 <= args.workers <= 12:
        raise SystemExit("--workers must be between 1 and 12")
    if not 1 <= args.chunk_mib <= 64:
        raise SystemExit("--chunk-mib must be between 1 and 64")
    args.outdir.mkdir(parents=True, exist_ok=True)
    cache = args.outdir / "cache" / "NK_common_all_cis_raw_pvalues"
    receipt_path = args.outdir / "TenK10K_NK_IL12RB2_selective_intake_receipt.json"
    chunks_manifest = cache / "chunks_manifest.json"
    output = args.outdir / "NK_IL12RB2_full_variant_eqtl.tsv"
    started = time.monotonic()
    receipt = {
        "schema_version": "CMM_TENK10K_SELECTIVE_MEMBER_INTAKE_2.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "source": {
            "record": SOURCE_RECORD,
            "url": args.url,
            "archive_name": ARCHIVE_NAME,
            "archive_size": ARCHIVE_SIZE,
            "provider_md5": ARCHIVE_PROVIDER_MD5,
            "provider_md5_verification": "NOT_RUN_SELECTIVE_MEMBER_ONLY",
        },
        "target": {"gene_id": TARGET_GENE_ID, "symbol": TARGET_GENE_SYMBOL, "celltype": "NK"},
    }
    atomic_json(receipt_path, receipt)
    try:
        header_path = cache / "local_header.bin"
        if not header_path.exists() or header_path.stat().st_size != MEMBER_DATA_OFFSET - MEMBER_LOCAL_HEADER_OFFSET:
            header_path.parent.mkdir(parents=True, exist_ok=True)
            fetch_range(
                args.url,
                MEMBER_LOCAL_HEADER_OFFSET,
                MEMBER_DATA_OFFSET - 1,
                header_path,
                args.retries,
            )
        receipt["member_header"] = validate_local_header(header_path.read_bytes())
        chunks, transfer = download_member_chunks(
            url=args.url,
            cache=cache,
            chunk_bytes=args.chunk_mib * 1024 * 1024,
            workers=args.workers,
            retries=args.retries,
            manifest_path=chunks_manifest,
        )
        receipt["transfer"] = transfer
        receipt["extract"] = extract_target(chunks, output)
        receipt["status"] = "PASS_SELECTIVE_MEMBER_INTAKE"
        return_code = 0
    except Exception as error:
        receipt["status"] = "HOLD_INCOMPLETE"
        receipt["error"] = f"{type(error).__name__}: {error}"
        return_code = 2
    finally:
        receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
        atomic_json(receipt_path, receipt)
        print(
            json.dumps(
                {
                    "status": receipt["status"],
                    "receipt": str(receipt_path),
                    "output": str(output) if output.exists() else None,
                    "error": receipt.get("error"),
                },
                ensure_ascii=False,
                indent=2,
            ),
            flush=True,
        )
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
