"""
07_latitude_lookelsewhere.py
=============================

Post-publication methodological extension. Adds a LATITUDE look-elsewhere
control to complement the longitude look-elsewhere control of §10.

Motivation
----------
Script 05 (§11(a)) tests structure counts within ±1.5° of FIVE specific
pole latitudes, with a Šidák correction for five simultaneous tests. That
correction is the right one IF the five latitudes were independent a priori
predictions. They were not: the data owner states in his commentary
(final report, Appendix A, point 3) that Poles II–V "were identified
partly through examination of the orientation data." The targets were
therefore read off the same intersection-latitude distribution against
which they are being tested.

This is the exact researcher-degree-of-freedom that motivated the §10
longitude scan (47°W was a chosen meridian). The longitude axis was
corrected with a min-T-over-72-meridians null; the latitude axis was not.
This script supplies the missing control: it asks how often a null model
produces a ±1.5° window AS FULL AS the observed Pole II / Pole III windows
ANYWHERE in the scanned latitude range — i.e. it compares the observed
peak counts to the null distribution of the MAXIMUM window count over a
grid of candidate latitudes.

Scope of the scan
-----------------
Pole I is the CURRENT geographic pole (90°N) and is known a priori; it was
not found by scanning the data. The look-elsewhere multiplicity therefore
applies to the search that produced Poles II–V, which a researcher would
conduct over the latitude axis below the known pole. The primary scan range
is [45°, 89°] (PRIMARY); a [45°, 90°] variant (WIDE) is also reported so the
effect of including the near-pole geometric-convergence region can be seen
directly. Window centres are stepped at 0.25°; window half-width is the
pre-registered ±1.5°.

Statistic
---------
For a set of intersection latitudes and a grid of window centres {c_g},
  count(c_g) = #{ i : |intersection_lat_i - c_g| <= 1.5 }
  T_max      = max_g count(c_g)        (over the scan range)

Look-elsewhere-corrected p-values, one-sided in the high-count direction:
  p_any  = P_null( T_max >= observed T_max )
  p_II   = P_null( T_max >= observed count within 1.5° of 76.0°N )
  p_III  = P_null( T_max >= observed count within 1.5° of 72.2°N )

p_II and p_III are the headline numbers: they ask whether a window as full
as the chosen peak is surprising once the freedom to choose its latitude is
accounted for. Compare these against the §11(a) Šidák p-values (II: 0.0015,
III: 0.0005 under the block-conditional null) to see how much of the
reported significance survives latitude look-elsewhere.

Null models (identical construction to scripts 03/03b/05/06)
------------------------------------------------------------
  - unconditional      : free permutation of folded bearings (§7)
  - conditional        : global within-hemisphere swap chain (03b)
  - block-conditional  : within-block within-hemisphere swap chain (§11(d), 06)

All three use seed 20260517 and M = 10,000, so the permutation streams match
the corresponding scripts exactly; this script only changes the statistic
computed from each permutation.

Status: post-publication extension, EXPLORATORY per pre-registration §12
point 3 (any analysis specified after the data were opened is labelled
exploratory and is not a confirmatory test).

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json (for the in-range N)

Outputs
-------
- results/07_latitude_lookelsewhere.json
- results/07_observed_scan_profile.csv          (centre, observed_count)
- results/07_null_maxcount_unconditional.npy    (M, 2): cols [PRIMARY, WIDE]
- results/07_null_maxcount_conditional.npy      (M, 2)
- results/07_null_maxcount_block_conditional.npy (M, 2)

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
SUMMARY_FILE = RESULTS_DIR / "07_latitude_lookelsewhere.json"
PROFILE_FILE = RESULTS_DIR / "07_observed_scan_profile.csv"
NULL_FILES = {
    "unconditional":     RESULTS_DIR / "07_null_maxcount_unconditional.npy",
    "conditional":       RESULTS_DIR / "07_null_maxcount_conditional.npy",
    "block_conditional": RESULTS_DIR / "07_null_maxcount_block_conditional.npy",
}

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN_HEMISPHERE_THRESHOLD = 0.0
TOLERANCE_DEG = 1.5

# Data-derived poles whose latitude was selected from the distribution.
POLE_II_LAT = 76.0
POLE_III_LAT = 72.2

# Scan grid. Centres stepped at 0.25°; two ranges reported.
SCAN_STEP_DEG = 0.25
SCAN_LAT_MIN = 45.0
SCAN_PRIMARY_MAX = 89.0   # excludes the 90° convergence singularity (Pole I, a priori)
SCAN_WIDE_MAX = 90.0      # includes it, for sensitivity

M_ITERATIONS = 10_000
RANDOM_SEED = 20260517
CHUNK_SIZE = 500

# Swap-chain parameters (identical to 03b / 05 / 06).
SWAPS_PER_SAMPLE = 2 * 994
WARMUP_SWAPS = 5 * 994


# ---------------------------------------------------------------------------
# Hash verification (identical to other scripts)
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


def parse_marios_intersection_column(series: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    str_series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    values = pd.to_numeric(str_series, errors="coerce").to_numpy()
    return values, ~np.isnan(values)


# ---------------------------------------------------------------------------
# Block assignment (identical to 06)
# ---------------------------------------------------------------------------


def assign_block(lat: float, lon: float) -> str:
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
# The latitude-scan statistic
# ---------------------------------------------------------------------------


def window_counts(intersection_lats: np.ndarray, centres: np.ndarray, tol: float) -> np.ndarray:
    """Count, for each row of intersection_lats and each window centre, the
    number of intersections within ±tol of the centre.

    Parameters
    ----------
    intersection_lats : (K, N)
    centres : (G,)
    tol : float

    Returns
    -------
    counts : (K, G) int32
    """
    within = np.abs(intersection_lats[:, :, None] - centres[None, None, :]) <= tol
    return within.sum(axis=1).astype(np.int32)


def max_counts_two_ranges(
    intersection_lats: np.ndarray,
    centres: np.ndarray,
    primary_mask: np.ndarray,
    tol: float,
) -> np.ndarray:
    """Return (K, 2): max window count over PRIMARY range and over WIDE range."""
    counts = window_counts(intersection_lats, centres, tol)  # (K, G)
    tmax_wide = counts.max(axis=1)
    tmax_primary = counts[:, primary_mask].max(axis=1)
    return np.stack([tmax_primary, tmax_wide], axis=1)


# ---------------------------------------------------------------------------
# Null permutation streams (identical construction to 03b / 05 / 06)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(lat, lon, bearings, target_lon_deg) -> np.ndarray:
    N = len(lat)
    lat_2d = np.broadcast_to(lat[:, None], (N, N))
    lon_2d = np.broadcast_to(lon[:, None], (N, N))
    bearings_2d = np.broadcast_to(bearings[None, :], (N, N))
    intersections = compute_intersection_lat(lat_2d, lon_2d, bearings_2d, target_lon_deg)
    return (intersections >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(intersections)


def run_swap_chain(compatibility, M, swaps_per_sample, warmup_swaps, seed,
                   block_of=None):
    """Metropolis swap chain on the (site, bearing) compatibility graph.

    If block_of is None: global swaps (conditional null, as in 03b/05).
    If block_of is an int array of length N: swaps only within a block
    (block-conditional null, as in 06).
    """
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]

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
            same_block = True if block_of is None else (block_of[i] == block_of[j])
            if i != j and same_block:
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
            print(f"    swap progress: {swap_idx_global}/{total_swaps} ({pct:5.1f}%)  "
                  f"elapsed {elapsed:5.1f}s  accept {n_accepted/max(n_attempted,1):.3f}")

    return permutations, n_accepted / max(n_attempted, 1)


# ---------------------------------------------------------------------------
# Null runners — each returns (M, 2) array of [T_max_primary, T_max_wide]
# ---------------------------------------------------------------------------


def null_max_unconditional(lat, lon, bearings_pool, centres, primary_mask,
                           tol, M, seed, chunk_size):
    rng = np.random.default_rng(seed)
    N = len(lat)
    out = np.empty((M, 2), dtype=np.int32)
    n_chunks = (M + chunk_size - 1) // chunk_size
    t0 = time.time()
    for c in range(n_chunks):
        i0 = c * chunk_size
        i1 = min(i0 + chunk_size, M)
        size = i1 - i0
        permuted = np.empty((size, N), dtype=float)
        for k in range(size):
            permuted[k] = rng.permutation(bearings_pool)
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
        inter = np.where(np.isnan(inter), 0.0, inter)
        out[i0:i1] = max_counts_two_ranges(inter, centres, primary_mask, tol)
        if (c + 1) % max(1, n_chunks // 5) == 0 or c == n_chunks - 1:
            print(f"    unconditional: {i1}/{M}  elapsed {time.time()-t0:5.1f}s")
    return out


def null_max_from_permutations(lat, lon, bearings, permutations, centres,
                               primary_mask, tol, chunk_size):
    M, N = permutations.shape
    out = np.empty((M, 2), dtype=np.int32)
    n_chunks = (M + chunk_size - 1) // chunk_size
    t0 = time.time()
    for c in range(n_chunks):
        i0 = c * chunk_size
        i1 = min(i0 + chunk_size, M)
        permuted = bearings[permutations[i0:i1]]
        size = i1 - i0
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
        inter = np.where(np.isnan(inter), 0.0, inter)
        out[i0:i1] = max_counts_two_ranges(inter, centres, primary_mask, tol)
        if (c + 1) % max(1, n_chunks // 5) == 0 or c == n_chunks - 1:
            print(f"    scan: {i1}/{M}  elapsed {time.time()-t0:5.1f}s")
    return out


# ---------------------------------------------------------------------------
# p-value helper
# ---------------------------------------------------------------------------


def lee_p(null_max_col: np.ndarray, observed_value: int, M: int) -> float:
    return (1 + int((null_max_col >= observed_value).sum())) / (1 + M)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 64)
    print("Latitude look-elsewhere control (post-publication extension)")
    print("Script: 07_latitude_lookelsewhere.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print("Status: EXPLORATORY (post-data) per pre-registration §12 point 3")
    print(f"Random seed: {RANDOM_SEED}   M = {M_ITERATIONS}   tol = ±{TOLERANCE_DEG}°")
    print("=" * 64)
    print()

    verified_hash = verify_hash()
    n_tests = run_self_tests()
    print(f"Geometry self-test: {n_tests} cases passed.")
    print()

    expected_n = json.loads(OBS_FILE.read_text())["n_in_range"]

    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    _, in_range_mask = parse_marios_intersection_column(
        df["Intersection Latitude at Lon 47.1W Line"]
    )
    N = int(in_range_mask.sum())
    if N != expected_n:
        print(f"ERROR: in-range count mismatch ({N} vs {expected_n}).", file=sys.stderr)
        sys.exit(1)

    df_in = df.loc[in_range_mask].reset_index(drop=True)
    lat = df_in["LAT"].to_numpy(dtype=float)
    lon = df_in["LON"].to_numpy(dtype=float)
    bearings = df_in["BEARING"].to_numpy(dtype=float)
    print(f"N in-range: {N}")

    centres = np.arange(SCAN_LAT_MIN, SCAN_WIDE_MAX + 1e-9, SCAN_STEP_DEG)
    primary_mask = centres <= SCAN_PRIMARY_MAX + 1e-9
    print(f"Scan grid: {len(centres)} centres from {SCAN_LAT_MIN}° to "
          f"{SCAN_WIDE_MAX}° at {SCAN_STEP_DEG}° step")
    print(f"  PRIMARY range [{SCAN_LAT_MIN}, {SCAN_PRIMARY_MAX}]  "
          f"({int(primary_mask.sum())} centres)")
    print(f"  WIDE    range [{SCAN_LAT_MIN}, {SCAN_WIDE_MAX}]  ({len(centres)} centres)")
    print()

    # ---- observed ----
    inter_obs = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    inter_obs = np.where(np.isnan(inter_obs), 0.0, inter_obs)

    counts_obs = window_counts(inter_obs[None, :], centres, TOLERANCE_DEG)[0]
    obs_tmax_primary = int(counts_obs[primary_mask].max())
    obs_tmax_wide = int(counts_obs.max())
    obs_argmax_primary = float(centres[primary_mask][np.argmax(counts_obs[primary_mask])])
    obs_argmax_wide = float(centres[np.argmax(counts_obs)])

    obs_count_II = int((np.abs(inter_obs - POLE_II_LAT) <= TOLERANCE_DEG).sum())
    obs_count_III = int((np.abs(inter_obs - POLE_III_LAT) <= TOLERANCE_DEG).sum())

    print("Observed:")
    print(f"  count within ±{TOLERANCE_DEG}° of Pole II  (76.0°N): {obs_count_II}")
    print(f"  count within ±{TOLERANCE_DEG}° of Pole III (72.2°N): {obs_count_III}")
    print(f"  T_max PRIMARY = {obs_tmax_primary} at {obs_argmax_primary:.2f}°N")
    print(f"  T_max WIDE    = {obs_tmax_wide} at {obs_argmax_wide:.2f}°N")
    print()

    pd.DataFrame({"centre_lat": centres, "observed_count": counts_obs}).to_csv(
        PROFILE_FILE, index=False
    )

    # ---- nulls ----
    print("Building compatibility matrix (conditional / block-conditional)...")
    t = time.time()
    compatibility = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    print(f"  built in {time.time()-t:.1f}s; density {compatibility.mean():.4f}")

    blocks = np.array([assign_block(lat[i], lon[i]) for i in range(N)])
    block_labels = sorted(set(blocks.tolist()))
    block_of = np.array([block_labels.index(b) for b in blocks], dtype=int)
    print(f"  blocks: " + ", ".join(f"{b}={int((blocks==b).sum())}" for b in block_labels))
    print()

    null_max = {}

    print("[1/3] unconditional null...")
    null_max["unconditional"] = null_max_unconditional(
        lat, lon, bearings, centres, primary_mask, TOLERANCE_DEG,
        M_ITERATIONS, RANDOM_SEED, CHUNK_SIZE,
    )

    print("[2/3] conditional null (global swap chain)...")
    perms_cond, acc_cond = run_swap_chain(
        compatibility, M_ITERATIONS, SWAPS_PER_SAMPLE, WARMUP_SWAPS, RANDOM_SEED,
        block_of=None,
    )
    print(f"    acceptance rate {acc_cond:.4f}")
    null_max["conditional"] = null_max_from_permutations(
        lat, lon, bearings, perms_cond, centres, primary_mask, TOLERANCE_DEG, CHUNK_SIZE
    )

    print("[3/3] block-conditional null (within-block swap chain)...")
    perms_block, acc_block = run_swap_chain(
        compatibility, M_ITERATIONS, SWAPS_PER_SAMPLE, WARMUP_SWAPS, RANDOM_SEED,
        block_of=block_of,
    )
    print(f"    acceptance rate {acc_block:.4f}")
    null_max["block_conditional"] = null_max_from_permutations(
        lat, lon, bearings, perms_block, centres, primary_mask, TOLERANCE_DEG, CHUNK_SIZE
    )
    print()

    for name, arr in null_max.items():
        np.save(NULL_FILES[name], arr)

    # ---- p-values ----
    range_names = ["PRIMARY", "WIDE"]
    output = {
        "script": "07_latitude_lookelsewhere.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "status": "exploratory_post_publication",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "tolerance_deg": TOLERANCE_DEG,
        "n_in_range": N,
        "scan": {
            "step_deg": SCAN_STEP_DEG,
            "primary_range": [SCAN_LAT_MIN, SCAN_PRIMARY_MAX],
            "wide_range": [SCAN_LAT_MIN, SCAN_WIDE_MAX],
        },
        "observed": {
            "count_pole_II_76.0": obs_count_II,
            "count_pole_III_72.2": obs_count_III,
            "T_max_primary": obs_tmax_primary,
            "T_max_primary_at_lat": obs_argmax_primary,
            "T_max_wide": obs_tmax_wide,
            "T_max_wide_at_lat": obs_argmax_wide,
        },
        "results": {},
    }

    print("=" * 64)
    print("LATITUDE LOOK-ELSEWHERE p-VALUES")
    print("(compare to §11(a) Šidák: II=0.0015, III=0.0005 under block-cond.)")
    print("=" * 64)
    for ri, rname in enumerate(range_names):
        print(f"\n--- scan range: {rname} "
              f"[{SCAN_LAT_MIN}, {SCAN_PRIMARY_MAX if rname=='PRIMARY' else SCAN_WIDE_MAX}] ---")
        print(f"  {'null model':20s}  {'null T_max mean':>15s}  "
              f"{'p_any':>8s}  {'p_II':>8s}  {'p_III':>8s}")
        for name, arr in null_max.items():
            col = arr[:, ri]
            p_any = lee_p(col, obs_tmax_primary if rname == "PRIMARY" else obs_tmax_wide, M_ITERATIONS)
            p_II = lee_p(col, obs_count_II, M_ITERATIONS)
            p_III = lee_p(col, obs_count_III, M_ITERATIONS)
            print(f"  {name:20s}  {col.mean():15.2f}  "
                  f"{p_any:8.4f}  {p_II:8.4f}  {p_III:8.4f}")
            output["results"].setdefault(rname, {})[name] = {
                "null_Tmax_mean": float(col.mean()),
                "null_Tmax_std": float(col.std()),
                "null_Tmax_p95": float(np.percentile(col, 95)),
                "p_any": p_any,
                "p_II": p_II,
                "p_III": p_III,
            }

    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print()
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print(f"Observed scan profile: {PROFILE_FILE.relative_to(REPO_ROOT)}")
    print()
    print("Interpretation: p_II and p_III are the observed Pole II / III window")
    print("counts compared against the null distribution of the MAXIMUM window")
    print("count anywhere in the scan range. If these are markedly larger than")
    print("the §11(a) Šidák p-values, the reported significance was inflated by")
    print("treating five data-derived latitudes as a priori predictions.")
    print()


if __name__ == "__main__":
    main()
