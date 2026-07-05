# Actual Data Files In This Repo

The actual downloaded source files are committed under `data/raw/`.

This page helps us find the raw data files quickly. For a plain-English explanation of each dataset, `docs/dataset-catalog.md` has the walkthrough.

## Contra Costa County Data

These are the core files for the San Ramon / Contra Costa graph-first path.

| Dataset | Actual file on GitHub | What it is |
| --- | --- | --- |
| Contra Costa parcels | `data/raw/contra_costa/Parcels_Public_May2026.zip` | Parcel shapefile zip from Contra Costa County GIS / Assessor. |
| City limits | `data/raw/contra_costa/BND_DCD_City_Limits.zip` | City boundary shapefile zip from Contra Costa County GIS / Planning. |
| LAFCO sphere of influence | `data/raw/contra_costa/BND_LAFCO_City_SOI.zip` | Sphere-of-influence boundary shapefile zip. |
| General plan land use | `data/raw/contra_costa/PLA_DCD_GPLanduseElement.zip` | General-plan land-use shapefile zip. |
| Urban limit line | `data/raw/contra_costa/PLA_DCD_ULL.zip` | Urban-limit-line shapefile zip. |
| Zoning | `data/raw/contra_costa/PLA_DCD_Zoning.zip` | County zoning shapefile zip. |

## Census Boundary Data

These are Census boundary files used for California, Contra Costa, San Ramon, and the location snapshot.

| Dataset | Actual file on GitHub | What it is |
| --- | --- | --- |
| Census tracts | `data/raw/census/tl_2025_06_tract.zip` | California tract boundary shapefile zip. |
| Census block groups | `data/raw/census/tl_2025_06_bg.zip` | California block-group boundary shapefile zip. |
| Census places | `data/raw/census/tl_2025_06_place.zip` | California incorporated-place boundary shapefile zip. |
| Census county boundaries | `data/raw/census/cb_2025_us_county_500k.zip` | U.S. county cartographic boundary shapefile zip, used here to show Contra Costa County inside California. |

## Schools

| Dataset | Actual file on GitHub | What it is |
| --- | --- | --- |
| CDE public schools and districts | `data/raw/schools/cde_public_schools_and_districts.txt` | California Department of Education school/district directory table. |

## Risk Layers

| Dataset | Actual file on GitHub | What it is |
| --- | --- | --- |
| CAL FIRE LRA fire hazard zones | `data/raw/risk/calfire_fhsz_lra_contra_costa_bbox.geojson` | Local Responsibility Area wildfire hazard extract for the Contra Costa project area. |
| CAL FIRE SRA fire hazard zones | `data/raw/risk/calfire_fhsz_sra_contra_costa_bbox.geojson` | State Responsibility Area wildfire hazard extract for the Contra Costa project area. |
| FEMA flood zone attributes | `data/raw/risk/fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson` | FEMA NFHL flood-zone attributes for the Contra Costa project area. |

## Amenities / POIs

| Dataset | Actual file on GitHub | What it is |
| --- | --- | --- |
| OSM San Ramon POIs | `data/raw/osm/osm_san_ramon_pois.json` | OpenStreetMap amenities, shops, leisure, and public-transport POIs for the San Ramon bbox. |

## San Francisco Permit Data

The San Francisco permit extract is large, so it is committed as split CSV parts.

Folder:

`data/raw/san_francisco/building_permits_selected_parts/`

Files:

| Part | Actual file on GitHub |
| --- | --- |
| 1 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_01.csv` |
| 2 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_02.csv` |
| 3 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_03.csv` |
| 4 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_04.csv` |
| 5 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_05.csv` |
| 6 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_06.csv` |
| 7 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_07.csv` |
| 8 | `data/raw/san_francisco/building_permits_selected_parts/building_permits_selected_part_08.csv` |

To rebuild the original single CSV locally:

```bash
python3 scripts/reconstruct_large_files.py
```

## Not Included Yet

These are still pending and are not in `data/raw/` yet:

| Dataset | Why it is not included yet |
| --- | --- |
| Comparable sales | Need a legal source, MLS/partner feed, purchased file, or manually seeded sale set. |
| 511 transit / GTFS | Needs a 511 API token. |
| Census ACS variables | Needs Census API key for the current pull. |
