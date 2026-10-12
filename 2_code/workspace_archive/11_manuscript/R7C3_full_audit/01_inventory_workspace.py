#!/usr/bin/env python3
"""Build a content-aware inventory of the complete YR1 workspace.

The inventory is intentionally local. It records sensitive/publication flags but
does not copy or publish source files. Git object internals are counted in the
directory totals and excluded from content parsing because they are repository
implementation data rather than research assets.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import stat
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11" / "inventory"

TEXT_EXT = {
    ".md", ".txt", ".tsv", ".csv", ".json", ".jsonl", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".conf", ".py", ".ps1", ".r", ".rmd",
    ".sh", ".bat", ".cmd", ".tex", ".bib", ".cff", ".html", ".htm",
    ".xml", ".sql", ".log", ".env.example", ".gitignore", ".gitattributes",
}
OFFICE_EXT = {".docx", ".xlsx", ".pptx", ".docm", ".xlsm", ".pptm"}
ARCHIVE_EXT = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".bz2", ".xz"}
DATA_EXT = {
    ".bed", ".bim", ".fam", ".vcf", ".bcf", ".pgen", ".pvar", ".psam",
    ".bam", ".bai", ".cram", ".crai", ".h5", ".h5ad", ".loom", ".mtx",
    ".parquet", ".feather", ".rds", ".rdata", ".npy", ".npz", ".zarr",
}
STAGE_RE = re.compile(r"(?i)(?:^|[^A-Z0-9])(R\d+[A-Z][A-Z0-9]*)(?:[^A-Z0-9]|$)")
STATUS_RE = re.compile(
    r"(?i)\b(PASS|FAIL|HOLD|GO|NO[-_ ]?GO|COMPLETE|FROZEN|READY|PENDING|"
    r"CONDITIONAL[-_ ]?GO|NOT[-_ ]?SUPPORTED|UNINFORMATIVE|FALSIFIED)\b"
)
SECRET_NAME_RE = re.compile(
    r"(?i)(token|secret|password|passwd|credential|private[_-]?key|oauth|cookie|session)"
)
PERSONAL_NAME_RE = re.compile(r"(?i)(author|approval|consent|correspond|orcid|email)")


def iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).astimezone().isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def category(rel: Path) -> str:
    p = rel.as_posix()
    top = rel.parts[0] if rel.parts else "ROOT"
    mapping = {
        "0_admin": "administration",
        "1_data": "source_or_derived_data",
        "2_code": "code",
        "3_results": "analysis_results",
        "4_figures": "figures",
        "4_output": "legacy_output",
        "5_analysis": "analysis_workspace",
        "5_manuscript": "manuscript",
        "6_release": "release",
        "7.Report": "reports",
        "8.Reference": "references",
        "9_Vote": "decision_records",
        "9.Version": "versioned_plans",
        "github": "github_worktrees",
        "tools": "tools",
        ".qiteng_v03242_runtime": "skill_runtime",
        "R5A2A2_OneK1K_archive_audit": "legacy_archive_audit",
    }
    if "/.git/" in f"/{p}/" or p.endswith("/.git"):
        return "git_internal"
    return mapping.get(top, "workspace_root")


def file_kind(path: Path) -> str:
    ext = path.suffix.lower()
    name = path.name.lower()
    if name in {"license", "copying"}:
        return "license_text"
    if ext in TEXT_EXT or name in {"makefile", "dockerfile"}:
        return "text"
    if ext in OFFICE_EXT:
        return "office"
    if ext == ".pdf":
        return "pdf"
    if ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".svg", ".webp"}:
        return "image"
    if ext in ARCHIVE_EXT:
        return "archive"
    if ext in DATA_EXT:
        return "binary_data"
    if ext in {".sha256", ".md5"}:
        return "checksum"
    return "other"


def stages(text: str) -> list[str]:
    return sorted({m.group(1).upper() for m in STAGE_RE.finditer(text)})


def public_class(rel: Path, cat: str, path: Path) -> tuple[str, str]:
    p = rel.as_posix().lower()
    n = path.name.lower()
    if cat == "git_internal":
        return "EXCLUDE", "git implementation data"
    if cat == "skill_runtime":
        return "EXCLUDE", "third-party/local skill runtime"
    if cat in {"source_or_derived_data", "legacy_archive_audit"}:
        return "REVIEW_OR_EXCLUDE", "source/individual-level/licence status requires file-level review"
    if SECRET_NAME_RE.search(n) or any(x in p for x in ["private", "credential", "token", "cookie"]):
        return "EXCLUDE", "credential or secret-risk naming"
    if PERSONAL_NAME_RE.search(n) and cat in {"administration", "workspace_root"}:
        return "REVIEW", "personal or authorship record"
    if path.stat().st_size > 10 * 1024 * 1024:
        return "LARGE_REVIEW", "larger than 10 MiB public-repository gate"
    if cat in {"code", "analysis_results", "figures", "manuscript", "reports", "release", "decision_records"}:
        return "POTENTIALLY_PUBLIC", "research artifact; secret/licence scan still required"
    return "REVIEW", "manual publication decision required"


def decode_text(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "utf-16", "gb18030", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def summarize_text(path: Path, size: int) -> dict[str, object]:
    limit = min(size, 8 * 1024 * 1024)
    with path.open("rb") as fh:
        data = fh.read(limit)
    text = decode_text(data)
    lines = text.splitlines()
    nonempty = [x.strip() for x in lines if x.strip()]
    heading = next((re.sub(r"^#+\s*", "", x)[:300] for x in nonempty if x.startswith("#")), "")
    if not heading and nonempty:
        heading = nonempty[0][:300]
    status = sorted({m.group(1).upper().replace(" ", "_").replace("-", "_") for m in STATUS_RE.finditer(text)})
    return {
        "content_title": heading,
        "text_lines_scanned": len(lines),
        "text_scan_complete": size <= limit,
        "stage_tokens": ";".join(stages(path.name + "\n" + text[:1_000_000])),
        "status_tokens": ";".join(status[:40]),
        "content_note": f"text preview {len(data)} bytes",
    }


def summarize_docx(path: Path) -> dict[str, object]:
    try:
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml")
            root = ET.fromstring(xml)
            ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paras = []
            for p in root.iter(ns + "p"):
                txt = "".join((t.text or "") for t in p.iter(ns + "t")).strip()
                if txt:
                    paras.append(txt)
            text = "\n".join(paras)
            title = paras[0][:300] if paras else ""
            return {
                "content_title": title,
                "text_lines_scanned": len(paras),
                "text_scan_complete": True,
                "stage_tokens": ";".join(stages(path.name + "\n" + text[:1_000_000])),
                "status_tokens": ";".join(sorted({m.group(1).upper() for m in STATUS_RE.finditer(text[:1_000_000])})[:40]),
                "content_note": f"DOCX paragraphs={len(paras)} members={len(zf.infolist())}",
            }
    except Exception as exc:
        return {"content_note": f"DOCX_PARSE_ERROR:{type(exc).__name__}:{exc}"}


def summarize_xlsx(path: Path) -> dict[str, object]:
    try:
        with zipfile.ZipFile(path) as zf:
            wb = ET.fromstring(zf.read("xl/workbook.xml"))
            ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            names = [s.attrib.get("name", "") for s in wb.findall(".//m:sheets/m:sheet", ns)]
            return {
                "content_title": ";".join(names[:20]),
                "text_scan_complete": True,
                "stage_tokens": ";".join(stages(path.name + " " + " ".join(names))),
                "content_note": f"XLSX sheets={len(names)} members={len(zf.infolist())}",
            }
    except Exception as exc:
        return {"content_note": f"XLSX_PARSE_ERROR:{type(exc).__name__}:{exc}"}


def summarize_zip(path: Path) -> dict[str, object]:
    try:
        with zipfile.ZipFile(path) as zf:
            infos = zf.infolist()
            total = sum(i.file_size for i in infos)
            names = [i.filename for i in infos]
            return {
                "content_title": ";".join(names[:5])[:300],
                "text_scan_complete": True,
                "stage_tokens": ";".join(stages(path.name + " " + " ".join(names[:1000]))),
                "content_note": f"ZIP entries={len(infos)} uncompressed={total}",
                "archive_entries": len(infos),
                "archive_uncompressed_bytes": total,
            }
    except Exception as exc:
        return {"content_note": f"ZIP_PARSE_ERROR:{type(exc).__name__}:{exc}"}


def summarize_pdf(path: Path) -> dict[str, object]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        meta = reader.metadata or {}
        title = str(meta.get("/Title") or "")[:300]
        return {
            "content_title": title,
            "text_scan_complete": False,
            "stage_tokens": ";".join(stages(path.name + " " + title)),
            "content_note": f"PDF pages={len(reader.pages)} creator={meta.get('/Creator') or ''}",
            "pdf_pages": len(reader.pages),
        }
    except Exception as exc:
        return {"content_note": f"PDF_PARSE_ERROR:{type(exc).__name__}:{exc}"}


def content_summary(path: Path, kind: str, size: int, git_internal: bool) -> dict[str, object]:
    if git_internal:
        return {"content_note": "git internal; content parsing skipped"}
    if kind == "text":
        return summarize_text(path, size)
    if kind == "office" and path.suffix.lower() in {".docx", ".docm"}:
        return summarize_docx(path)
    if kind == "office" and path.suffix.lower() in {".xlsx", ".xlsm"}:
        return summarize_xlsx(path)
    if kind == "archive" and path.suffix.lower() == ".zip":
        return summarize_zip(path)
    if kind == "pdf":
        return summarize_pdf(path)
    return {"stage_tokens": ";".join(stages(path.name)), "content_note": "metadata-only content classification"}


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--hash-max-mib", type=int, default=256)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    hash_max = args.hash_max_mib * 1024 * 1024
    started = datetime.now().astimezone()
    rows: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    dir_counts: Counter[str] = Counter()
    dir_bytes: Counter[str] = Counter()
    ext_counts: Counter[str] = Counter()
    ext_bytes: Counter[str] = Counter()
    cat_counts: Counter[str] = Counter()
    cat_bytes: Counter[str] = Counter()

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        # Avoid re-inventorying this run's generated outputs while it is writing.
        if current_path == out or out in current_path.parents:
            dirs[:] = []
            continue
        for name in files:
            path = current_path / name
            try:
                if path.is_symlink():
                    continue
                st = path.stat()
                if not stat.S_ISREG(st.st_mode):
                    continue
                rel = path.relative_to(root)
                top = rel.parts[0] if rel.parts else "ROOT"
                cat = category(rel)
                kind = file_kind(path)
                ext = path.suffix.lower() or "[no_ext]"
                git_internal = cat == "git_internal"
                pub, reason = public_class(rel, cat, path)
                summary = content_summary(path, kind, st.st_size, git_internal)
                digest = ""
                hash_state = "NOT_HASHED_SIZE_GATE"
                if not git_internal and st.st_size <= hash_max:
                    digest = sha256(path)
                    hash_state = "SHA256_COMPLETE"
                elif git_internal:
                    hash_state = "NOT_HASHED_GIT_INTERNAL"
                row = {
                    "relative_path": rel.as_posix(),
                    "absolute_path": str(path),
                    "top_level": top,
                    "category": cat,
                    "file_kind": kind,
                    "extension": ext,
                    "size_bytes": st.st_size,
                    "size_mib": f"{st.st_size / 1024 / 1024:.6f}",
                    "modified_local": iso_mtime(path),
                    "sha256": digest,
                    "hash_state": hash_state,
                    "public_class": pub,
                    "public_reason": reason,
                    "likely_sensitive_name": bool(SECRET_NAME_RE.search(name)),
                    "content_title": summary.get("content_title", ""),
                    "stage_tokens": summary.get("stage_tokens", ";".join(stages(name))),
                    "status_tokens": summary.get("status_tokens", ""),
                    "content_note": summary.get("content_note", ""),
                    "text_lines_scanned": summary.get("text_lines_scanned", ""),
                    "text_scan_complete": summary.get("text_scan_complete", ""),
                    "archive_entries": summary.get("archive_entries", ""),
                    "archive_uncompressed_bytes": summary.get("archive_uncompressed_bytes", ""),
                    "pdf_pages": summary.get("pdf_pages", ""),
                }
                rows.append(row)
                dir_counts[top] += 1
                dir_bytes[top] += st.st_size
                ext_counts[ext] += 1
                ext_bytes[ext] += st.st_size
                cat_counts[cat] += 1
                cat_bytes[cat] += st.st_size
            except Exception as exc:
                errors.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})

    rows.sort(key=lambda x: x["relative_path"].lower())
    fields = [
        "relative_path", "absolute_path", "top_level", "category", "file_kind", "extension",
        "size_bytes", "size_mib", "modified_local", "sha256", "hash_state", "public_class",
        "public_reason", "likely_sensitive_name", "content_title", "stage_tokens", "status_tokens",
        "content_note", "text_lines_scanned", "text_scan_complete", "archive_entries",
        "archive_uncompressed_bytes", "pdf_pages",
    ]
    write_tsv(out / "R7C3_all_local_files_inventory.tsv", rows, fields)
    large = sorted((r for r in rows if int(r["size_bytes"]) >= 100 * 1024 * 1024), key=lambda x: int(x["size_bytes"]), reverse=True)
    write_tsv(out / "R7C3_large_files_100MiB.tsv", large, fields)
    unhashed = [r for r in rows if r["hash_state"] == "NOT_HASHED_SIZE_GATE"]
    write_tsv(out / "R7C3_unhashed_large_files.tsv", unhashed, fields)

    top_rows = [
        {
            "top_level": key,
            "file_count": dir_counts[key],
            "bytes": dir_bytes[key],
            "gib": f"{dir_bytes[key] / 1024**3:.6f}",
        }
        for key in sorted(dir_counts)
    ]
    write_tsv(out / "R7C3_top_level_summary.tsv", top_rows, ["top_level", "file_count", "bytes", "gib"])
    ext_rows = [
        {"extension": key, "file_count": ext_counts[key], "bytes": ext_bytes[key], "gib": f"{ext_bytes[key] / 1024**3:.6f}"}
        for key in sorted(ext_counts, key=lambda k: ext_bytes[k], reverse=True)
    ]
    write_tsv(out / "R7C3_extension_summary.tsv", ext_rows, ["extension", "file_count", "bytes", "gib"])
    cat_rows = [
        {"category": key, "file_count": cat_counts[key], "bytes": cat_bytes[key], "gib": f"{cat_bytes[key] / 1024**3:.6f}"}
        for key in sorted(cat_counts, key=lambda k: cat_bytes[k], reverse=True)
    ]
    write_tsv(out / "R7C3_category_summary.tsv", cat_rows, ["category", "file_count", "bytes", "gib"])
    write_tsv(out / "R7C3_inventory_errors.tsv", errors, ["path", "error"])

    # Exact duplicates among files that were fully hashed.
    by_hash: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["sha256"]:
            by_hash[str(row["sha256"])].append(row)
    dup_rows: list[dict[str, object]] = []
    for digest, members in by_hash.items():
        if len(members) < 2:
            continue
        group_bytes = int(members[0]["size_bytes"])
        for member in members:
            dup_rows.append({
                "sha256": digest,
                "copies": len(members),
                "size_each": group_bytes,
                "potential_redundant_bytes": group_bytes * (len(members) - 1),
                "relative_path": member["relative_path"],
                "category": member["category"],
            })
    dup_rows.sort(key=lambda x: (-int(x["potential_redundant_bytes"]), str(x["sha256"]), str(x["relative_path"])))
    write_tsv(
        out / "R7C3_exact_duplicate_files_hashed_subset.tsv",
        dup_rows,
        ["sha256", "copies", "size_each", "potential_redundant_bytes", "relative_path", "category"],
    )

    completed = datetime.now().astimezone()
    state = {
        "schema_version": "1.0",
        "stage": "R7C3_FULL_WORKSPACE_AUDIT",
        "root": str(root),
        "started": started.isoformat(),
        "completed": completed.isoformat(),
        "file_count": len(rows),
        "total_bytes": sum(int(r["size_bytes"]) for r in rows),
        "total_gib": sum(int(r["size_bytes"]) for r in rows) / 1024**3,
        "content_parse_errors": len(errors),
        "hash_max_mib": args.hash_max_mib,
        "sha256_complete_files": sum(r["hash_state"] == "SHA256_COMPLETE" for r in rows),
        "unhashed_large_files": len(unhashed),
        "git_internal_files": sum(r["category"] == "git_internal" for r in rows),
        "exact_duplicate_rows": len(dup_rows),
        "note": "Audit output directory was excluded from its own pre-audit inventory snapshot.",
    }
    (out / "R7C3_inventory_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
