# Project Lattice Data Handoff

Prepared for team review on 2026-07-05.

## What This Package Is

This is a review-ready data package for Project Lattice: a property intelligence and explainable valuation product centered on parcel identity, local context, risk, schools, permits, and comparable sales.

The package is sufficient for source review, schema review, early feature engineering, knowledge-graph design, and a first-pass EDA discussion. It is not yet sufficient for production valuation because a permitted comparable-sales dataset is still missing.

## Start Here

Review these files in this order:

1. `reports/domain_eda_findings.md`  
   Product-oriented EDA: sufficiency matrix, core counts, risk mix, permit signal, schools, OSM POIs, and recommended decisions.

2. `reports/eda_summary.md`  
   Dataset inventory summary with row counts, file sizes, and blocked/deferred source list.

3. `reports/download_manifest.csv`  
   Machine-readable list of downloaded files, source URLs, status, notes, and sizes.

4. `reports/blocked_or_deferred_sources.csv`  
   Sources that need an API key, manual download, licensing, or a product decision.

5. `data/processed/samples/`  
   Small sample CSVs for quick review without opening the full raw datasets.

## Downloaded Data

Raw files live under `data/raw/`; metadata lives under `data/metadata/`.

Included:

| Area | Files | Current EDA signal |
| --- | --- | --- |
| Contra Costa parcels | `data/raw/contra_costa/Parcels_Public_May2026.zip` | 387,835 parcel records; APN present on 100%; street-number/name/city address fields complete on 94.2%. |
| San Ramon filtering | Contra Costa city limits plus parcel city/ZIP fields | San Ramon city abbreviation appears as `SNRMN` with 27,756 parcel rows. Spatial boundary validation still recommended. |
| Zoning and planning | Contra Costa zoning, general-plan land use, urban limit line, LAFCO SOI | Sufficient for contextual explanations; verify incorporated-city zoning coverage. |
| Census boundaries | California 2025 tract, block group, and place TIGER shapefiles | Boundaries included; ACS attributes need Census API key. |
| Schools | CDE public schools/districts file | 18,390 rows statewide; 479 Contra Costa rows; 44 rows with San Ramon in city or district. |
| Wildfire risk | CAL FIRE FHSZ LRA/SRA Contra Costa bbox extracts | LRA and SRA feature extracts included with fire-hazard categories. |
| Flood risk | FEMA NFHL Contra Costa bbox attributes | 6,435 flood-zone attribute rows. Full parcel-level geometry join needs a full FEMA geometry pull. |
| Amenities | OSM San Ramon POI extract | 7,026 OSM elements; useful for prototype proximity/context features. |
| Permits | San Francisco building permit selected-column CSV, stored as split CSV parts in this repository | 1,291,589 rows, 99.7% with point location. Strong demo dataset, but not San Ramon-specific. |

## Source Gaps

Critical:

- Comparable sales are still missing. Without sale price, sale date, and property attributes, Lattice can explain context and risk but cannot honestly claim production-grade valuation.

Needs credential/manual step:

- 511/Bay Area GTFS needs a 511 API token.
- Census ACS 5-year variables need a Census API key.
- CDE district-only endpoint returned a bot-validation page in automated download; the combined schools/districts file is included and usable.
- Full California OSM PBF was deferred because it is large; the package uses a focused San Ramon Overpass extract instead.

## Recommended Collaboration Workflow

Use the current folder as the source-controlled handoff for scripts, manifests, reports, and samples. Put the raw data package in shared storage such as Drive, Dropbox, S3, or an internal data bucket rather than sending it through chat or email.

Suggested team review split:

| Owner | Review focus | Output |
| --- | --- | --- |
| Product/data lead | Confirm MVP target: San Ramon graph-first vs SF permit demo | Decision on first demo geography and narrative. |
| Data engineer | Validate raw files, schemas, and reload process | Reproducible data lake layout and ingestion notes. |
| Geospatial analyst | Parcel joins to city limits, zoning, land use, fire, flood, Census | `property_features` join plan and join-quality report. |
| ML/valuation owner | Comparable-sales acquisition options | Decision on licensed comps, MLS partnership, or manually seeded prototype comps. |
| Compliance/source owner | Confirm licenses and allowed usage | Approved source list and restrictions. |

## Recommended Next Technical Steps

1. Build `property_features` with one row per parcel.
2. Spatially filter Contra Costa parcels to San Ramon using city limits, then compare to parcel `S_CTY_ABBR = SNRMN`.
3. Join parcels to zoning, general-plan land use, Census geography, CAL FIRE FHSZ, FEMA flood zones, schools, and OSM POIs.
4. Pull ACS variables once a Census API key is available.
5. Resolve comparable-sales source before training a valuation model.
6. Use the SF permit dataset as a parallel ingestion/explainability demo if the team needs a rich public dataset immediately.

## Large File Layout

The San Francisco permits extract is stored as split CSV parts under `data/raw/san_francisco/building_permits_selected_parts/` so every committed file stays below GitHub's normal single-file limit.

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

The generated reports are under `reports/`; reusable small extracts are under `data/processed/samples/`.
