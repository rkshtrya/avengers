#!/usr/bin/env python3
"""
Download a practical Project Lattice data review package.

This script intentionally avoids non-stdlib dependencies so teammates can rerun
it in a fresh environment. It downloads open, moderate-size datasets and creates
metadata records for sources that are credentialed, too large, or unresolved.
"""

from __future__ import annotations

import csv
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"
REPORTS = ROOT / "reports"

TODAY = "2026-07-05"


DIRECT_DOWNLOADS = [
    {
        "source_id": "contra_costa_parcels",
        "url": "https://gis.cccounty.us/Downloads/Assessor/Parcels_Public_May2026.zip",
        "path": RAW / "contra_costa" / "Parcels_Public_May2026.zip",
        "notes": "Base parcel geometry for Contra Costa County.",
    },
    {
        "source_id": "contra_costa_city_limits",
        "url": "https://gis.cccounty.us/Downloads/Planning/BND_DCD_City_Limits.zip",
        "path": RAW / "contra_costa" / "BND_DCD_City_Limits.zip",
        "notes": "City boundaries, useful for San Ramon filtering.",
    },
    {
        "source_id": "contra_costa_lafco_soi",
        "url": "https://gis.cccounty.us/Downloads/Planning/BND_LAFCO_City_SOI.zip",
        "path": RAW / "contra_costa" / "BND_LAFCO_City_SOI.zip",
        "notes": "Sphere-of-influence context.",
    },
    {
        "source_id": "contra_costa_general_plan_land_use",
        "url": "https://gis.cccounty.us/Downloads/Planning/PLA_DCD_GPLanduseElement.zip",
        "path": RAW / "contra_costa" / "PLA_DCD_GPLanduseElement.zip",
        "notes": "General plan land-use layer.",
    },
    {
        "source_id": "contra_costa_urban_limit_line",
        "url": "https://gis.cccounty.us/Downloads/Planning/PLA_DCD_ULL.zip",
        "path": RAW / "contra_costa" / "PLA_DCD_ULL.zip",
        "notes": "Urban limit line context.",
    },
    {
        "source_id": "contra_costa_zoning",
        "url": "https://gis.cccounty.us/Downloads/Planning/PLA_DCD_Zoning.zip",
        "path": RAW / "contra_costa" / "PLA_DCD_Zoning.zip",
        "notes": "County zoning layer. Needs incorporated-city coverage check.",
    },
    {
        "source_id": "census_tiger_ca_tracts",
        "url": "https://www2.census.gov/geo/tiger/TIGER2025/TRACT/tl_2025_06_tract.zip",
        "path": RAW / "census" / "tl_2025_06_tract.zip",
        "notes": "California census tract boundaries.",
    },
    {
        "source_id": "census_tiger_ca_block_groups",
        "url": "https://www2.census.gov/geo/tiger/TIGER2025/BG/tl_2025_06_bg.zip",
        "path": RAW / "census" / "tl_2025_06_bg.zip",
        "notes": "California census block-group boundaries.",
    },
    {
        "source_id": "census_tiger_ca_places",
        "url": "https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_06_place.zip",
        "path": RAW / "census" / "tl_2025_06_place.zip",
        "notes": "California incorporated place boundaries.",
    },
    {
        "source_id": "census_cb_us_counties_500k",
        "url": "https://www2.census.gov/geo/tiger/GENZ2025/shp/cb_2025_us_county_500k.zip",
        "path": RAW / "census" / "cb_2025_us_county_500k.zip",
        "notes": "Generalized U.S. county boundaries used for the California / Contra Costa location snapshot.",
    },
    {
        "source_id": "cde_public_schools_txt",
        "url": "https://www.cde.ca.gov/schooldirectory/report?rid=dl1&tp=txt",
        "path": RAW / "schools" / "cde_public_schools_and_districts.txt",
        "notes": "CDE public schools and districts tab-delimited file.",
    },
    {
        "source_id": "calfire_fhsz_catalog_metadata",
        "url": "https://data.ca.gov/api/3/action/package_show?id=fire-hazard-severity-zone-viewer1",
        "path": META / "calfire_fhsz_catalog_metadata.json",
        "notes": "State catalogue metadata for current CAL FIRE FHSZ viewer.",
    },
    {
        "source_id": "calfire_fhsz_webmap",
        "url": "https://CALFIRE-Forestry.maps.arcgis.com/sharing/rest/content/items/a86cdcb4a66344da8f44ad75e9fdb4c7/data?f=json",
        "path": META / "calfire_fhsz_webmap.json",
        "notes": "Underlying web map with FHSZ service URLs.",
    },
    {
        "source_id": "fema_nfhl_mapserver_metadata",
        "url": "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer?f=pjson",
        "path": META / "fema_nfhl_mapserver_metadata.json",
        "notes": "FEMA NFHL ArcGIS service metadata.",
    },
]


BLOCKED_OR_DEFERRED = [
    {
        "source_id": "county_sales_records",
        "status": "blocked",
        "reason": "No verified free automated bulk comparable-sales source for San Ramon/Contra Costa yet.",
        "next_step": "Secure permitted comps source or seed 50-200 sale records manually.",
    },
    {
        "source_id": "bay_area_511_gtfs",
        "status": "needs_api_key",
        "reason": "511 GTFS and transit APIs require a 511 API token.",
        "next_step": "Register at 511.org, set TRANSIT_511_API_KEY, then download regional operator_id=RG feed.",
    },
    {
        "source_id": "geofabrik_california_full_pbf",
        "status": "deferred_large_file",
        "reason": "Full California OSM PBF is about 1.3 GB. This repo uses an Overpass San Ramon POI extract instead.",
        "next_step": "Download only if team needs offline OSM processing: https://download.geofabrik.de/north-america/us/california.html",
    },
    {
        "source_id": "census_acs_5yr",
        "status": "needs_api_key",
        "reason": "Current Census API requests redirect to missing_key.html without a key.",
        "next_step": "Set CENSUS_API_KEY and pull selected ACS variables for Contra Costa/SF tracts and block groups.",
    },
    {
        "source_id": "cde_public_districts_txt",
        "status": "manual_download_or_retry",
        "reason": "The separate district-only endpoint returned an HTML bot-validation page in automated download. The combined schools/districts file is included.",
        "next_step": "Use the included CDE schools/districts file or manually download the district-only extract from the CDE directory page if needed.",
    },
]


ARCGIS_BBOX_EXTRACTS = [
    {
        "source_id": "fema_nfhl_contra_costa_flood_hazard_zones_attributes",
        "layer_url": "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28",
        "path": RAW / "risk" / "fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson",
        "bbox": [-122.55, 37.70, -121.45, 38.15],
        "out_fields": "DFIRM_ID,FLD_AR_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,V_DATUM,DEPTH,LEN_UNIT,VELOCITY,VEL_UNIT,AR_REVERT,BFE_REVERT,DEP_REVERT,DUAL_ZONE,SOURCE_CIT",
        "return_geometry": False,
        "format": "json",
        "notes": "FEMA flood hazard zone attributes intersecting approximate Contra Costa bbox. Geometry is omitted because the full NFHL geometry query is very large/unstable.",
    },
    {
        "source_id": "calfire_fhsz_lra_contra_costa_bbox",
        "layer_url": "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSALRA25_v1_All/FeatureServer/0",
        "path": RAW / "risk" / "calfire_fhsz_lra_contra_costa_bbox.geojson",
        "bbox": [-122.55, 37.70, -121.45, 38.15],
        "out_fields": "OBJECTID,SRA,FHSZ,FHSZ_Description,Shape__Area,Shape__Length",
        "notes": "CAL FIRE Local Responsibility Area FHSZ within approximate Contra Costa bbox.",
    },
    {
        "source_id": "calfire_fhsz_sra_contra_costa_bbox",
        "layer_url": "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSZSRA_23_3/FeatureServer/0",
        "path": RAW / "risk" / "calfire_fhsz_sra_contra_costa_bbox.geojson",
        "bbox": [-122.55, 37.70, -121.45, 38.15],
        "out_fields": "OBJECTID,SRA,FHSZ,FHSZ_Description,Shape__Area,Shape__Length",
        "notes": "CAL FIRE State Responsibility Area FHSZ within approximate Contra Costa bbox.",
    },
]


SOCRATA_EXPORTS = [
    {
        "source_id": "san_francisco_permits_selected",
        "path": RAW / "san_francisco" / "building_permits_selected.csv",
        "url": (
            "https://data.sfgov.org/resource/i98e-djp9.csv?"
            "$select=permit_number,permit_type,permit_type_definition,permit_creation_date,"
            "block,lot,filed_date,issued_date,approved_date,completed_date,status,status_date,street_number,"
            "street_name,street_suffix,zipcode,existing_use,proposed_use,existing_units,"
            "proposed_units,estimated_cost,revised_cost,adu,primary_address_flag,supervisor_district,"
            "neighborhoods_analysis_boundaries,record_id,data_as_of,location,point_source"
            "&$limit=1500000"
        ),
        "notes": "Selected columns for all available SF building permit rows, enough for EDA without full wide payload.",
    },
]


OVERPASS_EXTRACTS = [
    {
        "source_id": "osm_san_ramon_pois",
        "path": RAW / "osm" / "osm_san_ramon_pois.json",
        "bbox": (37.70, -122.05, 37.85, -121.85),
        "notes": "OpenStreetMap amenities/shops/leisure/public_transport in a San Ramon bbox.",
    }
]


def log(message: str) -> None:
    print(f"[download] {message}", flush=True)


def urlretrieve(url: str, path: Path, timeout: int = 120) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "ProjectLatticeDataReview/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status = getattr(response, "status", None)
        content_type = response.headers.get("content-type", "")
        with path.open("wb") as f:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
    return {
        "status": status,
        "content_type": content_type,
        "bytes": path.stat().st_size,
        "elapsed_sec": round(time.time() - started, 2),
    }


def download_direct(manifest: list[dict]) -> None:
    for item in DIRECT_DOWNLOADS + SOCRATA_EXPORTS:
        path = item["path"]
        if path.exists() and path.stat().st_size > 0:
            log(f"skip existing {path}")
            status = {"status": "existing", "bytes": path.stat().st_size}
        else:
            log(f"download {item['source_id']} -> {path}")
            try:
                status = urlretrieve(item["url"], path, timeout=240)
                status["status"] = status.get("status") or "downloaded"
            except Exception as exc:
                status = {"status": "failed", "error": str(exc)}
        manifest.append({
            "source_id": item["source_id"],
            "path": str(path.relative_to(ROOT)),
            "url": item["url"],
            "notes": item["notes"],
            **status,
        })


def arcgis_query(layer_url: str, params: dict, timeout: int = 120) -> dict:
    query_url = f"{layer_url.rstrip('/')}/query?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(query_url, headers={"User-Agent": "ProjectLatticeDataReview/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
    return json.loads(data.decode("utf-8"))


def download_arcgis_bbox(manifest: list[dict]) -> None:
    for item in ARCGIS_BBOX_EXTRACTS:
        path = item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 0:
            log(f"skip existing {path}")
            manifest.append({
                "source_id": item["source_id"],
                "path": str(path.relative_to(ROOT)),
                "url": item["layer_url"],
                "notes": item["notes"],
                "status": "existing",
                "bytes": path.stat().st_size,
            })
            continue
        xmin, ymin, xmax, ymax = item["bbox"]
        geom = json.dumps({"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax, "spatialReference": {"wkid": 4326}})
        features = []
        offset = 0
        page_size = 2000
        log(f"arcgis bbox {item['source_id']}")
        try:
            return_geometry = item.get("return_geometry", True)
            while True:
                params = {
                    "f": item.get("format", "geojson"),
                    "where": "1=1",
                    "outFields": item["out_fields"],
                    "returnGeometry": "true" if return_geometry else "false",
                    "geometry": geom,
                    "geometryType": "esriGeometryEnvelope",
                    "inSR": "4326",
                    "outSR": "4326",
                    "spatialRel": "esriSpatialRelIntersects",
                    "resultOffset": offset,
                    "resultRecordCount": page_size,
                }
                page = arcgis_query(item["layer_url"], params, timeout=180)
                batch = page.get("features", [])
                features.extend(batch)
                if len(batch) < page_size:
                    break
                offset += page_size
            if return_geometry:
                payload_features = features
            else:
                payload_features = [
                    {
                        "type": "Feature",
                        "geometry": None,
                        "properties": feature.get("attributes", feature.get("properties", {})),
                    }
                    for feature in features
                ]
            payload = {"type": "FeatureCollection", "features": payload_features}
            path.write_text(json.dumps(payload), encoding="utf-8")
            status = {"status": "downloaded", "features": len(features), "bytes": path.stat().st_size}
        except Exception as exc:
            status = {"status": "failed", "error": str(exc)}
        manifest.append({
            "source_id": item["source_id"],
            "path": str(path.relative_to(ROOT)),
            "url": item["layer_url"],
            "notes": item["notes"],
            **status,
        })


def download_overpass(manifest: list[dict]) -> None:
    endpoint = "https://overpass-api.de/api/interpreter"
    for item in OVERPASS_EXTRACTS:
        path = item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        south, west, north, east = item["bbox"]
        bbox = f"{south},{west},{north},{east}"
        query = f"""
[out:json][timeout:90];
(
  node["amenity"]({bbox});
  way["amenity"]({bbox});
  node["shop"]({bbox});
  way["shop"]({bbox});
  node["leisure"]({bbox});
  way["leisure"]({bbox});
  node["public_transport"]({bbox});
  way["public_transport"]({bbox});
);
out center tags;
"""
        log(f"overpass {item['source_id']}")
        try:
            data = urllib.parse.urlencode({"data": query}).encode("utf-8")
            req = urllib.request.Request(endpoint, data=data, headers={"User-Agent": "ProjectLatticeDataReview/1.0"})
            with urllib.request.urlopen(req, timeout=180) as response:
                raw = response.read()
            path.write_bytes(raw)
            payload = json.loads(raw.decode("utf-8"))
            status = {"status": "downloaded", "elements": len(payload.get("elements", [])), "bytes": path.stat().st_size}
        except Exception as exc:
            status = {"status": "failed", "error": str(exc)}
        manifest.append({
            "source_id": item["source_id"],
            "path": str(path.relative_to(ROOT)),
            "url": endpoint,
            "notes": item["notes"],
            **status,
        })


def write_manifest(manifest: list[dict]) -> None:
    META.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    manifest_path = META / "download_manifest.json"
    manifest_path.write_text(json.dumps({
        "created_at": TODAY,
        "root": str(ROOT),
        "downloads": manifest,
        "blocked_or_deferred": BLOCKED_OR_DEFERRED,
    }, indent=2), encoding="utf-8")
    csv_path = REPORTS / "download_manifest.csv"
    fieldnames = sorted({k for row in manifest for k in row.keys()})
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest)

    blocked_path = REPORTS / "blocked_or_deferred_sources.csv"
    with blocked_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_id", "status", "reason", "next_step"])
        writer.writeheader()
        writer.writerows(BLOCKED_OR_DEFERRED)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    download_direct(manifest)
    download_arcgis_bbox(manifest)
    download_overpass(manifest)
    write_manifest(manifest)
    log(f"done: {META / 'download_manifest.json'}")


if __name__ == "__main__":
    main()
