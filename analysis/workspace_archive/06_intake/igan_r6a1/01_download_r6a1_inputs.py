from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import requests


ROOT = Path(r"H:\SCI2\YR1")
TARGETS = [
    {
        "id": "igan_combined",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA_Summary/IgAN_Combined_metaanalysis.txt",
        "path": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis.txt",
        "expected_bytes": 492_016_732,
    },
    {
        "id": "igan_european",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA_Summary/IgAN_Combined_metaanalysis_European_only.txt",
        "path": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_European_only.txt",
        "expected_bytes": 164_526_659,
    },
    {
        "id": "igan_asian",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA_Summary/IgAN_Combined_metaanalysis_Asian_only.txt",
        "path": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_Asian_only.txt",
        "expected_bytes": 376_485_006,
    },
    {
        "id": "serum_iga_combined",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA/META.IGA.LEVELS.ALL.COMBINED.txt",
        "path": ROOT / "1_data/gwas/serum_IgA/Kiryluk2022/META.IGA.LEVELS.ALL.COMBINED.txt",
        "expected_bytes": 168_662_774,
    },
]


def hashes(path: Path) -> tuple[str, str]:
    md5 = hashlib.md5()
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            md5.update(block)
            sha.update(block)
    return md5.hexdigest(), sha.hexdigest()


def download(item: dict) -> dict:
    path = item["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.stat().st_size if path.exists() else 0
    if existing == item["expected_bytes"]:
        print(f"EXISTS {item['id']} {existing:,}", flush=True)
    else:
        if existing > item["expected_bytes"]:
            path.unlink()
            existing = 0
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) R6A1 scientific data intake",
            **({"Range": f"bytes={existing}-"} if existing else {}),
        }
        mode = "ab" if existing else "wb"
        with requests.get(item["url"], headers=headers, stream=True, timeout=(30, 300)) as response:
            response.raise_for_status()
            if existing and response.status_code != 206:
                existing = 0
                mode = "wb"
            with path.open(mode) as handle:
                downloaded = existing
                last = time.monotonic()
                for block in response.iter_content(4 * 1024 * 1024):
                    if not block:
                        continue
                    handle.write(block)
                    downloaded += len(block)
                    if time.monotonic() - last >= 10:
                        print(f"PROGRESS {item['id']} {downloaded:,}/{item['expected_bytes']:,}", flush=True)
                        last = time.monotonic()
        print(f"DOWNLOADED {item['id']} {path.stat().st_size:,}", flush=True)

    size = path.stat().st_size
    md5, sha256 = hashes(path)
    if size != item["expected_bytes"]:
        raise RuntimeError(f"byte mismatch for {item['id']}: {size} != {item['expected_bytes']}")
    return {
        **{k: str(v) if isinstance(v, Path) else v for k, v in item.items()},
        "actual_bytes": size,
        "md5": md5,
        "sha256": sha256,
        "byte_gate": "PASS",
        "official_checksum_available": False,
    }


results = [download(item) for item in TARGETS]
out = ROOT / "3_results/00_audit/R6A1/R6A1_download_byte_manifest.json"
out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"MANIFEST {out}", flush=True)
