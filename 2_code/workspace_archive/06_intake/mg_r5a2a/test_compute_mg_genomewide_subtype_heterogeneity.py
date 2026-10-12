#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import math
import pathlib
import sys


MODULE_PATH = pathlib.Path(__file__).with_name("compute_mg_genomewide_subtype_heterogeneity.py")
SPEC = importlib.util.spec_from_file_location("mg_heterogeneity", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def row(effect: str, other: str, odds_ratio: float, eaf: float = 0.2) -> dict[str, str]:
    return {
        "chromosome": "5",
        "base_pair_location": "151067567",
        "effect_allele": effect,
        "other_allele": other,
        "odds_ratio": str(odds_ratio),
        "standard_error": "0.1",
        "effect_allele_frequency": str(eaf),
        "p_value": "0.01",
        "rsid": "rs6861227",
        "variant_id": "5_151067567_T_G",
    }


def main() -> None:
    alt = MODULE.parse_row(row("G", "T", math.exp(0.4), 0.2))
    ref = MODULE.parse_row(row("T", "G", math.exp(-0.4), 0.8))
    assert alt.key == ref.key == (5, 151067567, "T", "G")
    assert abs(alt.beta_alt - 0.4) < 1e-12
    assert abs(ref.beta_alt - 0.4) < 1e-12
    assert abs(alt.eaf_alt - 0.2) < 1e-12
    assert abs(ref.eaf_alt - 0.2) < 1e-12
    comparison = MODULE.heterogeneity_row(alt, ref)
    assert abs(comparison["delta_beta_E_minus_L"]) < 1e-12

    invalid = row("A", "T", 1.1)
    try:
        MODULE.parse_row(invalid)
    except MODULE.RowError as exc:
        assert exc.code == "allele_set_mismatch"
    else:
        raise AssertionError("Allele-set mismatch was not rejected")
    print("SYNTHETIC_ALLELE_ORIENTATION_PASS")


if __name__ == "__main__":
    main()
