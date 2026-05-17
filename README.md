# Paleopole Orientation Verification

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20258203.svg)](https://doi.org/10.5281/zenodo.20258203)

An independent, pre-registered statistical test of the claim that the orientations of ancient pyramids, temples, and megalithic structures cluster around proposed former geographic pole positions.

## Background

Mario Buildreps has compiled a database of ~1,159 ancient structures worldwide and proposes that their orientations cluster around five paleopole positions located along the ~47°W meridian. The full framework, including the proposed pole coordinates, the binomial-test methodology, and supporting visualizations, is documented at [mariobuildreps.com](https://www.mariobuildreps.com/).

This repository contains an independent verification of the central empirical claim using a Monte Carlo simulation against a geographically-realistic null model. The analysis was **pre-registered before the database was opened**, to ensure that the methodology could not be adjusted after seeing the data.

## What this project tests

A single, narrow empirical claim:

> The orientations of ancient structures in Mario Buildreps' database cluster around the five proposed pole positions more than expected under random orientations applied to the same geographic distribution of sites.

This project does **not** test, validate, or refute any broader interpretive claims (Earth expansion, crustal deformation, the dating of human civilization, climate science, etc.). Those are separate questions outside the scope of a statistical test.

## Methodology

The pre-registration document in `preregistration/` is the authoritative specification of the analysis. In summary:

- **Null hypothesis**: orientations are randomly distributed (folded northernface azimuth in [−45°, +45°], drawn from the empirical orientation distribution), independent of site geography.
- **Test statistic**: pre-registered in `preregistration/`.
- **Null model**: Monte Carlo simulation (≥10,000 iterations) shuffling folded azimuths across sites while preserving site coordinates.
- **Multiple-comparisons handling**: pre-registered.
- **Sensitivity analyses**: alternative aggregation thresholds, geographic-block null model, with/without Pole VI, look-elsewhere control across longitudes.

## Repository structure

```
paleopole-orientation-verification/
├── README.md                    This file
├── LICENSE                      Dual license (see file)
├── .gitignore
├── preregistration/             Pre-registration document and Zenodo DOI
├── analysis/                    Python analysis code
├── results/                     Figures, summary statistics, write-up
└── data/                        Data not redistributed; see data/README.md
```

## Data

The database used in this analysis (`Database_Mario_Buildreps_V14.xlsx`) is **not redistributed** in this repository, per agreement with the data owner. Researchers wishing to reproduce this analysis should contact Mario Buildreps directly via [mariobuildreps.com](https://www.mariobuildreps.com/) to request access.

The SHA-256 hash of the exact file used in this analysis is recorded in `data/README.md` and in the pre-registration document, so that anyone obtaining the file from the source can verify byte-for-byte that they are analyzing the same data.

## Pre-registration

The pre-registration is deposited on Zenodo with a permanent DOI and OpenTimestamps proof. It is also committed to this repository under `preregistration/` and signed with a GPG key for additional provenance.

**Zenodo DOI**: *[10.5281/zenodo.20258203](https://doi.org/10.5281/zenodo.20258203)*

The pre-registration was written and timestamped **before** the database file was opened. The SHA-256 hash of the database file is recorded in the pre-registration itself, so the analysis can only legitimately be run against that exact file.

## Author

Salah-Eddin Gherbi

## Acknowledgments

Mario Buildreps generously provided the database for independent verification under the terms of non-redistribution. Whatever conclusions this analysis reaches, his willingness to subject his work to external scrutiny is appreciated.

## License

- Code (`analysis/`, scripts, configuration): MIT License
- Documents (`preregistration/`, `results/` write-ups, README): CC-BY-4.0

See `LICENSE` for full terms.
