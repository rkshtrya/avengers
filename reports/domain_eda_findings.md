# Project Lattice Domain EDA Findings

This is the product-facing EDA readout: not just what files exist, but whether they support the graph, explanation layer, and valuation path we want.

## Sufficiency Matrix

| Product need | Current data status | Verdict |
| --- | --- | --- |
| Parcel graph / property identity | Contra Costa parcels include APN, address fields, city, and ZIP for 387,835 parcels. | Sufficient for prototype graph base. |
| San Ramon filtering | Contra Costa city limits are included and parcels have city/ZIP fields. | Sufficient for first pass; verify exact San Ramon boundary spatially. |
| Zoning / land-use explanation | Zoning and general-plan land-use shapefiles are included. | Sufficient for context, subject to incorporated-city zoning coverage check. |
| Risk explanation | CAL FIRE FHSZ geometry and FEMA NFHL flood attributes are included for the project bbox. | Sufficient for review; parcel-level flood joins need full FEMA geometry or ArcGIS/QGIS pull. |
| Schools / districts | CDE public schools/districts file is included. | Sufficient for school metadata; performance/ratings need additional public accountability data. |
| Amenity / neighborhood context | OSM San Ramon POI extract is included. | Sufficient for prototype proximity features. |
| Permit/demo signal | SF permits include 1,291,589 selected-column records stored as split CSV parts. | Strong for SF demo; San Ramon permit feed still needs source validation. |
| Transit context | 511 GTFS/API requires token. | Not included yet. |
| Comparable sales / valuation target | No verified free bulk San Ramon/Contra Costa sale-price source is included. | Not sufficient for production valuation until acquired. |

## Contra Costa Parcels

- Parcel records: 387,835
- APN present: 387,835 (100.0%)
- Complete street-number/name/city address fields: 365,318 (94.2%)

Top parcel city values:
| Value | Count |
| --- | ---: |
| `CNCD` | 38,993 |
| `ANT` | 35,706 |
| `RCHMD` | 35,432 |
| `WALCR` | 34,949 |
| `SNRMN` | 27,756 |
| `BRTWD` | 23,844 |
| `DAN` | 22,237 |
| `PITTS` | 20,790 |
| `MRTNZ` | 17,161 |
| `OKLY` | 15,937 |
| `PLHL` | 12,247 |
| `SNPAB` | 11,095 |

Top parcel ZIP values:
| Value | Count |
| --- | ---: |
| `94565` | 26,529 |
| `94513` | 23,918 |
| `94509` | 19,920 |
| `94553` | 18,435 |
| `94561` | 15,943 |
| `94531` | 15,777 |
| `94806` | 15,106 |
| `94521` | 14,888 |
| `94583` | 14,688 |
| `94804` | 13,518 |

## Planning Layers

- `city_limits` fields: NAME, URL, Place, SHAPE_Leng, SHAPE_Area
- `zoning` fields: ZONING, OVERLAY, ZONE_OVER, Zoning_Tex, Overlay_Te, Zoning_Sta, URL, Shape_Leng, Shape_Area
- `general_plan_land_use` fields: GPLU_DESG, GP_TEXT, GP_DENSITY, URL, Shape_Leng, Shape_Area

These layers are best reviewed in QGIS or GeoPandas to confirm the relationship between county zoning and incorporated San Ramon zoning.

## San Francisco Permit Signal

- Permit rows: 1,291,589
- Creation date range: 1901-03-10 to 2026-07-02
- Rows with point location: 1,288,352 (99.7%)
- Estimated-cost present: 1,147,938 (88.9%); total estimated cost in rows: $120,865,831,177
- Revised-cost present: 895,475 (69.3%); total revised cost in rows: $104,401,704,731

Top permit statuses:
| Value | Count |
| --- | ---: |
| `complete` | 740,442 |
| `issued` | 247,431 |
| `expired` | 232,110 |
| `cancelled` | 43,192 |
| `filed` | 11,364 |
| `withdrawn` | 11,220 |
| `reinstated` | 1,496 |
| `approved` | 1,175 |
| `filing` | 1,097 |
| `suspend` | 639 |
| `disapproved` | 574 |
| `triage` | 440 |

Top permit types:
| Value | Count |
| --- | ---: |
| `otc alterations permit` | 970,808 |
| `additions alterations or repairs` | 271,178 |
| `sign - erect` | 21,141 |
| `new construction wood frame` | 13,115 |
| `demolitions` | 7,305 |
| `wall or painted sign` | 4,133 |
| `new construction` | 2,492 |
| `grade or quarry or fill or excavate` | 833 |
| `(blank)` | 584 |

Top permit creation years by row count:
| Value | Count |
| --- | ---: |
| `2019` | 42,682 |
| `2018` | 42,612 |
| `2017` | 41,170 |
| `2007` | 40,523 |
| `2015` | 40,132 |
| `2016` | 39,731 |
| `2008` | 38,209 |
| `2006` | 37,305 |
| `2014` | 36,658 |
| `2005` | 35,592 |
| `2013` | 35,203 |
| `2004` | 34,894 |

## Schools

- CDE school/district rows: 18,390
- Contra Costa rows: 479
- Rows with San Ramon in city or district name: 44

Top school counties:
| Value | Count |
| --- | ---: |
| `Los Angeles` | 3,742 |
| `San Diego` | 1,195 |
| `Orange` | 936 |
| `San Bernardino` | 909 |
| `Santa Clara` | 798 |
| `Riverside` | 796 |
| `Alameda` | 791 |
| `Fresno` | 651 |
| `Sacramento` | 649 |
| `Contra Costa` | 479 |

School status mix:
| Value | Count |
| --- | ---: |
| `Active` | 11,594 |
| `Closed` | 5,335 |
| `Merged` | 1,441 |
| `Pending` | 20 |

## Risk Layers

FEMA flood zone counts in Contra Costa bbox:
| Value | Count |
| --- | ---: |
| `X` | 3,852 |
| `AE` | 1,777 |
| `A` | 356 |
| `VE` | 272 |
| `AO` | 95 |
| `AH` | 38 |
| `D` | 29 |
| `OPEN WATER` | 15 |
| `V` | 1 |

FEMA SFHA flag counts:
| Value | Count |
| --- | ---: |
| `F` | 3,896 |
| `T` | 2,539 |

CAL FIRE LRA FHSZ counts:
| Value | Count |
| --- | ---: |
| `NonWildland` | 135 |
| `Moderate` | 91 |
| `High` | 80 |
| `Very High` | 22 |

CAL FIRE SRA FHSZ counts:
| Value | Count |
| --- | ---: |
| `Moderate` | 117 |
| `High` | 94 |
| `Very High` | 30 |

## OSM San Ramon POIs

- OSM elements: 7,026
- Named elements: 2,681 (38.2%)

Top amenities:
| Value | Count |
| --- | ---: |
| `parking` | 690 |
| `parking_space` | 459 |
| `bicycle_parking` | 269 |
| `bench` | 237 |
| `restaurant` | 229 |
| `fast_food` | 113 |
| `waste_basket` | 110 |
| `dentist` | 78 |
| `toilets` | 75 |
| `school` | 64 |
| `cafe` | 57 |
| `bank` | 51 |

Top shops:
| Value | Count |
| --- | ---: |
| `beauty` | 76 |
| `car_repair` | 59 |
| `hairdresser` | 58 |
| `clothes` | 31 |
| `convenience` | 30 |
| `car` | 30 |
| `supermarket` | 28 |
| `dry_cleaning` | 23 |
| `storage_rental` | 21 |
| `massage` | 18 |
| `copyshop` | 16 |
| `sports` | 15 |

Top leisure values:
| Value | Count |
| --- | ---: |
| `swimming_pool` | 969 |
| `pitch` | 594 |
| `picnic_table` | 252 |
| `playground` | 228 |
| `park` | 135 |
| `garden` | 124 |
| `fitness_centre` | 47 |
| `track` | 26 |
| `sports_centre` | 20 |
| `bleachers` | 20 |
| `outdoor_seating` | 19 |
| `fitness_station` | 17 |

## Decisions We Recommend

1. Keep San Ramon/Contra Costa as the explainability/knowledge-graph target, because the public spatial context is good.
2. Use San Francisco permits as the data-rich demo path if we need a fast proof that Lattice can ingest and explain real property-related events.
3. Keep model training paused until a legal comparable-sales source is secured; use the existing package for feature engineering, joins, and graph design first.
4. Next technical step: build a `property_features` table from parcels joined to city limits, zoning, land use, risk, Census geography, schools, and OSM POIs.
5. Next business/data step: decide whether we buy/license comps, partner for MLS access, or seed a small manually verified sale set for prototype valuation only.
