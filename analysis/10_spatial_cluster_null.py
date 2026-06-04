"""
10_spatial_cluster_null.py
==========================

Post-publication extension. The decisive control for pseudoreplication, and
the last gate before v3.

Why
---
The diagnostic for script 09 showed that 64 of Pole III's 119 contributors
(54%) lie in a single un-subdivided block, Am:Mesoamerica (371 sites). The
block-conditional nulls of 06/08/09 treat those 371 as exchangeable. But the
Mesoamerican orientation tradition is the most heavily documented case of
shared, systematic building orientation in the archaeological record (Aveni;
Šprajc): hundreds of structures built to a handful of recurring azimuth
"families." Treating them as independent draws is exactly pseudoreplication,
and it is the obvious candidate for the ~1% Pole III residual that survived
09 (p_III ≈ 0.011 under fine blocking) while the assumption-free GLOBAL
conditional null saw nothing (07: p_III ≈ 0.90).

This script removes the assumption directly. Instead of treating each of the
994 sites as an independent observation, it collapses spatially clustered
sites — which plausibly share a single orientation convention — into one
exchangeable unit each, and asks whether the number of independent CLUSTERS
pointing near a pole is surprising.

Method
------
1. Cluster sites by single-linkage on great-circle distance: any two sites
   within `threshold_km` are joined; clusters are the connected components.
   The distance threshold is swept ({25, 50, 75, 100} km) so it is not a
   hidden researcher degree of freedom.

2. Collapse each cluster to ONE representative = the member nearest the
   cluster centroid, using that member's RAW (lat, lon, bearing). No angular
   averaging; every representative is a real measured triple. Effective N is
   the number of clusters.

3. On the representatives, run the assumption-light GLOBAL conditional null
   (hemisphere-preserving swap chain; same construction as 03b/07, one block),
   M = 10,000.

4. Report, per threshold, both
     - the per-pole p (count of representatives within ±1.5° of Pole II / III), and
     - the latitude-look-elsewhere-corrected p (observed pole count vs the null
       distribution of the maximum ±1.5° window count anywhere in the scan).

Interpretation
--------------
This is a different statistic from 05–09 (clusters, not sites), and that is
the point: it answers "how many INDEPENDENT spatial units point near 72°N,
more than chance?" — the question pseudoreplication raised.

  - p_III erodes through 0.05 (and stays there across thresholds):
        the Pole III residual was Mesoamerican (and other) within-tradition
        replication. Both poles dissolve. v3 retracts cleanly.
  - p_III holds below ~0.05 even at cluster level across thresholds:
        a genuine weak residual survives the strongest available
        independence control. Still not evidence for a moved pole (the
        geophysical claim fails on independent grounds), but an honest
        anomaly worth reporting as such.

Status: post-publication extension, EXPLORATORY per pre-registration §12
point 3.

Inputs
------
- data/Database_Mario_Buildreps_V14.xlsx (hash-verified)
- results/02_observed_test_statistic.json (for the in-range N)

Outputs
-------
- results/10_spatial_cluster_null.json
- results/10_cluster_labels.csv             (per-site cluster id at each threshold)
- results/10_null_maxcount_<thr>km.npy      (M, 2): [pole-count cols not stored; max only]

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
SUMMARY_FILE = RESULTS_DIR / "10_spatial_cluster_null.json"
LABELS_FILE = RESULTS_DIR / "10_cluster_labels.csv"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN_HEMISPHERE_THRESHOLD = 0.0
TOLERANCE_DEG = 1.5

POLES_PRIMARY = {"I (current)": 90.0, "II": 76.0, "III": 72.2, "IV": 64.1, "V": 52.3}
POLE_II_LAT = 76.0
POLE_III_LAT = 72.2

THRESHOLDS_KM = [25.0, 50.0, 75.0, 100.0]
PRIMARY_THRESHOLD_KM = 75.0
EARTH_RADIUS_KM = 6371.0

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
# Spatial clustering (single-linkage connected components)
# ---------------------------------------------------------------------------


def haversine_matrix(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Pairwise great-circle distance (km), shape (N, N)."""
    phi = np.deg2rad(lat)
    lam = np.deg2rad(lon)
    dphi = phi[:, None] - phi[None, :]
    dlam = lam[:, None] - lam[None, :]
    a = np.sin(dphi / 2) ** 2 + np.cos(phi)[:, None] * np.cos(phi)[None, :] * np.sin(dlam / 2) ** 2
    a = np.clip(a, 0.0, 1.0)
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def connected_components(adjacency: np.ndarray) -> np.ndarray:
    """Union-find connected components from a boolean adjacency matrix.
    Returns an integer label per node (0..n_components-1, in first-seen order).
    """
    N = adjacency.shape[0]
    parent = np.arange(N)

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:  # path compression
            parent[x], x = root, parent[x]
        return root

    ii, jj = np.where(np.triu(adjacency, k=1))
    for i, j in zip(ii.tolist(), jj.tolist()):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)

    roots = np.array([find(i) for i in range(N)])
    # Relabel to 0..C-1 in first-seen order
    _, labels = np.unique(roots, return_inverse=True)
    return labels


def collapse_to_representatives(lat, lon, bearings, labels):
    """For each cluster, pick the member nearest the cluster centroid and
    return its raw (lat, lon, bearing). Returns arrays of length n_clusters
    plus the cluster sizes."""
    C = labels.max() + 1
    rep_lat = np.empty(C)
    rep_lon = np.empty(C)
    rep_bea = np.empty(C)
    sizes = np.empty(C, dtype=int)
    for c in range(C):
        idx = np.where(labels == c)[0]
        sizes[c] = len(idx)
        if len(idx) == 1:
            j = idx[0]
        else:
            clat = lat[idx].mean()
            clon = lon[idx].mean()
            # nearest member to centroid (planar is fine within a cluster)
            d = (lat[idx] - clat) ** 2 + (lon[idx] - clon) ** 2
            j = idx[int(np.argmin(d))]
        rep_lat[c] = lat[j]
        rep_lon[c] = lon[j]
        rep_bea[c] = bearings[j]
    return rep_lat, rep_lon, rep_bea, sizes


# ---------------------------------------------------------------------------
# Statistic + null (global conditional, on representatives)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(lat, lon, bearings, target_lon_deg):
    N = len(lat)
    lat_2d = np.broadcast_to(lat[:, None], (N, N))
    lon_2d = np.broadcast_to(lon[:, None], (N, N))
    bearings_2d = np.broadcast_to(bearings[None, :], (N, N))
    intersections = compute_intersection_lat(lat_2d, lon_2d, bearings_2d, target_lon_deg)
    return (intersections >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(intersections)


def run_conditional_swap_chain(compatibility, M, swaps_per_sample, warmup_swaps, seed):
    """Global within-hemisphere swap chain (one block). Same target as 03b/07."""
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]
    compatibility = compatibility.copy()
    np.fill_diagonal(compatibility, True)
    pi = np.arange(N)
    total = warmup_swaps + M * swaps_per_sample
    permutations = np.empty((M, N), dtype=np.int32)
    n_acc = n_att = 0
    done = 0
    proposal_chunk = 200_000
    while done < total:
        c = min(proposal_chunk, total - done)
        ii = rng.integers(0, N, size=c)
        jj = rng.integers(0, N, size=c)
        for k in range(c):
            i = ii[k]; j = jj[k]
            if i != j:
                bi = pi[i]; bj = pi[j]
                if compatibility[i, bj] and compatibility[j, bi]:
                    pi[i] = bj; pi[j] = bi; n_acc += 1
            n_att += 1; done += 1
            if done > warmup_swaps:
                aw = done - warmup_swaps
                if aw % swaps_per_sample == 0:
                    si = aw // swaps_per_sample - 1
                    if 0 <= si < M:
                        permutations[si] = pi
    return permutations, n_acc / max(n_att, 1)


def window_counts(inter, centres, tol):
    within = np.abs(inter[:, :, None] - centres[None, None, :]) <= tol
    return within.sum(axis=1).astype(np.int32)


def per_pole_counts(inter, pole_lats, tol):
    if inter.ndim == 1:
        inter = inter[None, :]
        sq = True
    else:
        sq = False
    within = np.abs(inter[..., None] - pole_lats[None, None, :]) <= tol
    counts = within.sum(axis=1).astype(int)
    return counts[0] if sq else counts


def lee_p(col, observed_value, M):
    return (1 + int((col >= observed_value).sum())) / (1 + M)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 68)
    print("Spatial-cluster null (pseudoreplication control; v3 gate)")
    print("Script: 10_spatial_cluster_null.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print("Status: EXPLORATORY (post-data) per pre-registration §12 point 3")
    print(f"Random seed: {RANDOM_SEED}   M = {M_ITERATIONS}   tol = ±{TOLERANCE_DEG}°")
    print("=" * 68)
    print()

    verified_hash = verify_hash()
    print(f"Geometry self-test: {run_self_tests()} cases passed.")
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
    print(f"N in-range sites: {N}")

    pole_names = list(POLES_PRIMARY.keys())
    pole_lats = np.array(list(POLES_PRIMARY.values()))
    K = len(pole_lats)
    centres = np.arange(SCAN_LAT_MIN, SCAN_WIDE_MAX + 1e-9, SCAN_STEP_DEG)
    primary_mask = centres <= SCAN_PRIMARY_MAX + 1e-9

    # Site-level distance matrix once.
    print("Computing pairwise great-circle distances...")
    D = haversine_matrix(lat, lon)
    print()

    labels_table = {"SITE_LAT": lat, "SITE_LON": lon, "BEARING": bearings}
    output = {
        "script": "10_spatial_cluster_null.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "status": "exploratory_post_publication",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "tolerance_deg": TOLERANCE_DEG,
        "n_in_range_sites": N,
        "primary_threshold_km": PRIMARY_THRESHOLD_KM,
        "thresholds": {},
    }

    for thr in THRESHOLDS_KM:
        print("=" * 68)
        print(f"Threshold: {thr:.0f} km")
        print("=" * 68)
        adjacency = (D <= thr)
        labels = connected_components(adjacency)
        labels_table[f"cluster_{int(thr)}km"] = labels
        C = labels.max() + 1

        rep_lat, rep_lon, rep_bea, sizes = collapse_to_representatives(
            lat, lon, bearings, labels
        )
        print(f"  {C} clusters from {N} sites  "
              f"(largest {sizes.max()}, singletons {(sizes==1).sum()}, "
              f"mean size {sizes.mean():.2f})")

        # Observed representative intersections + per-pole counts
        rep_inter = compute_intersection_lat(rep_lat, rep_lon, rep_bea, TARGET_LON_DEG)
        rep_inter = np.where(np.isnan(rep_inter), 0.0, rep_inter)
        obs_pp = per_pole_counts(rep_inter, pole_lats, TOLERANCE_DEG)
        counts_obs = window_counts(rep_inter[None, :], centres, TOLERANCE_DEG)[0]
        obs_tmax = int(counts_obs[primary_mask].max())
        obs_II = int((np.abs(rep_inter - POLE_II_LAT) <= TOLERANCE_DEG).sum())
        obs_III = int((np.abs(rep_inter - POLE_III_LAT) <= TOLERANCE_DEG).sum())

        # Null: global conditional on representatives
        compat = build_compatibility_matrix(rep_lat, rep_lon, rep_bea, TARGET_LON_DEG)
        sps = 2 * C
        warm = 5 * C
        perms, acc = run_conditional_swap_chain(compat, M_ITERATIONS, sps, warm, RANDOM_SEED)

        # Null statistics (chunked)
        null_pp = np.empty((M_ITERATIONS, K), dtype=int)
        null_tmax = np.empty(M_ITERATIONS, dtype=np.int32)
        chunk = 500
        for i0 in range(0, M_ITERATIONS, chunk):
            i1 = min(i0 + chunk, M_ITERATIONS)
            permuted = rep_bea[perms[i0:i1]]
            size = i1 - i0
            lat_bc = np.broadcast_to(rep_lat, (size, C))
            lon_bc = np.broadcast_to(rep_lon, (size, C))
            inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
            inter = np.where(np.isnan(inter), 0.0, inter)
            null_pp[i0:i1] = per_pole_counts(inter, pole_lats, TOLERANCE_DEG)
            wc = window_counts(inter, centres, TOLERANCE_DEG)
            null_tmax[i0:i1] = wc[:, primary_mask].max(axis=1)
        np.save(RESULTS_DIR / f"10_null_maxcount_{int(thr)}km.npy", null_tmax)

        # p-values
        p_pole = {nm: (1 + int((null_pp[:, k] >= obs_pp[k]).sum())) / (1 + M_ITERATIONS)
                  for k, nm in enumerate(pole_names)}
        p_II_lee = lee_p(null_tmax, obs_II, M_ITERATIONS)
        p_III_lee = lee_p(null_tmax, obs_III, M_ITERATIONS)

        print(f"  acceptance {acc:.3f}   null T_max mean {null_tmax.mean():.2f}")
        print(f"  observed cluster counts:  "
              + "  ".join(f"{nm.split()[0]}={obs_pp[k]}" for k, nm in enumerate(pole_names)))
        print(f"  per-pole p:   II={p_pole['II']:.4f}  III={p_pole['III']:.4f}")
        print(f"  +LEE p:       II={p_II_lee:.4f}  III={p_III_lee:.4f}")
        print()

        output["thresholds"][f"{int(thr)}km"] = {
            "n_clusters": int(C),
            "largest_cluster": int(sizes.max()),
            "n_singletons": int((sizes == 1).sum()),
            "acceptance_rate": float(acc),
            "null_Tmax_mean": float(null_tmax.mean()),
            "observed_per_pole": {nm: int(obs_pp[k]) for k, nm in enumerate(pole_names)},
            "obs_II": obs_II, "obs_III": obs_III,
            "per_pole_p": p_pole,
            "p_II_lee": p_II_lee,
            "p_III_lee": p_III_lee,
        }

    # Gate table
    print("=" * 68)
    print("GATE: Pole III at cluster level across distance thresholds")
    print("=" * 68)
    print(f"  {'threshold':>10s}  {'clusters':>8s}  {'largest':>7s}  "
          f"{'III p-pole':>10s}  {'III +LEE':>9s}")
    for thr in THRESHOLDS_KM:
        s = output["thresholds"][f"{int(thr)}km"]
        print(f"  {int(thr):8d}km  {s['n_clusters']:8d}  {s['largest_cluster']:7d}  "
              f"{s['per_pole_p']['III']:10.4f}  {s['p_III_lee']:9.4f}")
    print()
    print("  Pole III +LEE crossing >0.05 and staying there  -> both poles dissolve;")
    print("    the residual was within-tradition replication (Mesoamerica etc.).")
    print("  Pole III +LEE holding <0.05 across thresholds    -> genuine weak residual")
    print("    surviving the strongest independence control (still not a moved pole).")
    print()

    pd.DataFrame(labels_table).to_csv(LABELS_FILE, index=False)
    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print(f"Per-site cluster labels: {LABELS_FILE.relative_to(REPO_ROOT)}")
    print()


if __name__ == "__main__":
    main()
