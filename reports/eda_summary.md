# Project Lattice EDA Summary

I used the files in `data/raw` and `data/metadata` to check what we can actually build on.

## My Read

- This repo is strong enough for data-source review and first-pass EDA.
- Public/contextual layers are available: parcels, zoning/planning, schools, permits, Census boundaries, flood risk, wildfire risk, and OSM POIs.
- The material gap remains comparable sales: no verified free bulk source is included.
- Full spatial joins require GeoPandas, DuckDB Spatial, QGIS, or PostGIS; this EDA inspects schemas, record counts, fields, and samples.

## Downloaded Dataset Inventory

| Dataset | Kind | Rows/features | Columns | Size MB | Sample |
| --- | --- | ---: | ---: | ---: | --- |
| `data/metadata/calfire_fhsz_catalog_metadata.json` | json_metadata |  |  | 0.01 | `` |
| `data/metadata/calfire_fhsz_webmap.json` | json_metadata |  |  | 0.02 | `` |
| `data/metadata/download_manifest.json` | json_metadata |  |  | 0.01 | `` |
| `data/metadata/fema_nfhl_mapserver_metadata.json` | json_metadata |  |  | 0.01 | `` |
| `data/raw/census/tl_2025_06_bg.zip` | zip_shapefile_or_archive | 25607 | 13 | 50.47 | `data/processed/samples` |
| `data/raw/census/tl_2025_06_place.zip` | zip_shapefile_or_archive | 1619 | 16 | 9.43 | `data/processed/samples` |
| `data/raw/census/tl_2025_06_tract.zip` | zip_shapefile_or_archive | 9129 | 13 | 31.05 | `data/processed/samples` |
| `data/raw/contra_costa/BND_DCD_City_Limits.zip` | zip_shapefile_or_archive | 20 | 5 | 0.48 | `data/processed/samples` |
| `data/raw/contra_costa/BND_LAFCO_City_SOI.zip` | zip_shapefile_or_archive | 19 | 3 | 0.23 | `data/processed/samples` |
| `data/raw/contra_costa/PLA_DCD_GPLanduseElement.zip` | zip_shapefile_or_archive | 1732 | 6 | 2.59 | `data/processed/samples` |
| `data/raw/contra_costa/PLA_DCD_ULL.zip` | zip_shapefile_or_archive | 18 | 3 | 0.48 | `data/processed/samples` |
| `data/raw/contra_costa/PLA_DCD_Zoning.zip` | zip_shapefile_or_archive | 1259 | 9 | 1.32 | `data/processed/samples` |
| `data/raw/contra_costa/Parcels_Public_May2026.zip` | zip_shapefile_or_archive | 387835 | 10 | 40.08 | `data/processed/samples` |
| `data/raw/osm/osm_san_ramon_pois.json` | osm_overpass_json | 7026 | 339 | 1.59 | `data/processed/samples/osm_san_ramon_pois_sample.csv` |
| `data/raw/risk/calfire_fhsz_lra_contra_costa_bbox.geojson` | geojson | 328 | 6 | 10.90 | `data/processed/samples/calfire_fhsz_lra_contra_costa_bbox_properties_sample.csv` |
| `data/raw/risk/calfire_fhsz_sra_contra_costa_bbox.geojson` | geojson | 241 | 6 | 3.55 | `data/processed/samples/calfire_fhsz_sra_contra_costa_bbox_properties_sample.csv` |
| `data/raw/risk/fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson` | geojson | 6435 | 16 | 2.44 | `data/processed/samples/fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes_properties_sample.csv` |
| `data/raw/san_francisco/README.md` | other |  |  | 0.00 | `` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_01.csv` | tabular | 175000 | 30 | 69.41 | `data/processed/samples/building_permits_selected_part_01_sample.csv` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_02.csv` | tabular | 175000 | 30 | 70.60 | `data/processed/samples/building_permits_selected_part_02_sample.csv` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_03.csv` | tabular | 175000 | 30 | 70.52 | `data/processed/samples/building_permits_selected_part_03_sample.csv` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_04.csv` | tabular | 175000 | 30 | 70.69 | `data/processed/samples/building_permits_selected_part_04_sample.csv` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_05.csv` | tabular | 175000 | 30 | 70.67 | `data/processed/samples/building_permits_selected_part_05_sample.csv` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_06.csv` | tabular | 175000 | 30 | 70.46 | `data/processed/samples/building_permits_selected_part_06_sample.csv` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_07.csv` | tabular | 175000 | 30 | 70.20 | `data/processed/samples/building_permits_selected_part_07_sample.csv` |
| `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_08.csv` | tabular | 66589 | 30 | 26.85 | `data/processed/samples/building_permits_selected_part_08_sample.csv` |
| `data/raw/schools/cde_public_schools_and_districts.txt` | tabular | 18390 | 46 | 8.38 | `data/processed/samples/cde_public_schools_and_districts_sample.csv` |

## Blocked Or Deferred Sources

| Source | Status | Reason | Next step |
| --- | --- | --- | --- |
| `county_sales_records` | blocked | No verified free automated bulk comparable-sales source for San Ramon/Contra Costa yet. | Secure permitted comps source or seed 50-200 sale records manually. |
| `bay_area_511_gtfs` | needs_api_key | 511 GTFS and transit APIs require a 511 API token. | Register at 511.org, set TRANSIT_511_API_KEY, then download regional operator_id=RG feed. |
| `geofabrik_california_full_pbf` | deferred_large_file | Full California OSM PBF is about 1.3 GB. This repo uses an Overpass San Ramon POI extract instead. | Download only if team needs offline OSM processing: https://download.geofabrik.de/north-america/us/california.html |
| `census_acs_5yr` | needs_api_key | Current Census API requests redirect to missing_key.html without a key. | Set CENSUS_API_KEY and pull selected ACS variables for Contra Costa/SF tracts and block groups. |
| `cde_public_districts_txt` | manual_download_or_retry | The separate district-only endpoint returned an HTML bot-validation page in automated download. The combined schools/districts file is included. | Use the included CDE schools/districts file or manually download the district-only extract from the CDE directory page if needed. |

## EDA Takeaways

1. **San Ramon/Contra Costa story path is feasible for the graph base.** Contra Costa publishes parcel, zoning, land-use, city-limit, and urban-limit-line shapefiles.
2. **Risk layers are real and source-backed.** FEMA NFHL and CAL FIRE FHSZ services are queryable; this repo includes Contra Costa bbox extracts.
3. **School metadata is downloadable.** CDE public school/district files are included, but school-quality scoring should be derived carefully from public performance data rather than proprietary ratings.
4. **SF is still the easier data-first demo.** The SF permit extract has over one million records and good structured fields; in this repository it is stored as selected-column split CSV parts.
5. **Comparable sales is still the critical path.** Without sale price/date/property attributes, Lattice can explain context and risk but cannot honestly claim production-grade valuation.

## What I Would Do Next

1. Install geospatial tooling: `pip install geopandas pyogrio shapely duckdb duckdb-engine` or use QGIS/PostGIS.
2. Read Contra Costa parcels and city limits, filter parcels to San Ramon, and compute parcel count plus address/APN completeness.
3. Spatially join San Ramon parcels to zoning, land-use, FEMA flood zones, CAL FIRE FHSZ, OSM POIs, schools, and Census tracts.
4. Build a `property_features` table with one row per parcel or candidate listing.
5. Separately validate comparable-sales acquisition before building a valuation model.
