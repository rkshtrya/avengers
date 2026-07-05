#!/usr/bin/env python3
"""
Domain EDA for the Project Lattice data review.

This complements the lightweight schema inventory with product-oriented checks:
parcel coverage, permit distributions, school coverage, risk category counts,
OSM POI mix, and a sufficiency matrix for the Lattice MVP.
"""

from __future__ import annotations

import csv
import json
import math
import struct
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
PROFILES = REPORTS / "profiles"


def clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"nan", "none", "null"} else text


def pct(part: int | float, total: int | float) -> str:
    if not total:
        return "0.0%"
    return f"{100 * part / total:.1f}%"


def md_counter(counter: Counter, limit: int = 12) -> str:
    rows = ["| Value | Count |", "| --- | ---: |"]
    for key, count in counter.most_common(limit):
        rows.append(f"| `{clean(key) or '(blank)'}` | {count:,} |")
    return "\n".join(rows)


def write_counter_csv(path: Path, counter: Counter) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["value", "count"])
        for key, count in counter.most_common():
            writer.writerow([key, count])


def dbf_fields(dbf_bytes: bytes) -> tuple[list[dict], int, int, int]:
    num_records = int.from_bytes(dbf_bytes[4:8], "little")
    header_len = struct.unpack("<H", dbf_bytes[8:10])[0]
    record_len = struct.unpack("<H", dbf_bytes[10:12])[0]
    fields = []
    pos = 32
    while pos + 32 <= header_len and dbf_bytes[pos] != 0x0D:
        raw_name = dbf_bytes[pos:pos + 11].split(b"\x00", 1)[0]
        fields.append({
            "name": raw_name.decode("latin1", errors="ignore").strip(),
            "type": chr(dbf_bytes[pos + 11]),
            "length": dbf_bytes[pos + 16],
        })
        pos += 32
    return fields, num_records, header_len, record_len


def iter_dbf_rows_from_zip(path: Path):
    with zipfile.ZipFile(path) as z:
        dbf_name = next(name for name in z.namelist() if name.lower().endswith(".dbf"))
        data = z.read(dbf_name)
    fields, num_records, header_len, record_len = dbf_fields(data)
    offset = header_len
    for _ in range(num_records):
        rec = data[offset:offset + record_len]
        offset += record_len
        if not rec or rec[:1] == b"*":
            continue
        cursor = 1
        row = {}
        for field in fields:
            raw = rec[cursor:cursor + field["length"]]
            cursor += field["length"]
            row[field["name"]] = raw.decode("latin1", errors="ignore").strip()
        yield row


def first_dbf_rows(path: Path, limit: int = 5000) -> list[dict]:
    rows = []
    for row in iter_dbf_rows_from_zip(path):
        rows.append(row)
        if len(rows) >= limit:
            break
    return rows


def profile_parcels() -> dict:
    path = RAW / "contra_costa" / "Parcels_Public_May2026.zip"
    rows = 0
    city = Counter()
    zip_codes = Counter()
    address_complete = 0
    apn_present = 0
    for row in iter_dbf_rows_from_zip(path):
        rows += 1
        city[clean(row.get("S_CTY_ABBR"))] += 1
        zip_codes[clean(row.get("S_ZIP"))] += 1
        if clean(row.get("APN")):
            apn_present += 1
        if clean(row.get("S_STR_NBR")) and clean(row.get("S_STR_NM")) and clean(row.get("S_CTY_ABBR")):
            address_complete += 1
    write_counter_csv(PROFILES / "contra_costa_parcel_city_counts.csv", city)
    write_counter_csv(PROFILES / "contra_costa_parcel_zip_counts.csv", zip_codes)
    return {
        "rows": rows,
        "apn_present": apn_present,
        "address_complete": address_complete,
        "city": city,
        "zip_codes": zip_codes,
    }


def profile_small_shapefiles() -> dict:
    outputs = {}
    for label, rel in {
        "city_limits": "BND_DCD_City_Limits.zip",
        "zoning": "PLA_DCD_Zoning.zip",
        "general_plan_land_use": "PLA_DCD_GPLanduseElement.zip",
    }.items():
        rows = first_dbf_rows(RAW / "contra_costa" / rel)
        field_names = list(rows[0].keys()) if rows else []
        value_counts = {}
        for field in field_names:
            counter = Counter(clean(row.get(field)) for row in rows)
            if 1 < len(counter) <= min(100, len(rows)):
                value_counts[field] = counter
        outputs[label] = {"rows_sampled": len(rows), "fields": field_names, "value_counts": value_counts}
    return outputs


def profile_sf_permits() -> dict:
    path = RAW / "san_francisco" / "building_permits_selected.csv"
    parts_dir = RAW / "san_francisco" / "building_permits_selected_parts"
    if path.exists():
        paths = [path]
    else:
        paths = sorted(parts_dir.glob("*.csv"))
        if not paths:
            raise FileNotFoundError(f"Missing {path} and no split CSV parts found in {parts_dir}")
    usecols = [
        "permit_type_definition",
        "permit_creation_date",
        "filed_date",
        "issued_date",
        "completed_date",
        "status",
        "zipcode",
        "existing_use",
        "proposed_use",
        "estimated_cost",
        "revised_cost",
        "adu",
        "supervisor_district",
        "neighborhoods_analysis_boundaries",
        "location",
    ]
    rows = 0
    status = Counter()
    permit_type = Counter()
    year = Counter()
    neighborhood = Counter()
    zipcode = Counter()
    adu = Counter()
    locations = 0
    estimated_cost_count = 0
    revised_cost_count = 0
    estimated_cost_sum = 0.0
    revised_cost_sum = 0.0
    date_min = None
    date_max = None

    for csv_path in paths:
        for chunk in pd.read_csv(csv_path, usecols=usecols, chunksize=100000, low_memory=False):
            rows += len(chunk)
            status.update(chunk["status"].fillna("").astype(str).str.strip())
            permit_type.update(chunk["permit_type_definition"].fillna("").astype(str).str.strip())
            neighborhood.update(chunk["neighborhoods_analysis_boundaries"].fillna("").astype(str).str.strip())
            zipcode.update(chunk["zipcode"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.strip())
            adu.update(chunk["adu"].fillna("").astype(str).str.strip())
            locations += int(chunk["location"].fillna("").astype(str).str.startswith("POINT").sum())

            created = pd.to_datetime(chunk["permit_creation_date"], errors="coerce")
            year.update(created.dt.year.dropna().astype(int).astype(str))
            cmin = created.min()
            cmax = created.max()
            if pd.notna(cmin):
                date_min = cmin if date_min is None else min(date_min, cmin)
            if pd.notna(cmax):
                date_max = cmax if date_max is None else max(date_max, cmax)

            estimated = pd.to_numeric(chunk["estimated_cost"], errors="coerce")
            revised = pd.to_numeric(chunk["revised_cost"], errors="coerce")
            estimated_cost_count += int(estimated.notna().sum())
            revised_cost_count += int(revised.notna().sum())
            estimated_cost_sum += float(estimated.fillna(0).sum())
            revised_cost_sum += float(revised.fillna(0).sum())

    write_counter_csv(PROFILES / "sf_permit_status_counts.csv", status)
    write_counter_csv(PROFILES / "sf_permit_type_counts.csv", permit_type)
    write_counter_csv(PROFILES / "sf_permit_creation_year_counts.csv", year)
    write_counter_csv(PROFILES / "sf_permit_neighborhood_counts.csv", neighborhood)
    return {
        "rows": rows,
        "status": status,
        "permit_type": permit_type,
        "year": year,
        "neighborhood": neighborhood,
        "zipcode": zipcode,
        "adu": adu,
        "locations": locations,
        "estimated_cost_count": estimated_cost_count,
        "estimated_cost_sum": estimated_cost_sum,
        "revised_cost_count": revised_cost_count,
        "revised_cost_sum": revised_cost_sum,
        "date_min": "" if date_min is None else str(date_min.date()),
        "date_max": "" if date_max is None else str(date_max.date()),
    }


def profile_schools() -> dict:
    path = RAW / "schools" / "cde_public_schools_and_districts.txt"
    df = pd.read_csv(path, sep="\t", dtype=str, low_memory=False, encoding_errors="ignore")
    columns = {c.lower(): c for c in df.columns}
    county_col = columns.get("county")
    city_col = columns.get("city")
    district_col = columns.get("district")
    status_col = columns.get("status") or columns.get("statustype")
    county_counts = Counter(df[county_col].fillna("").str.strip()) if county_col else Counter()
    status_counts = Counter(df[status_col].fillna("").str.strip()) if status_col else Counter()
    city_counts = Counter(df[city_col].fillna("").str.strip()) if city_col else Counter()
    contra_costa = df[df[county_col].fillna("").str.lower().eq("contra costa")] if county_col else df.iloc[0:0]
    san_ramon_mask = pd.Series(False, index=df.index)
    if city_col:
        san_ramon_mask |= df[city_col].fillna("").str.contains("San Ramon", case=False, regex=False)
    if district_col:
        san_ramon_mask |= df[district_col].fillna("").str.contains("San Ramon", case=False, regex=False)
    san_ramon = df[san_ramon_mask]
    write_counter_csv(PROFILES / "cde_school_county_counts.csv", county_counts)
    write_counter_csv(PROFILES / "cde_school_city_counts.csv", city_counts)
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "county_counts": county_counts,
        "status_counts": status_counts,
        "contra_costa_rows": len(contra_costa),
        "san_ramon_rows": len(san_ramon),
    }


def geojson_property_counter(path: Path, field: str) -> Counter:
    payload = json.loads(path.read_text(encoding="utf-8"))
    counter = Counter()
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        counter[clean(props.get(field))] += 1
    return counter


def profile_risk() -> dict:
    fema_zone = geojson_property_counter(
        RAW / "risk" / "fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson",
        "FLD_ZONE",
    )
    fema_sfha = geojson_property_counter(
        RAW / "risk" / "fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson",
        "SFHA_TF",
    )
    lra = geojson_property_counter(RAW / "risk" / "calfire_fhsz_lra_contra_costa_bbox.geojson", "FHSZ_Description")
    sra = geojson_property_counter(RAW / "risk" / "calfire_fhsz_sra_contra_costa_bbox.geojson", "FHSZ_Description")
    write_counter_csv(PROFILES / "fema_flood_zone_counts.csv", fema_zone)
    write_counter_csv(PROFILES / "calfire_lra_fhsz_counts.csv", lra)
    write_counter_csv(PROFILES / "calfire_sra_fhsz_counts.csv", sra)
    return {"fema_zone": fema_zone, "fema_sfha": fema_sfha, "lra": lra, "sra": sra}


def profile_osm() -> dict:
    payload = json.loads((RAW / "osm" / "osm_san_ramon_pois.json").read_text(encoding="utf-8"))
    elements = payload.get("elements", [])
    amenity = Counter()
    shop = Counter()
    leisure = Counter()
    public_transport = Counter()
    named = 0
    for element in elements:
        tags = element.get("tags") or {}
        if clean(tags.get("name")):
            named += 1
        for field, counter in [
            ("amenity", amenity),
            ("shop", shop),
            ("leisure", leisure),
            ("public_transport", public_transport),
        ]:
            value = clean(tags.get(field))
            if value:
                counter[value] += 1
    write_counter_csv(PROFILES / "osm_amenity_counts.csv", amenity)
    write_counter_csv(PROFILES / "osm_shop_counts.csv", shop)
    write_counter_csv(PROFILES / "osm_leisure_counts.csv", leisure)
    return {
        "rows": len(elements),
        "named": named,
        "amenity": amenity,
        "shop": shop,
        "leisure": leisure,
        "public_transport": public_transport,
    }


def write_report(results: dict) -> None:
    parcels = results["parcels"]
    sf = results["sf_permits"]
    schools = results["schools"]
    risk = results["risk"]
    osm = results["osm"]
    small = results["small_shapefiles"]

    lines = []
    lines.append("# Project Lattice Domain EDA Findings")
    lines.append("")
    lines.append("This is the product-facing EDA readout: not just what files exist, but whether they support the graph, explanation layer, and valuation path we want.")
    lines.append("")
    lines.append("## Sufficiency Matrix")
    lines.append("")
    lines.append("| Product need | Current data status | Verdict |")
    lines.append("| --- | --- | --- |")
    lines.append("| Parcel graph / property identity | Contra Costa parcels include APN, address fields, city, and ZIP for 387,835 parcels. | Sufficient for prototype graph base. |")
    lines.append("| San Ramon filtering | San Ramon is a city inside Contra Costa County. Countywide city limits are included, and parcels have city/ZIP fields. | Sufficient for first pass; verify exact San Ramon boundary spatially. |")
    lines.append("| Zoning / land-use explanation | Zoning and general-plan land-use shapefiles are included. | Sufficient for context, subject to incorporated-city zoning coverage check. |")
    lines.append("| Risk explanation | CAL FIRE FHSZ geometry and FEMA NFHL flood attributes are included for the project bbox. | Sufficient for review; parcel-level flood joins need full FEMA geometry or ArcGIS/QGIS pull. |")
    lines.append("| Schools / districts | CDE public schools/districts file is included. | Sufficient for school metadata; performance/ratings need additional public accountability data. |")
    lines.append("| Amenity / neighborhood context | OSM San Ramon POI extract is included. | Sufficient for prototype proximity features. |")
    lines.append("| Permit/demo signal | SF permits include 1,291,589 selected-column records stored as split CSV parts. | Strong for SF demo; San Ramon permit feed still needs source validation. |")
    lines.append("| Transit context | 511 GTFS/API requires token. | Not included yet. |")
    lines.append("| Comparable sales / valuation target | No verified free bulk San Ramon/Contra Costa sale-price source is included. | Not sufficient for production valuation until acquired. |")
    lines.append("")
    lines.append("## Contra Costa Parcels")
    lines.append("")
    lines.append(f"- Parcel records: {parcels['rows']:,}")
    lines.append(f"- APN present: {parcels['apn_present']:,} ({pct(parcels['apn_present'], parcels['rows'])})")
    lines.append(f"- Complete street-number/name/city address fields: {parcels['address_complete']:,} ({pct(parcels['address_complete'], parcels['rows'])})")
    lines.append("")
    lines.append("Top parcel city values:")
    lines.append(md_counter(parcels["city"]))
    lines.append("")
    lines.append("Top parcel ZIP values:")
    lines.append(md_counter(parcels["zip_codes"], limit=10))
    lines.append("")
    lines.append("## Planning Layers")
    lines.append("")
    for label, item in small.items():
        lines.append(f"- `{label}` fields: {', '.join(item['fields'])}")
    lines.append("")
    lines.append("These layers are best reviewed in QGIS or GeoPandas to confirm the relationship between county zoning and incorporated San Ramon zoning.")
    lines.append("")
    lines.append("## San Francisco Permit Signal")
    lines.append("")
    lines.append(f"- Permit rows: {sf['rows']:,}")
    lines.append(f"- Creation date range: {sf['date_min']} to {sf['date_max']}")
    lines.append(f"- Rows with point location: {sf['locations']:,} ({pct(sf['locations'], sf['rows'])})")
    lines.append(f"- Estimated-cost present: {sf['estimated_cost_count']:,} ({pct(sf['estimated_cost_count'], sf['rows'])}); total estimated cost in rows: ${sf['estimated_cost_sum']:,.0f}")
    lines.append(f"- Revised-cost present: {sf['revised_cost_count']:,} ({pct(sf['revised_cost_count'], sf['rows'])}); total revised cost in rows: ${sf['revised_cost_sum']:,.0f}")
    lines.append("")
    lines.append("Top permit statuses:")
    lines.append(md_counter(sf["status"]))
    lines.append("")
    lines.append("Top permit types:")
    lines.append(md_counter(sf["permit_type"]))
    lines.append("")
    lines.append("Top permit creation years by row count:")
    year_counter = Counter(dict(sorted(sf["year"].items(), key=lambda kv: kv[0], reverse=True)))
    lines.append(md_counter(year_counter, limit=12))
    lines.append("")
    lines.append("## Schools")
    lines.append("")
    lines.append(f"- CDE school/district rows: {schools['rows']:,}")
    lines.append(f"- Contra Costa rows: {schools['contra_costa_rows']:,}")
    lines.append(f"- Rows with San Ramon in city or district name: {schools['san_ramon_rows']:,}")
    lines.append("")
    lines.append("Top school counties:")
    lines.append(md_counter(schools["county_counts"], limit=10))
    lines.append("")
    lines.append("School status mix:")
    lines.append(md_counter(schools["status_counts"], limit=10))
    lines.append("")
    lines.append("## Risk Layers")
    lines.append("")
    lines.append("FEMA flood zone counts in Contra Costa bbox:")
    lines.append(md_counter(risk["fema_zone"]))
    lines.append("")
    lines.append("FEMA SFHA flag counts:")
    lines.append(md_counter(risk["fema_sfha"]))
    lines.append("")
    lines.append("CAL FIRE LRA FHSZ counts:")
    lines.append(md_counter(risk["lra"]))
    lines.append("")
    lines.append("CAL FIRE SRA FHSZ counts:")
    lines.append(md_counter(risk["sra"]))
    lines.append("")
    lines.append("## OSM San Ramon POIs")
    lines.append("")
    lines.append(f"- OSM elements: {osm['rows']:,}")
    lines.append(f"- Named elements: {osm['named']:,} ({pct(osm['named'], osm['rows'])})")
    lines.append("")
    lines.append("Top amenities:")
    lines.append(md_counter(osm["amenity"]))
    lines.append("")
    lines.append("Top shops:")
    lines.append(md_counter(osm["shop"]))
    lines.append("")
    lines.append("Top leisure values:")
    lines.append(md_counter(osm["leisure"]))
    lines.append("")
    lines.append("## Recommended Decisions")
    lines.append("")
    lines.append("1. Keep San Ramon inside Contra Costa County as the explainability/knowledge-graph target, because the countywide public spatial context can be filtered to the city.")
    lines.append("2. Use San Francisco permits as the data-rich demo path if we need a fast proof that Lattice can ingest and explain real property-related events.")
    lines.append("3. Keep model training paused until a legal comparable-sales source is secured; use the existing package for feature engineering, joins, and graph design first.")
    lines.append("4. Next technical step: build a `property_features` table from parcels joined to city limits, zoning, land use, risk, Census geography, schools, and OSM POIs.")
    lines.append("5. Next business/data step: decide whether we buy/license comps, partner for MLS access, or seed a small manually verified sale set for prototype valuation only.")
    (REPORTS / "domain_eda_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    PROFILES.mkdir(parents=True, exist_ok=True)
    results = {
        "parcels": profile_parcels(),
        "small_shapefiles": profile_small_shapefiles(),
        "sf_permits": profile_sf_permits(),
        "schools": profile_schools(),
        "risk": profile_risk(),
        "osm": profile_osm(),
    }
    write_report(results)
    print(f"Wrote {REPORTS / 'domain_eda_findings.md'}")
    print(f"Wrote profile CSVs in {PROFILES}")


if __name__ == "__main__":
    main()
