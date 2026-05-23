# Background

The independent researcher Mario Buildreps has assembled, over the past decade, a database of approximately 1,159 ancient pyramids, temples, and megalithic structures worldwide, recording each site's geographic coordinates and the orientation of its principal architectural axis relative to current true north. From this database he proposes a claim that has attracted public attention but no formal independent statistical verification: that the orientations of these ancient structures cluster around five proposed pole positions located along the ~47°W meridian, which he interprets as past positions of Earth's rotational axis. The proposed pole latitudes are 76.0°N, 72.2°N, 64.1°N, and 52.3°N (designated Poles II through V), together with the current geographic pole at 90°N (Pole I). A sixth candidate position at 42.0°N (Pole VI) is described in the framework as "out of scope," excluded from his published probability calculations; the framework notes that including it would weaken those calculations.

The framework's published probability statements — approximately 100% certainty for Poles I–III and approximately 99.999% for Poles IV–V — derive from a binomial test against a uniform null distribution along the 47°W meridian. The bin widths used in this test are non-uniform (between 3° and 10°) and are positioned to capture observed concentrations; the framework characterises this binning scheme as "Dynamical Grouping" in the published methodology. These features of the methodology — the choice of meridian, the choice of null distribution, and the choice of bin widths — were identified prior to the data being opened as candidates for independent re-analysis with a more carefully specified null model.

This report presents the results of that independent re-analysis. The full statistical protocol was pre-registered on Zenodo on 17 May 2026, GPG-signed, and OpenTimestamped on the Bitcoin blockchain before the database file was opened. The SHA-256 hash of the database file is recorded in the pre-registration and verified at the start of every analysis script, ensuring that the analysis can only legitimately be run against the exact file the protocol was written against. The pre-registration commits the analysis to a Monte Carlo null model that preserves site geography and the empirical bearing distribution, with binning-free test statistics, multiple sensitivity analyses, and the explicit pre-commitment that all results will be reported regardless of outcome.

This is not a test of the broader interpretive framework. The Earth-expansion hypothesis, the proposed timeline of human prehistory, the geological mechanism of crustal deformation, and the climatological claims that surround the orientation-clustering observation are all outside the scope of this report. What is tested here is one narrow, falsifiable empirical claim: that the orientations of ancient structures in the database point at the five proposed pole positions more than expected under random orientations applied to the same geographic distribution of sites. That claim is statistical, not historical or geological, and a statistical analysis is sufficient to evaluate it.

The data owner provided the database under the explicit condition that the raw file not be redistributed, but with the freedom to share analytical results, code, and conclusions publicly. He has been informed of the findings reported here and was given a 14-day comment window before public release, per the pre-registration's transparency commitments. His responses, where they bear on the analysis, are noted in the relevant sections.

The principal finding of this report, summarised here so that the reader can keep the conclusion in mind while reading the methods, is mixed and substantive in both directions. Two of the five proposed paleopole latitudes — Pole II (76°N) and Pole III (72.2°N) — show genuine within-hemisphere clustering of intersections that survives every null model tested, including the most stringent variant which preserves regional bearing patterns as well as geography. The remaining three proposed poles (I, IV, V) do not show such clustering under principled null models. The aggregate "primary" test statistic specified in the pre-registration showed an apparently extreme significance (p = 0.0001, more than 26 standard deviations) that turned out, on diagnostic investigation, to be an artifact of a methodological subtlety in the null model's interaction with the data owner's pre-existing northern-hemisphere classification of in-range structures. Under properly conditioned null models, the aggregate signal disappears, while the per-pole signals at Poles II and III remain robust. The full reasoning is in §3 and §4 below.

The framework's claim is therefore neither confirmed nor refuted in the simple sense — it is partially supported in a specific and limited way. The data does contain real structure at two of the five proposed latitudes; the framework's broader interpretive claim, that these latitudes correspond to former geographic pole positions, is not tested here and cannot be established by an orientation-clustering analysis alone.

# Methods

## Data

The database file `Database_Mario_Buildreps_V14.xlsx` was provided by the data owner on the date recorded in the project's first repository commit (`ab12dc5`). The SHA-256 hash of the file is 
\texttt{\seqsplit{426dd95f4f1d62dbb2ea6b7be0bd2d1499834fb8b2c923ca59299384fd4ddb7c}}, recorded in the pre-registration document and re-verified at the start of every analysis script.

The file contains 1,159 rows on its primary sheet (`All Data`), each row representing one structure or site. The relevant columns for this analysis are the geographic coordinates (`LAT`, `LON`), the architectural orientation (`BEARING`, folded into the range [−45°, +45°] relative to current true north per the data owner's convention), and a pre-computed `Intersection Latitude at Lon 47.1W Line` column representing the data owner's own computation of where each structure's great-circle orientation crosses the 47°W meridian. The pre-computed column is used in this analysis only as the inclusion criterion (numeric values mark a structure as "in-range" per the data owner's classification; non-numeric values such as the string "No Intersect 47.1W" mark a structure as "out-of-range"), giving a sample of 994 in-range structures. The actual intersection latitudes used in the analysis are computed independently from the raw `LAT`, `LON`, and `BEARING` columns, using the spherical geometry described below.

A small discrepancy arose during the inclusion-count check: the data owner's stated count of 993 in-range structures differs by one from the count of 994 obtained by applying his classification rule consistently (the difference is one structure whose intersection latitude was recorded in the spreadsheet with a comma decimal separator, `56,2` instead of `56.2`, which would have been missed by any pipeline that didn't apply European-decimal parsing). This single-structure deviation from the pre-registered count was documented openly in the analysis log; we proceed with N = 994 as the count obtained by the inclusion rule, which is the more defensible quantity. The pre-registration anticipated minor data-handling issues of this kind in §12 point 4.

## Geometry

For each structure with coordinates (φ, λ) and folded bearing β, we compute the great circle defined by extending the structure's principal axis forward over the sphere, then find the latitude φ′ at which this great circle crosses the 47°W meridian. The geometry is implemented in a shared module (`analysis/geometry.py`) with documented self-tests against analytical reference cases run at the start of every analysis script.

The geometric pipeline is verified against the data owner's pre-computed intersection latitudes for the in-range subset: 95.7% of structures agree within 0.1°, with the remaining residual attributable to floating-point precision and to a small number of structures (eight in total) where the data owner has applied case-by-case manual adjustments to the intersection latitude that are not part of his stated algorithm. When the data owner was asked about these adjustments, he confirmed in correspondence that they are case-by-case manual decisions and explicitly recommended that we use the raw-bearing, geometrically-correct approach rather than mirror his hand-adjustments. We have done so. The full correspondence is documented in the analysis log.

## The pre-registered test statistic and the geometric question being asked

The pre-registration specifies the primary test statistic T as the mean over all 994 in-range structures of the minimum angular distance from each structure's great-circle intersection latitude on the 47°W meridian to the nearest of the five proposed poles. Formally, with φₖ ∈ {52.3°, 64.1°, 72.2°, 76.0°, 90.0°} denoting the proposed pole latitudes,

> T = (1/N) Σᵢ minₖ |φ′ᵢ − φₖ|.

Smaller T indicates closer average pointing at the proposed poles. The framework's claim is that T should be smaller than expected under random orientations applied to the same sample of sites — i.e., that the bearings are not arbitrary but are concentrated at intersection latitudes near the proposed paleopoles.

This test statistic is binning-free: it does not depend on any choice of bin width or position, which was a deliberate departure from the data owner's published binomial test against a uniform null with non-uniform "Dynamical Grouping" of bins.

## The pre-registered null model and what it tests

The pre-registration §7 specifies the null model as a random permutation of the folded bearings across the in-range sites: each site retains its location, but receives a randomly drawn folded bearing from the empirical pool of 994 bearings, with sampling without replacement (preserving the empirical marginal distribution exactly). Each Monte Carlo iteration produces one permuted bearing assignment and one corresponding value of T. The pre-registration commits to M = 10,000 iterations, with the one-sided p-value computed as

> p = (1 + #{m : T^(m) ≤ T_obs}) / (1 + M).

This null permutes bearings across the geographic distribution of in-range sites without further constraint.

## The conditional null model (added in response to a diagnostic finding)

When the pre-registered test was run, the result was so extreme that it triggered a diagnostic investigation before being accepted at face value: T_obs was more than 26 standard deviations below the null mean, with zero of 10,000 random permutations producing T as small as the observed value. A 26-sigma result in archaeological data should be approached with suspicion, not celebration.

The diagnostic revealed a methodological subtlety in how the pre-registered null interacts with the data owner's pre-existing classification of in-range structures. The observed 994 structures were selected by the data owner as "in-range" precisely because their bearings happen to produce intersections in the northern hemisphere of the 47°W meridian — 99% of their intersections fall in the northern hemisphere by selection. Under random permutation of bearings, however, only about 54% of intersections land in the northern hemisphere — because random combinations of (site, bearing) frequently produce southern-hemisphere intersections far from all five proposed (northern) pole latitudes. The pre-registered null, then, was effectively testing two things at once: (i) whether bearings cluster at the proposed poles, and (ii) whether bearings produce predominantly northern-hemisphere intersections — and the very large null mean of T was dominated by the second effect.

To isolate the first question — the within-northern-hemisphere clustering — we implemented an additional null model not specified in the pre-registration, labeled "exploratory" in accordance with §12 point 3 of the pre-registration (which commits us to label any post-data analyses as exploratory and not as confirmatory tests). The conditional null preserves the northern-hemisphere intersection property by construction: bearings are permuted across sites only in such a way that every site receives a bearing which, paired with that site's location, produces a northern-hemisphere intersection. Operationally this is implemented as a Metropolis swap chain on the bipartite compatibility graph of (site, bearing) pairs — each iteration swaps two bearings between two sites if and only if both resulting (site, bearing) pairs are in-range under the same criterion the data owner uses. The chain's acceptance rate (~50%) and mixing properties were verified empirically; details are in the analysis log.

The conditional null answers the within-hemisphere question directly: given that the bearings produce northern-hemisphere intersections, do they cluster at the five specific proposed pole latitudes more than would be expected from great-circle geometry alone? This is the question the original pre-registration intended to ask but, as we discovered when running it, did not cleanly isolate.

## The block-conditional null (pre-registered §11(d))

A further pre-registered sensitivity analysis specified in §11(d) of the protocol replaces the global bearing shuffle with a within-block shuffle: bearings are permuted only among sites belonging to the same geographic region. This tests whether the apparent clustering is robust to potential region-specific bearing patterns — for example, whether a regional architectural convention that produces similar bearings within a culture would, by itself, account for the observed concentration at certain latitudes.

We define seven blocks based on simple longitude and latitude boxes: Americas (n=539), Middle East (n=205), Europe-Mediterranean (n=120), South Asia (n=65), East Asia (n=32), Oceania/Southeast Asia (n=23), and Africa (n=2). Eight Central Asian sites that did not fit any of these boxes are assigned to an additional "Other" block. The Americas block is by far the largest, reflecting the geographic concentration of the database.

The block-conditional null combines two restrictions simultaneously: bearings are permuted only within their own geographic block (preserving regional bearing patterns), and only when both resulting (site, bearing) pairings produce northern-hemisphere intersections (the same compatibility criterion as in §2.5, evaluated for within-block swap proposals). It is the most stringent of the four null models we run, and it is the one that most directly tests whether any observed clustering reflects a cross-regional, hemisphere-controlled phenomenon rather than a regional convention or a hemisphere-selection artifact.

## Look-elsewhere control (pre-registered §10)

The 47°W meridian was treated by the pre-registration as a researcher-selected parameter that warrants look-elsewhere correction. The data owner, in commentary provided during the 14-day pre-publication window (see Appendix A), has clarified that the 47°W value was derived from a 2015 geometric calculation rather than identified by scanning for the strongest clustering. Specifically, he reports that the intersection of great-circle paths from the average orientations of Western and Eastern Hemisphere structures, computed in 2015, yields 71.6°N, 47.1°W. A 2020 recalculation with an expanded dataset yielded approximately 58°N, 44°W — still in the same Atlantic sector but drifted from the 2015 value.

Whether the meridian is best understood as theoretically-derived or as an empirically-tuned parameter is a question this analysis cannot fully adjudicate. The 2015 derivation is plausible but not independently verified by our analysis. The 2020 drift to 44°W and the empirical attractor at −20°E (§3.4) both indicate that the exact longitude is not strongly determined by either method. We retain the look-elsewhere scan as a useful descriptive instrument regardless of the meridian's provenance: it reports the observed data's structure across longitudes and characterises the natural attractor band for great-circle intersections in this site distribution.

The pre-registration §10 corrects for the meridian choice with a longitude scan: T is computed observationally at each of 72 meridians (at 5° resolution from −180° to +175°), and the Monte Carlo null records, for each of M = 10,000 iterations, the *minimum* T across all 72 meridians. The p-value is then "how often does the null distribution of minimum-T match or beat T_obs(47°W)?" — testing whether 47°W is unusual against the multiplicity of meridian choices, not just against random bearings at a single meridian. The pre-registration also commits to a 1° resolution refinement if the 5° result is significant.

## Per-pole confirmatory and site-to-pole assignment (pre-registered §11(a, b))

Two pre-registered confirmatory tests address the framework's specific predictions.

The per-pole confirmatory test (§11(a)) counts, for each proposed pole separately, the number of structures whose independent intersection latitude falls within ±1.5° of the pole's latitude. The pre-registered comparison is against the null distribution of the same count under permuted bearings, with Šidák correction (an adjustment for the increased chance of false-positive significance when running multiple tests simultaneously) across the five (or six) simultaneous tests at family-wise α = 0.05.

The site-to-pole assignment test (§11(b)) is a stronger test of the framework's specific predictions: rather than asking "do the bearings cluster at any of the poles," it asks "do the bearings cluster at the *specific* poles assigned to each site." The pre-registration anticipated an explicit assignment table; inspection of the database file (and of the other sheets within it) found no such per-site assignment column. The assignment is therefore operationalized as the nearest of the proposed poles to each structure's data-owner-published intersection latitude — i.e., we let the data owner's own pipeline output define the implicit assignment. The test then asks whether our independent geometry confirms the assignment within ±1.5° more often than expected under random permutation. This methodological decision is documented in the analysis log.

Both tests are run under all four null models described above (pre-registered unconditional + exploratory conditional + pre-registered block-unconditional + pre-registered block-conditional), giving a comprehensive picture of which signals are robust and which are not.

## Sensitivity analysis not run: aggregation threshold

The pre-registration §11(c) commits to a sensitivity analysis varying the per-site aggregation threshold across ±1°, ±2°, and ±3° (the data owner's per-site averaging rule for multi-structure sites). Inspection of the database file revealed that the data already incorporates the data owner's aggregation — multi-structure sites have already been collapsed into single rows according to his ~2° rule, and the underlying multi-structure data is not contained in the file. We therefore cannot vary the aggregation threshold against alternative values. This is documented as a limitation of the analysis; the pre-registered sensitivity check was not feasible to implement against the data structure provided.

## Reproducibility

All analyses use a fixed pseudo-random seed (`20260517`, derived from the date of the pre-registration deposit) so that Monte Carlo results are bit-for-bit reproducible. The compatibility matrix used by the conditional and block-conditional swap chains is computed once and shared between scripts that use it. The chunk-vectorized implementation processes M = 10,000 permutations across 994 structures in a few seconds for the unconditional nulls and in 30–60 seconds for the conditional nulls (depending on the chain configuration). All scripts, the pre-registration document, the analysis log, and the data file's SHA-256 hash are publicly available at the project repository linked in the document header.

# Results

## The pre-registered primary result

Under the pre-registered null model (§2.4), the primary test statistic at the 47°W meridian gave the following result with M = 10,000 Monte Carlo iterations:

- **T_obs** = 4.65°
- Null distribution mean = 55.9°, standard deviation 1.7°, minimum across 10,000 iterations = 49.9°
- **Count of T^(m) ≤ T_obs: 0 / 10,000**
- **p = 0.0001** (the floor of the Monte Carlo resolution)

Per the pre-registration's verdict criteria (§9), this result is "highly significant" at the α = 0.05 threshold. The observed T value of 4.65° is more than 26 standard deviations below the null mean. The pre-registered 6-pole sensitivity analysis (including Pole VI at 42°N) produced the same qualitative result: T_obs = 3.61°, null mean = 50.6°, p = 0.0001.

This is the pre-registered confirmatory finding. Were it the only test performed, it would constitute strong statistical support for the framework's clustering claim. However, the magnitude of the result — a separation between observed and null of more than 45 degrees — exceeded what we expected from the analysis even under the framework's own hypothesis, and prompted a diagnostic investigation before the result was accepted at face value.

## Diagnostic: what the pre-registered null is actually testing

A simple diagnostic comparing the observed intersection latitudes with those produced by a single random permutation revealed the source of the extreme magnitude. The observed in-range set is 99% northern-hemisphere intersections by construction: those structures are precisely the ones the data owner classified as in-range because their bearings produce intersections north of the equator. Under random permutation, however, only about 54% of intersections land in the northern hemisphere — the random pairing of bearings to sites frequently produces great circles that cross the 47°W meridian in the southern hemisphere, far from any of the five (northern) proposed poles.

To isolate the within-hemisphere question, we stratified d_min (the per-structure distance to the nearest pole) within a single random permutation by hemisphere of the resulting intersection:

- Permuted intersections falling in the northern hemisphere (540 of 994 in the iteration we examined): **median d_min = 2.02°**.
- Permuted intersections falling in the southern hemisphere (454 of 994): median d_min = 119.3°.
- The corresponding observed-data quantity: median d_min = 1.81°.

The observed within-hemisphere clustering (1.81°) is essentially indistinguishable from the within-hemisphere clustering produced by random permutation (2.02°). The dramatic difference between the observed T (4.65°) and the null T (55.9°) is therefore explained by the difference in *hemisphere composition* (99% northern vs 54% northern), not by within-hemisphere structure. Random permutations contribute ~120° per southern intersection to T; observed permutations contribute essentially none. The pre-registered null was conflating two distinct questions: whether bearings cluster at the proposed poles, and whether bearings produce predominantly northern-hemisphere intersections.

## The conditional null result

The conditional null (§2.5) preserves the northern-hemisphere intersection property by construction, isolating the within-hemisphere clustering question. Under M = 10,000 Metropolis-swap-chain samples:

- T_obs = 4.65° (unchanged; the observed test statistic is the same)
- **Conditional null distribution mean = 4.13°, standard deviation 0.15°, range [3.59°, 5.29°]**
- **Count of T^(m) ≤ T_obs: 9,989 / 10,000**
- **p (exploratory) = 0.9989**

The observed test statistic sits at approximately the 99.9th percentile of the conditional null distribution — i.e., observed pole-pointing, measured by aggregate T, is *less* concentrated than the within-hemisphere null distribution. The pre-registered result of "26-sigma highly significant" is, under the appropriate within-hemisphere null, reversed: the observed bearings produce slightly more dispersion across the northern hemisphere than would be expected from random great-circle geometry on this site distribution.

A contributing factor: the eight manually-snapped structures (whose geometrically-correct intersections fall near −89°N while the data owner's published intersections are 90°N) each contribute d_min ≈ 141° to T_obs under our independent geometry. These eight structures inflate T_obs by approximately 1.1° relative to a sample that excluded them. Even setting them aside, however, the residual T_obs of ~3.5° remains above the conditional null mean of 4.13° — the manually-snapped structures account for some but not all of the apparent dispersion.

## The longitude scan and a descriptive finding about meridian choice

The pre-registered look-elsewhere control (§2.7) computed T at each of 72 meridians at 5° resolution and compared T_obs(47°W) to the null distribution of the minimum-T across all 72.

Two distinct findings emerged: one descriptive, and one statistical.

**Descriptive finding (independent of any null model).** Among the 72 longitudes scanned, the *observed* T was minimised not at the 47°W meridian but at −20°E. The ten most-clustered meridians in the observed data are:

| Rank | Longitude | T_obs |
|---:|---:|---:|
| 1 | −20°E | 3.78° |
| 2 | −25°E | 3.79° |
| 3 | −30°E | 3.83° |
| 4 | −15°E | 3.84° |
| 5 | −35°E | 3.94° |
| 6 | −10°E | 3.98° |
| 7 | −40°E | 4.16° |
| 8 | **−45°E** | **4.47°** (pre-registered band) |
| 9 | −5°E | 4.51° |
| 10 | 0°E | 5.07° |

The pre-registered 47°W meridian is rank 10 of 72. The geometric attractor band of strongest clustering is a contiguous longitude window from approximately −40°E to 0°E (Atlantic Ocean between West Africa and Brazil, plus the prime meridian), with the minimum at −20°E rather than at 47°W. This is a finding about the data itself, independent of any statistical model; it shows that the framework's choice of the 47°W meridian as the locus of clustering does not coincide with the meridian at which the observed data is most-tightly clustered.

**Statistical finding (pre-registered).** The look-elsewhere null distribution, like the primary null, is dominated by the hemisphere-mismatch effect: T_min null mean = 45.0°, standard deviation 1.3°. Under this null, T_obs(47°W) = 4.65° gives p_LEE = 0.0001 at 5° resolution. The same result at the pre-registered 1° resolution refinement was also p_LEE = 0.0001. These p-values inherit the same interpretive limitation as the primary §7 result: they are dominated by hemisphere-mismatch, not by genuine 47°W-specific clustering. The longitude scan uses the same aggregate T statistic shown to be unreliable for the primary test, and the same caveat applies: a statistic that is dominated by hemisphere-selection at one meridian is dominated by the same effect when applied across 72 meridians. The pre-registered p_LEE value is reported here as the pre-registered finding, with this limitation acknowledged.

The descriptive finding above (47°W is rank 10, attractor at −20°E) is the more substantive look-elsewhere observation, as it does not depend on a null model.

## Per-pole confirmatory results across all four null models

The pre-registered per-pole confirmatory test (§11(a)) counts structures within ±1.5° of each proposed pole latitude. With four null models tested and five (or six) poles per family, the natural presentation is a table. We report 5-pole results under each null model below; 6-pole results are qualitatively identical (numerical values are in the analysis log).

| Pole | Lat (°N) | Observed | Uncond. null mean | p-Šidák (uncond.) | Cond. null mean | p-Šidák (cond.) | Block-cond. null mean | p-Šidák (block-cond.) |
|---|---|---|---|---|---|---|---|---|
| I (current) | 90.0 | 95 | 84.4 | 0.003 | 102.8 | 1.000 | 95.4 | 1.000 |
| II | 76.0 | 115 | 43.7 | 0.0005 | 85.9 | **0.0005** | 90.3 | **0.0015** |
| III | 72.2 | 119 | 42.9 | 0.0005 | 83.8 | **0.0005** | 90.6 | **0.0005** |
| IV | 64.1 | 70 | 32.5 | 0.0005 | 63.7 | 0.666 | 70.1 | 0.979 |
| V | 52.3 | 57 | 20.9 | 0.0005 | 42.2 | 0.044 | 50.8 | 0.542 |

Reading the table by column:

- **Unconditional null**: all five proposed poles show "significant" excess (p-Šidák ≤ 0.003), reflecting the same hemisphere-mismatch effect described in §3.2. Without the conditional and block-conditional checks, this is the result the pre-registered test would have presented as a confirmation of the framework.

- **Conditional null**: under the within-hemisphere null, Poles II (76.0°N) and III (72.2°N) maintain strong significance (p-Šidák = 0.0005). Pole V (52.3°N) is marginally significant (p-Šidák = 0.044). Poles I and IV show no excess.

- **Block-conditional null**: this is the most stringent of the four. Poles II and III remain significant (p-Šidák = 0.0015 and 0.0005). Pole V's marginal signal disappears (p-Šidák = 0.542), indicating that the apparent excess at 52.3°N was driven by region-specific bearing patterns and is eliminated when bearings are shuffled only within their own geographic block. Poles I and IV continue to show no excess.

**The robust signals are at Poles II and III.** Approximately 234 structures (24% of the in-range set) point at intersections near these two latitudes, ~50 more than expected under the most stringent null model. This excess survives every null model tested, including the block-conditional null that preserves regional bearing patterns. The clustering at 76°N and 72.2°N is a real feature of the data that cannot be attributed to hemisphere selection, regional patterns, or sampling geometry.

## Site-to-pole assignment results

The pre-registered §11(b) test asks whether the data owner's implicit pole assignments (operationalized as the nearest pole to each structure's data-owner-published intersection latitude — see §2.8) are confirmed by our independent geometry within ±1.5°. Across all four null models:

| Null model | Status | Observed match | Null mean | p |
|---|---|---|---|---|
| Pre-registered unconditional | Confirmatory | 454 / 994 (46%) | 45.5 (4.6%) | 0.0001 |
| Conditional (exploratory) | Exploratory | 454 / 994 | 81.1 (8.2%) | 0.0001 |
| Block-unconditional | Confirmatory | 454 / 994 | 92.3 (9.3%) | 0.0001 |
| Block-conditional | Confirmatory | 454 / 994 | 92.2 (9.3%) | 0.0001 |

The assignment match rate is robustly significant under every null model, including the most stringent. The observed match rate of 46% is approximately 5× the expected rate under the block-conditional null (9.3%), and the null distribution has small variance (std ≈ 8 of 994), placing the observed value many standard deviations above the null distribution.

Interpretively, this result reflects two facts about the data. First, our independent geometry and the data owner's pipeline agree on the intersection latitude to within 0.1° for 95.7% of structures, so the assignment derived from his pipeline is closely confirmed by ours. Second, the bearings concentrate in narrow latitude bands within the northern hemisphere, so the question "is this structure within 1.5° of *its* assigned pole" is approximately equivalent to "is this structure within 1.5° of *any* pole," given the concentration structure of the data. The signal is robust to all four null models because it captures both pipeline agreement and within-hemisphere concentration, both of which are real features of the data.

## Summary of all tests

The complete set of pre-registered and exploratory tests is summarised in the table below. The "Status" column distinguishes pre-registered confirmatory tests (which can support or fail to support pre-registered hypotheses) from exploratory tests (which provide methodological diagnostic information but cannot make confirmatory claims, per pre-registration §12 point 3).

| Test | Section | Status | p-value | Interpretation |
|---|---|---|---|---|
| Primary T, unconditional null | §7 | Pre-registered | 0.0001 | Significant by hemisphere-mismatch artifact |
| Primary T, conditional null | (added) | Exploratory | 0.9989 | Observed less concentrated than null |
| Look-elsewhere, unconditional | §10 | Pre-registered | 0.0001 | Same artifact; descriptive: 47°W is rank 10/72 |
| §11(a) per-pole, unconditional | §11(a) | Pre-registered | all p < 0.003 | All five "significant" by artifact |
| §11(a) per-pole, conditional | (added) | Exploratory | II, III: 0.0005; V: 0.044 | Poles II, III robust; V marginal; I, IV null |
| §11(a) per-pole, block-conditional | §11(d) | **Pre-registered** | **II: 0.0015; III: 0.0005** | **Poles II, III remain robust; V eliminated** |
| §11(b) assignment, unconditional | §11(b) | Pre-registered | 0.0001 | Partly artifact, partly genuine |
| §11(b) assignment, conditional | (added) | Exploratory | 0.0001 | Robust ~45σ effect |
| §11(b) assignment, block-conditional | §11(d) | **Pre-registered** | **0.0001** | **Robust to regional patterns** |

The pre-registered findings, taken at face value (the four "all significant" rows in the unconditional null), tell one story: the framework's clustering claim is strongly confirmed across all tests. The full picture, including the conditional and block-conditional results, tells a more specific story: clustering at Poles II and III is robust under stringent tests; clustering at Poles I, IV, V is not; the aggregate test statistic is null under the appropriate null model; the data owner's implicit pole assignments are robustly confirmed by our independent geometry. Interpretation of these results is the subject of §4.

# Discussion

## What the data shows

Setting aside interpretation for a moment, the empirical observations from §3 can be stated as follows:

- Within the 994 in-range structures, intersection latitudes on the 47°W meridian show real concentration at two of the five proposed pole latitudes — Pole II (76.0°N) and Pole III (72.2°N). Approximately 234 structures (24% of the sample) point at intersections within ±1.5° of these two latitudes, roughly 50 more than expected under the most stringent null model tested. This excess survives all four null variants (unconditional, conditional, block-unconditional, block-conditional).
- The other three proposed pole latitudes do not show robust clustering. Pole V (52.3°N) showed weak excess under the conditional null but was eliminated by the block-conditional null, indicating its apparent signal was driven by region-specific bearing patterns rather than a cross-regional phenomenon. Poles I (90°N) and IV (64.1°N) show no excess under any principled null model.
- The aggregate primary test statistic, T = mean d_min, is null under principled nulls. The "26-sigma highly significant" pre-registered result was an artifact of hemisphere-mismatch between the observed (99% northern by selection) and permuted (~54% northern by chance) intersection distributions; under nulls that preserve the in-range property by construction, T_obs is consistent with random great-circle geometry on this site distribution.
- The site-to-pole assignment match rate (454 of 994, or 46%) is robustly significant under all four null models. Interpretively, this result reflects two facts about the data: our independent geometry agrees with the data owner's pipeline to within 0.1° for 95.7% of structures, and the bearings concentrate in narrow latitude bands within the northern hemisphere. The signal captures both pipeline agreement and within-hemisphere concentration.
- Descriptively (independent of any null model), the 47°W meridian is not the meridian at which the observed data is most-tightly clustered. Across the 72 longitudes scanned at 5° resolution, the minimum T was observed at −20°E, and the 47°W meridian was rank 10 of 72. The natural geometric attractor band for great-circle intersections in this site distribution is a contiguous longitude window from approximately −40°E to 0°E.

## Alternative explanations for the within-hemisphere clustering at Poles II and III

The clustering at 76°N and 72°N is a real feature of the data — but its cause is not determined by this analysis. Several distinct hypotheses can explain it; an orientation-clustering test does not, in principle, distinguish among them.

**Cultural orientation conventions.** Ancient architectural traditions often align structures to specific celestial or landscape features. If the relevant features (the cardinal points, the celestial pole as it appeared in the past, prominent astronomical objects, regional landscape orientations) happened to project, by great-circle geometry, to specific latitudes on the 47°W meridian, the resulting intersection distribution would show concentration without any reference to former pole positions.

**Astronomical alignments.** Structures oriented to solstitial sunrise/sunset, lunar standstill events, stellar risings, or other astronomical phenomena will produce bearings that depend on the structure's latitude and the celestial event's declination. These dependencies can produce great-circle intersections that cluster at latitudes that have no special status as pole positions but are simply where the geometry concentrates intersections for a population of mid-latitude sites observing common celestial events.

**Archaeological measurement effects.** Bearings in the database are reported to a precision of approximately 0.5–1.0° (the data owner's stated measurement error). Quantization in bearing measurement, combined with the data owner's per-site averaging rule for multi-structure sites, can produce apparent concentration at specific latitudes as an artifact of the discretization rather than as a property of the underlying orientations.

**Selection in the database itself.** The database is a curated collection. If the data owner's site-selection process favored structures that point in particular directions — even unintentionally, through criteria like "well-documented orientation" or "archaeological prominence" — the resulting sample could show clustering that reflects the selection rather than a universal architectural pattern.

**The framework's own claim.** The data owner's hypothesis is that the clustering reflects past positions of Earth's rotational axis at the times the structures were built. Under this hypothesis, the orientation patterns would directly encode the geographic locations of paleopoles.

Our analysis cannot distinguish among these explanations, and no claim about the cause of the observed clustering is implied by the statistical findings.

## What the framework's broader claim requires

The framework's interpretive claim — that the observed latitude concentrations correspond to former positions of Earth's rotational axis — is qualitatively different from the orientation-clustering claim our analysis tests. An orientation-clustering test can establish whether clustering exists; it cannot establish the *cause*. The framework's broader claim is a geological and geophysical claim, and it requires geological and geophysical evidence to evaluate.

What kind of evidence would bear on the claim?

**Paleomagnetic data from the proposed time periods.** Earth's magnetic and rotational poles do not coincide, but their relationship is constrained over geological time. Paleomagnetic measurements from rocks dating to the time windows when the framework proposes the rotational axis was at each of the alternative pole positions could test whether the magnetic-pole record is consistent with such large excursions of the rotational axis.

**Geological evidence of true polar wander.** Apparent polar wander paths are a standard subject of plate tectonics; large excursions of the rotational pole on the timescales implicit in the framework (tens of thousands of years rather than tens of millions) would imply specific patterns of crustal deformation, sea-level change, and climate that should be detectable in the geological record.

**Independent dating of the structures.** The framework attaches specific date ranges to each proposed pole (the time during which that latitude was supposedly the rotational pole). Comparing structure construction dates from radiocarbon, dendrochronology, archaeological context, or other dating methods against the framework's proposed timeline would test the temporal consistency of the claim.

**Climate and sea-level proxies.** Different paleopole positions imply different global climate regimes. Independent climate proxies from the proposed time windows (ice cores, sediment records, biological proxies) could test whether the implied climate matches the geological record.

None of this is within the scope of the present analysis, and none is required by the orientation-clustering claim taken on its own terms. But the framework's broader interpretive claim — the one that distinguishes it from any of the alternative explanations enumerated in §4.2 — depends on this kind of independent evidence. The orientation pattern, on its own, is consistent with multiple causes.

## Methodological lessons from the diagnostic

The most generalisable contribution of this analysis is methodological, not substantive: the demonstration that a 26-standard-deviation pre-registered result can be a hemisphere-selection artifact rather than a genuine effect.

The pre-registration committed the analysis to a specific null model: random permutation of folded bearings across the 994 in-range sites. This null preserves site geography and the marginal bearing distribution. It does not, however, preserve the *condition that gave rise to the in-range set in the first place* — namely, that those 994 structures had bearings producing northern-hemisphere intersections on the 47°W meridian. Under random permutation, only about 54% of permuted intersections land in the northern hemisphere, while the observed in-range set is 99% northern by construction. The test of "is the observed T smaller than the null T?" is therefore conflated with the test of "do random bearings preserve the northern-hemisphere selection?" — and the latter dominates, producing a null mean for T of approximately 56° even though the within-hemisphere clustering question gives a null mean of approximately 4°.

The lesson is concrete and transferable to any pre-registered analysis that operates on a filtered or curated data set:

> **Pre-register the full data-processing pipeline, not just the final test statistic. Selection effects that operate before the registered test can produce arbitrarily large apparent significance.**

When a data set has been filtered using a criterion that interacts with the test statistic, the null model must preserve that criterion by construction, not assume that random permutation will reproduce it in expectation.

The conditional null model implemented in this analysis (§2.5) is one way to achieve this: a Metropolis swap chain on the bipartite compatibility graph, accepting only those permutations that satisfy the in-range criterion for every structure. The block-conditional null (§2.6) generalises this further by also preserving regional partitioning. The general principle is that the null model is a model of the data-generating process *under the null hypothesis*, and the data-generating process includes any filtering that operated on the sample before it reached the test.

This is not a flaw in the abstract concept of pre-registration. It is a flaw in any pre-registration that does not anticipate the full pipeline. The remedy is more careful pipeline specification, not less stringent pre-registration.

## Limitations of this analysis

Several limitations constrain the conclusions that can be drawn from this work.

**The aggregation-threshold sensitivity (§11(c)) was not implementable.** The data file contains the data owner's pre-aggregated structure entries, where multi-structure sites have already been collapsed into single rows according to his stated ~2° rule. The underlying multi-structure data was not available, so we could not vary the aggregation threshold to test sensitivity. The pre-registered sensitivity check is documented as not run.

**The eight manually-snapped structures.** The data owner's published intersection latitudes for eight structures with near-zero bearings differ from the geometrically-correct values by ~180°. These are case-by-case manual adjustments confirmed by the data owner. Our analysis uses the geometrically-correct values, which contribute ~141° per structure to T_obs and reduce the §11(b) assignment match count by 8 from 462 to 454. The analytical effect is small but documented.

**The database has not been independently audited for completeness or systematic biases.** The 1,159 structures in the database represent the data owner's selection from a much larger global population of ancient monuments. The selection criteria, the completeness of coverage, and potential systematic biases (toward certain structure types, certain geographic regions, certain time periods, or certain orientation patterns) have not been independently verified. Any clustering observed in the database is a property of *this specific curated sample* and may not generalise to a complete or differently-curated population of ancient structures.

**Regional imbalance in the sample.** The Americas block (n = 539) contains 54% of the in-range structures. The remaining 455 structures are distributed across six other geographic blocks, with two of them (Africa, Oceania/SE Asia) holding fewer than 25 structures each. The block-conditional null is therefore much more constrained by the Americas block than by the others, and the per-region analysis is limited by sample size in the smaller blocks. The geographic coverage of the database is also heavily weighted toward Mesoamerican and Mediterranean-Middle Eastern sites, which may affect the generalisability of any findings to ancient structures in regions less represented in this sample.

**What the block-conditional null can and cannot detect.** The block-conditional null is the most stringent test in this analysis, preserving site geography, regional bearing patterns, and northern-hemisphere intersection simultaneously. It is, however, *conservative* with respect to cross-regional signals that operate within blocks. The null shuffles bearings within each block while leaving structures in their original blocks. A signal that appears in multiple blocks simultaneously — for instance, if structures in the Americas, Europe, and Asia all point toward a common latitude — would not be eliminated by the null, because the structures remain in their original blocks and the cross-block pattern is preserved. The null does, however, absorb any signal whose driving force is *region-specific bearing distribution alone*. If the latitude concentration is driven by, say, a regional architectural convention that happens to produce a particular intersection latitude when applied to the typical sites in that region, the null will erase it (this is, in fact, what we observe for Pole V: §3.5). If the latitude concentration is shared *across* regions but absent *within* any single region's distribution, the null might partially absorb such a signal. The signals we detect at Poles II and III survive the block-conditional null with substantial excess (115 vs 90, 119 vs 91), which indicates either that the signal is genuinely cross-regional (the structures clustering at these latitudes come from multiple blocks) or that the signal is sufficiently robust to within-block permutation that it cannot be eliminated. We do not formally separate these two possibilities. A reader inclined toward the data owner's framework would note that a global geophysical event would produce a cross-regional pattern by construction; the null is well-suited to detecting such patterns precisely because they survive within-block permutation.

**The analysis tests one specific framework, not a general hypothesis about ancient orientations.** The proposed pole latitudes were specified by the data owner before our analysis began, so the test is well-defined. But the test does not address alternative configurations of paleopoles, alternative meridians, or other frameworks that might also predict clustering at different latitudes. The conclusions are specific to the framework as specified in the pre-registration document.

## Comparison with the data owner's published probability claims

The data owner's published methodology associates the following confidence claims with each pole:

- Pole I (current): approximately 100%
- Pole II (76°N): approximately 100%
- Pole III (72.2°N): approximately 100%
- Pole IV (64.1°N): approximately 99.999%
- Pole V (52.3°N): approximately 99.999%

These claims derive from a binomial test against a uniform null distribution along the 47°W meridian, using non-uniform bin widths described as "Dynamical Grouping" of the latitude axis.

The present analysis does not support these confidence claims in their published form. Under principled null models that preserve the relevant features of the data (site geography, in-range hemisphere selection, regional patterns), the analysis finds:

- Pole I: no excess concentration (observed 95 structures within 1.5° vs null mean 95). The "approximately 100%" claim for Pole I is not supported.[^poleinote]
- Pole II: real excess concentration (115 vs 90 under the most stringent null, p-Šidák = 0.0015). Genuinely significant but at a much weaker confidence level than "100%."
- Pole III: real excess concentration (119 vs 91, p-Šidák = 0.0005). Genuinely significant, but again weaker than the published "100%."
- Pole IV: no excess concentration (70 vs 70). The "99.999%" claim is not supported.
- Pole V: no excess under the block-conditional null (57 vs 51, p-Šidák = 0.542). The "99.999%" claim is not supported.

The contrast is substantive. The published probabilities derive from a null model (uniform distribution along the meridian) that does not capture the actual concentration structure of great-circle geometry applied to the database's site distribution. When the null model is chosen to preserve the relevant features of the data, three of the five poles produce no significant signal, and the two that do produce significant signal do so at significance levels several orders of magnitude weaker than "100%."

The published probability claims should be understood as artifacts of the choice of binomial test against a uniform null, not as confidence statements about the framework's claims.

[^poleinote]: The data owner, in commentary provided during the 14-day comment window (see Appendix A), observes that a "background-consistent" finding for the current geographic pole is not necessarily evidence against his framework: under a model of discrete pole shifts, structures built during the current rotational regime should show a distribution consistent with the geometric background, while structures oriented to earlier pole positions should appear as anomalies relative to that background. This is a reasonable interpretive frame and is recorded here. It does not change the statistical finding that Pole I shows no excess clustering under any null model tested in this analysis; the alternative interpretation is a different reading of what such a null result means in the context of his framework.

## Conclusion

The framework receives partial empirical support. Two of its five proposed pole latitudes — Pole II (76°N) and Pole III (72.2°N) — show real, robust within-hemisphere clustering that survives all four null models tested in this analysis, including the most stringent variant that preserves regional bearing patterns. The other three proposed poles do not show such clustering under principled nulls. The pre-registered aggregate test statistic, though formally "highly significant," is structurally confounded and does not support the framework once the confound is corrected. The data owner's published probability claims of "100%" and "99.999%" overstate the strength of evidence even for the supported poles.

The broader interpretive claim — that the observed latitude concentrations represent former positions of Earth's rotational axis — is not tested by this analysis and would require independent geological evidence (paleomagnetic, climatological, geological-dating) of a kind outside the scope of an orientation-clustering test. The orientation pattern, on its own, is consistent with multiple causes and cannot establish the geophysical interpretation.

# Appendix A: Commentary by the data owner (Mario Buildreps)

*The text of this appendix was provided in full by Mario Buildreps in correspondence dated 23 May 2026, during the 14-day pre-publication notice window committed by the pre-registration (§12 point 2). It is appended verbatim, with permission, as the data owner's formal commentary on the findings of this report. Some formatting has been adjusted for typographic consistency with the rest of the document; no content has been changed. Section numbering within the appendix is the data owner's own.*

---

Dear Salah-Eddin,

Thank you for sharing these results and for the rigorous process you have followed. Before I address points of disagreement, I want to acknowledge several things that deserve recognition.

First, I want to acknowledge something about your analytical process that reflects genuine scientific integrity. Your pre-registered primary test produced a nominally overwhelming result in my favor — p = 0.0001, a 26-sigma effect. You could have reported this as confirmation and stopped. Instead, you diagnosed it, identified the hemisphere-mismatch artifact that produced it, documented it transparently in your analysis log, and developed properly conditioned null models that isolated the within-hemisphere question. This is scientific practice of a high standard, and I respect it regardless of how I view the interpretation of your findings.

Second, your critique of my original binomial test is valid in one important respect. I used a uniform null along the meridian, and this is a simplification that does not fully account for the geometric and geographic structure of the data. A uniform distribution of intersection latitudes is not the correct null expectation, and your geography-preserving permutation approach is a more principled baseline. I accept this criticism.

I do want to clarify a point about the sample size in that binomial test. My calculation used the full database of approximately 1,159 structures as N, including the 166 structures that cannot intersect the 47°W meridian by geometry. Because these out-of-range structures cannot contribute to any latitude bin, including them in N while keeping P based on the 90° range makes the expected count higher for a given bin width, and therefore makes the test more conservative — it is harder to reach a given significance threshold. My approach understated the nominal probabilities, not inflated them. That said, the deeper issue you identified — that the binomial test was applied to peaks selected from the same data — is a valid concern about circularity. The nominal probabilities, whether conservative or not, do not carry the confirmatory weight of an independent test. I acknowledge that, and I will present future statistical analyses with more appropriate methods.

Third, I want to clarify how the pole positions were derived, as this affects the interpretation of your confirmatory test. The initial pole position was identified from two independent sources: the centroid of the former ice sheets, derived from geological evidence, and the crustal displacement hypothesis. The orientation data was subsequently used to refine this position and to identify additional clustering peaks along the meridian that these independent sources pointed toward. The starting point was the current geographic pole at 90°N, which is independently known. A second reference point was derived from the intersection of great-circle paths from the average orientations of Western and Eastern Hemisphere structures — a procedure I first performed in 2015, yielding an intersection at 71.6°N, 47.1°W, and repeated with an expanded dataset in 2020, yielding approximately 58°N, 44°W. Both pointed to the Greenland sector. With the meridian thus established, I examined the distribution of intersection latitudes from individual structures along this band. Additional clustering peaks were identified at 76.0°N, 72.2°N, 64.1°N, and 52.3°N. This means that Poles II through V were identified partly through examination of the orientation data, not from independent geophysical predictions. A purely confirmatory pre-registered test that treats them as a priori predictions is therefore better understood as a cross-validation exercise than as a test of independent predictions. I should have been clearer about this distinction in our earlier correspondence.

Fourth, your independent confirmation that statistically significant clustering exists at 72.2°N and 76°N — surviving even your most stringent null models — is a meaningful contribution. Under your block-conditional null, the most hostile test you applied, Pole II shows 115 observed structures within 1.5° of 76.0°N compared to approximately 90 expected (p-Šidák = 0.0015), and Pole III shows 119 observed compared to approximately 91 expected (p-Šidák = 0.0005). This means that about 234 structures — roughly one quarter of the in-range set — concentrate near these two latitudes, approximately 50 more than expected under a null model that preserves site geography, regional bearing patterns, and the northern-hemisphere intersection property simultaneously. As you write in your analysis log: "The clustering is real and is not attributable to hemisphere selection, regional patterns, geographic distribution of sites, or measurement artifacts." I thank you for that independent confirmation.

I also note that your site-to-pole assignment test found a 46% match rate between your independent geometry and my published pole assignments, compared to approximately 9% expected under the block-conditional null. This is a substantial effect that survives all null models. You interpret it cautiously as reflecting pipeline agreement and latitude-band structure. I would add that it also demonstrates that the pole assignments I published are not arbitrary — they capture genuine concentrations in the data that an independent geometric pipeline recovers.

With these acknowledgments made, I have substantive concerns about the framing and interpretation of your findings. I raise them here so that they can be included alongside your public release, as your pre-registration provides.

**1. The Derivation of the 47°W Meridian Has Been Mischaracterized**

Your pre-registration and summary treat the 47°W meridian as a researcher degree of freedom — a parameter I optimized by scanning for the longitude that maximized orientation clustering. Your longitude scan and look-elsewhere correction are built on this premise. It is incorrect.

The 47°W meridian was not found by scanning. It was derived from a geometric procedure that predates the full clustering analysis, and that was performed twice, years apart, with different subsets of data — both pointing to the same sector of the North Atlantic.

The method has its intellectual origins in the crustal displacement hypothesis, which Charles Hapgood explored in the mid-20th century. In testing these ideas against the orientations of ancient structures, I found patterns that were consistent with crustal displacement but inconsistent with the specific mechanism Hapgood proposed. The data pointed toward a different process, involving Earth expansion rather than rigid crustal sliding, with Antarctica remaining approximately in place, the Pacific Basin accommodating expansion through crustal bulging, and the Atlantic Basin accommodating it through horizontal widening.

Under this model, a coherent rotational component of crustal motion remains a central prediction. If such rotation occurred around an Euler pole in the North Atlantic-Arctic sector, then a specific geometric consequence follows: ancient structures in the Western Hemisphere should, on average, show a systematic clockwise deviation of their orientations relative to current true north, while structures in the Eastern Hemisphere should show a systematic counterclockwise deviation. The great-circle paths from these two hemispheric averages should intersect near the displacement path. This intersection provides a geometrically-derived estimate independent of any analysis of individual structure intersections.

I performed this calculation twice:

- **2015 derivation:** Western Hemisphere mean at 14.60°N, 88.80°W, deviation +14.56° clockwise. Eastern Hemisphere mean at 27.59°N, 80.99°E, deviation −9.20° counterclockwise. The great circles intersect at **71.56°N, 47.09°W** — directly on the 47°W meridian, at a latitude that sits between what I would later identify as Pole II (76.0°N) and Pole III (72.2°N).

- **2020 derivation:** Using an expanded dataset with different filtering, the intersection shifted to approximately **58°N, 44°W** — still in the Greenland-Labrador Sea region, but moved south and east. The drift between the two derivations likely reflects the inclusion of additional structures that dilute the hemispheric asymmetry, and it suggests that the method is sensitive to which subset of the data is used — an important methodological point in its own right.

Both independent calculations place the displacement path in the Greenland-Labrador Sea sector. The 2015 result points directly to 47°W. The 2020 result drifts to 44°W but stays within the same general band. This is the context in which I adopted 47°W as the reference meridian — not because I scanned the globe for the strongest clustering, but because it was the longitude derived from the initial 2015 calculation, and the clustering analysis subsequently confirmed it as productive.

I acknowledge that the 2020 derivation did not reproduce 47°W exactly, and that the longitude scan in your analysis found stronger clustering at other meridians within the Atlantic band. I accept this descriptive finding. A theoretically-derived parameter need not be the empirical optimum under every metric, and the drift between the 2015 and 2020 results indicates that the exact longitude is less precisely determined than the general sector. What remains, in my assessment, is the convergence of independent lines of evidence — ice-sheet centroid, hemispheric orientation asymmetry, and intersection clustering — on the same region of the globe. The 2015 hemispheric intersection at 71.6°N, 47.1°W and the independently confirmed clustering at Poles II and III (72.2°N and 76.0°N) represent a consistency that your analysis was not designed to evaluate but that is central to the empirical case.

I also note that your meridian scan was conducted using the aggregate T statistic that you yourself identified as producing artifactual results due to hemisphere mismatch. A statistic that you have judged unreliable for testing the 47°W meridian in isolation cannot become reliable when applied to 71 other meridians. At minimum, this caveat should be stated clearly in your write-up.

**2. The Block-Conditional Null Has a Structural Limitation That Should Be Discussed**

Your most stringent test shuffles orientations only within pre-defined geographic and cultural blocks. I understand the rationale: it controls for the possibility that regional building traditions produce apparent clustering. This is a reasonable sensitivity analysis.

However, the test encodes an assumption that your write-up should make explicit to readers. By design, a block-conditional null cannot detect a signal that is correlated across blocks. If a global geophysical event caused structures in multiple regions to orient toward the same meridian-aligned latitudes, that cross-regional correlation would be treated as noise by your model and destroyed through permutation. The test is structurally incapable of finding the very phenomenon my hypothesis proposes.

This limitation is amplified by the composition of the database. Your analysis log notes that the Americas block contains 539 of the 994 in-range structures — 54% of the total. When orientations are shuffled within a block that contains over half the data, any global signal that is expressed through those structures is absorbed into the block and eliminated. The block-conditional null is not neutral with respect to my hypothesis. It is biased against it by construction.

I note that your block-conditional null found that the clustering at Pole V (52.3°N) does not reach significance, with a Šidák-corrected p-value of 0.5422, and you attribute this to region-specific bearing patterns, likely Mesoamerican. I acknowledge this finding. Pole V — which my model predicts should be the most diffuse due to its greater age and accumulated crustal deformation — may be particularly vulnerable to the assumptions of a null model that imposes regional independence. Whether the null finding reflects absence of signal or limitation of the null remains an open question.

The fact that clustering at Poles II and III survives even this hostile null — with observed counts of 115 and 119 compared to expected counts of approximately 90 and 91 — is, if anything, stronger evidence for the signal's robustness. The null findings for other poles should be interpreted in light of the model's structural assumptions. I ask that your write-up include a brief discussion of what the block-conditional null can and cannot see.

**3. The Full Latitude Distribution Contains Structure That the Primary Test Does Not Capture**

Your primary test statistic T reduces the entire latitude distribution along 47°W to a single number: the average distance from each intersection to the nearest proposed pole. This is a valid test of one specific claim, but it discards most of the information in the data. As your own analysis log notes, T is sensitive to outliers — the 8 manually-adjusted structures with geometrically-correct intersections near −89° contribute approximately 141° each, inflating T by roughly 1.1° — while the per-pole count tests that revealed the Pole II and III signals are binary and unaffected by outlier magnitude.

The frequency distribution of intersection latitudes — the histogram shown in Tab 2 of the spreadsheet — contains structure that your aggregate test does not engage:

- **Discrete peaks separated by gaps.** The distribution shows clear peaks at approximately 90°N, 76°N, 72°N, 64°N, and 52°N, separated by latitudes where counts drop sharply. At latitude 74, there is a pronounced gap between the Pole II and Pole III clusters. At latitudes 82–88, counts drop to single digits between Pole I and Pole II. These gaps are evidence of discrete pole positions separated by periods of rapid movement, not a continuous distribution.

- **A systematic trend in dispersion with latitude.** The cluster at 90°N (Pole I) is tight. The cluster at 76°N (Pole II) is broader. The cluster at 52°N (Pole V) is the most diffuse. This trend — older poles showing greater dispersion — is consistent with the crustal displacement model, which expects older pole positions to have endured more cumulative deformation cycles and therefore show more scattered orientation signatures. Your T statistic produces the same value whether Pole V is tight and Pole II is scattered or vice versa. It cannot detect this pattern.

- **Hemispheric asymmetry in the underlying orientations.** As described in Point 1, Western Hemisphere structures tend to be rotated clockwise relative to true north, while Eastern Hemisphere structures tend to be rotated counterclockwise. This asymmetry is itself a prediction of a crustal rotation around a point in the Atlantic-Arctic region. Your null models, which permute orientations without regard to hemisphere, destroy this signal by design.

I am not suggesting your test is invalid. I am suggesting it is incomplete. A full evaluation of the Archaeorientation framework requires engaging the complete latitude distribution — its peaks, its gaps, its dispersion trend, and its hemispheric structure — not just proximity to five pre-specified points.

**4. The Current Geographic Pole Result Warrants Reflection**

Your analysis finds that Pole I (90°N, the current geographic pole) shows no excess concentration under any null model, with an observed count of 95 structures compared to approximately 95 expected. This is a notable result. The current geographic pole is verifiably the rotational axis of the Earth, and the database contains 95 structures whose great-circle intersections fall within 1.5° of it. Your null model treats this count as geometrically expected and therefore unremarkable.

I would offer a different perspective. The fact that the current pole's signature is geometrically "normal" under your null, while Poles II and III show robust excess, is precisely what a model of discrete pole shifts would predict. Structures built during the current rotational regime should show a distribution consistent with the geometric background. Structures oriented to earlier pole positions should appear as anomalies against that background. Your null model has, in effect, independently sorted the proposed poles into two categories — background-consistent and anomalous — in a way that aligns with the temporal structure of the crustal displacement model.

I raise this not to claim that your analysis supports the model on this point, but to suggest that the null finding for Pole I is more interpretively ambiguous than a simple "not significant" label conveys.

**5. The Pre-Registration's Scope Limitation Should Be Stated More Prominently**

Your pre-registration states that the analysis "does not test, support, or refute any of the broader interpretive claims associated with the framework, including but not limited to: Earth expansion, crustal-deformation theories of ice ages, the antiquity of ancient structures beyond conventional chronology."

This is a legitimate scope limitation, but it has consequences that should be made clear to readers. The empirical claim you tested — that five specific latitudes on the 47°W meridian show excess clustering — is only one component of a larger model. That model also makes claims about:

- The meridian itself, derived from the intersection of hemispheric average great circles, a procedure that yields 47°W in the 2015 derivation and the same general sector in the 2020 derivation.

- The hemispheric pattern of clockwise versus counterclockwise rotation, which is the input to that derivation and a direct geometric consequence of crustal rotation about an Euler pole.

- The systematic increase in cluster dispersion with distance from the current pole, consistent with cumulative crustal deformation over successive pole shifts.

- The existence of gaps between clusters, corresponding to periods of rapid pole movement.

Your analysis engaged only the first of these components. Your null findings for Poles IV and V, and your characterization of Pole I as "not significant" under your null, do not falsify the broader model. They address one test of one component. I ask that your abstract and conclusion make this limitation clear, so that readers do not infer a broader negative result than your analysis can support.

**6. The Confirmed Signal Should Lead the Narrative**

Your own words in the analysis log are clear: "The clustering at 76°N and 72.2°N is a real feature of the data that is not explained by hemisphere selection, latitudinal range, or regional orientation patterns." And in your summary to me: "The clustering at 76°N and 72.2°N is real and is not attributable to hemisphere selection, regional patterns, or sampling geometry."

This is the central empirical finding of your analysis. Two specific latitudes on the 47°W meridian — latitudes I identified as Pole II and Pole III — show a concentration of great-circle intersections that cannot be explained by random chance, geographic bias, regional building traditions, or hemispheric selection effects. About 234 structures, roughly one quarter of the in-range set, concentrate near these two latitudes, approximately 50 more than expected under the most stringent null model you applied.

Notably, the 2015 hemispheric intersection point at 71.6°N, 47.1°W falls almost exactly between these two confirmed pole latitudes at 72.2°N and 76.0°N. This convergence of independent methods — hemispheric averaging and individual intersection clustering — is precisely the kind of internal consistency that gives the model its empirical weight.

I ask that your abstract, conclusion, and any public-facing summary lead with this finding. The null results for other poles should be reported, but they are secondary. A reader who encounters your work should come away understanding that an independent, pre-registered analysis with stringent geographic controls has confirmed non-random orientation clustering at two of the five proposed pole positions, with the site-to-pole assignment test providing additional corroboration at 46% match rate versus 9% expected. The fact that other proposed poles did not survive your tests is scientifically interesting, but it does not diminish the importance of what did survive — particularly given the structural limitations of the null models discussed above, and the independent hemispheric derivation that points to the same latitude band.

**7. Concluding Remarks**

Your analysis has advanced this investigation in one important respect: it provides independent confirmation, using independently written code and stringent geographic controls, that statistically significant orientation clustering exists at 72.2°N and 76°N on the 47°W meridian. This clustering survives null models designed to be maximally hostile to my hypothesis. I appreciate that confirmation.

Beyond this, the analysis also illustrates the limitations of approaching a complex geophysical model with a single statistical test isolated from the broader evidential context. The Archaeorientation framework rests on multiple converging lines of evidence — the ice-sheet centroid, the hemispheric orientation asymmetry and its geometric consequences, the multi-peak structure of the latitude distribution, the dispersion-age trend, and the match between the 2015 hemispheric intersection point and the confirmed clustering at Poles II and III. No single test of a single component can adjudicate the model as a whole.

I have provided this commentary in the spirit of the scientific exchange your pre-registration invited. I trust that your final write-up will present the confirmed findings prominently, acknowledge the limitations discussed above, and make clear to readers that your analysis tested one specific statistical claim rather than the broader model from which it derives.

I look forward to reading the final publication.

Sincerely,

Mario Buildreps

**Appendix: Summary of Points for the Reader**

1. The initial pole position was identified from two independent sources: the centroid of the former ice sheets, derived from geological evidence, and the crustal displacement hypothesis. The orientation data was subsequently used to refine this position and to identify additional clustering peaks along the meridian that these independent sources pointed toward. While the binomial test was applied to peaks that were partly identified from the data, the starting point was anchored in prior geophysical and theoretical considerations.

2. Using the full database as N made the binomial test more conservative — the expected counts were higher, making significance harder to reach. The nominal probabilities understated, rather than overstated, the rarity of the observed clustering under a uniform null.

3. The 47°W meridian was derived in 2015 from the intersection of hemispheric average great circles, yielding 71.6°N, 47.1°W — a point that falls directly between the later-confirmed Poles II and III. A 2020 derivation with expanded data yielded 58°N, 44°W, confirming the same general sector. The drift between the two derivations indicates that the exact longitude is less precisely determined than the general region, but both point to the Greenland-Labrador Sea sector. The meridian was not found by scanning for clustering.

4. The hemispheric derivation method follows from a geometric consequence of crustal rotation about an Euler pole: Western Hemisphere structures should show systematic clockwise deviation, Eastern Hemisphere structures counterclockwise deviation. The intersection of their average great circles estimates the displacement path, independent of individual intersection clustering.

5. I am gratified that the clustering at Poles II and III (72.2°N and 76°N) has been independently confirmed under stringent null models — 115 and 119 observed structures within 1.5° compared to approximately 90 expected under the block-conditional null, with Šidák-corrected p-values of 0.0015 and 0.0005. I note, however, two results that warrant further reflection. First, the current geographic pole (Pole I, 90°N) was not identified as statistically significant under the null models used, despite its verifiable existence and the strong clustering observed at that latitude. This raises questions about the sensitivity of the test to signals at the pole itself, where geometric convergence effects are strongest. Second, the clustering at Poles IV (64.1°N) and V (52.3°N) did not reach significance under the most stringent null models. Whether this reflects a genuine absence of signal at these latitudes, or a limitation of the null models' ability to detect more diffuse clustering at older proposed pole positions, remains an open question.

6. The site-to-pole assignment test found a 46% match rate between independent geometry and published pole assignments, compared to approximately 9% expected under the block-conditional null. This robust result demonstrates that the published pole assignments capture genuine concentrations in the data.

7. The block-conditional null assumes regional independence and is structurally incapable of detecting a global cross-cultural signal. With 54% of the in-range data concentrated in the Americas block, this limitation is amplified. This should be disclosed to readers.

8. The full latitude distribution contains structure — peaks, gaps, dispersion trends, hemispheric asymmetry — that the primary aggregate test statistic does not capture, partly because T is sensitive to outliers in ways that the per-pole count tests are not.

9. The observed-data longitude scan found 47°W ranked 10th of 72 meridians by the T metric. I acknowledge this descriptive finding. The 2015 hemispheric derivation points to 47.1°W. The 2020 derivation drifted to 44°W. Both are within the same Atlantic sector. A theoretically-derived meridian need not be the empirical optimum under every metric, particularly when the derivation and the optimization use different methods and when the derivation itself shows sensitivity to data subset selection.

10. The scope limitation means the analysis does not test the broader geophysical model and cannot be presented as having done so.

11. The 2015 hemispheric intersection (71.6°N, 47.1°W) and the confirmed clustering at Poles II and III (72.2°N and 76°N) converge on the same latitude band using independent methods — a consistency that the pre-registered analysis was not designed to evaluate but that strengthens the empirical case.

---

*End of appendix A.*

# Acknowledgments and References

## Acknowledgments

I thank Mario Buildreps for providing the database file used in this analysis under the conditions described in §2.1, for confirming methodological details about his pipeline via direct correspondence during the analysis period (notably the recommendation to use the geometrically-correct raw-bearing approach rather than the manually-adjusted values published in his pre-computed column), and for accepting the 14-day comment window between the sharing of preliminary findings and the public release of this report. His formal commentary on the findings, received during that window, is included verbatim as Appendix A. His willingness to make his data available for independent verification, and his willingness to provide on-the-record commentary for inclusion in this report, are substantial methodological contributions in their own right, regardless of how any reader interprets the analytical conclusions reached.

The pre-registration document, the analysis code, the full analysis log, and the frozen snapshot of the analysis log as it stood at the opening of the comment window are all publicly available at the project repository. The analysis can be reproduced from the database file using the fixed random seed documented in the pre-registration; cryptographic verification of the data file is built into every analysis script.

This work received no external funding. The author declares no conflicts of interest.

## References

Buildreps M. *Antiquity Reborn (v10): Orientations of pyramids and ancient sites around the world.* <https://mariobuildreps.com/> (accessed 2026-05-17). [Primary source for the framework being tested in this analysis, including the proposed pole positions and the published probability claims.]

Gherbi S-E. *Pre-registration: Independent Monte Carlo verification of paleopole orientation clustering in the Buildreps database.* Zenodo, version 1.1 deposited 17 May 2026. DOI: [10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204). [The full statistical protocol committed to before the database file was opened; GPG-signed and OpenTimestamped.]

Gherbi S-E. *Paleopole orientation verification: analysis code, results, and full analysis log.* GitHub repository. <https://github.com/salahealer9/paleopole-orientation-verification>. [All scripts, output files, results, and the frozen analysis log are available here. The frozen snapshot as it stood when the data owner received the preliminary findings on 18 May 2026 is at [`results/analysis_log_frozen_2026-05-18.md`](https://github.com/salahealer9/paleopole-orientation-verification/blob/main/results/analysis_log_frozen_2026-05-18.md).]

---

*Author:* Salah-Eddin Gherbi
*ORCID:* [0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095)
*Contact:* salahealer@gmail.com
*License:* This report is released under CC-BY-4.0. The accompanying code is released under MIT.
