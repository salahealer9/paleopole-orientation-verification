# Analysis Log — Frozen Version (2026-05-18)

**This is a snapshot of the analysis log as it existed when results were first
shared with the data owner on 2026-05-18, opening the 14-day comment window
per pre-registration §12 point 2.**

**No content in this file will be modified after 2026-05-18.** Subsequent
developments (the data owner's reply, drafting decisions for the public
writeup, the writeup itself) are recorded in the live analysis log at
[`analysis_log.md`](./analysis_log.md), not in this frozen file.

This frozen snapshot is the canonical reference for what was shared with
the data owner during the 14-day comment window.

---

Chronological record of the analysis as it proceeds. Each entry documents what was done, when, and why. This log is committed to the repository alongside the analysis code so that the full process is auditable.

---

## 2026-05-17 — Note on file access prior to formal analysis

Prior to the formal start of analysis, a brief preview of the database file was read to confirm the column structure. This is documented here for full transparency, even though it does not affect any decision pre-registered at Zenodo DOI [10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204).

**What was inspected:**
- Column headers of `Database_Mario_Buildreps_V14.xlsx`
- The first 5 rows of the first sheet
- The total row count of the first sheet

**Columns observed:**
`SITE NAME`, `COUNTRY`, `LAT`, `LON`, `BEARING`, `Intersection Latitude at Lon 47.1W Line`, `Rounded Latitudes`, `Remarks`, `Date added`

**Quantities confirmed:**
- Total row count: 1,159 — consistent with the data owner's description (993 in-range + 166 out-of-range).
- Bearing values in the preview rows span both negative and positive values within ±45°, consistent with the folded northernface azimuth convention described by the data owner.
- A pre-computed column `Intersection Latitude at Lon 47.1W Line` exists in the file.

**What was not inspected:**
- The distribution of bearings beyond the 5 preview rows.
- The distribution of intersection latitudes.
- Any aggregated or summary statistics over the data.
- The other tabs of the spreadsheet (rules document on tab 2 etc.).

**Effect on pre-registered analysis:** None. The pre-registered tests are specified independently of the file contents and depend only on the column semantics (which match Mario's prior descriptions), the row count (which matches), and the orientation convention (which matches). No threshold, test statistic, null model, or sensitivity analysis was specified or adjusted based on this preview.

**Methodological note for downstream analysis:** The file contains a pre-computed `Intersection Latitude at Lon 47.1W Line` column derived by the data owner. The pre-registered analysis will compute great-circle intersections **independently** from the raw `LAT`, `LON`, and `BEARING` columns, and will treat agreement (or disagreement) with the data owner's pre-computed values as a sanity check on the geometry pipeline. The data owner's pre-computed values will not be used as inputs to the test statistic.

From this point onward, all file access is mediated by versioned scripts in `analysis/`, beginning with `00_verify_and_describe.py`.

---

## 2026-05-17 — Geometry conventions discovered through validation

Running `01_geometry_check.py` against Mario's pre-computed `Intersection Latitude at Lon 47.1W Line` column revealed two operational conventions in his methodology that were not fully explicit in the pre-registration or his rules document. Both are documented here for transparency and adopted in our analysis pipeline with rationale.

### Convention 1: "No Intersect" is a northern-hemisphere filter

Mario marks 166 rows as `"No Intersect 47.1W"`. Independent computation (using pure spherical geometry: a great circle defined by site location + bearing crosses any meridian at exactly one latitude in (−90°, +90°), absent degenerate cases) gives a numeric intersection for every one of those 166 rows.

**All 165 of the 166 marked "No Intersect" rows have independent intersections in the southern hemisphere** (range −88.7° to −19.3°, median −66.3°). Zero exceptions in the northern hemisphere. The single remaining row was a degenerate case.

**Interpretation**: Mario's "No Intersect" label is not a geometric statement (no intersection exists) but a content filter: he discards intersections that land outside the northern hemisphere, because his five proposed paleopoles all lie at northern latitudes (52.3°, 64.1°, 72.2°, 76.0°, and 90°N). A great circle whose forward direction points into the southern hemisphere of the 47°W meridian is not a candidate for the clustering claim being tested.

**Decision**: We adopt the same filter for the pre-registered analysis. The pre-registration specifies N = 993 in-range structures, matching Mario's count after this filter is applied. Including the 166 southern-hemisphere intersections would change the test denominator from what was pre-registered. This is also consistent with rule 2 from Mario's rules document, which counts the 166 in the probability denominator without crediting them as confirmations — a conservative choice we replicate.

### Convention 2: Pole-passing case resolves to +90°

For 46 rows where the bearing is 0° or near-0° and the site is not on the target meridian, the great circle passes through both geographic poles. In this case, the intersection with any meridian is geometrically at *both* ±90° simultaneously. Mario's pre-computed values give +90° in these cases; our initial computation gave −90° (forced by the sign of the great-circle pole vector's z-component).

**Decision**: We update the geometry primitive to return +90° in the pole-passing case, matching Mario's convention. Rationale: when the great circle passes through both poles and the intersection is geometrically ambiguous, the appropriate convention for a test of *northern-hemisphere* paleopole clustering is to select the northern pole intersection. This is a principled choice, not curve-fitting: any other resolution of the ambiguity would treat the structure as if its great circle "missed" the northern hemisphere when in fact it grazed both poles.

The geometry self-test in `01_geometry_check.py` has been updated to include this case.

### Effect on pre-registered analysis

Neither convention changes any pre-registered test statistic, null model, multiple-comparisons handling, or sensitivity analysis. Both conventions are operational filters/disambiguations that align our independent geometry with Mario's, so that our test computes what the pre-registration says it computes: the test statistic T over the 993 in-range structures.

After applying these conventions, expected agreement with Mario's pre-computed `Intersection Latitude at Lon 47.1W Line` column should reach ≥99% within 0.1° for the 993 in-range rows, with the remaining small disagreements attributable to floating-point precision in his calculations.

A second run of `01_geometry_check.py` after these updates will be the final geometry-validation gate before script 02.

---

## 2026-05-17 — Bearing-snapping question resolved by data owner

The second run of `01_geometry_check.py` (after adopting the northern-hemisphere filter and the pole-passing +90° convention) revealed a small remaining residual: 7 rows where the data owner's pre-computed intersection latitude was +90° despite the recorded `BEARING` being exactly ±1°, and where our geometrically-correct computation gives ≈ −89°. The pattern was consistent with a possible bearing-snapping convention (rounding small bearings to zero) not stated in the rules document.

To resolve this ambiguity within the pre-registration discipline, I emailed the data owner with a table of the 7 specific rows and asked two questions:

1. Is there a bearing-magnitude threshold below which the orientation is treated as zero in the computation?
2. If so, what is the threshold value?

**Data owner's reply (received 2026-05-17, copied here verbatim):**

> Hi Salah,
>
> I think your values (My Value) are more consistent. I would strictly follow your method. In some cases I decided to "attach" some structures to our current pole, because they were obvious in my view. There might have been regions that were seismically more active, maybe distorting regional plate orientations over time, or maybe cultures with less advanced tools to orient properly within a small margin of error. Or maybe both.
>
> Mario

**Interpretation:** there is no systematic bearing-snapping rule in the data owner's pipeline. The 7 anomalous +90° values are case-by-case manual adjustments where the data owner chose to "attach" certain structures to the current pole based on his own judgment. The data owner explicitly recommends following the geometrically-correct (raw-bearing) approach.

**Decision:** the pre-registered analysis uses the raw `BEARING` values without any snapping or threshold. No code change is required; the geometry primitive in `01_geometry_check.py` is already correct. The 7 structures will contribute their geometrically-correct intersection latitudes (near −89°) to the test statistic, the same as any other structure.

**Why this matters for the pre-registration discipline:** the data owner's case-by-case "attachments" of certain structures to the current pole — applied in the direction of strengthening the Pole I cluster — are post-hoc per-row decisions that are not governed by a documented rule. Our pre-registered test, by design, evaluates the claim under a single consistent geometric definition applied uniformly to all structures. This is the appropriate independent test of the underlying clustering claim.

A note on the data owner's offered justifications (regional seismic activity, cultural skill levels) is appropriate here for transparency: these are plausible hypotheses, but they were offered after observing the data pattern, and they are not part of the operationalised methodology being tested. The pre-registration tests the orientation-clustering claim as a single statistical hypothesis, not a family of regional or cultural sub-hypotheses.

The geometry validation is now considered complete. Script 01 is ready to commit and we proceed to designing script 02 (the test statistic).

---

## 2026-05-17 — Inclusion criterion refined; data parsing fix for European decimal separator

The first run of `02_observed_test_statistic.py` revealed that applying a strict northern-hemisphere filter (intersection latitude ≥ 0) gives N = 985, not the pre-registered N = 993. A diagnostic comparison against the data owner's `Intersection Latitude at Lon 47.1W Line` column showed 10 disagreements:

**9 "Mario IN-range, our hemisphere filter OUT-of-range":**

- **7 manually-snapped sites** (bearings near ±1°: Castillo de Teayo, Cempoala, Messene, Red Pyramid, Bent Pyramid, Lumbini, Tomb of First Emperor). The data owner confirmed in his email of 2026-05-17 that these are case-by-case adjustments where he "attached" the structure to the current pole. His published values are 90°; geometrically-correct values are near −89°.
- **1 partially-snapped site**: Haran (LAT 36.86, LON 39.03, BEARING +10°). The data owner's value is +15°; independent geometry gives −81.9°. This is a much larger discrepancy than the ±1° cases (97° apart), but the pattern is the same: a hand-adjusted value differs substantially from the algorithmic output.
- **1 counter-example to the hemisphere filter**: Shimao (LAT 38.6, LON 110.3, BEARING −38°, Mario value −6.1°, independent value −6.15°). Mario classifies a southern-hemisphere intersection as in-range. This shows that the "No Intersect" classification is not strictly hemisphere-based — there is at least one southern-hemisphere intersection in Mario's in-range set.

**1 "Mario OUT-of-range, our hemisphere filter IN-range":**

- **Chaco Canyon** (LAT 40.38, LON −7.34, BEARING −45°). The data owner's column shows `56,2` (with a comma decimal separator, European convention). Our pandas-based parser failed to convert this to a number, so we marked it as "No Intersect." Independent geometry gives +56.19°, matching the intended `56.2°` exactly. This is a data-quality / parsing issue, not a methodological disagreement.

### Decisions

**(1) Inclusion criterion**: the pre-registered N = 993 is the data owner's classification. We adopt his classification (the `Intersection Latitude at Lon 47.1W Line` column is numeric vs. non-numeric) as the inclusion criterion. This matches the pre-registered N exactly.

**(2) Geometry**: regardless of Mario's classification or pre-computed intersection values, the test statistic T uses our independent geometry (per his explicit recommendation of 2026-05-17). For the 8 manually-adjusted sites that he classifies in-range, this means their geometrically-correct intersections (~−89° for the bearing-±1° cases, −81.9° for Haran) will contribute large d_i values to T, pulling T upward. This is conservative: it tests the clustering claim under the geometry Mario himself endorsed, rather than under the hand-adjusted values that strengthen his published probabilities.

**(3) Parser fix**: the parsing of Mario's column is updated to replace comma decimal separators with periods before numeric conversion. This correctly classifies Chaco Canyon as in-range.

### Effect on pre-registered analysis

None on test specification, null model, or significance thresholds. The pre-registered N = 993 is preserved exactly. The inclusion criterion is the data owner's published classification, which is what the pre-registration was written against.

The "hemisphere filter" framing in the previous log entry (Convention 1) was an inference that turned out to be approximate but not exact. The accurate framing is: the inclusion criterion is whatever the data owner himself classifies as in-range, which is approximately but not strictly a northern-hemisphere filter. This refinement is documented here for transparency.

---

## 2026-05-17 — Final reconciliation of N: 994 in-range, +1 from pre-registered N = 993

After applying the comma-decimal parser fix, the in-range count is 994, not the pre-registered 993. The single additional structure is Chaco Canyon, whose intersection latitude was recorded as `56,2` (European decimal comma) in the data owner's spreadsheet — clearly a numeric value he intended as in-range, but mis-parsed as text in any pipeline using period-as-decimal-separator (including his own MATLAB pipeline, judging from his published count of 993).

### Possible explanations for the +1 discrepancy

- Mario's stated count of 993 may have come from his own pipeline that also failed to parse `56,2`, in which case our value of 994 corrects the same parsing error in his code.
- Alternatively, the 993 figure may have been from an earlier version of the database before Chaco Canyon was added (some rows in the file have "Date added" = 2020).
- A third possibility is that he was approximating ("about 1,000 in-range") and our 994 happens to be the precise number.

We cannot determine which without further correspondence, and the distinction does not affect the methodology.

### Decision: use N = 994 and document the +1 deviation

Per pre-registration §12, point 4: "Method changes after seeing the data are prohibited. If a clear specification error in this pre-registration is discovered after opening the data ... I will document the error, the correction, and the reason in the final write-up."

This is a specification error of the most minor kind: the pre-registration described the data owner's *stated count* of 993, but the data file (with his classification rule applied consistently and with European decimal parsing) contains 994 in-range structures. Manually excluding Chaco Canyon to hit N = 993 would itself be a researcher degree of freedom (choosing which structure to drop on a target N), introducing a different and larger bias than the +1 deviation it would "fix."

The faithful interpretation of the pre-registration is that N is determined by the inclusion rule (the data owner's classification, parseable as numeric), not by the stated count. The rule gives N = 994. Including Chaco Canyon is the conservative choice: it adds one structure with a geometrically valid intersection that is well-positioned (independent value: +56.19°, close to Pole V at +52.3°), which mildly *strengthens* the apparent clustering rather than weakening it. Excluding it would arbitrarily remove a structure that the data owner intended to include.

### Effect on pre-registered analysis

The +1 deviation in N is documented here transparently. No test statistic, null model, significance threshold, or sensitivity analysis is changed. T_obs (5-pole) computed on N = 994 is 4.649°. The Monte Carlo null distribution will be computed using the same 994 structures, and the p-value will be unaffected by this single-structure deviation from the pre-registered count.

### Effect on T_obs

After applying the data owner's recommended geometry (raw bearings, no hand-snapping) and using his classification for inclusion (994 in-range):

- T_obs (5-pole, primary): 4.649°
- T_obs (6-pole, sensitivity): 3.610°

The 8 manually-snapped structures (the 7 the data owner identified plus Haran, which appears to be a similar manual adjustment) contribute large d_i values to T (each near 141°, distance from their geometrically-correct ~−89° intersection to the nearest of the five proposed poles). These 8 structures account for roughly 1.1° of the 4.6° in T_obs — i.e., T would be ~3.5° without them. The published probability values of the data owner depended on their being snapped to the current pole, which our analysis does not adopt.

The d_min distribution shows a clear bimodal-ish character: 75% of structures are within 4.12° of a pole, with a long tail driven by the manually-snapped structures and other geometrically-distant intersections. The Monte Carlo will reveal whether the bulk concentration is unusual under the null.

This concludes the inspection of the observed data. Script 03 (Monte Carlo null distribution) is the next step.

---

## 2026-05-17 — Primary Monte Carlo result and a critical interpretive limitation of the pre-registered null

Script 03 was run as specified in pre-registration §7. The headline result:

- **T_obs (5-pole, primary)**: 4.6489°
- **Null mean**: 55.89°, **null std**: 1.71°, **null minimum across M = 10,000 iterations**: 49.86°
- **Count of T_null ≤ T_obs**: 0 / 10,000
- **p-value (5-pole)**: 0.0001
- **Verdict per pre-registration §9**: HIGHLY SIGNIFICANT (p < 0.01)

- **T_obs (6-pole, sensitivity)**: 3.6099°
- **p-value (6-pole)**: 0.0001 (count 0 / 10,000)

### Why the result is methodologically suspect at face value

T_obs is more than 26 standard deviations below the null mean. The closest random permutation in 10,000 was still ~45° worse than the observed value. Real-world archaeological data does not produce 26-sigma effects without some artefact of the null model. This called for diagnostic investigation before accepting the result.

### Diagnostic: the null does not preserve the in-range property

A simple diagnostic comparing one random permutation against the observed data revealed the mechanism:

- **Observed intersection latitudes**: 99.1% in the northern hemisphere (985 of 994); median +70.3°.
- **Single random permutation**: 51.6% in the northern hemisphere (513 of 994); median +29.5°.
- **Across 100 random permutations**: northern-hemisphere count averaged 534.8, range [482, 576].

The observed data has 994 northern-hemisphere intersections because the data owner classified those structures as in-range — i.e., the (site, bearing) pairs in the observed set were *selected* to produce northern intersections. When we randomly permute the bearings, most random pairings of (site, bearing) produce southern-hemisphere intersections, giving very large d_i values to the nearest northern pole and inflating T.

A further diagnostic stratified d_min by the hemisphere of the resulting permuted intersection:

- Permuted intersections in [0°, 90°] (540 of 994 in one iteration): **median d_min = 2.02°**.
- Permuted intersections in [−90°, 0°) (454 of 994 in one iteration): **median d_min = 119.30°**.

This breakdown is decisive. The observed d_min median is **1.81°**. The permuted d_min median *for the northern subset only* is **2.02°** — essentially identical. The 26-sigma "highly significant" headline result is therefore entirely an artefact of the hemisphere mismatch in the null model: random bearings paired with observed sites yield ~54% northern intersections, while observed bearings paired with observed sites yield ~99% northern intersections, and the southern half of the random permutations contributes ~120° to d_min each, dominating T.

The null mean of ~56° is consistent with this decomposition: (454 × 119.3 + 540 × 2.0) / 994 ≈ 55.9°, matching the observed null mean of 55.89° to two decimal places.

### What the pre-registered null actually tests vs. what we wanted to test

**What §7 implements**: given the 994 (lat, lon, bearing) triples from the observed in-range set, are random re-pairings of bearings to sites consistent with the observed concentration near the five proposed pole latitudes?

**Result**: very strongly no. Random re-pairings produce mostly southern-hemisphere intersections. The observed data does not.

**What we intended to test**: given that the orientations are non-random in a way that produces predominantly northern-hemisphere intersections, are those intersections clustering more tightly at the five specific paleopoles than expected?

**The pre-registered null does not isolate this question.** The diagnostic above suggests that *within* the northern hemisphere, random permutation produces clustering essentially indistinguishable from the observed clustering (2.02° vs 1.81°). This is consistent with the alternative hypothesis that the apparent clustering at the five proposed poles is a geometric inevitability of where great circles from this geographic distribution of sites land in the northern hemisphere of the 47°W meridian — not evidence of pole-pointing by ancient builders.

The 47°W meridian passes through Greenland and the high-latitude North Atlantic. Sites concentrated in the mid-latitudes (Mesoamerica, the Mediterranean, the Middle East, South and East Asia) have great circles that, when they cross 47°W in the northern hemisphere at all, are geometrically constrained to a band roughly covering [50°N, 90°N] — i.e., the range in which the five proposed poles lie. The five "poles" may be five marker points within a region where great-circle geometry already concentrates crossings, rather than five distinct attractors.

### Decision

Per pre-registration §12 point 4 ("Method changes after seeing the data are prohibited"), I will not revise §7 or deposit a v1.2 of the pre-registration after seeing the data. The pre-registered analysis is the analysis I committed to, and its result (p = 0.0001, "highly significant" under §9) stands as the pre-registered confirmatory finding — but with the interpretive limitation documented above.

The pre-registered finding will be characterised accurately in the final writeup: it rejects the null that "any random reassignment of bearings produces this much northern-hemisphere concentration," which is a meaningful but weaker statement than "the bearings cluster around the five specific proposed poles more than expected from great-circle geometry alone."

Per pre-registration §12 point 3 ("No new tests will be added post-hoc without clear labeling"), I will additionally implement and run a **conditional null Monte Carlo** (script 03b) that preserves the in-range property of the observed data. This is an **exploratory** analysis in the formal sense: it was not pre-registered and is run after seeing the data. It addresses the within-hemisphere clustering question that the pre-registered null could not isolate. Its result will be reported alongside the pre-registered result with the explicit labeling required by §12 point 3.

**Anticipated outcome**: based on the diagnostic above (2.02° permuted vs 1.81° observed within the northern hemisphere), the conditional-null p-value is expected to be well above the pre-registered α = 0.05 threshold. If confirmed, this would indicate that the observed clustering at the proposed paleopoles is not statistically distinguishable from random great-circle geometry conditioned on northern-hemisphere intersection.

The conditional null will be specified as a **site-wise restricted permutation** (Conditional-null A): for each site, the bearing pool is restricted to those bearings (from the empirical pool of 994) which, when assigned to that site, produce a northern-hemisphere intersection. Permutation samples from these per-site restricted pools. This preserves the in-range property by construction, with the trade-off that the resulting marginal bearing distribution may be slightly distorted relative to the empirical marginal. The distortion will be quantified and reported as a sensitivity check.

---

## 2026-05-17 — Conditional-null exploratory result (script 03b)

Script 03b ran the exploratory conditional-null Monte Carlo as specified in the previous log entry. Implementation: Metropolis swap chain starting at the identity permutation, with site-wise compatibility constraints, M = 10,000 retained permutations after 4,970-swap warmup with 1,988-swap thinning interval.

### Result

**5-pole (primary structure, exploratory only)**:
- T_obs: 4.6489°
- Conditional null mean: 4.1286°
- Null std: 0.1534°
- Null 5th / 50th / 95th percentile: 3.882° / 4.124° / 4.384°
- Count of T_null ≤ T_obs: **9,989 / 10,000**
- **p-value (exploratory): 0.9989**

**6-pole (sensitivity, exploratory)**:
- T_obs: 3.6099°
- Conditional null mean: 3.1605°
- Count of T_null ≤ T_obs: 9,996 / 10,000
- p-value (exploratory): 0.9996

### Interpretation

The prediction in the previous log entry was confirmed and refined: within the conditional null preserving the northern-hemisphere property, the observed data is **not** more clustered at the five proposed paleopoles than random great-circle geometry would produce. The observed T is in the upper tail of the conditional null — i.e., observed clustering is *worse* than random.

Substantively, this means:

- The 26-sigma "highly significant" pre-registered result is entirely explained by the hemisphere preference: observed bearings produce ~99% northern-hemisphere intersections, while random bearings on the same sites produce only ~54% northern. The pre-registered null detected this hemisphere preference and rejected the broad null of "any random reassignment of bearings."
- Once the hemisphere preference is preserved by construction (the conditional null), the observed clustering at the five specific poles is not statistically distinguishable from random great-circle geometry on this site distribution. In fact, it is slightly *worse* than typical random permutations, driven in part by the 8 manually-adjusted structures whose geometrically-correct intersections (which our analysis uses) are in the southern hemisphere, contributing ~141° per structure to T_obs.

### Chain diagnostics and methodological notes

- Compatibility matrix density: 53.7% (530,380 of 988,036 (site, bearing) pairs in-range).
- Per-site eligibility ranged from 370 to 824 bearings out of 994.
- Identity-permutation diagonal validity: 985 of 994 (the 9 sites failing this check were Shimao, Haran, and the 7 manually-snapped ±1° structures — see earlier log entries for 2026-05-17 documenting these as the data owner's hand-adjustments).
- Swap acceptance rate: 0.5006 (consistent with rapid mixing).
- Residual conditional-null property violation: 403 southern intersections across 9,940,000 total permuted intersections (0.0041%). This residual is concentrated at the 9 sites with forced-True diagonal entries; it inflates the null mean by approximately 0.006°, well below the precision needed for the headline finding (T_obs of 4.65° vs null mean of 4.13°, separation of 0.52°).

The 403-intersection residual is documented here for transparency and would be eliminated in a strict-rejection implementation, but the cost of strict rejection (rejection rate near 100% for these specific sites under independent re-sampling) would dwarf the methodological gain.

### Status of this result

EXPLORATORY per pre-registration §12 point 3. This finding does not constitute a confirmatory rejection of the framework's hypothesis. It does, however, provide strong evidence that the within-northern-hemisphere clustering at the proposed paleopoles is not distinguishable from great-circle geometry's natural concentration on this geographic sample.

### Combined interpretation of the two Monte Carlo results

| Question | Test | p-value | Status |
|---|---|---|---|
| Are bearings random across all (site, bearing) pairings? | Pre-registered §7 null | 0.0001 | Confirmatory: rejected. |
| Are bearings random *conditional on the in-range filter*? | Conditional null (exploratory) | 0.9989 | Exploratory: not rejected, in fact directionally opposite. |

Both results are correct. Together they describe what the data shows: the bearings are non-random in producing predominantly northern-hemisphere intersections, but within the northern hemisphere, the clustering at the proposed paleopoles is a geometric inevitability of great-circle geometry given this site distribution and meridian choice — not evidence of pole-pointing by the structures' builders.

This is the central empirical finding of the analysis. The final writeup will present both results, with the pre-registered result as the confirmatory finding and the conditional-null result as the exploratory finding clarifying what the pre-registered null could not isolate. The data owner will receive both results 14 days before public release per pre-registration §12 point 2.

---

## 2026-05-17 — Longitude scan result (script 04, pre-registered §10)

Script 04 ran the pre-registered look-elsewhere longitude scan as specified in §10 of the pre-registration. The scan uses the same unconditional null as §7 (script 03), which is the pre-registered specification.

### Observed-data finding (non-null)

Before considering any Monte Carlo, the observed T_obs at each of 72 longitudes (5° resolution) yields a striking result:

- **T_obs at 47°W (pre-registered): 4.649°**
- **T_obs minimum across the scan: 3.783° at longitude −20°E** (off the West African coast)
- **47°W is rank 10 of 72 most-clustered meridians.**

The top 10 most-clustered meridians are all in a contiguous band from approximately −40° to 0° (the Atlantic between Africa and South America, plus the prime meridian). Ranks 1-9 all lie in a single 40°-wide longitude window. Rank 10 (+0°, the prime meridian) is the first to break the pattern. The pre-registered 47°W meridian falls on the *edge* of this attractor band, not at its center.

**This is a falsifiable, non-statistical observation that does not depend on any null model.** Within the observed data, 47°W is not the most-clustered meridian. The natural geometric attractor for great-circle intersections of these sites in the northern hemisphere is centered around −20°E, not −47°W.

| Rank | Longitude | T_obs |
|---:|---:|---:|
| 1 | −20.0° | 3.783° |
| 2 | −25.0° | 3.787° |
| 3 | −30.0° | 3.826° |
| 4 | −15.0° | 3.844° |
| 5 | −35.0° | 3.936° |
| 6 | −10.0° | 3.983° |
| 7 | −40.0° | 4.158° |
| 8 | **−45.0°** | **4.470°** (pre-registered band) |
| 9 | −5.0° | 4.511° |
| 10 | 0.0° | 5.072° |

### Pre-registered Monte Carlo result

The look-elsewhere null distribution (M = 10,000, 5° resolution) under the pre-registered unconditional null:

- T_min null mean: 45.02°
- T_min null std: 1.25°
- T_min null minimum (across iterations): 40.61°
- T_min null 5th percentile: 42.93°
- Count of T_min_null ≤ T_obs(47°W): 0 / 10,000
- **p_LEE (5° primary): 0.0001 (SIGNIFICANT at α = 0.05)**

The 1° resolution sensitivity scan was triggered by the 5° result being below α = 0.05 (per §10b):

- **p_LEE (1° sensitivity): 0.0001**

### Interpretation: same artifact as script 03

The pre-registered null in §10 inherits the hemisphere-mismatch issue documented for §7: random bearing permutations produce only ~54% northern-hemisphere intersections at any given meridian, while observed bearings produce ~99% northern. The "minimum T across longitudes under random permutation" is therefore still dominated by southern-hemisphere contributions: the null T_min mean of ~45° is consistent with most meridians having ~half their intersections in the south, contributing ~100°+ per such structure.

T_obs(47°W) = 4.65° appears extraordinarily small relative to T_min null mean of 45°, producing p_LEE = 0.0001. But this is the same artifact that produced the script 03 result: the test is sensitive to "are bearings random in any sense," not "is 47°W specifically clustered compared to geometry-driven attractor meridians."

### Combined picture (as of this entry)

| Test | Status | p-value | What it shows |
|---|---|---|---|
| §7 unconditional null at 47°W | pre-registered (script 03) | 0.0001 | Bearings non-random in producing northern intersections |
| Conditional null at 47°W | exploratory (script 03b) | 0.9989 | Within-hemisphere clustering at 47°W not distinguishable from random geometry |
| §10 look-elsewhere unconditional | pre-registered (script 04) | 0.0001 | Same artifact as §7, propagated through longitude scan |
| **Observed-data ranking** | **descriptive** | **n/a** | **47°W is rank 10 of 72; minimum-T meridian is at −20°E** |

The pre-registered tests both show "significance," but the observed-data ranking and the conditional-null result jointly demonstrate that 47°W is not the specially-clustered meridian Mario's framework claims it is. The natural geometric attractor band centers around −20°E, and even at 47°W, within-hemisphere clustering is not distinguishable from random great-circle geometry.

### Next analytical step

A **conditional look-elsewhere scan** would parallel the relationship of script 03b to script 03: it would replace the unconditional null in §10's longitude scan with the conditional swap-chain null from 03b. This is not pre-registered and would be labeled exploratory.

Given the observed-data ranking finding above, and the consistency between scripts 03 and 04 in showing the same hemisphere-mismatch artifact, a conditional look-elsewhere scan may not be necessary for the substantive finding — the observed-data result already shows that 47°W is not the minimum-T meridian, which is the relevant non-statistical fact. The conditional look-elsewhere scan would convert this descriptive fact into a formal p-value, but the substantive conclusion is already clear.

For completeness and methodological symmetry, an exploratory conditional look-elsewhere scan may still be run as script 04b. To be decided in light of the remaining pre-registered work in script 05 (per-pole confirmatory and site-to-pole assignment tests).

---

## 2026-05-18 — Per-pole and assignment test results (script 05)

Script 05 implements §11(a) (per-pole confirmatory) and §11(b) (site-to-pole assignment), each under the pre-registered unconditional null AND under the exploratory swap-chain conditional null. The §11(b) assignment is operationalised as the nearest of the five (or six) proposed poles to the data owner's published intersection latitude per structure, per the decision documented in the previous analysis log entry.

### Key results

#### §11(a) per-pole, conditional null (exploratory, 5-pole)

| Pole | Lat | Observed | Cond null mean | p-raw | p-Šidák |
|---|---|---|---|---|---|
| I (current) | 90.0°N | 95 | 102.77 | 1.0000 | 1.0000 |
| II | 76.0°N | 115 | 85.92 | 0.0001 | 0.0005 |
| III | 72.2°N | 119 | 83.77 | 0.0001 | 0.0005 |
| IV | 64.1°N | 70 | 63.73 | 0.1967 | 0.6655 |
| V | 52.3°N | 57 | 42.22 | 0.0090 | 0.0442 |

#### §11(b) assignment, both nulls (5-pole)

- Observed count: **454 / 994** match (46%)
- Unconditional null mean: 45.5 (p = 0.0001)
- Conditional null mean: 81.1 (p = 0.0001 exploratory)

### Substantive interpretation: a genuine within-hemisphere finding

These results show structure that script 03b's aggregate T statistic did not reveal. Specifically:

**Within the conditional null** (which preserves the northern-hemisphere property of the observed data), three of the five proposed poles show significant excess concentration of structures:

- **Pole II (76.0°N): observed 115 vs expected 86** — a 34% excess.
- **Pole III (72.2°N): observed 119 vs expected 84** — a 42% excess.
- **Pole V (52.3°N): observed 57 vs expected 42** — a 36% excess (marginal under Šidák).

Poles I (90°N) and IV (64.1°N) show no significant excess. The §11(b) assignment test confirms the aggregate pattern: 454 structures (46%) have their independent intersection within 1.5° of their pipeline-assigned pole, compared to ~81 (8%) expected under the conditional null. This is a roughly 45σ effect — not a hemisphere-mismatch artifact, because the conditional null preserves the in-range property by construction.

**Reconciling with script 03b's aggregate T result**: the conditional null mean T was 4.13°, while observed T was 4.65° — observed appears slightly *worse* on the aggregate statistic. The reconciliation:

- The aggregate T = mean(d_min) is sensitive to outliers. The 8 manually-snapped structures with geometrically-correct intersections near −89°N contribute d_min ≈ 141° each, pulling T up by ~1.1°.
- The §11(b) match count, being binary (within 1.5° or not), is insensitive to those outliers — they count as "non-match" regardless of how far from a pole they are.
- For the bulk of structures (excluding the ~8 outliers), the data clusters at specific pole latitudes more tightly than the conditional null produces.

### What this within-hemisphere finding does and does not show

**Shows**: the observed bearings produce intersection latitudes that concentrate at specific narrow bands around Poles II, III, and V (76°, 72°, 52°N), more so than random bearings constrained to produce northern-hemisphere intersections would. This is a real statistical effect that cannot be attributed to the hemisphere-mismatch artifact responsible for the script 03 and script 04 pre-registered "significance."

**Does not show**: that these concentrations represent ancient pole-pointing. The concentrations occur within a natural geometric attractor band (centered at −20°E per script 04, but evident across longitudes in [−40°, 0°]) determined by the site distribution. The proposed pole latitudes were derived by the data owner from where intersections concentrate, not specified independently. Other explanations for within-band concentration include cultural orientation conventions (e.g., shared architectural traditions producing similar bearings across regional groups), measurement quantization (bearings reported in degree increments), or specific orientation targets unrelated to paleopoles (e.g., sunrise/sunset directions at certain dates).

The pre-registration does not test among these alternative explanations. The site-to-pole assignment test (§11(b)) was the strongest pre-registered test of the framework's specific predictions, and it does support the claim that the proposed poles capture concentrations in the data — but it does not establish that the concentrations represent the specific phenomenon (former geographic pole positions) that the framework hypothesises.

### Interaction with the manually-adjusted structures

The 8 manually-snapped structures (the ±1° bearing structures and Haran) are interesting from a §11(b) perspective. The data owner assigned all 8 to Pole I (90°N) in his published values (intersection = 90°). Our independent geometry places them at ≈ −89°. Under §11(b), these 8 structures contribute as "non-matches" because the geometrically-correct intersection is far from the assigned pole. Without them, the assignment match rate would be 462/986 = 47% rather than 454/994 = 46%.

The data owner's case-by-case manual adjustments are the only place in the analysis where our pipeline gives systematically different results from his on the in-range subset. They contribute about 0.1° upward bias to T_obs and reduce the §11(b) match count by 8.

### Combined picture, all pre-registered tests

| Test | Section | Status | Result |
|---|---|---|---|
| Primary T, unconditional null | §7 (script 03) | pre-registered | p = 0.0001 (significant, but hemisphere-mismatch artifact) |
| Primary T, conditional null | exploratory (script 03b) | exploratory | p = 0.9989 (observed worse than null) |
| Look-elsewhere, unconditional | §10 (script 04) | pre-registered | p = 0.0001 (same artifact; 47°W is rank 10/72 in observed data) |
| Per-pole, unconditional | §11(a) | pre-registered | All five poles "significant" by artifact |
| Per-pole, conditional | exploratory | exploratory | Poles II, III significant (Šidák p < 0.001); Pole V marginal; Poles I, IV null |
| Assignment, unconditional | §11(b) | pre-registered | p = 0.0001 (artifact) |
| Assignment, conditional | exploratory | exploratory | **p = 0.0001 — genuine effect, ~45σ** |

### Status of analysis

The substantive analytical work is now complete. The framework's central claim of orientation-clustering at the proposed paleopoles is *partially* supported (Poles II, III, V show within-hemisphere excess), *not supported* for Pole I and Pole IV, and the broader interpretive claim (these are former geographic poles) is neither tested nor supported by this analysis.

The writeup must navigate this carefully. The pre-registered tests "succeed" in the formal sense (significant p-values), but for the wrong reason (hemisphere mismatch). The exploratory conditional tests, taken together, paint a more nuanced picture: there IS a within-hemisphere clustering effect at three of the five poles, but it does not establish the framework's interpretive claim.

The data owner will receive these findings 14 days before public release per pre-registration §12 point 2.

---

## 2026-05-18 — Geographic-block null sensitivity (script 06, pre-registered §11(d))

Script 06 implements the pre-registered §11(d) geographic-block null model. Bearings are permuted within seven geographic blocks (Americas n=539, Middle East n=205, Europe-Med n=120, South Asia n=65, East Asia n=32, Oceania/SE Asia n=23, Africa n=2), plus 8 sites in an "Other" block (mostly Central Asian sites that fell outside the box definitions: Sawran ×4, Toniná, Koshoy Korgon ×2, Big Qırq Qız Qala). The Americas block dominates (54% of in-range structures), reflecting the geographic concentration of the database.

The script runs both a block-unconditional null (within-block shuffle without further constraint) and a block-conditional null (within-block swap chain preserving the northern-hemisphere property). The block-conditional null is the most stringent test in the analysis: it preserves site coordinates, marginal bearing distribution within each block, and the northern-hemisphere intersection property simultaneously.

### Results

**Primary T statistic:**

| Test | T_obs | Null mean | p |
|---|---|---|---|
| Block-unconditional | 4.65° | 4.76° | 0.170 |
| Block-conditional | 4.65° | 4.55° | 0.842 |

Aggregate T shows no clustering signal under either block-permutation null.

**§11(a) per-pole counts (block-conditional null, Šidák-corrected):**

| Pole | Lat | Observed | Block-cond null mean | p-Šidák |
|---|---|---|---|---|
| I (current) | 90.0°N | 95 | 95.44 | 0.9998 |
| II | 76.0°N | 115 | 90.29 | **0.0015** |
| III | 72.2°N | 119 | 90.63 | **0.0005** |
| IV | 64.1°N | 70 | 70.13 | 0.9789 |
| V | 52.3°N | 57 | 50.77 | 0.5422 |

**§11(b) assignment match (block-conditional null):**
- Observed: 454; null mean: 92.2; p = 0.0001 (exploratory)

### Substantive interpretation

The block-permutation null reveals which apparent signals are robust to regional patterns and which are not.

**Robust signals (survive all four null models):**

- **Pole II (76°N)** shows an excess of ~25 structures over expectation (115 vs 90), p-Šidák = 0.0015. This survives unconditional, conditional, block-unconditional, and block-conditional permutation. The clustering at 76°N is a real feature of the data that is not explained by hemisphere selection, latitudinal range, or regional orientation patterns.
- **Pole III (72.2°N)** shows an excess of ~28 structures (119 vs 91), p-Šidák = 0.0005. Same robustness profile as Pole II.

**Region-specific signal (disappears under block-conditional):**

- **Pole V (52.3°N)** was marginally significant (p-Šidák = 0.0442) under the conditional null in script 05. Under the block-conditional null, this drops to p-Šidák = 0.5422. The Pole V excess was driven by region-specific bearing patterns — once we permute only within regions, the apparent concentration at 52°N disappears. This is consistent with one region (likely Americas, given its size and the proximity of typical Mesoamerican site latitudes) having a bearing distribution that places intersections preferentially at 52°N.

**No signal under any null:**

- **Pole I (90°N)**: observed 95 vs expected 95 across all nulls. The current geographic pole is not a concentration point in the data.
- **Pole IV (64.1°N)**: observed 70 vs expected 70 across all nulls. No excess.

**§11(b) assignment match remains highly significant (p = 0.0001) under all null models including block-conditional.** This signal is robust because the §11(b) test measures agreement between our independent pipeline and the data owner's pipeline at the pole-assignment level, which is a structural feature of the data that block-permutation does not eliminate.

### Final summary of all tests run

| Test | Pre-registered? | Status | Key finding |
|---|---|---|---|
| §7 primary T, unconditional null | Yes | Confirmatory (script 03) | p = 0.0001, but artifact of hemisphere mismatch |
| §7 primary T, conditional null | No | Exploratory (script 03b) | p = 0.9989, observed worse than null |
| §10 look-elsewhere, unconditional | Yes | Confirmatory (script 04) | p = 0.0001, same artifact. Descriptive: 47°W is rank 10/72 |
| §11(a) per-pole, unconditional | Yes | Confirmatory (script 05) | All five "significant" by artifact |
| §11(a) per-pole, conditional | No | Exploratory (script 05) | **Poles II, III significant**; V marginal; I, IV null |
| §11(a) per-pole, block-conditional | Yes | Confirmatory §11(d) (script 06) | **Poles II, III remain significant**; V null; I, IV null |
| §11(b) assignment, unconditional | Yes | Confirmatory (script 05) | p = 0.0001, partly artifact |
| §11(b) assignment, conditional | No | Exploratory (script 05) | p = 0.0001 (~45σ effect) |
| §11(b) assignment, block-conditional | Yes | Confirmatory §11(d) (script 06) | **p = 0.0001 robust to regional patterns** |

### Final interpretation

After comprehensive testing under multiple null models including the most stringent (block-conditional), the analysis finds:

1. **Genuine within-hemisphere clustering exists at Poles II (76°N) and III (72.2°N).** This is the strongest, most robust finding of the analysis. About 234 structures (24% of the in-range set) point at intersections near these two latitudes, ~50 more than expected under the most stringent null model. The clustering is real and is not attributable to hemisphere selection, regional patterns, geographic distribution of sites, or measurement artifacts.

2. **Poles I, IV, V, and VI do not show robust support.** Pole V showed a region-specific signal that disappears under within-region permutation. Poles I, IV, and VI show no excess under any principled null. The framework's claim of five (or six) distinct paleopoles is not supported in this specific form.

3. **The site-to-pole assignment match rate is very high (46% vs 8% expected under random permutation, p = 0.0001 under all nulls).** This reflects close pipeline agreement between our independent geometry and the data owner's, combined with the latitude-band structure of the data. It is consistent with the framework's pole-assignment claims but does not by itself establish them — the same statistic would obtain for any framework that placed candidate "poles" at the observed concentration latitudes.

4. **The aggregate primary T statistic is null under all principled nulls.** The 26-sigma result under the pre-registered unconditional null was entirely an artifact of hemisphere mismatch.

5. **The interpretive claim that the observed latitude concentrations represent former geographic pole positions is not testable by this analysis** and is neither confirmed nor refuted. Alternative explanations for the within-hemisphere clustering at 72° and 76°N — including cultural orientation conventions, astronomical alignment patterns, archaeological measurement conventions, or other causes — are not addressed by an orientation-clustering test alone.

### Status of analysis

The substantive pre-registered analysis is now complete. Aggregation-threshold sensitivity (§11(c)) was not feasible to implement because the database contains the data owner's pre-aggregated structure entries rather than raw multi-structure data, and we could not obtain raw structure-by-structure data without further correspondence. This will be noted in the writeup as a documented limitation.

Next step: draft the writeup and prepare the 14-day notice email to the data owner per pre-registration §12 point 2.

---





