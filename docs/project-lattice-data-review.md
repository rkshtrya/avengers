# Project Lattice Data Review

Prepared for team review on 2026-07-05.

## Why We Put This Together

We want to look at Project Lattice from the data first, not just from the product story. The product only works if we can connect a valuation and explanation back to real property records, risk layers, schools, permits, amenities, and eventually comparable sales.

This repo is ready for source review, schema review, early feature engineering, knowledge-graph design, and first-pass EDA. It is not ready for production valuation yet because comparable sales are still unresolved.

## Start Here

A helpful review order:

1. `DATA_FILES.md`  
   Direct list of the actual raw source files uploaded to GitHub.

2. `docs/dataset-catalog.md`  
   Plain-English explanation of every dataset: county/geography, data type, source agency, source URL, local file path, and status.

3. `notebooks/01_data_inventory.ipynb`  
   Quick inventory of the downloaded data and where everything lives.

4. `notebooks/02_executed_eda.ipynb`  
   Visual EDA charts and tables, already executed.

5. `notebooks/03_availability_and_next_steps.ipynb`  
   What is available, what is pending, and what we can decide together.

6. `reports/domain_eda_findings.md`  
   Our main EDA summary. This is where the data is mapped back to the product.

7. `reports/eda_summary.md`  
   Dataset inventory, row counts, sizes, sample paths, and blocked sources.

8. `reports/download_manifest.csv`  
   Source URLs, file paths, status, notes, and sizes.

9. `reports/blocked_or_deferred_sources.csv`  
   Items that need an API key, manual download, licensing, or a product decision.

10. `data/processed/samples/`  
   Small samples so we can review quickly before loading full files.

## What We Downloaded

Raw files are under `data/raw/`; source metadata is under `data/metadata/`.

Geography note for the team: **San Ramon is a city inside Contra Costa County**. Contra Costa is the county-level data umbrella. San Ramon is the city-level focus. That is why several files are countywide Contra Costa datasets even though the story we are testing is San Ramon.

| Area | Files | What we found |
| --- | --- | --- |
| Contra Costa parcels | `data/raw/contra_costa/Parcels_Public_May2026.zip` | 387,835 parcel records; APN present on 100%; street-number/name/city fields complete on 94.2%. |
| San Ramon filtering | Contra Costa city limits plus parcel city/ZIP fields | San Ramon appears as `SNRMN` with 27,756 parcel rows. We can still validate with the city boundary geometry. |
| Zoning and planning | Contra Costa zoning, general-plan land use, urban limit line, LAFCO SOI | Good enough for contextual explanations; we can confirm incorporated-city zoning coverage. |
| Census boundaries | California 2025 tract, block group, and place TIGER shapefiles | Boundaries are included; ACS attributes still need a Census API key. |
| Schools | CDE public schools/districts file | 18,390 statewide rows; 479 Contra Costa rows; 44 rows with San Ramon in city or district. |
| Wildfire risk | CAL FIRE FHSZ LRA/SRA Contra Costa bbox extracts | Fire-hazard categories are included for the project area. |
| Flood risk | FEMA NFHL Contra Costa bbox attributes | 6,435 flood-zone attribute rows. Parcel-level flood joins need full FEMA geometry or a GIS pull. |
| Amenities | OSM San Ramon POI extract | 7,026 OSM elements for prototype proximity/context features. |
| Permits | San Francisco building permit selected-column CSV, stored as split CSV parts | 1,291,589 rows; 99.7% have point location. Strong demo dataset, but not San Ramon-specific. |

## Gaps We Can Resolve Together

Critical:

- Comparable sales are still missing. Without sale price, sale date, and property attributes, Lattice can explain context and risk but cannot honestly claim production-grade valuation.

Needs credential/manual step:

- 511/Bay Area GTFS needs a 511 API token.
- Census ACS 5-year variables need a Census API key.
- CDE district-only endpoint returned a bot-validation page through automated download; the combined schools/districts file is included and usable.
- Full California OSM PBF is large, so we are using a focused San Ramon Overpass extract for now.

## How We Can Collaborate

We can use this repo as the working source of truth for scripts, manifests, reports, samples, and source decisions. Since the raw files are already organized here, we can review directly in GitHub. For additional large files, we can decide together whether they belong in Git, a Release asset, Drive, S3, or another shared data store.

Suggested split:

| Owner | Review focus | Output |
| --- | --- | --- |
| Product/data lead | Confirm MVP target: San Ramon graph-first vs SF permit demo | Decision on first demo geography and story. |
| Data engineer | Validate raw files, schemas, and reload process | Reproducible data layout and ingestion notes. |
| Geospatial analyst | Parcel joins to city limits, zoning, land use, fire, flood, Census | `property_features` join plan and join-quality report. |
| ML/valuation owner | Comparable-sales acquisition options | Decision on licensed comps, MLS partnership, or manually seeded prototype comps. |
| Compliance/source owner | Confirm licenses and allowed usage | Approved source list and restrictions. |

## Next Technical Steps

1. Build `property_features` with one row per parcel.
2. Spatially filter Contra Costa parcels to San Ramon using city limits, then compare that result to parcel `S_CTY_ABBR = SNRMN`.
3. Join parcels to zoning, general-plan land use, Census geography, CAL FIRE FHSZ, FEMA flood zones, schools, and OSM POIs.
4. Pull ACS variables once a Census API key is available.
5. Resolve comparable-sales access before training a valuation model.
6. Use the SF permit dataset as the data-rich ingestion/explainability demo if we need a faster proof point.

## Large File Layout

The San Francisco permits extract is stored as split CSV parts under:

`data/raw/san_francisco/building_permits_selected_parts/`

To rebuild the original single CSV locally:

```bash
python3 scripts/reconstruct_large_files.py
```

## Reproducibility

To refresh downloads:

```bash
python3 scripts/download_project_lattice_data.py
```

To regenerate EDA:

```bash
python3 scripts/eda_project_lattice_data.py
python3 scripts/profile_project_lattice_data.py
```

Reports are under `reports/`; small review samples are under `data/processed/samples/`.
