# Analysis Log

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

## 2026-05-23 — Data owner's commentary received; writeup incorporations and declines

Five days into the 14-day pre-publication notice window opened on 18 May 2026, the data owner provided a formal written commentary on the preliminary findings (received 23 May 2026). The full text is included verbatim as Appendix A of the final writeup (`writeup/results_v1.0.md`). This log entry documents the reasoning for which elements of the commentary were incorporated into the writeup and which were not, in the spirit of maintaining the analytical and methodological reasoning of the project as a transparent record.

### Summary of the data owner's reply

The data owner's commentary has the following structure:

- A preface acknowledging several aspects of the analytical process: the discipline of diagnosing the 26-sigma artifact, the methodological lesson on hemisphere-conditioning in selection-effect-aware nulls, the independent confirmation of clustering at Poles II and III under stringent null models, and the validity of the critique of his original binomial test against a uniform null.
- A clarification regarding the sample size used in his original binomial test (using N = 1,159 rather than 994 made his test conservative rather than inflated; he accepts the deeper circularity issue).
- A clarification regarding the historical derivation of the 47°W meridian, which he states was derived from a 2015 hemispheric-intersection calculation (yielding 71.6°N, 47.1°W) and re-derived in 2020 (yielding approximately 58°N, 44°W), rather than being identified by scanning for the strongest clustering.
- A clarification that Poles II–V were identified partly through examination of the orientation data, making the pre-registered per-pole confirmatory test better understood as cross-validation than as a test of independent predictions.
- Acknowledgment of the descriptive longitude-scan finding (47°W is rank 10 of 72 in the observed data).
- Seven substantive concerns about framing and interpretation: the meridian characterisation, the block-conditional null's structural limitations, the aggregate T statistic missing structural information in the latitude distribution, the interpretation of the Pole I null finding, the prominence of the scope limitation, the prominence of the confirmed signal in the narrative, and the broader claim that the analysis tested one component of a multi-component framework.

### Decisions on incorporation

The pre-registration's §12 point 4 commits to incorporating "factual corrections" identified during the comment window, while declining "interpretive disagreements." The boundary between these categories is consequential and I applied it as follows.

**Incorporated into the writeup:**

1. **47°W meridian's derivation history** (§2.7). The data owner's account of the 2015 hemispheric-intersection calculation is factual context about how the meridian was chosen that we did not have during the pre-registration drafting. We accept his account in good faith for the historical record, while noting that we cannot independently verify the 2015 derivation. The §2.7 text now presents both the theoretical-derivation account and the empirical longitude-scan results, with neither presented as definitive.

2. **The Pole II–V derivation as cross-validation** (implicit in §2.8 and §3.5 framing). The clarification that Poles II–V were identified partly from data examination means our per-pole confirmatory tests function as cross-validation rather than independent prediction. The implication is documented in the relevant sections without restructuring the test specifications, which remain pre-registered as drafted.

3. **The block-conditional null's structural limitation** (§4.5). The data owner's concern that the null may be biased against his hypothesis required closer analysis. His stronger formulation — that the null is "structurally incapable of detecting a global cross-cultural signal" — was, on careful examination, not entirely accurate. The null preserves block membership (each structure remains in its original block) and shuffles bearings only within blocks; a cross-regional signal that appears across multiple blocks would survive this procedure because the original block-to-block structure is preserved. What the null *does* erase is the possibility that the signal is driven by region-specific bearing distribution alone. We added an expanded paragraph to §4.5 documenting both what the null detects (cross-regional patterns) and what it absorbs (region-specific signals), explicitly noting that the surviving signals at Poles II and III are consistent with either interpretation (genuinely cross-regional, or sufficiently robust to within-block permutation) and that the analysis does not formally separate these possibilities.

4. **The data owner's alternative interpretive frame for Pole I** (§4.6 footnote). The observation that a "background-consistent" finding for the current geographic pole is consistent with a discrete-pole-shift model — under which current-era structures would be expected to match the geometric background while older structures should appear as anomalies — is a reasonable reading of the null result for Pole I. This is recorded as a footnote, presented as the data owner's alternative interpretation rather than our endorsement, since it does not change the statistical finding that Pole I shows no excess clustering under any null model tested.

5. **The longitude scan caveat** (§3.4). The pre-registered p_LEE values inherit the same hemisphere-mismatch limitation as the primary T statistic. The §3.4 text now states this caveat explicitly: a statistic that is dominated by hemisphere-selection at one meridian is dominated by the same effect when applied across 72 meridians. The pre-registered p_LEE value is reported as the pre-registered finding, with this limitation acknowledged.

6. **The data owner's full commentary as Appendix A**. Per the pre-registration's commitment to transparency in the final writeup, the commentary is included verbatim with his permission. This ensures that any reader of the report has direct access to his perspective alongside the analytical conclusions, without requiring the reader to track the email thread or external references.

7. **Updated acknowledgments**. The acknowledgments section now credits the data owner for providing on-the-record commentary in addition to the database.

**Not incorporated:**

1. **No changes to statistical findings, p-values, or analytical conclusions.** The data owner's commentary did not identify factual errors in the analysis itself. The pre-registered tests were run as specified, the null models behave as documented, and the p-values are correct. No incorporation is required at the analytical level.

2. **No change to the abstract's framing.** The abstract already leads with the Pole II and III findings, which is what the data owner asked it to do. Further softening of the language about the null findings for Poles I, IV, V would overclaim relative to what the analysis establishes.

3. **No change to the conclusion's restrained register** (§4.7). The conclusion states that "the framework receives partial empirical support." This is fair to the data. Strengthening it (e.g., to "the framework is supported") would not honour the actual findings, which show robust clustering at only two of five proposed poles and a null aggregate signal under principled nulls.

4. **The descriptive longitude-scan finding remains in the report.** The data owner accepted that 47°W is rank 10 of 72 in the observed data, and the report records this as a descriptive observation. The 47°W meridian's theoretical-derivation context is added alongside, but the descriptive empirical observation is not retracted. A theoretically-derived parameter and an empirical optimum are different quantities, and the report presents both.

5. **The §3.2 diagnostic narrative and §4.4 methodological lesson stand.** The data owner explicitly acknowledged these as the most valuable element of the analysis. The pre-registered unconditional null was confounded; the diagnostic identified the confound; the conditional and block-conditional nulls isolated the within-hemisphere question. This narrative is not softened in any way.

### Reasoning for the boundary

The boundary between factual-correction-incorporated and interpretive-disagreement-declined is articulated explicitly in the response to the data owner. The principle:

- **Factual clarifications about the framework's derivation history**: incorporated. We did not have this information when the analysis was designed; it deserves to be in the record.
- **Methodological limitations the data owner identifies**: incorporated where reasonable. The block-conditional null limitation is a legitimate concern that we did not adequately disclose in our initial draft.
- **Interpretive disagreements about what the findings mean**: not incorporated by changes to our analytical framing. Such disagreements belong in the commentary as the data owner has provided it, where any reader will encounter them.
- **Factual corrections to the analysis itself**: would have been incorporated, but the data owner's commentary did not identify any.

This is not a softening of the analytical conclusions. It is the addition of context that, in combination with the appended commentary, gives the reader a more complete view of both the analysis and the framework's defence.

### Methodological note on the comment-window phase

The pre-registration's §12 point 2 commits to a 14-day window before public release of results, with the data owner welcome to provide commentary. The pre-registration does not commit to a specific procedure for incorporating comments. The procedure adopted here — incorporate factual clarifications and acknowledged methodological limitations, append the full commentary as a separate appendix, and decline interpretive disagreements at the analytical-framing level — was chosen as a balance between the data owner's reasonable interest in being heard and the report's need to maintain analytical integrity.

This is, in itself, a methodological choice that may inform future pre-registered work that includes a comment window. Specifying the comment-incorporation procedure in the pre-registration itself (rather than leaving it to be worked out during the window) might be a useful refinement of pre-registration practice.

### Status

The writeup edits described above have been applied to `writeup/results_v1.0.md` and committed on 23 May 2026. The data owner has been notified of the changes in a response sent on the same date. The text of the response is preserved at `results/correspondence/2026-05-23_response_to_mario.md`. The publication date remains 1 June 2026 as per the pre-registration; if the data owner provides factual corrections to the language drafted in response to his commentary by 30 May, these will be incorporated.

---

## 2026-05-24 — Comment-window closure

The data owner replied on 24 May to the 23 May response, confirming:

- The 2015 hemispheric-intersection coordinates as paraphrased in §2.7 (71.6°N, 47.1°W) are accurate; no factual correction is needed.
- No other factual corrections to the language drafted for his commentary points.
- Acceptance of the technical clarification on the block-conditional null's behaviour, with his original framing preserved in Appendix A and our refined framing preserved in the body §4.5.
- No objection to the publication timeline (final version by 31 May, Zenodo deposit on 1 June).

The full reply is preserved verbatim at `results/correspondence/2026-05-24_reply_from_mario.md`.

The 14-day pre-publication notice window opened on 18 May 2026 is effectively closed with the data owner's confirmation. The writeup is now in its final form pending only the rendering, signing, and timestamping workflow scheduled for 30-31 May, and the Zenodo deposit and follow-up email on 1 June.

---

## 2026-05-31 — Publication artifact finalised

The final report has been rendered, GPG-signed, and OpenTimestamped, completing the pre-registered analytical and documentation protocol. The artifact is now committed to the public repository at `writeup/results_v1.0.pdf`. The Zenodo deposit is scheduled for 1 June 2026 per the pre-registration's publication-date commitment.

### Provenance summary

The publication artifact has the following cryptographic provenance chain:

- **PDF file**: `writeup/results_v1.0.pdf`
- **SHA-256**: `582b798e34a2bba58b7a93e4e46215c1d8812d81d21e90fb1f90d8557b0402a6`
- **GPG signature**: `writeup/results_v1.0.pdf.asc` — signed with the same key used for the pre-registration (key ID `D4EC0...`) and for every commit in this repository.
- **OpenTimestamps proofs**:
  - PDF: `writeup/results_v1.0.pdf.ots` — Bitcoin block 951758, merkleroot `f5a820f2b9e363658dc6d7c43167851ae0e155d1ccb87e3ec5ecd33dc19358b1`
  - Signature: `writeup/results_v1.0.pdf.asc.ots` — Bitcoin block 951797, merkleroot `eee902eebc3b300a6ac1e41c671d8f9d54c56409f90150bc54e534a0e0ee74a0`

Any future reader can independently verify the cryptographic claims by:
1. Computing the SHA-256 of the PDF and confirming it matches the value above.
2. Running `gpg --verify writeup/results_v1.0.pdf.asc writeup/results_v1.0.pdf` against the public GPG key.
3. Running `ots verify writeup/results_v1.0.pdf.ots` (with `--no-bitcoin` if no local Bitcoin node is available) and confirming the Bitcoin block heights against any public Bitcoin explorer.

This is the same provenance pattern used for the pre-registration document deposited on 17 May 2026, applied now to the final report. Together they form a complete cryptographically-attested chain: the protocol was committed before the data was opened, and the report was rendered after the analysis was complete, with both timestamps independently verifiable on the Bitcoin blockchain.

### Status of the project

With this entry, the analytical and documentation work of the project is complete. What remains is the mechanical publication workflow on 1 June: depositing the artifact as version 2 of the existing Zenodo record (DOI 10.5281/zenodo.20258204), updating the repository README with the new version DOI, and notifying the data owner.

The pre-registered protocol committed on 17 May 2026 has been executed in full. The 14-day pre-publication notice window committed by the protocol has been honoured. The data owner's formal commentary has been incorporated as factual clarifications in the body of the report and preserved verbatim as Appendix A. The findings reported are the findings produced by the pre-registered analysis, modified only in framing and limitation discussion in response to the data owner's substantive concerns. No statistical conclusion has been altered post-data.

This concludes the analysis log for version 1.0 of the report. Any future entries — corrections, errata, responses to post-publication critique, follow-up analyses — will be marked clearly as such and will not modify the existing record.

---

## 2026-06-01 — Post-publication peer review; latitude look-elsewhere and finer-block sensitivity

Within hours of the v2 deposit on Zenodo (DOI 10.5281/zenodo.20474028), a substantive peer-review response was received privately. The reviewer agreed that the v2 work was procedurally sound — the pre-registration discipline, the 26-sigma diagnosis, the escalating null models, the descriptive longitude finding, the separation of statistical and geophysical claims — but identified two specific gaps in the analytical machinery that v2 had not closed, and a framing claim that v2's wording overstated. The reviewer prefers anonymity; their substantive points stand on their merits.

The three points:

1. **Missing latitude look-elsewhere correction.** §10 of the pre-registration corrected for longitude (the 72-meridian min-T scan), but §11(a) tested counts at five specific latitudes with Šidák ×5. The Šidák correction is appropriate only if the five latitudes were a priori independent predictions. The data owner conceded in his v2 Appendix A commentary (point 3) that Poles II–V were "identified partly through examination of the orientation data." The targets were therefore read off the same intersection-latitude distribution against which they were being tested — the identical researcher-degree-of-freedom that motivated the longitude scan, left uncontrolled on the latitude axis.

2. **Pseudoreplication in the block-conditional null.** §11(d)'s within-block shuffle treats all 539 Americas structures as exchangeable. Orientations within architectural traditions are spatially autocorrelated; a single tradition (e.g. a cluster of Mesoamerican sites) shares a convention, so dozens of sites carry near-identical bearings. Treating these as exchangeable inflates the effective sample size in the null and over-disperses it, making the observed concentration appear more surprising than it should against a properly autocorrelated baseline. The data owner had raised the inverse concern (Appendix A point 2: that within-block shuffling destroys a cross-regional signal); both worries point to the same lever — block granularity is doing heavy lifting at n=7.

3. **The v2 framing overstates what was shown.** The v2 abstract led with "robust within-hemisphere clustering at Poles II and III." Given the data-derived nature of the targets and the missing controls in points 1 and 2, the honest characterization is "data-derived peaks reproduce under independent geometry and survive several nulls, pending latitude look-elsewhere correction and a finer-blocking sensitivity check." V2 also separated what is geometrically one broad concentration (Poles II and III are 3.8° apart; their ±1.5° windows nearly abut) into two distinct findings, when the natural unit is one ~7°-wide peak holding ~24% of the sample.

The first two points are testable with the existing infrastructure. Two new exploratory scripts were drafted, reviewed for correctness against the reviewer's specification, run with the same random seed (20260517) and M = 10,000 as the pre-registered analyses, and committed to the repository on 1 June.

### Script 07: latitude look-elsewhere control

`analysis/07_latitude_lookelsewhere.py` scans the populated northern range (45–89°N PRIMARY, 45–90°N WIDE) at 0.25° step, and under each null records the *maximum* count in any ±1.5° window across the scan. The look-elsewhere-corrected p-value is then computed as the probability that this null T_max distribution produces a window as full as the observed Pole II / Pole III window count.

Observed: T_max at 72.00°N with 119 structures. Pole II window (76°N) holds 115 adjacent. Pole III window (72.2°N) is essentially the T_max — confirming that the data's strongest concentration is at the Pole III latitude.

Latitude-LEE-corrected p-values, three nulls:

| Null model | Null T_max mean | p_II (115) | p_III (119) |
|---|---|---|---|
| Unconditional | 93.3 | 0.0001 | 0.0001 |
| Conditional (global within-hemisphere) | 121.2 | **0.999** | **0.905** |
| Block-conditional (within-block within-hemisphere) | 110.4 | 0.0043 | 0.0003 |

The unconditional row is still dominated by hemisphere-mismatch and uninterpretable in isolation, as v2 established.

The conditional row is the most decisive single result. Under the global within-hemisphere null — the one that preserves the only constraint v2 established as mandatory (the northern-hemisphere inclusion criterion), and which imposes no assumption about block structure — the null's *maximum* window count anywhere in the scan range averages 121.2, slightly above the observed peak of 119. Free reshuffling of hemisphere-compatible bearings produces a fuller window somewhere than the observed peak, more often than not. Once the freedom to choose which latitude to call a pole is accounted for, the observed concentration is not significant; for Pole II it is essentially typical (p = 0.999), for Pole III it is slightly worse than typical (p = 0.905).

The block-conditional row produces small p-values, but its interpretation now requires care: it imposes within-block exchangeability, which the next script demonstrates is a stronger assumption than the data supports.

### Script 08: finer-block sensitivity

`analysis/08_finer_block_sensitivity.py` runs the §11(a) per-pole test under the block-conditional null at three granularities. The `coarse` scheme (8 blocks) reproduces the v2 §11(d) result and serves as a validation of the within-block swap chain (which uses block-proportional proposal weighting rather than v2's global proposal with rejection). The `americas_split` scheme splits the Americas (n=539) by latitude into North American (n=6), Mesoamerican (n=371), and Andes/S.America (n=162). The `fine` scheme additionally splits Middle East and Europe-Med.

Trend table:

| Scheme | n_blocks | Pole II null mean | Pole II obs | Pole II p-Šidák | Pole III null mean | Pole III obs | Pole III p-Šidák |
|---|---|---|---|---|---|---|---|
| coarse | 8 | 90.2 | 115 | 0.0010 | 90.8 | 119 | 0.0005 |
| americas_split | 10 | 100.8 | 115 | 0.0452 | 100.1 | 119 | 0.0080 |
| fine | 12 | 101.8 | 115 | 0.0571 | 99.5 | 119 | 0.0030 |

Validation: `coarse` produces II=0.0010, III=0.0005, matching script 06's 0.0015 and 0.0005 to within Monte Carlo error. The within-block swap chain is working correctly.

The substantive result is what happens to the null means as blocks get finer:

- Pole II null mean: 90.2 → 100.8 → 101.8.
- Pole III null mean: 90.8 → 100.1 → 99.5.

This climb of ~10 structures in each null mean *is* the pseudoreplication, made quantitative. With the Americas constrained to keep its bearings within its three sub-regions (especially the dominant Mesoamerican sub-block of 371 sites), the null already piles ~100 structures into the high-north band by itself — because mid-latitude near-cardinal sites project there geometrically and the Mesoamerican bearings, held inside Mesoamerica, are no longer randomly redistributable across the entire western hemisphere.

Decomposition of the apparent excess:

- Pole II: under `coarse`, excess = 115 - 90 = 25 structures over null mean. Under `fine`, excess = 115 - 102 = 13. About 48% of the apparent Pole II excess was driven by within-Americas exchangeability rather than cross-regional structure.
- Pole III: under `coarse`, excess = 119 - 91 = 28. Under `fine`, excess = 119 - 99 = 20. About 32% of the apparent Pole III excess was within-Americas exchangeability.

Pole II crosses out of significance under the fine scheme (p = 0.0571, just above 0.05). Pole III weakens by ~6× but holds as a ~3σ residual (p = 0.0030).

§11(b) assignment match remains p = 0.0001 across all three schemes, consistent with the v2 §3.6 interpretation (the test is largely tautological: it measures pipeline agreement and within-hemisphere latitude-band structure, not pole-pointing).

### Substantive interpretation

Taken together, the two scripts substantially retract the v2 characterization of "robust clustering at Poles II and III":

**Pole II is not robust.** It fails both post-publication controls. Under the global conditional null with look-elsewhere correction it is entirely typical (p ≈ 0.999). Under finer geographic blocking it falls to p ≈ 0.057. Pole II is consistent with a look-elsewhere-plus-autocorrelation artifact.

**Pole III is a null-dependent residual.** It survives the block-conditional nulls with look-elsewhere correction (p ≈ 0.0003 coarse, p ≈ 0.003 fine) and remains a ~3σ effect under finer blocking. But it does not survive the global conditional null with look-elsewhere correction (p ≈ 0.90), and it weakens monotonically as blocking better captures spatial autocorrelation. Its survival depends entirely on which null model is treated as the relevant baseline.

The block-conditional null is the more stringent test in one direction (it imposes more independence structure than free reshuffling) and the less appropriate test in another (it treats spatially autocorrelated sub-traditions as exchangeable). At the relevant granularity, it manufactures significance for the v2 framework's claims by over-dispersing the null. The data owner argued in his v2 Appendix A commentary that the block-conditional null was biased against his hypothesis. The post-publication analysis shows the opposite: at the coarse granularity used in v2, it was biased *toward* significance for his hypothesis by treating autocorrelated Mesoamerican sites as exchangeable. Under finer blocking that better respects the autocorrelation structure, the apparent signal attenuates.

The "one peak, not two" framing is also now numerically supported. The observed T_max is at 72°N, with the adjacent 76°N window containing 115 structures. These are not two distinct concentrations; they are one broad concentration centered near 72-73°N, spanning roughly 70-78°N, that v2 reported as two findings because the framework's specification carved this continuous concentration into two named poles.

### Methodological lessons

The v2 report identified one methodological lesson (pre-register selection effects, not just the final test statistic). The post-publication analysis extends this to three:

1. **Pre-register the full data-processing pipeline, including all selection criteria** (the original v2 lesson). The 26-sigma artifact arose because the pre-registered null did not preserve the in-range hemisphere selection.

2. **When testing targets are data-derived rather than a priori, simple multiple-comparisons corrections like Šidák are insufficient.** A continuous look-elsewhere control over the actual search space is required. The Šidák ×5 correction in v2 §11(a) treated five data-derived latitudes as independent predictions; the correct correction was the latitude look-elsewhere null implemented in script 07.

3. **In spatially or culturally autocorrelated data, the granularity of any blocking null is itself a researcher degree of freedom.** Coarse blocks treat autocorrelated sub-traditions as exchangeable, inflating the apparent effect size; finer blocks that better respect the autocorrelation structure produce more honest nulls. The right granularity is "the granularity at which observations are actually independent," which in archaeological data is closer to "tradition" than to "continent."

### What follows

A v3 update of the Zenodo record will be drafted in the coming days, incorporating:

- A new results section (likely §3.8) reporting the latitude look-elsewhere and finer-block sensitivity analyses.
- Revisions to §3.5 (per-pole results) and §4.7 (conclusion) to retract the v2 "robust clustering at Poles II and III" characterization and replace it with the "Pole II not robust; Pole III null-dependent residual" framing.
- Expansion of §4.4 (methodological lessons) from one to three lessons.
- A brief preface to v3 noting the post-publication review and the changes incorporated.
- A response to the data owner's Appendix A point 2 specifically, noting that the post-publication finding inverts his concern about the block-conditional null's bias direction.

The v3 deposit is targeted for approximately 4-5 June 2026 — three to four days after v2, to give the data owner time to absorb v2 in its full form before v3 changes the framing of his framework's specific claims, and to allow the v3 writeup to be drafted carefully rather than rushed.

This is not a retraction of v2. V2's analyses are correct as run, its provenance chain is intact, and the methodological discovery (the 26-sigma artifact) remains a substantive contribution. V3 adds two more analyses that refine the framing of what v2 demonstrated. The pre-registration discipline is doing exactly what it was designed to do: catching the work's own gaps before they accumulate in the public record.

---

## 2026-06-04 — v3 decision gate: scripts 09 and 10; clean null finding at all proposed poles

The 1 June log entry left v3 in a preliminary framing of "Pole II not robust, Pole III null-dependent residual." That framing was provisional: it rested on a single observed asymmetry (the global conditional null with look-elsewhere gave p_III ≈ 0.90, while the block-conditional null with look-elsewhere gave p_III ≈ 0.0003) that had not been mechanistically explained. Before drafting the v3 writeup, the post-publication reviewer correctly identified that asymmetry as a gate, not a finding, and recommended a combined-controls check before publication. Two scripts were drafted, reviewed for correctness against their respective specifications, run with the standard seed (20260517) and M = 10,000, and committed on 4 June.

### Script 09: latitude look-elsewhere under finer-block nulls

`analysis/09_lookelsewhere_under_finer_blocks.py` applies both post-publication controls simultaneously: the latitude look-elsewhere statistic from script 07, computed under the finer-block nulls from script 08. The `coarse` row reproduces script 07's block-conditional LEE p-values within Monte Carlo error (p_II = 0.0050 vs 07's 0.0043; p_III = 0.0001 vs 07's 0.0003), validating the wiring.

Trend across granularity (PRIMARY range, latitude-LEE-corrected):

| Scheme | Null T_max mean | p (Pole II, 76°N) | p (Pole III, 72.2°N) |
|---|---|---|---|
| coarse | 110.4 | 0.0050 | 0.0001 |
| americas_split | 110.9 | 0.0727 | 0.0122 |
| fine | 110.8 | 0.0656 | 0.0108 |

Pole II fails the combined controls cleanly: 0.0050 → 0.073 → 0.066, stable above 0.05. Pole III's per-pole p climbs from 0.0001 to 0.0108 between `coarse` and `americas_split`, then stalls — the `fine` step (splitting the Middle East and Europe-Med) produced essentially no change. Two mechanistically important features of this table are worth flagging:

**The null T_max mean is flat.** It stays at ~110 across all three schemes. The pseudoreplication story predicted the null mean would rise toward the observed 119 as finer blocking better constrained the bearings — that mechanism did not fire. The climb in p_III came from the upper tail of the null distribution widening, not from the centre moving.

**The fine step did nothing because it never touched the block where Pole III lives.** A diagnostic cross-tabulation of Pole III's site-level contributors against the fine-block labels shows: 64 of Pole III's 119 contributors are in Am:Mesoamerica, a single 371-site block that neither 08 nor 09 ever split. The `fine` scheme split the Middle East and Europe-Med (~1 Pole III contributor in each), while Mesoamerica remained intact. Script 09 was not testing the block that mattered.

This left the global-vs-block asymmetry unresolved — the block-conditional null was producing significance for Pole III that the assumption-light global null did not show, and the explanation was likely the autocorrelation structure of Mesoamerican architectural orientations (a well-documented phenomenon in the Aveni/Šprajc literature), but the test for this had not yet been run.

### Script 10: spatial-cluster null (assumption-light pseudoreplication control)

`analysis/10_spatial_cluster_null.py` removes the block-exchangeability assumption directly. Sites are grouped via single-linkage connected components into spatially coherent clusters (any two sites within a distance threshold are linked), each cluster is collapsed to a single representative (the real site nearest the cluster centroid — no angular averaging), and the global conditional null with latitude look-elsewhere correction is run on the representatives. The effective sample size becomes the number of independent spatial clusters, which is the standard pseudoreplication fix. The distance threshold is swept across 25, 50, 75, and 100 km so it is not a hidden researcher degree of freedom.

Result (PRIMARY range, global conditional null with LEE correction on cluster representatives):

| Threshold | Clusters | Pole III contributors | Pole III p (per-pole, no LEE) | Pole III p_LEE |
|---|---|---|---|---|
| 25 km | 286 | 25 clusters (from 119 sites) | 0.1360 | **1.0000** |
| 50 km | 210 | 17 clusters | 0.3140 | **1.0000** |
| 75 km | 173 | 13 clusters | 0.4911 | **1.0000** |
| 100 km | 144 | 10 clusters | 0.4107 | **1.0000** |

Pole II shows the same pattern: per-pole p climbs from 0.010 at 25 km to 0.056 at 100 km, with p_LEE = 1.0000 at every threshold.

The result is stable across the entire 25-100 km threshold sweep. Single-linkage chaining is not driving it: the largest cluster grows from 64 sites at 25 km to 244 at 100 km (as expected from chaining behaviour), and the conclusion does not change. The per-pole p drifting around with threshold while p_LEE pins at 1.0 is the signature of noise, not signal.

The mechanism is visible in the cluster counts. At the tightest threshold (25 km, the most conservative against over-clustering), the 119 site-level "contributors" to Pole III collapse to 25 independent clusters (representing 106 of the 119 sites; 13 sites in singleton clusters scattered elsewhere). Against this, the null's typical maximum window count across the scan range averages 37. The site-level 119 was never 119 independent observations — it was a handful of dozens of spatial units, replicated.

A diagnostic at the 25 km threshold breaks the 25 Pole III clusters down by region:

| Region | Clusters | Sites in those clusters |
|---|---|---|
| Am:Mesoamerica | 5 | 42 (includes one 29-site cluster in northern Yucatán, ~20.3°N, 89.6°W) |
| ME:west | 7 | 16 |
| Med:south | 6 | 12 |
| Eur:north | 4 | 8 |
| Am:Andes/S.Am | 1 | 12 (single Andean coastal cluster) |
| Oceania/SE Asia | 1 | 2 |
| South Asia | 1 | 1 |

The Americas supply 54 of 106 sites in Pole III clusters but only 6 of 25 independent clusters. The site-level concentration was inflated chiefly by a few dense American clusters being counted as separate observations — most strikingly, a single 29-site cluster in the northern Yucatán entering the v2 §11(a) test as 29 independent points.

### Substantive interpretation

The asymmetry that motivated this gate is now mechanistically explained. The global conditional null (script 07, p_III = 0.90) was the correct test: with hemisphere preservation enforced but no exchangeability assumption beyond that, the observed peak does not exceed what free reshuffling produces somewhere in the scan range. The block-conditional null (06/07/08/09 coarse) produced apparent significance by treating spatially autocorrelated sites as exchangeable, particularly the dense Mesoamerican cluster carrying ~24% of the apparent Pole III contributors. The spatial-cluster null (script 10) is the assumption-light test that confirms the global null was correct: with autocorrelation removed by collapsing to clusters, no proposed pole shows excess clustering at any threshold.

The v2 finding of "robust clustering at Poles II and III" does not survive the controls identified in post-publication review. Both poles are consistent with the null:

- **Pole II** is consistent with a look-elsewhere-plus-autocorrelation artifact. Under the combined controls (latitude LEE under finer blocking, script 09; spatial-cluster null, script 10), it does not reach significance at any threshold.
- **Pole III**, which the 1 June log entry characterized as a null-dependent residual, dissolves under script 10. The block-conditional nulls that previously sustained it were artifacts of the within-block exchangeability assumption, which the spatial-cluster null removes directly.
- **The §11(b) assignment match** remains p = 0.0001 at the site level across all nulls, but the v2 report already established (§3.6) that this test is largely tautological — it measures pipeline agreement and within-hemisphere latitude-band structure, not pole-pointing. It is not independent evidence of clustering at the proposed poles.

This is a clean null finding at every proposed paleopole.

### Methodological lessons (revised)

The v2 report identified one methodological lesson. The post-publication analysis extends this to four, one per script in the post-publication sequence:

1. **Pre-register the full data-processing pipeline including selection criteria.** Selection effects that operate before the registered test can produce arbitrarily large apparent significance. (V2 lesson, from the 26-sigma artifact.)
2. **When testing targets are data-derived rather than a priori, simple multiple-comparisons corrections are insufficient.** A continuous look-elsewhere control over the actual search space is required. (Script 07.)
3. **In spatially or culturally autocorrelated data, the granularity of any blocking null is itself a researcher degree of freedom.** Block nulls are only as honest as the blocks that constitute them; the right granularity is the granularity at which observations are actually independent. (Scripts 08 and 09.)
4. **The honest independence unit in spatially autocorrelated data is the cluster, not the site.** A spatial-cluster null, with the threshold swept rather than fixed, removes the granularity-choice degree of freedom and provides an assumption-light pseudoreplication control. (Script 10.)

### What follows

V3 of the Zenodo record will be drafted in the next day, with deposit targeted for 4-5 June 2026. The framing changes from the preliminary v3 sketched in the 1 June log entry: the conclusion is now a single line rather than a two-tier statement.

> Under controls for both latitude look-elsewhere and spatial autocorrelation, no proposed paleopole shows clustering distinguishable from chance. The v2 result does not survive controls identified in post-publication review.

This is not a retraction of v2. V2's analyses are correct for the nulls it ran. The pre-registered protocol caught a real methodological issue (the 26-sigma artifact), the analysis identified two more issues (latitude look-elsewhere and pseudoreplication) that the controls applied during v2 had not addressed, and the v3 controls complete the picture. The pre-registration discipline is doing what it was designed to do: identifying the work's own gaps before they accumulate in the public record.

Mario Buildreps has been notified that v3 is imminent, in a response to his closing reply of 4 June acknowledging the v2 publication. His v2 Appendix A commentary remains preserved verbatim. A brief note in v3 Appendix B will address his Appendix A point 2 specifically: he argued the block-conditional null was biased against his hypothesis. The spatial-cluster null is the assumption-light version of what he was implicitly asking for; it removes the apparent signal rather than restoring it.

---

## 2026-06-05 — v3 finalised and deposited

The v3 report has been finalised, rendered, GPG-signed, and OpenTimestamped.

**PDF SHA-256:** `0661bba4709c90591056a43904589c4cfb5d880cc2ddc50c37b55151b78f3e40` (replace with actual)

**Bitcoin attestations (upgraded 5 June 2026 after block confirmation):**

- `writeup/results_v1.0.pdf.ots` — Bitcoin block **952402**, merkleroot `7aab6dd40936b73eab49a662811b05d988045909a5f374281b11c72c1df89b8e`
- `writeup/results_v1.0.pdf.asc.ots` — Bitcoin block **952402**, merkleroot `7aab6dd40936b73eab49a662811b05d988045909a5f374281b11c72c1df89b8e`

**Zenodo deposit:**

- Version 3 DOI: `10.5281/zenodo.20546301`
- Deposited 5 June 2026
- Supersedes version 2 (10.5281/zenodo.20474028)

**Corrected conclusion:** Under controls for both latitude look-elsewhere (assumption-free conditional null) and spatial autocorrelation (spatial-cluster null), no proposed pole shows clustering distinguishable from chance. Pole II p = 0.999, Pole III p = 0.90 under the global conditional null with look-elsewhere; both poles p = 1.0 under the spatial-cluster null with look-elsewhere (25–100 km thresholds). The v2 characterisation of "robust clustering at Poles II and III" is withdrawn.

Version 2 remains available as a prior version. The pre-registration (10.5281/zenodo.20258204) and the v2 analyses are unchanged. The transition from v2 to v3 is documented in Appendix B and in this analysis log.

This entry closes the post-publication review loop initiated on 1 June 2026. The project's documentation is complete.

---

## 2026-06-05 — v3.1 work: script 11 and the scope of point 3

Mario Buildreps replied to the v3 publication notification on 5 June 2026 with a substantive letter raising five concerns. His full letter is preserved verbatim as Appendix D of the v3.1 report; the analytical work prompted by it is recorded here. The decision to undertake a v3.1 update rather than respond purely by correspondence was made after Opus 4.8 post-publication review (see correspondence) of an initial draft response; the review revised the framing of which points required concession. The reviewer identified that three of Buildreps' five points were either methodologically incorrect (the asymmetric-ratchet claim in point 5), partly addressed in v3 already (the pre-registration framing in points 1 and 4), or empirically testable in ways that would resolve them rather than negotiate them (the rule-faithfulness claim in point 2 and the cluster-independence claim in point 3).

### Script 11: implementation of Buildreps' stated peak-finding rule

Buildreps' point 2 argued that the latitude look-elsewhere correction in script 07 tested a "caricature" of his method — that he did not scan the latitude axis for the fullest window but applied explicit rule-based criteria from a rules document shared before the database was opened. Script 11 (`analysis/11_data_owner_rule_simulation.py`) implements his rules as specified (minimum 12 structures per degree, clusters extending ≥3 degrees, gaps between clusters indicating discrete poles) and tests them under three null models (uniform, conditional, block-conditional). The script was drafted by the Opus 4.8 reviewer from Buildreps' rules document and verified against his stated thresholds with unit tests before running.

**Results (flat-12 rule variant):**

| Null model | Observed n_poles | Null mean n_poles | p(n_poles ≥ obs) |
|------------|------------------|-------------------|------------------|
| Uniform | 2 | 3.89 | 0.9622 |
| Conditional (global) | 2 | 2.06 | 0.7508 |
| Block-conditional | 2 | 1.38 | 0.3362 |

Buildreps' rule, faithfully implemented, recovers his poles II–V on the observed data (Pole I = no; coverage II = yes, III = yes, IV = yes, V = yes). His rule's claim to recover his proposed poles is therefore not in dispute. The substantive finding is that his rule covers the Pole III latitude band in 10,000 of 10,000 replicates, because the great-circle geometry concentrates intersections in that band regardless of permutation; across replicates the rule finds no more poles overall than in random data (null means 1.38–2.06 vs observed 2). The rule reproduces its observed output, but under realistic nulls that output is not distinguishable from its output on random data.

### Script 11b: diagnosis of the per-degree binomial baseline

A second component of Buildreps' published methodology — the per-degree binomial that produces his "100% probability" and "99.999% probability" claims — was diagnosed in parallel (script 11b within the same module). The binomial compares observed structure counts in each pole's degree-bin against a baseline expectation.

Under Buildreps' published baseline (uniform expectation of ~11 structures per degree across the latitude axis), the p-values are astronomical:

| Pole | Observed in degree-bin | p (uniform baseline) |
|------|------------------------|----------------------|
| I (90.0°N) | 90 | 3.7 × 10⁻⁵¹ |
| II (76.0°N) | 33 | 5.7 × 10⁻⁸ |
| III (72.2°N) | 36 | 1.6 × 10⁻⁹ |
| IV (64.1°N) | 30 | 1.5 × 10⁻⁶ |
| V (52.3°N) | 15 | 0.148 |

Re-running the identical binomial test with the per-degree expectation that the actual site geography produces under the conditional null (a non-uniform expectation reflecting that random great-circle intersections of mid-latitude sites pile in specific latitude bands by geometry):

| Pole | p (conditional baseline) | p (block-conditional baseline) |
|------|--------------------------|--------------------------------|
| I (90.0°N) | 0.672 | 0.522 |
| II (76.0°N) | 0.119 | 0.257 |
| III (72.2°N) | 0.030 | 0.084 |
| IV (64.1°N) | 0.077 | 0.111 |
| V (52.3°N) | 0.324 | 0.637 |

The departure from uniformity is real and unremarkable; it does not measure clustering at the proposed poles. The only marginally significant cell — Pole III at p = 0.030 under the conditional null — is unremarkable in isolation and not significant after multiplicity correction across five poles.

### What script 11 closes; what remains open

Point 2 of Buildreps' letter is addressed. His rule is faithful as published and his binomial is computed correctly, but the published confidence rests on a uniform-sky baseline that does not reflect the per-degree expectation the actual site geography produces. The disagreement was never the rule — it was the baseline against which the rule's output was scored.

Point 3 (the spatial-cluster null's proximity-equals-dependence assumption) is not addressed by script 11. It is empirically testable but requires chronological evidence for the structures in the dominant spatial clusters of §3.8.3 — particularly the 29-site cluster centred near 20.3°N, 89.6°W in the northern Yucatán. The dating evidence must be conventionally derived (radiocarbon, ceramic seriation, epigraphic) rather than orientation-derived, to avoid circularity in testing whether independent cultures arrived at the same orientation versus a single tradition replicating itself across multiple sites.

### Scope decision on point 3

A reviewer-noted scope question was resolved before drafting the response to Buildreps' letter. Adjudicating whether the 29 Yucatán structures represent multiple independent cultures across a millennium versus a single tradition replicated is a Mesoamerican archaeological question, not a statistical-verification one. The pre-registered agreement and the v1-v3 sequence have all been about a specific statistical claim: do intersections cluster at the proposed latitudes more than chance? On that question, four null models converge on no.

The spatial-cluster null's assumption that geographic proximity proxies cultural-temporal dependence is a real limitation, correctly disclosed in v3 §4.5 (now moved to §3.8.3 in v3.1 for placement). Disclosing a limitation is not the same as taking on the obligation to resolve it. The burden of producing chronological evidence belongs to the party making the archaeological claim that those structures are independently dated.

It was decided before contacting him that only model-independent dates (radiocarbon, ceramic seriation, epigraphic) can bear on this question; orientation-derived dates cannot, as they would assume the conclusion under test. This criterion was fixed before his response was received.

If Buildreps supplies model-independent dates showing genuine multi-period multi-polity spread for the 29 sites, v3.1 may be superseded by a v4 that re-runs the cluster null with chronological constraints incorporated. If he supplies orientation-derived dates or no dates, point 3 remains disclosed-but-unresolved from the available evidence, and v3.1's conclusion stands under its explicit assumption.

This scope discipline keeps the project inside the agreement it was registered against and avoids the failure mode of becoming an amateur arbiter of Mesoamerican chronology. The report's job was the statistical question. On that question, the limitation is disclosed, the conclusion is conditional on the assumption, and the assumption is testable by someone with the relevant disciplinary expertise — which is not the author and is not the scope of this report.

### V3.1 deposit

A v3.1 deposit will follow this commit, incorporating §3.8.4 (script 11), the §3.7 summary table updates, the cluster-null limitation paragraph moved into §3.8.3, the Appendix B note on the v3 → v3.1 relationship, and the new Appendix D containing Buildreps' 5 June letter verbatim. The v3.1 Zenodo version will reserve a new DOI; the v3 record at 10.5281/zenodo.20546301 remains accessible as the prior version.

An email to Buildreps will be drafted after the v3.1 commit lands, pointing him at the §3.8.5 result for point 2 (with the named 29-site list for point 3), stating the decision rule for what chronological evidence would resolve point 3 in either direction, and clarifying that the burden of producing the archaeological evidence rests with him as the party making the archaeological claim.

---

## 2026-06-06 — Cluster 26 composition: within-site replication resolved, cross-site convergence open

Following Mario Buildreps' 5 June 2026 letter (Appendix D), the 29-entry cluster (25 km linkage) that dominates the Pole III count was examined in detail.

### Composition of the 29 entries

Extraction from `results/10_cluster_labels.csv` and join to the original database:

| Site | Entries | Bearings |
|------|---------|----------|
| Uxmal | 8 | 31,22,21,19,17,12,11,10 |
| Labna | 6 | 45,23,16,13.5,13,10 |
| Kabah | 6 | 19,15,14.5,13.5,13,12 |
| Chacmultun | 4 | 20,15,14,10 |
| Xlapak | 2 | 20,18 |
| Palenque | 1 | 26 |
| Cancuén | 1 | 24 |
| Sayil | 1 | 14.5 |

*Bearings verified against script output; no transcription errors.*

**The 29 entries correspond to 8 distinct physical locations.** The columns examined (site name, coordinates, bearing, remarks) carry no unique structure identifiers. No date column is present in the main sheet. The sole `Remarks` entry is "2 structures similar oriented" for Sayil, which indicates shared orientation, not independence.

### Geographic note on site names

Two site labels appear inconsistent with their coordinates:
- "Palenque" at ~20.25°N, 89.65°W — the well-known Palenque is in Chiapas at ~17.48°N, 92.05°W. The coordinates given are in the Puuc region.
- "Cancuén" at ~20.2°N — the known Cancuén is in the Petén at ~15.9°N.

This discrepancy does not affect the conclusion that the 29 entries are a small number of locations rather than 29 independent sites; if anything, a mislabel could reduce the distinct-location count further. Flagged for the data owner to confirm.

### Two distinct independence questions

**Within-site replication (resolved by the data).** The multiple bearings from Uxmal (8), Labna (6), Kabah (6), Chacmultun (4), and Xlapak (2) are not independent observations. The spatial-cluster null collapsed them into their physical locations. This part of point 3 is answered directly from the database, without recourse to archaeology. The cluster null was correct to do so.

**Cross-site convergence (open, burden on the data owner).** Whether the 8 distinct locations represent independent cultures converging on the same latitude band, or one shared Maya orientation tradition, is an archaeological question. The database does not contain the metadata to resolve it. The data owner must provide model-independent evidence (unique structure identifiers, radiocarbon/ceramic/epigraphic dates, polity attribution) to justify treating these as independent observations.

Per the criterion fixed before contacting him, only model-independent dates can bear on cross-site independence; orientation-derived dates are excluded as circular.

### Decision rule

- If the data owner provides solid evidence of cross-site independence, a new pre-registered analysis (v4) will be run respecting that independence.
- If no such evidence is provided, the spatial-cluster null stands as the best available control, and point 3 will remain noted in the report as disclosed but unresolved (standing under its stated assumption).

The author's role is statistical verification, not archaeological adjudication. The within-site replication question is settled by the data itself. The cross-site convergence question is the data owner's to answer.

---

## 2026-06-08 — Script 12 pre-commitment: hemisphere-preserving permutation null

The data owner's 8 June 2026 second follow-up letter (correspondence file `2026-06-08_followup_from_mario.md`) raised three further methodological points after conceding that script 11 implemented his peak-finding rule faithfully and that his published binomial figures rest on a baseline the data do not support. Of his three new points, point 1 — that the v3 null models do not preserve the East/West hemispheric bearing asymmetry from which he derived the 47°W meridian — is a substantive methodological question worth running directly rather than answering rhetorically. This entry pre-commits the specification, the decision rule, and the interpretation framework for script 12 (and its companion diagnostic, script 13) before any code is written, so that the readout is not adjustable after the results are seen.

### Background

The data owner's published work (2015, 2020) identifies a systematic clockwise bearing deviation in the Americas and a counterclockwise deviation in the Old World, and derives the 47°W meridian from the convergence of these deviations. He argues that the v3 nulls (script 03b global conditional, script 06 block-conditional, script 10 spatial-cluster) permute bearings in ways that do not preserve this asymmetry, and that the null finding at Poles II and III is therefore unsurprising — the null erases the structure that produces the peaks before testing them.

This is partly correct as a description of the v3 nulls: the global conditional null permutes bearings across all in-range sites with no hemisphere constraint, and the spatial-cluster null permutes at the cluster level globally. The block-conditional null permutes within seven geographic regions, but those blocks are not cut on an East/West line. None of the v3 nulls explicitly preserves an East/West bearing asymmetry as a feature of the null distribution.

Script 12 runs a null that preserves the asymmetry by permuting bearings only within hemispheres, and re-computes the per-pole counts, the latitude look-elsewhere correction, and the cluster-null statistic under this modified null. It is exploratory per pre-registration §12 point 3.

### Hemisphere cut: pre-committed definitions (primary + sensitivity)

The data owner's claim is specifically about the Americas versus the Old World, not about the prime meridian. To preserve the asymmetry he actually describes, the **primary** cut isolates the Americas:

- **Primary cut (Americas / Old World):** Western = longitude in [−180°, −30°); Eastern = longitude in [−30°, +180°]. The −30° line runs through the mid-Atlantic and cleanly separates the Americas (the population carrying his claimed clockwise deviation) from Europe, Africa, and Asia.

- **Sensitivity cut (prime meridian):** Western = [−180°, 0°); Eastern = [0°, +180°]. The conventional geographic definition, run as a robustness check.

Both cuts are run. Rationale for running both: the primary cut matches the data owner's stated asymmetry and so genuinely preserves the feature he says the v3 nulls destroy; the sensitivity cut guards against the objection that the result depends on where the line is drawn. If the peaks dissolve under both cuts, the conclusion is robust to the cut definition.

Cuts derived from the data are explicitly rejected. A cut at 47°W would condition the null on the meridian the data owner derived from the data; a cut at ±20°E would condition it on the attractor longitude observed in the v3 longitude scan (§3.4). Both would condition the null on the conclusion under test. If the data owner's published basis specifies a different cut, this entry will be amended in a follow-up entry, with the change documented before running; amendment after seeing partial results is not permitted.

### Script 12 design

Three nulls, paralleling the v3 nulls with the hemisphere constraint added, run under each of the two cuts above:

1. **Conditional, hemisphere-preserving (12a):** Metropolis swap chain analogous to script 03b, with swaps accepted only between sites in the same hemisphere. Preserves the in-range hemisphere selection and the East/West bearing asymmetry simultaneously.
2. **Block-conditional, hemisphere-preserving (12b):** swap chain analogous to script 06, with blocks intersected with hemisphere (splitting any block that straddles the cut).
3. **Spatial-cluster, hemisphere-preserving (12c):** cluster-level swap chain analogous to script 10, with swaps restricted to within-hemisphere cluster representatives.

For each null the script computes: per-pole counts at Poles I–V (paralleling §3.5); latitude look-elsewhere corrected p-values at Poles II and III (paralleling §3.8.1). **The look-elsewhere maximum-window distribution is computed from the hemisphere-preserving null's own per-degree distribution, not reused from script 07.** Standard seed (20260517), M = 10,000.

**Descriptive output (reported regardless of branch):** the fraction of in-range structures in each hemisphere group under each cut, and the per-hemisphere distribution of intersection latitudes. In particular, the hemisphere membership of the Pole III cluster contributors is reported. If the Pole III contributors are overwhelmingly in one hemisphere, the within-hemisphere null permutes them largely among themselves, making it close to the global null for that pole; this descriptive fact is part of the interpretation and is surfaced explicitly rather than left implicit.

### Three-way decision rule (pre-committed before running)

Applied to the primary (Americas/Old World) cut. The sensitivity cut is reported alongside; if it disagrees with the primary cut, the disagreement is reported and neither is treated as decisive without the circularity diagnostic.

**Branch A (peaks dissolve under the hemisphere-preserving null):** Pole II p_LEE ≥ 0.05 *and* Pole III p_LEE ≥ 0.05 under the hemisphere-preserving conditional null with look-elsewhere correction. The data owner's point 1 is answered on the null he asked for. v3.1 reports the result and the conclusion stands as previously formulated.

**Branch B (peaks survive):** Pole II p_LEE < 0.05 *or* Pole III p_LEE < 0.05. The circularity diagnostic (script 13, below) is run before any substantive conclusion. Two sub-branches, decided by the diagnostic's reported fraction:

- **B1 (asymmetry geometrically entailed):** the preserved asymmetry can be reproduced from latitude-clustered intersections alone. Survival under this null is then circular — the null preserves a feature that is itself a consequence of the peaks — and does not vindicate the framework. v3.1 reports the result with the circularity finding.
- **B2 (asymmetry has independent structure):** the asymmetry is not reproduced from latitude clustering alone. Survival is then a genuine result and requires v4 with a new pre-registration specifying how the hemisphere–bearing relationship enters the null. v3.1 still deposits (see stopping rule); v4 is opened in parallel.

**Branch C (mixed):** Pole II and Pole III p_LEE fall on opposite sides of 0.05. Reported pole-by-pole with no aggregate verdict; the diagnostic is run for the surviving pole only, with B1/B2 applied to that pole.

These branches are exhaustive. There is no fourth "the result is ambiguous, run further controls" option; genuine ambiguity is a Branch C outcome and is reported as such.

### Circularity diagnostic (script 13): pre-committed specification

The diagnostic tests whether the East/West bearing asymmetry that the hemisphere-preserving null preserves is itself a geometric consequence of intersections being concentrated at far-northern latitudes on the 47°W meridian, rather than an independent property of how structures are oriented.

**Step 1 — Observed asymmetry.** Compute a deviation-from-true-north measure of bearing per hemisphere (the folded ±45° bearing convention used throughout), and take the difference of hemisphere medians as the observed asymmetry magnitude D_obs.

**Step 2 — Synthetic bearings from the latitude-clustered model.** For each in-range site (real lat/lon), draw a target intersection latitude from the *observed* empirical distribution of intersection latitudes, then compute the bearing carrying that site's great circle to that target latitude on the 47°W meridian. **Multiplicity and existence are resolved by a fixed, model-neutral rule: where more than one bearing reaches the target latitude, take the solution of minimum absolute deviation from true north; where no bearing reaches it, discard the site and report the discarded count.** The minimum-deviation rule is chosen because it does not reference the site's observed bearing (which would reintroduce the quantity under test) and is the same neutral criterion for every site. This yields a synthetic bearing dataset with, by construction, the observed latitude clustering but no independent hemispheric input.

**Step 3 — Synthetic asymmetry.** Compute the same hemisphere-median statistic on the synthetic data: D_synth.

**Step 4 — Report the reproduction fraction R = D_synth / D_obs** (not a binary threshold). Interpretation is pre-committed by range:

- **R ≥ 0.80:** the asymmetry is dominated by geometric entailment → Branch B1.
- **R ≤ 0.20:** the asymmetry has substantial independent structure → Branch B2.
- **0.20 < R < 0.80:** partial. Reported as "the asymmetry is approximately R reproducible from geometry alone." Resolved by a pre-committed secondary criterion: re-run the hemisphere-preserving conditional null on the *synthetic* bearings; if the peaks survive on synthetic data too (which carries only the geometric asymmetry), the surviving signal is geometric → B1; if they do not, the observed survival depended on the non-geometric component → B2.

There is no sampling/inferential framework here (both D quantities are computed once from real or constructed data); R is a magnitude comparison and is reported as such. Script 13 is a separate artifact with its own log entry so its output can be examined independently of the script 12 null result.

### Stopping rule (pre-committed)

Scripts 12 and 13 are the final analyses before the v3.1 deposit, regardless of outcome:

- Branch A → v3.1 deposits as formulated.
- Branch B1 / partial-resolving-to-B1 → v3.1 deposits with the circularity
  finding included.
- Branch B2 / partial-resolving-to-B2 → v3.1 deposits *and* a v4
  pre-registration is opened; the v3.1 deposit is not held for v4.
- Branch C → v3.1 deposits with the pole-by-pole result and per-pole diagnostic.

In every branch, v3.1 deposits after script 12 and 13. Further methodological controls beyond these are v4 territory and require their own pre-registration. This stopping rule is committed now, before results, so that the decision to deposit is not contingent on whether the outcome is favorable.

### What this entry locks in

1. Hemisphere cut: primary = Americas/Old World at −30°; sensitivity = prime meridian at 0°. Both run. Data-derived cuts (47°W, ±20°E) rejected.
2. Three nulls (12a conditional, 12b block-conditional, 12c spatial-cluster), each under both cuts; LEE computed from each null's own distribution.
3. Per-hemisphere descriptive output, including Pole III contributors' hemisphere membership, reported in every branch.
4. Standard seed (20260517), M = 10,000.
5. Three-way decision rule (A / B-with-B1·B2 / C), exhaustive; no fourth run further controls" option.
6. Circularity diagnostic (script 13): hemisphere-median bearing statistic; synthetic bearings with the minimum-deviation solution rule and reported discard count; reproduction fraction R with pre-committed ranges and a secondary criterion for the 0.20–0.80 band.
7. Stopping rule: v3.1 deposits after scripts 12 and 13 in every branch; B2 additionally opens a v4 pre-registration in parallel.

Any deviation from this specification during implementation will be recorded in a subsequent log entry with explicit rationale before the affected step is run. A different hemisphere cut specified by the data owner's published basis is acceptable grounds for amendment before running; deviations after seeing partial results are not.

The scripts will be implemented in collaboration with Claude Opus 4.8 (Anthropic) acting as analytic interlocutor, following this pre-commitment. The author runs the code, verifies the output against the pre-committed branches, and is responsible for the conclusions.

---

## 2026-06-08 — Scripts 12 & 13: hemisphere-preserving null and the asymmetry circularity diagnostic (point 1 closed)

This entry records the results of scripts 12 and 13, run under the pre-commitment of the 2026-06-08 entry above, in response to point 1 of the data owner's second follow-up (`2026-06-08_followup_from_mario.md`): that the v3 null models do not preserve the East/West hemispheric bearing asymmetry from which he derived the 47°W meridian, and therefore erase the peak-generating structure before testing.

### Script 12 — hemisphere-preserving permutation null (Branch C)

Bearings were permuted only within hemispheres (preserving the per-hemisphere bearing pool, hence the asymmetry), under both pre-committed cuts (primary −30° Americas/Old World; sensitivity 0° prime meridian), for three nulls (conditional 12a, block-conditional 12b, spatial-cluster 12c). Seed 20260517, M = 10,000. Look-elsewhere computed from each null's own window distribution.

Per-pole, primary cut, look-elsewhere corrected:

| Null | Pole II p_LEE | Pole III p_LEE |
|------|---------------|----------------|
| 12a conditional (site) | 0.4602 | 0.0135 |
| 12b block-conditional × hemisphere | 0.0056 | 0.0005 |
| 12c spatial-cluster (25 km) | 0.0629 | 1.0000 |

Decision (12a, primary cut): Pole II p_LEE = 0.46 (dissolves); Pole III p_LEE = 0.0135 (survives) → **Branch C**, so the circularity diagnostic was run for Pole III only.

Two findings frame the surviving pole. First, the descriptive composition: the Pole III contributors split 73 West / 46 East under the −30° cut (78/41 under 0°) — it is not a single-hemisphere phenomenon, contrary to the premise of point 1. Second, 12c: once spatially proximate structures are collapsed to one unit each *and* the hemispheric asymmetry is preserved, Pole III dissolves completely (p_LEE = 1.0; per-pole 0.0001 → 0.19). The 12a survival is carried by within-cluster replication, not by the asymmetry. (12b reproduces the committed block-conditional result, 0.0005, confirming the grouping machinery.)

### Script 13 — asymmetry circularity diagnostic (Branch B1)

The diagnostic tests whether the East/West asymmetry that 12a preserves is itself a geometric consequence of intersections clustering at far-northern latitudes. Synthetic bearings were reconstructed (min-deviation-from-north solution, verified by forward evaluation, sites unable to reach an assigned target discarded) to reproduce the observed *latitude* distribution with no hemispheric input.

  D_obs = +34.0° (−30° cut), +33.0° (0° cut)
  D_synth (median over 1,000 reconstructions) = +32.7° / +32.2°
  R = D_synth/D_obs = 0.96 / 0.97  [5–95%: 0.92–1.02]
  Uniform-target reference R = 1.14 / 1.15
  Mean discards 16.5%
  → R ≥ 0.80 at both cuts → **Branch B1**.

The hemispheric bearing asymmetry is reproduced (~96%) from the latitude distribution plus geometry alone, with no hemispheric input — and is reproduced even from uniform targets (reference R > 1). Because bearing 0 = true north sends a great circle through the pole, reaching a far-northern target forces a small deviation whose sign is fixed by the site's longitude relative to −47.1°; the East/West asymmetry is the aggregate of that geometric necessity. The Pole III survival under the hemisphere-preserving null (12a) is therefore **circular**: the null preserves a feature entailed by the peak it is meant to test. This does not vindicate the framework.

Two elaborations of the locked spec, recorded as elaborations not deviations: R is reported as a distribution over 1,000 reconstructions (median as headline) rather than a single construction; and a uniform-target reference R is reported as supplementary context. Neither changes the locked decision rule.

### Disposition of point 1, and the close of the exchange

Point 1 is answered three independent ways: (a) the Pole III contributors are not single-hemisphere (73/46); (b) preserving the asymmetry and collapsing replication together (12c) dissolves Pole III entirely; (c) the asymmetry itself is geometrically entailed by the latitude clustering (13, R = 0.96), so its preservation cannot be evidence for a pole. Point 2 was conceded by the data owner (script 11). Point 3's within-site half is resolved from the database (the 29 entries are 8 locations); its cross-site half requires model-independent dates the data owner states do not exist, so it remains disclosed-but-unresolved under the standing decision rule.

Per the pre-committed stopping rule, scripts 12 and 13 are the final analyses before the v3.1 deposit. v3.1 deposits regardless of further correspondence. Branch B1 does not trigger v4. Should the data owner respond again, the response will be recorded and assessed, but no further analysis is undertaken at this stage: no remaining point bears on the statistical question that is not already answered.
