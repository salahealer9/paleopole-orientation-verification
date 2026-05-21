# Independent Monte Carlo Verification of Paleopole Orientation Clustering in the Buildreps Database

**Final Report**

**Author:** Salah-Eddin Gherbi
**ORCID:** 0009-0005-4017-1095
**Version:** 1.0 (draft)
**Date:** [to be added on finalisation]

**Pre-registration:** [10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204)
**Repository:** <https://github.com/salahealer9/paleopole-orientation-verification>
**Frozen analysis log:** [`results/analysis_log_frozen_2026-05-18.md`](https://github.com/salahealer9/paleopole-orientation-verification/blob/main/results/analysis_log_frozen_2026-05-18.md)

---

## 1. Background

The independent researcher Mario Buildreps has assembled, over the past decade, a database of approximately 1,159 ancient pyramids, temples, and megalithic structures worldwide, recording each site's geographic coordinates and the orientation of its principal architectural axis relative to current true north. From this database he proposes a claim that has attracted public attention but no formal independent statistical verification: that the orientations of these ancient structures cluster around five proposed pole positions located along the ~47°W meridian, which he interprets as past positions of Earth's rotational axis. The proposed pole latitudes are 76.0°N, 72.2°N, 64.1°N, and 52.3°N (designated Poles II through V), together with the current geographic pole at 90°N (Pole I). A sixth candidate position at 42.0°N (Pole VI) is described in the framework as "out of scope," excluded from his published probability calculations; the framework notes that including it would weaken those calculations.

The framework's published probability statements — approximately 100% certainty for Poles I–III and approximately 99.999% for Poles IV–V — derive from a binomial test against a uniform null distribution along the 47°W meridian. The bin widths used in this test are non-uniform (between 3° and 10°) and are positioned to capture observed concentrations; the framework characterises this binning scheme as "Dynamical Grouping" in the published methodology. These features of the methodology — the choice of meridian, the choice of null distribution, and the choice of bin widths — were identified prior to the data being opened as candidates for independent re-analysis with a more carefully specified null model.

This report presents the results of that independent re-analysis. The full statistical protocol was pre-registered on Zenodo on 17 May 2026, GPG-signed, and OpenTimestamped on the Bitcoin blockchain before the database file was opened. The SHA-256 hash of the database file is recorded in the pre-registration and verified at the start of every analysis script, ensuring that the analysis can only legitimately be run against the exact file the protocol was written against. The pre-registration commits the analysis to a Monte Carlo null model that preserves site geography and the empirical bearing distribution, with binning-free test statistics, multiple sensitivity analyses, and the explicit pre-commitment that all results will be reported regardless of outcome.

This is not a test of the broader interpretive framework. The Earth-expansion hypothesis, the proposed timeline of human prehistory, the geological mechanism of crustal deformation, and the climatological claims that surround the orientation-clustering observation are all outside the scope of this report. What is tested here is one narrow, falsifiable empirical claim: that the orientations of ancient structures in the database point at the five proposed pole positions more than expected under random orientations applied to the same geographic distribution of sites. That claim is statistical, not historical or geological, and a statistical analysis is sufficient to evaluate it.

The data owner provided the database under the explicit condition that the raw file not be redistributed, but with the freedom to share analytical results, code, and conclusions publicly. He has been informed of the findings reported here and was given a 14-day comment window before public release, per the pre-registration's transparency commitments. His responses, where they bear on the analysis, are noted in the relevant sections.

The principal finding of this report, summarised here so that the reader can keep the conclusion in mind while reading the methods, is mixed and substantive in both directions. Two of the five proposed paleopole latitudes — Pole II (76°N) and Pole III (72.2°N) — show genuine within-hemisphere clustering of intersections that survives every null model tested, including the most stringent variant which preserves regional bearing patterns as well as geography. The remaining three proposed poles (I, IV, V) do not show such clustering under principled null models. The aggregate "primary" test statistic specified in the pre-registration showed an apparently extreme significance (p = 0.0001, more than 26 standard deviations) that turned out, on diagnostic investigation, to be an artifact of a methodological subtlety in the null model's interaction with the data owner's pre-existing northern-hemisphere classification of in-range structures. Under properly conditioned null models, the aggregate signal disappears, while the per-pole signals at Poles II and III remain robust. The full reasoning is in §3 and §4 below.

The framework's claim is therefore neither confirmed nor refuted in the simple sense — it is partially supported in a specific and limited way. The data does contain real structure at two of the five proposed latitudes; the framework's broader interpretive claim, that these latitudes correspond to former geographic pole positions, is not tested here and cannot be established by an orientation-clustering analysis alone.

## 2. Methods

### 2.1 Data

The database file `Database_Mario_Buildreps_V14.xlsx` was provided by the data owner on the date recorded in the project's first repository commit (`ab12dc5`). The SHA-256 hash of the file is `426dd95f4f1d62dbb2ea6b7be0bd2d1499834fb8b2c923ca59299384fd4ddb7c`, recorded in the pre-registration document and re-verified at the start of every analysis script.

The file contains 1,159 rows on its primary sheet (`All Data`), each row representing one structure or site. The relevant columns for this analysis are the geographic coordinates (`LAT`, `LON`), the architectural orientation (`BEARING`, folded into the range [−45°, +45°] relative to current true north per the data owner's convention), and a pre-computed `Intersection Latitude at Lon 47.1W Line` column representing the data owner's own computation of where each structure's great-circle orientation crosses the 47°W meridian. The pre-computed column is used in this analysis only as the inclusion criterion (numeric values mark a structure as "in-range" per the data owner's classification; non-numeric values such as the string "No Intersect 47.1W" mark a structure as "out-of-range"), giving a sample of 994 in-range structures. The actual intersection latitudes used in the analysis are computed independently from the raw `LAT`, `LON`, and `BEARING` columns, using the spherical geometry described below.

A small discrepancy arose during the inclusion-count check: the data owner's stated count of 993 in-range structures differs by one from the count of 994 obtained by applying his classification rule consistently (the difference is one structure whose intersection latitude was recorded in the spreadsheet with a comma decimal separator, `56,2` instead of `56.2`, which would have been missed by any pipeline that didn't apply European-decimal parsing). This single-structure deviation from the pre-registered count was documented openly in the analysis log; we proceed with N = 994 as the count obtained by the inclusion rule, which is the more defensible quantity. The pre-registration anticipated minor data-handling issues of this kind in §12 point 4.

### 2.2 Geometry

For each structure with coordinates (φ, λ) and folded bearing β, we compute the great circle defined by extending the structure's principal axis forward over the sphere, then find the latitude φ′ at which this great circle crosses the 47°W meridian. The geometry is implemented in a shared module (`analysis/geometry.py`) with documented self-tests against analytical reference cases run at the start of every analysis script.

The geometric pipeline is verified against the data owner's pre-computed intersection latitudes for the in-range subset: 95.7% of structures agree within 0.1°, with the remaining residual attributable to floating-point precision and to a small number of structures (eight in total) where the data owner has applied case-by-case manual adjustments to the intersection latitude that are not part of his stated algorithm. When the data owner was asked about these adjustments, he confirmed in correspondence that they are case-by-case manual decisions and explicitly recommended that we use the raw-bearing, geometrically-correct approach rather than mirror his hand-adjustments. We have done so. The full correspondence is documented in the analysis log.

### 2.3 The pre-registered test statistic and the geometric question being asked

The pre-registration specifies the primary test statistic T as the mean over all 994 in-range structures of the minimum angular distance from each structure's great-circle intersection latitude on the 47°W meridian to the nearest of the five proposed poles. Formally, with φ_k ∈ {52.3°, 64.1°, 72.2°, 76.0°, 90.0°} denoting the proposed pole latitudes,

> T = (1/N) Σᵢ minₖ |φ′ᵢ − φₖ|.

Smaller T indicates closer average pointing at the proposed poles. The framework's claim is that T should be smaller than expected under random orientations applied to the same sample of sites — i.e., that the bearings are not arbitrary but are concentrated at intersection latitudes near the proposed paleopoles.

This test statistic is binning-free: it does not depend on any choice of bin width or position, which was a deliberate departure from the data owner's published binomial test against a uniform null with non-uniform "Dynamical Grouping" of bins.

### 2.4 The pre-registered null model and what it tests

The pre-registration §7 specifies the null model as a random permutation of the folded bearings across the in-range sites: each site retains its location, but receives a randomly drawn folded bearing from the empirical pool of 994 bearings, with sampling without replacement (preserving the empirical marginal distribution exactly). Each Monte Carlo iteration produces one permuted bearing assignment and one corresponding value of T. The pre-registration commits to M = 10,000 iterations, with the one-sided p-value computed as

> p = (1 + #{m : T^(m) ≤ T_obs}) / (1 + M).

This null permutes bearings across the geographic distribution of in-range sites without further constraint.

### 2.5 The conditional null model (added in response to a diagnostic finding)

When the pre-registered test was run, the result was so extreme that it triggered a diagnostic investigation before being accepted at face value: T_obs was more than 26 standard deviations below the null mean, with zero of 10,000 random permutations producing T as small as the observed value. A 26-sigma result in archaeological data should be approached with suspicion, not celebration.

The diagnostic revealed a methodological subtlety in how the pre-registered null interacts with the data owner's pre-existing classification of in-range structures. The observed 994 structures were selected by the data owner as "in-range" precisely because their bearings happen to produce intersections in the northern hemisphere of the 47°W meridian — 99% of their intersections fall in the northern hemisphere by selection. Under random permutation of bearings, however, only about 54% of intersections land in the northern hemisphere — because random combinations of (site, bearing) frequently produce southern-hemisphere intersections far from all five proposed (northern) pole latitudes. The pre-registered null, then, was effectively testing two things at once: (i) whether bearings cluster at the proposed poles, and (ii) whether bearings produce predominantly northern-hemisphere intersections — and the very large null mean of T was dominated by the second effect.

To isolate the first question — the within-northern-hemisphere clustering — we implemented an additional null model not specified in the pre-registration, labeled "exploratory" in accordance with §12 point 3 of the pre-registration (which commits us to label any post-data analyses as exploratory and not as confirmatory tests). The conditional null preserves the northern-hemisphere intersection property by construction: bearings are permuted across sites only in such a way that every site receives a bearing which, paired with that site's location, produces a northern-hemisphere intersection. Operationally this is implemented as a Metropolis swap chain on the bipartite compatibility graph of (site, bearing) pairs — each iteration swaps two bearings between two sites if and only if both resulting (site, bearing) pairs are in-range under the same criterion the data owner uses. The chain's acceptance rate (~50%) and mixing properties were verified empirically; details are in the analysis log.

The conditional null answers the within-hemisphere question directly: given that the bearings produce northern-hemisphere intersections, do they cluster at the five specific proposed pole latitudes more than would be expected from great-circle geometry alone? This is the question the original pre-registration intended to ask but, as we discovered when running it, did not cleanly isolate.

### 2.6 The block-conditional null (pre-registered §11(d))

A further pre-registered sensitivity analysis specified in §11(d) of the protocol replaces the global bearing shuffle with a within-block shuffle: bearings are permuted only among sites belonging to the same geographic region. This tests whether the apparent clustering is robust to potential region-specific bearing patterns — for example, whether a regional architectural convention that produces similar bearings within a culture would, by itself, account for the observed concentration at certain latitudes.

We define seven blocks based on simple longitude and latitude boxes: Americas (n=539), Middle East (n=205), Europe-Mediterranean (n=120), South Asia (n=65), East Asia (n=32), Oceania/Southeast Asia (n=23), and Africa (n=2). Eight Central Asian sites that did not fit any of these boxes are assigned to an additional "Other" block. The Americas block is by far the largest, reflecting the geographic concentration of the database.

The block-conditional null combines two restrictions simultaneously: bearings are permuted only within their own geographic block (preserving regional bearing patterns), and only when both resulting (site, bearing) pairings produce northern-hemisphere intersections (the same compatibility criterion as in §2.5, evaluated for within-block swap proposals). It is the most stringent of the four null models we run, and it is the one that most directly tests whether any observed clustering reflects a cross-regional, hemisphere-controlled phenomenon rather than a regional convention or a hemisphere-selection artifact.

### 2.7 Look-elsewhere control (pre-registered §10)

The 47°W meridian is itself a researcher choice: the data owner has identified it as the longitude of strongest clustering in his own exploratory analysis. Asking "is T at 47°W unusually small?" implicitly asks the test to find clustering at *the* most-clustered meridian, which biases the test toward significance. The pre-registration §10 corrects for this with a longitude scan: T is computed observationally at each of 72 meridians (at 5° resolution from −180° to +175°), and the Monte Carlo null records, for each of M = 10,000 iterations, the *minimum* T across all 72 meridians. The p-value is then "how often does the null distribution of minimum-T match or beat T_obs(47°W)?" — testing whether 47°W is unusual against the multiplicity of meridian choices, not just against random bearings at a single meridian.

The pre-registration also commits to a 1° resolution refinement if the 5° result is significant.

### 2.8 Per-pole confirmatory and site-to-pole assignment (pre-registered §11(a, b))

Two pre-registered confirmatory tests address the framework's specific predictions.

The per-pole confirmatory test (§11(a)) counts, for each proposed pole separately, the number of structures whose independent intersection latitude falls within ±1.5° of the pole's latitude. The pre-registered comparison is against the null distribution of the same count under permuted bearings, with Šidák correction (an adjustment for the increased chance of false-positive significance when running multiple tests simultaneously) across the five (or six) simultaneous tests at family-wise α = 0.05.

The site-to-pole assignment test (§11(b)) is a stronger test of the framework's specific predictions: rather than asking "do the bearings cluster at any of the poles," it asks "do the bearings cluster at the *specific* poles assigned to each site." The pre-registration anticipated an explicit assignment table; inspection of the database file (and of the other sheets within it) found no such per-site assignment column. The assignment is therefore operationalized as the nearest of the proposed poles to each structure's data-owner-published intersection latitude — i.e., we let the data owner's own pipeline output define the implicit assignment. The test then asks whether our independent geometry confirms the assignment within ±1.5° more often than expected under random permutation. This methodological decision is documented in the analysis log.

Both tests are run under all four null models described above (pre-registered unconditional + exploratory conditional + pre-registered block-unconditional + pre-registered block-conditional), giving a comprehensive picture of which signals are robust and which are not.

### 2.9 Sensitivity analysis not run: aggregation threshold

The pre-registration §11(c) commits to a sensitivity analysis varying the per-site aggregation threshold across ±1°, ±2°, and ±3° (the data owner's per-site averaging rule for multi-structure sites). Inspection of the database file revealed that the data already incorporates the data owner's aggregation — multi-structure sites have already been collapsed into single rows according to his ~2° rule, and the underlying multi-structure data is not contained in the file. We therefore cannot vary the aggregation threshold against alternative values. This is documented as a limitation of the analysis; the pre-registered sensitivity check was not feasible to implement against the data structure provided.

### 2.10 Reproducibility

All analyses use a fixed pseudo-random seed (`20260517`, derived from the date of the pre-registration deposit) so that Monte Carlo results are bit-for-bit reproducible. The compatibility matrix used by the conditional and block-conditional swap chains is computed once and shared between scripts that use it. The chunk-vectorized implementation processes M = 10,000 permutations across 994 structures in a few seconds for the unconditional nulls and in 30–60 seconds for the conditional nulls (depending on the chain configuration). All scripts, the pre-registration document, the analysis log, and the data file's SHA-256 hash are publicly available at the project repository linked in the document header.

