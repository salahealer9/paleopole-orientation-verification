"""
06_geographic_block_null.py
============================

Seventh script in the analysis pipeline. Implements the geographic-block
null model per pre-registration §11(d):

  "Replace the global orientation shuffle with a block-permutation null
   that shuffles orientations only within geographic/cultural regions
   (Americas, Europe-Mediterranean, Middle East, South Asia, East Asia,
   Africa, Oceania, defined by simple longitude/latitude bands specified
   in the analysis code). This tests robustness to potential
   within-region orientation correlation."

Rationale
---------
The unconditional null (script 03) and the conditional within-hemisphere
null (script 03b) both shuffle bearings across all sites. If different
regions have their own characteristic orientation patterns (e.g., shared
architectural traditions producing similar bearings within Mesoamerica,
or within the Mediterranean), then global shuffling will mix bearings
across cultures and produce intersection distributions that are not
representative of any actual cultural group.

The block-permutation null asks the more specific question: assuming
each region has its own orientation pool (whatever cultural conventions
prevail there), and only mixing bearings within each region, does the
overall pattern of clustering at the proposed paleopoles still emerge?

If yes, the clustering is robust to regional patterns and is a global
phenomenon. If no, the clustering may be driven by region-specific
orientation traditions that happen to produce intersections concentrated
near certain latitudes when the great-circle geometry is computed.

Block definitions
-----------------
The pre-registration commits to "simple longitude/latitude bands
specified in the analysis code." We use the following seven blocks,
chosen to match the major geographic concentrations in the dataset:

  Americas:           lon ∈ [-180°, -30°]
  Europe-Med:         lon ∈ [-30°,  +30°], lat ∈ [+30°, +75°]
  Middle East:        lon ∈ [+30°,  +60°], lat ∈ [+15°, +45°]
  Africa:             lon ∈ [-30°,  +60°], lat ∈ [-40°, +30°]   (excl. Middle East)
  South Asia:         lon ∈ [+60°,  +95°], lat ∈  [+5°, +40°]
  East Asia:          lon ∈ [+95°, +180°], lat ∈ [+15°, +60°]
  Oceania/SE Asia:    lon ∈ [+95°, +180°], lat ∈ [-50°, +15°]

Sites that fall outside all blocks (e.g., in extreme latitudes or
unusual locations) are assigned to a special "Other" block. The number
of such sites and their identities are reported.

This script runs the test under TWO null variants:

  Block-unconditional:
      Within each block, randomly permute bearings without constraint.
      Some permutations will produce southern-hemisphere intersections;
      this is analogous to script 03's unconditional null but with
      block-level grouping.

  Block-conditional:
      Within each block, use the swap-chain procedure from script 03b
      restricted to within-block swaps. Preserves both block membership
      and the northern-hemisphere intersection property.

Tests computed under both nulls
-------------------------------
  - Primary T statistic (pre-registration §6)
  - §11(a) per-pole confirmatory counts
  - §11(b) site-to-pole assignment match count (using the same
    Mario-pipeline-derived assignment from script 05)

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json
- results/05_per_pole_and_assignment.json (for assignment vector)

Outputs
-------
- results/06_geographic_block_null.json
- results/06_block_assignments.csv: per-site block label
- results/06_null_block_uncond_5pole.npy
- results/06_null_block_cond_5pole.npy

Pre-registration: https://doi.org/10.5281/zenodo.20258204
Status:           Pre-registered §11(d) sensitivity analysis
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
SUMMARY_FILE = RESULTS_DIR / "06_geographic_block_null.json"
BLOCK_LABELS_FILE = RESULTS_DIR / "06_block_assignments.csv"
NULL_BLOCK_UNCOND_FILE = RESULTS_DIR / "06_null_block_uncond_5pole.npy"
NULL_BLOCK_COND_FILE = RESULTS_DIR / "06_null_block_cond_5pole.npy"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN_HEMISPHERE_THRESHOLD = 0.0
TOLERANCE_DEG = 1.5

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


# ---------------------------------------------------------------------------
# Block definitions
# ---------------------------------------------------------------------------


def assign_block(lat: float, lon: float) -> str:
    """Assign a (lat, lon) coordinate to one of the seven geographic blocks
    (or 'Other' if none match).
    """
    if -180.0 <= lon <= -30.0:
        return "Americas"
    if -30.0 < lon <= 30.0 and 30.0 <= lat <= 75.0:
        return "Europe-Med"
    if 30.0 < lon <= 60.0 and 15.0 <= lat <= 45.0:
        return "Middle East"
    if -30.0 < lon <= 60.0 and -40.0 <= lat < 30.0:
        return "Africa"
    if 60.0 < lon <= 95.0 and 5.0 <= lat <= 40.0:
        return "South Asia"
    if 95.0 < lon <= 180.0 and 15.0 <= lat <= 60.0:
        return "East Asia"
    if 95.0 < lon <= 180.0 and -50.0 <= lat < 15.0:
        return "Oceania/SE Asia"
    return "Other"


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


def parse_marios_intersection_column(series: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    str_series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    values = pd.to_numeric(str_series, errors="coerce").to_numpy()
    return values, ~np.isnan(values)


# ---------------------------------------------------------------------------
# Test statistic helpers (same as scripts 03 and 05)
# ---------------------------------------------------------------------------


def compute_T_vec(intersection_lats: np.ndarray, pole_lats: np.ndarray) -> np.ndarray:
    """Vectorized T over batch axis 0."""
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False
    distances = np.abs(intersection_lats[..., None] - pole_lats[None, None, :])
    d_min = distances.min(axis=-1)
    T = d_min.mean(axis=-1)
    return T[0] if squeeze else T


def compute_per_pole_counts(
    intersection_lats: np.ndarray, pole_lats: np.ndarray, tol: float
) -> np.ndarray:
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False
    within = np.abs(intersection_lats[..., None] - pole_lats[None, None, :]) <= tol
    counts = within.sum(axis=1).astype(int)
    return counts[0] if squeeze else counts


def compute_assignment_count(
    intersection_lats: np.ndarray, assigned_lats: np.ndarray, tol: float
) -> np.ndarray:
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False
    diff = np.abs(intersection_lats - assigned_lats[None, :])
    counts = (diff <= tol).sum(axis=1).astype(int)
    return int(counts[0]) if squeeze else counts


# ---------------------------------------------------------------------------
# Block-permutation: unconditional
# ---------------------------------------------------------------------------


def run_block_unconditional_mc(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings: np.ndarray,
    block_indices: list[np.ndarray],
    pole_lats: np.ndarray,
    assigned_pole_lats: np.ndarray,
    target_lon_deg: float,
    tolerance: float,
    M: int,
    seed: int,
    chunk_size: int = 500,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Block-permutation null: within each block, shuffle bearings
    without constraint.

    Returns
    -------
    T_null : (M,)
    per_pole_null : (M, K)
    assign_null : (M,)
    """
    rng = np.random.default_rng(seed)
    N = len(lat)
    K = len(pole_lats)

    T_null = np.empty(M, dtype=float)
    per_pole_null = np.empty((M, K), dtype=int)
    assign_null = np.empty(M, dtype=int)

    n_chunks = (M + chunk_size - 1) // chunk_size
    t_start = time.time()

    for chunk_idx in range(n_chunks):
        i_start = chunk_idx * chunk_size
        i_end = min(i_start + chunk_size, M)
        size = i_end - i_start

        # Build (size, N) permuted bearings using within-block shuffling
        permuted = np.empty((size, N), dtype=float)
        for k in range(size):
            new_bearings = bearings.copy()
            for block_idx in block_indices:
                if len(block_idx) > 1:
                    new_bearings[block_idx] = rng.permutation(bearings[block_idx])
            permuted[k] = new_bearings

        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        intersections = compute_intersection_lat(
            lat_bc, lon_bc, permuted, target_lon_deg
        )
        if np.any(np.isnan(intersections)):
            intersections = np.where(np.isnan(intersections), 0.0, intersections)

        T_null[i_start:i_end] = compute_T_vec(intersections, pole_lats)
        per_pole_null[i_start:i_end] = compute_per_pole_counts(
            intersections, pole_lats, tolerance
        )
        assign_null[i_start:i_end] = compute_assignment_count(
            intersections, assigned_pole_lats, tolerance
        )

        if (chunk_idx + 1) % max(1, n_chunks // 10) == 0 or chunk_idx == n_chunks - 1:
            elapsed = time.time() - t_start
            pct = 100.0 * i_end / M
            eta = elapsed * (M - i_end) / max(i_end, 1)
            print(f"  block-uncond progress: {i_end}/{M} ({pct:5.1f}%)  "
                  f"elapsed {elapsed:5.1f}s  ETA {eta:5.1f}s")

    return T_null, per_pole_null, assign_null


# ---------------------------------------------------------------------------
# Block-permutation: conditional (within-block swap chain)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(
    lat: np.ndarray, lon: np.ndarray, bearings: np.ndarray, target_lon_deg: float,
) -> np.ndarray:
    N = len(lat)
    lat_2d = np.broadcast_to(lat[:, None], (N, N))
    lon_2d = np.broadcast_to(lon[:, None], (N, N))
    bearings_2d = np.broadcast_to(bearings[None, :], (N, N))
    intersections = compute_intersection_lat(lat_2d, lon_2d, bearings_2d, target_lon_deg)
    return (intersections >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(intersections)


def run_block_conditional_swap_chain(
    compatibility: np.ndarray,
    block_indices: list[np.ndarray],
    M: int,
    swaps_per_sample: int,
    warmup_swaps: int,
    seed: int,
) -> tuple[np.ndarray, dict]:
    """Swap chain restricted to within-block swaps.

    Like the swap chain in script 03b, but the proposed swap (i, j) is
    only considered if i and j are in the same block.
    """
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]

    # Force diagonal True
    compatibility = compatibility.copy()
    np.fill_diagonal(compatibility, True)

    # Build block membership for each site: site_to_block[i] = block_idx
    site_to_block = np.full(N, -1, dtype=int)
    for b, indices in enumerate(block_indices):
        site_to_block[indices] = b

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
            if i != j and site_to_block[i] == site_to_block[j]:
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
            print(f"  block-cond swap progress: {swap_idx_global}/{total_swaps} "
                  f"({pct:5.1f}%)  elapsed {elapsed:5.1f}s  "
                  f"accept {n_accepted/max(n_attempted,1):.3f}")

    return permutations, {
        "n_swaps_attempted": n_attempted,
        "n_swaps_accepted": n_accepted,
        "acceptance_rate": n_accepted / n_attempted if n_attempted else 0.0,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("Pre-registered §11(d): geographic-block null sensitivity analysis")
    print("Script: 06_geographic_block_null.py")
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
    expected_n = obs["n_in_range"]
    T_obs_5 = obs["T_obs_5pole"]
    print(f"T_obs (5-pole) from script 02: {T_obs_5:.6f}°")
    print()

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
    pole_lats = np.array(list(POLES_PRIMARY.values()))
    K = len(pole_lats)

    # ----------------------------------------------------------------- #
    # Assign blocks
    # ----------------------------------------------------------------- #
    blocks = [assign_block(lat[i], lon[i]) for i in range(N)]
    block_labels = sorted(set(blocks))
    block_indices = []
    print("Block assignments:")
    for b in block_labels:
        idx = np.array([i for i, x in enumerate(blocks) if x == b])
        block_indices.append(idx)
        print(f"  {b:25s} n = {len(idx):4d}")
    print()

    # Save block assignment CSV
    block_df = df_in[["SITE NAME", "COUNTRY", "LAT", "LON", "BEARING"]].copy()
    block_df["block"] = blocks
    block_df.to_csv(BLOCK_LABELS_FILE, index=False)
    print(f"Per-site block labels saved to {BLOCK_LABELS_FILE.relative_to(REPO_ROOT)}")
    print()

    if "Other" in block_labels:
        n_other = sum(1 for b in blocks if b == "Other")
        print(f"NOTE: {n_other} sites do not fit any geographic block. They will")
        print(f"      be a separate block in the permutation null. Affected sites:")
        for i, b in enumerate(blocks):
            if b == "Other":
                print(f"        {df_in.iloc[i]['SITE NAME']} ({lat[i]:.2f}, {lon[i]:.2f})")
        print()

    # Compute observed test stats
    indep_int_lat = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    if np.any(np.isnan(indep_int_lat)):
        indep_int_lat = np.where(np.isnan(indep_int_lat), 0.0, indep_int_lat)

    nearest_pole_idx = np.argmin(
        np.abs(marios_int_lat[:, None] - pole_lats[None, :]), axis=1
    )
    assigned_pole_lats = pole_lats[nearest_pole_idx]

    T_observed = compute_T_vec(indep_int_lat, pole_lats)
    obs_per_pole = compute_per_pole_counts(indep_int_lat, pole_lats, TOLERANCE_DEG)
    obs_assign = compute_assignment_count(indep_int_lat, assigned_pole_lats, TOLERANCE_DEG)

    print(f"Observed statistics (independent geometry):")
    print(f"  T (5-pole):                          {T_observed:.6f}°")
    print(f"  §11(a) per-pole counts:")
    for k, name in enumerate(POLES_PRIMARY.keys()):
        print(f"    Pole {name:15} ({pole_lats[k]:5.1f}°N):  {obs_per_pole[k]}")
    print(f"  §11(b) assignment matches:           {obs_assign} / {N}")
    print()

    # ----------------------------------------------------------------- #
    # Block-unconditional MC
    # ----------------------------------------------------------------- #
    print("Running block-unconditional MC...")
    T_null_un, per_pole_null_un, assign_null_un = run_block_unconditional_mc(
        lat, lon, bearings, block_indices, pole_lats, assigned_pole_lats,
        TARGET_LON_DEG, TOLERANCE_DEG, M_ITERATIONS, RANDOM_SEED,
    )
    print()

    # ----------------------------------------------------------------- #
    # Block-conditional MC (within-block swap chain)
    # ----------------------------------------------------------------- #
    print("Building compatibility matrix for block-conditional null...")
    t = time.time()
    compatibility = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    print(f"  built in {time.time()-t:.1f}s")
    print()

    print("Running block-conditional swap chain...")
    swaps_per_sample = 2 * N
    warmup = 5 * N
    permutations, chain_diag = run_block_conditional_swap_chain(
        compatibility, block_indices, M_ITERATIONS, swaps_per_sample, warmup, RANDOM_SEED,
    )
    print(f"  Acceptance rate: {chain_diag['acceptance_rate']:.4f}")
    print()

    # Compute T, per-pole, assignment for block-conditional samples
    print("Computing test statistics for block-conditional samples...")
    permuted_bearings = bearings[permutations]
    lat_bc = np.broadcast_to(lat, (M_ITERATIONS, N))
    lon_bc = np.broadcast_to(lon, (M_ITERATIONS, N))
    intersections_cond = compute_intersection_lat(
        lat_bc, lon_bc, permuted_bearings, TARGET_LON_DEG
    )
    if np.any(np.isnan(intersections_cond)):
        intersections_cond = np.where(np.isnan(intersections_cond), 0.0, intersections_cond)
    T_null_cond = compute_T_vec(intersections_cond, pole_lats)
    per_pole_null_cond = compute_per_pole_counts(intersections_cond, pole_lats, TOLERANCE_DEG)
    assign_null_cond = compute_assignment_count(intersections_cond, assigned_pole_lats, TOLERANCE_DEG)
    print()

    # ----------------------------------------------------------------- #
    # Results
    # ----------------------------------------------------------------- #
    # T
    p_T_uncond = (1 + int((T_null_un <= T_observed).sum())) / (1 + M_ITERATIONS)
    p_T_cond = (1 + int((T_null_cond <= T_observed).sum())) / (1 + M_ITERATIONS)

    print(f"Primary T results (block-permutation null):")
    print(f"  T_observed:               {T_observed:.6f}°")
    print(f"  Block-uncond null mean:   {T_null_un.mean():.6f}°   p = {p_T_uncond:.6f}")
    print(f"  Block-cond null mean:     {T_null_cond.mean():.6f}°   p = {p_T_cond:.6f}")
    print()

    # Per-pole
    p_pp_un = np.array([
        (1 + int((per_pole_null_un[:, k] >= obs_per_pole[k]).sum())) / (1 + M_ITERATIONS)
        for k in range(K)
    ])
    p_pp_cond = np.array([
        (1 + int((per_pole_null_cond[:, k] >= obs_per_pole[k]).sum())) / (1 + M_ITERATIONS)
        for k in range(K)
    ])
    p_sidak_un = 1.0 - (1.0 - p_pp_un) ** K
    p_sidak_cond = 1.0 - (1.0 - p_pp_cond) ** K

    print(f"§11(a) per-pole p-values (block-permutation null):")
    print(f"  {'Pole':17s}  {'obs':>5s}  "
          f"{'uncon-null':>11s}  {'p-Šidák-un':>11s}  "
          f"{'cond-null':>11s}  {'p-Šidák-cn':>11s}")
    for k, name in enumerate(POLES_PRIMARY.keys()):
        print(f"  {name:17s}  {obs_per_pole[k]:5d}  "
              f"{per_pole_null_un[:, k].mean():11.2f}  {p_sidak_un[k]:11.4f}  "
              f"{per_pole_null_cond[:, k].mean():11.2f}  {p_sidak_cond[k]:11.4f}")
    print()

    # Assignment
    p_assign_un = (1 + int((assign_null_un >= obs_assign).sum())) / (1 + M_ITERATIONS)
    p_assign_cond = (1 + int((assign_null_cond >= obs_assign).sum())) / (1 + M_ITERATIONS)
    print(f"§11(b) assignment results (block-permutation null):")
    print(f"  Observed:                 {obs_assign}")
    print(f"  Block-uncond null mean:   {assign_null_un.mean():.2f}   p = {p_assign_un:.6f}")
    print(f"  Block-cond null mean:     {assign_null_cond.mean():.2f}   p = {p_assign_cond:.6f}")
    print()

    # Save outputs
    np.save(NULL_BLOCK_UNCOND_FILE, T_null_un)
    np.save(NULL_BLOCK_COND_FILE, T_null_cond)

    summary = {
        "script": "06_geographic_block_null.py",
        "status": "Pre-registered §11(d) sensitivity",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "n_in_range": N,
        "blocks": {b: int(len(block_indices[i])) for i, b in enumerate(block_labels)},
        "T_observed": float(T_observed),
        "block_unconditional": {
            "T_null_mean": float(T_null_un.mean()),
            "T_null_std": float(T_null_un.std()),
            "p_T": p_T_uncond,
            "per_pole_null_mean": {n: float(per_pole_null_un[:, k].mean()) for k, n in enumerate(POLES_PRIMARY.keys())},
            "per_pole_p_sidak": {n: float(p_sidak_un[k]) for k, n in enumerate(POLES_PRIMARY.keys())},
            "assignment_null_mean": float(assign_null_un.mean()),
            "assignment_p": p_assign_un,
        },
        "block_conditional": {
            "T_null_mean": float(T_null_cond.mean()),
            "T_null_std": float(T_null_cond.std()),
            "p_T": p_T_cond,
            "per_pole_null_mean": {n: float(per_pole_null_cond[:, k].mean()) for k, n in enumerate(POLES_PRIMARY.keys())},
            "per_pole_p_sidak": {n: float(p_sidak_cond[k]) for k, n in enumerate(POLES_PRIMARY.keys())},
            "assignment_null_mean": float(assign_null_cond.mean()),
            "assignment_p": p_assign_cond,
            "chain_acceptance_rate": chain_diag["acceptance_rate"],
        },
        "observed_per_pole": {n: int(obs_per_pole[k]) for k, n in enumerate(POLES_PRIMARY.keys())},
        "observed_assignment": int(obs_assign),
    }

    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print("Pre-registered §11(d) complete. Substantive analytical work is done.")
    print()


if __name__ == "__main__":
    main()
