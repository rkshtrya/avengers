# Project Lattice: How We Understand The Product And Data Plan

## Core Product Thesis

Project Lattice is more than another automated valuation model. The wedge is explainable, evidence-backed real estate valuation: we estimate whether a property is fairly priced, overpriced, or undervalued, then show the sourced chain of reasons behind that judgment.

The deck positions Lattice between two existing worlds:

- Consumer tools such as Zillow: easy to use, but mostly black-box and weak on "why."
- Enterprise property graphs such as Cherre: deep relational analytics, but too expensive and institution-focused for everyday buyers and smaller investors.

So the product needs to optimize for three things at once:

- A credible valuation range.
- A plain-English explanation of the drivers.
- A provenance trail that lets the user verify each claim.

The right mental model for us is a real-estate knowledge graph plus agents. The graph stores typed entities and sourced relationships. The agents read and write that graph, but the graph and verifier are what make the product defensible.

## MVP Geography We Can Consider

We see two viable MVP paths.

For the general audience, the geography reads like this: **Contra Costa County is the larger county in the East Bay, and San Ramon is a city inside that county**. When we say "San Ramon / Contra Costa," we mean a San Ramon-focused product story built from the official countywide data that covers it.

### Option A: San Ramon / Contra Costa County story-first MVP

This matches the deck example and the suburban buyer use case. Contra Costa is usable because it publishes parcel and zoning downloads, and 511 covers regional transit. The likely friction is sale-price/comps access: public records exist, but automated bulk access is not as clean as the slide deck implies.

We would use this path if the demo story matters more than data convenience.

### Option B: San Francisco data-first MVP

San Francisco has stronger civic open-data infrastructure, including a verified Socrata building-permits endpoint. This is the fastest route to a working demo with permits, zoning/planning signals, transit, amenities, risk, and neighborhood context.

We would use this path if shipping the six-week capstone is the priority. We can still tell the Lattice story and later port to San Ramon.

## Data source matrix

| Layer | Best MVP source | What it gives us | Graph nodes/edges | Reliability | Notes |
| --- | --- | --- | --- | --- | --- |
| Parcels and base property geography | [Contra Costa GIS downloads](https://gis.cccounty.us/Downloads/) -> `Assessor/Parcels_Public_May2026.zip`; for Alameda use [Alameda Assessor Parcel Viewer](https://www.acassessor.org/homeowners/parcel-viewer/) | Parcel geometry, APN, address/location context | `Property`, `Parcel`, `located_in`, `has_boundary` | High for geometry, but not a legal survey | Contra Costa has a downloadable parcel zip. Alameda's site is view-oriented; bulk data is purchasable. |
| Property assessment and characteristics | [Alameda assessed value lookup](https://www.acassessor.org/homeowners/assessed-value-look-up/), Alameda bulk data fee schedule, Contra Costa Assessor/property tools | Assessed values, tax/assessment context, property facts where available | `assessed_at`, `has_characteristic`, `tax_roll_record` | Medium-high | Good for provenance, but assessed value is not market value. |
| Comparable sale prices | County recorder/assessor records; limited manual seed set; optional third-party transaction feed | Sale price, sale date, beds/baths/sqft if available | `ComparableSale`, `sold_for`, `sold_on`, `similar_to` | Variable | This is the riskiest layer. For a serious backtest, confirm bulk access or use a jurisdiction with clean transaction data. |
| Permits and development signals | Contra Costa planning downloads; city permit portals; for SF, verified endpoint: `https://data.sfgov.org/resource/i98e-djp9.json?$limit=1` | Permit type/status, dates, costs, unit changes, location | `Permit`, `improves`, `nearby_permit_signal`, `changes_units` | High if official | Permits are strong "hidden upside/downside" signals. |
| Zoning and land use | [Contra Costa Planning downloads](https://gis.cccounty.us/Downloads/Planning/) including zoning and general-plan land-use zips; city zoning GIS where available | Zoning class, land-use constraints, redevelopment context | `zoned_for`, `allows`, `constrained_by` | High | Verify city-vs-county jurisdiction. County zoning may not cover incorporated city rules. |
| Demographics and economics | [Census ACS 5-year API](https://www.census.gov/data/developers/data-sets/acs-5year.html), [TIGER/Line shapefiles](https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/tiger-geo-line.html) | Income, commute mode/time, tenure, vacancy, housing costs, tract/block-group geometry | `Neighborhood`, `has_demographic_context`, `has_commute_profile` | High but lagged | Use ACS as slow-moving context, not a point-in-time price signal. |
| Schools | [CDE public schools/districts files](https://www.cde.ca.gov/ds/si/ds/pubschls.asp), [NCES CCD files](https://nces.ed.gov/ccd/files.asp), [Urban Institute Education Data Portal](https://educationdata.urban.org/documentation/) | School locations, districts, grade spans, enrollment, demographics | `School`, `served_by`, `near`, `ranked_by_metric` | Medium-high | Avoid proprietary GreatSchools-style ratings unless licensed. Derive an internal school score from public test/accountability data. |
| Transit and commute | [511 Bay Area Transit Data](https://511.org/open-data/transit), GTFS regional feed with `operator_id=RG`, GTFS-RT where useful | Stops, routes, schedules, stop proximity, commute paths | `TransitStop`, `Route`, `near`, `commute_time_to` | High | 511 requires an API token and has a default rate limit. Use static GTFS for MVP. |
| Amenities and POIs | [OpenStreetMap Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API), [Geofabrik California extract](https://download.geofabrik.de/north-america/us/california.html) | Parks, groceries, trails, roads, walkability context | `Amenity`, `near`, `walkable_to` | Medium | OSM is open but variable quality. Attribute correctly under [ODbL](https://www.openstreetmap.org/copyright). |
| Flood risk | [FEMA NFHL GIS services](https://hazards.fema.gov/femaportal/wps/portal/NFHLWMS) | Flood hazard zones, FIRM panels, effective dates | `RiskZone`, `inside`, `flood_risk` | High | Use as checkable risk evidence; FEMA provides ArcGIS REST/WMS/WFS. |
| Wildfire risk | [CAL FIRE Fire Hazard Severity Zones](https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones) | Moderate/high/very high fire hazard zones | `RiskZone`, `inside`, `wildfire_hazard` | High | Relevant for Bay Area hillside/suburban properties. |
| Boundaries | County/city GIS, Census TIGER, CDE/NCES school/district data | City, county, tract, school district, neighborhood boundaries | `located_in`, `within_district`, `within_tract` | High | Boundary alignment is critical for joins. |

## Recommended Source Strategy

We should start with a graph that answers fewer questions very well rather than a broad graph that makes claims we cannot verify:

1. Pick one MVP geography.
2. Create a property table from parcel geometry plus a small set of known sold properties.
3. Attach public context: tract demographics, nearest transit stops, nearby permits, zoning, FEMA flood zone, CAL FIRE hazard zone, OSM amenities, and school/district metadata.
4. Build a comparable-sale adjustment model that uses public micro-factors, not a broad macro intrinsic valuation.
5. Make every derived claim store `source_url`, `source_id`, `source_date`, `retrieved_at`, and `confidence`.

## Minimum Viable Graph Schema

### Core nodes

- `Property`: APN, address, lat/lon, parcel geometry, beds/baths/sqft if available.
- `Sale`: price, sale date, source record, arms-length flag if available.
- `Neighborhood`: tract/block group/city/neighborhood.
- `School`: name, district, grade span, location, public metrics.
- `TransitStop`: stop ID, agency, route/service metadata.
- `Permit`: permit number, type, status, cost, issue date, location.
- `RiskZone`: flood, wildfire, liquefaction or other hazards.
- `Amenity`: OSM POI, park, grocery, trail, etc.
- `BuyerProfile`: budget, commute target, school preference, risk tolerance.

### Core edges

- `Property LOCATED_IN Neighborhood`
- `Property NEAR TransitStop/Amenity/School`
- `Property ZONED_FOR ZoningDistrict`
- `Property INSIDE RiskZone`
- `Property HAS_PERMIT_SIGNAL Permit`
- `Property COMPARABLE_TO Property`
- `Sale SOLD_PROPERTY Property`
- `BuyerProfile PRIORITIZES School/Commute/Risk/Budget`
- `Claim SUPPORTED_BY SourceRecord`

## Verifier Requirements

We can treat every Lattice explanation as incomplete unless it can pass these checks:

- The claim has at least one source.
- The source URL or dataset endpoint is stored.
- The source date and retrieval time are stored.
- The claim is based on a deterministic graph edge or a model output with logged inputs.
- The claim is not stronger than the source supports. Example: OSM proximity can support "near a grocery store," but not "high-quality grocery access" unless another metric defines quality.

## Biggest Data Risks

1. Sale/comps data is the hardest part. County-level public access is inconsistent, and bulk sale records may require purchase or manual extraction.
2. School quality is politically and legally sensitive. Use transparent public metrics instead of opaque third-party ratings.
3. City permit and zoning coverage varies. The ingestion layer can store gaps explicitly instead of pretending coverage is complete.
4. OSM is useful, and it works best when it is not the sole basis for high-stakes claims.
5. "Near transit" is not enough. The product needs commute-time reasoning, ideally using GTFS plus street-network routing.

## Best First Build Path

For a capstone-quality MVP, we can take this path:

1. Use Contra Costa parcels/zoning if you want to stay aligned with San Ramon.
2. Use 511 GTFS regional transit, Census ACS/TIGER, FEMA NFHL, CAL FIRE FHSZ, CDE/NCES schools, and OSM amenities.
3. Seed 50-200 comparable sales manually or from a permitted source.
4. Backtest only against that known sale set.
5. Make the demo show the explainability loop: valuation -> drivers -> source links -> verifier status.

For a faster technical demo, we can take this path:

1. Use San Francisco as the first metro because the open-data surface is richer.
2. Use DataSF building permits, 511 transit, ACS/TIGER, FEMA, CAL FIRE, OSM, and school datasets.
3. Defer polished sale-price ingestion until the source is licensed or verified.

## Verification Status

As of July 3, 2026, our read is that source sufficiency is mixed:

- Sufficient for the explanation layer: yes. Parcels, zoning, permits, transit, demographics, schools, amenities, flood risk, and wildfire risk can support a sourced "why" experience.
- Sufficient for a capstone MVP: yes, if comparable sales are seeded manually or obtained from a permitted source.
- Sufficient for a production valuation engine: not yet. The unresolved dependency is reliable, automatable comparable-sale transaction data with sale price, sale date, and property characteristics.

Concrete checks performed:

- Contra Costa parcel download responded with HTTP 200 for `https://gis.cccounty.us/Downloads/Assessor/Parcels_Public_May2026.zip`; file size was about 40 MB.
- San Francisco building permit API returned live records from `https://data.sfgov.org/resource/i98e-djp9.json`.
- FEMA NFHL ArcGIS service responded with live map/query metadata from `https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer?f=pjson`, including `Flood Hazard Zones`.
- Geofabrik California OSM extract responded with HTTP 200 for the current California `.osm.pbf` file.
- OpenStreetMap API capabilities responded as online.
- 511's documentation confirms GTFS, regional `RG` feeds, GTFS-Realtime, stops, routes, and timetable APIs are available with an API token.
- Census documentation confirms ACS 5-year data is available for counties, places, tracts, and block groups, but current API calls require an API key.

The decision point is therefore not whether enough public data exists. It does. The decision point is whether we can secure or seed enough comparable sales to make the valuation number credible.
