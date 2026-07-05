#!/usr/bin/env python3
"""
Dependency-light EDA for Project Lattice downloaded sources.

This produces:
- reports/dataset_inventory.csv
- reports/eda_summary.md
- data/processed/samples/*

It inspects CSV/TXT/JSON/GeoJSON and shapefile zip DBF attributes. Full spatial
joins still need GeoPandas, DuckDB Spatial, QGIS, or PostGIS.
"""

from __future__ import annotations

import csv
import json
import math
import os
import struct
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SAMPLES = PROCESSED / "samples"
REPORTS = ROOT / "reports"


def safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def detect_sep(path: Path) -> str:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:10000]
    if sample.count("\t") > sample.count(","):
        return "\t"
    return ","


def line_count(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for _ in f)


def summarize_tabular(path: Path, source_id: str) -> dict:
    sep = detect_sep(path)
    rows = max(line_count(path) - 1, 0)
    sample = pd.read_csv(path, sep=sep, nrows=10000, low_memory=False, encoding_errors="ignore")
    sample_path = SAMPLES / f"{source_id}_sample.csv"
    sample.head(250).to_csv(sample_path, index=False)
    missing = sample.isna().mean().sort_values(ascending=False).head(15)
    summary = {
        "source_id": source_id,
        "path": safe_rel(path),
        "kind": "tabular",
        "bytes": path.stat().st_size,
        "row_count": rows,
        "column_count": len(sample.columns),
        "columns": "|".join(map(str, sample.columns)),
        "sample_path": safe_rel(sample_path),
        "notes": f"sep={repr(sep)}; top_missing_sample={missing.to_dict()}",
    }
    return summary


def dbf_schema_and_sample(dbf_bytes: bytes, sample_n: int = 5) -> dict:
    # dBASE III/IV header.
    if len(dbf_bytes) < 32:
        return {"error": "DBF too small"}
    num_records = struct.unpack("<I", dbf_bytes[4:8])[0]
    header_len = struct.unpack("<H", dbf_bytes[8:10])[0]
    record_len = struct.unpack("<H", dbf_bytes[10:12])[0]
    fields = []
    pos = 32
    while pos + 32 <= header_len and dbf_bytes[pos] != 0x0D:
        raw_name = dbf_bytes[pos:pos + 11].split(b"\x00", 1)[0]
        name = raw_name.decode("latin1", errors="ignore").strip()
        ftype = chr(dbf_bytes[pos + 11])
        flen = dbf_bytes[pos + 16]
        fdec = dbf_bytes[pos + 17]
        fields.append({"name": name, "type": ftype, "length": flen, "decimal": fdec})
        pos += 32

    samples = []
    offset = header_len
    for _ in range(min(sample_n, num_records)):
        rec = dbf_bytes[offset:offset + record_len]
        offset += record_len
        if not rec or rec[:1] == b"*":
            continue
        cursor = 1
        row = {}
        for field in fields:
            raw = rec[cursor:cursor + field["length"]]
            cursor += field["length"]
            row[field["name"]] = raw.decode("latin1", errors="ignore").strip()
        samples.append(row)
    return {"record_count": num_records, "fields": fields, "samples": samples}


def shp_header(shp_bytes: bytes) -> dict:
    if len(shp_bytes) < 100:
        return {}
    file_code = struct.unpack(">i", shp_bytes[0:4])[0]
    file_length_words = struct.unpack(">i", shp_bytes[24:28])[0]
    version = struct.unpack("<i", shp_bytes[28:32])[0]
    shape_type = struct.unpack("<i", shp_bytes[32:36])[0]
    bbox = struct.unpack("<dddd", shp_bytes[36:68])
    return {
        "file_code": file_code,
        "file_length_bytes": file_length_words * 2,
        "version": version,
        "shape_type": shape_type,
        "bbox": bbox,
    }


def summarize_zip(path: Path, source_id: str) -> dict:
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        dbfs = [n for n in names if n.lower().endswith(".dbf")]
        shps = [n for n in names if n.lower().endswith(".shp")]
        dbf_infos = []
        for dbf in dbfs:
            info = dbf_schema_and_sample(z.read(dbf), sample_n=5)
            info["dbf"] = dbf
            dbf_infos.append(info)
            sample_path = SAMPLES / f"{source_id}_{Path(dbf).stem}_sample.csv"
            if info.get("samples"):
                with sample_path.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(info["samples"][0].keys()))
                    writer.writeheader()
                    writer.writerows(info["samples"])
        shp_infos = []
        for shp in shps:
            head = shp_header(z.read(shp)[:100])
            head["shp"] = shp
            shp_infos.append(head)
    first_dbf = dbf_infos[0] if dbf_infos else {}
    columns = "|".join(f["name"] for f in first_dbf.get("fields", []))
    return {
        "source_id": source_id,
        "path": safe_rel(path),
        "kind": "zip_shapefile_or_archive",
        "bytes": path.stat().st_size,
        "row_count": first_dbf.get("record_count"),
        "column_count": len(first_dbf.get("fields", [])),
        "columns": columns,
        "sample_path": safe_rel(SAMPLES),
        "notes": json.dumps({"members": names[:30], "dbf": dbf_infos, "shp": shp_infos}, default=str)[:12000],
    }


def summarize_json(path: Path, source_id: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and data.get("type") == "FeatureCollection":
        features = data.get("features", [])
        props = [f.get("properties", {}) for f in features[:1000]]
        fields = sorted({k for p in props for k in p.keys()})
        counts = {}
        for field in fields[:50]:
            counts[field] = sum(1 for p in props if p.get(field) not in (None, ""))
        sample_path = SAMPLES / f"{source_id}_properties_sample.csv"
        pd.DataFrame(props[:250]).to_csv(sample_path, index=False)
        return {
            "source_id": source_id,
            "path": safe_rel(path),
            "kind": "geojson",
            "bytes": path.stat().st_size,
            "row_count": len(features),
            "column_count": len(fields),
            "columns": "|".join(fields),
            "sample_path": safe_rel(sample_path),
            "notes": f"non_null_counts_in_first_1000={counts}",
        }
    if isinstance(data, dict) and "elements" in data:
        elements = data.get("elements", [])
        tag_keys = Counter()
        type_counts = Counter()
        rows = []
        for element in elements:
            type_counts[element.get("type")] += 1
            tags = element.get("tags") or {}
            tag_keys.update(tags.keys())
            rows.append({
                "id": element.get("id"),
                "type": element.get("type"),
                "lat": element.get("lat") or (element.get("center") or {}).get("lat"),
                "lon": element.get("lon") or (element.get("center") or {}).get("lon"),
                "name": tags.get("name"),
                "amenity": tags.get("amenity"),
                "shop": tags.get("shop"),
                "leisure": tags.get("leisure"),
                "public_transport": tags.get("public_transport"),
            })
        sample_path = SAMPLES / f"{source_id}_sample.csv"
        pd.DataFrame(rows[:1000]).to_csv(sample_path, index=False)
        return {
            "source_id": source_id,
            "path": safe_rel(path),
            "kind": "osm_overpass_json",
            "bytes": path.stat().st_size,
            "row_count": len(elements),
            "column_count": len(tag_keys),
            "columns": "|".join(k for k, _ in tag_keys.most_common(50)),
            "sample_path": safe_rel(sample_path),
            "notes": f"type_counts={dict(type_counts)}; top_tag_keys={tag_keys.most_common(20)}",
        }
    return {
        "source_id": source_id,
        "path": safe_rel(path),
        "kind": "json_metadata",
        "bytes": path.stat().st_size,
        "row_count": None,
        "column_count": None,
        "columns": "",
        "sample_path": "",
        "notes": f"top_level_keys={list(data.keys()) if isinstance(data, dict) else type(data).__name__}",
    }


def source_id_from_path(path: Path) -> str:
    return path.stem.replace(".", "_").replace("-", "_")


def inspect_files() -> list[dict]:
    summaries = []
    for path in sorted(list(RAW.rglob("*")) + list((ROOT / "data" / "metadata").rglob("*"))):
        if not path.is_file() or path.name.startswith("."):
            continue
        source_id = source_id_from_path(path)
        try:
            if path.suffix.lower() == ".zip":
                summaries.append(summarize_zip(path, source_id))
            elif path.suffix.lower() in [".csv", ".txt", ".tsv"]:
                summaries.append(summarize_tabular(path, source_id))
            elif path.suffix.lower() in [".json", ".geojson"]:
                summaries.append(summarize_json(path, source_id))
            else:
                summaries.append({
                    "source_id": source_id,
                    "path": safe_rel(path),
                    "kind": "other",
                    "bytes": path.stat().st_size,
                    "row_count": None,
                    "column_count": None,
                    "columns": "",
                    "sample_path": "",
                    "notes": "not inspected",
                })
        except Exception as exc:
            summaries.append({
                "source_id": source_id,
                "path": safe_rel(path),
                "kind": "inspection_failed",
                "bytes": path.stat().st_size,
                "row_count": None,
                "column_count": None,
                "columns": "",
                "sample_path": "",
                "notes": str(exc),
            })
    return summaries


def write_inventory(summaries: list[dict]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(summaries)
    df.to_csv(REPORTS / "dataset_inventory.csv", index=False)


def write_markdown(summaries: list[dict]) -> None:
    blocked_path = REPORTS / "blocked_or_deferred_sources.csv"
    blocked_rows = []
    if blocked_path.exists():
        blocked_rows = list(csv.DictReader(blocked_path.open(encoding="utf-8")))

    lines = []
    lines.append("# Project Lattice EDA Summary")
    lines.append("")
    lines.append("I used the files in `data/raw` and `data/metadata` to check what we can actually build on.")
    lines.append("")
    lines.append("## My Read")
    lines.append("")
    lines.append("- This repo is strong enough for data-source review and first-pass EDA.")
    lines.append("- Public/contextual layers are available: parcels, zoning/planning, schools, permits, Census boundaries, flood risk, wildfire risk, and OSM POIs.")
    lines.append("- The material gap remains comparable sales: no verified free bulk source is included.")
    lines.append("- Full spatial joins require GeoPandas, DuckDB Spatial, QGIS, or PostGIS; this EDA inspects schemas, record counts, fields, and samples.")
    lines.append("")
    lines.append("## Downloaded Dataset Inventory")
    lines.append("")
    lines.append("| Dataset | Kind | Rows/features | Columns | Size MB | Sample |")
    lines.append("| --- | --- | ---: | ---: | ---: | --- |")
    for s in summaries:
        size_mb = (s.get("bytes") or 0) / (1024 * 1024)
        rows = s.get("row_count")
        rows_text = "" if rows is None or (isinstance(rows, float) and math.isnan(rows)) else str(rows)
        sample = s.get("sample_path") or ""
        lines.append(f"| `{s['path']}` | {s['kind']} | {rows_text} | {s.get('column_count') or ''} | {size_mb:.2f} | `{sample}` |")
    lines.append("")
    lines.append("## Blocked Or Deferred Sources")
    lines.append("")
    if blocked_rows:
        lines.append("| Source | Status | Reason | Next step |")
        lines.append("| --- | --- | --- | --- |")
        for row in blocked_rows:
            lines.append(f"| `{row['source_id']}` | {row['status']} | {row['reason']} | {row['next_step']} |")
    else:
        lines.append("No blocked/deferred source file found.")
    lines.append("")
    lines.append("## EDA Takeaways")
    lines.append("")
    lines.append("1. **San Ramon/Contra Costa story path is feasible for the graph base.** Contra Costa publishes parcel, zoning, land-use, city-limit, and urban-limit-line shapefiles.")
    lines.append("2. **Risk layers are real and source-backed.** FEMA NFHL and CAL FIRE FHSZ services are queryable; this repo includes Contra Costa bbox extracts.")
    lines.append("3. **School metadata is downloadable.** CDE public school/district files are included, but school-quality scoring should be derived carefully from public performance data rather than proprietary ratings.")
    lines.append("4. **SF is still the easier data-first demo.** The SF permit extract has over one million records and good structured fields; in this repository it is stored as selected-column split CSV parts.")
    lines.append("5. **Comparable sales is still the critical path.** Without sale price/date/property attributes, Lattice can explain context and risk but cannot honestly claim production-grade valuation.")
    lines.append("")
    lines.append("## What I Would Do Next")
    lines.append("")
    lines.append("1. Install geospatial tooling: `pip install geopandas pyogrio shapely duckdb duckdb-engine` or use QGIS/PostGIS.")
    lines.append("2. Read Contra Costa parcels and city limits, filter parcels to San Ramon, and compute parcel count plus address/APN completeness.")
    lines.append("3. Spatially join San Ramon parcels to zoning, land-use, FEMA flood zones, CAL FIRE FHSZ, OSM POIs, schools, and Census tracts.")
    lines.append("4. Build a `property_features` table with one row per parcel or candidate listing.")
    lines.append("5. Separately validate comparable-sales acquisition before building a valuation model.")
    (REPORTS / "eda_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    SAMPLES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    summaries = inspect_files()
    write_inventory(summaries)
    write_markdown(summaries)
    print(f"Wrote {REPORTS / 'dataset_inventory.csv'}")
    print(f"Wrote {REPORTS / 'eda_summary.md'}")


if __name__ == "__main__":
    main()
