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


