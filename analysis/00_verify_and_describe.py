"""
00_verify_and_describe.py
=========================

First script in the pre-registered analysis pipeline for the paleopole
orientation verification project.

Purpose
-------
Before any analytical step is taken:

1. Verify that the database file on disk matches the SHA-256 hash recorded
   in the pre-registration (Zenodo DOI 10.5281/zenodo.20258204). If the
   hash does not match, the script exits with an error — the analysis
   cannot proceed because the file is not the file the pre-registration
   was written against.

2. Inspect the file's schema: sheet names, column names, dtypes, row counts.
   These are structural properties, not analytical content.

3. Report missingness (NaN counts per column) and basic structural integrity
   checks (e.g., are LAT/LON within valid ranges, is BEARING within the
   declared [-45, +45] folded range).

4. Print the result of all checks to stdout AND write a machine-readable
   JSON summary to results/00_schema_summary.json.

This script does NOT:
- compute any test statistic
- inspect the distribution of orientations
- aggregate or summarise the analytical content of the data
- generate plots

Usage
-----
From the repository root:

    python analysis/00_verify_and_describe.py

The script expects:
- The database file at: data/Database_Mario_Buildreps_V14.xlsx
- The reference hash at: data/Database_Mario_Buildreps_V14.xlsx.sha256

The reference hash file is the GPG-signed and OpenTimestamped artifact
committed to the repository in the initial commit (ab12dc5).

Pre-registration: https://doi.org/10.5281/zenodo.20258204
Repository:       https://github.com/salahealer9/paleopole-orientation-verification
Author:           Salah-Eddin Gherbi
License:          MIT
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Paths (resolved relative to the repository root, regardless of CWD)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx"
HASH_FILE = REPO_ROOT / "data" / "Database_Mario_Buildreps_V14.xlsx.sha256"
RESULTS_DIR = REPO_ROOT / "results"
SUMMARY_FILE = RESULTS_DIR / "00_schema_summary.json"


# ---------------------------------------------------------------------------
# Hash verification
# ---------------------------------------------------------------------------


def compute_sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of the file at *path*.

    Reads in 64 KiB chunks to avoid loading large files into memory.
    """
    sha256 = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def read_reference_hash(hash_file: Path) -> str:
    """Read the reference hash from the .sha256 file.

    The file is in the standard ``sha256sum`` format:
        <64-hex-chars>  <filename>
    Only the hash portion is returned.
    """
    text = hash_file.read_text().strip()
    parts = text.split()
    if not parts or len(parts[0]) != 64:
        raise ValueError(f"Hash file {hash_file} does not contain a valid SHA-256 hash.")
    return parts[0].lower()


def verify_hash() -> str:
    """Verify the database file matches the recorded hash.

    Returns the (verified) hash on success. Exits with status 1 on failure.
    """
    if not DATA_FILE.exists():
        print(f"ERROR: database file not found at {DATA_FILE}", file=sys.stderr)
        print("Place the file received from the data owner in data/ and retry.", file=sys.stderr)
        sys.exit(1)

    if not HASH_FILE.exists():
        print(f"ERROR: reference hash file not found at {HASH_FILE}", file=sys.stderr)
        sys.exit(1)

    expected = read_reference_hash(HASH_FILE)
    actual = compute_sha256(DATA_FILE)

    print("SHA-256 verification")
    print("-" * 60)
    print(f"  expected: {expected}")
    print(f"  actual:   {actual}")

    if expected != actual:
        print("\nERROR: hash mismatch. The file on disk is NOT the file the")
        print("pre-registration was written against. Analysis cannot proceed.", file=sys.stderr)
        sys.exit(1)

    print("  status:   MATCH")
    print()
    return actual


# ---------------------------------------------------------------------------
# Schema inspection
# ---------------------------------------------------------------------------

# Columns the pre-registration assumes to be present, with semantic notes.
# This is what we EXPECT based on the pre-registration; the script reports
# whether the file matches.

EXPECTED_COLUMNS = [
    "SITE NAME",
    "COUNTRY",
    "LAT",
    "LON",
    "BEARING",
    "Intersection Latitude at Lon 47.1W Line",
    "Rounded Latitudes",
    "Remarks",
    "Date added",
]

# Data-owner-stated quantities, for cross-check
EXPECTED_TOTAL_ROWS = 1159
EXPECTED_IN_RANGE_ROWS = 993
EXPECTED_OUT_OF_RANGE_ROWS = 166


def inspect_workbook() -> dict:
    """List all sheets in the workbook with their row counts and columns."""
    print("Workbook structure")
    print("-" * 60)

    xl = pd.ExcelFile(DATA_FILE)
    sheet_info = {}
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)
        sheet_info[sheet_name] = {
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "columns": df.columns.tolist(),
        }
        print(f"  sheet: {sheet_name!r}")
        print(f"    rows: {len(df)}")
        print(f"    cols: {len(df.columns)}")

    print()
    return sheet_info


def inspect_main_sheet(sheet_name: str | None = None) -> dict:
    """Inspect the primary data sheet (the one the analysis will use).

    If *sheet_name* is None, uses the first sheet.
    """
    df = pd.read_excel(DATA_FILE, sheet_name=sheet_name or 0)
    sheet_used = sheet_name if sheet_name is not None else pd.ExcelFile(DATA_FILE).sheet_names[0]

    print(f"Primary data sheet: {sheet_used!r}")
    print("-" * 60)
    print(f"  rows: {len(df)}")
    print(f"  cols: {len(df.columns)}")
    print()

    # Column presence check
    print("  Expected columns present:")
    missing = []
    for col in EXPECTED_COLUMNS:
        present = col in df.columns
        marker = "OK " if present else "MISSING"
        print(f"    [{marker}] {col}")
        if not present:
            missing.append(col)
    print()

    # Unexpected columns
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if extra:
        print("  Unexpected columns (present in file, not in pre-registration):")
        for col in extra:
            print(f"    [WARN] {col}")
        print()

    # Dtypes
    print("  Column dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"    {col}: {dtype}")
    print()

    # Missingness
    print("  Missing values (NaN count) per column:")
    nan_counts = df.isna().sum()
    for col, count in nan_counts.items():
        print(f"    {col}: {count}")
    print()

    # Range checks for LAT, LON, BEARING — these are structural integrity
    # checks, not analytical inspection.
    range_checks = {}
    for col, lo, hi in [
        ("LAT", -90.0, 90.0),
        ("LON", -180.0, 180.0),
        ("BEARING", -45.0, 45.0),
    ]:
        if col in df.columns:
            col_data = pd.to_numeric(df[col], errors="coerce")
            below = int((col_data < lo).sum())
            above = int((col_data > hi).sum())
            n_nan = int(col_data.isna().sum())
            range_checks[col] = {
                "expected_range": [lo, hi],
                "n_below_range": below,
                "n_above_range": above,
                "n_nan": n_nan,
            }
            status = "OK" if below == 0 and above == 0 else "OUT OF RANGE"
            print(f"  Range check {col} in [{lo}, {hi}]: [{status}]"
                  f" below={below}, above={above}, nan={n_nan}")
    print()

    # Row count check against the data owner's stated quantities.
    print("  Row count check:")
    print(f"    observed:           {len(df)}")
    print(f"    expected total:     {EXPECTED_TOTAL_ROWS}")
    print(f"    expected in-range:  {EXPECTED_IN_RANGE_ROWS}")
    print(f"    expected out-range: {EXPECTED_OUT_OF_RANGE_ROWS}")
    if len(df) == EXPECTED_TOTAL_ROWS:
        print(f"    [OK] total row count matches the data owner's stated quantity")
    else:
        print(f"    [WARN] total row count does not match expected {EXPECTED_TOTAL_ROWS}")
    print()

    return {
        "sheet_name": sheet_used,
        "n_rows": int(len(df)),
        "n_cols": int(len(df.columns)),
        "columns_present": df.columns.tolist(),
        "missing_columns": missing,
        "unexpected_columns": extra,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "nan_counts": {col: int(c) for col, c in nan_counts.items()},
        "range_checks": range_checks,
        "row_count_match": bool(len(df) == EXPECTED_TOTAL_ROWS),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("Pre-registered analysis: schema verification and description")
    print("Script: 00_verify_and_describe.py")
    print(f"Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print("Pre-registration DOI: 10.5281/zenodo.20258204")
    print("=" * 60)
    print()

    verified_hash = verify_hash()
    workbook_info = inspect_workbook()
    main_sheet_info = inspect_main_sheet()

    summary = {
        "script": "00_verify_and_describe.py",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "preregistration_doi": "10.5281/zenodo.20258204",
        "file_hash_sha256": verified_hash,
        "workbook_sheets": workbook_info,
        "primary_sheet": main_sheet_info,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(f"Schema summary written to {SUMMARY_FILE.relative_to(REPO_ROOT)}")
    print()
    print("Verification complete. Next script: 01_geometry_check.py")
    print()


if __name__ == "__main__":
    main()
