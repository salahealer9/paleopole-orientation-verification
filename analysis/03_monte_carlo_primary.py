"""
03_monte_carlo_primary.py
=========================

Fourth script in the pre-registered analysis pipeline.

Purpose
-------
Generate the Monte Carlo null distribution of the primary test statistic
T at the 47°W meridian, and compute the primary p-value, per pre-
registration §7.

Procedure (verbatim from pre-registration §7):

  1. Read the 994 in-range structures' coordinates (φᵢ, λᵢ) from the
     database. These remain fixed across all iterations.
  2. Read the 994 in-range folded orientations and store them as a
     vector A.
  3. For each Monte Carlo iteration m ∈ {1, …, M}:
     a. Randomly permute A to produce A^(m), so that each site retains
        its location but receives a randomly drawn folded orientation
        from the empirical pool (sampling without replacement,
        preserving the marginal distribution).
     b. Compute T^(m) using the procedure in §6.
  4. Repeat for M = 10,000 iterations.

  The p-value for the primary test is:
      p = (1 + #{m : T^(m) ≤ T_obs}) / (1 + M)

The 6-pole sensitivity p-value is also computed using the same null
distribution (§8: "Test 8b is pre-registered, will be run regardless
of the outcome of Test 8a, and will be reported transparently as a
sensitivity analysis").

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json (for T_obs values to compare against)

Outputs
-------
- results/03_monte_carlo_primary.json: T_obs, p-values (5-pole and
  6-pole), null distribution percentiles, seed, M.
- results/03_null_distribution_5pole.npy: full vector of T^(m) values
  for the 5-pole primary (binary; committed for exact reproducibility).
- results/03_null_distribution_6pole.npy: same for the 6-pole sensitivity.

Reproducibility
---------------
The pseudo-random seed is hardcoded. The seed value is 20260517,
chosen as the ISO date of the pre-registration deposit. Re-running this
script on the same data should produce bit-for-bit identical results.

Pre-registration: https://doi.org/10.5281/zenodo.20258204
License:          MIT
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
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
OBS_FILE = RESULTS_DIR / "02_observed_test_statistic.json"
SUMMARY_FILE = RESULTS_DIR / "03_monte_carlo_primary.json"
NULL_5POLE_FILE = RESULTS_DIR / "03_null_distribution_5pole.npy"
NULL_6POLE_FILE = RESULTS_DIR / "03_null_distribution_6pole.npy"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1

POLES_PRIMARY = {
    "I (current)":   90.0,
    "II":            76.0,
    "III":           72.2,
    "IV":            64.1,
    "V":             52.3,
}
POLES_WITH_VI = {**POLES_PRIMARY, "VI": 42.0}

# Pre-registration §7: M = 10,000 iterations.
M_ITERATIONS = 10_000

# Pseudo-random seed for reproducibility. Hardcoded per pre-registration §13.
RANDOM_SEED = 20260517

# Pre-registered significance threshold (§9): α = 0.05, one-sided.
ALPHA_PRIMARY = 0.05


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
# Parse Mario's classification column (same as script 02)
# ---------------------------------------------------------------------------


def parse_marios_intersection_column(series: pd.Series) -> np.ndarray:
    """Return a bool array marking rows the data owner classifies as in-range
    (numeric value in the column, comma-decimal accepted)."""
    str_series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    values = pd.to_numeric(str_series, errors="coerce").to_numpy()
    return ~np.isnan(values)


# ---------------------------------------------------------------------------
# Test statistic (same as script 02)
# ---------------------------------------------------------------------------


def compute_T_vectorized(
    intersection_lats: np.ndarray,
    pole_lats: np.ndarray,
) -> np.ndarray:
    """Compute T for a batch of intersection-latitude vectors.

    Parameters
    ----------
    intersection_lats : array of shape (M, N) or (N,)
        Each row is a vector of N intersection latitudes for one
        Monte Carlo iteration.
    pole_lats : array of shape (K,)

    Returns
    -------
    T : array of shape (M,) if input is 2D, scalar if input is 1D.
        T = (1/N) Σ_i min_k |φ'_i - φ_k| for each iteration.
    """
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False

    # Shape: (M, N, K)
    distances = np.abs(intersection_lats[..., None] - pole_lats[None, None, :])
    # Min over poles: shape (M, N)
    d_min = distances.min(axis=-1)
    # Mean over structures: shape (M,)
    T = d_min.mean(axis=-1)

    if squeeze:
        return T[0]
    return T


# ---------------------------------------------------------------------------
# Monte Carlo procedure
# ---------------------------------------------------------------------------


def run_monte_carlo(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings_pool: np.ndarray,
    pole_lats: np.ndarray,
    target_lon_deg: float,
    M: int,
    seed: int,
    chunk_size: int = 500,
) -> np.ndarray:
    """Run the Monte Carlo null permutation per pre-registration §7.

    The site coordinates (lat, lon) are fixed across iterations. For each
    iteration, the bearings_pool is randomly permuted and assigned to the
    sites; then T is computed.

    For memory efficiency, we process iterations in chunks: each chunk
    builds a (chunk_size, N) array of permuted bearings, computes the
    chunk_size intersection latitudes in one vectorized pass, computes
    T for each, and accumulates the results.

    Parameters
    ----------
    lat, lon : arrays of shape (N,)
        Site coordinates, fixed.
    bearings_pool : array of shape (N,)
        The empirical distribution of folded orientations to permute.
    pole_lats : array of shape (K,)
        The pole latitudes to test clustering against.
    target_lon_deg : float
        Target meridian longitude.
    M : int
        Number of Monte Carlo iterations.
    seed : int
        Pseudo-random seed for reproducibility.
    chunk_size : int
        Number of iterations to process per vectorized batch.

    Returns
    -------
    T_null : array of shape (M,)
        The null distribution of T.
    """
    rng = np.random.default_rng(seed)
    N = len(lat)

    T_null = np.empty(M, dtype=float)
    n_chunks = (M + chunk_size - 1) // chunk_size

    t_start = time.time()
    for chunk_idx in range(n_chunks):
        i_start = chunk_idx * chunk_size
        i_end = min(i_start + chunk_size, M)
        size = i_end - i_start

        # Build (size, N) array of permuted bearings: each row is one
        # permutation of bearings_pool. This is the §7 step 3a operation.
        permuted_bearings = np.empty((size, N), dtype=float)
        for k in range(size):
            permuted_bearings[k] = rng.permutation(bearings_pool)

        # Broadcast lat/lon to (size, N) to match permuted_bearings.
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))

        # Compute intersection latitudes for the whole chunk in one call.
        # The geometry primitive vectorizes over the last axis.
        intersections = compute_intersection_lat(
            lat_bc, lon_bc, permuted_bearings, target_lon_deg
        )

        # NaN intersections from degenerate geometry can occur for specific
        # (site, bearing) pairs (great circle coincides with target meridian).
        # Per pre-registration §7, the null preserves the empirical
        # distribution of bearings, so degenerate combinations are part of
        # the null space. Replace NaN with a large distance penalty for T
        # computation, equivalent to "this orientation does not contribute
        # to clustering". A reasonable choice is to skip them entirely by
        # using nanmean for d_min — but we want consistent N across
        # iterations to match the observed-data treatment. Following the
        # observed-data convention (which produces a numeric d_i for every
        # in-range structure under raw geometry), we treat any NaN from
        # the chunk as a max-distance contribution by replacing with a
        # very large value.
        # In practice, NaN should be rare (only when a permuted bearing
        # combines with a site coord to exactly hit the degenerate case).
        if np.any(np.isnan(intersections)):
            n_nan = int(np.isnan(intersections).sum())
            print(f"  [note] chunk {chunk_idx}: {n_nan} NaN intersections from "
                  f"degenerate geometry; treated as max-distance for T.")
            # Replace NaN with 0 (latitude on equator) — this will produce
            # a d_i value but make it large for northern poles. The chance
            # of hitting exact degeneracy under random permutation is
            # vanishingly small (would require specific combinations of
            # (site, bearing) yielding norm < 1e-12), so this branch is
            # mostly defensive.
            intersections = np.where(np.isnan(intersections), 0.0, intersections)

        # Compute T for each iteration in the chunk
        T_chunk = compute_T_vectorized(intersections, pole_lats)
        T_null[i_start:i_end] = T_chunk

        # Progress report every 10% or so
        if (chunk_idx + 1) % max(1, n_chunks // 10) == 0 or chunk_idx == n_chunks - 1:
            elapsed = time.time() - t_start
            pct = 100.0 * (i_end) / M
            eta = elapsed * (M - i_end) / max(i_end, 1)
            print(f"  progress: {i_end}/{M} ({pct:5.1f}%)  "
                  f"elapsed {elapsed:5.1f}s  ETA {eta:5.1f}s")

    return T_null


def compute_p_value(T_obs: float, T_null: np.ndarray) -> float:
    """Compute the one-sided p-value per pre-registration §7:
        p = (1 + #{m : T^(m) <= T_obs}) / (1 + M)
    """
    M = len(T_null)
    return (1 + int(np.sum(T_null <= T_obs))) / (1 + M)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("Pre-registered analysis: Monte Carlo null distribution (primary)")
    print("Script: 03_monte_carlo_primary.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Iterations: M = {M_ITERATIONS}")
    print("=" * 60)
    print()

    verified_hash = verify_hash()
    n_tests = run_self_tests()
    print(f"Geometry self-test: {n_tests} cases passed.")
    print()

    # Load observed T values
    if not OBS_FILE.exists():
        print(f"ERROR: {OBS_FILE} not found. Run script 02 first.", file=sys.stderr)
        sys.exit(1)
    obs = json.loads(OBS_FILE.read_text())
    T_obs_5 = obs["T_obs_5pole"]
    T_obs_6 = obs["T_obs_6pole"]
    expected_n = obs["n_in_range"]
    print(f"Loaded observed T from script 02:")
    print(f"  T_obs (5-pole): {T_obs_5:.6f}°")
    print(f"  T_obs (6-pole): {T_obs_6:.6f}°")
    print(f"  N in-range:     {expected_n}")
    print()

    # Load data and filter to in-range (data owner's classification)
    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    in_range_mask = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )
    n_in_range = int(in_range_mask.sum())
    print(f"In-range structures: {n_in_range}")

    if n_in_range != expected_n:
        print(f"ERROR: in-range count from script 02 ({expected_n}) does not match "
              f"the current count ({n_in_range}). Investigate before proceeding.",
              file=sys.stderr)
        sys.exit(1)
    print()

    df_in = df.loc[in_range_mask].reset_index(drop=True)
    lat = df_in["LAT"].to_numpy(dtype=float)
    lon = df_in["LON"].to_numpy(dtype=float)
    bearings = df_in["BEARING"].to_numpy(dtype=float)

    print(f"Empirical bearing distribution (pool for permutation):")
    print(f"  min:    {bearings.min():+.2f}°")
    print(f"  max:    {bearings.max():+.2f}°")
    print(f"  mean:   {bearings.mean():+.2f}°")
    print(f"  median: {np.median(bearings):+.2f}°")
    print(f"  std:    {bearings.std():.2f}°")
    print()

    # ----------------------------------------------------------------- #
    # 5-pole Monte Carlo
    # ----------------------------------------------------------------- #
    print("Running 5-pole Monte Carlo (primary)...")
    print("-" * 60)
    pole_lats_5 = np.array(list(POLES_PRIMARY.values()))
    T_null_5 = run_monte_carlo(
        lat=lat, lon=lon, bearings_pool=bearings,
        pole_lats=pole_lats_5,
        target_lon_deg=TARGET_LON_DEG,
        M=M_ITERATIONS, seed=RANDOM_SEED,
    )
    print()

    p_5 = compute_p_value(T_obs_5, T_null_5)
    print(f"5-pole results (PRIMARY):")
    print(f"  T_obs:           {T_obs_5:.6f}°")
    print(f"  Null mean:       {T_null_5.mean():.6f}°")
    print(f"  Null std:        {T_null_5.std():.6f}°")
    print(f"  Null min:        {T_null_5.min():.6f}°")
    print(f"  Null 1st pct:    {np.percentile(T_null_5, 1):.6f}°")
    print(f"  Null 5th pct:    {np.percentile(T_null_5, 5):.6f}°")
    print(f"  Null median:     {np.median(T_null_5):.6f}°")
    print(f"  Null max:        {T_null_5.max():.6f}°")
    print(f"  Count T_null <= T_obs:  {int((T_null_5 <= T_obs_5).sum())} / {M_ITERATIONS}")
    print(f"  p-value:         {p_5:.6f}")
    if p_5 < 0.01:
        verdict = "HIGHLY SIGNIFICANT (p < 0.01)"
    elif p_5 < ALPHA_PRIMARY:
        verdict = f"SIGNIFICANT (p < {ALPHA_PRIMARY})"
    else:
        verdict = f"NOT SIGNIFICANT at pre-registered α = {ALPHA_PRIMARY}"
    print(f"  Verdict (per pre-registration §9): {verdict}")
    print()

    # ----------------------------------------------------------------- #
    # 6-pole Monte Carlo (sensitivity)
    # ----------------------------------------------------------------- #
    print("Running 6-pole Monte Carlo (sensitivity per §8)...")
    print("-" * 60)
    pole_lats_6 = np.array(list(POLES_WITH_VI.values()))
    # Use the SAME seed so the permutations are the same — this means the
    # 6-pole result differs from the 5-pole result only because of the
    # additional pole, not because of different permutations.
    T_null_6 = run_monte_carlo(
        lat=lat, lon=lon, bearings_pool=bearings,
        pole_lats=pole_lats_6,
        target_lon_deg=TARGET_LON_DEG,
        M=M_ITERATIONS, seed=RANDOM_SEED,
    )
    print()

    p_6 = compute_p_value(T_obs_6, T_null_6)
    print(f"6-pole results (SENSITIVITY):")
    print(f"  T_obs:           {T_obs_6:.6f}°")
    print(f"  Null mean:       {T_null_6.mean():.6f}°")
    print(f"  Null std:        {T_null_6.std():.6f}°")
    print(f"  Null 5th pct:    {np.percentile(T_null_6, 5):.6f}°")
    print(f"  Count T_null <= T_obs:  {int((T_null_6 <= T_obs_6).sum())} / {M_ITERATIONS}")
    print(f"  p-value:         {p_6:.6f}")
    print()

    # ----------------------------------------------------------------- #
    # Save outputs
    # ----------------------------------------------------------------- #
    np.save(NULL_5POLE_FILE, T_null_5)
    np.save(NULL_6POLE_FILE, T_null_6)
    print(f"Null distribution arrays saved:")
    print(f"  {NULL_5POLE_FILE.relative_to(REPO_ROOT)}")
    print(f"  {NULL_6POLE_FILE.relative_to(REPO_ROOT)}")
    print()

    summary = {
        "script": "03_monte_carlo_primary.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "alpha_primary": ALPHA_PRIMARY,
        "n_in_range": n_in_range,
        "target_lon_deg": TARGET_LON_DEG,
        "poles_primary": POLES_PRIMARY,
        "poles_with_vi": POLES_WITH_VI,
        "primary_5pole": {
            "T_obs": T_obs_5,
            "T_null_mean": float(T_null_5.mean()),
            "T_null_std": float(T_null_5.std()),
            "T_null_min": float(T_null_5.min()),
            "T_null_p1": float(np.percentile(T_null_5, 1)),
            "T_null_p5": float(np.percentile(T_null_5, 5)),
            "T_null_median": float(np.median(T_null_5)),
            "T_null_p95": float(np.percentile(T_null_5, 95)),
            "T_null_max": float(T_null_5.max()),
            "count_T_null_le_T_obs": int((T_null_5 <= T_obs_5).sum()),
            "p_value": p_5,
            "verdict": verdict,
        },
        "sensitivity_6pole": {
            "T_obs": T_obs_6,
            "T_null_mean": float(T_null_6.mean()),
            "T_null_std": float(T_null_6.std()),
            "T_null_p5": float(np.percentile(T_null_6, 5)),
            "count_T_null_le_T_obs": int((T_null_6 <= T_obs_6).sum()),
            "p_value": p_6,
        },
    }

    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print(f"Primary result: T_obs (5-pole) = {T_obs_5:.4f}°, "
          f"p = {p_5:.4f}. {verdict}")
    print()
    print("Next: longitude scan / look-elsewhere control (script 04).")
    print()


if __name__ == "__main__":
    main()
