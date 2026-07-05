# Raw Data Guide

This folder contains the actual downloaded data files.

Use `../../DATA_FILES.md` for the direct file index. This page explains the folders.

## Folder Map

| Folder | Geography | What is inside | Why it matters |
| --- | --- | --- | --- |
| `contra_costa/` | Contra Costa County | Parcels, city limits, zoning, general plan, urban limit line, LAFCO sphere of influence | Main San Ramon / Contra Costa graph base. |
| `census/` | California statewide plus U.S. county boundary context | 2025 Census TIGER tract, block group, place shapefiles, plus 2025 cartographic county boundaries | Used to connect parcels to Census geography and show Contra Costa County inside California. |
| `schools/` | California statewide | CDE public schools and districts text file | Used for school and district context. |
| `risk/` | Contra Costa project area | CAL FIRE hazard files and FEMA flood-zone attributes | Used for risk explanations. |
| `osm/` | San Ramon bounding box | OpenStreetMap POIs from Overpass | Used for nearby amenities and neighborhood context. |
| `san_francisco/` | City and County of San Francisco | Building permits split into CSV parts | Useful for a data-rich permit ingestion demo. |

## How To Read These Files

Most files are spatial files:

- `.zip` shapefile packages can be opened in QGIS, GeoPandas, or many GIS tools.
- `.geojson` files can be opened in QGIS, GeoPandas, or a text editor for small previews.
- `.json` OSM files are best read with Python or a JSON viewer.
- `.csv` permit parts can be opened with pandas or spreadsheet tools, but they are large.

## Do Not Edit Raw Files

The files in this folder should be treated like evidence.

If a cleaner version is needed, write it to a processed folder and document the script that created it.
