#!/usr/bin/env python3
"""Create, upload and optionally publish the R7B4B2 Zenodo deposition.

Authentication is read only from the ZENODO_TOKEN environment variable and is
never printed or written to disk. The script is idempotent after creation when
called with --deposition-id. Publication is explicit via --publish.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(r"H:\SCI2\YR1")
REPO = ROOT / "github" / "igan-open-regulatory-evidence"
RELEASE = ROOT / "6_release" / "R7B4B2_2026-10-10"
PUBLIC_ZIP = RELEASE / "PBC_R7B4B2_OpenResearchCompendium_2026-10-10.zip"
PUBLIC_SHA = RELEASE / "PBC_R7B4B2_OpenResearchCompendium_2026-10-10.zip.sha256"
MANUSCRIPT_PDF = ROOT / "5_manuscript" / "R7B4B_FinalSubmissionCandidate" / "manuscript" / "R7B4B_HumanGenomics_final_WPS.pdf"
RECEIPT = RELEASE / "R7B4B2_zenodo_receipt.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checked(response: requests.Response, expected: set[int]) -> dict:
    if response.status_code not in expected:
        detail = response.text[:2000]
        raise RuntimeError(f"Zenodo API HTTP {response.status_code}: {detail}")
    if not response.content:
        return {}
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true", help="Publish and mint the DOI after validation and upload.")
    parser.add_argument("--deposition-id", type=int, help="Resume an existing unpublished deposition.")
    parser.add_argument("--base-url", default="https://zenodo.org/api")
    args = parser.parse_args()

    token = os.environ.get("ZENODO_TOKEN", "").strip()
    if not token:
        print(
            "ZENODO_AUTH_REQUIRED: set ZENODO_TOKEN locally with deposit:write and deposit:actions scopes; "
            "the token was not requested, printed or stored.",
            file=sys.stderr,
        )
        raise SystemExit(20)

    for path in [PUBLIC_ZIP, PUBLIC_SHA, MANUSCRIPT_PDF, REPO / ".zenodo.json"]:
        if not path.is_file():
            raise FileNotFoundError(path)

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    base = args.base_url.rstrip("/")

    if args.deposition_id:
        dep = checked(session.get(f"{base}/deposit/depositions/{args.deposition_id}", timeout=60), {200})
    else:
        dep = checked(
            session.post(
                f"{base}/deposit/depositions",
                json={"metadata": {"prereserve_doi": True}},
                timeout=60,
            ),
            {201},
        )

    deposition_id = int(dep["id"])
    if dep.get("submitted"):
        raise RuntimeError(f"Deposition {deposition_id} is already published; refusing to overwrite it.")

    metadata = json.loads((REPO / ".zenodo.json").read_text(encoding="utf-8"))
    metadata["prereserve_doi"] = True
    dep = checked(
        session.put(
            f"{base}/deposit/depositions/{deposition_id}",
            json={"metadata": metadata},
            timeout=60,
        ),
        {200},
    )

    bucket = dep["links"]["bucket"]
    files_to_upload = [PUBLIC_ZIP, PUBLIC_SHA, MANUSCRIPT_PDF]
    uploaded = []
    existing = {item.get("filename") or item.get("name") or item.get("key") for item in dep.get("files", [])}
    for path in files_to_upload:
        if path.name in existing:
            uploaded.append({"name": path.name, "status": "ALREADY_PRESENT", "sha256": digest(path), "bytes": path.stat().st_size})
            continue
        with path.open("rb") as fh:
            info = checked(
                session.put(f"{bucket}/{quote(path.name)}", data=fh, timeout=1800),
                {200, 201},
            )
        uploaded.append(
            {
                "name": path.name,
                "status": "UPLOADED",
                "sha256": digest(path),
                "bytes": path.stat().st_size,
                "zenodo_checksum": info.get("checksum"),
            }
        )

    dep = checked(session.get(f"{base}/deposit/depositions/{deposition_id}", timeout=60), {200})
    reserved = dep.get("metadata", {}).get("prereserve_doi", {})
    receipt = {
        "stage": "R7B4B2_ZENODO",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "deposition_id": deposition_id,
        "state": dep.get("state"),
        "submitted": dep.get("submitted"),
        "reserved_doi": reserved.get("doi") if isinstance(reserved, dict) else None,
        "html": dep.get("links", {}).get("html"),
        "files": uploaded,
        "publish_requested": bool(args.publish),
    }

    if args.publish:
        published = checked(
            session.post(f"{base}/deposit/depositions/{deposition_id}/actions/publish", timeout=180),
            {200, 201, 202},
        )
        receipt.update(
            {
                "state": published.get("state"),
                "submitted": published.get("submitted"),
                "doi": published.get("doi") or published.get("metadata", {}).get("doi"),
                "doi_url": published.get("doi_url"),
                "record_url": published.get("record_url") or published.get("links", {}).get("record_html"),
            }
        )

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
