"""
01_geometry_check.py
====================

Second script in the pre-registered analysis pipeline.

Purpose
-------
The database file contains a pre-computed column,
``Intersection Latitude at Lon 47.1W Line``, derived by the data owner.
The pre-registered analysis computes great-circle intersections
INDEPENDENTLY from the raw ``LAT``, ``LON``, and ``BEARING`` columns
using the primitives in ``geometry.py``. This script validates that
the independent geometry pipeline produces results consistent with the
data owner's pre-computed values.

Specifically, this script:

1. Verifies the database SHA-256 hash.
2. Runs the geometry self-tests.
3. Loads the 'All Data' sheet.
4. Computes intersection latitudes independently for all rows.
5. Compares against Mario's pre-computed column row by row.
6. Reports agreement statistics and writes a row-level CSV of
   discrepancies.

This script does NOT compute any test statistic. The test statistic
is in script 02.

Pre-registration: https://doi.org/10.5281/zenodo.20258204
License:          MIT
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import compute_intersection_lat, run_self_tests  # noqa: E402


# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx"
HASH_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx.sha256"
RESULTS_DIR = REPO_ROOT / "results"
SUMMARY_FILE = RESULTS_DIR / "01_geometry_comparison.json"
DISCREPANCY_FILE = RESULTS_DIR / "01_geometry_discrepancies.csv"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
DISCREPANCY_THRESHOLD_DEG = 0.1


# ---------------------------------------------------------------------------
# Hash verification
# ---------------------------------------------------------------------------


def compute_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def read_reference_hash(hash_file: Path) -> str:
    text = hash_file.read_text().strip()
    parts = text.split()
    if not parts or len(parts[0]) != 64:
        raise ValueError(f"Hash file {hash_file} does not contain a valid SHA-256 hash.")
    return parts[0].lower()


def verify_hash() -> str:
    if not DATA_FILE.exists() or not HASH_FILE.exists():
        print("ERROR: data file or hash file missing.", file=sys.stderr)
        sys.exit(1)
    expected = read_reference_hash(HASH_FILE)
    actual = compute_sha256(DATA_FILE)
    if expected != actual:
        print("ERROR: hash mismatch. Re-run script 00 to investigate.", file=sys.stderr)
        sys.exit(1)
    print(f"SHA-256 verified: {actual}")
    print()
    return actual


# ---------------------------------------------------------------------------
# Parse Mario's pre-computed column
# ---------------------------------------------------------------------------


def parse_marios_intersection_column(series: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Parse the 'Intersection Latitude at Lon 47.1W Line' column.

    The column has dtype 'object' because out-of-range rows contain
    'No Intersect 47.1W' instead of a number.

    Returns
    -------
    values : float array (NaN for non-numeric entries)
    is_no_intersect : bool array (True where non-numeric)
    """
    values = pd.to_numeric(series, errors="coerce").to_numpy()
    is_no_intersect = np.isnan(values)
    return values, is_no_intersect


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("Pre-registered analysis: independent geometry verification")
    print("Script: 01_geometry_check.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print("=" * 60)
    print()

    verified_hash = verify_hash()

    n_tests = run_self_tests()
    print(f"Geometry self-test: {n_tests} cases passed.")
    print()

    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    n = len(df)
    print(f"Loaded {n} rows from sheet {PRIMARY_SHEET!r}.")
    print()

    lat = df["LAT"].to_numpy(dtype=float)
    lon = df["LON"].to_numpy(dtype=float)
    bearing = df["BEARING"].to_numpy(dtype=float)

    marios_values, marios_no_intersect = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )
    independent = compute_intersection_lat(lat, lon, bearing, TARGET_LON_DEG)

    # ----------------------------------------------------------------- #
    # Comparison
    # ----------------------------------------------------------------- #
    print("Independent vs. pre-computed intersection latitudes")
    print("-" * 60)

    both_numeric = ~marios_no_intersect & ~np.isnan(independent)
    n_compared = int(both_numeric.sum())

    diff = independent[both_numeric] - marios_values[both_numeric]
    abs_diff = np.abs(diff)

    print(f"  rows with numeric value in both: {n_compared}")
    print(f"  mean absolute difference:        {np.mean(abs_diff):.6f}°")
    print(f"  median absolute difference:      {np.median(abs_diff):.6f}°")
    print(f"  max absolute difference:         {np.max(abs_diff):.6f}°")
    print(f"  std of difference:               {np.std(diff):.6f}°")
    print()
    print("  Agreement at thresholds:")
    for tol in [0.001, 0.01, 0.1, 1.0]:
        n_within = int((abs_diff <= tol).sum())
        pct = 100.0 * n_within / n_compared if n_compared else 0.0
        print(f"    |diff| <= {tol:>5}°:  {n_within} / {n_compared}  ({pct:.2f}%)")
    print()

    # ----------------------------------------------------------------- #
    # No-intersect agreement
    # ----------------------------------------------------------------- #
    print("'No Intersect' agreement")
    print("-" * 60)

    independent_no_intersect = np.isnan(independent)
    both_no_intersect = marios_no_intersect & independent_no_intersect
    marios_only = marios_no_intersect & ~independent_no_intersect
    independent_only = ~marios_no_intersect & independent_no_intersect

    print(f"  Mario marks no-intersect:                {int(marios_no_intersect.sum())}")
    print(f"  Independent calc gives no-intersect:     {int(independent_no_intersect.sum())}")
    print(f"  Both agree (no-intersect):               {int(both_no_intersect.sum())}")
    print(f"  Mario says no-intersect, indep gives #:  {int(marios_only.sum())}")
    print(f"  Indep says no-intersect, Mario gives #:  {int(independent_only.sum())}")
    print()
    print(f"  Note: Per analysis log (2026-05-17 entry on Convention 1), the")
    print(f"  data owner's 'No Intersect' label is operationally a northern-")
    print(f"  hemisphere filter applied to southern-hemisphere intersections.")
    print(f"  The geometric calculation produces a numeric value for all rows;")
    print(f"  the filter is applied at the analysis layer (script 02).")
    print()

    # ----------------------------------------------------------------- #
    # Discrepancies above threshold
    # ----------------------------------------------------------------- #
    discrepancy_mask = np.zeros(n, dtype=bool)
    discrepancy_mask[both_numeric] = abs_diff > DISCREPANCY_THRESHOLD_DEG
    discrepancy_mask |= marios_only | independent_only

    n_discrepant = int(discrepancy_mask.sum())
    print(f"Rows flagged for discrepancy (|diff| > {DISCREPANCY_THRESHOLD_DEG}° "
          f"or no-intersect mismatch): {n_discrepant}")
    print()

    if n_discrepant > 0:
        discrepancy_df = df.loc[discrepancy_mask, [
            "SITE NAME", "COUNTRY", "LAT", "LON", "BEARING",
            "Intersection Latitude at Lon 47.1W Line",
        ]].copy()
        discrepancy_df["independent_intersection_lat"] = independent[discrepancy_mask]
        discrepancy_df["difference_deg"] = (
            independent[discrepancy_mask] - marios_values[discrepancy_mask]
        )
        discrepancy_df.to_csv(DISCREPANCY_FILE, index=False)
        print(f"Per-row discrepancies written to {DISCREPANCY_FILE.relative_to(REPO_ROOT)}")
    else:
        print("No discrepancies above threshold.")
    print()

    summary = {
        "script": "01_geometry_check.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "target_lon_deg": TARGET_LON_DEG,
        "discrepancy_threshold_deg": DISCREPANCY_THRESHOLD_DEG,
        "n_rows_total": int(n),
        "n_rows_compared_numeric": n_compared,
        "abs_diff_mean_deg": float(np.mean(abs_diff)) if n_compared else None,
        "abs_diff_median_deg": float(np.median(abs_diff)) if n_compared else None,
        "abs_diff_max_deg": float(np.max(abs_diff)) if n_compared else None,
        "diff_std_deg": float(np.std(diff)) if n_compared else None,
        "agreement_at_thresholds": {
            f"{tol}_deg": int((abs_diff <= tol).sum()) for tol in [0.001, 0.01, 0.1, 1.0]
        } if n_compared else {},
        "no_intersect_counts": {
            "marios_no_intersect": int(marios_no_intersect.sum()),
            "independent_no_intersect": int(independent_no_intersect.sum()),
            "both_agree_no_intersect": int(both_no_intersect.sum()),
            "marios_only_no_intersect": int(marios_only.sum()),
            "independent_only_no_intersect": int(independent_only.sum()),
        },
        "n_discrepant_rows": n_discrepant,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print("Geometry check complete. Next: observed test statistic (script 02).")
    print()


if __name__ == "__main__":
    main()
