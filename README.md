# Paleopole Orientation Verification

[![Zenodo record (latest version)](https://zenodo.org/badge/DOI/10.5281/zenodo.20258203.svg)](https://doi.org/10.5281/zenodo.20258203)

An independent, pre-registered statistical test of the claim that the orientations of ancient pyramids, temples, and megalithic structures cluster around proposed former geographic pole positions located along the ~47°W meridian.

## Status

**Final report published 1 June 2026.** The pre-registered protocol committed on 17 May 2026 has been executed in full. The 14-day pre-publication notice window has closed with the data owner's formal commentary incorporated. The publication artifact is GPG-signed and OpenTimestamped on the Bitcoin blockchain.

The Zenodo record has two versions:

| Version | Date | Description | Version DOI |
|---|---|---|---|
| 1 | 17 May 2026 | Pre-registration of the statistical protocol | [10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204) |
| 2 | 1 June 2026 | Final report incorporating analysis results and the data owner's commentary | [10.5281/zenodo.20474028](https://doi.org/10.5281/zenodo.20474028) |

The concept DOI [10.5281/zenodo.20258203](https://doi.org/10.5281/zenodo.20258203) always resolves to the latest version. The corresponding GitHub release tags are `prereg-v1.1` and `report-v1.0`.

## Background

Mario Buildreps has compiled a database of ~1,159 ancient structures worldwide and proposes that their orientations cluster around five paleopole positions located along the ~47°W meridian. The full framework, including the proposed pole coordinates, the binomial-test methodology, and supporting visualizations, is documented at [mariobuildreps.com](https://www.mariobuildreps.com/).

This repository contains an independent verification of the central empirical claim using Monte Carlo simulation against geographically-realistic null models. The analysis was **pre-registered before the database was opened**, to ensure that the methodology could not be adjusted after seeing the data.

## What this project tests

A single, narrow empirical claim:

> The orientations of ancient structures in the database cluster around the five proposed pole positions more than expected under random orientations applied to the same geographic distribution of sites.

This project does **not** test, validate, or refute any broader interpretive claims (Earth expansion, crustal deformation, the dating of human civilization, climate science, etc.). Those are separate questions outside the scope of an orientation-clustering statistical test, as discussed in §4.3 of the final report.

## Summary of findings

After running the pre-registered protocol with four progressively more stringent null models:

- **Robust within-hemisphere clustering exists at Pole II (76°N) and Pole III (72.2°N)**, surviving all four null models including the block-conditional null that preserves site geography, regional bearing patterns, and the northern-hemisphere intersection property simultaneously. About 234 structures (24% of the in-range sample) concentrate near these two latitudes, ~50 more than expected under the most stringent null.
- **Poles I (90°N), IV (64.1°N), and V (52.3°N) do not show robust excess under principled null models.** Pole V's apparent signal under hemisphere-conditional permutation is eliminated under within-region permutation.
- **The pre-registered aggregate test statistic showed a 26-sigma effect**, but diagnostic analysis revealed this to be an artifact of hemisphere-mismatch between the in-range subset (99% northern by selection) and the unconditional null (54% northern by chance). Under properly-conditioned nulls, the aggregate effect is null.
- **The site-to-pole assignment match rate is 46% vs 9% expected** under the most stringent null — robust across all four null models.
- **The data owner's published "100% probability" claims at Poles I-III and "99.999%" at Poles IV-V are not supported** in their published form; under principled null models, three of the five proposed poles show no excess concentration.
- **The broader interpretive claim** that the observed clustering represents former geographic pole positions is not tested by this analysis and requires independent geological evidence to evaluate.

The full report is at [10.5281/zenodo.20474028](https://doi.org/10.5281/zenodo.20474028).

## Methodology

The pre-registration document at `preregistration/preregistration_v1.1.md` is the authoritative specification. In summary:

- **Test statistic**: T = mean of per-structure minimum angular distance to the nearest of the five proposed poles, on the structure's great-circle intersection with the 47°W meridian. Binning-free.
- **Pre-registered null model**: random permutation of folded bearings across in-range sites, preserving site geography and the empirical bearing distribution.
- **Exploratory conditional null** (added after diagnostic): Metropolis swap chain preserving the in-range hemisphere property by construction.
- **Pre-registered block-conditional null** (§11(d)): within-block permutation across seven geographic regions, with the in-range property preserved.
- **Look-elsewhere control** (§10): longitude scan at 5° resolution with minimum-T null distribution.
- **Per-pole confirmatory test** (§11(a)): structure counts within ±1.5° of each proposed pole, Šidák-corrected.
- **Site-to-pole assignment test** (§11(b)): match rate between independent geometry and data-owner pipeline.

Monte Carlo iterations: M = 10,000. Random seed: 20260517. Reproducible from the database file.

## Repository structure

```
paleopole-orientation-verification/
├── README.md                          This file
├── LICENSE                            Dual license (MIT for code, CC-BY-4.0 for documents)
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
│   └── 06_geographic_block_null.py
├── results/                           Analysis outputs, log, correspondence
│   ├── analysis_log.md                Live log of the project from inception
│   ├── analysis_log_frozen_2026-05-18.md   Snapshot from when results were first shared with the data owner
│   ├── correspondence/                Emails exchanged during the comment window
│   └── *.json, *.csv, *.npy           Per-script output files
├── writeup/                           Final report source and rendered artifact
│   ├── results_v1.0.md                Source markdown
│   ├── results_v1.0.pdf               Rendered PDF (final artifact)
│   ├── results_v1.0.pdf.asc           GPG signature
│   ├── results_v1.0.pdf.ots           OpenTimestamps proof for PDF
│   ├── results_v1.0.pdf.asc.ots       OpenTimestamps proof for signature
│   ├── pandoc_metadata.yaml           Rendering configuration
│   └── render_writeup.sh              Reproducible render script
└── data/                              Data not redistributed; see data/README.md for hash
```

## Data

The database used in this analysis (`Database_Mario_Buildreps_V14.xlsx`) is **not redistributed** in this repository, per agreement with the data owner. Researchers wishing to reproduce this analysis should contact Mario Buildreps directly via [mariobuildreps.com](https://www.mariobuildreps.com/) to request access.

The SHA-256 hash of the exact file used in this analysis is recorded in `data/README.md` and in the pre-registration document, so that anyone obtaining the file from the source can verify byte-for-byte that they are analyzing the same data:

```
426dd95f4f1d62dbb2ea6b7be0bd2d1499834fb8b2c923ca59299384fd4ddb7c
```

## Cryptographic provenance

Every commit in this repository is GPG-signed. The pre-registration document and the final report PDF are additionally OpenTimestamped on the Bitcoin blockchain.

| Artifact | SHA-256 | Bitcoin attestation |
|---|---|---|
| Pre-registration PDF | (see `preregistration/preregistration_v1.1.pdf.asc`) | OTS proof in `preregistration/` |
| Final report PDF | `582b798e34a2bba58b7a93e4e46215c1d8812d81d21e90fb1f90d8557b0402a6` | Bitcoin block 951758, merkleroot `f5a820f2b9e363658dc6d7c43167851ae0e155d1ccb87e3ec5ecd33dc19358b1` |
| Final report signature | (see `writeup/results_v1.0.pdf.asc`) | Bitcoin block 951797, merkleroot `eee902eebc3b300a6ac1e41c671d8f9d54c56409f90150bc54e534a0e0ee74a0` |

Anyone can independently verify by running `gpg --verify` against the signature and `ots verify --no-bitcoin` against the OTS proof, then checking the reported Bitcoin block heights against any public blockchain explorer.

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

# Run analyses in order
python analysis/00_verify_and_describe.py
python analysis/01_geometry_check.py
python analysis/02_observed_test_statistic.py
python analysis/03_monte_carlo_primary.py
python analysis/03b_conditional_null_exploratory.py
python analysis/04_longitude_scan.py
python analysis/05_per_pole_and_assignment.py
python analysis/06_geographic_block_null.py

# Re-render the writeup PDF (requires pandoc and texlive)
./writeup/render_writeup.sh
```

All analyses use fixed pseudo-random seed `20260517` and are bit-for-bit reproducible.

## Citing this work

If you reference the analysis in your own work, please cite both:

- **Pre-registration**: Gherbi, S.-E. (2026). *Pre-registration: Independent Monte Carlo verification of paleopole orientation clustering in the Buildreps database.* Zenodo. [https://doi.org/10.5281/zenodo.20258204](https://doi.org/10.5281/zenodo.20258204)
- **Final report**: Gherbi, S.-E. (2026). *Independent Monte Carlo verification of paleopole orientation clustering in the Buildreps database — Final report.* Zenodo. [https://doi.org/10.5281/zenodo.20474028](https://doi.org/10.5281/zenodo.20474028)

A `CITATION.cff` file is included in the repository for tools that read structured citation metadata.

## Author

**Salah-Eddin Gherbi**
ORCID: [0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095)
Contact: salahealer@gmail.com

## Acknowledgments

Mario Buildreps generously provided the database for independent verification under the terms of non-redistribution, confirmed methodological details about his pipeline via direct correspondence during the analysis period, and accepted the 14-day pre-publication notice window committed by the pre-registration. His formal commentary on the findings is preserved verbatim as Appendix A of the final report. The discussion that took place during the comment window — both in agreement and in disagreement — is part of the public record.

## License

- Code (`analysis/`, scripts, configuration): MIT License
- Documents (`preregistration/`, `results/` write-ups, README): CC-BY-4.0

See `LICENSE` for full terms.
