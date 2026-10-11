#!/usr/bin/env python3
"""Validate the private R7B4B author record without publishing its contents."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_RECORD = Path(r"H:\SCI2\YR1\5_manuscript\R7B4B_PreauthorFinalSubmissionGate\submission\R7B4B_author_record.EMPTY.json")
DEFAULT_OUT = Path(r"H:\SCI2\YR1\5_manuscript\R7B4B_PreauthorFinalSubmissionGate\qa\R7B4B_author_record_validation.json")


def present(value) -> bool:
    return value is not None and value is not False and value != "" and value != []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--mode", choices=["metadata", "final"], default="final")
    args = parser.parse_args()
    data = json.loads(args.record.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, passed: bool, detail) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "HOLD", "detail": str(detail)})

    authors = data.get("authors", [])
    affiliations = data.get("affiliations", [])
    author_initials = [author.get("initials") for author in authors]
    affiliation_ids = {item.get("id") for item in affiliations}
    check("record_version", data.get("record_version") == "R7B4B-1.0", data.get("record_version"))
    check("authors", bool(authors) and all(present(a.get("publication_name")) and present(a.get("initials")) and present(a.get("affiliation_ids")) and present(a.get("credit_roles")) for a in authors), len(authors))
    check("unique_author_initials", bool(author_initials) and len(author_initials) == len(set(author_initials)), author_initials)
    check("affiliations", bool(affiliations) and all(present(a.get("id")) and present(a.get("full_institutional_address")) for a in affiliations), len(affiliations))
    used_affiliations = {value for author in authors for value in author.get("affiliation_ids", [])}
    check("author_affiliation_mapping", bool(used_affiliations) and used_affiliations.issubset(affiliation_ids), sorted(used_affiliations - affiliation_ids))
    corresponding = data.get("corresponding_author", {})
    email = corresponding.get("institutional_email") or ""
    check("corresponding_author", corresponding.get("author_initials") in author_initials and present(corresponding.get("postal_address")) and bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)), corresponding.get("author_initials"))

    declarations = data.get("declarations", {})
    ethics = declarations.get("ethics", {})
    check("ethics", ethics.get("confirmed") is True and all(present(ethics.get(key)) for key in ["determination", "institution_or_committee", "reference_number_or_not_applicable", "approved_wording", "evidence_reference"]), ethics.get("determination"))
    consent = declarations.get("consent_for_publication", {})
    check("consent_for_publication", consent.get("confirmed") is True and present(consent.get("statement")), consent.get("confirmed"))
    coi = declarations.get("competing_interests", {})
    check("competing_interests", coi.get("all_authors_confirmed") is True and present(coi.get("statement")), coi.get("all_authors_confirmed"))
    funding = declarations.get("research_funding", {})
    check("research_funding", funding.get("confirmed") is True and present(funding.get("statement")) and present(funding.get("funder_role_statement")), funding.get("confirmed"))
    contributions = declarations.get("authors_contributions", {})
    check("authors_contributions", contributions.get("confirmed") is True and present(contributions.get("statement_using_initials")), contributions.get("confirmed"))
    acknowledgements = declarations.get("acknowledgements", {})
    check("acknowledgements", present(acknowledgements.get("statement_or_not_applicable")) and acknowledgements.get("permissions_confirmed") is True, acknowledgements.get("permissions_confirmed"))
    check("ai_disclosure", declarations.get("ai_disclosure", {}).get("statement_approved") is True, declarations.get("ai_disclosure", {}))
    check("originality", declarations.get("originality", {}).get("not_published_or_under_review_elsewhere") is True, declarations.get("originality", {}))

    publication = data.get("publication_arrangements", {})
    check("apc_and_licence", publication.get("confirmed") is True and present(publication.get("apc_route")) and publication.get("research_funding_separate_from_apc") is True and publication.get("licence_choice") in {"CC BY", "CC BY-NC-ND"}, publication)
    qualification = data.get("institutional_journal_qualification", {})
    check("institutional_journal_qualification", qualification.get("status") == "PASS" and all(present(qualification.get(key)) for key in ["evaluation_system", "year", "category", "evidence_reference"]), qualification.get("status"))

    if args.mode == "final":
        approval = data.get("final_version_approval", {})
        check("final_hashes", bool(re.fullmatch(r"[0-9a-fA-F]{64}", approval.get("manuscript_docx_sha256") or "")) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", approval.get("cover_letter_docx_sha256") or "")), "version-bound hashes")
        check("all_author_approval", approval.get("all_authors_approved") is True and set(approval.get("approved_author_initials", [])) == set(author_initials) and present(approval.get("approval_date")), approval.get("approved_author_initials"))
        authorization = data.get("submission_authorization", {})
        check("submission_authorization", authorization.get("authorized") is True and authorization.get("authorized_by_author_initials") == corresponding.get("author_initials") and present(authorization.get("authorization_date")) and authorization.get("author_operated_submission_confirmed") is True, authorization.get("authorized"))

    holds = [item for item in checks if item["status"] == "HOLD"]
    result = {
        "record": str(args.record),
        "mode": args.mode,
        "status": "PASS" if not holds else "HOLD_HUMAN_INPUT_REQUIRED",
        "summary": {"pass": len(checks) - len(holds), "hold": len(holds), "total": len(checks)},
        "checks": checks,
        "privacy": "No private field values are copied beyond bounded check details; do not publish completed input records."
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["summary"] | {"status": result["status"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
