#!/usr/bin/env python3
"""Bind a published R7B4B2 Zenodo DOI into public citation/provenance files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
REPO = ROOT / "github" / "igan-open-regulatory-evidence"
DEFAULT_RECEIPT = ROOT / "6_release" / "R7B4B2_2026-10-10" / "R7B4B2_zenodo_receipt.json"
TAG = "r7b4b2-author-approved-open-research-release-2026-10-10"


def write(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def update_report(path: Path, doi: str, record_url: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("GITHUB_RELEASE = PUBLISHING_AUTHORIZED", "GITHUB_RELEASE = COMPLETE_VERIFIED")
    text = text.replace("ZENODO_DOI = PENDING_AUTHENTICATED_EXECUTION", f"ZENODO_DOI = {doi}")
    text = text.replace(
        "若 Zenodo 身份验证在本轮恢复，立即发布并把 DOI 回写至 `CITATION.cff`、README、出版状态 JSON 与 GitHub Release。若没有凭据，下一阶段被严格限定为 `R7B4B3_ZENODO_AUTHENTICATED_PUBLICATION_AND_DOI_BINDING`；完成 DOI 绑定后再由作者登录 Human Genomics 投稿系统，不新增生物学分析。",
        f"Zenodo 已通过作者账户发布，DOI 为 [{doi}](https://doi.org/{doi})，公开记录为 {record_url}。DOI 已回写至 `CITATION.cff`、README、出版状态 JSON 与 GitHub Release。下一阶段为作者登录 Human Genomics 投稿系统完成正式投稿；不新增生物学分析。",
    )
    if f"https://doi.org/{doi}" not in text:
        text += f"\n\n## 9. 最终 DOI\n\n- DOI: https://doi.org/{doi}\n- Zenodo record: {record_url}\n"
    write(path, text)


def rebuild_manifest() -> None:
    rows = []
    for path in sorted(REPO.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.name == "MANIFEST.sha256":
            continue
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(block)
        rows.append(f"{h.hexdigest()}  {path.relative_to(REPO).as_posix()}\n")
    write(REPO / "MANIFEST.sha256", "".join(rows))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    receipt_path = args.receipt.resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not receipt.get("submitted"):
        raise RuntimeError("Zenodo receipt is not a published record; DOI binding refused.")
    doi = receipt.get("doi") or receipt.get("reserved_doi")
    if not isinstance(doi, str) or not re.fullmatch(r"10\.5281/zenodo\.\d+", doi):
        raise RuntimeError(f"Unexpected or missing production Zenodo DOI: {doi!r}")
    record_url = receipt.get("record_url") or receipt.get("doi_url") or f"https://doi.org/{doi}"

    citation = REPO / "CITATION.cff"
    cff = citation.read_text(encoding="utf-8")
    cff = re.sub(r"(?m)^doi:.*\n?", "", cff)
    cff = re.sub(r"(?m)^url:.*\n?", "", cff)
    marker = "date-released: 2026-10-10\n"
    if marker not in cff:
        raise RuntimeError("CITATION.cff date-released marker not found")
    cff = cff.replace(marker, marker + f'doi: "{doi}"\nurl: "https://doi.org/{doi}"\n')
    write(citation, cff)

    readme = REPO / "README.md"
    text = readme.read_text(encoding="utf-8")
    doi_line = f"\nZenodo DOI: [{doi}](https://doi.org/{doi})\n"
    heading = "## R7B4B2 author-approved open research release"
    if f"https://doi.org/{doi}" not in text:
        pos = text.find(heading)
        if pos < 0:
            raise RuntimeError("R7B4B2 README section not found")
        next_heading = text.find("\n## ", pos + len(heading))
        if next_heading < 0:
            text += doi_line
        else:
            text = text[:next_heading] + doi_line + text[next_heading:]
    write(readme, text)

    state_path = REPO / "results" / "r7b4b2" / "R7B4B2_publication_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["github"]["status"] = "PUBLISHED_VERIFIED"
    state["zenodo"] = {
        "status": "PUBLISHED",
        "doi": doi,
        "doi_url": f"https://doi.org/{doi}",
        "record_url": record_url,
        "deposition_id": receipt.get("deposition_id"),
    }
    write(state_path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")

    receipt_public = REPO / "results" / "r7b4b2" / "R7B4B2_zenodo_receipt.json"
    receipt_public.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(receipt_path, receipt_public)

    for report in [
        REPO / "reports" / "r7b4b2" / "99_CMM_R7B4B2_GitHub_Zenodo_DOI_release_record_2026-10-10.md",
        ROOT / "5_manuscript" / "R7B4B_FinalSubmissionCandidate" / "reports" / "99_CMM_R7B4B2_GitHub_投稿包_Zenodo_DOI发布_详细行动记录_2026-10-10.md",
        ROOT / "7.Report" / "99_CMM_R7B4B2_GitHub_投稿包_Zenodo_DOI发布_详细行动记录_2026-10-10.md",
    ]:
        update_report(report, doi, record_url)

    rebuild_manifest()
    print(json.dumps({"doi": doi, "doi_url": f"https://doi.org/{doi}", "record_url": record_url, "tag": TAG}, indent=2))


if __name__ == "__main__":
    main()
