"""
09_lookelsewhere_under_finer_blocks.py
======================================

Post-publication extension and decision gate for v3.

Scripts 07 and 08 each applied ONE control:
  - 07: latitude look-elsewhere correction, under the unconditional, global
        conditional, and COARSE block-conditional nulls.
  - 08: per-pole test (no look-elsewhere), under coarse / americas_split /
        fine block-conditional nulls.

They left one asymmetry unexamined. Under the assumption-free GLOBAL
conditional null, the latitude look-elsewhere correction kills Pole III
(07: p_III = 0.90). Under the COARSE block-conditional null it survives
(07: p_III = 0.0003). The pseudoreplication account (08) says the block
null's significance is partly manufactured by treating autocorrelated
sub-traditions as independent, and that it should erode as blocks get
finer. If that account is correct, then applying BOTH controls together —
the latitude look-elsewhere correction UNDER finer-block nulls — should
push Pole III's corrected p upward, toward the global-null result.

This script tests exactly that. For each block scheme of 08
(coarse / americas_split / fine) it builds the within-block-conditional
null (08's well-mixed within-block swap chain), and for each null draw
computes the MAXIMUM ±1.5° window count anywhere in the scan range
(07's statistic). The look-elsewhere-corrected p-values for Pole II and
Pole III are then read off the null distribution of that maximum.

Decision gate
-------------
  - coarse row should reproduce 07's block-conditional look-elsewhere
    result (T_max mean ~110; p_II ~0.004; p_III ~0.0003), within Monte
    Carlo error. This validates the wiring. (07 used a global-proposal
    swap chain; this script uses 08's within-block proposal. Same
    stationary distribution; agreement at coarse granularity confirms it.)

  - If p_III climbs toward non-significance from coarse -> fine, the
    pseudoreplication + look-elsewhere account is coherent and v3 can
    state plainly that Pole III's survival was null-dependent and does
    not hold once both controls are applied. PUBLISH.

  - If p_III stays small under fine blocking, the global-vs-block
    asymmetry is NOT explained by autocorrelation, Pole III is a genuine
    residual surviving both controls, and the v3 interpretation needs
    rethinking before deposit. DO NOT PUBLISH on the current story.

Status: post-publication extension, EXPLORATORY per pre-registration §12
point 3.

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json (for the in-range N)

Outputs
-------
- results/09_lookelsewhere_under_finer_blocks.json
- results/09_null_maxcount_<scheme>.npy  (M, 2): cols [PRIMARY, WIDE]

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
SUMMARY_FILE = RESULTS_DIR / "09_lookelsewhere_under_finer_blocks.json"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN_HEMISPHERE_THRESHOLD = 0.0
TOLERANCE_DEG = 1.5

POLE_II_LAT = 76.0
POLE_III_LAT = 72.2

# Scan grid — identical to 07.
SCAN_STEP_DEG = 0.25
SCAN_LAT_MIN = 45.0
SCAN_PRIMARY_MAX = 89.0
SCAN_WIDE_MAX = 90.0

M_ITERATIONS = 10_000
RANDOM_SEED = 20260517


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
# Block schemes (identical to 08)
# ---------------------------------------------------------------------------


def assign_block_coarse(lat: float, lon: float) -> str:
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


def assign_block_americas_split(lat: float, lon: float) -> str:
    base = assign_block_coarse(lat, lon)
    if base != "Americas":
        return base
    if lat >= 23.0:
        return "Am:N.America"
    if lat >= 10.0:
        return "Am:Mesoamerica"
    return "Am:Andes/S.Am"


def assign_block_fine(lat: float, lon: float) -> str:
    base = assign_block_americas_split(lat, lon)
    if base == "Middle East":
        return "ME:west" if lon <= 45.0 else "ME:east"
    if base == "Europe-Med":
        return "Eur:north" if lat >= 40.0 else "Med:south"
    return base


SCHEMES = {
    "coarse": assign_block_coarse,
    "americas_split": assign_block_americas_split,
    "fine": assign_block_fine,
}


# ---------------------------------------------------------------------------
# Scan statistic (identical to 07)
# ---------------------------------------------------------------------------


def window_counts(intersection_lats: np.ndarray, centres: np.ndarray, tol: float) -> np.ndarray:
    within = np.abs(intersection_lats[:, :, None] - centres[None, None, :]) <= tol
    return within.sum(axis=1).astype(np.int32)


def max_counts_two_ranges(intersection_lats, centres, primary_mask, tol):
    counts = window_counts(intersection_lats, centres, tol)
    return np.stack([counts[:, primary_mask].max(axis=1), counts.max(axis=1)], axis=1)


# ---------------------------------------------------------------------------
# Compatibility matrix (identical to 06/07/08)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(lat, lon, bearings, target_lon_deg) -> np.ndarray:
    N = len(lat)
    lat_2d = np.broadcast_to(lat[:, None], (N, N))
    lon_2d = np.broadcast_to(lon[:, None], (N, N))
    bearings_2d = np.broadcast_to(bearings[None, :], (N, N))
    intersections = compute_intersection_lat(lat_2d, lon_2d, bearings_2d, target_lon_deg)
    return (intersections >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(intersections)


# ---------------------------------------------------------------------------
# Within-block swap chain (identical to 08)
# ---------------------------------------------------------------------------


def run_within_block_swap_chain(compatibility, members_list, M, swaps_per_sample,
                                warmup_swaps, seed):
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]
    compatibility = compatibility.copy()
    np.fill_diagonal(compatibility, True)

    swap_blocks = [m for m in members_list if len(m) >= 2]
    sizes = np.array([len(m) for m in swap_blocks], dtype=float)
    weights = sizes / sizes.sum()
    B = len(swap_blocks)

    pi = np.arange(N)
    total = warmup_swaps + M * swaps_per_sample
    permutations = np.empty((M, N), dtype=np.int32)
    n_acc = 0
    n_att = 0
    t0 = time.time()
    done = 0
    proposal_chunk = 200_000
    while done < total:
        c = min(proposal_chunk, total - done)
        bsel = rng.choice(B, size=c, p=weights)
        u1 = rng.random(c)
        u2 = rng.random(c)
        for k in range(c):
            mem = swap_blocks[bsel[k]]
            nb = mem.shape[0]
            a = int(u1[k] * nb)
            b = int(u2[k] * nb)
            if a != b:
                i = mem[a]
                j = mem[b]
                bi = pi[i]
                bj = pi[j]
                if compatibility[i, bj] and compatibility[j, bi]:
                    pi[i] = bj
                    pi[j] = bi
                    n_acc += 1
            n_att += 1
            done += 1
            if done > warmup_swaps:
                aw = done - warmup_swaps
                if aw % swaps_per_sample == 0:
                    si = aw // swaps_per_sample - 1
                    if 0 <= si < M:
                        permutations[si] = pi
        if (done // (total // 10 + 1)) > ((done - c) // (total // 10 + 1)):
            print(f"    swap progress: {done}/{total} ({100.0*done/total:5.1f}%)  "
                  f"elapsed {time.time()-t0:5.1f}s  accept {n_acc/max(n_att,1):.3f}")
    return permutations, {"acceptance_rate": n_acc / max(n_att, 1)}


def null_max_from_permutations(lat, lon, bearings, permutations, centres,
                               primary_mask, tol, chunk_size=500):
    M, N = permutations.shape
    out = np.empty((M, 2), dtype=np.int32)
    for i0 in range(0, M, chunk_size):
        i1 = min(i0 + chunk_size, M)
        permuted = bearings[permutations[i0:i1]]
        size = i1 - i0
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
        inter = np.where(np.isnan(inter), 0.0, inter)
        out[i0:i1] = max_counts_two_ranges(inter, centres, primary_mask, tol)
    return out


def lee_p(col, observed_value, M):
    return (1 + int((col >= observed_value).sum())) / (1 + M)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 68)
    print("Latitude look-elsewhere UNDER finer-block nulls (v3 decision gate)")
    print("Script: 09_lookelsewhere_under_finer_blocks.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print("Status: EXPLORATORY (post-data) per pre-registration §12 point 3")
    print(f"Random seed: {RANDOM_SEED}   M = {M_ITERATIONS}   tol = ±{TOLERANCE_DEG}°")
    print("=" * 68)
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

    swaps_per_sample = 2 * N
    warmup = 5 * N

    centres = np.arange(SCAN_LAT_MIN, SCAN_WIDE_MAX + 1e-9, SCAN_STEP_DEG)
    primary_mask = centres <= SCAN_PRIMARY_MAX + 1e-9

    # Observed (scheme-independent)
    inter_obs = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    inter_obs = np.where(np.isnan(inter_obs), 0.0, inter_obs)
    obs_count_II = int((np.abs(inter_obs - POLE_II_LAT) <= TOLERANCE_DEG).sum())
    obs_count_III = int((np.abs(inter_obs - POLE_III_LAT) <= TOLERANCE_DEG).sum())
    counts_obs = window_counts(inter_obs[None, :], centres, TOLERANCE_DEG)[0]
    obs_tmax_primary = int(counts_obs[primary_mask].max())
    obs_tmax_wide = int(counts_obs.max())
    print(f"Observed: count II(76.0)={obs_count_II}  III(72.2)={obs_count_III}  "
          f"T_max PRIMARY={obs_tmax_primary}  T_max WIDE={obs_tmax_wide}")
    print()

    print("Building compatibility matrix...")
    t = time.time()
    compatibility = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    print(f"  built in {time.time()-t:.1f}s; density {compatibility.mean():.4f}")
    print()

    output = {
        "script": "09_lookelsewhere_under_finer_blocks.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "status": "exploratory_post_publication",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "tolerance_deg": TOLERANCE_DEG,
        "n_in_range": N,
        "scan": {"step_deg": SCAN_STEP_DEG,
                 "primary_range": [SCAN_LAT_MIN, SCAN_PRIMARY_MAX],
                 "wide_range": [SCAN_LAT_MIN, SCAN_WIDE_MAX]},
        "observed": {"count_II": obs_count_II, "count_III": obs_count_III,
                     "T_max_primary": obs_tmax_primary, "T_max_wide": obs_tmax_wide},
        "schemes": {},
    }

    for scheme_name, fn in SCHEMES.items():
        print("=" * 68)
        print(f"Scheme: {scheme_name}")
        print("=" * 68)
        block_of_label = np.array([fn(lat[i], lon[i]) for i in range(N)])
        block_labels = sorted(set(block_of_label.tolist()))
        members_list = [np.where(block_of_label == b)[0] for b in block_labels]
        print(f"  {len(block_labels)} blocks")
        perms, diag = run_within_block_swap_chain(
            compatibility, members_list, M_ITERATIONS, swaps_per_sample, warmup, RANDOM_SEED
        )
        print(f"  acceptance rate: {diag['acceptance_rate']:.4f}")
        nmax = null_max_from_permutations(
            lat, lon, bearings, perms, centres, primary_mask, TOLERANCE_DEG
        )
        np.save(RESULTS_DIR / f"09_null_maxcount_{scheme_name}.npy", nmax)

        scheme_out = {"n_blocks": len(block_labels),
                      "acceptance_rate": diag["acceptance_rate"]}
        for ri, rname in enumerate(["PRIMARY", "WIDE"]):
            col = nmax[:, ri]
            obs_tmax = obs_tmax_primary if rname == "PRIMARY" else obs_tmax_wide
            scheme_out[rname] = {
                "null_Tmax_mean": float(col.mean()),
                "null_Tmax_std": float(col.std()),
                "p_any": lee_p(col, obs_tmax, M_ITERATIONS),
                "p_II": lee_p(col, obs_count_II, M_ITERATIONS),
                "p_III": lee_p(col, obs_count_III, M_ITERATIONS),
            }
        output["schemes"][scheme_name] = scheme_out
        pr = scheme_out["PRIMARY"]
        print(f"  PRIMARY: null T_max mean {pr['null_Tmax_mean']:.2f} "
              f"(std {pr['null_Tmax_std']:.2f})  "
              f"p_II={pr['p_II']:.4f}  p_III={pr['p_III']:.4f}")
        print()

    # Decision-gate table
    print("=" * 68)
    print("GATE: latitude-LEE-corrected p (PRIMARY range) across granularity")
    print("=" * 68)
    print(f"  {'scheme':16s}  {'null T_max mean':>15s}  {'p_II':>8s}  {'p_III':>8s}")
    for scheme_name in SCHEMES:
        s = output["schemes"][scheme_name]["PRIMARY"]
        print(f"  {scheme_name:16s}  {s['null_Tmax_mean']:15.2f}  "
              f"{s['p_II']:8.4f}  {s['p_III']:8.4f}")
    print()
    print("  Anchor: 07 block-conditional LEE gave p_II=0.0043, p_III=0.0003.")
    print("  The 'coarse' row here should match that within MC error.")
    print()
    print("  Reading:")
    print("   - p_III climbs coarse->fine toward non-significance:")
    print("       pseudoreplication + look-elsewhere account is COHERENT. Publish v3")
    print("       stating Pole III's survival was null-dependent and does not hold")
    print("       once both controls are applied.")
    print("   - p_III stays small under 'fine':")
    print("       Pole III is a genuine residual surviving BOTH controls. The")
    print("       global-vs-block asymmetry is NOT autocorrelation. Rethink before")
    print("       deposit.")
    print()

    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()


if __name__ == "__main__":
    main()
