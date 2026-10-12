#!/usr/bin/env python3
"""Acquire FinnGen manifests and build a byte-level, no-GWAS-download plan.

This command downloads only the two public manifest TSVs (about 1.6 MB total),
selects the frozen SSc endpoints, and performs HTTP HEAD requests for each
summary object and its tabix index. It never downloads a GWAS object.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import re
import ssl
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_MANIFEST_COLUMNS = {
    "phenocode",
    "phenotype",
    "category",
    "num_cases",
    "num_controls",
    "path_bucket",
    "path_https",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download_small_file(url: str, destination: Path, retries: int = 4) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        temp_name: str | None = None
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "YR1-R4A12FG2-manifest-audit/1.0"},
            )
            with urllib.request.urlopen(request, timeout=90, context=ssl.create_default_context()) as response:
                fd, temp_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".tmp", dir=destination.parent)
                with os.fdopen(fd, "wb") as output:
                    while True:
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        output.write(block)
                headers = {key.lower(): value for key, value in response.headers.items()}
                status = response.status
            os.replace(temp_name, destination)
            temp_name = None
            return {
                "url": url,
                "http_status": status,
                "bytes": destination.stat().st_size,
                "sha256": sha256_file(destination),
                "etag": headers.get("etag", "").strip('"'),
                "last_modified": headers.get("last-modified", ""),
            }
        except Exception as exc:  # pragma: no cover - network-dependent path
            last_error = exc
            if temp_name and Path(temp_name).exists():
                Path(temp_name).unlink()
            if attempt < retries:
                time.sleep(attempt)
    raise RuntimeError(f"failed to download manifest after {retries} attempts: {url}: {last_error}")


def parse_manifest(path: Path, expected_endpoints: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        columns = reader.fieldnames or []
        missing = sorted(REQUIRED_MANIFEST_COLUMNS - set(columns))
        if missing:
            raise ValueError(f"{path.name}: missing manifest columns: {', '.join(missing)}")
        all_rows = list(reader)
    selected: list[dict[str, str]] = []
    for endpoint in expected_endpoints:
        matches = [row for row in all_rows if row["phenocode"] == endpoint]
        if len(matches) != 1:
            raise ValueError(f"{path.name}: expected exactly one row for {endpoint}; found {len(matches)}")
        row = matches[0]
        int(row["num_cases"])
        int(row["num_controls"])
        if not row["path_https"].startswith("https://storage.googleapis.com/finngen-public-data-"):
            raise ValueError(f"{path.name}: unexpected path_https for {endpoint}")
        selected.append(row)
    return selected, columns


def _parse_hash_headers(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        for part in value.split(","):
            if "=" in part:
                key, encoded = part.strip().split("=", 1)
                result[key.lower()] = encoded
    return result


def head_object(url: str, retries: int = 4) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url,
                method="HEAD",
                headers={"User-Agent": "YR1-R4A12FG2-object-head/1.0"},
            )
            with urllib.request.urlopen(request, timeout=60, context=ssl.create_default_context()) as response:
                hash_headers = _parse_hash_headers(response.headers.get_all("x-goog-hash", []))
                size_text = response.headers.get("x-goog-stored-content-length") or response.headers.get("content-length")
                return {
                    "http_status": response.status,
                    "content_length": int(size_text) if size_text else None,
                    "etag": response.headers.get("etag", "").strip('"'),
                    "provider_md5_base64": hash_headers.get("md5", ""),
                    "provider_crc32c_base64": hash_headers.get("crc32c", ""),
                    "last_modified": response.headers.get("last-modified", ""),
                    "accept_ranges": response.headers.get("accept-ranges", ""),
                    "content_type": response.headers.get("content-type", ""),
                }
        except Exception as exc:  # pragma: no cover - network-dependent path
            last_error = exc
            if attempt < retries:
                time.sleep(attempt)
    raise RuntimeError(f"HEAD failed after {retries} attempts: {url}: {last_error}")


def provider_md5_hex(encoded: str) -> str:
    if not encoded:
        return ""
    try:
        return base64.b64decode(encoded).hex()
    except Exception:
        return ""


def write_tsv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(receipt: dict[str, Any]) -> str:
    primary = [row for row in receipt["objects"] if row["endpoint"] == "M13_SYSTSLCE"]
    lines = [
        "# R4A12-FG2 FinnGen manifest 与对象 HEAD 验收",
        "",
        f"生成时间（UTC）：`{receipt['generated_at_utc']}`",
        "",
        f"状态：**{receipt['status']}**",
        "",
        "本次只下载两份公开 manifest，并对目标对象执行 HEAD；没有下载 GWAS 数据对象。",
        "",
        "## 关键纠偏",
        "",
        f"- R12 `M13_SYSTSLCE` public analysis manifest：cases = **{receipt['case_count_facts']['R12_M13_SYSTSLCE']}**。",
        f"- R13 `M13_SYSTSLCE` public analysis manifest：cases = **{receipt['case_count_facts']['R13_M13_SYSTSLCE']}**。",
        "- R12 的 public analysis N 必须使用 manifest 的 854，不能把 Risteys phenotype count 881 写入 GWAS analysis N。",
        "",
        "| Release | Endpoint | Manifest cases | Manifest controls |",
        "|---|---|---:|---:|",
    ]
    for row in receipt["target_manifest_rows"]:
        lines.append(f"| {row['release']} | `{row['phenocode']}` | {row['num_cases']} | {row['num_controls']} |")
    lines.extend([
        "",
        "## 主对象",
        "",
        "| Release | Object | HTTP | Bytes | Provider MD5 | State |",
        "|---|---|---:|---:|---|---|",
    ])
    for row in primary:
        lines.append(
            f"| {row['release']} | {row['object_kind']} | {row['http_status']} | {row['content_length']} | "
            f"`{row['provider_md5_hex']}` | {row['download_state']} |"
        )
    lines.extend(
        [
            "",
            f"计划内全部 12 个对象总量：**{receipt['planned_total_bytes']:,} bytes**。",
            f"优先下载的 R13/R12 `M13_SYSTSLCE` summary + index：**{receipt['primary_total_bytes']:,} bytes**。",
            "",
            "## R12 sex-specific gate",
            "",
            f"- HTTPS probe：`{receipt['r12_sex_specific_gate']['https_probe_status']}`。",
            f"- 本机 Google Cloud active accounts：`{receipt['r12_sex_specific_gate']['active_gcloud_accounts']}`。",
            "- 该 gate 仍需 Green Library 授权后取得真实 drop-list 字节；当前不得推断 endpoint 可用。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    manifests_dir = args.data_root / "manifests"
    metadata_dir = args.data_root / "metadata"
    incoming_dir = args.data_root / "incoming"
    args.result_root.mkdir(parents=True, exist_ok=True)
    incoming_dir.mkdir(parents=True, exist_ok=True)

    manifest_receipts: dict[str, Any] = {}
    target_rows: list[dict[str, Any]] = []
    objects: list[dict[str, Any]] = []

    for release in ("R12", "R13"):
        manifest_path = manifests_dir / f"finngen_{release}_manifest.tsv"
        manifest_receipts[release] = download_small_file(config["manifest_urls"][release], manifest_path)
        selected, columns = parse_manifest(manifest_path, config["target_endpoints"])
        manifest_receipts[release]["local_path"] = str(manifest_path)
        manifest_receipts[release]["columns"] = columns
        for row in selected:
            selected_row = {"release": release, **row}
            target_rows.append(selected_row)
            for object_kind, url in (("summary", row["path_https"]), ("tabix_index", row["path_https"] + ".tbi")):
                head = head_object(url)
                if head["http_status"] != 200 or not head["content_length"]:
                    raise RuntimeError(f"object is not byte-ready: {url}: {head}")
                filename = url.rsplit("/", 1)[-1]
                priority = (
                    "P1_PRIMARY"
                    if row["phenocode"] == config["primary_endpoint"] and release == "R13"
                    else "P2_BRIDGE"
                    if row["phenocode"] == config["primary_endpoint"] and release == "R12"
                    else "P3_SENSITIVITY"
                )
                objects.append(
                    {
                        "release": release,
                        "release_role": config["release_roles"][release],
                        "endpoint": row["phenocode"],
                        "phenotype": row["phenotype"],
                        "manifest_num_cases": int(row["num_cases"]),
                        "manifest_num_controls": int(row["num_controls"]),
                        "object_kind": object_kind,
                        "priority": priority,
                        "url": url,
                        "local_path": str(incoming_dir / release / row["phenocode"] / filename),
                        **head,
                        "provider_md5_hex": provider_md5_hex(head["provider_md5_base64"]),
                        "download_state": "PLANNED_NOT_DOWNLOADED",
                    }
                )

    target_columns = ["release", *manifest_receipts["R12"]["columns"]]
    write_tsv(metadata_dir / "target_manifest_rows.tsv", target_rows, target_columns)
    object_columns = [
        "release",
        "release_role",
        "endpoint",
        "phenotype",
        "manifest_num_cases",
        "manifest_num_controls",
        "object_kind",
        "priority",
        "url",
        "local_path",
        "http_status",
        "content_length",
        "etag",
        "provider_md5_base64",
        "provider_md5_hex",
        "provider_crc32c_base64",
        "last_modified",
        "accept_ranges",
        "content_type",
        "download_state",
    ]
    write_tsv(metadata_dir / "object_inventory.tsv", objects, object_columns)
    write_tsv(metadata_dir / "download_plan.tsv", objects, object_columns)

    r12_row = next(row for row in target_rows if row["release"] == "R12" and row["phenocode"] == "M13_SYSTSLCE")
    r13_row = next(row for row in target_rows if row["release"] == "R13" and row["phenocode"] == "M13_SYSTSLCE")
    planned_total = sum(int(row["content_length"]) for row in objects)
    primary_total = sum(int(row["content_length"]) for row in objects if row["endpoint"] == config["primary_endpoint"])

    sex_probe_url = config["r12_sex_specific_drop_list"]["public_https_probe"]
    try:
        head_object(sex_probe_url, retries=1)
        sex_status = "HTTP_200_UNEXPECTED_PUBLIC_ACCESS"
    except Exception as exc:
        match = re.search(r"HTTP Error (\d+)", str(exc))
        sex_status = f"HTTP_{match.group(1)}" if match else f"UNAVAILABLE:{type(exc).__name__}"

    receipt = {
        "schema_version": "1.0",
        "gate": "R4A12-FG2_FG-A_PREFLIGHT",
        "generated_at_utc": utc_now(),
        "status": "PASS_PUBLIC_MANIFEST_AND_OBJECT_HEAD_READY_NO_GWAS_DOWNLOADED",
        "manifest_receipts": manifest_receipts,
        "target_endpoints": config["target_endpoints"],
        "case_count_facts": {
            "R12_M13_SYSTSLCE": int(r12_row["num_cases"]),
            "R13_M13_SYSTSLCE": int(r13_row["num_cases"]),
            "R12_risteys_phenotype_count_from_prior_report": 881,
            "R12_manifest_minus_risteys": int(r12_row["num_cases"]) - 881,
            "interpretation": "Use manifest num_cases as the analysis-file N; Risteys phenotype count is not interchangeable.",
        },
        "target_manifest_rows": [
            {
                "release": row["release"],
                "phenocode": row["phenocode"],
                "num_cases": int(row["num_cases"]),
                "num_controls": int(row["num_controls"]),
            }
            for row in target_rows
        ],
        "prior_report_risteys_counts_for_context_only": {
            "R12": {"M13_SYSTSLCE": 881, "SYSTSCLE_STRICT": 323, "CREST": 533},
            "R13": {"M13_SYSTSLCE": 883, "SYSTSCLE_STRICT": 320, "CREST": 546},
        },
        "r12_manifest_analysis_minus_prior_risteys": {
            endpoint: next(
                int(row["num_cases"])
                for row in target_rows
                if row["release"] == "R12" and row["phenocode"] == endpoint
            ) - context_count
            for endpoint, context_count in {"M13_SYSTSLCE": 881, "SYSTSCLE_STRICT": 323, "CREST": 533}.items()
        },
        "objects": objects,
        "planned_total_bytes": planned_total,
        "primary_total_bytes": primary_total,
        "r12_sex_specific_gate": {
            "gs_uri": config["r12_sex_specific_drop_list"]["gs_uri"],
            "https_probe_status": sex_status,
            "active_gcloud_accounts": [],
            "status": "HOLD_GREEN_LIBRARY_AUTH_REQUIRED",
        },
        "scientific_boundary": "No disease association, colocalization, SMR, fine-mapping, C1, or project GO/NO-GO status was computed or changed.",
    }
    receipt_path = args.result_root / "R4A12FG2_manifest_object_receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.result_root / "R4A12FG2_manifest_object_receipt.md").write_text(render_markdown(receipt), encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "objects": len(objects), "primary_total_bytes": primary_total, "receipt": str(receipt_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
