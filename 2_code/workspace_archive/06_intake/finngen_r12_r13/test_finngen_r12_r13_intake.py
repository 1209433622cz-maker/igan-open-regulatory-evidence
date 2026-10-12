#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import finngen_manifest_audit as audit
import p0_validate_finngen_region as p0


class ManifestTests(unittest.TestCase):
    def test_parse_exact_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.tsv"
            columns = ["phenocode", "phenotype", "category", "num_cases", "num_controls", "path_bucket", "path_https"]
            rows = [
                [endpoint, endpoint, "cat", "10", "90", "gs://bucket/x", f"https://storage.googleapis.com/finngen-public-data-r13/{endpoint}.gz"]
                for endpoint in ("M13_SYSTSLCE", "SYSTSCLE_STRICT", "CREST")
            ]
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
                writer.writerow(columns)
                writer.writerows(rows)
            selected, observed = audit.parse_manifest(path, [row[0] for row in rows])
            self.assertEqual(len(selected), 3)
            self.assertEqual(observed, columns)

    def test_duplicate_target_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.tsv"
            text = (
                "phenocode\tphenotype\tcategory\tnum_cases\tnum_controls\tpath_bucket\tpath_https\n"
                "M13_SYSTSLCE\tSSc\tcat\t10\t90\tgs://x\thttps://storage.googleapis.com/finngen-public-data-r13/x.gz\n"
                "M13_SYSTSLCE\tSSc\tcat\t10\t90\tgs://x\thttps://storage.googleapis.com/finngen-public-data-r13/y.gz\n"
            )
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.parse_manifest(path, ["M13_SYSTSLCE"])

    def test_provider_md5_conversion(self):
        self.assertEqual(audit.provider_md5_hex("4+8/Ac5dutVPNbYHdvwd9g=="), "e3ef3f01ce5dbad54f35b60776fc1df6")


class RegionTests(unittest.TestCase):
    def test_open_plain_and_gzip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plain = root / "x.tsv"
            gz = root / "x.tsv.gz"
            plain.write_text("a\tb\n1\t2\n", encoding="utf-8")
            with gzip.open(gz, "wt", encoding="utf-8") as handle:
                handle.write("a\tb\n1\t2\n")
            with p0.open_text(plain) as handle:
                self.assertEqual(handle.readline().strip(), "a\tb")
            with p0.open_text(gz) as handle:
                self.assertEqual(handle.readline().strip(), "a\tb")

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            p0.finite_number("nan")

    def _write_region(self, path: Path, include_anchor: bool) -> None:
        columns = [
            "#chrom", "pos", "ref", "alt", "rsids", "nearest_genes",
            "pval", "mlogp", "beta", "sebeta", "af_alt",
            "af_alt_cases", "af_alt_controls",
        ]
        start = 66_840_524
        rows = []
        for index in range(101):
            pos = start + index * 3_000
            rows.append(["1", pos, "A", "G", f"rsSynthetic{index}", "IL12RB2", "0.5", "0.301", "0.01", "0.1", "0.2", "0.21", "0.19"])
        if include_anchor:
            rows[50] = ["1", 67_340_524, "T", "C", "rs6662198", "IL12RB2", "1e-8", "8", "0.2", "0.03", "0.25", "0.3", "0.24"]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            writer.writerow(columns)
            writer.writerows(rows)

    def test_region_cli_passes_valid_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_path = root / "region.tsv"
            output_path = root / "result.json"
            self._write_region(input_path, include_anchor=True)
            command = [
                sys.executable,
                str(Path(__file__).with_name("p0_validate_finngen_region.py")),
                "--input", str(input_path),
                "--config", str(Path(__file__).with_name("target_config.json")),
                "--release", "R13",
                "--output", str(output_path),
            ]
            completed = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8"))["status"], "PASS_REGION_STRUCTURAL_READY_FOR_HARMONIZATION")

    def test_region_cli_holds_without_anchor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_path = root / "region.tsv"
            output_path = root / "result.json"
            self._write_region(input_path, include_anchor=False)
            command = [
                sys.executable,
                str(Path(__file__).with_name("p0_validate_finngen_region.py")),
                "--input", str(input_path),
                "--config", str(Path(__file__).with_name("target_config.json")),
                "--release", "R13",
                "--output", str(output_path),
            ]
            completed = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "HOLD_REGION_STRUCTURAL_GATE_FAILED")
            self.assertIn("exact_anchor_count:0!=1", result["errors"])


class DownloadTests(unittest.TestCase):
    def test_download_runner_defaults_to_dry_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            incoming = root / "incoming"
            incoming.mkdir()
            plan = root / "plan.tsv"
            destination = incoming / "R13" / "M13_SYSTSLCE" / "x.gz"
            columns = ["endpoint", "content_length", "priority", "release", "object_kind", "url", "local_path"]
            with plan.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerow({
                    "endpoint": "M13_SYSTSLCE", "content_length": "123", "priority": "P1_PRIMARY",
                    "release": "R13", "object_kind": "summary", "url": "https://example.invalid/x.gz",
                    "local_path": str(destination),
                })
            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("download_finngen_objects.py")),
                    "--plan", str(plan), "--incoming-root", str(incoming),
                    "--receipt", str(root / "receipt.json"),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertIn("DRY_RUN_ONLY", completed.stdout)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
