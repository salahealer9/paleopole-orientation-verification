# Background

The independent researcher Mario Buildreps has assembled, over the past decade, a database of approximately 1,159 ancient pyramids, temples, and megalithic structures worldwide, recording each site's geographic coordinates and the orientation of its principal architectural axis relative to current true north. From this database he proposes a claim that has attracted public attention but no formal independent statistical verification: that the orientations of these ancient structures cluster around five proposed pole positions located along the ~47°W meridian, which he interprets as past positions of Earth's rotational axis. The proposed pole latitudes are 76.0°N, 72.2°N, 64.1°N, and 52.3°N (designated Poles II through V), together with the current geographic pole at 90°N (Pole I). A sixth candidate position at 42.0°N (Pole VI) is described in the framework as "out of scope," excluded from his published probability calculations; the framework notes that including it would weaken those calculations.

The framework's published probability statements — approximately 100% certainty for Poles I–III and approximately 99.999% for Poles IV–V — derive from a binomial test against a uniform null distribution along the 47°W meridian. The bin widths used in this test are non-uniform (between 3° and 10°) and are positioned to capture observed concentrations; the framework characterises this binning scheme as "Dynamical Grouping" in the published methodology. These features of the methodology — the choice of meridian, the choice of null distribution, and the choice of bin widths — were identified prior to the data being opened as candidates for independent re-analysis with a more carefully specified null model.

This report presents the results of that independent re-analysis. The full statistical protocol was pre-registered on Zenodo on 17 May 2026, GPG-signed, and OpenTimestamped on the Bitcoin blockchain before the database file was opened. The SHA-256 hash of the database file is recorded in the pre-registration and verified at the start of every analysis script, ensuring that the analysis can only legitimately be run against the exact file the protocol was written against. The pre-registration commits the analysis to a Monte Carlo null model that preserves site geography and the empirical bearing distribution, with binning-free test statistics, multiple sensitivity analyses, and the explicit pre-commitment that all results will be reported regardless of outcome.

**Version note (v3).** This is version 3 of this report. Version 2 (deposited 1 June 2026) reported a preliminary positive result: apparent clustering at Poles II and III that survived the pre-registered and conditional null models. Post-publication review identified two independence controls that version had not applied — a latitude look-elsewhere correction and a control for spatial non-independence of structures. Three additional analyses were run to apply them (scripts `07`–`10` in the repository: latitude look-elsewhere, finer-block sensitivity, and a spatial-cluster null). They overturn the preliminary positive; the corrected conclusion is reported here. Version 2 remains available as a prior version of this Zenodo record; the pre-registered and v2 analyses themselves are unchanged. The new analyses are presented in §3.8 and their relationship to v2 is set out in Appendix B. Per pre-registration §12 point 3, all three are labelled exploratory. Version 3.1 (this version) responds to the data owner's 5 June 2026 follow-up: it foregrounds the spatial-cluster null's central caveat beside the result (§3.8), presents the pre-registered and exploratory findings side by side (§3.7), reproduces his letter verbatim (Appendix D), and notes two empirical analyses now under way in response. The analytic conclusion is unchanged.

This is not a test of the broader interpretive framework. The Earth-expansion hypothesis, the proposed timeline of human prehistory, the geological mechanism of crustal deformation, and the climatological claims that surround the orientation-clustering observation are all outside the scope of this report. What is tested here is one narrow, falsifiable empirical claim: that the orientations of ancient structures in the database point at the five proposed pole positions more than expected under random orientations applied to the same geographic distribution of sites. That claim is statistical, not historical or geological, and a statistical analysis is sufficient to evaluate it.

The data owner provided the database under the explicit condition that the raw file not be redistributed, but with the freedom to share analytical results, code, and conclusions publicly. He has been informed of the findings reported here and was given a 14-day comment window before public release, per the pre-registration's transparency commitments. His responses, where they bear on the analysis, are noted in the relevant sections.

The principal finding of this report, summarised here so that the reader can keep the conclusion in mind while reading the methods, is a null result at every proposed pole once controls for look-elsewhere multiplicity and spatial non-independence are applied. The aggregate "primary" test statistic specified in the pre-registration showed an apparently extreme significance (p = 0.0001, more than 26 standard deviations) that turned out, on diagnostic investigation, to be an artifact of the null model's interaction with the data owner's pre-existing northern-hemisphere classification of in-range structures; under properly conditioned null models the aggregate signal disappears. Two of the five proposed latitudes — Pole II (76°N) and Pole III (72.2°N) — initially appeared to retain per-pole clustering that survived even the block-conditional null, and an earlier version of this report (v2) characterised that clustering as robust. Two controls identified in post-publication review remove it. First, the per-pole test treated five latitudes as a priori targets, whereas the data owner states (Appendix A) that Poles II–V were identified partly by examination of the orientation data; a latitude look-elsewhere correction — the analogue of the meridian correction already in the protocol — removes Pole II, and under the assumption-free global conditional null removes Pole III as well. Second, the block-conditional null treated spatially autocorrelated structures as independent; a spatial-cluster null that collapses nearby sites to one independent unit each reduces the apparent Pole III concentration from 119 structures at the site level to 25 independent clusters, a count statistically indistinguishable from the null (p = 1.0 with the look-elsewhere correction, stable across linkage thresholds from 25 to 100 km). The largest single contributor was one 29-site cluster in the northern Yucatán that had entered the site-level count as 29 independent observations. With both controls applied, no proposed pole shows clustering distinguishable from chance. The full reasoning, including the v2 per-pole results as originally found, is in §3 and §4 below.

The framework's narrow statistical claim is therefore not supported by this analysis. Under null models that control for both the look-elsewhere freedom in the choice of target latitudes and the spatial non-independence of structures, the orientations in the database do not point at the five proposed pole positions more than expected from great-circle geometry applied to the same geographic distribution of sites. The broader interpretive claim — that these latitudes correspond to former geographic pole positions — is not tested here and, as set out below, cannot be established by an orientation-clustering analysis in any case; nothing in this report bears on it either way, except to withdraw the statistical clustering that had been offered as its evidence.

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

**Latitude look-elsewhere (post-publication, exploratory).** The same multiplicity argument applies to the choice of target *latitudes*, not only to the meridian. The five proposed pole latitudes were not points fixed before the data were seen: the data owner states (Appendix A) that Poles II–V were identified partly by examining the orientation distribution. Counting structures near five such data-derived latitudes therefore carries the same look-elsewhere burden the protocol already recognised for the meridian, and the Šidák correction over five poles (§2.8) does not address it — it corrects for five comparisons, not for a continuous latitude axis from which the fullest windows were chosen. Script `07` supplies the missing control as the direct analogue of the §10 meridian scan: it slides a ±1.5° window across the populated northern range (45°–89°N at 0.25° steps) and, for each Monte Carlo iteration, records the *maximum* structure count in any window. The look-elsewhere-corrected p-value for a given pole is the fraction of null iterations whose maximum window count anywhere equals or exceeds the count observed at that pole — that is, how often the null produces a concentration as tight as the proposed pole *somewhere* along the latitude axis. The control is run under each null model; results are in §3.8. Per pre-registration §12 point 3 it is labelled exploratory.

## Per-pole confirmatory and site-to-pole assignment (pre-registered §11(a, b))

Two pre-registered confirmatory tests address the framework's specific predictions.

The per-pole confirmatory test (§11(a)) counts, for each proposed pole separately, the number of structures whose independent intersection latitude falls within ±1.5° of the pole's latitude. The pre-registered comparison is against the null distribution of the same count under permuted bearings, with Šidák correction (an adjustment for the increased chance of false-positive significance when running multiple tests simultaneously) across the five (or six) simultaneous tests at family-wise α = 0.05.

The site-to-pole assignment test (§11(b)) is a stronger test of the framework's specific predictions: rather than asking "do the bearings cluster at any of the poles," it asks "do the bearings cluster at the *specific* poles assigned to each site." The pre-registration anticipated an explicit assignment table; inspection of the database file (and of the other sheets within it) found no such per-site assignment column. The assignment is therefore operationalized as the nearest of the proposed poles to each structure's data-owner-published intersection latitude — i.e., we let the data owner's own pipeline output define the implicit assignment. The test then asks whether our independent geometry confirms the assignment within ±1.5° more often than expected under random permutation. This methodological decision is documented in the analysis log.

Both tests are run under all four null models described above (pre-registered unconditional + exploratory conditional + pre-registered block-unconditional + pre-registered block-conditional), giving a comprehensive picture of which signals are robust and which are not.

**Two caveats to the per-pole test, addressed post-publication.** As pre-registered, the per-pole test treats the five pole latitudes as fixed targets and the 994 structures as independent observations. Neither assumption holds without qualification, and version 3 adds a control for each.

*(i) Data-derived targets.* As noted in §2.7, Poles II–V were identified partly from the orientation data (Appendix A). The latitude look-elsewhere control of script `07` corrects the per-pole counts for this freedom; it is the latitude analogue of the meridian correction the protocol already specified.

*(ii) Non-independent observations.* The block-conditional null (§2.6) permutes bearings within coarse geographic blocks, the largest of which — the Americas (n = 539) — contains dense clusters of structures from single architectural traditions whose orientations are strongly correlated. Treating such structures as exchangeable over-disperses the null and can inflate per-pole significance, a form of pseudoreplication. Two post-publication analyses bracket this. A finer-block sensitivity analysis (scripts `08`, `09`) subdivides the dominant blocks along documented latitude/longitude bands and re-runs the per-pole test, with and without the latitude look-elsewhere correction, across a gradient of block granularity. A spatial-cluster null (script `10`) goes further: it collapses sites lying within a fixed great-circle distance of one another (single-linkage; thresholds of 25–100 km) into one representative each — the member nearest the cluster centroid, using its raw coordinates and bearing — so that the effective sample becomes the number of spatially independent units. It then asks how many *clusters*, rather than sites, point within ±1.5° of a pole, under the conditional null and with the latitude look-elsewhere correction applied. All three post-publication analyses are labelled exploratory per pre-registration §12 point 3; their results, and the diagnostic that motivated the cluster null, are in §3.8.

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

- **Within the four null models reported in this section, the apparent signals are at Poles II and III.** Approximately 234 structures (24% of the in-range set) point at intersections near these two latitudes, ~50 more than expected under the block-conditional null. This excess survives all four null models reported above, including the block-conditional null that preserves regional bearing patterns within seven coarse geographic blocks.

*[v3 — superseded.] This was the central positive finding of version 2. It does not survive the two further controls reported in §3.8. A latitude look-elsewhere correction — the analogue of the meridian correction already in the protocol — removes Pole II, and under the assumption-free conditional null removes Pole III as well; the per-pole test above treats five data-derived latitudes (Appendix A) as a priori targets, which the Šidák correction does not address. A spatial-cluster null then shows that the residual surviving the block-conditional null is an artifact of treating spatially autocorrelated structures as independent: the block-conditional null preserves regional bearing patterns but still counts the 539 structures within a region as 539 independent observations. The paragraph above is retained as the result as version 2 found it; the corrected conclusion is in §3.8 and §4.*

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

*[v3.] Because the assignment test conflates these two real but mundane features — agreement between our geometry and the data owner's pipeline (within 0.1° for 95.7% of structures), and the within-hemisphere concentration of intersections — it is not independent evidence for the proposed poles. It receives neither a look-elsewhere correction nor an independence (cluster-level) control, and it would remain at p = 0.0001 under the §3.8 reanalysis for the same two reasons it is significant here, not because any pole survives. It carries no weight in the version 3 conclusion and is retained for completeness and continuity with version 2.*

## Summary of all tests

The complete set of pre-registered and exploratory tests is summarised in the table below. The "Status" column distinguishes pre-registered confirmatory tests (which can support or fail to support pre-registered hypotheses) from exploratory tests (which provide methodological diagnostic information but cannot make confirmatory claims, per pre-registration §12 point 3).

| Test | Section | Status | p-value | Interpretation |
|---|---|---|---|---|
| Primary T, unconditional null | §7 | Pre-registered | 0.0001 | Significant by hemisphere-mismatch artifact |
| Primary T, conditional null | (added) | Exploratory | 0.9989 | Observed less concentrated than null |
| Look-elsewhere, unconditional | §10 | Pre-registered | 0.0001 | Same artifact; descriptive: 47°W is rank 10/72 |
| §11(a) per-pole, unconditional | §11(a) | Pre-registered | all p < 0.003 | All five "significant" by artifact |
| §11(a) per-pole, conditional | (added) | Exploratory | II, III: 0.0005; V: 0.044 | II, III significant; V marginal; I, IV null — superseded, see §3.8 |
| §11(a) per-pole, block-conditional | §11(d) | Pre-registered | II: 0.0015; III: 0.0005 | II, III significant under this null; V eliminated — superseded, see §3.8 |
| §11(b) assignment, unconditional | §11(b) | Pre-registered | 0.0001 | Partly artifact, partly genuine |
| §11(b) assignment, conditional | (added) | Exploratory | 0.0001 | ~45σ effect: pipeline agreement + concentration, not poles (§3.6) |
| §11(b) assignment, block-conditional | §11(d) | Pre-registered | 0.0001 | Robust to regional patterns; not evidence for poles (§3.6) |
| §11(a) per-pole + latitude look-elsewhere (07) | §3.8 | Exploratory | cond.: II 0.999, III 0.90; block-cond.: II 0.0043, III 0.0003 | Under the assumption-free conditional null, II and III vanish once latitude multiplicity is corrected |
| §11(a) per-pole, finer blocks (08, 09) | §3.8 | Exploratory | block-cond., coarse→fine: II 0.0010→0.057; III 0.0005→0.003 | Significance erodes as the Americas block is subdivided |
| Spatial-cluster null, +LEE (10) | §3.8 | Exploratory | II & III: 1.000 (25–100 km) | No pole distinguishable from chance when nearby structures are treated as one unit |

Taken at face value, the pre-registered unconditional rows tell one story — the framework's clustering claim is confirmed across every test — but §3.2 shows that story is a hemisphere-selection artifact. The conditional and block-conditional rows tell a more specific one, and were the basis of version 2: the aggregate statistic is null, clustering at Poles I, IV and V is absent, and clustering at Poles II and III appears robust under the block-conditional null. The three post-publication rows (§3.8) revise that last point. The per-pole significance at Poles II and III does not survive a latitude look-elsewhere correction under the assumption-free conditional null, erodes as the dominant geographic block is subdivided, and disappears entirely under a spatial-cluster null that treats spatially autocorrelated structures as single units. The corrected conclusion is that no proposed pole shows clustering distinguishable from chance. The assignment test remains significant under every null but measures agreement between our geometry and the data owner's pipeline together with the within-hemisphere concentration of intersections, not the pole positions (§3.6). Interpretation of these results is the subject of §4.

**Pre-registered versus exploratory findings, weighed side by side.** Because the conclusion rests on exploratory analyses while the pre-registered confirmatory tests at Poles II and III returned significance, the two are set out together here so the reader can weigh them directly:

| Analysis | Pole II | Pole III | Status | Identified caveat |
|---|---|---|---|---|
| Block-conditional null + Šidák (§11(d)) | 0.0015 | 0.0005 | Pre-registered | Counts spatially autocorrelated structures as independent (pseudoreplication) |
| Block-conditional + latitude LEE | 0.0043 | 0.0003 | Exploratory | Same pseudoreplication limitation |
| Assumption-free conditional null + latitude LEE | 0.999 | 0.90 | Exploratory | No block-independence assumption |
| Spatial-cluster null + LEE | 1.000 | 1.000 | Exploratory | Proximity-as-independence assumption (§3.8) |

The pre-registered confirmatory tests at Poles II and III are significant; the conclusion that no pole survives rests on the exploratory controls. This report weights the exploratory controls as decisive not because they are newer but because the pre-registered block-conditional null is now known to contain a specific, identified flaw — it counts spatially autocorrelated structures as independent — that the exploratory controls were built to remove. Pre-registration certifies that an analysis was not tuned to the data after the fact; it does not certify that the chosen null model was correct, and a registered test with a since-identified flaw does not override the analysis that identified the flaw. Two further points bear on how the controls accumulated. First, they moved in one direction — toward the null — because each corrected an assumption that biased significance *upward* (look-elsewhere multiplicity, then spatial non-independence); correcting upward-biased errors necessarily moves the result one way, and no symmetric "loosening" control exists that raises sensitivity to a real signal without also admitting false positives. Second, not every control was capable only of tightening: the finer-block analysis (script 09) was specified so that a rise in Pole III's significance under finer blocking would have been reported as a surviving residual — it was a gate that could have exonerated the pole, and did not. A reader who weights pre-registration status above the identified flaw may reasonably place more confidence in the block-conditional result than this report does; the numbers for every analysis are above, and the data owner's dissent on exactly this weighting is recorded verbatim in Appendix D.

## Post-publication controls: latitude look-elsewhere and spatial independence

The per-pole result of §3.5 — apparent clustering at Poles II and III surviving the block-conditional null — was the positive finding of version 2. Post-publication review (see Appendix C for the reviewer's own summary of the gaps identified and the predictions made) identified two assumptions that result rested on and that none of the four null models above had tested: that the five pole latitudes were targets fixed before the data were seen, and that the 994 structures are independent observations. This section reports four analyses (scripts `07`–`10`) that relax those assumptions. All are labelled exploratory per pre-registration §12 point 3: their role is to apply controls the confirmatory tests did not, not to introduce new confirmatory claims. The result is that, with both controls applied, no proposed pole shows clustering distinguishable from chance.

### Latitude look-elsewhere (script 07)

The §10 longitude scan corrected for the freedom in the choice of *meridian*. The same correction is required for the choice of *latitude*, because Poles II–V were identified partly from the orientation data (Appendix A) rather than predicted a priori. Script `07` slides a ±1.5° window across the populated northern range (45°–89°N, 0.25° steps) and records, for each null iteration, the maximum structure count in any window; the look-elsewhere-corrected p-value for a pole is the fraction of iterations whose maximum window count anywhere matches or exceeds the observed count at that pole. The observed peak is 119 structures, at 72.0°N; the result is identical whether the near-pole convergence region (90°N) is included or excluded from the scan.

| Null model | Null T_max mean | p (any window) | p (Pole II = 115) | p (Pole III = 119) |
|---|---|---|---|---|
| Unconditional | 93.3 | 0.0001 | 0.0001 | 0.0001 |
| Conditional (within-hemisphere) | 121.2 | 0.9048 | 0.9989 | 0.9048 |
| Block-conditional | 110.4 | 0.0003 | 0.0043 | 0.0003 |

The decisive row is the conditional null — the one that imposes the within-hemisphere property established as necessary in §3.2, but makes no further assumption. Under it, the null's maximum window count anywhere averages 121, slightly *above* the observed peak of 119: free reshuffling of the hemisphere-compatible bearings produces a fuller window somewhere along the latitude axis more often than not. Once the freedom to choose which latitude to call a pole is accounted for, the observed concentration is not merely non-significant but slightly below typical (p_II = 0.999, p_III = 0.90). The block-conditional null still returns small p-values (p_II = 0.0043, p_III = 0.0003); the discrepancy between the two — significant under the block null, null under the assumption-free global null — is what the independence controls below resolve.

### Finer-block sensitivity (scripts 08 and 09)

The block-conditional null shuffles bearings within seven coarse blocks, the largest being the Americas (n = 539). If a dense cluster of structures from one architectural tradition shares an orientation convention, shuffling those bearings freely across the whole block treats correlated structures as independent and over-disperses the null, inflating significance. Script `08` re-runs the per-pole test at three granularities; script `09` repeats it with the latitude look-elsewhere correction of `07` applied under each. The `coarse` scheme reproduces §3.5 / the block-conditional column of `07` within Monte Carlo error, validating the implementation.

| Scheme | Blocks | Pole II null mean → p-Šidák | Pole III null mean → p-Šidák | Pole III, +LEE |
|---|---|---|---|---|
| coarse | 8 | 90.2 → 0.0010 | 90.8 → 0.0005 | 0.0001 |
| americas_split | 10 | 100.8 → 0.0452 | 100.1 → 0.0080 | 0.0122 |
| fine | 12 | 101.8 → 0.0571 | 99.5 → 0.0030 | 0.0108 |

As the Americas block is subdivided (into North America, Mesoamerica, and the Andes/South America by latitude), the per-pole null mean rises from ~90 to ~100 — the over-dispersion made quantitative. Pole II crosses out of significance (0.0010 → 0.057). Pole III weakens roughly six-fold but holds as a residual near 0.003–0.011. The `fine` step (which further split the Middle East and Europe) barely moved Pole III, for a diagnostic reason: it did not subdivide the block where Pole III's contributors lie. Of the 119 structures within ±1.5° of 72.2°N, 64 (54%) fall in a single un-subdivided block, `Am:Mesoamerica` (n = 371). The finer-block analysis had not yet reached the relevant population, which motivated the spatial-cluster null below.

### Spatial-cluster null (script 10)

To control for non-independence directly, script `10` collapses structures lying within a fixed great-circle distance of one another (single-linkage connected components) into one representative each — the member nearest the cluster centroid, retaining its raw coordinates and bearing — so that the effective sample becomes the number of spatially independent units. It then asks how many *clusters* point within ±1.5° of a pole, under the conditional null and with the latitude look-elsewhere correction. The distance threshold is swept from 25 to 100 km.

| Threshold | Clusters | Largest | Pole III (clusters) | Pole III p (per-pole) | Pole III p (+LEE) |
|---|---|---|---|---|---|
| 25 km | 286 | 64 | 25 | 0.136 | 1.000 |
| 50 km | 210 | 64 | 17 | 0.314 | 1.000 |
| 75 km | 173 | 101 | 13 | 0.491 | 1.000 |
| 100 km | 144 | 244 | 10 | 0.410 | 1.000 |

Pole III is non-significant at every threshold even without the look-elsewhere correction (per-pole p = 0.14–0.49), and with it the p-value is 1.0 throughout — the null's maximum window count routinely exceeds the observed cluster count. Pole II behaves identically (per-pole p = 0.010–0.20; +LEE p = 1.0 at all thresholds). The verdict is stable as the largest cluster grows from 64 to 244 sites, so single-linkage chaining is not driving it.

The cluster collapse also locates the source of the v2 signal precisely. At 25 km (minimal merging, the most conservative reading), the 119 site-level contributors to the Pole III window correspond to 25 independent clusters containing 106 sites. Five of those clusters are Mesoamerican, carrying 42 of the 106 sites — including the single largest contributor, one 29-site cluster in the northern Yucatán (≈20.3°N, 89.6°W) that had entered the site-level count as 29 independent observations. With one further American (Andean) cluster of 12 coastal sites, the Americas supply roughly half the underlying sites (54 of 106) but only a quarter of the independent clusters (6 of 25); the remaining nineteen are small, one-to-six-site groups scattered across the Mediterranean, Middle East, and Europe. The site-level concentration was dense-cluster replication, chiefly American; reduced to independent units, the clusters are a multi-region scatter indistinguishable from the null.

**A caveat on the cluster null's central assumption, stated here beside the result.** The spatial-cluster null treats geographic proximity as a proxy for non-independence: structures within the linkage distance are collapsed into one unit. This is correct if nearby structures of a shared tradition inherited a common orientation convention. It is contestable in one specific way that the framework under test explicitly raises. A global geophysical event of the kind the framework proposes would cause structures built in the same region at *different* times by *different* cultures to point toward the same latitude band; such structures would be genuinely independent observations, yet the cluster null would merge them and discard the signal. The database carries no culture or date labels, so the analysis cannot, from its own contents, distinguish "29 structures of one tradition replicating one convention" from "29 structures of several periods independently converging on one orientation." The first makes the cluster null correct; the second would make it over-conservative. This is an empirical question about the 29-site northern-Yucatán cluster that dominates the Pole III count, and it is answerable from published Maya chronology. That check, together with a Monte Carlo simulation of the framework's own stated peak-finding rules (which addresses a parallel objection to the latitude look-elsewhere control), is in progress and will be reported in a subsequent version; both are described in the author's note to Appendix D. The synthesis below holds under the cluster null's independence assumption; the assumption itself is now under test.

### Synthesis

The two controls resolve the discrepancy noted in §3.8.1. The assumption-free global conditional null saw no concentration (p_III = 0.90); the block-conditional null returned significance; the spatial-cluster null — which removes the independence assumption directly rather than approximating it through geographic blocks — confirms the global null. The block-conditional significance was manufactured by treating spatially autocorrelated structures as independent, and it erodes monotonically as that assumption is relaxed (coarse blocks → finer blocks → spatial clusters). With both the latitude look-elsewhere correction and a control for spatial non-independence applied, no proposed pole — including Poles II and III — shows clustering distinguishable from chance. This withdraws the central positive finding of version 2. It does not bear on the framework's geophysical interpretation, which an orientation-clustering analysis cannot test in any case (§4); it removes the statistical clustering that had been offered as that interpretation's evidence.

# Discussion

## What the data shows

Setting aside interpretation for a moment, the empirical observations from §3 can be stated as follows:

- At the site level, intersection latitudes on the 47°W meridian show an apparent concentration at two of the five proposed pole latitudes — Pole II (76.0°N) and Pole III (72.2°N): about 234 structures (24% of the sample) fall within ±1.5° of these two latitudes, and this excess survives all four null models of §3.5. It does not, however, survive the two controls of §3.8. Once the data-derived choice of target latitude is corrected for, the assumption-free conditional null produces a window as full somewhere along the latitude axis more often than not (Pole II p = 0.999, Pole III p = 0.90). Once spatially autocorrelated structures are collapsed to one unit each, the concentration is indistinguishable from chance at every distance threshold from 25 to 100 km (p = 1.0 with the look-elsewhere correction). Reduced to independent units, the 119 site-level contributors to the Pole III window become 25 clusters, the largest a single 29-site Mesoamerican cluster. No proposed pole shows clustering beyond chance once both controls are applied.
- The other three proposed pole latitudes do not show clustering even at the site level under principled nulls. Pole V (52.3°N) showed weak excess under the conditional null but was eliminated by the block-conditional null, indicating its apparent signal was region-specific. Poles I (90°N) and IV (64.1°N) show no excess under any principled null model.
- The aggregate primary test statistic, T = mean d_min, is null under principled nulls. The "26-sigma highly significant" pre-registered result was an artifact of hemisphere-mismatch between the observed (99% northern by selection) and permuted (~54% northern by chance) intersection distributions; under nulls that preserve the in-range property by construction, T_obs is consistent with random great-circle geometry on this site distribution.
- The site-to-pole assignment match rate (454 of 994, 46%) is significant under all four null models, but reflects agreement between our independent geometry and the data owner's pipeline (within 0.1° for 95.7% of structures) together with the within-hemisphere concentration of intersections — not the pole positions (§3.6). It is not independent evidence for the framework.
- Descriptively (independent of any null model), the 47°W meridian is not the meridian at which the observed data is most tightly clustered. Across the 72 longitudes scanned at 5° resolution, the minimum T was at −20°E, and 47°W ranked 10th of 72. The natural geometric attractor band for great-circle intersections in this site distribution runs from approximately −40°E to 0°E.

## Alternative explanations for the within-hemisphere clustering at Poles II and III

As §3.8 shows, the apparent site-level concentration at 76°N and 72.2°N is not distinguishable from chance once look-elsewhere multiplicity and spatial non-independence are accounted for, so there is, in the end, no beyond-chance clustering to explain. It is worth noting nonetheless that even taken at face value the concentration would not have pointed to former pole positions: several mundane mechanisms produce latitude concentration in great-circle intersections, and an orientation-clustering test does not, in principle, distinguish among them. The spatial-cluster analysis (§3.8) identifies the operative one here — shared orientation within dense, same-tradition site clusters.

**Cultural orientation conventions.** Ancient architectural traditions often align structures to specific celestial or landscape features. If the relevant features (the cardinal points, the celestial pole as it appeared in the past, prominent astronomical objects, regional landscape orientations) happened to project, by great-circle geometry, to specific latitudes on the 47°W meridian, the resulting intersection distribution would show concentration without any reference to former pole positions.

**Astronomical alignments.** Structures oriented to solstitial sunrise/sunset, lunar standstill events, stellar risings, or other astronomical phenomena will produce bearings that depend on the structure's latitude and the celestial event's declination. These dependencies can produce great-circle intersections that cluster at latitudes that have no special status as pole positions but are simply where the geometry concentrates intersections for a population of mid-latitude sites observing common celestial events.

**Archaeological measurement effects.** Bearings in the database are reported to a precision of approximately 0.5–1.0° (the data owner's stated measurement error). Quantization in bearing measurement, combined with the data owner's per-site averaging rule for multi-structure sites, can produce apparent concentration at specific latitudes as an artifact of the discretization rather than as a property of the underlying orientations.

**Selection in the database itself.** The database is a curated collection. If the data owner's site-selection process favored structures that point in particular directions — even unintentionally, through criteria like "well-documented orientation" or "archaeological prominence" — the resulting sample could show clustering that reflects the selection rather than a universal architectural pattern.

**The framework's own claim.** The data owner's hypothesis is that the clustering reflects past positions of Earth's rotational axis at the times the structures were built. Under this hypothesis, the orientation patterns would directly encode the geographic locations of paleopoles.

Among the mundane explanations the analysis does not fully adjudicate. But it does bear on the last one: the spatial-cluster null (§3.8) specifically disfavours the framework's claim, because a genuinely cross-regional, pole-driven pattern — supported by many independent locations — would have survived collapsing the data to independent spatial units, and the observed concentration did not. What remains is consistent with ordinary within-tradition convention and carries no implication of former pole positions.

## What the framework's broader claim requires

The framework's interpretive claim — that the observed latitude concentrations correspond to former positions of Earth's rotational axis — is qualitatively different from the orientation-clustering claim our analysis tests. An orientation-clustering test can establish whether clustering exists; it cannot establish the *cause*. The framework's broader claim is a geological and geophysical claim, and it requires geological and geophysical evidence to evaluate.

What kind of evidence would bear on the claim?

**Paleomagnetic data from the proposed time periods.** Earth's magnetic and rotational poles do not coincide, but their relationship is constrained over geological time. Paleomagnetic measurements from rocks dating to the time windows when the framework proposes the rotational axis was at each of the alternative pole positions could test whether the magnetic-pole record is consistent with such large excursions of the rotational axis.

**Geological evidence of true polar wander.** Apparent polar wander paths are a standard subject of plate tectonics; large excursions of the rotational pole on the timescales implicit in the framework (tens of thousands of years rather than tens of millions) would imply specific patterns of crustal deformation, sea-level change, and climate that should be detectable in the geological record.

**Independent dating of the structures.** The framework attaches specific date ranges to each proposed pole (the time during which that latitude was supposedly the rotational pole). Comparing structure construction dates from radiocarbon, dendrochronology, archaeological context, or other dating methods against the framework's proposed timeline would test the temporal consistency of the claim.

**Climate and sea-level proxies.** Different paleopole positions imply different global climate regimes. Independent climate proxies from the proposed time windows (ice cores, sediment records, biological proxies) could test whether the implied climate matches the geological record.

None of this is within the scope of the present analysis, and none is required by the orientation-clustering claim taken on its own terms. But the framework's broader interpretive claim — the one that distinguishes it from any of the alternative explanations enumerated in §4.2 — depends on this kind of independent evidence. The orientation pattern, on its own, is consistent with multiple causes.

## Methodological lessons

The most generalisable contribution of this analysis is methodological, not substantive. Three transferable lessons emerged, each forced by a control the pre-registered protocol did not contain, and each caught after the fact by the same open, instrumented process that produced the preliminary positive.

**First: pre-register the full data-processing pipeline, not just the test statistic.** The pre-registration committed the analysis to a specific null model: random permutation of folded bearings across the 994 in-range sites. This null preserves site geography and the marginal bearing distribution. It does not preserve the *condition that gave rise to the in-range set in the first place* — that those 994 structures had bearings producing northern-hemisphere intersections on the 47°W meridian. Under random permutation, only about 54% of permuted intersections land in the northern hemisphere, while the observed in-range set is 99% northern by construction. The test "is the observed T smaller than the null T?" is therefore conflated with "do random bearings preserve the northern-hemisphere selection?", and the latter dominates — producing a null mean for T of about 56° even though the within-hemisphere clustering question gives a null mean of about 4°. This is what generated the apparent 26-standard-deviation result.

**Pre-register the full data-processing pipeline, not just the final test statistic. Selection effects that operate before the registered test can produce arbitrarily large apparent significance.**

When a data set has been filtered using a criterion that interacts with the test statistic, the null model must preserve that criterion by construction, not assume random permutation will reproduce it in expectation. The conditional null (§2.5) does this with a Metropolis swap chain on the bipartite compatibility graph, accepting only permutations that satisfy the in-range criterion for every structure; the block-conditional null (§2.6) generalises it to preserve regional partitioning as well.

**Second: a look-elsewhere correction must cover every axis that was searched, not only the one anticipated.** The protocol included a look-elsewhere correction for the choice of *meridian* (§10), because the 47°W reference longitude was visibly a chosen quantity. It did not include the analogous correction for the choice of *latitude*: the per-pole test applied a Šidák correction for five poles as though those five latitudes had been fixed in advance, when the data owner states they were identified partly from the orientation data (Appendix A). The latitude look-elsewhere control (script 07) showed the omission was decisive — under the assumption-free conditional null, the apparent per-pole significance at Poles II and III disappears once the freedom to place the window anywhere on the latitude axis is accounted for.

**When targets are derived from the data, correct for the full search space on every axis that was free to vary — not only the axes whose freedom is obvious.**

**Third: the unit of randomisation must match the unit of independence — often the spatial cluster, not the individual record.** The block-conditional null treated structures as exchangeable within coarse geographic blocks. But archaeological structures are spatially autocorrelated: dense clusters of a single architectural tradition share an orientation convention, so the effective number of independent observations is far smaller than the record count. Treating 539 American structures as 539 independent draws inflated the per-pole null's confidence. Finer geographic blocking (scripts 08, 09) reduced the apparent significance, but only where it subdivided the relevant population; a spatial-cluster null (script 10) that collapsed nearby structures to one representative each removed it entirely. A single 29-site cluster in the northern Yucatán had been contributing 29 ostensibly independent points to the Pole III count.

**Permutation and block nulls are only as good as their independence assumption. When records are spatially (or otherwise) autocorrelated, randomise at the level of the independent unit — the cluster — not the individual record, or significance will be overstated by the degree of replication.**

None of the three is a flaw in pre-registration as such; each is a flaw in a pre-registration that did not anticipate the full structure of the problem — the processing pipeline, the search space, and the dependence structure of the data. The remedy in every case is more careful specification, not less stringency. That all three gaps were found and closed after publication, by the same pre-registered and openly logged workflow, is the substantive point: the discipline that produced an over-confident preliminary result is also what made it checkable and the correction unambiguous.

## Limitations of this analysis

Several limitations constrain the conclusions that can be drawn from this work.

**The aggregation-threshold sensitivity (§11(c)) was not implementable.** The data file contains the data owner's pre-aggregated structure entries, where multi-structure sites have already been collapsed into single rows according to his stated ~2° rule. The underlying multi-structure data was not available, so we could not vary the aggregation threshold to test sensitivity. The pre-registered sensitivity check is documented as not run.

**The eight manually-snapped structures.** The data owner's published intersection latitudes for eight structures with near-zero bearings differ from the geometrically-correct values by ~180°. These are case-by-case manual adjustments confirmed by the data owner. Our analysis uses the geometrically-correct values, which contribute ~141° per structure to T_obs and reduce the §11(b) assignment match count by 8 from 462 to 454. The analytical effect is small but documented.

**The database has not been independently audited for completeness or systematic biases.** The 1,159 structures in the database represent the data owner's selection from a much larger global population of ancient monuments. The selection criteria, the completeness of coverage, and potential systematic biases (toward certain structure types, certain geographic regions, certain time periods, or certain orientation patterns) have not been independently verified. Any clustering observed in the database is a property of *this specific curated sample* and may not generalise to a complete or differently-curated population of ancient structures.

**Regional imbalance in the sample.** The Americas block (n = 539) contains 54% of the in-range structures. The remaining 455 structures are distributed across six other geographic blocks, with two of them (Africa, Oceania/SE Asia) holding fewer than 25 structures each. The block-conditional null is therefore much more constrained by the Americas block than by the others, and the per-region analysis is limited by sample size in the smaller blocks. The geographic coverage of the database is also heavily weighted toward Mesoamerican and Mediterranean-Middle Eastern sites, which may affect the generalisability of any findings to ancient structures in regions less represented in this sample. This imbalance, and the spatial autocorrelation within the Americas block in particular, is what the spatial-cluster control of §3.8 was introduced to address.

**What the block-conditional null can and cannot detect — and how §3.8 resolved it.** The block-conditional null preserves site geography, regional bearing patterns, and northern-hemisphere intersection simultaneously, but it shuffles bearings freely within each block while leaving structures in their original blocks. This makes it conservative toward genuinely cross-regional signals — these survive within-block permutation because the cross-block pattern is preserved — while at the same time treating every structure within a block as an independent observation. Version 2 reported that Poles II and III survived this null and did not formally separate the two possible explanations: a genuinely cross-regional concentration, or a within-region signal merely robust to within-block permutation. The post-publication analyses of §3.8 settle the question in favour of the second. The spatial-cluster null (script 10) treats spatially autocorrelated structures as single units regardless of block, so a genuinely cross-regional concentration — one supported by many independent locations — would survive it, whereas a concentration carried by a few dense same-tradition clusters would not. It did not survive: collapsed to independent clusters the signal is indistinguishable from chance, and over half of the Pole III contributors proved to come from a single Mesoamerican cluster. The block-conditional significance was therefore driven by within-region replication (pseudoreplication), not by a cross-regional pattern. This also addresses the point, recorded in §4.6 and Appendix A, that a global geophysical event would by construction produce a cross-regional pattern: precisely such a pattern would have survived the cluster null, and the observed signal did not.

**The spatial-cluster null relies on a proximity proxy for independence.** Because geographic proximity may merge structures that are in fact independent — which the framework under test specifically predicts a global event would produce — this is the most consequential limitation of the post-publication controls. It is discussed in full beside the cluster-null result (§3.8), together with the two empirical checks now under way.

**The analysis tests one specific framework, not a general hypothesis about ancient orientations.** The proposed pole latitudes were specified by the data owner before our analysis began, so the test is well-defined. But the test does not address alternative configurations of paleopoles, alternative meridians, or other frameworks that might also predict clustering at different latitudes. The conclusions are specific to the framework as specified in the pre-registration document.

## Comparison with the data owner's published probability claims

The data owner's published methodology associates the following confidence claims with each pole:

- Pole I (current): approximately 100%
- Pole II (76°N): approximately 100%
- Pole III (72.2°N): approximately 100%
- Pole IV (64.1°N): approximately 99.999%
- Pole V (52.3°N): approximately 99.999%

These claims derive from a binomial test against a uniform null distribution along the 47°W meridian, using non-uniform bin widths described as "Dynamical Grouping" of the latitude axis.

The present analysis does not support these confidence claims for any pole. Under null models that preserve the relevant features of the data (site geography, in-range hemisphere selection, regional patterns) and — in the post-publication analyses — correct for the data-derived choice of target latitude and for the spatial non-independence of structures, the analysis finds:

- Pole I: no excess concentration (95 within 1.5° vs null mean 95). The "≈100%" claim is not supported.[^poleinote]
- Pole II: an apparent excess under the block-conditional null (115 vs 90, p-Šidák = 0.0015) that does not survive the latitude look-elsewhere correction (p = 0.999 under the assumption-free conditional null) or the spatial-cluster null (p = 1.0). The "≈100%" claim is not supported.
- Pole III: similarly, an apparent excess (119 vs 91, p-Šidák = 0.0005) that does not survive the look-elsewhere correction under the assumption-free null (p = 0.90) or the spatial-cluster null (p = 1.0). The "≈100%" claim is not supported.
- Pole IV: no excess concentration (70 vs 70). The "≈99.999%" claim is not supported.
- Pole V: no excess under the block-conditional null (57 vs 51, p-Šidák = 0.542). The "≈99.999%" claim is not supported.

The contrast is substantive and has two sources. First, the published probabilities derive from a binomial test against a uniform orientation distribution along the meridian; building orientations are not uniformly distributed — they cluster near cardinal directions and other terrestrial conventions — so a uniform null overstates the significance of any concentration whatever. Second, the published method, like the block-conditional null, treats spatially autocorrelated structures as independent, so an orientation convention shared across many sites of one tradition is counted as many independent confirmations rather than one. When the null preserves the data's actual orientation structure, and the analysis counts independent spatial units rather than individual structures, no pole produces a significant signal. The published "100%" and "99.999%" figures should be understood as artifacts of these two choices — a uniform-orientation null and the treatment of correlated structures as independent — not as confidence statements about the framework's claims.

[^poleinote]: The data owner, in commentary provided during the 14-day comment window (see Appendix A), observes that a "background-consistent" finding for the current geographic pole is not necessarily evidence against his framework: under a model of discrete pole shifts, structures built during the current rotational regime should show a distribution consistent with the geometric background, while structures oriented to earlier pole positions should appear as anomalies relative to that background. This is a reasonable interpretive frame and is recorded here. It does not change the statistical finding that Pole I shows no excess clustering under any null model tested in this analysis; the alternative interpretation is a different reading of what such a null result means in the context of his framework.

## Conclusion

On the narrow statistical question it set out to test, the framework does not receive empirical support. The pre-registered aggregate test statistic, though formally "highly significant" at 26 standard deviations, is structurally confounded by a hemisphere-selection effect and is null once that confound is corrected. The per-pole test initially appeared to support two of the five proposed latitudes — Pole II (76°N) and Pole III (72.2°N) — and version 2 of this report characterised that clustering as robust. Two controls applied after publication withdraw it. A latitude look-elsewhere correction removes the significance once the data-derived choice of target latitude is accounted for; under the assumption-free conditional null, Poles II and III are no more concentrated than a freely reshuffled hemisphere produces somewhere along the latitude axis. A spatial-cluster null then shows the apparent Pole III concentration to be an artifact of treating spatially autocorrelated structures — over half of them from a single dense Mesoamerican cluster — as independent observations: collapsed to independent units, the 119 site-level contributors become 25 clusters, indistinguishable from chance. With both controls applied, no proposed pole shows clustering distinguishable from chance. The data owner's published probability claims of "100%" and "99.999%" are not supported by this analysis for any pole (§4.6).

The broader interpretive claim — that the observed latitude concentrations represent former positions of Earth's rotational axis — is not tested by this analysis and could not be established by an orientation-clustering test in any case; it would require independent geological evidence (paleomagnetic, climatological, geological-dating) outside this scope. This report's contribution to that claim is only to remove the orientation-clustering signal that had been offered as evidence for it.

The more durable contribution is methodological: a worked demonstration, on a real data set, of how selection effects, look-elsewhere multiplicity, and spatial pseudoreplication can each manufacture or inflate statistical significance — and of how a pre-registered, openly logged, fully reproducible workflow allows each to be identified and corrected, including the correction of this analysis's own preliminary positive.

The data owner's dissent from this conclusion, and two empirical tests undertaken in response — a simulation of his own peak-finding procedure and a chronological check of the principal cluster — are recorded in Appendix D; the conclusion stands as stated pending those results.

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

# Appendix B: Relationship between version 2 and version 3

*This appendix records what changed between version 2 of this report (deposited 1 June 2026) and version 3, and why, so that a reader encountering either version — or the data owner's commentary in Appendix A — can place the findings in their correct state.*

**What version 2 reported.** Version 2 found that the pre-registered aggregate test statistic was null once a hemisphere-selection artifact was diagnosed and corrected; that Poles I, IV and V showed no clustering under principled nulls; and that Poles II (76°N) and III (72.2°N) showed per-pole clustering that survived all four null models tested, including the block-conditional null. It characterised that clustering at Poles II and III as a robust, real feature of the data.

**What version 3 adds.** Post-publication review (see Appendix C for the reviewer's own summary) identified two controls that version 2 had not applied, each following from a feature version 2 itself documented. First, the per-pole test corrected for the freedom to choose a meridian (the §10 longitude scan) but not for the freedom to choose a target latitude — although the data owner had stated (Appendix A, point 3) that Poles II–V were identified partly from the orientation data. Second, the block-conditional null treated the 539 structures of the dominant geographic block as independent, when archaeological structures are spatially autocorrelated. Three analyses (scripts 07–10, reported in §3.8) supply the missing controls: a latitude look-elsewhere correction, a finer-block sensitivity analysis, and a spatial-cluster null.

**What changed in the conclusion.** With both controls applied, the per-pole clustering at Poles II and III is not distinguishable from chance. It does not survive the latitude look-elsewhere correction under the assumption-free conditional null (p = 0.999 and 0.90), and it disappears under the spatial-cluster null (p = 1.0 across linkage thresholds from 25 to 100 km), where over half of the Pole III contributors prove to come from a single Mesoamerican cluster. Version 3 therefore withdraws version 2's characterisation of robust clustering at Poles II and III. The corrected conclusion is that no proposed pole shows clustering distinguishable from chance.

**The nature of the change.** This is a completion of version 2's analysis, not a repudiation of it. The numerical results version 2 reported are correct for the null models it ran: the per-pole counts (115, 119) and their block-conditional p-values (0.0015, 0.0005) are unchanged and are reproduced in §3.5 and §3.8. What version 2 lacked was the application of two further controls — one of which it had already applied on the other axis (look-elsewhere on longitude), and one of which its own limitations section had flagged as an open question (§4.5). Version 3 resolves both. Stated once and plainly: version 3 retracts the positive finding of version 2 and replaces it with a null result.

**On Appendix A.** The data owner's commentary in Appendix A was written in May 2026 in response to the preliminary (version 2) findings, and welcomes the independent confirmation of clustering at Poles II and III as a meaningful contribution. It is preserved verbatim as the record of his response at that time; the specific finding it welcomes has since been withdrawn, for the reasons given in §3.8. Notably, two of the points he raised are the points on which version 3 turns: his statement that Poles II–V were data-derived (point 3) is what necessitates the latitude look-elsewhere correction, and his concern about the block-conditional null's treatment of the data (point 2) is the converse of the pseudoreplication problem the spatial-cluster null addresses.

**Auditability.** Version 2 remains available as a prior version of this Zenodo record. The pre-registration and the version 2 analyses are unchanged. The analysis log records the post-publication review, the decision to run the additional analyses, and their results; scripts 07–10 and their outputs are in the repository. Per pre-registration §12 point 3, all three post-publication analyses are labelled exploratory. The transition from version 2 to version 3 is itself fully reconstructable from the repository's commit history and the timestamped log.

---

# Appendix C: Post-publication review of version 2 — summary

**Reviewer:** Claude Opus 4.8 (Anthropic), acting as an external reviewer.

**Note:** This summary was generated by Claude Opus 4.8, the reviewer model itself, based on the original review session. The original session transcript is not included; this summary captures the methodological gaps identified, the controls proposed, and the predicted outcomes. The reviewer's principal prediction — that the apparent clustering at Poles II and III would not survive controls for look-elsewhere multiplicity and spatial non-independence — was confirmed when the analyses were run; two specific intermediate predictions were not, and are recorded as such below. The author verified all outputs independently.

## Scope

This was a post-publication review of version 2, conducted in a single working session in which the reviewer was given the version 2 manuscript and the analysis repository (code, pre-registration, and analysis log). The review focused on the per-pole confirmatory result — the apparent clustering at Poles II (76°N) and III (72.2°N) that version 2 characterised as robust — and on the null models used to test it.

## Gaps identified

Two assumptions in the version 2 per-pole analysis were not controlled for by any of its four null models:

1. **Latitude look-elsewhere.** The protocol corrected for the freedom to choose the reference *meridian* (the §10 longitude scan) but not for the analogous freedom in the choice of target *latitude*, although the data owner had stated (Appendix A) that Poles II–V were identified partly from the orientation data. The Šidák correction over five poles addressed five comparisons, not the continuous latitude axis from which the fullest windows had been selected.

2. **Spatial pseudoreplication.** The block-conditional null permuted bearings within coarse geographic blocks while treating every structure within a block as independent. Because structures of a shared architectural tradition are spatially autocorrelated, the effective number of independent observations is smaller than the record count, which can inflate per-pole significance.

## Controls proposed

The reviewer proposed and drafted four analyses: a latitude look-elsewhere correction under each null model (script 07); a finer-block sensitivity analysis subdividing the dominant geographic blocks (08); the latitude look-elsewhere correction applied under those finer blocks (09); and a spatial-cluster null collapsing nearby structures to one independent unit each (10).

## Predictions and outcomes

The reviewer's central prediction was directional: that the apparent clustering at Poles II and III would not survive controls for both look-elsewhere multiplicity and spatial independence. This was confirmed. Under the assumption-free conditional null with the latitude look-elsewhere correction (script 07), the corrected p-values were 0.999 (Pole II) and 0.90 (Pole III): the observed concentrations were no greater than a freely reshuffled hemisphere produces somewhere along the latitude axis. Under the spatial-cluster null (script 10), both poles were non-significant at every linkage threshold from 25 to 100 km (p = 1.0 with the look-elsewhere correction).

Two specific intermediate predictions were *not* borne out, and are recorded for completeness. First, the reviewer initially expected the block-conditional look-elsewhere correction to move Pole III into roughly p = 0.01–0.05; in fact it remained near p = 0.0003, while it was the assumption-free *conditional* null that removed the signal. Second, the reviewer expected finer geographic blocking to be the decisive control — raising the null baseline toward the observed count and pushing Pole III to approximately p = 0.5; instead Pole III plateaued near p = 0.011 under finer blocking, because the finer blocks did not subdivide the single Mesoamerican cluster carrying most of its contributors. It was the spatial-cluster null, not finer blocking, that reduced Pole III to non-significance. The conclusion the reviewer predicted held; the mechanism it had identified as decisive was corrected by the analyses themselves.

## Role and limits

The reviewer identified the gaps, proposed and drafted the four analysis scripts, and drafted the version 3 revisions to this report. The author ran all analyses on the source data, verified the outputs against the pre-registered pipeline, and is responsible for the conclusions, including the decision to withdraw the version 2 finding. This summary was written by the reviewer model from its account of the review session and has not been checked against a verbatim transcript; statements about what was predicted should be read as the reviewer's reconstruction.

---

# Appendix D: Follow-up correspondence from the data owner (5 June 2026), with author's note

*Author's note.* On 5 June 2026, after version 3 was deposited, the data owner sent the response reproduced below in full and unaltered. It raises five concerns. Two identify empirically testable questions rather than matters of presentation, and are being answered by analysis rather than argument: that the latitude look-elsewhere control modelled a worst-case continuous search rather than his actual rule-based peak-finding procedure (his point 2), and that the spatial-cluster null treats geographic proximity as dependence in a way his framework specifically contests (his point 3). Two analyses are accordingly under way and will be reported in a subsequent version — a Monte Carlo simulation of his stated peak-finding rules (received 17 May 2026, before the database was opened) run under the same null models used here, which tests his actual method rather than a worst-case proxy (point 2); and a check of published Maya chronology for the 29-site northern-Yucatán cluster that dominates the Pole III count, to determine whether those structures represent one tradition replicating a single convention or independent structures of different periods converging on one orientation (point 3). The remaining concerns bear on the weight and ordering of analyses. The relative weight of pre-registered versus exploratory results is now set out side by side in §3.7, where readers can judge it directly, and the cluster-null limitation his point 3 raises is now stated beside the result in §3.8 rather than only in the limitations section. On his point 5 — that controls were only ever added toward greater stringency — two facts are recorded in §3.7: each successive control corrected an assumption that biased significance upward, so correcting them necessarily moved the result one way; and one control (script 09) was a pre-committed gate capable of exonerating Pole III, which it did not. The conclusion of §4.7 is stated as it stands pending the two analyses named above; should they prove consistent with the framework, a version 4 will say so. The letter follows without alteration.

---

Dear Salah-Eddin,

I have read version 3 carefully. I want to raise several concerns that I believe warrant the same scrutiny you have applied to my work throughout this process.

1. The pre-registration was effectively abandoned, and this should be acknowledged more candidly.

The pre-registration was deposited to lock the methodology before the data was opened. That was its purpose. The pre-registered primary test gave p = 0.0001. You discarded it. The pre-registered per-pole test under the block-conditional null — which was specified in §11(d) of the protocol — gave p = 0.0015 for Pole II and p = 0.0005 for Pole III after Šidák correction. These results are still in your v3 report. They are pre-registered. They are significant.

The analyses that ultimately drove the conclusion to null — the latitude look-elsewhere correction under the assumption-free conditional null, and the spatial-cluster null — were not pre-registered. They were added after publication, after a reviewer identified them, and after the v2 positive finding was already in the record. They are labelled exploratory, as they should be. But the conclusion of the report now rests on exploratory analyses, while the pre-registered confirmatory analyses that showed significance are set aside as "superseded."

I am not arguing that the exploratory analyses are invalid. I am arguing that a report whose conclusion is driven by post-hoc, post-publication, never-pre-registered analyses should not present itself as a pre-registered confirmatory study. The pre-registration was the anchor. The anchor was cut loose. The ship drifted. The final position is not where the anchor was dropped.

Your Appendix B states that v3 is "a completion of version 2's analysis, not a repudiation of it." I disagree. A completion would have been running the pre-registered tests and reporting them. What happened instead was a progressive tightening of controls — each one defensible on its own, but each one added after seeing what survived the previous round — until no signal remained. The ratchet only ever turned one way.

2. The latitude look-elsewhere correction tested a procedure I never used.

The latitude look-elsewhere control slides a ±1.5° window across the entire latitude axis and asks whether random data produces a window as full as the observed one somewhere. Finding that it does, you conclude that the clustering at my proposed pole latitudes is not significant.

But this is not what I did. I did not scan the latitude axis for the single fullest window and call it a pole. I applied explicit, pre-specified rules: a minimum of 12 structures per degree, clusters extending over at least 3 degrees, gaps between clusters indicating discrete pole positions, and a dispersion trend consistent with the physical model. These rules constrain how many peaks can be identified and where they can fall. They are not equivalent to "find the fullest window anywhere."

A fairer test — and one I would still welcome — would simulate the full process: generate random orientation data, apply my peak-finding rules exactly as stated in the rules document I sent you before you opened the database, and ask how many poles are identified and at what latitudes. That would test my actual method. What you tested instead was a caricature of it, and the caricature failed a test the real method might have passed.

You note in §2.7 that "the Šidák correction over five poles addressed five comparisons, not a continuous latitude axis from which the fullest windows were chosen." But my poles were not chosen as the five fullest windows from a continuous scan. They were identified by a rule-based procedure that imposes its own multiplicity constraint — you cannot have more peaks than the rules permit. Your correction overcorrects by assuming a freedom of choice that my method never exercised.

3. The spatial-cluster null assumes what it needs to prove, and the caveat is buried.

The spatial-cluster null collapses nearby structures into single units based on geographic proximity. At 25 km, 119 structures near Pole III become 25 clusters. The largest single cluster contains 29 sites from the northern Yucatán. Because the signal is concentrated in the Americas, and the Americas block is the most densely sampled, the spatial-cluster null disproportionately erodes the signal.

You acknowledge in §4.5 that "spatial proximity is only a proxy for shared architectural tradition" and that "genuinely independent structures that happen to lie close together are merged, while dispersed members of one tradition are not." This is a profound limitation, and it appears in the limitations section, not in the results section where the cluster null is presented as decisive. A reader who skims the results will see p = 1.0 and conclude the signal is gone. A reader who reaches §4.5 will learn that the test may have merged genuinely independent structures. The placement matters.

The 29-site Yucatán cluster is the centerpiece of your argument that the Pole III signal was pseudoreplication. But were those 29 structures built by the same people, at the same time, for the same purpose? Or were they built over centuries, by different groups, who independently oriented their structures in a direction that happens to point toward the same latitude band? The database does not contain the cultural or chronological metadata to answer this question. The spatial-cluster null assumes the answer is the first. It may be the second. If it is, collapsing them into one observation discards real signal.

A global geophysical event — precisely what my model proposes — would cause structures in many locations, built at different times by different cultures, to point toward the same latitude band. The spatial-cluster null is structurally biased against detecting such a signal, because it treats geographic proximity as dependence regardless of whether the structures are actually dependent.

4. The pre-registered block-conditional results remain significant, and this is not adequately explained.

Even in v3, under the pre-registered block-conditional null with Šidák correction, Pole II returns p = 0.0015 and Pole III returns p = 0.0005. Under the latitude look-elsewhere correction applied to the block-conditional null, Pole III still returns p = 0.0003. These are pre-registered or pre-registered-adjacent analyses. They show significance.

You argue that the spatial-cluster null resolves the discrepancy between the block-conditional and assumption-free conditional results in favor of the conditional null. But the spatial-cluster null is the least pre-registered, most aggressive, and most assumption-laden of all the controls you applied. To treat it as the decisive arbiter — and to dismiss the pre-registered analyses that contradict it — is to weight the evidence in favor of the null.

A more balanced presentation would report that the pre-registered analyses show significant clustering at Poles II and III, that the latitude look-elsewhere correction eliminates Pole II under the assumption-free null but not under the block-conditional null, and that the spatial-cluster null — which carries the acknowledged limitation about proximity as a proxy for dependence — eliminates both. Readers could then judge for themselves how much weight to place on each analysis. Instead, the conclusion treats the spatial-cluster null as having settled the matter.

5. The process structurally favored null findings, and this should be transparent.

The pre-registration committed to a specific null model. That model produced a result in my favor. It was discarded. A conditional null was added. Under it, the aggregate T was null but the per-pole counts at Poles II and III were significant. A block-conditional null was added. Under it, Poles II and III remained significant. A latitude look-elsewhere correction was added. Under the assumption-free null, Pole III became non-significant; under the block-conditional null, it remained significant. A spatial-cluster null was added. Under it, everything became non-significant.

At each step, a new control was introduced after seeing what survived the previous step. At each step, the control made the test more conservative. At each step, the control was methodologically defensible on its own. But the cumulative effect was a one-way ratchet toward the null. No control was ever added that might have made the test more sensitive to a real signal. No control was ever relaxed after being found to be too stringent. The process only tightened.

I am not suggesting bad faith. I am suggesting that when a process can only move in one direction, and that direction is toward the null, the final null result is overdetermined by the process itself. This should be acknowledged.

Closing

I opened my data to independent verification because I believe that is what science requires. You conducted a rigorous analysis, caught your own errors, and engaged with my commentary in good faith. I have respected this throughout.

But the v3 report has moved far from the pre-registered methodology that was the basis of our agreement. Its conclusion rests on analyses that were never pre-registered, that were added after publication, and that carry acknowledged limitations that are not given proportional weight in the conclusion. The pre-registered analyses that showed significance are present in the report but treated as superseded. The latitude look-elsewhere correction tested a procedure I never used. The spatial-cluster null assumes spatial proximity equals dependence, which my model explicitly predicts it would not.

I am not asking you to change your conclusion. I am asking that the final public record reflect these concerns with the same prominence that the v3 conclusion reflects its own. The reader should understand that the pre-registered tests showed significance, that the analyses that eliminated it were post-hoc and exploratory, and that reasonable people can disagree about how much weight they should carry.

My v2 commentary stands in Appendix A as my response at that stage of the process. The finding it welcomed has been withdrawn. The concerns I raised then — about the derivation of the meridian, the hemispheric asymmetry, and the scope limitation — remain, and they were never tested by this analysis. The broader geophysical model stands or falls on evidence this report never engaged.

I remain open to a test of my actual method, applied to my actual procedure, with controls specified before the data is opened. What v3 tested was something else.

Sincerely,

Mario Buildreps

---

# Acknowledgments and References

## Acknowledgments

I thank Mario Buildreps for providing the database file used in this analysis under the conditions described in §2.1, for confirming methodological details about his pipeline via direct correspondence during the analysis period (notably the recommendation to use the geometrically-correct raw-bearing approach rather than the manually-adjusted values published in his pre-computed column), and for accepting the 14-day comment window between the sharing of preliminary findings and the public release of this report. His formal commentary on the findings, received during that window, is included verbatim as Appendix A. His willingness to make his data available for independent verification, and his willingness to provide on-the-record commentary for inclusion in this report, are substantial methodological contributions in their own right, regardless of how any reader interprets the analytical conclusions reached.

Two methodological controls that distinguish version 3 from version 2 — the latitude look-elsewhere correction and the spatial-cluster independence control — were identified in a post-publication review carried out by Claude Opus 4.8 (Anthropic) acting as an external reviewer in a separate session from the one in which the analysis was developed with Claude Opus 4.7 (Anthropic). The reviewer's own summary of the gaps identified, the controls proposed, and the predictions made (with notes on which predictions were borne out and which were not) is included as Appendix C. The implementation of the controls (analysis scripts `07`–`10`) and the drafting of the version 3 revisions to this report were carried out with the assistance of Claude Opus 4.8 used as an analytic interlocutor throughout the project. The author ran all analyses on the source data, verified the outputs against the pre-registered pipeline, and is responsible for the conclusions, including the decision to withdraw the version 2 finding. The analysis code and full reasoning are available in the repository for independent inspection.

The pre-registration document, the analysis code, the full analysis log, and the frozen snapshot of the analysis log as it stood at the opening of the comment window are all publicly available at the project repository. The analysis can be reproduced from the database file using the fixed random seed documented in the pre-registration; cryptographic verification of the data file is built into every analysis script.

This work received no external funding. The author declares no conflicts of interest.

## References

Buildreps M. *Antiquity Reborn (v10): Orientations of pyramids and ancient sites around the world.* <https://mariobuildreps.com/> (accessed 2026-05-17). [Primary source for the framework being tested in this analysis, including the proposed pole positions and the published probability claims.]

Gherbi S-E. *Pre-registration: Independent Monte Carlo verification of paleopole orientation clustering in the Buildreps database.* Zenodo, version 1.1 deposited 17 May 2026. DOI: [10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204). [The full statistical protocol committed to before the database file was opened; GPG-signed and OpenTimestamped.]

Gherbi S-E. *Independent pre-registered verification of paleopole orientation clustering in the Buildreps database.* Zenodo. Version 2 deposited 1 June 2026 (DOI: [10.5281/zenodo.20474028](https://doi.org/10.5281/zenodo.20474028)); version 3 (this version) deposited 5 June 2026 (DOI: https://doi.org/10.5281/zenodo.20546301). [Version 2 reported a preliminary positive result at Poles II and III; version 3 withdraws it following the post-publication controls of §3.8. See Appendix B for the relationship between versions.]

Gherbi S-E. *Paleopole orientation verification: analysis code, results, and full analysis log.* GitHub repository. <https://github.com/salahealer9/paleopole-orientation-verification>. [All scripts, output files, results, and the frozen analysis log are available here. The frozen snapshot as it stood when the data owner received the preliminary findings on 18 May 2026 is at [`results/analysis_log_frozen_2026-05-18.md`](https://github.com/salahealer9/paleopole-orientation-verification/blob/main/results/analysis_log_frozen_2026-05-18.md).]

---

*Author:* Salah-Eddin Gherbi
*ORCID:* [0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095)
*Contact:* salahealer@gmail.com
*License:* This report is released under CC-BY-4.0. The accompanying code is released under MIT.
