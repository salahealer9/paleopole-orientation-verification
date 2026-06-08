"""
12_hemisphere_preserving_null.py
================================

Post-publication extension, addressing point 1 of the data owner's 8 June 2026
second follow-up letter: that the v3 null models (03b global conditional, 06
block-conditional, 10 spatial-cluster) do not preserve the East/West hemispheric
bearing asymmetry from which he derived the 47°W meridian, and therefore "erase
the structure that produces the peaks before testing them."

This script runs nulls that PRESERVE that asymmetry, by permuting bearings only
within hemispheres, and re-computes the per-pole counts and the latitude
look-elsewhere correction under them. Specification, decision rule, and
interpretation were pre-committed in results/analysis_log.md (entry dated
2026-06-08) BEFORE this code was written. This script implements that
pre-commitment without deviation; any deviation is to be logged separately.

Locked specification (see log)
------------------------------
Hemisphere cut:
  - PRIMARY (Americas / Old World): West = lon in [-180, -30); East = [-30, 180].
    Matches the data owner's stated asymmetry (Americas vs Old World).
  - SENSITIVITY (prime meridian): West = [-180, 0); East = [0, 180].
  Both cuts are run. Data-derived cuts (47°W, ±20°E) are rejected as
  conditioning the null on the conclusion under test.

Three nulls, each under each cut:
  12a conditional, hemisphere-preserving      (swap restricted to same hemisphere)
  12b block-conditional, hemisphere-preserving (swap restricted to block × hemisphere)
  12c spatial-cluster, hemisphere-preserving   (25 km cluster reps; swap within hemisphere)

For each null: per-pole counts at Poles I–V; latitude look-elsewhere corrected
p-values at Poles II and III. The look-elsewhere maximum-window distribution is
computed from THIS null's own per-degree window scan, NOT reused from script 07.

Descriptive output (reported regardless of branch): hemisphere fractions under
each cut; per-hemisphere intersection-latitude summary; hemisphere membership of
the observed Pole III (72.2°N ±1.5°) contributors.

Decision rule (read off 12a, PRIMARY cut, look-elsewhere corrected):
  Branch A : Pole II p_LEE >= 0.05 AND Pole III p_LEE >= 0.05
             -> peaks dissolve under the hemisphere-preserving null; point 1
                answered; v3.1 conclusion stands.
  Branch B : Pole II p_LEE < 0.05 OR Pole III p_LEE < 0.05
             -> run the circularity diagnostic (script 13) before concluding.
  Branch C : II and III on opposite sides of 0.05 -> pole-by-pole, diagnostic on
             the surviving pole only.
This script REPORTS the branch; it does not itself run script 13.

Standard seed 20260517, M = 10000. Exploratory per pre-registration §12 point 3.

Inputs : data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
         results/02_observed_test_statistic.json
Outputs: results/12_hemisphere_preserving_null.json

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
SUMMARY_FILE = RESULTS_DIR / "12_hemisphere_preserving_null.json"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN_HEMISPHERE_THRESHOLD = 0.0

POLES = {"I": 90.0, "II": 76.0, "III": 72.2, "IV": 64.1, "V": 52.3}
WINDOW_HALF = 1.5
SCAN_CENTERS = np.arange(45.0, 89.0 + 1e-9, 0.25)

# Pre-committed hemisphere cuts (West is lon < cut).
CUTS = {"primary_-30 (Americas/OldWorld)": -30.0, "sensitivity_0 (prime meridian)": 0.0}

CLUSTER_THRESHOLD_KM = 25.0  # 12c, matching script 10's headline threshold
M_ITERATIONS = 10_000
RANDOM_SEED = 20260517
EARTH_RADIUS_KM = 6371.0088


# ---------------------------------------------------------------------------
# Hash / parsing / blocks (identical to prior scripts)
# ---------------------------------------------------------------------------


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


def assign_block_coarse(lat, lon):
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


def hemisphere_label(lon: float, cut: float) -> str:
    return "W" if lon < cut else "E"


# ---------------------------------------------------------------------------
# Window statistics
# ---------------------------------------------------------------------------


def t_max_window(sorted_lats: np.ndarray) -> int:
    """Maximum count in any ±1.5° window across the 45–89°N scan."""
    lo = np.searchsorted(sorted_lats, SCAN_CENTERS - WINDOW_HALF, side="left")
    hi = np.searchsorted(sorted_lats, SCAN_CENTERS + WINDOW_HALF, side="right")
    return int((hi - lo).max())


def pole_counts(lats: np.ndarray) -> dict:
    return {n: int(((lats >= L - WINDOW_HALF) & (lats <= L + WINDOW_HALF)).sum())
            for n, L in POLES.items()}


# ---------------------------------------------------------------------------
# Compatibility and swap chain (identical mechanism to scripts 06/10/11)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(lat, lon, bearings, target_lon_deg):
    N = len(lat)
    lat2 = np.broadcast_to(lat[:, None], (N, N))
    lon2 = np.broadcast_to(lon[:, None], (N, N))
    b2 = np.broadcast_to(bearings[None, :], (N, N))
    inter = compute_intersection_lat(lat2, lon2, b2, target_lon_deg)
    return (inter >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(inter)


def run_swap_chain(compatibility, M, sps, warmup, seed, block_of):
    """Metropolis swap chain. Swaps accepted only within the same group
    (block_of), and only when both reassigned bearings stay compatible."""
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]
    compatibility = compatibility.copy()
    np.fill_diagonal(compatibility, True)
    pi = np.arange(N)
    total = warmup + M * sps
    perms = np.empty((M, N), dtype=np.int32)
    done = 0
    chunk = 200_000
    accept = 0
    while done < total:
        c = min(chunk, total - done)
        ii = rng.integers(0, N, size=c)
        jj = rng.integers(0, N, size=c)
        for k in range(c):
            i = ii[k]; j = jj[k]
            if i != j and block_of[i] == block_of[j]:
                bi = pi[i]; bj = pi[j]
                if compatibility[i, bj] and compatibility[j, bi]:
                    pi[i] = bj; pi[j] = bi
                    accept += 1
            done += 1
            if done > warmup and (done - warmup) % sps == 0:
                s = (done - warmup) // sps - 1
                if 0 <= s < M:
                    perms[s] = pi
    return perms, accept / max(1, total)


def null_statistics(lat, lon, bearings, perms, obs_counts, chunk=500):
    """Per-null distributions: T_max per iteration, and per-pole counts."""
    M, N = perms.shape
    tmax = np.empty(M, dtype=int)
    pole_null = {n: np.empty(M, dtype=int) for n in POLES}
    for i0 in range(0, M, chunk):
        i1 = min(i0 + chunk, M)
        permuted = bearings[perms[i0:i1]]
        size = i1 - i0
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
        for r in range(size):
            lats = inter[r]
            lats = lats[(lats >= 0.0) & ~np.isnan(lats)]
            tmax[i0 + r] = t_max_window(np.sort(lats))
            for n, L in POLES.items():
                pole_null[n][i0 + r] = int(((lats >= L - WINDOW_HALF) & (lats <= L + WINDOW_HALF)).sum())
    out = {"tmax_mean": float(tmax.mean()), "tmax_p95": float(np.percentile(tmax, 95)),
           "per_pole": {}}
    for n in POLES:
        obs = obs_counts[n]
        p_pole = (1 + int((pole_null[n] >= obs).sum())) / (1 + M)   # uncorrected
        p_lee = (1 + int((tmax >= obs).sum())) / (1 + M)            # look-elsewhere
        out["per_pole"][n] = {"observed": obs,
                              "null_mean": float(pole_null[n].mean()),
                              "p_per_pole": p_pole,
                              "p_lee": p_lee}
    return out


# ---------------------------------------------------------------------------
# 25 km single-linkage clustering for 12c (matching script 10)
# ---------------------------------------------------------------------------


def haversine_km(lat1, lon1, lat2, lon2):
    p1 = np.radians(lat1); p2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1); dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def cluster_representatives(lat, lon, threshold_km=CLUSTER_THRESHOLD_KM):
    """Single-linkage components at threshold_km; representative = member
    nearest the component centroid. Returns representative row indices."""
    N = len(lat)
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(N):
        d = haversine_km(lat[i], lon[i], lat, lon)
        for j in np.where((d <= threshold_km))[0]:
            if j > i:
                union(i, int(j))
    comps = {}
    for i in range(N):
        comps.setdefault(find(i), []).append(i)
    reps = []
    for members in comps.values():
        m = np.array(members)
        clat = lat[m].mean(); clon = lon[m].mean()
        d = haversine_km(clat, clon, lat[m], lon[m])
        reps.append(int(m[int(np.argmin(d))]))
    return sorted(reps)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("\n" + "=" * 70)
    print("Hemisphere-preserving permutation null (script 12; addresses point 1)")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Status: EXPLORATORY (post-data) per pre-registration §12 point 3")
    print(f"Seed: {RANDOM_SEED}   M = {M_ITERATIONS}")
    print("Specification pre-committed in analysis_log.md (2026-06-08)")
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

    inter_obs = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    obs_counts = pole_counts(inter_obs[(inter_obs >= 0) & ~np.isnan(inter_obs)])
    obs_tmax = t_max_window(np.sort(inter_obs[(inter_obs >= 0) & ~np.isnan(inter_obs)]))
    print("Observed per-pole counts (±1.5°): "
          + ", ".join(f"{n}={obs_counts[n]}" for n in POLES) + f"   T_max={obs_tmax}")

    # ---- descriptive: hemisphere composition & Pole III contributors ----
    print("\n--- descriptive: hemisphere composition ---")
    descriptive = {}
    pole3_mask = (inter_obs >= POLES["III"] - WINDOW_HALF) & (inter_obs <= POLES["III"] + WINDOW_HALF)
    for cut_name, cut in CUTS.items():
        west = lon < cut
        n_w = int(west.sum()); n_e = int((~west).sum())
        p3_w = int((pole3_mask & west).sum()); p3_e = int((pole3_mask & ~west).sum())
        descriptive[cut_name] = {"n_west": n_w, "n_east": n_e,
                                 "pole3_contrib_west": p3_w, "pole3_contrib_east": p3_e}
        print(f"  cut {cut_name}: West {n_w} / East {n_e}; "
              f"Pole III contributors  West {p3_w} / East {p3_e}")

    # ---- cluster representatives for 12c (cut-independent collapse) ----
    print(f"\nBuilding 25 km cluster representatives for 12c...")
    t = time.time()
    reps = cluster_representatives(lat, lon)
    rlat, rlon, rbear = lat[reps], lon[reps], bearings[reps]
    inter_rep = compute_intersection_lat(rlat, rlon, rbear, TARGET_LON_DEG)
    obs_counts_rep = pole_counts(inter_rep[(inter_rep >= 0) & ~np.isnan(inter_rep)])
    print(f"  {len(reps)} representatives ({time.time()-t:.1f}s); "
          + "cluster per-pole: " + ", ".join(f"{n}={obs_counts_rep[n]}" for n in POLES))

    blocks = np.array([assign_block_coarse(lat[i], lon[i]) for i in range(N)])

    print("\nBuilding compatibility matrices...")
    comp_site = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    comp_rep = build_compatibility_matrix(rlat, rlon, rbear, TARGET_LON_DEG)
    sps_site, warm_site = 2 * N, 5 * N
    sps_rep, warm_rep = 2 * len(reps), 5 * len(reps)

    results = {}
    for cut_name, cut in CUTS.items():
        print(f"\n{'='*70}\nCUT: {cut_name}\n{'='*70}")
        hemi_site = np.array([hemisphere_label(lon[i], cut) for i in range(N)])
        hemi_block = np.array([f"{blocks[i]}|{hemi_site[i]}" for i in range(N)])
        hemi_rep = np.array([hemisphere_label(rlon[i], cut) for i in range(len(reps))])

        # group-id arrays for the swap chain
        def to_ids(labels):
            u = {v: k for k, v in enumerate(sorted(set(labels.tolist())))}
            return np.array([u[v] for v in labels])

        cut_block = {}

        print("  [12a] conditional, hemisphere-preserving...")
        perms_a, acc_a = run_swap_chain(comp_site, M_ITERATIONS, sps_site, warm_site,
                                        RANDOM_SEED, to_ids(hemi_site))
        cut_block["12a_conditional"] = null_statistics(lat, lon, bearings, perms_a, obs_counts)
        cut_block["12a_conditional"]["acceptance"] = round(acc_a, 4)

        print("  [12b] block-conditional, hemisphere-preserving...")
        perms_b, acc_b = run_swap_chain(comp_site, M_ITERATIONS, sps_site, warm_site,
                                        RANDOM_SEED, to_ids(hemi_block))
        cut_block["12b_block_conditional"] = null_statistics(lat, lon, bearings, perms_b, obs_counts)
        cut_block["12b_block_conditional"]["acceptance"] = round(acc_b, 4)

        print("  [12c] spatial-cluster, hemisphere-preserving...")
        perms_c, acc_c = run_swap_chain(comp_rep, M_ITERATIONS, sps_rep, warm_rep,
                                        RANDOM_SEED, to_ids(hemi_rep))
        cut_block["12c_spatial_cluster"] = null_statistics(rlat, rlon, rbear, perms_c, obs_counts_rep)
        cut_block["12c_spatial_cluster"]["acceptance"] = round(acc_c, 4)

        results[cut_name] = cut_block

        for tag, blk in cut_block.items():
            ii = blk["per_pole"]["II"]; iii = blk["per_pole"]["III"]
            print(f"    {tag:24s} null T_max {blk['tmax_mean']:6.1f}  "
                  f"II p_LEE={ii['p_lee']:.4f}  III p_LEE={iii['p_lee']:.4f}  "
                  f"(per-pole II={ii['p_per_pole']:.4f} III={iii['p_per_pole']:.4f})")

    # ---- branch determination: 12a, PRIMARY cut, look-elsewhere ----
    primary_name = [k for k in CUTS if k.startswith("primary")][0]
    a = results[primary_name]["12a_conditional"]["per_pole"]
    pII, pIII = a["II"]["p_lee"], a["III"]["p_lee"]
    if pII >= 0.05 and pIII >= 0.05:
        branch = "A"
    elif (pII < 0.05) != (pIII < 0.05):
        branch = "C"
    else:
        branch = "B"
    print("\n" + "=" * 70)
    print("DECISION (12a, primary cut, look-elsewhere corrected)")
    print("=" * 70)
    print(f"  Pole II p_LEE  = {pII:.4f}")
    print(f"  Pole III p_LEE = {pIII:.4f}")
    print(f"  => BRANCH {branch}")
    if branch == "A":
        print("  Peaks dissolve under the hemisphere-preserving null. Point 1 answered;")
        print("  v3.1 conclusion stands. (Script 13 not required.)")
    elif branch == "B":
        print("  Peaks survive. Run script 13 (circularity diagnostic) before concluding;")
        print("  B1 if asymmetry is geometrically entailed, B2 if it has independent structure.")
    else:
        print("  Mixed (II and III differ). Run script 13 for the surviving pole only.")
    print()

    output = {
        "script": "12_hemisphere_preserving_null.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "status": "exploratory_post_publication",
        "precommitment": "analysis_log.md entry 2026-06-08",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "n_in_range": N,
        "n_cluster_representatives_25km": len(reps),
        "observed_pole_counts": obs_counts,
        "observed_pole_counts_cluster": obs_counts_rep,
        "observed_tmax": obs_tmax,
        "descriptive": descriptive,
        "cuts": CUTS,
        "results": results,
        "branch_primary_12a_lee": {"pole_II_p_lee": pII, "pole_III_p_lee": pIII, "branch": branch},
    }
    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}\n")


if __name__ == "__main__":
    main()
