"""
02_observed_test_statistic.py
=============================

Third script in the pre-registered analysis pipeline.

Purpose
-------
Compute the OBSERVED value of the primary test statistic T as specified
in §6 of the pre-registration:

    For each in-range structure i:
        compute great-circle intersection latitude φ'_i on the 47°W meridian
        for each pole k in {Pole I..V} with latitude φ_k:
            d_{i,k} = |φ'_i − φ_k|
        d_i = min_k d_{i,k}
    T = (1/N) Σ d_i,  with N = 993

This script computes T_obs only — the Monte Carlo null distribution
and the p-value are computed in script 03.

Per the pre-registration §11(c), the per-site aggregation threshold is
varied across {1°, 2°, 3°}. The PRIMARY result uses no per-site
aggregation here (each row in 'All Data' is one entry, as the file
already reflects the data owner's aggregation), with the sensitivity
analysis to be run in a later script if multi-structure-at-one-site
rows can be identified in the raw data. The aggregation question is
addressed properly in script 05; this script reports T using the file
as-given.

The script also computes T_obs for the Pole VI sensitivity case
(adding (42.0°N) as a sixth candidate pole) per pre-registration §8.

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)

Outputs
-------
- results/02_observed_test_statistic.json: T_obs (5-pole and 6-pole),
  the d_i distribution summary, and the per-pole assignment counts
  (which structure is closest to which pole — used by script 04 for
  the per-pole confirmatory test).
- results/02_per_structure_distances.csv: row-level d_{i,k} values
  for all 993 in-range structures, used as input to script 03.

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

# Local import — analysis/ is treated as a flat directory of scripts,
# so we ensure it's on sys.path when run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import compute_intersection_lat, run_self_tests  # noqa: E402


# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx"
HASH_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx.sha256"
RESULTS_DIR = REPO_ROOT / "results"
SUMMARY_FILE = RESULTS_DIR / "02_observed_test_statistic.json"
DISTANCES_FILE = RESULTS_DIR / "02_per_structure_distances.csv"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1

# The five proposed paleopole latitudes, all at lon ≈ 47°W.
# Source: data owner's email (2026-05-XX) and Fig 14 of mariobuildreps.com.
POLES_PRIMARY = {
    "I (current)":   90.0,
    "II":            76.0,
    "III":           72.2,
    "IV":            64.1,
    "V":             52.3,
}

# Pole VI for the sensitivity analysis (pre-registration §8).
POLES_WITH_VI = {**POLES_PRIMARY, "VI": 42.0}

EXPECTED_IN_RANGE = 993


def parse_marios_intersection_column(series: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Parse the 'Intersection Latitude at Lon 47.1W Line' column.

    The column has dtype 'object' because out-of-range rows contain
    'No Intersect 47.1W' instead of a number. At least one row
    (Chaco Canyon) uses a comma decimal separator ('56,2' instead of
    '56.2'), which we handle by replacing commas with periods before
    parsing.

    Returns
    -------
    values : float array (NaN for non-numeric entries)
    is_in_range : bool array (True where the value is numeric, i.e.
        Mario classifies the structure as in-range)
    """
    # Coerce to string, then replace comma decimals, then parse as float.
    str_series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    values = pd.to_numeric(str_series, errors="coerce").to_numpy()
    is_in_range = ~np.isnan(values)
    return values, is_in_range


# ---------------------------------------------------------------------------
# Hash verification (duplicated to keep script self-contained)
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
# Test statistic computation
# ---------------------------------------------------------------------------


def compute_d_matrix(intersection_lats: np.ndarray, poles: dict) -> np.ndarray:
    """For each structure i and each pole k, compute d_{i,k} = |φ'_i - φ_k|.

    Parameters
    ----------
    intersection_lats : array of shape (N,)
    poles : dict mapping pole name -> latitude (degrees)

    Returns
    -------
    d_matrix : array of shape (N, K), where K = len(poles).
        Columns are in the order of the poles dict.
    """
    pole_lats = np.array(list(poles.values()))
    d_matrix = np.abs(intersection_lats[:, None] - pole_lats[None, :])
    return d_matrix


def compute_T(intersection_lats: np.ndarray, poles: dict) -> tuple[float, np.ndarray, np.ndarray]:
    """Compute the test statistic T per pre-registration §6.

    Returns
    -------
    T : float
        T = (1/N) Σ_i min_k |φ'_i - φ_k|
    d_min : array of shape (N,)
        Per-structure minimum distance to the nearest pole.
    nearest_pole_index : array of shape (N,), dtype int
        Index of the pole each structure is closest to (0-based).
    """
    d_matrix = compute_d_matrix(intersection_lats, poles)
    d_min = d_matrix.min(axis=1)
    nearest_pole_index = d_matrix.argmin(axis=1)
    T = float(d_min.mean())
    return T, d_min, nearest_pole_index


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("Pre-registered analysis: observed test statistic")
    print("Script: 02_observed_test_statistic.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print("=" * 60)
    print()

    verified_hash = verify_hash()

    # Run geometry self-tests
    n_tests = run_self_tests()
    print(f"Geometry self-test: {n_tests} cases passed.")
    print()

    # Load data
    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    n_total = len(df)
    print(f"Loaded {n_total} rows from sheet {PRIMARY_SHEET!r}.")
    print()

    # Compute independent intersection latitudes for ALL rows
    lat = df["LAT"].to_numpy(dtype=float)
    lon = df["LON"].to_numpy(dtype=float)
    bearing = df["BEARING"].to_numpy(dtype=float)
    intersection = compute_intersection_lat(lat, lon, bearing, TARGET_LON_DEG)

    # Use Mario's classification for in-range/out-of-range determination,
    # but our independent geometry for the actual intersection latitudes.
    # See analysis log entry 2026-05-17 for rationale: Mario's published
    # classification gives N = 993 as pre-registered; using our independent
    # geometry on those 993 ensures the test is computed with the
    # geometrically-correct (raw-bearing, no hand-snapping) intersections,
    # which the data owner himself recommended.
    marios_values, marios_in_range = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )
    n_in_range = int(marios_in_range.sum())
    n_out_of_range = n_total - n_in_range

    print(f"Inclusion (data owner's classification, parsed with comma-decimal fix):")
    print(f"  in-range:             {n_in_range}")
    print(f"  out-of-range:         {n_out_of_range}")
    print(f"  pre-registered N:     {EXPECTED_IN_RANGE}")
    if n_in_range == EXPECTED_IN_RANGE:
        print(f"  [OK]  in-range count matches pre-registered N")
    elif n_in_range == EXPECTED_IN_RANGE + 1:
        print(f"  [NOTE] in-range count is pre-registered N + 1 (Chaco Canyon, "
              f"recovered by comma-decimal parser fix). See analysis log "
              f"2026-05-17 entries for details.")
    else:
        print(f"  [WARN] in-range count differs from pre-registered N by more "
              f"than the documented +1; investigate.")
    print()

    # Subset to in-range structures.
    intersection_in_range = intersection[marios_in_range]
    df_in_range = df.loc[marios_in_range].reset_index(drop=True)
    df_in_range["independent_intersection_lat"] = intersection_in_range

    # Sanity check: are any of the in-range intersections NaN (degenerate
    # geometry case)? These would need special handling.
    n_nan_in_range = int(np.isnan(intersection_in_range).sum())
    if n_nan_in_range > 0:
        print(f"  [WARN] {n_nan_in_range} in-range structures have NaN intersection "
              f"(degenerate geometry).")
        print(f"  These would need to be removed before computing T. Investigating...")
        # Don't exit yet; let the user see what's happening.
    print()

    # ----------------------------------------------------------------- #
    # Primary: T_obs with five poles (I-V)
    # ----------------------------------------------------------------- #
    print("Primary test statistic T (five poles, pre-registration §6)")
    print("-" * 60)
    T_5, d_min_5, nearest_5 = compute_T(intersection_in_range, POLES_PRIMARY)
    print(f"  Pole latitudes (I-V): {list(POLES_PRIMARY.values())}")
    print(f"  N in-range:           {n_in_range}")
    print(f"  T_obs:                {T_5:.6f}°")
    print()
    print(f"  d_min distribution:")
    print(f"    min:                {d_min_5.min():.6f}°")
    print(f"    25th percentile:    {np.percentile(d_min_5, 25):.6f}°")
    print(f"    median:             {np.median(d_min_5):.6f}°")
    print(f"    75th percentile:    {np.percentile(d_min_5, 75):.6f}°")
    print(f"    max:                {d_min_5.max():.6f}°")
    print(f"    mean (= T):         {d_min_5.mean():.6f}°")
    print(f"    std:                {d_min_5.std():.6f}°")
    print()
    print(f"  Counts of structures closest to each pole:")
    pole_names_5 = list(POLES_PRIMARY.keys())
    for idx, name in enumerate(pole_names_5):
        count = int((nearest_5 == idx).sum())
        print(f"    Pole {name:15} ({POLES_PRIMARY[name]:5.1f}°N):  {count:4d}")
    print()

    # ----------------------------------------------------------------- #
    # Sensitivity: T_obs with six poles (I-VI)
    # ----------------------------------------------------------------- #
    print("Sensitivity test statistic T (six poles, pre-registration §8)")
    print("-" * 60)
    T_6, d_min_6, nearest_6 = compute_T(intersection_in_range, POLES_WITH_VI)
    print(f"  Pole latitudes (I-VI): {list(POLES_WITH_VI.values())}")
    print(f"  T_obs (6-pole):        {T_6:.6f}°")
    print(f"  Difference vs 5-pole:  {T_5 - T_6:+.6f}° "
          f"(positive means including Pole VI reduces T)")
    print()
    print(f"  Counts of structures closest to each pole (6-pole):")
    pole_names_6 = list(POLES_WITH_VI.keys())
    for idx, name in enumerate(pole_names_6):
        count = int((nearest_6 == idx).sum())
        print(f"    Pole {name:15} ({POLES_WITH_VI[name]:5.1f}°N):  {count:4d}")
    print()

    # ----------------------------------------------------------------- #
    # Save per-structure distances for use by script 03
    # ----------------------------------------------------------------- #
    distances_df = df_in_range[
        ["SITE NAME", "COUNTRY", "LAT", "LON", "BEARING", "independent_intersection_lat"]
    ].copy()
    for idx, name in enumerate(pole_names_5):
        distances_df[f"d_{name}"] = compute_d_matrix(
            intersection_in_range, POLES_PRIMARY
        )[:, idx]
    distances_df["d_min_5pole"] = d_min_5
    distances_df["nearest_pole_5pole"] = [pole_names_5[i] for i in nearest_5]
    distances_df["d_min_6pole"] = d_min_6
    distances_df["nearest_pole_6pole"] = [pole_names_6[i] for i in nearest_6]
    distances_df.to_csv(DISTANCES_FILE, index=False)
    print(f"Per-structure distances written to {DISTANCES_FILE.relative_to(REPO_ROOT)}")
    print()

    # ----------------------------------------------------------------- #
    # JSON summary
    # ----------------------------------------------------------------- #
    summary = {
        "script": "02_observed_test_statistic.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "target_lon_deg": TARGET_LON_DEG,
        "inclusion_criterion": (
            "data owner's 'Intersection Latitude at Lon 47.1W Line' column "
            "is numeric (parsed with comma-decimal fix)"
        ),
        "n_total": int(n_total),
        "n_in_range": int(n_in_range),
        "n_out_of_range": int(n_out_of_range),
        "expected_n_in_range": EXPECTED_IN_RANGE,
        "in_range_count_matches_prereg": bool(n_in_range == EXPECTED_IN_RANGE),
        "n_nan_intersection_in_range": n_nan_in_range,
        "poles_primary": POLES_PRIMARY,
        "poles_with_vi": POLES_WITH_VI,
        "T_obs_5pole": T_5,
        "T_obs_6pole": T_6,
        "d_min_5pole_summary": {
            "min": float(d_min_5.min()),
            "p25": float(np.percentile(d_min_5, 25)),
            "median": float(np.median(d_min_5)),
            "p75": float(np.percentile(d_min_5, 75)),
            "max": float(d_min_5.max()),
            "mean": float(d_min_5.mean()),
            "std": float(d_min_5.std()),
        },
        "nearest_pole_counts_5pole": {
            name: int((nearest_5 == i).sum()) for i, name in enumerate(pole_names_5)
        },
        "nearest_pole_counts_6pole": {
            name: int((nearest_6 == i).sum()) for i, name in enumerate(pole_names_6)
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print(f"Observed T (5-pole) = {T_5:.4f}°.  Next: Monte Carlo null distribution (script 03).")
    print()


if __name__ == "__main__":
    main()
