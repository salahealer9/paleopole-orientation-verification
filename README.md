# Paleopole Orientation Verification

[![Zenodo record (latest version)](https://zenodo.org/badge/DOI/10.5281/zenodo.20258203.svg)](https://doi.org/10.5281/zenodo.20258203)

An independent, pre-registered statistical test of the claim that the orientations of ancient pyramids, temples, and megalithic structures cluster around proposed former geographic pole positions located along the ~47°W meridian.

## Status

**Final report v3.1 published 8 June 2026.** The pre-registered protocol committed on 17 May 2026 has been executed in full. The 14-day pre-publication notice window has closed with the data owner's formal commentary incorporated. Post-publication review by a Claude Opus 4.8 (Anthropic) external reviewer identified two further methodological controls, which have been applied in v3; v3.1 adds three further analyses (scripts 11–13) responding to the data owner's 5 and 8 June 2026 follow-up letters. All publication artifacts are GPG-signed and OpenTimestamped on the Bitcoin blockchain.

The Zenodo record has four versions:

| Version | Date | Description | Version DOI |
|---|---|---|---|
| 1 | 17 May 2026 | Pre-registration of the statistical protocol | [10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204) |
| 2 | 1 June 2026 | Final report (initial) — superseded by v3 | [10.5281/zenodo.20474028](https://doi.org/10.5281/zenodo.20474028) |
| 3 | 5 June 2026 | Final report — withdraws v2 finding following post-publication review (superseded by v3.1) | [10.5281/zenodo.20546301](https://doi.org/10.5281/zenodo.20546301) |
| 3.1 | 8 June 2026 | Final report (current) — adds scripts 11–13 in response to data-owner follow-up; conclusion unchanged | [10.5281/zenodo.20593690](https://doi.org/10.5281/zenodo.20593690) |

The concept DOI [10.5281/zenodo.20258203](https://doi.org/10.5281/zenodo.20258203) always resolves to the latest version. The corresponding GitHub release tags are `prereg-v1.1`, `report-v1.0` (v2), `report-v3.0` (v3), and `report-v3.1` (current).

## Background

Mario Buildreps has compiled a database of ~1,159 ancient structures worldwide and proposes that their orientations cluster around five paleopole positions located along the ~47°W meridian. The full framework, including the proposed pole coordinates, the binomial-test methodology, and supporting visualizations, is documented at [mariobuildreps.com](https://www.mariobuildreps.com/).

This repository contains an independent verification of the central empirical claim using Monte Carlo simulation against geographically-realistic null models. The analysis was **pre-registered before the database was opened**, to ensure that the methodology could not be adjusted after seeing the data.

## What this project tests

A single, narrow empirical claim:

> The orientations of ancient structures in the database cluster around the five proposed pole positions more than expected under random orientations applied to the same geographic distribution of sites.

This project does **not** test, validate, or refute any broader interpretive claims (Earth expansion, crustal deformation, the dating of human civilization, climate science, etc.). Those are separate questions outside the scope of an orientation-clustering statistical test, as discussed in §4.3 of the final report.

## Summary of findings

V2 of this report (deposited 1 June 2026) found apparent within-hemisphere clustering at Poles II (76°N) and III (72.2°N) that survived all four pre-registered and exploratory null models tested, and characterised it as robust. **Post-publication review identified two further controls that had not been applied:** a latitude look-elsewhere correction (the latitude analogue of the meridian look-elsewhere already in §10 of the protocol), and a spatial-cluster null that treats nearby structures as one independent unit rather than counting each site as an independent observation. Under both controls applied together, **no proposed pole shows clustering distinguishable from chance.** V3 (deposited 5 June 2026) withdraws the v2 finding.

Specifically (v3, current):

- **Under the assumption-free conditional null with latitude look-elsewhere correction:** Pole II p = 0.999, Pole III p = 0.90. Once the freedom to choose which latitude to call a pole is corrected for, the observed concentrations are no greater than free reshuffling of hemisphere-compatible bearings produces somewhere along the latitude axis.
- **Under the spatial-cluster null with the same correction:** both poles return p = 1.0 at every linkage threshold from 25 to 100 km. The 119 site-level contributors to the Pole III window reduce to 25 independent clusters at 25 km threshold, the largest a single 29-site Mesoamerican cluster in the northern Yucatán.
- **Poles I (90°N), IV (64.1°N), and V (52.3°N)** show no excess concentration under any principled null model. This finding is unchanged from v2.
- **The pre-registered aggregate test statistic** showed an apparent 26-sigma effect under the unconditional null; diagnostic analysis (v2/v3 §3.2) showed this to be an artifact of hemisphere-selection in the in-range subset (99% northern by selection vs ~54% northern under free permutation). Under properly-conditioned nulls, the aggregate effect is null. This finding is unchanged from v2.
- **The data owner's published "100% probability" claims at Poles I-III and "99.999%" at Poles IV-V are not supported** for any pole.
- **The site-to-pole assignment match rate** (46% vs ~9% expected) is robust under all null models, but reflects agreement between our independent geometry and the data owner's pipeline (within 0.1° for 95.7% of structures) together with the within-hemisphere concentration of intersections — not the pole positions. It is not independent evidence for the framework.
- **The broader interpretive claim** that the observed clustering represents former geographic pole positions is not tested by this analysis and requires independent geological evidence to evaluate.

The current report (v3.1) is at [10.5281/zenodo.20593690](https://doi.org/10.5281/zenodo.20593690).

## Methodology

The pre-registration document at `preregistration/preregistration_v1.1.md` is the authoritative specification of the original protocol. In summary, the analysis applies four pre-registered or exploratory null models and three post-publication controls:

**Pre-registered or v2-era nulls:**

- **Test statistic**: T = mean of per-structure minimum angular distance to the nearest of the five proposed poles, on the structure's great-circle intersection with the 47°W meridian. Binning-free.
- **Pre-registered unconditional null**: random permutation of folded bearings across in-range sites, preserving site geography and the empirical bearing distribution (scripts 03, 04, 05).
- **Exploratory conditional null** (added after diagnostic): Metropolis swap chain preserving the in-range hemisphere property by construction (script 03b).
- **Pre-registered block-conditional null** (§11(d)): within-block permutation across seven geographic regions, with the in-range property preserved (script 06).
- **Longitude look-elsewhere control** (§10): longitude scan at 5° resolution with minimum-T null distribution (script 04).
- **Per-pole confirmatory test** (§11(a)): structure counts within ±1.5° of each proposed pole, Šidák-corrected (script 05).
- **Site-to-pole assignment test** (§11(b)): match rate between independent geometry and data-owner pipeline (script 05).

**Post-publication controls (v3, exploratory per §12 point 3):**

- **Latitude look-elsewhere** (script 07): the latitude analogue of the meridian look-elsewhere, scanning a ±1.5° window across the populated northern range (45–89°N) and recording the maximum window count per null iteration.
- **Finer-block sensitivity** (scripts 08, 09): per-pole test re-run at progressively finer block granularities (coarse → americas_split → fine), with and without the latitude look-elsewhere correction.
- **Spatial-cluster null** (script 10): single-linkage spatial clustering of nearby sites (25–100 km thresholds), with the per-pole test computed on cluster representatives.
- **Data-owner rule simulation** (script 11): implements the data owner's own peak-finding rule and per-degree binomial under realistic nulls (v3.1 post-publication).
- **Hemisphere-preserving null + circularity diagnostic** (scripts 12–13): permutes bearings within hemispheres to preserve the East/West asymmetry, and tests whether that asymmetry is geometrically entailed by the latitude clustering (v3.1 post-publication).

Monte Carlo iterations: M = 10,000 throughout. Random seed: 20260517. Reproducible from the database file.

## Repository structure

```
paleopole-orientation-verification/
├── README.md                          This file
├── CITATION.cff                       Citation metadata
├── LICENSE                            Dual license (MIT for code, CC-BY-4.0 for documents)
├── .gitignore
├── requirements.txt                   Python dependencies
├── preregistration/                   Pre-registration document with GPG signature and OTS proof
├── analysis/                          Python analysis scripts
│   ├── geometry.py                    Spherical geometry primitives with self-tests
│   ├── 00_verify_and_describe.py
│   ├── 01_geometry_check.py
│   ├── 02_observed_test_statistic.py
│   ├── 03_monte_carlo_primary.py
│   ├── 03b_conditional_null_exploratory.py
│   ├── 04_longitude_scan.py
│   ├── 05_per_pole_and_assignment.py
│   ├── 06_geographic_block_null.py
│   ├── 07_latitude_lookelsewhere.py        # v3 post-publication
│   ├── 08_finer_block_sensitivity.py       # v3 post-publication
│   ├── 09_lookelsewhere_under_finer_blocks.py  # v3 post-publication
│   ├── 10_spatial_cluster_null.py          # v3 post-publication
│   ├── 11_data_owner_rule_simulation.py   # v3.1 post-publication
│   ├── 12_hemisphere_preserving_null.py   # v3.1 post-publication
│   └── 13_asymmetry_circularity_check.py  # v3.1 post-publication
├── results/                           Analysis outputs, log, correspondence
│   ├── analysis_log.md                Live log of the project from inception
│   ├── analysis_log_frozen_2026-05-18.md   Snapshot from when results were first shared with the data owner
│   ├── correspondence/                Emails exchanged during the comment window and afterwards
│   └── *.json, *.csv, *.npy           Per-script output files
├── writeup/                           Final report source and rendered artifact
│   ├── results_v1.0.md                Source markdown (current v3 content)
│   ├── results_v1.0.pdf               Rendered v3.1 PDF (current artifact)
│   ├── results_v1.0.pdf.asc           v3.1 GPG signature
│   ├── results_v1.0.pdf.ots           v3.1 OpenTimestamps proof for PDF
│   ├── results_v1.0.pdf.asc.ots       v3.1 OpenTimestamps proof for signature
│   ├── pandoc_metadata.yaml           Rendering configuration
│   └── render_writeup.sh              Reproducible render script
└── data/                              Data not redistributed; see data/README.md for hash
```

Note: the filename `results_v1.0.*` follows the file's own internal versioning at the source-markdown level; the document inside has versioned over time (v1 / v2 / v3) at the Zenodo record level. The PDF currently committed in this repository is the v3 publication artifact. V2 of the report remains available as a prior version of the Zenodo record.

## Data

The database used in this analysis (`Database_Mario_Buildreps_V14.xlsx`) is **not redistributed** in this repository, per agreement with the data owner. Researchers wishing to reproduce this analysis should contact Mario Buildreps directly via [mariobuildreps.com](https://www.mariobuildreps.com/) to request access.

The SHA-256 hash of the exact file used in this analysis is recorded in `data/README.md` and in the pre-registration document, so that anyone obtaining the file from the source can verify byte-for-byte that they are analyzing the same data:

```
426dd95f4f1d62dbb2ea6b7be0bd2d1499834fb8b2c923ca59299384fd4ddb7c
```

## Cryptographic provenance

Every commit in this repository is GPG-signed. The pre-registration document and each version of the final report PDF are additionally OpenTimestamped on the Bitcoin blockchain.

| Artifact | SHA-256 | Bitcoin attestation |
|---|---|---|
| Pre-registration PDF (v1.1) | (see `preregistration/preregistration_v1.1.pdf.asc`) | OTS proof in `preregistration/` |
| Final report v2 PDF | `582b798e34a2bba58b7a93e4e46215c1d8812d81d21e90fb1f90d8557b0402a6` | Bitcoin block 951758, merkleroot `f5a820f2b9e363658dc6d7c43167851ae0e155d1ccb87e3ec5ecd33dc19358b1` |
| Final report v3 PDF (superseded) | `0661bba4709c90591056a43904589c4cfb5d880cc2ddc50c37b55151b78f3e40` | Bitcoin block 952402, merkleroot `7aab6dd40936b73eab49a662811b05d988045909a5f374281b11c72c1df89b8e` |
| Final report v3.1 PDF (current) | `82fea07d4ed8141ecdbe46fbd655e100ad4b4b4bc63e10c7dda72287c2f5ef6e` | Bitcoin blocks 952853 and 952854, merkleroots `e96b67321d5b90ccd07ad3e06f084406fb6b43066c0f514226952b3400a21cda` and `57ab8ece804ad847b212bf00b08d59ec4e0139a3eacc829441589d8ba045517e` |

Anyone can independently verify by running `gpg --verify` against the signature and `ots verify --no-bitcoin` against the OTS proof, then checking the reported Bitcoin block heights against any public blockchain explorer (e.g., [mempool.space](https://mempool.space)).

## Reproducing the analysis

With the database file obtained from the source:

```bash
git clone https://github.com/salahealer9/paleopole-orientation-verification.git
cd paleopole-orientation-verification

# Verify the database hash before proceeding
sha256sum data/Database_Mario_Buildreps_V14.xlsx
# Should match 426dd95f4f1d62dbb2ea6b7be0bd2d1499834fb8b2c923ca59299384fd4ddb7c

# Install dependencies
pip install -r requirements.txt

# Run pre-registered and v2-era analyses in order
python analysis/00_verify_and_describe.py
python analysis/01_geometry_check.py
python analysis/02_observed_test_statistic.py
python analysis/03_monte_carlo_primary.py
python analysis/03b_conditional_null_exploratory.py
python analysis/04_longitude_scan.py
python analysis/05_per_pole_and_assignment.py
python analysis/06_geographic_block_null.py

# Run v3 post-publication controls
python analysis/07_latitude_lookelsewhere.py
python analysis/08_finer_block_sensitivity.py
python analysis/09_lookelsewhere_under_finer_blocks.py
python analysis/10_spatial_cluster_null.py

# Run v3.1 post-publication analyses
python analysis/11_data_owner_rule_simulation.py
python analysis/12_hemisphere_preserving_null.py
python analysis/13_asymmetry_circularity_check.py

# Re-render the writeup PDF (requires pandoc and texlive)
./writeup/render_writeup.sh
```

All analyses use fixed pseudo-random seed `20260517` and are bit-for-bit reproducible.

## Citing this work

If you reference the analysis in your own work, please cite the current version of the report and the pre-registration:

- **Final report (current, v3.1)**: Gherbi, S.-E. (2026). *Independent Monte Carlo Verification of Paleopole Orientation Clustering in the Buildreps Database (v3.1).* Zenodo. [https://doi.org/10.5281/zenodo.20593690](https://doi.org/10.5281/zenodo.20593690)
- **Pre-registration**: Gherbi, S.-E. (2026). *Pre-registration: Independent Monte Carlo verification of paleopole orientation clustering in the Buildreps database.* Zenodo. [https://doi.org/10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204)

If citing a superseded version, v2 is 10.5281/zenodo.20474028 and v3 is 10.5281/zenodo.20546301; both have been superseded by v3.1.

A `CITATION.cff` file is included in the repository for tools that read structured citation metadata.

## Author

**Salah-Eddin Gherbi**
ORCID: [0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095)
Contact: salahealer@gmail.com

## Acknowledgments

Mario Buildreps generously provided the database for independent verification under the terms of non-redistribution, confirmed methodological details about his pipeline via direct correspondence during the analysis period, and accepted the 14-day pre-publication notice window committed by the pre-registration. His formal commentary on the findings is preserved verbatim as Appendix A of the final report.

The two methodological controls that distinguish v3 from v2 — the latitude look-elsewhere correction and the spatial-cluster independence control — were identified in a post-publication review carried out by Claude Opus 4.8 (Anthropic) acting as an external reviewer. The reviewer's own summary of the gaps identified and predictions made is preserved verbatim as Appendix C of the final report.

The discussion that took place during the comment window and the post-publication review — both in agreement and in disagreement — is part of the public record.

Version 3.1's further analyses (scripts 11–13) followed from the same reviewer's engagement with the data owner's June 2026 follow-up correspondence; the author ran and verified all analyses and is responsible for the conclusions.

## License

- Code (`analysis/`, scripts, configuration): MIT License
- Documents (`preregistration/`, `results/` write-ups, README): CC-BY-4.0

See `LICENSE` for full terms.