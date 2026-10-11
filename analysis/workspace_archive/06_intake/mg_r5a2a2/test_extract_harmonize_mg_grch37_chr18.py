#!/usr/bin/env python3
"""Focused tests for the allele-orientation rules used by R5A2A2."""

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("extract_harmonize_mg_grch37_chr18.py")
SPEC = importlib.util.spec_from_file_location("harmonizer", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class HarmonizationTests(unittest.TestCase):
    def test_direct_a1(self):
        value = MODULE.classify_and_orient("A", "C", "A", "C", 0.2, 0.4, 0.41)
        self.assertTrue(value["inference_eligible"])
        self.assertAlmostEqual(value["beta_A1"], 0.2)
        self.assertAlmostEqual(value["eaf_A1"], 0.4)

    def test_swapped_a2(self):
        value = MODULE.classify_and_orient("C", "A", "A", "C", 0.2, 0.4, 0.59)
        self.assertTrue(value["inference_eligible"])
        self.assertAlmostEqual(value["beta_A1"], -0.2)
        self.assertAlmostEqual(value["eaf_A1"], 0.6)

    def test_reverse_complement(self):
        value = MODULE.classify_and_orient("T", "G", "A", "C", 0.2, 0.4, 0.39)
        self.assertTrue(value["inference_eligible"])
        self.assertEqual(value["match_type"], "STRAND_DIRECT_A1")

    def test_palindrome_frequency_flip(self):
        value = MODULE.classify_and_orient("A", "T", "A", "T", 0.2, 0.8, 0.2)
        self.assertTrue(value["inference_eligible"])
        self.assertAlmostEqual(value["beta_A1"], -0.2)
        self.assertAlmostEqual(value["eaf_A1"], 0.2)
        self.assertIn("FREQ_FLIPPED", value["match_type"])

    def test_palindrome_ambiguous(self):
        value = MODULE.classify_and_orient("A", "T", "A", "T", 0.2, 0.5, 0.49)
        self.assertFalse(value["inference_eligible"])
        self.assertEqual(value["exclusion_reason"], "PALINDROMIC_FREQUENCY_AMBIGUOUS")

    def test_mismatch(self):
        value = MODULE.classify_and_orient("A", "G", "A", "C", 0.2, 0.4, 0.4)
        self.assertFalse(value["inference_eligible"])
        self.assertEqual(value["exclusion_reason"], "ALLELE_MISMATCH")


if __name__ == "__main__":
    unittest.main()
