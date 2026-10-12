"""Portable path contract for the public R7C3G reproduction scripts."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


REPO_ROOT = Path(
    os.environ.get("R7_REPO_ROOT", Path(__file__).resolve().parents[3])
).resolve()
CURRENT_PACKAGE = REPO_ROOT / "5_manuscript" / "current" / "R7C3H"
RESULTS_ROOT = REPO_ROOT / "3_results"
PROTOCOLS_ROOT = REPO_ROOT / "0_admin" / "protocols"
FIGURES_ROOT = REPO_ROOT / "4_figures"


def runtime_output(stage: str) -> Path:
    """Return an output directory outside the checkout unless explicitly set."""

    configured = os.environ.get("R7_RUNTIME_OUT")
    base = Path(configured).resolve() if configured else Path(tempfile.gettempdir()) / "pbc-r7-portable-qa"
    out = base / stage
    out.mkdir(parents=True, exist_ok=True)
    return out
