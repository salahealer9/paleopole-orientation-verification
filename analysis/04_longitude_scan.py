"""
04_longitude_scan.py
====================

Pre-registered look-elsewhere control per pre-registration §10.

The choice of 47°W as the reference meridian is a researcher degree
of freedom — the data owner identified 47°W as the longitude of
strongest clustering in his exploratory analysis. To control for
this, the pre-registration commits to a two-step longitude scan:

  Step 10a (primary, 5° resolution):
      For each candidate longitude λ_c in {-180°, -175°, ..., +175°}
      (72 longitudes), compute T(λ_c) using the procedure in §6 with
      the meridian relocated to λ_c. Compare T_obs(47°W) to the
      empirical distribution of T_min = min_λ_c T(λ_c) across the
      same M Monte Carlo iterations.

  Step 10b (sensitivity, 1° resolution, conditional):
      If p_LEE at 5° resolution is below 0.05, re-run at 1° resolution
      (360 longitudes) as a higher-resolution sensitivity analysis.

This script implements both steps. The 1° scan is run only if the
5° scan returns p_LEE < 0.05.

Important methodological note
-----------------------------
This script uses the SAME pre-registered (unconditional) null as
script 03. The conditional-null result from script 03b applies only
to the within-hemisphere clustering question and is not the right
comparison for a look-elsewhere scan, which is asking a different
question: across all possible reference meridians, is 47°W unusually
clustered? The unconditional null answers that.

Note also that, because the unconditional null is dominated by
hemisphere mismatch (see analysis log 2026-05-17), the scan will be
substantially affected by which meridians happen to receive
northern-hemisphere intersections from random bearings on this site
distribution. The 47°W meridian, by being a high-latitude meridian,
naturally attracts northern-hemisphere intersections. Other high-
latitude meridians (those passing close to the geographic pole) will
similarly attract them. This is a property of the test as
pre-registered; we report it transparently.

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json (T_obs at 47°W)

Outputs
-------
- results/04_longitude_scan.json: full results including p_LEE.
- results/04_T_obs_by_longitude.npy: T_obs at each scanned longitude.
- results/04_T_min_null_5deg.npy: distribution of T_min across M iterations.
- results/04_T_min_null_1deg.npy: same at 1° resolution (only if run).

Reproducibility
---------------
Same random seed as scripts 03 and 03b: 20260517.

Pre-registration: https://doi.org/10.5281/zenodo.20258204
Status:           CONFIRMATORY (pre-registered §10)
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
SUMMARY_FILE = RESULTS_DIR / "04_longitude_scan.json"
T_BY_LON_FILE = RESULTS_DIR / "04_T_obs_by_longitude.npy"
T_MIN_5DEG_FILE = RESULTS_DIR / "04_T_min_null_5deg.npy"
T_MIN_1DEG_FILE = RESULTS_DIR / "04_T_min_null_1deg.npy"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG_PRIMARY = -47.1

POLES_PRIMARY = {
    "I (current)":   90.0,
    "II":            76.0,
    "III":           72.2,
    "IV":            64.1,
    "V":             52.3,
}

M_ITERATIONS = 10_000
RANDOM_SEED = 20260517
ALPHA = 0.05

# Pre-registration §10a: 5° resolution scan
SCAN_RESOLUTION_PRIMARY = 5.0
# Pre-registration §10b: 1° resolution if p_LEE < 0.05
SCAN_RESOLUTION_FINE = 1.0


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
        print("ERROR: hash mismatch.", file=sys.stderr)
        sys.exit(1)
    print(f"SHA-256 verified: {actual}")
    print()
    return actual


# ---------------------------------------------------------------------------
# Inclusion (same as scripts 02, 03, 03b)
# ---------------------------------------------------------------------------


def parse_marios_intersection_column(series: pd.Series) -> np.ndarray:
    str_series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    values = pd.to_numeric(str_series, errors="coerce").to_numpy()
    return ~np.isnan(values)


# ---------------------------------------------------------------------------
# T computation at an arbitrary meridian
# ---------------------------------------------------------------------------


def compute_T_at_longitude(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings_array: np.ndarray,
    target_lon_deg: float,
    pole_lats: np.ndarray,
) -> np.ndarray:
    """Compute T at a specified meridian for one or many bearing assignments.

    Parameters
    ----------
    lat, lon : (N,)
    bearings_array : (N,) or (M, N)
        Single bearing vector or batch of bearing vectors.
    target_lon_deg : float
    pole_lats : (K,)

    Returns
    -------
    T : float (if 1D bearings) or (M,) array (if 2D)
    """
    if bearings_array.ndim == 1:
        bearings_array = bearings_array[None, :]
        squeeze = True
    else:
        squeeze = False

    M, N = bearings_array.shape
    lat_bc = np.broadcast_to(lat, (M, N))
    lon_bc = np.broadcast_to(lon, (M, N))

    intersections = compute_intersection_lat(
        lat_bc, lon_bc, bearings_array, target_lon_deg
    )

    # Replace any NaN with 0 (defensive, very rare)
    if np.any(np.isnan(intersections)):
        intersections = np.where(np.isnan(intersections), 0.0, intersections)

    # d_min and T
    distances = np.abs(intersections[..., None] - pole_lats[None, None, :])
    d_min = distances.min(axis=-1)
    T = d_min.mean(axis=-1)

    if squeeze:
        return T[0]
    return T


# ---------------------------------------------------------------------------
# Scan procedures
# ---------------------------------------------------------------------------


def compute_T_obs_across_longitudes(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings: np.ndarray,
    longitudes: np.ndarray,
    pole_lats: np.ndarray,
) -> np.ndarray:
    """Compute T_obs at each meridian in *longitudes*."""
    T_obs_by_lon = np.empty(len(longitudes), dtype=float)
    for i, lam in enumerate(longitudes):
        T_obs_by_lon[i] = compute_T_at_longitude(lat, lon, bearings, lam, pole_lats)
    return T_obs_by_lon


def run_longitude_scan_mc(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings_pool: np.ndarray,
    longitudes: np.ndarray,
    pole_lats: np.ndarray,
    M: int,
    seed: int,
    iter_chunk: int = 200,
) -> np.ndarray:
    """For each Monte Carlo iteration, permute bearings, then compute T
    at each longitude in *longitudes*. Return the minimum-T across
    longitudes for each iteration.

    Returns
    -------
    T_min : (M,) array
        For each iteration, T_min = min over longitudes of T at that longitude.
    """
    rng = np.random.default_rng(seed)
    N = len(lat)
    n_lon = len(longitudes)
    T_min_null = np.empty(M, dtype=float)

    n_chunks = (M + iter_chunk - 1) // iter_chunk
    t_start = time.time()

    for chunk_idx in range(n_chunks):
        i_start = chunk_idx * iter_chunk
        i_end = min(i_start + iter_chunk, M)
        size = i_end - i_start

        # Build permuted bearings for this chunk
        permuted = np.empty((size, N), dtype=float)
        for k in range(size):
            permuted[k] = rng.permutation(bearings_pool)

        # Compute T at each longitude for the chunk
        # Shape of T_chunk: (size, n_lon)
        T_chunk = np.empty((size, n_lon), dtype=float)
        for j, lam in enumerate(longitudes):
            T_chunk[:, j] = compute_T_at_longitude(lat, lon, permuted, lam, pole_lats)

        # Min over longitudes per iteration
        T_min_null[i_start:i_end] = T_chunk.min(axis=1)

        if (chunk_idx + 1) % max(1, n_chunks // 10) == 0 or chunk_idx == n_chunks - 1:
            elapsed = time.time() - t_start
            pct = 100.0 * i_end / M
            eta = elapsed * (M - i_end) / max(i_end, 1)
            print(f"  progress: {i_end}/{M} ({pct:5.1f}%)  "
                  f"elapsed {elapsed:6.1f}s  ETA {eta:6.1f}s")

    return T_min_null


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("Pre-registered analysis: longitude scan / look-elsewhere control")
    print("Script: 04_longitude_scan.py")
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

    obs = json.loads(OBS_FILE.read_text())
    T_obs_47W = obs["T_obs_5pole"]
    print(f"T_obs(47°W) from script 02: {T_obs_47W:.6f}°")
    print()

    # Load and filter data
    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    in_range_mask = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )
    df_in = df.loc[in_range_mask].reset_index(drop=True)
    lat = df_in["LAT"].to_numpy(dtype=float)
    lon = df_in["LON"].to_numpy(dtype=float)
    bearings = df_in["BEARING"].to_numpy(dtype=float)
    pole_lats = np.array(list(POLES_PRIMARY.values()))
    N = len(lat)
    print(f"N in-range: {N}")
    print()

    # ----------------------------------------------------------------- #
    # Compute T_obs across all longitudes at 5° resolution
    # ----------------------------------------------------------------- #
    longitudes_5deg = np.arange(-180.0, 180.0, SCAN_RESOLUTION_PRIMARY)
    print(f"Computing T_obs across {len(longitudes_5deg)} longitudes at "
          f"{SCAN_RESOLUTION_PRIMARY}° resolution...")
    T_obs_by_lon_5deg = compute_T_obs_across_longitudes(
        lat, lon, bearings, longitudes_5deg, pole_lats
    )
    np.save(T_BY_LON_FILE, T_obs_by_lon_5deg)

    # Find minimum T_obs across longitudes (which meridian most clusters?)
    i_min = np.argmin(T_obs_by_lon_5deg)
    lon_min_T = longitudes_5deg[i_min]
    T_obs_min = T_obs_by_lon_5deg[i_min]
    print(f"  T_obs at 47°W (pre-registered): {T_obs_47W:.4f}°")
    print(f"  Minimum T_obs across scan: {T_obs_min:.4f}° at longitude {lon_min_T:.1f}°")
    print(f"  T_obs(47°W) rank (from smallest): "
          f"{int((T_obs_by_lon_5deg < T_obs_47W).sum()) + 1} of {len(longitudes_5deg)}")
    print()

    # Print top 10 most-clustered meridians for context
    sorted_idx = np.argsort(T_obs_by_lon_5deg)
    print(f"  Top 10 most-clustered meridians (observed):")
    for rank, idx in enumerate(sorted_idx[:10]):
        marker = "  <-- pre-registered" if abs(longitudes_5deg[idx] - (-45.0)) < 2.5 else ""
        print(f"    rank {rank+1:2d}: lon={longitudes_5deg[idx]:+7.1f}°  "
              f"T={T_obs_by_lon_5deg[idx]:.4f}°{marker}")
    print()

    # ----------------------------------------------------------------- #
    # Step 10a: 5° resolution Monte Carlo for look-elsewhere null
    # ----------------------------------------------------------------- #
    print(f"Step 10a: Running 5° resolution longitude-scan Monte Carlo (M = {M_ITERATIONS})...")
    print("-" * 60)
    T_min_null_5deg = run_longitude_scan_mc(
        lat=lat, lon=lon, bearings_pool=bearings,
        longitudes=longitudes_5deg, pole_lats=pole_lats,
        M=M_ITERATIONS, seed=RANDOM_SEED,
    )
    np.save(T_MIN_5DEG_FILE, T_min_null_5deg)

    # p_LEE per pre-registration §10:
    #   p_LEE = (1 + #{m : T_min^(m) <= T_obs(47°W)}) / (1 + M)
    p_LEE_5deg = (1 + int(np.sum(T_min_null_5deg <= T_obs_47W))) / (1 + M_ITERATIONS)

    print(f"\nLook-elsewhere null distribution (5° resolution, M = {M_ITERATIONS}):")
    print(f"  T_min null mean:   {T_min_null_5deg.mean():.4f}°")
    print(f"  T_min null std:    {T_min_null_5deg.std():.4f}°")
    print(f"  T_min null min:    {T_min_null_5deg.min():.4f}°")
    print(f"  T_min null 1st pct: {np.percentile(T_min_null_5deg, 1):.4f}°")
    print(f"  T_min null 5th pct: {np.percentile(T_min_null_5deg, 5):.4f}°")
    print(f"  T_min null median: {np.median(T_min_null_5deg):.4f}°")
    print(f"  T_min null 95th pct: {np.percentile(T_min_null_5deg, 95):.4f}°")
    print(f"  T_min null max:    {T_min_null_5deg.max():.4f}°")
    print()
    print(f"  T_obs(47°W) = {T_obs_47W:.4f}°")
    print(f"  Count T_min_null <= T_obs(47°W): "
          f"{int((T_min_null_5deg <= T_obs_47W).sum())} / {M_ITERATIONS}")
    print(f"  p_LEE (5° resolution): {p_LEE_5deg:.6f}")

    if p_LEE_5deg < ALPHA:
        verdict_5deg = (
            f"SIGNIFICANT at α = {ALPHA} after look-elsewhere correction"
        )
    else:
        verdict_5deg = (
            f"NOT significant at α = {ALPHA} after look-elsewhere correction"
        )
    print(f"  Verdict: {verdict_5deg}")
    print()

    # ----------------------------------------------------------------- #
    # Step 10b: 1° resolution scan if 5° was significant
    # ----------------------------------------------------------------- #
    if p_LEE_5deg < ALPHA:
        print(f"Step 10b: p_LEE at 5° < {ALPHA}, running 1° resolution sensitivity scan...")
        print("-" * 60)
        longitudes_1deg = np.arange(-180.0, 180.0, SCAN_RESOLUTION_FINE)
        # Note: 360 longitudes × 10,000 iterations is heavier.
        # Cost scales linearly with n_lon, so this should take 5× longer than 5°.
        T_min_null_1deg = run_longitude_scan_mc(
            lat=lat, lon=lon, bearings_pool=bearings,
            longitudes=longitudes_1deg, pole_lats=pole_lats,
            M=M_ITERATIONS, seed=RANDOM_SEED,
        )
        np.save(T_MIN_1DEG_FILE, T_min_null_1deg)

        p_LEE_1deg = (1 + int(np.sum(T_min_null_1deg <= T_obs_47W))) / (1 + M_ITERATIONS)
        print(f"\nLook-elsewhere p_LEE (1° resolution sensitivity): {p_LEE_1deg:.6f}")
    else:
        print(f"Step 10b skipped: p_LEE at 5° resolution is {p_LEE_5deg:.4f}, "
              f"not below {ALPHA}.")
        p_LEE_1deg = None
    print()

    # ----------------------------------------------------------------- #
    # JSON summary
    # ----------------------------------------------------------------- #
    summary = {
        "script": "04_longitude_scan.py",
        "status": "CONFIRMATORY (pre-registered §10)",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "alpha": ALPHA,
        "n_in_range": N,
        "target_lon_deg_primary": TARGET_LON_DEG_PRIMARY,
        "scan_resolution_primary": SCAN_RESOLUTION_PRIMARY,
        "scan_resolution_fine": SCAN_RESOLUTION_FINE,
        "T_obs_47W": T_obs_47W,
        "T_obs_min_across_scan": float(T_obs_min),
        "T_obs_min_longitude": float(lon_min_T),
        "T_obs_47W_rank_in_scan": int((T_obs_by_lon_5deg < T_obs_47W).sum()) + 1,
        "n_longitudes_5deg": int(len(longitudes_5deg)),
        "step_10a_5deg": {
            "p_LEE": p_LEE_5deg,
            "T_min_null_mean": float(T_min_null_5deg.mean()),
            "T_min_null_std": float(T_min_null_5deg.std()),
            "T_min_null_min": float(T_min_null_5deg.min()),
            "T_min_null_p1": float(np.percentile(T_min_null_5deg, 1)),
            "T_min_null_p5": float(np.percentile(T_min_null_5deg, 5)),
            "T_min_null_median": float(np.median(T_min_null_5deg)),
            "count_T_min_null_le_T_obs_47W": int((T_min_null_5deg <= T_obs_47W).sum()),
            "verdict": verdict_5deg,
        },
        "step_10b_1deg": (
            {
                "p_LEE": p_LEE_1deg,
                "executed": True,
            } if p_LEE_1deg is not None else {
                "executed": False,
                "reason": f"p_LEE at 5° resolution ({p_LEE_5deg:.4f}) "
                          f"not below α = {ALPHA}",
            }
        ),
    }

    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print(f"Primary look-elsewhere result: p_LEE (5°) = {p_LEE_5deg:.4f}. {verdict_5deg}")
    print()
    print("Next: per-pole and site-to-pole assignment tests (script 05).")
    print()


if __name__ == "__main__":
    main()
