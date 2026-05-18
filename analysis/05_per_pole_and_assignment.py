"""
05_per_pole_and_assignment.py
==============================

Sixth script in the analysis pipeline. Implements pre-registration
§11(a) (per-pole confirmatory test) and §11(b) (site-to-pole
assignment test), each under both the pre-registered unconditional
null and an exploratory conditional null.

§11(a) — Per-pole confirmatory test (pre-registered)
----------------------------------------------------
For each of the five (or six) poles individually, compute the count
of structures whose great-circle intersection on the 47°W meridian
falls within ±1.5° of φ_k. Compare to the null distribution of the
same count under permuted orientations. Šidák-corrected p-values
across five (or six) simultaneous tests at family-wise α = 0.05.

§11(b) — Site-to-pole assignment test (pre-registered)
------------------------------------------------------
For sites in the database matched to specific poles, test whether each
site's orientation points to its assigned pole within ±1.5° more often
than expected under the null.

Implementation of §11(b): the pre-registration assumed an explicit
assignment table. Inspection of the database file (script 00, plus
schema inspection of the other sheets) found no per-site pole-
assignment column. The data owner's published pole assignments live
on his website as named-site lists per pole, not in the data file.

Per the analysis log entry for 2026-05-17 on this decision, we
operationalise the assignment as follows: each in-range structure's
assigned pole is the nearest of {52.3, 64.1, 72.2, 76.0, 90.0} (or
six poles for sensitivity) to that structure's MARIO-PUBLISHED
intersection latitude. This treats the assignment as whatever the
data owner's pipeline implicitly produces, and asks whether our
independent geometry confirms the assignment at the per-site level.

For each structure i:
  assigned_pole_lat[i] = nearest pole to mario_intersection_lat[i]
  observed_match[i]    = 1 if |independent_intersection_lat[i]
                                - assigned_pole_lat[i]| <= 1.5°
  observed_count       = sum(observed_match[i])

Under the null, the independent intersection latitudes are recomputed
from permuted bearings, but Mario's published assignment stays fixed.

Conditional-null variants (exploratory, per §12 point 3)
--------------------------------------------------------
Both tests are run under the same Metropolis swap chain null as
script 03b, in addition to the pre-registered unconditional null.

This script reads the compatibility matrix produced implicitly by the
same logic in 03b, but re-builds it here for self-containedness.

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json (for the in-range N)
- results/02_per_structure_distances.csv (for per-structure data)

Outputs
-------
- results/05_per_pole_and_assignment.json
- results/05_per_pole_observed_counts.csv: per-pole observed counts
- results/05_null_per_pole_unconditional.npy: (M, K) array of per-pole
  counts under the unconditional null
- results/05_null_per_pole_conditional.npy: same under conditional null
- results/05_null_assignment_unconditional.npy: (M,) array of
  observed_count under unconditional null
- results/05_null_assignment_conditional.npy: same under conditional null

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
SUMMARY_FILE = RESULTS_DIR / "05_per_pole_and_assignment.json"
PER_POLE_OBS_FILE = RESULTS_DIR / "05_per_pole_observed_counts.csv"
PER_POLE_NULL_UNCOND = RESULTS_DIR / "05_null_per_pole_unconditional.npy"
PER_POLE_NULL_COND = RESULTS_DIR / "05_null_per_pole_conditional.npy"
ASSIGN_NULL_UNCOND = RESULTS_DIR / "05_null_assignment_unconditional.npy"
ASSIGN_NULL_COND = RESULTS_DIR / "05_null_assignment_conditional.npy"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN_HEMISPHERE_THRESHOLD = 0.0

POLES_PRIMARY = {
    "I (current)":   90.0,
    "II":            76.0,
    "III":           72.2,
    "IV":            64.1,
    "V":             52.3,
}
POLES_WITH_VI = {**POLES_PRIMARY, "VI": 42.0}

# Pre-registration §11(a): ±1.5° tolerance window around each pole.
TOLERANCE_DEG = 1.5

M_ITERATIONS = 10_000
RANDOM_SEED = 20260517
ALPHA = 0.05

# Same chain parameters as script 03b.
SWAPS_PER_SAMPLE = 2 * 994
WARMUP_SWAPS = 5 * 994


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
    expected = read_reference_hash(HASH_FILE)
    actual = compute_sha256(DATA_FILE)
    if expected != actual:
        print("ERROR: hash mismatch.", file=sys.stderr)
        sys.exit(1)
    print(f"SHA-256 verified: {actual}")
    print()
    return actual


# ---------------------------------------------------------------------------
# Inclusion + Mario's published intersection latitudes (for §11(b) assignment)
# ---------------------------------------------------------------------------


def parse_marios_intersection_column(series: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Returns (mario_values, in_range_mask)."""
    str_series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    values = pd.to_numeric(str_series, errors="coerce").to_numpy()
    return values, ~np.isnan(values)


# ---------------------------------------------------------------------------
# Per-pole and assignment test statistics
# ---------------------------------------------------------------------------


def compute_per_pole_counts(
    intersection_lats: np.ndarray,
    pole_lats: np.ndarray,
    tolerance: float,
) -> np.ndarray:
    """For each pole, count structures whose intersection lat is within
    ±tolerance of the pole lat.

    Parameters
    ----------
    intersection_lats : (M, N) or (N,)
    pole_lats : (K,)
    tolerance : float (degrees)

    Returns
    -------
    counts : (M, K) or (K,) array of int
    """
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False

    # Shape (M, N, K)
    within = np.abs(intersection_lats[..., None] - pole_lats[None, None, :]) <= tolerance
    # Sum over N (structures)
    counts = within.sum(axis=1).astype(int)

    if squeeze:
        return counts[0]
    return counts


def compute_assignment_match_count(
    intersection_lats: np.ndarray,
    assigned_pole_lats: np.ndarray,
    tolerance: float,
) -> np.ndarray:
    """For each structure i and each (possibly permuted) intersection
    latitude, check whether the intersection is within ±tolerance of the
    structure's pre-fixed assigned pole. Return the count.

    Parameters
    ----------
    intersection_lats : (M, N) or (N,)
    assigned_pole_lats : (N,)
        Fixed across all iterations: each structure's assigned pole
        derived from Mario's published intersection latitudes.
    tolerance : float

    Returns
    -------
    count : (M,) or scalar
    """
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False

    diff = np.abs(intersection_lats - assigned_pole_lats[None, :])
    matches = (diff <= tolerance).sum(axis=1).astype(int)

    if squeeze:
        return int(matches[0])
    return matches


def sidak_correction(p: float, k: int) -> float:
    """Šidák-correct a single p-value for k simultaneous tests."""
    return 1.0 - (1.0 - p) ** k


# ---------------------------------------------------------------------------
# Unconditional null Monte Carlo
# ---------------------------------------------------------------------------


def run_unconditional_mc(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings_pool: np.ndarray,
    pole_lats: np.ndarray,
    assigned_pole_lats: np.ndarray,
    target_lon_deg: float,
    tolerance: float,
    M: int,
    seed: int,
    chunk_size: int = 500,
) -> tuple[np.ndarray, np.ndarray]:
    """Permute bearings unrestrictedly; for each iteration return:
    - per-pole counts (M, K)
    - assignment match counts (M,)
    """
    rng = np.random.default_rng(seed)
    N = len(lat)
    K = len(pole_lats)

    null_per_pole = np.empty((M, K), dtype=int)
    null_assign = np.empty(M, dtype=int)

    n_chunks = (M + chunk_size - 1) // chunk_size
    t_start = time.time()

    for chunk_idx in range(n_chunks):
        i_start = chunk_idx * chunk_size
        i_end = min(i_start + chunk_size, M)
        size = i_end - i_start

        permuted = np.empty((size, N), dtype=float)
        for k in range(size):
            permuted[k] = rng.permutation(bearings_pool)

        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))

        intersections = compute_intersection_lat(
            lat_bc, lon_bc, permuted, target_lon_deg
        )
        if np.any(np.isnan(intersections)):
            intersections = np.where(np.isnan(intersections), 0.0, intersections)

        null_per_pole[i_start:i_end] = compute_per_pole_counts(
            intersections, pole_lats, tolerance
        )
        null_assign[i_start:i_end] = compute_assignment_match_count(
            intersections, assigned_pole_lats, tolerance
        )

        if (chunk_idx + 1) % max(1, n_chunks // 10) == 0 or chunk_idx == n_chunks - 1:
            elapsed = time.time() - t_start
            pct = 100.0 * i_end / M
            eta = elapsed * (M - i_end) / max(i_end, 1)
            print(f"  unconditional progress: {i_end}/{M} ({pct:5.1f}%)  "
                  f"elapsed {elapsed:6.1f}s  ETA {eta:6.1f}s")

    return null_per_pole, null_assign


# ---------------------------------------------------------------------------
# Conditional null via swap chain (re-implemented for self-containedness)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings: np.ndarray,
    target_lon_deg: float,
) -> np.ndarray:
    N = len(lat)
    lat_2d = np.broadcast_to(lat[:, None], (N, N))
    lon_2d = np.broadcast_to(lon[:, None], (N, N))
    bearings_2d = np.broadcast_to(bearings[None, :], (N, N))
    intersections = compute_intersection_lat(lat_2d, lon_2d, bearings_2d, target_lon_deg)
    return (intersections >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(intersections)


def run_swap_chain(
    compatibility: np.ndarray,
    M: int,
    swaps_per_sample: int,
    warmup_swaps: int,
    seed: int,
) -> tuple[np.ndarray, dict]:
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]

    # Force diagonal True for sites where it isn't (the manually-snapped
    # structures and Haran, per analysis log 2026-05-17).
    invalid_diag = ~np.diag(compatibility)
    if invalid_diag.any():
        compatibility = compatibility.copy()
        np.fill_diagonal(compatibility, True)

    pi = np.arange(N)
    n_attempted = 0
    n_accepted = 0
    total_swaps = warmup_swaps + M * swaps_per_sample
    permutations = np.empty((M, N), dtype=np.int32)

    t_start = time.time()
    swap_idx_global = 0
    proposal_chunk_size = 100_000

    while swap_idx_global < total_swaps:
        chunk = min(proposal_chunk_size, total_swaps - swap_idx_global)
        i_props = rng.integers(0, N, size=chunk)
        j_props = rng.integers(0, N, size=chunk)

        for k in range(chunk):
            i = i_props[k]
            j = j_props[k]
            if i != j:
                bi = pi[i]
                bj = pi[j]
                if compatibility[i, bj] and compatibility[j, bi]:
                    pi[i] = bj
                    pi[j] = bi
                    n_accepted += 1
            n_attempted += 1
            swap_idx_global += 1

            if swap_idx_global > warmup_swaps:
                after_warmup = swap_idx_global - warmup_swaps
                if after_warmup % swaps_per_sample == 0:
                    sample_idx = (after_warmup // swaps_per_sample) - 1
                    if 0 <= sample_idx < M:
                        permutations[sample_idx] = pi

        if (swap_idx_global // (total_swaps // 10 + 1)) > ((swap_idx_global - chunk) // (total_swaps // 10 + 1)):
            elapsed = time.time() - t_start
            pct = 100.0 * swap_idx_global / total_swaps
            eta = elapsed * (total_swaps - swap_idx_global) / max(swap_idx_global, 1)
            print(f"  swap progress: {swap_idx_global}/{total_swaps} ({pct:5.1f}%)  "
                  f"elapsed {elapsed:5.1f}s  accept {n_accepted/max(n_attempted,1):.3f}")

    return permutations, {
        "n_swaps_attempted": n_attempted,
        "n_swaps_accepted": n_accepted,
        "acceptance_rate": n_accepted / n_attempted if n_attempted else 0.0,
    }


def run_conditional_mc(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings: np.ndarray,
    pole_lats: np.ndarray,
    assigned_pole_lats: np.ndarray,
    target_lon_deg: float,
    tolerance: float,
    M: int,
    seed: int,
    compatibility: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict]:
    permutations, chain_diag = run_swap_chain(
        compatibility, M, SWAPS_PER_SAMPLE, WARMUP_SWAPS, seed
    )
    permuted_bearings = bearings[permutations]
    M_, N = permutations.shape

    lat_bc = np.broadcast_to(lat, (M_, N))
    lon_bc = np.broadcast_to(lon, (M_, N))
    intersections = compute_intersection_lat(
        lat_bc, lon_bc, permuted_bearings, target_lon_deg
    )
    if np.any(np.isnan(intersections)):
        intersections = np.where(np.isnan(intersections), 0.0, intersections)

    null_per_pole = compute_per_pole_counts(intersections, pole_lats, tolerance)
    null_assign = compute_assignment_match_count(
        intersections, assigned_pole_lats, tolerance
    )
    return null_per_pole, null_assign, chain_diag


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("Pre-registered §11(a) and §11(b), with exploratory conditional variants")
    print("Script: 05_per_pole_and_assignment.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Iterations: M = {M_ITERATIONS}")
    print(f"Tolerance: ±{TOLERANCE_DEG}°")
    print("=" * 60)
    print()

    verified_hash = verify_hash()
    n_tests = run_self_tests()
    print(f"Geometry self-test: {n_tests} cases passed.")
    print()

    obs = json.loads(OBS_FILE.read_text())
    expected_n = obs["n_in_range"]

    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    marios_values, in_range_mask = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )
    n_in_range = int(in_range_mask.sum())
    if n_in_range != expected_n:
        print("ERROR: in-range count mismatch.", file=sys.stderr)
        sys.exit(1)

    df_in = df.loc[in_range_mask].reset_index(drop=True)
    lat = df_in["LAT"].to_numpy(dtype=float)
    lon = df_in["LON"].to_numpy(dtype=float)
    bearings = df_in["BEARING"].to_numpy(dtype=float)
    marios_int_lat = marios_values[in_range_mask]
    N = n_in_range

    print(f"N in-range: {N}")
    print()

    # ----------------------------------------------------------------- #
    # Observed independent intersections
    # ----------------------------------------------------------------- #
    indep_int_lat = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    if np.any(np.isnan(indep_int_lat)):
        indep_int_lat = np.where(np.isnan(indep_int_lat), 0.0, indep_int_lat)

    # ----------------------------------------------------------------- #
    # Pole-by-pole loop (5 poles primary, then 6 poles sensitivity)
    # ----------------------------------------------------------------- #
    pole_specs = [
        ("5-pole (primary)", POLES_PRIMARY),
        ("6-pole (sensitivity)", POLES_WITH_VI),
    ]

    output: dict = {
        "script": "05_per_pole_and_assignment.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "alpha": ALPHA,
        "tolerance_deg": TOLERANCE_DEG,
        "n_in_range": N,
    }

    # Build compatibility matrix once (used by conditional MC)
    print("Building compatibility matrix for conditional null...")
    t = time.time()
    compatibility = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    print(f"  built in {time.time()-t:.1f}s; density {compatibility.mean():.4f}")
    print()

    per_pole_observed_rows = []

    for spec_name, poles_dict in pole_specs:
        print()
        print(f"{'=' * 60}")
        print(f"Test family: {spec_name}")
        print(f"{'=' * 60}")
        print()

        pole_names = list(poles_dict.keys())
        pole_lats = np.array(list(poles_dict.values()))
        K = len(pole_lats)

        # ------------------------------------------------------------- #
        # §11(b) assignment: assign each structure to nearest pole by
        # Mario's intersection latitude.
        # ------------------------------------------------------------- #
        nearest_pole_idx = np.argmin(
            np.abs(marios_int_lat[:, None] - pole_lats[None, :]), axis=1
        )
        assigned_pole_lats = pole_lats[nearest_pole_idx]
        # For reporting: how Mario's pipeline distributed structures.
        marios_assignment_counts = np.bincount(nearest_pole_idx, minlength=K)
        print(f"Mario's pipeline assignment (nearest pole to his published "
              f"intersection lat):")
        for k, name in enumerate(pole_names):
            print(f"  Pole {name:15} ({pole_lats[k]:5.1f}°N): "
                  f"{marios_assignment_counts[k]:4d}")
        print()

        # ------------------------------------------------------------- #
        # Observed §11(a) per-pole counts (using INDEPENDENT geometry)
        # ------------------------------------------------------------- #
        obs_per_pole = compute_per_pole_counts(indep_int_lat, pole_lats, TOLERANCE_DEG)
        print(f"§11(a) observed per-pole counts (|indep int lat - pole| <= "
              f"{TOLERANCE_DEG}°):")
        for k, name in enumerate(pole_names):
            print(f"  Pole {name:15} ({pole_lats[k]:5.1f}°N): {obs_per_pole[k]:4d}")
        print()

        # ------------------------------------------------------------- #
        # Observed §11(b) assignment match count (independent vs assigned)
        # ------------------------------------------------------------- #
        obs_assign = compute_assignment_match_count(
            indep_int_lat, assigned_pole_lats, TOLERANCE_DEG
        )
        print(f"§11(b) observed assignment match count: {obs_assign} / {N}")
        print(f"  (structures whose independent intersection is within "
              f"{TOLERANCE_DEG}° of the pole that Mario's pipeline implicitly "
              f"assigned them to)")
        print()

        # ------------------------------------------------------------- #
        # Unconditional MC (pre-registered)
        # ------------------------------------------------------------- #
        print(f"Running unconditional MC (pre-registered) — {spec_name}...")
        null_per_pole_un, null_assign_un = run_unconditional_mc(
            lat, lon, bearings, pole_lats, assigned_pole_lats,
            TARGET_LON_DEG, TOLERANCE_DEG, M_ITERATIONS, RANDOM_SEED,
        )
        print()

        # ------------------------------------------------------------- #
        # Conditional MC (exploratory)
        # ------------------------------------------------------------- #
        print(f"Running conditional MC (exploratory swap chain) — {spec_name}...")
        null_per_pole_cn, null_assign_cn, chain_diag = run_conditional_mc(
            lat, lon, bearings, pole_lats, assigned_pole_lats,
            TARGET_LON_DEG, TOLERANCE_DEG, M_ITERATIONS, RANDOM_SEED,
            compatibility,
        )
        print(f"  Chain acceptance rate: {chain_diag['acceptance_rate']:.4f}")
        print()

        # ------------------------------------------------------------- #
        # P-values: §11(a) per-pole
        # ------------------------------------------------------------- #
        # P-value for "observed ≥ null" (high count is the signal direction)
        p_uncond = np.array([
            (1 + int((null_per_pole_un[:, k] >= obs_per_pole[k]).sum())) / (1 + M_ITERATIONS)
            for k in range(K)
        ])
        p_cond = np.array([
            (1 + int((null_per_pole_cn[:, k] >= obs_per_pole[k]).sum())) / (1 + M_ITERATIONS)
            for k in range(K)
        ])
        p_sidak_uncond = np.array([sidak_correction(p, K) for p in p_uncond])
        p_sidak_cond = np.array([sidak_correction(p, K) for p in p_cond])

        print(f"§11(a) per-pole p-values ({spec_name}):")
        print(f"  {'Pole':17s}  {'obs':>5s}  "
              f"{'unc-null mean':>14s}  {'p-raw-unc':>10s}  {'p-Šidák-unc':>12s}  "
              f"{'con-null mean':>14s}  {'p-raw-con':>10s}  {'p-Šidák-con':>12s}")
        for k, name in enumerate(pole_names):
            print(f"  {name:17s}  {obs_per_pole[k]:5d}  "
                  f"{null_per_pole_un[:, k].mean():14.2f}  "
                  f"{p_uncond[k]:10.4f}  {p_sidak_uncond[k]:12.4f}  "
                  f"{null_per_pole_cn[:, k].mean():14.2f}  "
                  f"{p_cond[k]:10.4f}  {p_sidak_cond[k]:12.4f}")
            per_pole_observed_rows.append({
                "test_family": spec_name,
                "pole": name,
                "pole_lat": pole_lats[k],
                "obs_count": int(obs_per_pole[k]),
                "marios_assignment_count": int(marios_assignment_counts[k]),
                "uncond_null_mean": float(null_per_pole_un[:, k].mean()),
                "uncond_null_std": float(null_per_pole_un[:, k].std()),
                "p_raw_uncond": float(p_uncond[k]),
                "p_sidak_uncond": float(p_sidak_uncond[k]),
                "cond_null_mean": float(null_per_pole_cn[:, k].mean()),
                "cond_null_std": float(null_per_pole_cn[:, k].std()),
                "p_raw_cond": float(p_cond[k]),
                "p_sidak_cond": float(p_sidak_cond[k]),
            })
        print()

        # ------------------------------------------------------------- #
        # P-values: §11(b) assignment
        # ------------------------------------------------------------- #
        p_assign_uncond = (1 + int((null_assign_un >= obs_assign).sum())) / (1 + M_ITERATIONS)
        p_assign_cond = (1 + int((null_assign_cn >= obs_assign).sum())) / (1 + M_ITERATIONS)
        print(f"§11(b) assignment match results ({spec_name}):")
        print(f"  observed count:            {obs_assign}")
        print(f"  unconditional null mean:   {null_assign_un.mean():.2f}")
        print(f"  unconditional null std:    {null_assign_un.std():.2f}")
        print(f"  p (pre-registered):        {p_assign_uncond:.6f}")
        print(f"  conditional null mean:     {null_assign_cn.mean():.2f}")
        print(f"  conditional null std:      {null_assign_cn.std():.2f}")
        print(f"  p (exploratory):           {p_assign_cond:.6f}")
        print()

        # Save outputs for this spec
        key = spec_name.split()[0]
        output[key] = {
            "poles": poles_dict,
            "marios_assignment_counts": {n: int(c) for n, c in zip(pole_names, marios_assignment_counts)},
            "observed_per_pole_counts": {n: int(c) for n, c in zip(pole_names, obs_per_pole)},
            "uncond": {
                "per_pole_null_mean": {n: float(null_per_pole_un[:, k].mean()) for k, n in enumerate(pole_names)},
                "per_pole_p_raw":  {n: float(p_uncond[k]) for k, n in enumerate(pole_names)},
                "per_pole_p_sidak": {n: float(p_sidak_uncond[k]) for k, n in enumerate(pole_names)},
                "assignment_obs": int(obs_assign),
                "assignment_null_mean": float(null_assign_un.mean()),
                "assignment_p": float(p_assign_uncond),
            },
            "cond": {
                "per_pole_null_mean": {n: float(null_per_pole_cn[:, k].mean()) for k, n in enumerate(pole_names)},
                "per_pole_p_raw":  {n: float(p_cond[k]) for k, n in enumerate(pole_names)},
                "per_pole_p_sidak": {n: float(p_sidak_cond[k]) for k, n in enumerate(pole_names)},
                "assignment_p": float(p_assign_cond),
                "chain_acceptance_rate": chain_diag["acceptance_rate"],
            },
        }

        # Save null arrays (5-pole only, to keep file sizes manageable)
        if key == "5-pole":
            np.save(PER_POLE_NULL_UNCOND, null_per_pole_un)
            np.save(PER_POLE_NULL_COND, null_per_pole_cn)
            np.save(ASSIGN_NULL_UNCOND, null_assign_un)
            np.save(ASSIGN_NULL_COND, null_assign_cn)
            print(f"Null arrays for 5-pole saved.")
            print()

    # ----------------------------------------------------------------- #
    # Save per-pole observed CSV and JSON summary
    # ----------------------------------------------------------------- #
    pd.DataFrame(per_pole_observed_rows).to_csv(PER_POLE_OBS_FILE, index=False)
    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print(f"\nSummary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print(f"Per-pole observed CSV: {PER_POLE_OBS_FILE.relative_to(REPO_ROOT)}")
    print()
    print("Pre-registered §11(a) and §11(b) tests complete, with exploratory")
    print("conditional-null variants. Analysis is substantively complete.")
    print()


if __name__ == "__main__":
    main()
