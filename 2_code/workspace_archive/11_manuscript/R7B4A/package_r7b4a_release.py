#!/usr/bin/env python3
"""Package the final R7B4A Human Genomics submission-interface release."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
BASE = ROOT / "5_manuscript" / "R7B4A_HumanGenomics_SubmissionInterface"
CODE = ROOT / "2_code" / "11_manuscript" / "R7B4A"
RELEASE = ROOT / "6_release"
ZIP = RELEASE / "CMM_R7B4A_HumanGenomics_SubmissionInterface_2026-10-10.zip"
SHA = RELEASE / f"{ZIP.name}.sha256"
RECEIPT = RELEASE / "CMM_R7B4A_HumanGenomics_SubmissionInterface_2026-10-10_release_receipt.json"
PREFIX = "CMM_R7B4A_HumanGenomics_SubmissionInterface_2026-10-10"


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_tree(entries: dict[str, Path], source: Path, arc_root: str, *, exclude_parts=()) -> None:
    for path in sorted(source.rglob("*")):
        if not path.is_file() or any(part in path.parts for part in exclude_parts):
            continue
        arcname = f"{PREFIX}/{arc_root}/{path.relative_to(source).as_posix()}"
        entries[arcname] = path


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    entries: dict[str, Path] = {}
    for folder in ["manuscript", "cover_letter", "figures", "graphical_abstract", "supplement", "results", "submission"]:
        add_tree(entries, BASE / folder, folder)
    qa_names = [
        "R7B4A_final_QA.json",
        "R7B4A_final_QA.tsv",
        "R7B4A_inherited_reference_bibliographic_verification.json",
        "R7B4A_inherited_reference_bibliographic_verification.tsv",
        "R7B4A_inherited_reference_bibliographic_verification_state.json",
        "github_sync_receipt.json",
        "manuscript_contact_final.png",
        "cover_final_page.png",
    ]
    for name in qa_names:
        path = BASE / "qa" / name
        if path.exists():
            entries[f"{PREFIX}/qa/{name}"] = path
    entries[f"{PREFIX}/reports/{(BASE / '99_CMM_R7B4A_期刊资格冻结与投稿接口_详细行动记录_2026-10-10.md').name}"] = BASE / "99_CMM_R7B4A_期刊资格冻结与投稿接口_详细行动记录_2026-10-10.md"
    add_tree(entries, CODE, "code", exclude_parts=("__pycache__",))

    readme = f"""# R7B4A Human Genomics Submission Interface Release

Status: technical interface complete; human author gate pending.

Primary route: Human Genomics, Research.

This package contains the journal-specific manuscript, WPS reviewer PDF, one-page WPS cover-letter draft, Figure 1–6 triplets, mandatory 920x300 graphical abstract, two additional files, journal audit, upload map, author-completion form, final QA, public-repository receipt, execution code and detailed action record.

Final machine QA: 42/42 PASS.

Public immutable tag: https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/tree/r7b4a-human-genomics-interface-2026-10-10

Release tag commit: c768ff4c02481331c6563cf8e040062a8e31b6db

Remote main receipt commit: c3ad79a2cffa41281faf01088b95516867b1ad91

The package is not a submitted manuscript. Authors, affiliations, correspondence, CRediT, funding, competing interests, institutional ethics/waiver wording, acknowledgements, APC/licence route and all-author approval remain mandatory human-supplied fields. External submission requires explicit corresponding-author authorization.
""".encode("utf-8")

    checksums = []
    for arcname, path in sorted(entries.items()):
        checksums.append(f"{digest_file(path)}  {arcname.removeprefix(PREFIX + '/')}")
    checksums.append(f"{digest_bytes(readme)}  README.md")
    checksum_data = ("\n".join(checksums) + "\n").encode("utf-8")

    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for arcname, path in sorted(entries.items()):
            archive.write(path, arcname)
        archive.writestr(f"{PREFIX}/README.md", readme)
        archive.writestr(f"{PREFIX}/checksums.sha256", checksum_data)

    with zipfile.ZipFile(ZIP) as archive:
        bad = archive.testzip()
        members = archive.namelist()
        checksum_lines = archive.read(f"{PREFIX}/checksums.sha256").decode("utf-8").splitlines()
        verified = 0
        for line in checksum_lines:
            expected, relative = line.split("  ", 1)
            actual = digest_bytes(archive.read(f"{PREFIX}/{relative}"))
            if actual != expected:
                raise RuntimeError(f"Internal checksum mismatch: {relative}")
            verified += 1
    if bad is not None:
        raise RuntimeError(f"ZIP CRC failure: {bad}")

    outer = digest_file(ZIP)
    SHA.write_text(f"{outer}  {ZIP.name}\n", encoding="utf-8")
    receipt = {
        "release": ZIP.name,
        "bytes": ZIP.stat().st_size,
        "sha256": outer,
        "zip_crc": "PASS",
        "zip_entries": len(members),
        "internal_checksums": f"{verified}/{verified} PASS",
        "final_machine_qa": "42/42 PASS",
        "wps_manuscript_pages": 31,
        "wps_cover_pages": 1,
        "github_release_commit": "c768ff4c02481331c6563cf8e040062a8e31b6db",
        "github_main_receipt_commit": "c3ad79a2cffa41281faf01088b95516867b1ad91",
        "github_tag": "r7b4a-human-genomics-interface-2026-10-10",
        "status": "PASS_HUMAN_GATE_PENDING",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
