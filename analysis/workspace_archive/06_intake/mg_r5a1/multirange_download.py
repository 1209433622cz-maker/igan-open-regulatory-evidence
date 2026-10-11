#!/usr/bin/env python3
"""Resume an HTTP download with parallel byte ranges and verify the final size.

The existing output, when present, is treated as a verified prefix. Temporary range
files are retained after failure so the command can be retried without losing work.
An external cryptographic checksum must still be checked after completion.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import pathlib
import subprocess
import sys


def ranges(start: int, stop: int, workers: int) -> list[tuple[int, int, int]]:
    remaining = stop - start + 1
    workers = max(1, min(workers, remaining))
    base, extra = divmod(remaining, workers)
    result = []
    cursor = start
    for index in range(workers):
        width = base + (1 if index < extra else 0)
        result.append((index, cursor, cursor + width - 1))
        cursor += width
    return result


def fetch(url: str, part: pathlib.Path, start: int, stop: int) -> tuple[pathlib.Path, int]:
    expected = stop - start + 1
    have = part.stat().st_size if part.exists() else 0
    if have > expected:
        part.unlink()
        have = 0
    if have == expected:
        return part, expected
    new_path = pathlib.Path(str(part) + ".new")
    transferred = new_path.stat().st_size if new_path.exists() else 0
    if have + transferred > expected:
        new_path.unlink()
        transferred = 0
    stalled_attempts = 0
    while have + transferred < expected:
        actual_start = start + have + transferred
        fragment = pathlib.Path(str(part) + ".fragment")
        if fragment.exists():
            fragment.unlink()
        command = [
            "curl.exe", "--location", "--fail", "--silent", "--show-error",
            "--retry", "5", "--retry-all-errors", "--retry-delay", "2",
            "--range", f"{actual_start}-{stop}", "--output", str(fragment), url,
        ]
        result = subprocess.run(command, check=False)
        received = fragment.stat().st_size if fragment.exists() else 0
        remaining = expected - have - transferred
        if received > remaining:
            raise RuntimeError(
                f"Range {actual_start}-{stop} returned {received} bytes; expected at most {remaining}. "
                "Server may have ignored Range."
            )
        if received:
            with new_path.open("ab") as destination, fragment.open("rb") as source:
                while block := source.read(8 * 1024 * 1024):
                    destination.write(block)
            fragment.unlink()
            transferred += received
            stalled_attempts = 0
        else:
            stalled_attempts += 1
        if result.returncode != 0 and stalled_attempts >= 3:
            raise RuntimeError(f"Range {actual_start}-{stop} stalled after three attempts")
    received = new_path.stat().st_size
    if received != expected - have:
        raise RuntimeError(f"Temporary range size mismatch: {new_path}")
    mode = "ab" if have else "wb"
    with part.open(mode) as destination, new_path.open("rb") as source:
        while block := source.read(8 * 1024 * 1024):
            destination.write(block)
    new_path.unlink()
    if part.stat().st_size != expected:
        raise RuntimeError(f"Part size mismatch: {part}")
    return part, expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--concurrency", type=int, default=None)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    prefix = args.output.stat().st_size if args.output.exists() else 0
    if prefix == args.size:
        print(f"COMPLETE\t{args.output}\t{args.size}", flush=True)
        return 0
    if prefix > args.size:
        raise RuntimeError(f"Existing output is larger than expected: {prefix}>{args.size}")

    jobs = ranges(prefix, args.size - 1, args.workers)
    print(
        f"START\t{args.output}\tprefix={prefix}\tremaining={args.size-prefix}"
        f"\tworkers={len(jobs)}",
        flush=True,
    )
    completed: dict[int, pathlib.Path] = {}
    max_parallel = args.concurrency or len(jobs)
    max_parallel = max(1, min(max_parallel, len(jobs)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as pool:
        future_map = {}
        for index, start, stop in jobs:
            part = pathlib.Path(f"{args.output}.part{index:02d}.{start}-{stop}")
            future = pool.submit(fetch, args.url, part, start, stop)
            future_map[future] = (index, start, stop)
        for future in concurrent.futures.as_completed(future_map):
            index, start, stop = future_map[future]
            part, size = future.result()
            completed[index] = part
            print(f"PART_OK\t{index}\t{start}-{stop}\t{size}", flush=True)

    with args.output.open("ab") as destination:
        for index, _start, _stop in jobs:
            part = completed[index]
            with part.open("rb") as source:
                while block := source.read(8 * 1024 * 1024):
                    destination.write(block)
            part.unlink()
    if args.output.stat().st_size != args.size:
        raise RuntimeError(f"Final size mismatch: {args.output.stat().st_size}!={args.size}")
    print(f"COMPLETE\t{args.output}\t{args.size}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
