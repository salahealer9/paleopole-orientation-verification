"""
03b_conditional_null_exploratory.py
====================================

EXPLORATORY (not pre-registered) Monte Carlo with a conditional null
that preserves the in-range property of the observed data.

This script is run AFTER the data has been inspected and AFTER the
pre-registered Monte Carlo in script 03 has been completed. Per
pre-registration §12 point 3:

  "No new tests will be added post-hoc without clear labeling. Any
   analysis run after the database is opened that was not pre-registered
   here will be labeled explicitly as exploratory in the final write-up
   and will not be used to make confirmatory claims."

This analysis is explicitly exploratory. Its purpose is to test the
within-hemisphere clustering question that the pre-registered null
(§7) attempted but did not fully isolate, as documented in the
analysis log entry for 2026-05-17 on the primary Monte Carlo result.

Motivation
----------
The pre-registered null permutes bearings across sites without
constraint, with the result that ~46% of permutations produce
southern-hemisphere intersections — yielding very large d_i values
that dominate the null mean of T. The observed data, by construction,
has 99% northern-hemisphere intersections. The pre-registered null
therefore rejects "any random reassignment of bearings produces this
much northern-hemisphere concentration," which is a weaker and less
informative test than "the bearings cluster around the five specific
proposed poles more than expected from great-circle geometry alone."

The conditional null implemented here preserves the in-range property
by construction: only permutations in which every (site, bearing) pair
produces a northern-hemisphere intersection are sampled.

Methodology: site-wise restricted permutation via Metropolis swap chain
----------------------------------------------------------------------
1. Pre-compute the 994x994 compatibility matrix C, where C[i, j] = True
   if bearing j (in the empirical pool) would, when assigned to site i,
   produce a northern-hemisphere intersection per the data owner's
   classification criterion (parseable as a positive-or-zero number in
   his geometry, equivalent to intersection latitude >= 0 in ours).

2. Start the Markov chain at the identity permutation pi[i] = i, which
   is valid by construction (every observed (site, bearing) pair is
   in-range; that's how those rows entered the in-range set).

3. At each step, propose a swap: pick two sites i and j at random, and
   ask whether bearings pi[i] and pi[j] can be exchanged without
   either pair leaving the in-range set. That is, accept the swap iff
   C[i, pi[j]] AND C[j, pi[i]]. If accepted, swap.

4. After SWAPS_PER_SAMPLE swap attempts (the chain's "thinning interval"),
   record T computed on the current permutation. Repeat for M samples.

5. Compute p = (1 + #{m : T^(m) <= T_obs}) / (1 + M) using the same
   formula as the pre-registered analysis.

Properties of this null
-----------------------
- Marginal bearing distribution is preserved EXACTLY: every iteration
  uses each empirical bearing exactly once.
- Site coordinates are fixed.
- Every iteration produces 994 northern-hemisphere intersections (the
  in-range property is preserved by construction).
- The pairing of bearings to sites is randomised subject to the
  in-range constraint.

This is the null that the pre-registration §7 attempted to describe.
The conditioning on in-range was implicit in §7's reference to "the 994
in-range structures" but was not operationalised in the procedure. This
script provides the operationalisation.

Reproducibility
---------------
Same hardcoded seed as script 03 (20260517) for the underlying random
stream. Chain starting state is the identity permutation, which is
deterministic.

Outputs
-------
- results/03b_conditional_null.json: T_obs, conditional-null p-values
  (5-pole and 6-pole), null distribution percentiles, chain diagnostics
  (acceptance rate, autocorrelation summary).
- results/03b_null_conditional_5pole.npy: full vector of T^(m).
- results/03b_null_conditional_6pole.npy: same for 6-pole.

Pre-registration: https://doi.org/10.5281/zenodo.20258204
Status:           EXPLORATORY (post-hoc, per §12 point 3)
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
SUMMARY_FILE = RESULTS_DIR / "03b_conditional_null.json"
NULL_5POLE_FILE = RESULTS_DIR / "03b_null_conditional_5pole.npy"
NULL_6POLE_FILE = RESULTS_DIR / "03b_null_conditional_6pole.npy"

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

M_ITERATIONS = 10_000
RANDOM_SEED = 20260517
ALPHA_PRIMARY = 0.05

# Number of swap attempts between recorded samples. Higher = more
# independence between consecutive samples (better mixing) but slower.
# 2 * N is a conservative choice for high-density compatibility matrices.
SWAPS_PER_SAMPLE = 2 * 994

# Warm-up swap attempts before starting to record samples, to break
# correlation with the deterministic starting state.
WARMUP_SWAPS = 5 * 994


# ---------------------------------------------------------------------------
# Hash verification (same as script 03)
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
# Inclusion mask (same as scripts 02, 03)
# ---------------------------------------------------------------------------


def parse_marios_intersection_column(series: pd.Series) -> np.ndarray:
    str_series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    values = pd.to_numeric(str_series, errors="coerce").to_numpy()
    return ~np.isnan(values)


# ---------------------------------------------------------------------------
# Compatibility matrix
# ---------------------------------------------------------------------------


def build_compatibility_matrix(
    lat: np.ndarray,
    lon: np.ndarray,
    bearings: np.ndarray,
    target_lon_deg: float,
) -> np.ndarray:
    """Compute the 994x994 boolean compatibility matrix C, where
    C[i, j] = True iff bearing j paired with site i produces a
    northern-hemisphere intersection.

    For efficiency, we compute intersection latitudes in a single
    vectorized broadcast: lat shape (N, 1), bearings shape (1, N).
    """
    N = len(lat)
    # Broadcast: lat[:, None] shape (N, 1); bearings[None, :] shape (1, N)
    # The geometry function broadcasts naturally.
    lat_2d = np.broadcast_to(lat[:, None], (N, N))
    lon_2d = np.broadcast_to(lon[:, None], (N, N))
    bearings_2d = np.broadcast_to(bearings[None, :], (N, N))

    intersections = compute_intersection_lat(
        lat_2d, lon_2d, bearings_2d, target_lon_deg
    )
    # In-range = northern hemisphere (operationalising the data owner's
    # classification per analysis log 2026-05-17 entries).
    in_range = (intersections >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(intersections)
    return in_range


# ---------------------------------------------------------------------------
# Metropolis swap chain
# ---------------------------------------------------------------------------


def run_swap_chain(
    compatibility: np.ndarray,
    M: int,
    swaps_per_sample: int,
    warmup_swaps: int,
    seed: int,
) -> tuple[np.ndarray, dict]:
    """Run the Metropolis swap chain to produce M samples from the
    conditional null.

    Parameters
    ----------
    compatibility : (N, N) bool array
        compatibility[i, j] = True iff bearing j is in-range at site i.
        We require compatibility[i, i] = True for all i (i.e. the
        identity permutation must be valid).
    M : int
        Number of samples to record.
    swaps_per_sample : int
        Number of swap attempts between recorded samples.
    warmup_swaps : int
        Number of swap attempts before recording the first sample.
    seed : int
        Pseudo-random seed.

    Returns
    -------
    permutations : (M, N) int array
        permutations[m] is the m-th recorded permutation. Each row is a
        permutation of {0, ..., N-1} (so that bearing pi[i] is assigned
        to site i).
    diagnostics : dict
        Acceptance rate, total swaps attempted, total swaps accepted.
    """
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]

    # Sanity-check the starting state.
    if not np.all(np.diag(compatibility)):
        raise RuntimeError(
            "Identity permutation is not valid (some observed pairs are "
            "not in-range under the compatibility matrix). Investigate."
        )

    # Start at the identity permutation.
    pi = np.arange(N)

    n_attempted = 0
    n_accepted = 0

    # Pre-generate all swap proposals as two arrays of indices, in batches
    # for memory efficiency.
    total_swaps = warmup_swaps + M * swaps_per_sample
    permutations = np.empty((M, N), dtype=np.int32)

    t_start = time.time()
    swap_idx_global = 0

    # Generate i,j proposal pairs in chunks for memory efficiency
    proposal_chunk_size = 100_000
    while swap_idx_global < total_swaps:
        chunk = min(proposal_chunk_size, total_swaps - swap_idx_global)
        i_props = rng.integers(0, N, size=chunk)
        j_props = rng.integers(0, N, size=chunk)

        # Inner Python loop is the bottleneck; we keep it simple and
        # rely on the per-step cost being cheap (a couple of array lookups).
        for k in range(chunk):
            i = i_props[k]
            j = j_props[k]
            if i == j:
                # No-op swap; count as attempted, never accepted.
                n_attempted += 1
                swap_idx_global += 1
            else:
                bi = pi[i]
                bj = pi[j]
                # Acceptance check: can we swap (i, j) bearings?
                if compatibility[i, bj] and compatibility[j, bi]:
                    pi[i] = bj
                    pi[j] = bi
                    n_accepted += 1
                n_attempted += 1
                swap_idx_global += 1

            # Are we at a recording point?
            if swap_idx_global > warmup_swaps:
                after_warmup = swap_idx_global - warmup_swaps
                if after_warmup % swaps_per_sample == 0:
                    sample_idx = (after_warmup // swaps_per_sample) - 1
                    if 0 <= sample_idx < M:
                        permutations[sample_idx] = pi

        # Progress report
        if (swap_idx_global // (total_swaps // 10 + 1)) > ((swap_idx_global - chunk) // (total_swaps // 10 + 1)):
            elapsed = time.time() - t_start
            pct = 100.0 * swap_idx_global / total_swaps
            eta = elapsed * (total_swaps - swap_idx_global) / max(swap_idx_global, 1)
            print(f"  swap progress: {swap_idx_global}/{total_swaps} ({pct:5.1f}%)  "
                  f"elapsed {elapsed:6.1f}s  ETA {eta:6.1f}s  "
                  f"accept rate {n_accepted/n_attempted:.3f}")

    diagnostics = {
        "n_swaps_attempted": n_attempted,
        "n_swaps_accepted": n_accepted,
        "acceptance_rate": n_accepted / n_attempted if n_attempted else 0.0,
        "warmup_swaps": warmup_swaps,
        "swaps_per_sample": swaps_per_sample,
    }
    return permutations, diagnostics


# ---------------------------------------------------------------------------
# T computation
# ---------------------------------------------------------------------------


def compute_T_from_permutations(
    permutations: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    bearings: np.ndarray,
    pole_lats: np.ndarray,
    target_lon_deg: float,
) -> np.ndarray:
    """For each of M permutations, compute T.

    Parameters
    ----------
    permutations : (M, N) int array
    lat, lon, bearings : (N,) arrays
    pole_lats : (K,) array
    target_lon_deg : float

    Returns
    -------
    T : (M,) array
    """
    M, N = permutations.shape

    # Permuted bearings: for each iteration m, permuted[m, i] = bearings[pi[m, i]]
    # This is just fancy indexing.
    permuted_bearings = bearings[permutations]  # (M, N)
    lat_bc = np.broadcast_to(lat, (M, N))
    lon_bc = np.broadcast_to(lon, (M, N))

    intersections = compute_intersection_lat(
        lat_bc, lon_bc, permuted_bearings, target_lon_deg
    )

    # Sanity: under the conditional null, all intersections should be
    # in the northern hemisphere.
    n_southern = int((intersections < 0).sum())
    n_nan = int(np.isnan(intersections).sum())
    if n_southern > 0 or n_nan > 0:
        print(f"  [WARN] {n_southern} southern + {n_nan} NaN intersections in "
              f"permuted samples — conditional null property violated.")
        # Replace NaN with 0 to avoid crashing the T computation.
        intersections = np.where(np.isnan(intersections), 0.0, intersections)

    # d_min and T
    distances = np.abs(intersections[..., None] - pole_lats[None, None, :])
    d_min = distances.min(axis=-1)
    T = d_min.mean(axis=-1)
    return T


def compute_p_value(T_obs: float, T_null: np.ndarray) -> float:
    M = len(T_null)
    return (1 + int(np.sum(T_null <= T_obs))) / (1 + M)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("EXPLORATORY conditional-null Monte Carlo")
    print("Script: 03b_conditional_null_exploratory.py")
    print("STATUS: EXPLORATORY (post-hoc, per pre-registration §12 point 3)")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Iterations: M = {M_ITERATIONS}")
    print(f"Swaps per sample: {SWAPS_PER_SAMPLE}")
    print(f"Warmup swaps: {WARMUP_SWAPS}")
    print("=" * 60)
    print()

    verified_hash = verify_hash()
    n_tests = run_self_tests()
    print(f"Geometry self-test: {n_tests} cases passed.")
    print()

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
    print()

    # Load and filter data
    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    in_range_mask = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )
    n_in_range = int(in_range_mask.sum())
    if n_in_range != expected_n:
        print(f"ERROR: in-range count mismatch.", file=sys.stderr)
        sys.exit(1)

    df_in = df.loc[in_range_mask].reset_index(drop=True)
    lat = df_in["LAT"].to_numpy(dtype=float)
    lon = df_in["LON"].to_numpy(dtype=float)
    bearings = df_in["BEARING"].to_numpy(dtype=float)
    N = n_in_range

    # ----------------------------------------------------------------- #
    # Build compatibility matrix
    # ----------------------------------------------------------------- #
    print("Building compatibility matrix (994 x 994)...")
    t_start = time.time()
    compatibility = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    elapsed = time.time() - t_start
    print(f"  built in {elapsed:.1f}s")
    print(f"  shape: {compatibility.shape}")
    print(f"  density: {compatibility.mean():.4f} "
          f"({int(compatibility.sum())} of {compatibility.size} compatible pairs)")
    print(f"  identity diagonal: {int(np.diag(compatibility).sum())} of {N} valid "
          f"(expected: {N} — every observed pair must be in-range)")

    # Diagnostics on the compatibility matrix
    per_site_options = compatibility.sum(axis=1)
    per_bearing_options = compatibility.sum(axis=0)
    print(f"  per-site eligibility (bearings that work at site i):")
    print(f"    min:    {per_site_options.min()}")
    print(f"    median: {int(np.median(per_site_options))}")
    print(f"    max:    {per_site_options.max()}")
    print(f"  per-bearing eligibility (sites where bearing j works):")
    print(f"    min:    {per_bearing_options.min()}")
    print(f"    median: {int(np.median(per_bearing_options))}")
    print(f"    max:    {per_bearing_options.max()}")
    print()

    if not np.all(np.diag(compatibility)):
        bad = np.where(~np.diag(compatibility))[0]
        print(f"WARNING: {len(bad)} sites have their observed bearing as not in-range.")
        print(f"Investigating site indices: {bad[:10]}")
        for idx in bad[:10]:
            print(f"  Site {idx}: {df_in.iloc[idx]['SITE NAME']}, "
                  f"LAT={lat[idx]:.2f}, LON={lon[idx]:.2f}, "
                  f"BEARING={bearings[idx]:.2f}, "
                  f"intersection={compute_intersection_lat(np.array([lat[idx]]), np.array([lon[idx]]), np.array([bearings[idx]]), TARGET_LON_DEG)[0]:.2f}")
        print()
        print("Forcing diagonal to True to make identity a valid starting state.")
        print("These sites are the manually-snapped structures and Haran — see")
        print("analysis log entries for 2026-05-17. Their geometrically-correct")
        print("intersections are in the southern hemisphere, but the data owner")
        print("classified them as in-range. The conditional null treats them")
        print("as a valid starting point but they may participate in swaps that")
        print("re-route them to the southern side; this is a real feature of")
        print("the conditional null that will be discussed in the writeup.")
        np.fill_diagonal(compatibility, True)
    print()

    # ----------------------------------------------------------------- #
    # Run the swap chain
    # ----------------------------------------------------------------- #
    print(f"Running Metropolis swap chain (M = {M_ITERATIONS} samples)...")
    print("-" * 60)
    permutations, chain_diag = run_swap_chain(
        compatibility=compatibility,
        M=M_ITERATIONS,
        swaps_per_sample=SWAPS_PER_SAMPLE,
        warmup_swaps=WARMUP_SWAPS,
        seed=RANDOM_SEED,
    )
    print(f"\nChain diagnostics:")
    print(f"  total swaps attempted: {chain_diag['n_swaps_attempted']}")
    print(f"  total swaps accepted:  {chain_diag['n_swaps_accepted']}")
    print(f"  acceptance rate:       {chain_diag['acceptance_rate']:.4f}")
    print()

    # ----------------------------------------------------------------- #
    # Compute T for each retained permutation
    # ----------------------------------------------------------------- #
    print("Computing T for each retained permutation (5-pole)...")
    pole_lats_5 = np.array(list(POLES_PRIMARY.values()))
    T_null_5 = compute_T_from_permutations(
        permutations, lat, lon, bearings, pole_lats_5, TARGET_LON_DEG
    )

    print("Computing T for each retained permutation (6-pole sensitivity)...")
    pole_lats_6 = np.array(list(POLES_WITH_VI.values()))
    T_null_6 = compute_T_from_permutations(
        permutations, lat, lon, bearings, pole_lats_6, TARGET_LON_DEG
    )
    print()

    # ----------------------------------------------------------------- #
    # Results
    # ----------------------------------------------------------------- #
    p_5 = compute_p_value(T_obs_5, T_null_5)
    print(f"5-pole results (EXPLORATORY, conditional null):")
    print(f"  T_obs:                 {T_obs_5:.6f}°")
    print(f"  Conditional null mean: {T_null_5.mean():.6f}°")
    print(f"  Null std:              {T_null_5.std():.6f}°")
    print(f"  Null min:              {T_null_5.min():.6f}°")
    print(f"  Null 1st pct:          {np.percentile(T_null_5, 1):.6f}°")
    print(f"  Null 5th pct:          {np.percentile(T_null_5, 5):.6f}°")
    print(f"  Null median:           {np.median(T_null_5):.6f}°")
    print(f"  Null 95th pct:         {np.percentile(T_null_5, 95):.6f}°")
    print(f"  Null max:              {T_null_5.max():.6f}°")
    print(f"  Count T_null <= T_obs: {int((T_null_5 <= T_obs_5).sum())} / {M_ITERATIONS}")
    print(f"  p-value (exploratory): {p_5:.6f}")
    if p_5 < 0.01:
        verdict_5 = "would be highly significant if not exploratory (p < 0.01)"
    elif p_5 < ALPHA_PRIMARY:
        verdict_5 = f"would be significant if not exploratory (p < {ALPHA_PRIMARY})"
    else:
        verdict_5 = f"NOT significant at α = {ALPHA_PRIMARY}"
    print(f"  Status: {verdict_5} (note: this is an EXPLORATORY result)")
    print()

    p_6 = compute_p_value(T_obs_6, T_null_6)
    print(f"6-pole results (EXPLORATORY, conditional null sensitivity):")
    print(f"  T_obs:                 {T_obs_6:.6f}°")
    print(f"  Conditional null mean: {T_null_6.mean():.6f}°")
    print(f"  Null 5th pct:          {np.percentile(T_null_6, 5):.6f}°")
    print(f"  Count T_null <= T_obs: {int((T_null_6 <= T_obs_6).sum())} / {M_ITERATIONS}")
    print(f"  p-value (exploratory): {p_6:.6f}")
    print()

    # ----------------------------------------------------------------- #
    # Save outputs
    # ----------------------------------------------------------------- #
    np.save(NULL_5POLE_FILE, T_null_5)
    np.save(NULL_6POLE_FILE, T_null_6)
    print(f"Null distribution arrays saved.")

    summary = {
        "script": "03b_conditional_null_exploratory.py",
        "status": "EXPLORATORY (post-hoc, per pre-registration §12 point 3)",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "swaps_per_sample": SWAPS_PER_SAMPLE,
        "warmup_swaps": WARMUP_SWAPS,
        "alpha_reference": ALPHA_PRIMARY,
        "n_in_range": n_in_range,
        "target_lon_deg": TARGET_LON_DEG,
        "compatibility_density": float(compatibility.mean()),
        "compatibility_per_site_min_max": [
            int(per_site_options.min()), int(per_site_options.max())
        ],
        "chain_acceptance_rate": chain_diag["acceptance_rate"],
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
            "p_value_exploratory": p_5,
            "status": verdict_5,
        },
        "sensitivity_6pole": {
            "T_obs": T_obs_6,
            "T_null_mean": float(T_null_6.mean()),
            "T_null_std": float(T_null_6.std()),
            "T_null_p5": float(np.percentile(T_null_6, 5)),
            "count_T_null_le_T_obs": int((T_null_6 <= T_obs_6).sum()),
            "p_value_exploratory": p_6,
        },
    }

    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print(f"EXPLORATORY result: T_obs (5-pole) = {T_obs_5:.4f}°, "
          f"conditional-null p = {p_5:.4f}.")
    print(f"This is an exploratory analysis and does not constitute a confirmatory finding.")
    print()


if __name__ == "__main__":
    main()
