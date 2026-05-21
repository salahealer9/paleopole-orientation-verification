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
