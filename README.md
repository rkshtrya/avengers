# Project Lattice Data Review

I put this repo together so we can review Project Lattice from the data up.

The main question for us: **can this data support an explainable real-estate valuation product?**

My current answer: **yes for the knowledge graph and explanation demo; not yet for production valuation until we secure comparable sales.**

## Start Here

![Review path](reports/figures/review_path.svg)

Open these in order:

| Step | Open | What it shows |
| --- | --- | --- |
| 1 | `docs/dataset-catalog.md` | What each dataset is, what county/geography it covers, where it came from, and why it matters. |
| 2 | `notebooks/01_data_inventory.ipynb` | What data files are already downloaded and where they live. |
| 3 | `notebooks/02_executed_eda.ipynb` | The main EDA charts and tables, already executed. |
| 4 | `notebooks/03_availability_and_next_steps.ipynb` | What is available, what is pending, and what we need to decide. |
| 5 | `docs/project-lattice-data-handoff.md` | My written walkthrough for the team. |

## Data Readiness

![Data readiness](reports/figures/data_readiness.svg)

## Biggest Datasets

![Major dataset counts](reports/figures/major_record_counts.svg)

## What Is In The Repo

```text
data/raw/                  Actual downloaded source data, organized by source
data/processed/samples/    Small samples for quick review
data/metadata/             Source metadata
reports/                   EDA summaries, charts, and profile tables
notebooks/                 Executed notebooks for review
docs/                      Team walkthrough and source plan
scripts/                   Reproducible download + EDA scripts
project_brief/             Project deck export
```

## Data Included

The detailed dataset guide is here:

`docs/dataset-catalog.md`

It explains each dataset in plain English:

- what county or geography it covers
- what kind of data it is
- where it was sourced from
- where the file lives in the repo
- what the team should look for
- whether it is available or still pending

Quick view:

| Area | County / geography | Status | Location |
| --- | --- | --- | --- |
| Contra Costa parcels | Contra Costa County | Available | `data/raw/contra_costa/Parcels_Public_May2026.zip` |
| City limits / zoning / land use | Contra Costa County | Available | `data/raw/contra_costa/` |
| Census boundaries | California statewide | Available | `data/raw/census/` |
| Schools | California statewide, with Contra Costa rows | Available | `data/raw/schools/` |
| Wildfire and flood risk | Contra Costa project area | Available | `data/raw/risk/` |
| OSM San Ramon POIs | San Ramon / Contra Costa bbox | Available | `data/raw/osm/` |
| SF permits | City and County of San Francisco | Available as split CSV parts | `data/raw/san_francisco/building_permits_selected_parts/` |
| Comparable sales | Target metro TBD | Pending | Need legal source or seed set |
| 511 transit | Bay Area | Pending | API token needed |
| ACS variables | Contra Costa/SF tracts and block groups | Pending | Census API key needed |

## Main EDA Files

- `reports/visual_review.md`
- `docs/dataset-catalog.md`
- `reports/domain_eda_findings.md`
- `reports/eda_summary.md`
- `reports/download_manifest.csv`
- `reports/blocked_or_deferred_sources.csv`

## Rebuild The Large SF Permit CSV

The SF permit extract is 519 MB as one CSV, so I split it into GitHub-safe parts.

To rebuild it locally:

```bash
python3 scripts/reconstruct_large_files.py
```

## Reproduce The EDA

```bash
python3 -m pip install -r requirements.txt
python3 scripts/eda_project_lattice_data.py
python3 scripts/profile_project_lattice_data.py
python3 scripts/build_review_assets.py
```
