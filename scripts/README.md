# Scripts Guide

These scripts download, inspect, profile, and rebuild the Project Lattice data package.

Run scripts from the repo root.

## Scripts

| Script | What it does |
| --- | --- |
| `download_project_lattice_data.py` | Downloads the source files and writes download metadata. |
| `eda_project_lattice_data.py` | Runs the main EDA and creates summaries, samples, and tables. |
| `profile_project_lattice_data.py` | Creates profile/count tables for key datasets. |
| `build_review_assets.py` | Builds visual review assets and notebook-supporting tables. |
| `reconstruct_large_files.py` | Rebuilds the single SF permits CSV from the committed split parts. |

## Reproduce The Main Outputs

```bash
python3 scripts/eda_project_lattice_data.py
python3 scripts/profile_project_lattice_data.py
python3 scripts/build_review_assets.py
```

## Rebuild The Large SF Permit CSV

```bash
python3 scripts/reconstruct_large_files.py
```

This creates:

`data/raw/san_francisco/building_permits_selected.csv`

That rebuilt file is ignored by Git because the split CSV parts are already committed.
