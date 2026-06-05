"""
11_data_owner_rule_simulation.py
================================

Post-publication extension, addressing the data owner's point 2 (5 June 2026
follow-up; Appendix D): that the latitude look-elsewhere control (script 07)
modelled a worst-case continuous window search rather than his actual,
rule-based peak-finding procedure. This script implements his procedure as he
stated it (email of 17 May 2026, received before the database was opened) and
tests it directly.

His rules, operationalised
--------------------------
The procedure identifies a "pole" from the per-degree histogram of intersection
latitudes on the 47°W meridian:
  - bin in-range intersection latitudes into 1° bins over [0, 90);
  - a candidate pole is a maximal run of CONSECUTIVE 1° bins each holding
    >= THRESHOLD structures (rule 4: 11.03/deg is chance, >=12 is "above
    average"); the run ends at the first bin below THRESHOLD (rule 9);
  - the run must span >= 3 degrees and total >= 36 structures (rules 8-10, 12).
Primary THRESHOLD = 12. A sensitivity variant applies THRESHOLD = 15 for bins
at >= 80°N (rule 11: "preferably 15 or more ... closer to the current pole").

What is and is not being tested
-------------------------------
His pole-IDENTIFICATION rule is implemented verbatim. What this script replaces
is his SIGNIFICANCE model. His published probabilities come from a binomial
test against a UNIFORM distribution of structures over 90° (rule 3: 993/90 =
11.03 per degree). That uniform baseline is the claim under test. The script
scores his rule against three null models:

  A. uniform        - structures distributed uniformly over the 90 degree-bins
                      (multinomial, p = 1/90). This is the Monte-Carlo
                      equivalent of his own binomial baseline.
  B. conditional    - hemisphere-preserving permutation of folded bearings
                      (global swap chain; as in 03b / 07 / 10).
  C. block-conditional - within-block hemisphere-preserving permutation
                      (as in 06 / 08).

Nulls B and C reproduce the real distribution of intersection latitudes — the
hemisphere selection and the great-circle "attractor" band — that uniform
sampling does not. (His rule 2, that the 166 out-of-range structures count in
the binomial denominator, pertains to his analytic p-value, not to the
per-degree histogram; it does not enter the Monte-Carlo nulls, which use the
empirical null distribution of his rule's output directly.)

For each null the script records, over M iterations:
  - the distribution of the NUMBER of poles his rule identifies anywhere;
  - for each of his five claimed pole latitudes, how often his rule places a
    qualifying pole over that 1° band.

Reading
-------
  - If his rule fires far more often on the observed data than under a null,
    his poles are surprising relative to that null.
  - The expected contrast: observed poles are highly significant against the
    UNIFORM null (reproducing his ~100% / 99.999% claims) but NOT against the
    conditional / block-conditional nulls, under which the high-north degree
    bins routinely exceed 12 by geometry alone. That would show his
    pole-finding rule is faithful but his uniform significance baseline is the
    source of the inflated confidence — the disagreement is the null model, not
    the rule.

Status: post-publication extension, EXPLORATORY per pre-registration §12
point 3.

Inputs : data/Database_Mario_Buildreps_V14.xlsx (hash-verified);
         results/02_observed_test_statistic.json
Outputs: results/11_data_owner_rule_simulation.json
         results/11_npoles_<null>.npy  (M,) per null

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
SUMMARY_FILE = RESULTS_DIR / "11_data_owner_rule_simulation.json"

PRIMARY_SHEET = "All Data"
TARGET_LON_DEG = -47.1
NORTHERN_HEMISPHERE_THRESHOLD = 0.0

# His pole-finding rule parameters.
DEGREE_BINS = 90                  # [0, 90)
THRESHOLD = 12                    # rule 4
MIN_RUN_DEGREES = 3               # rules 8, 9, 12
MIN_TOTAL = 36                    # rules 8-10
NEARPOLE_LAT = 80.0               # rule 11: stricter threshold near current pole
NEARPOLE_THRESHOLD = 15           # rule 11

# His five claimed poles (bin index = floor(latitude)).
CLAIMED_POLES = {"I (90.0)": 90.0, "II (76.0)": 76.0, "III (72.2)": 72.2,
                 "IV (64.1)": 64.1, "V (52.3)": 52.3}

M_ITERATIONS = 10_000
RANDOM_SEED = 20260517


# ---------------------------------------------------------------------------
# Hash verification (identical to other scripts)
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


# ---------------------------------------------------------------------------
# His pole-finding rule
# ---------------------------------------------------------------------------


def per_degree_histogram(intersection_lats: np.ndarray) -> np.ndarray:
    """Counts of northern intersection latitudes in 1° bins over [0, 90)."""
    lat = intersection_lats[(intersection_lats >= 0.0) & (intersection_lats < 90.0 + 1e-9)]
    idx = np.clip(np.floor(lat).astype(int), 0, DEGREE_BINS - 1)
    return np.bincount(idx, minlength=DEGREE_BINS)


def find_poles(counts: np.ndarray,
               threshold: int = THRESHOLD,
               nearpole_lat: float | None = None,
               nearpole_threshold: int = NEARPOLE_THRESHOLD):
    """Apply the data owner's rule. Returns list of (start_deg, end_deg, total)."""
    thr = np.full(DEGREE_BINS, threshold, dtype=int)
    if nearpole_lat is not None:
        thr[int(nearpole_lat):] = nearpole_threshold
    poles = []
    i = 0
    n = len(counts)
    while i < n:
        if counts[i] >= thr[i]:
            j = i
            while j < n and counts[j] >= thr[j]:
                j += 1
            run_len = j - i
            run_total = int(counts[i:j].sum())
            if run_len >= MIN_RUN_DEGREES and run_total >= MIN_TOTAL:
                poles.append((i, j, run_total))
            i = j
        else:
            i += 1
    return poles


def poles_cover(poles, bin_index: int) -> bool:
    return any(start <= bin_index < end for start, end, _ in poles)


# ---------------------------------------------------------------------------
# His binomial, re-run under the realistic per-degree expectation (point 2, 11b)
# ---------------------------------------------------------------------------
#
# His published confidence is a per-degree binomial upper tail, P(X >= x | N, p),
# with p = 1/90 (uniform over 90°, rule 3). The realistic per-degree probability
# is not 1/90: the great-circle geometry concentrates intersections in a high-
# north band. Re-running his exact binomial with p set to the conditional-null
# expected fraction per degree shows what his test reports once the baseline
# matches the data's actual distribution.

import math  # noqa: E402


def _lgam_table(n):
    return np.array([math.lgamma(i + 1) for i in range(n + 1)])  # log(i!)


def binom_sf_upper(obs: int, N: int, p: float, lgam: np.ndarray) -> float:
    """Exact upper tail P(X >= obs) for Binomial(N, p), in log space."""
    if obs <= 0:
        return 1.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    ks = np.arange(obs, N + 1)
    log_c = lgam[N] - lgam[ks] - lgam[N - ks]
    log_pmf = log_c + ks * math.log(p) + (N - ks) * math.log1p(-p)
    mx = log_pmf.max()
    return float(np.exp(mx) * np.exp(log_pmf - mx).sum())


def mean_per_degree_histogram(lat, lon, bearings, perms, chunk=500):
    """Mean per-degree histogram across a set of null permutations."""
    M, N = perms.shape
    acc = np.zeros(DEGREE_BINS)
    for i0 in range(0, M, chunk):
        i1 = min(i0 + chunk, M)
        permuted = bearings[perms[i0:i1]]
        size = i1 - i0
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
        for r in range(size):
            acc += per_degree_histogram(inter[r])
    return acc / M


# ---------------------------------------------------------------------------
# Null permutation streams (reused constructions)
# ---------------------------------------------------------------------------


def build_compatibility_matrix(lat, lon, bearings, target_lon_deg):
    N = len(lat)
    lat2 = np.broadcast_to(lat[:, None], (N, N))
    lon2 = np.broadcast_to(lon[:, None], (N, N))
    b2 = np.broadcast_to(bearings[None, :], (N, N))
    inter = compute_intersection_lat(lat2, lon2, b2, target_lon_deg)
    return (inter >= NORTHERN_HEMISPHERE_THRESHOLD) & ~np.isnan(inter)


def run_swap_chain(compatibility, M, sps, warmup, seed, block_of=None):
    rng = np.random.default_rng(seed)
    N = compatibility.shape[0]
    compatibility = compatibility.copy()
    np.fill_diagonal(compatibility, True)
    pi = np.arange(N)
    total = warmup + M * sps
    perms = np.empty((M, N), dtype=np.int32)
    done = 0
    chunk = 200_000
    while done < total:
        c = min(chunk, total - done)
        ii = rng.integers(0, N, size=c)
        jj = rng.integers(0, N, size=c)
        for k in range(c):
            i = ii[k]; j = jj[k]
            ok = (i != j) and (block_of is None or block_of[i] == block_of[j])
            if ok:
                bi = pi[i]; bj = pi[j]
                if compatibility[i, bj] and compatibility[j, bi]:
                    pi[i] = bj; pi[j] = bi
            done += 1
            if done > warmup and (done - warmup) % sps == 0:
                s = (done - warmup) // sps - 1
                if 0 <= s < M:
                    perms[s] = pi
    return perms


# ---------------------------------------------------------------------------
# Null runners — return (npoles array, per-claimed-pole hit counts)
# ---------------------------------------------------------------------------


def score_histogram(counts, claimed_bins, near_variant):
    poles = find_poles(counts, nearpole_lat=NEARPOLE_LAT if near_variant else None)
    n = len(poles)
    hits = {name: poles_cover(poles, b) for name, b in claimed_bins.items()}
    return n, hits


def run_uniform_null(N, claimed_bins, M, seed, near_variant):
    rng = np.random.default_rng(seed)
    npoles = np.empty(M, dtype=int)
    hits = {name: 0 for name in claimed_bins}
    p = np.full(DEGREE_BINS, 1.0 / DEGREE_BINS)
    for it in range(M):
        counts = rng.multinomial(N, p)
        n, h = score_histogram(counts, claimed_bins, near_variant)
        npoles[it] = n
        for name in claimed_bins:
            hits[name] += int(h[name])
    return npoles, hits


def run_permutation_null(lat, lon, bearings, perms, claimed_bins, near_variant,
                         chunk=500):
    M, N = perms.shape
    npoles = np.empty(M, dtype=int)
    hits = {name: 0 for name in claimed_bins}
    for i0 in range(0, M, chunk):
        i1 = min(i0 + chunk, M)
        permuted = bearings[perms[i0:i1]]
        size = i1 - i0
        lat_bc = np.broadcast_to(lat, (size, N))
        lon_bc = np.broadcast_to(lon, (size, N))
        inter = compute_intersection_lat(lat_bc, lon_bc, permuted, TARGET_LON_DEG)
        for r in range(size):
            counts = per_degree_histogram(inter[r])
            n, h = score_histogram(counts, claimed_bins, near_variant)
            npoles[i0 + r] = n
            for name in claimed_bins:
                hits[name] += int(h[name])
    return npoles, hits


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("\n" + "=" * 70)
    print("Data-owner rule simulation (script 11; addresses point 2)")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Status: EXPLORATORY (post-data) per pre-registration §12 point 3")
    print(f"Seed: {RANDOM_SEED}   M = {M_ITERATIONS}")
    print(f"Rule: >= {THRESHOLD}/deg, >= {MIN_RUN_DEGREES} deg, total >= {MIN_TOTAL}")
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

    claimed_bins = {name: int(np.floor(min(L, 89.0))) for name, L in CLAIMED_POLES.items()}

    # ---- observed ----
    inter_obs = compute_intersection_lat(lat, lon, bearings, TARGET_LON_DEG)
    counts_obs = per_degree_histogram(inter_obs)
    poles_obs = find_poles(counts_obs)
    print(f"\nObserved per-degree histogram: max {counts_obs.max()}/deg at "
          f"{int(np.argmax(counts_obs))}°N; mean {counts_obs.mean():.2f}/deg")
    print(f"Observed poles found by the rule ({len(poles_obs)}):")
    for s, e, t in poles_obs:
        print(f"    {s}–{e}°N  (span {e-s}°, total {t})")
    obs_npoles = len(poles_obs)
    obs_hits = {name: poles_cover(poles_obs, b) for name, b in claimed_bins.items()}
    print("  Claimed-pole coverage (observed): "
          + ", ".join(f"{name.split()[0]}={'Y' if obs_hits[name] else 'n'}"
                      for name in claimed_bins))

    # ---- nulls ----
    print("\nBuilding compatibility matrix...")
    t = time.time()
    compatibility = build_compatibility_matrix(lat, lon, bearings, TARGET_LON_DEG)
    print(f"  built in {time.time()-t:.1f}s")
    blocks = np.array([assign_block_coarse(lat[i], lon[i]) for i in range(N)])
    labels = sorted(set(blocks.tolist()))
    block_of = np.array([labels.index(b) for b in blocks])
    sps, warm = 2 * N, 5 * N

    # Swap chains do not depend on the threshold variant; build them once.
    print("  building conditional null (global swap chain)...")
    perms_b = run_swap_chain(compatibility, M_ITERATIONS, sps, warm, RANDOM_SEED)
    print("  building block-conditional null (within-block swap chain)...")
    perms_c = run_swap_chain(compatibility, M_ITERATIONS, sps, warm, RANDOM_SEED, block_of=block_of)

    results = {}
    npoles_store = {}
    for near_variant in (False, True):
        tag = "nearpole15" if near_variant else "flat12"
        print(f"\n--- threshold variant: {tag} ---")

        print("  [A] uniform null...")
        nu, hu = run_uniform_null(N, claimed_bins, M_ITERATIONS, RANDOM_SEED, near_variant)

        print("  [B] conditional null...")
        nb, hb = run_permutation_null(lat, lon, bearings, perms_b, claimed_bins, near_variant)

        print("  [C] block-conditional null...")
        nc, hc = run_permutation_null(lat, lon, bearings, perms_c, claimed_bins, near_variant)

        obs_n = len(find_poles(counts_obs, nearpole_lat=NEARPOLE_LAT if near_variant else None))
        obs_h = {name: poles_cover(find_poles(counts_obs, nearpole_lat=NEARPOLE_LAT if near_variant else None), b)
                 for name, b in claimed_bins.items()}

        block = {}
        for nm, arr, hitc in (("uniform", nu, hu), ("conditional", nb, hb), ("block_conditional", nc, hc)):
            p_npoles = (1 + int((arr >= obs_n).sum())) / (1 + M_ITERATIONS)
            per_pole = {}
            for name in claimed_bins:
                null_rate = hitc[name] / M_ITERATIONS
                per_pole[name] = {
                    "observed_detected": bool(obs_h[name]),
                    "null_detection_rate": null_rate,
                    "p": (1 + hitc[name]) / (1 + M_ITERATIONS) if obs_h[name] else None,
                }
            block[nm] = {
                "null_npoles_mean": float(arr.mean()),
                "null_npoles_p95": float(np.percentile(arr, 95)),
                "observed_npoles": obs_n,
                "p_npoles": p_npoles,
                "per_claimed_pole": per_pole,
            }
            npoles_store[f"{tag}_{nm}"] = arr
            print(f"    {nm:18s} null poles mean {arr.mean():5.2f} (p95 {np.percentile(arr,95):.0f})  "
                  f"obs {obs_n}  p(npoles)={p_npoles:.4f}")
        results[tag] = block

    for k, arr in npoles_store.items():
        np.save(RESULTS_DIR / f"11_npoles_{k}.npy", arr)

    # ---- gate table (primary variant) ----
    print("\n" + "=" * 70)
    print("GATE (flat-12 rule): does his procedure find his poles beyond chance?")
    print("=" * 70)
    prim = results["flat12"]
    print(f"  {'null':18s}  {'obs npoles':>10s}  {'null mean':>9s}  {'p(npoles)':>9s}  "
          f"{'III rate':>8s}")
    for nm in ("uniform", "conditional", "block_conditional"):
        b = prim[nm]
        iii = b["per_claimed_pole"]["III (72.2)"]["null_detection_rate"]
        print(f"  {nm:18s}  {b['observed_npoles']:10d}  {b['null_npoles_mean']:9.2f}  "
              f"{b['p_npoles']:9.4f}  {iii:8.3f}")
    print()
    print("  Expected reading: significant vs the UNIFORM null (his binomial")
    print("  baseline), not significant vs the conditional / block-conditional")
    print("  nulls. If so, his pole-finding rule is faithful but the uniform")
    print("  baseline is the source of the inflated confidence — the dispute is")
    print("  the null model, not the rule.")
    print()

    # ---- 11b: his binomial under uniform vs realistic per-degree expectation ----
    print("=" * 70)
    print("11b: his per-degree binomial, uniform baseline vs realistic geometry")
    print("=" * 70)
    lgam = _lgam_table(N)
    exp_cond = mean_per_degree_histogram(lat, lon, bearings, perms_b)
    exp_block = mean_per_degree_histogram(lat, lon, bearings, perms_c)
    p_uniform_deg = 1.0 / DEGREE_BINS

    print(f"  {'pole/bin':12s} {'obs':>4s} | {'unif exp':>8s} {'p(unif)':>10s} "
          f"| {'cond exp':>8s} {'p(cond)':>9s} | {'blk exp':>8s} {'p(blk)':>9s}")
    binom_rows = {}
    for name, b in claimed_bins.items():
        x = int(counts_obs[b])
        p_unif = binom_sf_upper(x, N, p_uniform_deg, lgam)
        p_cond = binom_sf_upper(x, N, exp_cond[b] / N, lgam)
        p_blk = binom_sf_upper(x, N, exp_block[b] / N, lgam)
        print(f"  {name:12s} {x:>4d} | {N*p_uniform_deg:8.2f} {p_unif:10.2e} "
              f"| {exp_cond[b]:8.2f} {p_cond:9.3f} | {exp_block[b]:8.2f} {p_blk:9.3f}")
        binom_rows[name] = {
            "bin": b, "observed": x,
            "uniform_expected": round(N * p_uniform_deg, 3), "p_uniform": p_unif,
            "conditional_expected": round(float(exp_cond[b]), 3), "p_conditional": p_cond,
            "block_expected": round(float(exp_block[b]), 3), "p_block": p_blk,
        }
    print()
    print("  p(unif) reproduces his binomial: a single high bin is astronomically")
    print("  unlikely IF structures were uniform over 90°. p(cond)/p(blk) re-run the")
    print("  identical binomial with the per-degree expectation the geometry actually")
    print("  produces; the same bins are then unremarkable. The small p is a measure")
    print("  of departure from uniformity, not evidence for a pole.")
    print()

    output = {
        "script": "11_data_owner_rule_simulation.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "status": "exploratory_post_publication",
        "file_hash_sha256": verified_hash,
        "random_seed": RANDOM_SEED,
        "M_iterations": M_ITERATIONS,
        "rule": {"threshold": THRESHOLD, "min_run_degrees": MIN_RUN_DEGREES,
                 "min_total": MIN_TOTAL, "nearpole_lat": NEARPOLE_LAT,
                 "nearpole_threshold": NEARPOLE_THRESHOLD},
        "n_in_range": N,
        "observed_histogram_max_per_deg": int(counts_obs.max()),
        "observed_poles_flat12": [{"start": s, "end": e, "total": t} for s, e, t in poles_obs],
        "binomial_uniform_vs_realistic": binom_rows,
        "results": results,
    }
    SUMMARY_FILE.write_text(json.dumps(output, indent=2))
    print(f"Summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}\n")


if __name__ == "__main__":
    main()
