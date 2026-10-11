#!/usr/bin/env python3
"""Independent final gate for R7C3 local, public and submission deliverables."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11"
REL = ROOT / "6_release" / "R7C3_2026-10-11"
REPO = ROOT / "0_admin" / "repositories" / "igan-open-regulatory-evidence"
OUT = AUDIT / "qa"
OUT.mkdir(parents=True, exist_ok=True)
checks = []


def add(name: str, passed: bool, observed, expected) -> None:
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", "observed": str(observed), "expected": str(expected)})


def load(rel: str): return json.loads((AUDIT / rel).read_text(encoding="utf-8-sig"))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def verify_zip(path: Path, manifest_suffix: str | None = None) -> tuple[bool, int, int]:
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: return False, len(z.infolist()), 0
        verified = 0
        if manifest_suffix:
            names = z.namelist()
            manifest_name = next(x for x in names if x.endswith(manifest_suffix))
            base = manifest_name.rsplit("/", 1)[0] + "/"
            for line in z.read(manifest_name).decode("utf-8-sig").splitlines():
                if not line.strip(): continue
                expected, rel = line.split("  ", 1)
                if hashlib.sha256(z.read(base + rel)).hexdigest() != expected: return False, len(names), verified
                verified += 1
        return True, len(z.infolist()), verified


inv = load("inventory/R7C3_inventory_state.json")
integ = load("integrity/R7C3_archive_integrity_summary.json")
dup = load("duplicates/R7C3_duplicate_state.json")
rec = load("records/R7C3_action_record_state.json")
frag = load("fragments/R7C3_fragment_state.json")
asset = load("assets/R7C3_high_value_asset_state.json")
post = load("github/R7C3_github_post_sync_audit.json")
receipt = json.loads((REL / "R7C3_github_release_receipt.json").read_text(encoding="utf-8-sig"))
substate = json.loads((ROOT / "5_manuscript/R7C3_npj_FinalSubmissionPackage_2026-10-11/00_Submission_Package_State.json").read_text(encoding="utf-8"))

add("inventory_file_count", inv["file_count"] == 50630, inv["file_count"], 50630)
add("research_hash_complete", inv["research_non_git_sha256_complete"] == 49565, inv["research_non_git_sha256_complete"], 49565)
add("archive_all_pass", integ["pass"] == integ["targets"] and integ["fail"] == 0, f"{integ['pass']}/{integ['targets']};fail={integ['fail']}", "4333/4333;fail=0")
add("duplicate_state_recorded", dup["duplicate_groups"] == 11375, dup["duplicate_groups"], 11375)
add("action_record_unique", rec["unique_action_record_contents"] == 85, rec["unique_action_record_contents"], 85)
add("asset_ledger_complete", asset["assets"] == 26 and not asset["missing"], f"assets={asset['assets']};missing={len(asset['missing'])}", "26;0")
add("fragment_primary_blocker", frag["primary_evidence_blockers"] == 0, frag["primary_evidence_blockers"], 0)
add("submission_copy_identity", substate["copy_identity_pass"] == 15, substate["copy_identity_pass"], 15)
add("submission_status", substate["status"] == "READY_AUTHOR_OPERATED_SUBMISSION", substate["status"], "READY_AUTHOR_OPERATED_SUBMISSION")
add("wps_pages", substate["wps_pages_reviewed"] == 34, substate["wps_pages_reviewed"], 34)
add("scientific_changes", substate["scientific_changes"] == 0, substate["scientific_changes"], 0)
add("repo_head_remote", post["head"] == post["origin_main"] == receipt["head"], f"{post['head']}|{post['origin_main']}", receipt["head"])
add("repo_clean", post["status_porcelain"] == "", repr(post["status_porcelain"]), "''")
add("repo_manifest_failures", len(post["manifest_failures"]) == 0, len(post["manifest_failures"]), 0)
add("repo_manifest_missing", len(post["manifest_missing_entries"]) == 0, len(post["manifest_missing_entries"]), 0)
add("repo_manifest_extra", len(post["manifest_extra_entries"]) == 0, len(post["manifest_extra_entries"]), 0)
add("repo_large_files", len(post["files_over_10MiB"]) == 0, len(post["files_over_10MiB"]), 0)
add("repo_secret_hits", len(post["secret_pattern_hits"]) == 0, len(post["secret_pattern_hits"]), 0)
add("release_digest_match", receipt["digest_match"] is True, receipt["digest_match"], True)
add("release_tag_commit", receipt["tag_commit"] == receipt["head"], receipt["tag_commit"], receipt["head"])
add("zenodo_not_fabricated", receipt["zenodo_doi"] is None, receipt["zenodo_doi"], None)

zips = [
    ("local_full_zip", REL / "CMM_R7C3_FullWorkspaceAudit_SubmissionGate_LOCAL_2026-10-11.zip", "checksums.sha256"),
    ("public_release_zip", REL / "CMM_R7C3_PublicAudit_SubmissionRelease_2026-10-11.zip", "checksums.sha256"),
    ("submission_zip", REL / "PBC_R7C3_npj_FinalSubmissionPackage_2026-10-11.zip", "checksums.sha256"),
]
for name, path, suffix in zips:
    ok, entries, verified = verify_zip(path, suffix)
    add(name + "_crc_and_internal_hash", ok, f"entries={entries};verified={verified}", "PASS")
    sidecar = Path(str(path) + ".sha256")
    expected = sidecar.read_text(encoding="utf-8-sig").split()[0]
    add(name + "_external_sha", sha256(path) == expected, sha256(path), expected)

reports = list((AUDIT / "reports").glob("*.md"))
add("detailed_report_present", any(p.name.startswith("99_CMM_R7C3") for p in reports), len(reports), ">=7 and 99 present")
add("report_count", len(reports) == 7, len(reports), 7)

with (OUT / "R7C3_final_QA.tsv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(checks[0]), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(checks)
state = {"checks": len(checks), "pass": sum(x["status"] == "PASS" for x in checks), "fail": sum(x["status"] == "FAIL" for x in checks), "failures": [x for x in checks if x["status"] == "FAIL"]}
(OUT / "R7C3_final_QA.json").write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
if state["fail"]: raise SystemExit(1)
