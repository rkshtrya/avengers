# Dataset Catalog

This is the plain-English guide to the data in the repo. For each dataset I list what it is, what geography it covers, where it came from, and how I expect us to use it for Project Lattice.

## Quick Table

| Dataset | Geography / county | Kind of data | Source agency | Status | Local path |
| --- | --- | --- | --- | --- | --- |
| Contra Costa Assessor Parcels | Contra Costa County, California | Parcel geometry + assessor parcel identifiers/address fields | Contra Costa County GIS / Assessor | Downloaded | `data/raw/contra_costa/Parcels_Public_May2026.zip` |
| Contra Costa City Limits | Contra Costa County, California | Municipal boundary polygons | Contra Costa County GIS / Planning | Downloaded | `data/raw/contra_costa/BND_DCD_City_Limits.zip` |
| Contra Costa LAFCO Sphere of Influence | Contra Costa County, California | Sphere-of-influence boundary polygons | Contra Costa County GIS / Planning | Downloaded | `data/raw/contra_costa/BND_LAFCO_City_SOI.zip` |
| Contra Costa General Plan Land Use | Contra Costa County, California | General-plan land-use polygons | Contra Costa County GIS / Planning | Downloaded | `data/raw/contra_costa/PLA_DCD_GPLanduseElement.zip` |
| Contra Costa Urban Limit Line | Contra Costa County, California | Urban limit line polygons | Contra Costa County GIS / Planning | Downloaded | `data/raw/contra_costa/PLA_DCD_ULL.zip` |
| Contra Costa Zoning | Contra Costa County, California | Zoning polygons | Contra Costa County GIS / Planning | Downloaded; coverage check needed | `data/raw/contra_costa/PLA_DCD_Zoning.zip` |
| Census TIGER Tracts | California statewide | Census tract boundary shapefile | U.S. Census Bureau TIGER/Line | Downloaded | `data/raw/census/tl_2025_06_tract.zip` |
| Census TIGER Block Groups | California statewide | Census block-group boundary shapefile | U.S. Census Bureau TIGER/Line | Downloaded | `data/raw/census/tl_2025_06_bg.zip` |
| Census TIGER Places | California statewide | Incorporated place boundary shapefile | U.S. Census Bureau TIGER/Line | Downloaded | `data/raw/census/tl_2025_06_place.zip` |
| CDE Public Schools and Districts | California statewide; includes Contra Costa and San Ramon rows | School/district directory table | California Department of Education | Downloaded | `data/raw/schools/cde_public_schools_and_districts.txt` |
| CAL FIRE Local Responsibility Area Fire Hazard Zones | Contra Costa County project bbox | Wildfire hazard polygons | CAL FIRE / Office of the State Fire Marshal | Downloaded | `data/raw/risk/calfire_fhsz_lra_contra_costa_bbox.geojson` |
| CAL FIRE State Responsibility Area Fire Hazard Zones | Contra Costa County project bbox | Wildfire hazard polygons | CAL FIRE / Office of the State Fire Marshal | Downloaded | `data/raw/risk/calfire_fhsz_sra_contra_costa_bbox.geojson` |
| FEMA National Flood Hazard Layer Attributes | Contra Costa County project bbox | Flood hazard zone attributes | FEMA NFHL ArcGIS service | Downloaded attributes; parcel-level geometry join still pending | `data/raw/risk/fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson` |
| OpenStreetMap San Ramon POIs | San Ramon / Contra Costa County bbox | Amenities, shops, leisure, public-transport POIs | OpenStreetMap via Overpass API | Downloaded | `data/raw/osm/osm_san_ramon_pois.json` |
| San Francisco Building Permits | City and County of San Francisco | Building permit table with status, dates, cost, use, units, and point location | DataSF / San Francisco Department of Building Inspection | Downloaded as split CSV parts | `data/raw/san_francisco/building_permits_selected_parts/` |
| Comparable Sales | Target metro, likely Contra Costa / San Ramon first | Sale price, sale date, property attributes, APN/address match key | TBD: county records, MLS/partner feed, purchased data, or manually seeded records | Pending | `Not included yet` |
| 511 Bay Area Transit / GTFS | Bay Area, including Contra Costa County | Transit stops, routes, schedules, service calendars | 511.org | Pending API token | `Not included yet` |
| Census ACS 5-Year Variables | United States; planned pull for Contra Costa/SF tracts and block groups | Demographic and housing attributes | U.S. Census Bureau ACS API | Pending Census API key | `Not included yet` |

## Dataset Notes

### Contra Costa Assessor Parcels

- **Geography / county:** Contra Costa County, California
- **Kind of data:** Parcel geometry + assessor parcel identifiers/address fields
- **Source agency:** Contra Costa County GIS / Assessor
- **Local path:** `data/raw/contra_costa/Parcels_Public_May2026.zip`
- **Source URL:** https://gis.cccounty.us/Downloads/Assessor/Parcels_Public_May2026.zip
- **What to look for:** APN, parcel/address fields, parcel boundaries. This is the base property graph layer.
- **Status:** Downloaded

### Contra Costa City Limits

- **Geography / county:** Contra Costa County, California
- **Kind of data:** Municipal boundary polygons
- **Source agency:** Contra Costa County GIS / Planning
- **Local path:** `data/raw/contra_costa/BND_DCD_City_Limits.zip`
- **Source URL:** https://gis.cccounty.us/Downloads/Planning/BND_DCD_City_Limits.zip
- **What to look for:** City boundary polygons used to filter parcels to San Ramon and validate parcel city codes.
- **Status:** Downloaded

### Contra Costa LAFCO Sphere of Influence

- **Geography / county:** Contra Costa County, California
- **Kind of data:** Sphere-of-influence boundary polygons
- **Source agency:** Contra Costa County GIS / Planning
- **Local path:** `data/raw/contra_costa/BND_LAFCO_City_SOI.zip`
- **Source URL:** https://gis.cccounty.us/Downloads/Planning/BND_LAFCO_City_SOI.zip
- **What to look for:** Planning/jurisdiction context around city influence areas.
- **Status:** Downloaded

### Contra Costa General Plan Land Use

- **Geography / county:** Contra Costa County, California
- **Kind of data:** General-plan land-use polygons
- **Source agency:** Contra Costa County GIS / Planning
- **Local path:** `data/raw/contra_costa/PLA_DCD_GPLanduseElement.zip`
- **Source URL:** https://gis.cccounty.us/Downloads/Planning/PLA_DCD_GPLanduseElement.zip
- **What to look for:** Land-use designations that can support explainable context around property and neighborhood character.
- **Status:** Downloaded

### Contra Costa Urban Limit Line

- **Geography / county:** Contra Costa County, California
- **Kind of data:** Urban limit line polygons
- **Source agency:** Contra Costa County GIS / Planning
- **Local path:** `data/raw/contra_costa/PLA_DCD_ULL.zip`
- **Source URL:** https://gis.cccounty.us/Downloads/Planning/PLA_DCD_ULL.zip
- **What to look for:** Growth boundary context for development constraints or expansion signals.
- **Status:** Downloaded

### Contra Costa Zoning

- **Geography / county:** Contra Costa County, California
- **Kind of data:** Zoning polygons
- **Source agency:** Contra Costa County GIS / Planning
- **Local path:** `data/raw/contra_costa/PLA_DCD_Zoning.zip`
- **Source URL:** https://gis.cccounty.us/Downloads/Planning/PLA_DCD_Zoning.zip
- **What to look for:** Zoning classifications and overlays. We still need to verify incorporated San Ramon coverage.
- **Status:** Downloaded; coverage check needed

### Census TIGER Tracts

- **Geography / county:** California statewide
- **Kind of data:** Census tract boundary shapefile
- **Source agency:** U.S. Census Bureau TIGER/Line
- **Local path:** `data/raw/census/tl_2025_06_tract.zip`
- **Source URL:** https://www2.census.gov/geo/tiger/TIGER2025/TRACT/tl_2025_06_tract.zip
- **What to look for:** Tract IDs and geometry for joining parcels to Census geography.
- **Status:** Downloaded

### Census TIGER Block Groups

- **Geography / county:** California statewide
- **Kind of data:** Census block-group boundary shapefile
- **Source agency:** U.S. Census Bureau TIGER/Line
- **Local path:** `data/raw/census/tl_2025_06_bg.zip`
- **Source URL:** https://www2.census.gov/geo/tiger/TIGER2025/BG/tl_2025_06_bg.zip
- **What to look for:** Block-group IDs and geometry for finer demographic joins once ACS variables are pulled.
- **Status:** Downloaded

### Census TIGER Places

- **Geography / county:** California statewide
- **Kind of data:** Incorporated place boundary shapefile
- **Source agency:** U.S. Census Bureau TIGER/Line
- **Local path:** `data/raw/census/tl_2025_06_place.zip`
- **Source URL:** https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_06_place.zip
- **What to look for:** Place boundaries for city-level geography checks.
- **Status:** Downloaded

### CDE Public Schools and Districts

- **Geography / county:** California statewide; includes Contra Costa and San Ramon rows
- **Kind of data:** School/district directory table
- **Source agency:** California Department of Education
- **Local path:** `data/raw/schools/cde_public_schools_and_districts.txt`
- **Source URL:** https://www.cde.ca.gov/schooldirectory/report?rid=dl1&tp=txt
- **What to look for:** School names, districts, locations, grade spans, status, and administrative metadata.
- **Status:** Downloaded

### CAL FIRE Local Responsibility Area Fire Hazard Zones

- **Geography / county:** Contra Costa County project bbox
- **Kind of data:** Wildfire hazard polygons
- **Source agency:** CAL FIRE / Office of the State Fire Marshal
- **Local path:** `data/raw/risk/calfire_fhsz_lra_contra_costa_bbox.geojson`
- **Source URL:** https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSALRA25_v1_All/FeatureServer/0
- **What to look for:** Local responsibility area fire hazard classes: NonWildland, Moderate, High, Very High.
- **Status:** Downloaded

### CAL FIRE State Responsibility Area Fire Hazard Zones

- **Geography / county:** Contra Costa County project bbox
- **Kind of data:** Wildfire hazard polygons
- **Source agency:** CAL FIRE / Office of the State Fire Marshal
- **Local path:** `data/raw/risk/calfire_fhsz_sra_contra_costa_bbox.geojson`
- **Source URL:** https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSZSRA_23_3/FeatureServer/0
- **What to look for:** State responsibility area fire hazard classes: Moderate, High, Very High.
- **Status:** Downloaded

### FEMA National Flood Hazard Layer Attributes

- **Geography / county:** Contra Costa County project bbox
- **Kind of data:** Flood hazard zone attributes
- **Source agency:** FEMA NFHL ArcGIS service
- **Local path:** `data/raw/risk/fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson`
- **Source URL:** https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28
- **What to look for:** Flood zone code, SFHA flag, base flood elevation fields. Geometry is omitted for this extract.
- **Status:** Downloaded attributes; parcel-level geometry join still pending

### OpenStreetMap San Ramon POIs

- **Geography / county:** San Ramon / Contra Costa County bbox
- **Kind of data:** Amenities, shops, leisure, public-transport POIs
- **Source agency:** OpenStreetMap via Overpass API
- **Local path:** `data/raw/osm/osm_san_ramon_pois.json`
- **Source URL:** https://overpass-api.de/api/interpreter
- **What to look for:** Nearby amenities such as restaurants, parks, schools, shops, parking, and leisure features.
- **Status:** Downloaded

### San Francisco Building Permits

- **Geography / county:** City and County of San Francisco
- **Kind of data:** Building permit table with status, dates, cost, use, units, and point location
- **Source agency:** DataSF / San Francisco Department of Building Inspection
- **Local path:** `data/raw/san_francisco/building_permits_selected_parts/`
- **Source URL:** https://data.sfgov.org/resource/i98e-djp9.csv
- **What to look for:** 1.29M permit records for a data-rich ingestion/explainability demo. Stored as split CSV parts.
- **Status:** Downloaded as split CSV parts

### Comparable Sales

- **Geography / county:** Target metro, likely Contra Costa / San Ramon first
- **Kind of data:** Sale price, sale date, property attributes, APN/address match key
- **Source agency:** TBD: county records, MLS/partner feed, purchased data, or manually seeded records
- **Local path:** `Not included yet`
- **Source URL:** TBD
- **What to look for:** This is the missing valuation target. We need this before presenting production-grade valuation.
- **Status:** Pending

### 511 Bay Area Transit / GTFS

- **Geography / county:** Bay Area, including Contra Costa County
- **Kind of data:** Transit stops, routes, schedules, service calendars
- **Source agency:** 511.org
- **Local path:** `Not included yet`
- **Source URL:** https://511.org/open-data/transit
- **What to look for:** Commute and transit-access features after an API token is available.
- **Status:** Pending API token

### Census ACS 5-Year Variables

- **Geography / county:** United States; planned pull for Contra Costa/SF tracts and block groups
- **Kind of data:** Demographic and housing attributes
- **Source agency:** U.S. Census Bureau ACS API
- **Local path:** `Not included yet`
- **Source URL:** https://www.census.gov/data/developers/data-sets/acs-5year.html
- **What to look for:** Median income, commute, tenure, vacancy, housing cost, and related context variables.
- **Status:** Pending Census API key
