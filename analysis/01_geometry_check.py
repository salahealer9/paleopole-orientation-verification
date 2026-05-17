"""
01_geometry_check.py
====================

Second script in the pre-registered analysis pipeline for the paleopole
orientation verification project.

Purpose
-------
The database file contains a pre-computed column,
``Intersection Latitude at Lon 47.1W Line``, derived by the data owner.
The pre-registered analysis computes great-circle intersections
INDEPENDENTLY from the raw ``LAT``, ``LON``, and ``BEARING`` columns.
This script validates that the independent geometry pipeline produces
results consistent with the data owner's pre-computed values, so that
any disagreement is identified and characterised BEFORE the test
statistic is computed.

Specifically, this script:

1. Verifies the database SHA-256 hash (same as script 00).
2. Loads the 'All Data' sheet.
3. For each row, computes the latitude at which the great circle
   defined by (LAT, LON, BEARING) crosses the 47.1°W meridian — using
   pure spherical trigonometry, with no reference to Mario's value.
4. Compares the independent computation to Mario's pre-computed column
   row by row.
5. Reports agreement statistics and writes a row-level CSV of any
   discrepancies above a configurable threshold.
6. Cross-checks that rows Mario marks as 'No Intersect 47.1W' are
   identified as out-of-range by the independent computation.

This script does NOT run any test statistic, generate any plot of the
orientation distribution, or report any clustering. It is a geometry
sanity check.

Geometry: great-circle / meridian intersection
----------------------------------------------
A structure at (φ, λ) on the sphere with a bearing β (measured clockwise
from true north) defines an initial direction of travel along the surface.
The great circle through (φ, λ) in that direction can be parameterised
analytically. We solve for the latitude at which this great circle
crosses the target meridian λ₀ = -47.1°.

The pole of the great circle has direction perpendicular to both the
position vector at (φ, λ) and the unit tangent vector pointing along
bearing β at that point. In Cartesian coordinates:

    r = (cos φ cos λ, cos φ sin λ, sin φ)
    t̂ = (-sin β sin λ - cos β sin φ cos λ,
          sin β cos λ - cos β sin φ sin λ,
          cos β cos φ)
    n̂ = r × t̂ / |r × t̂|

The great circle is then the set of unit vectors u with u · n̂ = 0.
Intersecting with the meridian λ = λ₀ gives a pair of latitudes
(antipodal); we select the one in the forward direction of travel.

Convention for BEARING
----------------------
The data owner defines BEARING as the folded northernface azimuth in
[-45°, +45°], measured relative to current true north. A bearing of 0
means the northernface points to current geographic north. A positive
bearing rotates eastward; a negative bearing rotates westward.

Edge cases
----------
- Structures very close to the poles: the meridian crossing is
  geometrically degenerate. Handled by checking the magnitude of the
  great-circle pole vector and treating tiny magnitudes as 'no
  intersection' (NaN).
- Great circles parallel to the target meridian: no intersection.
  Handled by checking the sine of the inclination angle.

Usage
-----
From the repository root:

    python analysis/01_geometry_check.py

Outputs
-------
- ``results/01_geometry_comparison.json``: summary statistics
- ``results/01_geometry_discrepancies.csv``: row-level details for any
  rows whose independent latitude disagrees with Mario's pre-computed
  value by more than a small tolerance.

Pre-registration: https://doi.org/10.5281/zenodo.20258204
Repository:       https://github.com/salahealer9/paleopole-orientation-verification
Author:           Salah-Eddin Gherbi
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

# The reference meridian for the comparison. The data owner uses 47.1°W,
# which is a longitude of -47.1° in the standard signed convention.
TARGET_LON_DEG = -47.1

# Discrepancy threshold for flagging individual rows in the output CSV.
# Rows whose independent computation disagrees with Mario's value by
# more than this many degrees are recorded.
DISCREPANCY_THRESHOLD_DEG = 0.1


# ---------------------------------------------------------------------------
# Hash verification (duplicated from 00 to make this script self-contained)
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
# Geometry: great-circle intersection with a meridian
# ---------------------------------------------------------------------------


def lat_lon_bearing_to_great_circle_pole(
    lat_deg: np.ndarray,
    lon_deg: np.ndarray,
    bearing_deg: np.ndarray,
) -> np.ndarray:
    """Return the unit pole vector (n̂) of the great circle through
    (lat, lon) along the initial bearing.

    The pole of a great circle is the axis perpendicular to the plane
    containing the great circle, normalised to unit length.

    Parameters
    ----------
    lat_deg, lon_deg, bearing_deg : arrays of degrees, all the same shape.

    Returns
    -------
    n_hat : array of shape (N, 3)
        Unit vectors in Earth-centered Cartesian coordinates.
    """
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    beta = np.deg2rad(bearing_deg)

    # Position vector r at (lat, lon) on the unit sphere.
    r_x = np.cos(lat) * np.cos(lon)
    r_y = np.cos(lat) * np.sin(lon)
    r_z = np.sin(lat)

    # Local east and north unit vectors at (lat, lon).
    #   east  = (-sin λ, cos λ, 0)
    #   north = (-sin φ cos λ, -sin φ sin λ, cos φ)
    east_x = -np.sin(lon)
    east_y = np.cos(lon)
    east_z = np.zeros_like(lat)

    north_x = -np.sin(lat) * np.cos(lon)
    north_y = -np.sin(lat) * np.sin(lon)
    north_z = np.cos(lat)

    # Tangent vector t̂ in the direction of the bearing.
    # Bearing β is measured clockwise from local north, so:
    #   t̂ = cos β · north + sin β · east
    t_x = np.cos(beta) * north_x + np.sin(beta) * east_x
    t_y = np.cos(beta) * north_y + np.sin(beta) * east_y
    t_z = np.cos(beta) * north_z + np.sin(beta) * east_z

    # Pole n̂ = r × t̂  (then normalise).
    n_x = r_y * t_z - r_z * t_y
    n_y = r_z * t_x - r_x * t_z
    n_z = r_x * t_y - r_y * t_x

    norm = np.sqrt(n_x**2 + n_y**2 + n_z**2)
    # Guard against degenerate cases (essentially r ∥ t̂, which shouldn't
    # happen for valid inputs but we protect against numerical noise).
    norm = np.where(norm < 1e-12, np.nan, norm)
    return np.stack([n_x / norm, n_y / norm, n_z / norm], axis=-1)


def great_circle_meridian_intersection_lat(
    pole: np.ndarray,
    target_lon_deg: float,
) -> np.ndarray:
    """Compute the latitude where a great circle (specified by its pole
    vector) crosses the meridian at longitude *target_lon_deg*.

    A point on the meridian λ₀ has the form:
        u(φ) = (cos φ cos λ₀, cos φ sin λ₀, sin φ)

    The intersection condition is u · n̂ = 0, which gives:
        cos φ (n_x cos λ₀ + n_y sin λ₀) + sin φ · n_z = 0
        tan φ = -(n_x cos λ₀ + n_y sin λ₀) / n_z

    Latitude φ is bounded by ±90°, so ``arctan`` (range (-π/2, π/2)) is
    the correct inverse — NOT ``arctan2``, which would occasionally
    place the answer on the antipodal half-meridian.

    Special cases:
      - If the great circle coincides with the target meridian (both
        numerator and denominator vanish), the intersection is the
        entire meridian; NaN is returned.
      - If the great circle is "perpendicular" so that n_z ≈ 0 but the
        numerator is nonzero, the great circle passes through both
        geographic poles and crosses the target meridian at BOTH ±90°
        simultaneously. The convention adopted here is to return +90°
        (the north pole), consistent with the data owner's convention,
        because the proposed paleopoles all lie in the northern hemisphere
        and the south pole intersection is not a candidate for the
        clustering claim being tested.

    Parameters
    ----------
    pole : array of shape (N, 3)
    target_lon_deg : float

    Returns
    -------
    lat_deg : array of shape (N,)
    """
    lam = np.deg2rad(target_lon_deg)

    n_x = pole[..., 0]
    n_y = pole[..., 1]
    n_z = pole[..., 2]

    numerator = -(n_x * np.cos(lam) + n_y * np.sin(lam))
    denominator = n_z

    # Detect the degenerate case where both vanish (great circle coincides
    # with the target meridian itself).
    degenerate = (np.abs(numerator) < 1e-10) & (np.abs(denominator) < 1e-10)

    # Detect the pole-passing case: great circle passes through both
    # geographic poles, so intersection with any meridian is at ±90°.
    # By convention (matching the data owner and the northern-hemisphere
    # focus of the proposed poles), return +90° in this case.
    pole_passing = (np.abs(denominator) < 1e-10) & ~degenerate

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = numerator / denominator
        lat = np.rad2deg(np.arctan(ratio))

    # Apply special-case overrides.
    lat = np.where(pole_passing, 90.0, lat)
    invalid = np.isnan(n_x) | np.isnan(n_y) | np.isnan(n_z)
    lat = np.where(degenerate | invalid, np.nan, lat)
    return lat


def compute_independent_intersection_lat(
    lat_deg: np.ndarray,
    lon_deg: np.ndarray,
    bearing_deg: np.ndarray,
    target_lon_deg: float = TARGET_LON_DEG,
) -> np.ndarray:
    """End-to-end: from (lat, lon, bearing) compute the latitude where
    the great circle crosses *target_lon_deg*."""
    pole = lat_lon_bearing_to_great_circle_pole(lat_deg, lon_deg, bearing_deg)
    return great_circle_meridian_intersection_lat(pole, target_lon_deg)


def run_geometry_self_tests() -> None:
    """Run a small set of analytically-known test cases against the
    geometry primitives. Aborts the script with an error if any test
    fails. Provides defence in depth against silent regressions.
    """
    # Each tuple: (lat, lon, bearing, expected_intersection, tolerance, description)
    # 'None' for expected means: assert NaN.
    cases = [
        # Bearing 0 from a site ON the target meridian: degenerate (great
        # circle IS the target meridian).
        (0.0, -47.1, 0.0, None, 0.0, "On-meridian, bearing 0 — degenerate"),
        (45.0, -47.1, 0.0, None, 0.0, "On-meridian at lat 45, bearing 0 — degenerate"),
        # A site on the target meridian at the equator with non-zero
        # bearing: intersection is the site itself (lat 0).
        (0.0, -47.1, -45.0, 0.0, 1e-6, "On-meridian, bearing -45 — intersection at site"),
        # Equator-tracing great circle: intersects at lat 0.
        (0.0, -30.0, 90.0, 0.0, 1e-6, "Equator at bearing 90 — traces equator"),
        # Hand-computed general case.
        (30.0, -40.0, -30.0, 39.356, 0.01, "Hand-computed: (30, -40), bearing -30"),
        # Pole-passing case: bearing 0 from a site off the target meridian
        # produces a great circle through both poles; by northern-hemisphere
        # convention we return +90°, matching the data owner's convention.
        (20.4476, -97.3779, 0.0, 90.0, 1e-6, "Pole-passing case (El Tajín proxy): bearing 0"),
        (36.4222, 9.2183, 0.0, 90.0, 1e-6, "Pole-passing case (Dougga proxy): bearing 0"),
    ]

    failures = []
    for lat, lon, bearing, expected, tol, description in cases:
        result = compute_independent_intersection_lat(
            np.atleast_1d(lat), np.atleast_1d(lon), np.atleast_1d(bearing)
        )[0]
        if expected is None:
            if not np.isnan(result):
                failures.append(f"{description}: expected NaN, got {result}")
        else:
            if np.isnan(result) or abs(result - expected) > tol:
                failures.append(
                    f"{description}: expected {expected}, got {result}, tol={tol}"
                )

    if failures:
        print("GEOMETRY SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    print(f"Geometry self-test: {len(cases)} cases passed.")
    print()


# ---------------------------------------------------------------------------
# Comparison against Mario's pre-computed column
# ---------------------------------------------------------------------------


def parse_marios_intersection_column(series: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Parse the 'Intersection Latitude at Lon 47.1W Line' column,
    which has dtype 'object' because out-of-range rows contain text
    like 'No Intersect 47.1W' instead of a number.

    Returns
    -------
    values : float array (NaN for non-numeric entries)
    is_no_intersect : bool array (True where the entry is the
        'No Intersect 47.1W' marker or any non-numeric value)
    """
    values = pd.to_numeric(series, errors="coerce").to_numpy()
    is_no_intersect = np.isnan(values)
    return values, is_no_intersect


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
    run_geometry_self_tests()

    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    n = len(df)
    print(f"Loaded {n} rows from sheet {PRIMARY_SHEET!r}.")
    print()

    lat = df["LAT"].to_numpy(dtype=float)
    lon = df["LON"].to_numpy(dtype=float)
    bearing = df["BEARING"].to_numpy(dtype=float)

    # Mario's pre-computed values
    marios_values, marios_no_intersect = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )

    # Independent computation
    independent = compute_independent_intersection_lat(lat, lon, bearing, TARGET_LON_DEG)

    # ----------------------------------------------------------------- #
    # Comparison
    # ----------------------------------------------------------------- #
    print("Independent vs. pre-computed intersection latitudes")
    print("-" * 60)

    # For rows where Mario has a numeric value, compare directly.
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

    # ----------------------------------------------------------------- #
    # Discrepancies above threshold
    # ----------------------------------------------------------------- #
    discrepancy_mask = np.zeros(n, dtype=bool)
    discrepancy_mask[both_numeric] = abs_diff > DISCREPANCY_THRESHOLD_DEG
    # Also flag rows where Mario and independent disagree on whether
    # there is an intersection at all.
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
        print("No discrepancies above threshold — independent computation matches "
              "the data owner's values.")
    print()

    # ----------------------------------------------------------------- #
    # JSON summary
    # ----------------------------------------------------------------- #
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
        "discrepancy_threshold_used": DISCREPANCY_THRESHOLD_DEG,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print("Geometry check complete. Next: design the test statistic implementation (script 02).")
    print()


if __name__ == "__main__":
    main()
