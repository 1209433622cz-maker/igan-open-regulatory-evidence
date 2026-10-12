#!/usr/bin/env python3
"""Verify manuscript reference metadata against DOI/Crossref and URL endpoints."""

from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
MD = ROOT / "5_manuscript/R7B3A_ManuscriptV2/manuscript/R7B3A_full_english_manuscript_v2.md"
OUT = ROOT / "5_manuscript/R7B3A_ManuscriptV2/qa"
OUT.mkdir(parents=True, exist_ok=True)


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def fetch_json(url: str) -> tuple[int, dict | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "R7B3A-reference-audit/1.0 (mailto:research@example.invalid)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            return response.status, json.loads(raw.decode("utf-8")), response.geturl()
    except Exception as exc:
        return 0, None, str(exc)


def check_url(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl()
    except Exception as exc:
        return 0, str(exc)


def main() -> int:
    text = MD.read_text(encoding="utf-8")
    ref_text = text.split("## References", 1)[1].split("## Figure legends", 1)[0]
    refs = re.findall(r"(?m)^(\d+)\. (.+)$", ref_text)
    if len(refs) != 22:
        raise ValueError(f"expected 22 references, found {len(refs)}")
    records = []
    for num_s, citation in refs:
        num = int(num_s)
        doi_match = re.search(r"doi:(10\.\d{4,9}/[^\s]+)", citation, re.I)
        url_match = re.search(r"https?://[^\s]+", citation)
        title_match = re.match(r".*?\. (.+?)\. \*", citation)
        cited_title = title_match.group(1) if title_match else ""
        record = {"reference": num, "citation": citation, "doi": None, "url": None,
                  "endpoint_status": 0, "resolved_url": "", "metadata_title": "",
                  "metadata_year": None, "title_similarity": None, "status": ""}
        if doi_match:
            doi = doi_match.group(1).rstrip(".")
            record["doi"] = doi
            status, payload, resolved = fetch_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
            record["endpoint_status"] = status; record["resolved_url"] = resolved
            if status == 200 and payload:
                message = payload.get("message", {})
                title = (message.get("title") or [""])[0]
                year_parts = (message.get("published-print") or message.get("published-online") or message.get("issued") or {}).get("date-parts", [[]])
                year = year_parts[0][0] if year_parts and year_parts[0] else None
                sim = SequenceMatcher(None, norm(cited_title), norm(title)).ratio() if cited_title else None
                record.update(metadata_title=title, metadata_year=year, title_similarity=sim,
                              status="PASS" if (sim is None or sim >= .90) else "REVIEW")
            else:
                record["status"] = "FAIL"
        elif url_match:
            url = url_match.group(0).rstrip(".")
            record["url"] = url
            status, resolved = check_url(url)
            record["endpoint_status"] = status; record["resolved_url"] = resolved
            record["status"] = "PASS" if status in {200, 202, 301, 302, 303} else "REVIEW"
        else:
            record["status"] = "REVIEW"
        records.append(record)
        time.sleep(.1)
    frame = pd.DataFrame(records)
    frame.to_csv(OUT / "R7B3A_reference_bibliographic_verification.tsv", sep="\t", index=False)
    state = {
        "references": len(frame), "pass": int((frame.status == "PASS").sum()),
        "review": int((frame.status == "REVIEW").sum()), "fail": int((frame.status == "FAIL").sum()),
        "status": "PASS" if not (frame.status == "FAIL").any() else "FAIL",
        "records": records,
    }
    (OUT / "R7B3A_reference_bibliographic_verification.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: state[k] for k in ["references", "pass", "review", "fail", "status"]}))
    return 0 if state["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
