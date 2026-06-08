"""
13_asymmetry_circularity_check.py
=================================

Companion diagnostic to script 12, addressing the Branch B/C question raised by
the 8 June 2026 pre-commitment (analysis_log.md, 2026-06-08): when the
hemisphere-preserving null leaves a peak surviving (here Pole III, p_LEE =
0.0135 under the primary cut, per script 12), is that survival a genuine result,
or is it circular — because the East/West bearing asymmetry the null preserves is
*itself* a geometric consequence of intersections being concentrated at
far-northern latitudes on the 47°W meridian?

The test (pre-committed before this code was written)
-----------------------------------------------------
Step 1. D_obs: the observed hemispheric bearing asymmetry = median signed
        bearing (West) - median signed bearing (East), under the pre-committed
        cut(s).
Step 2. Synthetic bearings carrying the observed LATITUDE clustering but NO
        independent hemispheric input: for each in-range site (real lat/lon),
        assign a target intersection latitude drawn from the observed
        distribution of intersection latitudes (permuted across sites), then
        reconstruct the bearing that reaches that target on the 47°W meridian.
        Multiplicity/existence resolved by the LOCKED rule: where more than one
        bearing reaches the target, take the solution of minimum absolute
        deviation from true north (min |bearing|); where none reaches it within
        the folded [-45, 45] range, discard the site and report the count.
        Because bearing 0 = true north sends the great circle through the pole,
        and the sign of the small deviation needed to reach a far-northern
        target is fixed by the site's longitude relative to -47.1, this
        reconstruction uses only geometry + the latitude distribution.
Step 3. D_synth: the same hemispheric-median statistic on the synthetic bearings.
Step 4. R = D_synth / D_obs (a magnitude/sign comparison, not an inferential
        test). Pre-committed interpretation:
            R >= 0.80           -> B1 (asymmetry geometrically entailed; the
                                   Pole III survival under script 12 is circular
                                   and does not vindicate the framework)
            R <= 0.20           -> B2 (asymmetry has independent structure;
                                   genuine result -> v4 pre-registration)
            0.20 < R < 0.80     -> partial; resolved by the secondary criterion:
                                   re-run the hemisphere-preserving conditional
                                   null on the SYNTHETIC bearings and ask whether
                                   Pole III survives. Survives -> B1; not -> B2.

Scope: per the Branch C outcome of script 12, only Pole III need be adjudicated
(Pole II dissolved under the hemisphere-preserving conditional null, p_LEE =
0.46). D_obs / D_synth are whole-dataset asymmetry measures (the asymmetry is a
global feature); the secondary criterion, if triggered, is evaluated at Pole III.

Elaboration of the locked "computed once" framing, documented here: rather than a
single permutation, the synthetic construction is repeated M_SYNTH times and the
DISTRIBUTION of R is reported, with the median R as the headline value compared
to the thresholds. This is strictly more informative than one draw and does not
change the locked decision rule; it is recorded as an elaboration, not a
deviation. A supplementary uniform-target reconstruction is also reported, to
show how much of D_synth comes from "any northern target" versus the observed
latitude clustering specifically.

Standard seed 20260517. Exploratory per pre-registration §12 point 3.

Inputs : data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
         results/02_observed_test_statistic.json
Outputs: results/13_asymmetry_circularity_check.json

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import compute_intersection_lat, run_self_tests  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx"
HASH_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx.sha256"
RESULTS_DIR = REPO_ROOT / "results"
OBS_FILE = RESULTS_DIR / "02_observed_test_statistic.json"
SUMMARY_FILE = RESULTS_DIR / "13_asymmetry_circularity_check.json"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN = 0.0

POLE_III = 72.2
WINDOW_HALF = 1.5
SCAN_CENTERS = np.arange(45.0, 89.0 + 1e-9, 0.25)

CUTS = {"primary_-30 (Americas/OldWorld)": -30.0, "sensitivity_0 (prime meridian)": 0.0}
BEARING_GRID = np.arange(-45.0, 45.0 + 1e-9, 0.1)   # folded range, 0.1° resolution
M_SYNTH = 1000
RANDOM_SEED = 20260517

# Pre-committed thresholds.
R_B1 = 0.80
R_B2 = 0.20


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_hash() -> str:
    expected = HASH_FILE.read_text().split()[0].lower()
    actual = compute_sha256(DATA_FILE)
    if expected != actual:
        print("ERROR: hash mismatch.", file=sys.stderr)
        sys.exit(1)
    print(f"SHA-256 verified: {actual}\n")
    return actual


def parse_marios_intersection_column(series: pd.Series):
    s = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    v = pd.to_numeric(s, errors="coerce").to_numpy()
    return v, ~np.isnan(v)


# ---------------------------------------------------------------------------
# Inverse geometry: min-|bearing| solution reaching a target latitude
# ---------------------------------------------------------------------------


def precompute_phi_grid(lat, lon):
    """PHI[i, g] = intersection latitude for site i at BEARING_GRID[g]."""
    N = len(lat)
    G = len(BEARING_GRID)
    lat_bc = np.broadcast_to(lat[:, None], (N, G))
    lon_bc = np.broadcast_to(lon[:, None], (N, G))
    b_bc = np.broadcast_to(BEARING_GRID[None, :], (N, G))
    return compute_intersection_lat(lat_bc, lon_bc, b_bc, TARGET_LON_DEG)  # (N, G)


MAX_JUMP_DEG = 5.0   # continuity guard: reject grid intervals that jump (pole wrap)
VERIFY_TOL_DEG = 0.5  # a reconstructed bearing must reach its target within this
BISECT_ITERS = 30


def reconstruct_min_dev_bearings(lat, lon, phi_grid, targets):
    """For each site, the min-|bearing| solution whose intersection latitude
    equals targets[i]. Crossings are detected on the grid with a continuity
    guard (rejecting pole-wrap discontinuities), the chosen interval is refined
    by bisection, and the result is verified by forward evaluation; sites with
    no genuine solution are discarded. Returns (bearings, valid_mask)."""
    N = len(targets)
    arange = np.arange(N)
    mid = (BEARING_GRID[:-1] + BEARING_GRID[1:]) / 2.0
    abs_mid = np.abs(mid)[None, :]                                  # (1, G-1)
    d = phi_grid - targets[:, None]                                # (N, G)
    finite = ~np.isnan(d)
    jump = np.abs(phi_grid[:, 1:] - phi_grid[:, :-1])              # (N, G-1)
    s = np.sign(d)
    cross = ((s[:, :-1] * s[:, 1:] < 0)
             & finite[:, :-1] & finite[:, 1:]
             & (jump < MAX_JUMP_DEG))                              # genuine crossings only
    masked = np.where(cross, abs_mid, np.inf)
    jmin = np.argmin(masked, axis=1)
    has = np.isfinite(masked[arange, jmin])

    # Bisection within the chosen [a, b] grid interval (vectorised over sites).
    a = BEARING_GRID[jmin].astype(float)
    b = BEARING_GRID[jmin + 1].astype(float)
    fa = phi_grid[arange, jmin] - targets
    sa = np.sign(fa)
    for _ in range(BISECT_ITERS):
        mbv = 0.5 * (a + b)
        fm = compute_intersection_lat(lat, lon, mbv, TARGET_LON_DEG) - targets
        same = np.sign(fm) == sa
        a = np.where(same, mbv, a)
        b = np.where(same, b, mbv)
    beta = 0.5 * (a + b)

    reach = compute_intersection_lat(lat, lon, beta, TARGET_LON_DEG)
    ok = has & ~np.isnan(reach) & (np.abs(reach - targets) <= VERIFY_TOL_DEG)
    beta = np.where(ok, beta, np.nan)
    return beta, ok


def hemisphere_asymmetry(bearings, lon, cut, valid=None):
    """median(signed bearing | West) - median(signed bearing | East)."""
    west = lon < cut
    if valid is not None:
        west = west & valid
        east = (~(lon < cut)) & valid
    else:
        east = ~(lon < cut)
    bw = bearings[west]; be = bearings[east]
    bw = bw[~np.isnan(bw)]; be = be[~np.isnan(be)]
    if len(bw) == 0 or len(be) == 0:
        return np.nan
    return float(np.median(bw) - np.median(be))


# ---------------------------------------------------------------------------
# Secondary criterion (only if R lands in the partial band): hemisphere-
# preserving conditional null on the SYNTHETIC bearings, Pole III survival.
# ---------------------------------------------------------------------------


def t_max_window(sorted_lats):
    lo = np.searchsorted(sorted_lats, SCAN_CENTERS - WINDOW_HALF, side="left")
    hi = np.searchsorted(sorted_lats, SCAN_CENTERS + WINDOW_HALF, side="right")
    return int((hi - lo).max())


def build_compatibility(lat, lon, bearings):
    N = len(lat)
    lat2 = np.broadcast_to(lat[:, None], (N, N))
    lon2 = np.broadcast_to(lon[:, None], (N, N))
    b2 = np.broadcast_to(bearings[None, :], (N, N))
    inter = compute_intersection_lat(lat2, lon2, b2, TARGET_LON_DEG)
    return (inter >= NORTHERN) & ~np.isnan(inter)


def swap_chain(compat, M, sps, warmup, seed, group):
    rng = np.random.default_rng(seed)
    N = compat.shape[0]
    compat = compat.copy(); np.fill_diagonal(compat, True)
    pi = np.arange(N); total = warmup + M * sps
    perms = np.empty((M, N), dtype=np.int32); done = 0
    while done < total:
        c = min(200_000, total - done)
        ii = rng.integers(0, N, size=c); jj = rng.integers(0, N, size=c)
        for k in range(c):
            i = ii[k]; j = jj[k]
            if i != j and group[i] == group[j]:
                bi = pi[i]; bj = pi[j]
                if compat[i, bj] and compat[j, bi]:
                    pi[i] = bj; pi[j] = bi
            done += 1
            if done > warmup and (done - warmup) % sps == 0:
                s = (done - warmup) // sps - 1
                if 0 <= s < M:
                    perms[s] = pi
    return perms


def pole3_lee_under_null(lat, lon, bearings, cut, seed):
    """Pole III look-elsewhere p-value under the hemisphere-preserving
    conditional null applied to the given (synthetic) bearings."""
    N = len(lat)
    inter = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    lats = inter[(inter >= 0) & ~np.isnan(inter)]
    obs_iii = int(((lats >= POLE_III - WINDOW_HALF) & (lats <= POLE_III + WINDOW_HALF)).sum())
    compat = build_compatibility(lat, lon, bearings)
    group = np.where(lon < cut, 0, 1)
    perms = swap_chain(compat, 10_000, 2 * N, 5 * N, seed, group)
    tmax = np.empty(10_000, dtype=int)
    for i0 in range(0, 10_000, 500):
        i1 = min(i0 + 500, 10_000)
        permuted = bearings[perms[i0:i1]]; size = i1 - i0
        it = compute_intersection_lat(np.broadcast_to(lat, (size, N)),
                                      np.broadcast_to(lon, (size, N)), permuted, TARGET_LON_DEG)
        for r in range(size):
            row = it[r]; row = row[(row >= 0) & ~np.isnan(row)]
            tmax[i0 + r] = t_max_window(np.sort(row))
    return (1 + int((tmax >= obs_iii).sum())) / (1 + 10_000), obs_iii


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("\n" + "=" * 70)
    print("Asymmetry circularity diagnostic (script 13; Branch C -> Pole III)")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Status: EXPLORATORY; specification pre-committed (analysis_log 2026-06-08)")
    print(f"Seed: {RANDOM_SEED}   M_synth = {M_SYNTH}")
    print("=" * 70 + "\n")

    verified_hash = verify_hash()
    print(f"Geometry self-test: {run_self_tests()} cases passed.\n")

    expected_n = json.loads(OBS_FILE.read_text())["n_in_range"]
    df = pd.read_excel(DATA_FILE, sheet_name=PRIMARY_SHEET)
    _, mask = parse_marios_intersection_column(df["Intersection Latitude at Lon 47.1W Line"])
    N = int(mask.sum())
    if N != expected_n:
        print(f"ERROR: in-range count mismatch ({N} vs {expected_n}).", file=sys.stderr)
        sys.exit(1)
    di = df.loc[mask].reset_index(drop=True)
    lat = di["LAT"].to_numpy(float)
    lon = di["LON"].to_numpy(float)
    bearings = di["BEARING"].to_numpy(float)
    print(f"N in-range: {N}")

    obs_phi = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    obs_phi_valid = obs_phi[(obs_phi >= 0) & ~np.isnan(obs_phi)]

    # ---- Step 1: observed asymmetry, both cuts ----
    print("\n--- Step 1: observed hemispheric bearing asymmetry D_obs ---")
    D_obs = {}
    for cut_name, cut in CUTS.items():
        d = hemisphere_asymmetry(bearings, lon, cut)
        D_obs[cut_name] = d
        west = lon < cut
        print(f"  {cut_name}: median bearing West={np.median(bearings[west]):+.2f}  "
              f"East={np.median(bearings[~west]):+.2f}  D_obs={d:+.2f}")

    # ---- Step 2/3: synthetic reconstruction, distribution of D_synth ----
    print(f"\n--- Steps 2-3: synthetic reconstruction ({M_SYNTH} permutations) ---")
    phi_grid = precompute_phi_grid(lat, lon)
    rng = np.random.default_rng(RANDOM_SEED)

    D_synth = {c: np.empty(M_SYNTH) for c in CUTS}
    D_synth_uniform = {c: np.empty(M_SYNTH) for c in CUTS}
    discards = np.empty(M_SYNTH, dtype=int)
    lo_phi, hi_phi = obs_phi_valid.min(), obs_phi_valid.max()

    first_synth_bearings = None
    for it in range(M_SYNTH):
        targets = obs_phi_valid[rng.integers(0, len(obs_phi_valid), size=N)]  # draw from observed dist
        b_syn, valid = reconstruct_min_dev_bearings(lat, lon, phi_grid, targets)
        discards[it] = int((~valid).sum())
        if it == 0:
            first_synth_bearings = (b_syn.copy(), valid.copy())
        for cut_name, cut in CUTS.items():
            D_synth[cut_name][it] = hemisphere_asymmetry(b_syn, lon, cut, valid)
        # uniform-target reference
        tu = rng.uniform(lo_phi, hi_phi, size=N)
        bu, vu = reconstruct_min_dev_bearings(lat, lon, phi_grid, tu)
        for cut_name, cut in CUTS.items():
            D_synth_uniform[cut_name][it] = hemisphere_asymmetry(bu, lon, cut, vu)

    print(f"  mean discards per permutation: {discards.mean():.1f} of {N} "
          f"({100*discards.mean()/N:.1f}%)")

    # ---- Step 4: R and branch, per cut ----
    print("\n--- Step 4: reproduction fraction R = D_synth / D_obs ---")
    results = {}
    for cut_name, cut in CUTS.items():
        ds = D_synth[cut_name]
        dsu = D_synth_uniform[cut_name]
        R = ds / D_obs[cut_name]
        R_med = float(np.median(R))
        R_lo, R_hi = float(np.percentile(R, 5)), float(np.percentile(R, 95))
        R_uniform_med = float(np.median(dsu / D_obs[cut_name]))
        if R_med >= R_B1:
            branch = "B1"
        elif R_med <= R_B2:
            branch = "B2"
        else:
            branch = "partial"
        results[cut_name] = {
            "D_obs": D_obs[cut_name],
            "D_synth_median": float(np.median(ds)),
            "D_synth_5_95": [float(np.percentile(ds, 5)), float(np.percentile(ds, 95))],
            "R_median": R_med, "R_5_95": [R_lo, R_hi],
            "R_uniform_target_median": R_uniform_med,
            "branch": branch,
        }
        print(f"  {cut_name}:")
        print(f"    D_obs={D_obs[cut_name]:+.2f}  D_synth(med)={np.median(ds):+.2f}  "
              f"R(med)={R_med:.2f}  [5–95%: {R_lo:.2f}, {R_hi:.2f}]")
        print(f"    R under uniform targets (reference) = {R_uniform_med:.2f}")
        print(f"    -> {branch}")

    # ---- Secondary criterion, only if primary cut lands in the partial band ----
    primary = [k for k in CUTS if k.startswith("primary")][0]
    secondary = None
    if results[primary]["branch"] == "partial":
        print("\n--- Secondary criterion (partial band): null on synthetic bearings ---")
        b_syn, valid = first_synth_bearings
        use = valid & ~np.isnan(b_syn)
        p3, obs3 = pole3_lee_under_null(lat[use], lon[use], b_syn[use],
                                        CUTS[primary], RANDOM_SEED)
        sec_branch = "B1" if p3 < 0.05 else "B2"
        secondary = {"pole3_lee_on_synthetic": p3, "obs_pole3_synthetic": obs3,
                     "resolved_branch": sec_branch}
        print(f"  Pole III p_LEE on synthetic bearings = {p3:.4f} -> {sec_branch}")
        final_branch = sec_branch
    else:
        final_branch = results[primary]["branch"]

    print("\n" + "=" * 70)
    print("DIAGNOSIS (primary cut)")
    print("=" * 70)
    print(f"  R(median) = {results[primary]['R_median']:.2f}  ->  Branch {final_branch}")
    if final_branch == "B1":
        print("  The hemispheric bearing asymmetry is reproduced from the observed")
        print("  latitude clustering plus geometry alone. The Pole III survival under")
        print("  the hemisphere-preserving null (script 12, 12a) is therefore circular:")
        print("  the null preserves a feature that is itself a consequence of the peak.")
        print("  It does NOT vindicate the framework. v3.1 conclusion stands.")
    else:
        print("  The hemispheric bearing asymmetry has structure beyond what the")
        print("  latitude clustering plus geometry produces. The Pole III survival is")
        print("  a genuine result requiring a v4 pre-registration.")
    print()

    output = {
        "script": "13_asymmetry_circularity_check.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "status": "exploratory_post_publication",
        "precommitment": "analysis_log.md entry 2026-06-08",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_synth": M_SYNTH,
        "bearing_grid_step_deg": 0.1,
        "n_in_range": N,
        "mean_discards_per_perm": float(discards.mean()),
        "thresholds": {"B1_if_R_ge": R_B1, "B2_if_R_le": R_B2},
        "by_cut": results,
        "secondary_criterion": secondary,
        "final_branch_primary_cut": final_branch,
    }
    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}\n")


if __name__ == "__main__":
    main()
