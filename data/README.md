# Data

## Important: data is not redistributed in this repository

The database analyzed in this project — `Database_Mario_Buildreps_V14.xlsx` — is **not** included in this repository, and the directory it would occupy is enforced as empty by `.gitignore` at the repository root.

This is a deliberate choice, made in agreement with the data owner:

> Mario Buildreps provided the database for the purpose of independent statistical verification, with the explicit condition that the raw data not be redistributed. Only summary statistics, code, and conclusions are made public via this repository and the associated Zenodo deposit.

## How to obtain the data

Researchers wishing to reproduce this analysis should contact Mario Buildreps directly through his website: [mariobuildreps.com](https://www.mariobuildreps.com/).

## File identity

The exact file used in this analysis can be verified by SHA-256 hash:

```
File:   Database_Mario_Buildreps_V14.xlsx
SHA-256: <to be inserted once hash is computed and recorded in the pre-registration>
```

The same hash appears in the pre-registration document deposited on Zenodo. Anyone obtaining the database from Mario Buildreps can verify byte-for-byte that they have the same file by running:

```bash
sha256sum Database_Mario_Buildreps_V14.xlsx
```

(on Linux/macOS) or:

```powershell
Get-FileHash -Algorithm SHA256 Database_Mario_Buildreps_V14.xlsx
```

(on Windows PowerShell).

If the hash does not match, the analysis in this repository does not strictly apply to the file in hand — different versions of the database may yield different results.

## Local placement

If you obtain a copy of the database and wish to run the analysis, place it in this directory as `Database_Mario_Buildreps_V14.xlsx`. The `.gitignore` ensures it will not be committed.

## License

The database is the intellectual property of Mario Buildreps and is **not** covered by the licenses of this repository (MIT for code, CC-BY-4.0 for documents). All rights to the database itself remain with the data owner.
