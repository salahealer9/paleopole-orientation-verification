"""
08_finer_block_sensitivity.py
==============================

Post-publication methodological extension. Tests the robustness of the
block-conditional per-pole result (§11(d) / script 06) to the GRANULARITY
of the geographic blocks.

Motivation
----------
The block-conditional null (06) shuffles bearings only within seven coarse
geographic blocks. The Americas block alone holds 539 of 994 in-range
structures (54%). Treating all 539 as exchangeable assumes orientation
independence across the whole hemisphere of the New World. But orientations
are spatially autocorrelated: a single architectural tradition (a cluster of
Maya, or Andean, sites) shares a convention, so many sites carry near-
identical bearings. If the high-north concentration is produced by one or a
few such coherent sub-traditions whose shared orientation happens to project
near 72–76°N, then a free shuffle WITHIN the whole Americas block breaks that
correlation and OVER-DISPERSES the null — inflating significance, because the
effective number of independent draws is closer to "number of traditions"
than "number of sites."

This is the converse of the data owner's concern (Appendix A, point 2), that
within-block shuffling DESTROYS a genuine cross-regional signal. Both worries
point to the same lever: block granularity. This script brackets it by
running the test at three levels of granularity and reporting the trend.

Logic of the test
------------------
  - If p(Pole II), p(Pole III) stay roughly STABLE as blocks get finer:
        the signal is not an artifact of within-Americas exchangeability;
        it is robust to (and, for a truly cross-regional signal, expected to
        survive) finer blocking.
  - If those p-values CLIMB toward non-significance as blocks get finer:
        the apparent excess was driven by autocorrelated sub-traditions
        being counted as independent sites — i.e. pseudoreplication.

Granularity schemes (all refine the coarse 7-block scheme of script 06)
-----------------------------------------------------------------------
  coarse           : exactly the seven blocks of script 06. Run here as an
                     anchor/validation: its block-conditional per-pole means
                     and p-values should match script 06 to within Monte
                     Carlo error. (Not bit-identical: this script uses a
                     within-block swap proposal rather than 06's global
                     proposal-with-rejection, for better mixing at fine
                     granularity. Same stationary distribution; agreement at
                     coarse granularity validates 06's mixing.)

  americas_split   : the Americas block is split by latitude into
                       Am:N.America   (lat >= 23)
                       Am:Mesoamerica (10 <= lat < 23)
                       Am:Andes/S.Am  (lat < 10)
                     All other blocks unchanged. This localises any
                     pseudoreplication to the dominant block.

  fine             : americas_split, plus
                       Middle East split by longitude at 45°E
                         (ME:west lon <= 45, ME:east lon > 45)
                       Europe-Med split by latitude at 40°N
                         (Eur:north lat >= 40, Med:south lat < 40)

Each split uses simple lat/lon bands (pre-registration §11(d) language) and
partitions its parent block exhaustively (no sites dropped).

Tests computed per scheme (block-conditional null only)
-------------------------------------------------------
  §11(a) per-pole confirmatory counts (5-pole primary), Šidák-corrected
  §11(b) site-to-pole assignment match count (secondary, for parity with 06)

The block-conditional (within-hemisphere) constraint is preserved exactly as
in 03b/05/06: a swap is accepted only if both resulting (site, bearing) pairs
produce northern-hemisphere intersections on the 47°W meridian.

Status: post-publication extension, EXPLORATORY per pre-registration §12
point 3.

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json (for the in-range N)

Outputs
-------
- results/08_finer_block_sensitivity.json
- results/08_block_assignments_by_scheme.csv (per-site label under each scheme)
- results/08_null_per_pole_<scheme>.npy  (M, K) per scheme

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
SUMMARY_FILE = RESULTS_DIR / "08_finer_block_sensitivity.json"
LABELS_FILE = RESULTS_DIR / "08_block_assignments_by_scheme.csv"

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
# Block schemes
# ---------------------------------------------------------------------------


def assign_block_coarse(lat: float, lon: float) -> str:
    """Seven coarse blocks — identical to script 06."""
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
    """Coarse, but the Americas split by latitude into three cultural bands."""
    base = assign_block_coarse(lat, lon)
    if base != "Americas":
        return base
    if lat >= 23.0:
        return "Am:N.America"
    if lat >= 10.0:
        return "Am:Mesoamerica"
    return "Am:Andes/S.Am"


def assign_block_fine(lat: float, lon: float) -> str:
    """americas_split, plus Middle East split by longitude and Europe-Med
    split by latitude."""
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
# Statistics (identical to 05 / 06)
# ---------------------------------------------------------------------------


def compute_per_pole_counts(intersection_lats, pole_lats, tol):
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False
    within = np.abs(intersection_lats[..., None] - pole_lats[None, None, :]) <= tol
    counts = within.sum(axis=1).astype(int)
    return counts[0] if squeeze else counts


def compute_assignment_count(intersection_lats, assigned_lats, tol):
    if intersection_lats.ndim == 1:
        intersection_lats = intersection_lats[None, :]
        squeeze = True
    else:
        squeeze = False
    diff = np.abs(intersection_lats - assigned_lats[None, :])
    counts = (diff <= tol).sum(axis=1).astype(int)
    return int(counts[0]) if squeeze else counts


def sidak(p, k):
    return 1.0 - (1.0 - p) ** k


# ---------------------------------------------------------------------------
# Compatibility matrix (identical to 06)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(lat, lon, bearings, target_lon_deg) -> np.ndarray:
    N = len(lat)
    lat_2d = np.broadcast_to(lat[:, None], (N, N))
    lon_2d = np.broadcast_to(lon[:, None], (N, N))
    bearings_2d = np.broadcast_to(bearings[None, :], (N, N))
    intersections = compute_intersection_lat(lat_2d, lon_2d, bearings_2d, target_lon_deg)
    return (intersections >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(intersections)


# ---------------------------------------------------------------------------
# Within-block swap chain (within-hemisphere conditional, any granularity)
# ---------------------------------------------------------------------------


def run_within_block_swap_chain(
    compatibility: np.ndarray,
    members_list: list[np.ndarray],
    M: int,
    swaps_per_sample: int,
    warmup_swaps: int,
    seed: int,
) -> tuple[np.ndarray, dict]:
    """Sample within-block, hemisphere-preserving bearing permutations.

    Unlike 06 (which proposes a global (i, j) and rejects cross-block pairs),
    this proposes swaps WITHIN a block directly: a block is chosen with
    probability proportional to its size, then two of its members. Every
    proposal is therefore useful, which keeps mixing adequate even when the
    finer schemes produce small blocks. The stationary distribution is the
    same as 06's (uniform over hemisphere-compatible within-block
    permutations); at coarse granularity the per-pole null should match 06
    within Monte Carlo error.

    Blocks with fewer than two members have their bearings held fixed
    (conservative).
    """
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

    return permutations, {
        "n_blocks_swappable": B,
        "acceptance_rate": n_acc / max(n_att, 1),
    }


def null_per_pole_and_assign(lat, lon, bearings, permutations, pole_lats,
                             assigned_pole_lats, tol, chunk_size=500):
    M, N = permutations.shape
    K = len(pole_lats)
    null_pp = np.empty((M, K), dtype=int)
    null_as = np.empty(M, dtype=int)
    for i0 in range(0, M, chunk_size):
        i1 = min(i0 + chunk_size, M)
        permuted = bearings[permutations[i0:i1]]
        size = i1 - i0
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
        inter = np.where(np.isnan(inter), 0.0, inter)
        null_pp[i0:i1] = compute_per_pole_counts(inter, pole_lats, tol)
        null_as[i0:i1] = compute_assignment_count(inter, assigned_pole_lats, tol)
    return null_pp, null_as


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 66)
    print("Finer-block sensitivity of the block-conditional per-pole test")
    print("Script: 08_finer_block_sensitivity.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print("Status: EXPLORATORY (post-data) per pre-registration §12 point 3")
    print(f"Random seed: {RANDOM_SEED}   M = {M_ITERATIONS}   tol = ±{TOLERANCE_DEG}°")
    print("=" * 66)
    print()

    verified_hash = verify_hash()
    n_tests = run_self_tests()
    print(f"Geometry self-test: {n_tests} cases passed.")
    print()

    expected_n = json.loads(OBS_FILE.read_text())["n_in_range"]

    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    marios_values, in_range_mask = parse_marios_intersection_column(
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
    marios_int_lat = marios_values[in_range_mask]
    print(f"N in-range: {N}")

    swaps_per_sample = 2 * N
    warmup = 5 * N

    pole_names = list(POLES_PRIMARY.keys())
    pole_lats = np.array(list(POLES_PRIMARY.values()))
    K = len(pole_lats)

    # Assignment (nearest pole to Mario's published intersection lat) — fixed.
    nearest = np.argmin(np.abs(marios_int_lat[:, None] - pole_lats[None, :]), axis=1)
    assigned_pole_lats = pole_lats[nearest]

    # Observed (scheme-independent: uses real bearings)
    inter_obs = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    inter_obs = np.where(np.isnan(inter_obs), 0.0, inter_obs)
    obs_pp = compute_per_pole_counts(inter_obs, pole_lats, TOLERANCE_DEG)
    obs_as = compute_assignment_count(inter_obs, assigned_pole_lats, TOLERANCE_DEG)

    print("Observed per-pole counts (independent geometry):")
    for k, nm in enumerate(pole_names):
        print(f"  Pole {nm:14s} ({pole_lats[k]:5.1f}°N): {obs_pp[k]:4d}")
    print(f"Observed assignment match: {obs_as} / {N}")
    print()

    print("Building compatibility matrix...")
    t = time.time()
    compatibility = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    print(f"  built in {time.time()-t:.1f}s; density {compatibility.mean():.4f}")
    print()

    labels_table = {"SITE_LAT": lat, "SITE_LON": lon}
    output = {
        "script": "08_finer_block_sensitivity.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "status": "exploratory_post_publication",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "tolerance_deg": TOLERANCE_DEG,
        "n_in_range": N,
        "swaps_per_sample": swaps_per_sample,
        "warmup_swaps": warmup,
        "observed_per_pole": {nm: int(obs_pp[k]) for k, nm in enumerate(pole_names)},
        "observed_assignment": int(obs_as),
        "schemes": {},
    }

    for scheme_name, fn in SCHEMES.items():
        print("=" * 66)
        print(f"Scheme: {scheme_name}")
        print("=" * 66)

        block_of_label = np.array([fn(lat[i], lon[i]) for i in range(N)])
        labels_table[scheme_name] = block_of_label
        block_labels = sorted(set(block_of_label.tolist()))
        members_list = [np.where(block_of_label == b)[0] for b in block_labels]
        sizes = {b: int(len(m)) for b, m in zip(block_labels, members_list)}
        print(f"  {len(block_labels)} blocks: "
              + ", ".join(f"{b}={s}" for b, s in sizes.items()))

        perms, diag = run_within_block_swap_chain(
            compatibility, members_list, M_ITERATIONS, swaps_per_sample, warmup, RANDOM_SEED
        )
        print(f"  swappable blocks: {diag['n_blocks_swappable']}  "
              f"acceptance rate: {diag['acceptance_rate']:.4f}")

        null_pp, null_as = null_per_pole_and_assign(
            lat, lon, bearings, perms, pole_lats, assigned_pole_lats, TOLERANCE_DEG
        )
        np.save(RESULTS_DIR / f"08_null_per_pole_{scheme_name}.npy", null_pp)

        p_raw = np.array([
            (1 + int((null_pp[:, k] >= obs_pp[k]).sum())) / (1 + M_ITERATIONS)
            for k in range(K)
        ])
        p_sid = np.array([sidak(p, K) for p in p_raw])
        p_assign = (1 + int((null_as >= obs_as).sum())) / (1 + M_ITERATIONS)

        print(f"  §11(a) per-pole (block-conditional, {scheme_name}):")
        print(f"    {'Pole':14s}  {'obs':>4s}  {'null mean':>9s}  "
              f"{'null std':>8s}  {'p-Šidák':>9s}")
        for k, nm in enumerate(pole_names):
            flag = "  <-- II/III" if nm in ("II", "III") else ""
            print(f"    {nm:14s}  {obs_pp[k]:4d}  {null_pp[:, k].mean():9.2f}  "
                  f"{null_pp[:, k].std():8.2f}  {p_sid[k]:9.4f}{flag}")
        print(f"  §11(b) assignment: obs {obs_as}  null mean "
              f"{null_as.mean():.2f}  p {p_assign:.4f}")
        print()

        output["schemes"][scheme_name] = {
            "n_blocks": len(block_labels),
            "block_sizes": sizes,
            "swappable_blocks": diag["n_blocks_swappable"],
            "acceptance_rate": diag["acceptance_rate"],
            "per_pole": {
                nm: {
                    "obs": int(obs_pp[k]),
                    "null_mean": float(null_pp[:, k].mean()),
                    "null_std": float(null_pp[:, k].std()),
                    "p_raw": float(p_raw[k]),
                    "p_sidak": float(p_sid[k]),
                }
                for k, nm in enumerate(pole_names)
            },
            "assignment": {
                "obs": int(obs_as),
                "null_mean": float(null_as.mean()),
                "p": float(p_assign),
            },
        }

    # Trend summary for II and III across granularity
    print("=" * 66)
    print("TREND: Pole II / III p-Šidák (block-conditional) across granularity")
    print("=" * 66)
    print(f"  {'scheme':16s}  {'n_blocks':>8s}  {'II p-Šidák':>11s}  {'III p-Šidák':>12s}")
    for scheme_name in SCHEMES:
        s = output["schemes"][scheme_name]
        print(f"  {scheme_name:16s}  {s['n_blocks']:8d}  "
              f"{s['per_pole']['II']['p_sidak']:11.4f}  "
              f"{s['per_pole']['III']['p_sidak']:12.4f}")
    print()
    print("  Reference (script 06, 7 coarse blocks): II=0.0015, III=0.0005.")
    print("  Stable across schemes -> robust to within-Americas exchangeability.")
    print("  Climbing toward non-significance      -> pseudoreplication.")
    print()

    pd.DataFrame(labels_table).to_csv(LABELS_FILE, index=False)
    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print(f"Per-site block labels: {LABELS_FILE.relative_to(REPO_ROOT)}")
    print()


if __name__ == "__main__":
    main()
