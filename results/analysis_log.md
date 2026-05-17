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
