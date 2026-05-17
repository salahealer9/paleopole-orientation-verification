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

The null distribution mean of ~56° corresponds approximately to "typical permuted intersection at latitude −20° to −30°, average distance to nearest pole in [52.3°, 90°] is ~75° — softened by some fraction landing near a pole." This null is dominated by "permuted intersections that fell in the southern hemisphere," not by "permuted intersections that fell at non-special northern latitudes."

### What the pre-registered null actually tests vs. what we wanted to test

**What §7 implements**: given the 994 (lat, lon, bearing) triples from the observed in-range set, are random re-pairings of bearings to sites consistent with the observed concentration near the five proposed pole latitudes?

**Result**: very strongly no. Random re-pairings produce mostly southern-hemisphere intersections. The observed data does not.

**What we intended to test**: given that the orientations are non-random in a way that produces predominantly northern-hemisphere intersections, are those intersections clustering more tightly at the five specific paleopoles than expected?

**The pre-registered null does not isolate this question.** It rejects the broader hypothesis that bearings are randomly paired with sites, which is true but is a weaker and less informative finding than the framework's specific claim.

### Decision

Per pre-registration §12 point 4 ("Method changes after seeing the data are prohibited"), I will not revise §7 or deposit a v1.2 of the pre-registration after seeing the data. The pre-registered analysis is the analysis I committed to, and its result (p = 0.0001, "highly significant" under §9) stands as the pre-registered confirmatory finding.

The interpretive limitation will be reported transparently in the final writeup. The pre-registered finding will be characterised accurately: it rejects the null that "any random reassignment of bearings produces this much northern-hemisphere concentration," which is a meaningful but weaker statement than "the bearings cluster around the five specific proposed poles more than other plausible explanations predict."

Per pre-registration §12 point 3 ("No new tests will be added post-hoc without clear labeling"), I will additionally implement and run a **conditional null Monte Carlo** that preserves the in-range property of the observed data. This is an **exploratory** analysis in the formal sense — it was not pre-registered and is run after seeing the data. It addresses what the pre-registered null was *intended* to test but failed to isolate. Its result will be reported alongside the pre-registered result with the explicit labeling required by §12 point 3.

The script for the exploratory conditional Monte Carlo will be `03b_conditional_null_exploratory.py`. The conditional null will be specified as: rejection-sample bearing permutations until one produces 994 in-range intersections (per the data owner's classification criterion applied to the permuted data), then compute T from those 994. This null preserves both the marginal bearing distribution and the in-range property.

---