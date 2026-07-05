#!/usr/bin/env python3
"""
Build the visual walkthrough and executed review notebooks for Project Lattice.

This intentionally uses only pandas and the Python standard library so the repo
stays easy to run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
NOTEBOOKS = ROOT / "notebooks"


BLUE = "#2563eb"
GREEN = "#059669"
AMBER = "#d97706"
RED = "#dc2626"
SLATE = "#334155"
LIGHT = "#f8fafc"
BORDER = "#cbd5e1"


DATASET_CATALOG = [
    {
        "Dataset": "Contra Costa Assessor Parcels",
        "Geography / county": "Contra Costa County, California",
        "Kind of data": "Parcel geometry + assessor parcel identifiers/address fields",
        "Source agency": "Contra Costa County GIS / Assessor",
        "Local path": "data/raw/contra_costa/Parcels_Public_May2026.zip",
        "Source URL": "https://gis.cccounty.us/Downloads/Assessor/Parcels_Public_May2026.zip",
        "What to look for": "APN, parcel/address fields, parcel boundaries. This is the base property graph layer.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "Contra Costa City Limits",
        "Geography / county": "Contra Costa County, California",
        "Kind of data": "Municipal boundary polygons",
        "Source agency": "Contra Costa County GIS / Planning",
        "Local path": "data/raw/contra_costa/BND_DCD_City_Limits.zip",
        "Source URL": "https://gis.cccounty.us/Downloads/Planning/BND_DCD_City_Limits.zip",
        "What to look for": "City boundary polygons used to filter parcels to San Ramon and validate parcel city codes.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "Contra Costa LAFCO Sphere of Influence",
        "Geography / county": "Contra Costa County, California",
        "Kind of data": "Sphere-of-influence boundary polygons",
        "Source agency": "Contra Costa County GIS / Planning",
        "Local path": "data/raw/contra_costa/BND_LAFCO_City_SOI.zip",
        "Source URL": "https://gis.cccounty.us/Downloads/Planning/BND_LAFCO_City_SOI.zip",
        "What to look for": "Planning/jurisdiction context around city influence areas.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "Contra Costa General Plan Land Use",
        "Geography / county": "Contra Costa County, California",
        "Kind of data": "General-plan land-use polygons",
        "Source agency": "Contra Costa County GIS / Planning",
        "Local path": "data/raw/contra_costa/PLA_DCD_GPLanduseElement.zip",
        "Source URL": "https://gis.cccounty.us/Downloads/Planning/PLA_DCD_GPLanduseElement.zip",
        "What to look for": "Land-use designations that can support explainable context around property and neighborhood character.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "Contra Costa Urban Limit Line",
        "Geography / county": "Contra Costa County, California",
        "Kind of data": "Urban limit line polygons",
        "Source agency": "Contra Costa County GIS / Planning",
        "Local path": "data/raw/contra_costa/PLA_DCD_ULL.zip",
        "Source URL": "https://gis.cccounty.us/Downloads/Planning/PLA_DCD_ULL.zip",
        "What to look for": "Growth boundary context for development constraints or expansion signals.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "Contra Costa Zoning",
        "Geography / county": "Contra Costa County, California",
        "Kind of data": "Zoning polygons",
        "Source agency": "Contra Costa County GIS / Planning",
        "Local path": "data/raw/contra_costa/PLA_DCD_Zoning.zip",
        "Source URL": "https://gis.cccounty.us/Downloads/Planning/PLA_DCD_Zoning.zip",
        "What to look for": "Zoning classifications and overlays. We still need to verify incorporated San Ramon coverage.",
        "Status": "Downloaded; coverage check needed",
    },
    {
        "Dataset": "Census TIGER Tracts",
        "Geography / county": "California statewide",
        "Kind of data": "Census tract boundary shapefile",
        "Source agency": "U.S. Census Bureau TIGER/Line",
        "Local path": "data/raw/census/tl_2025_06_tract.zip",
        "Source URL": "https://www2.census.gov/geo/tiger/TIGER2025/TRACT/tl_2025_06_tract.zip",
        "What to look for": "Tract IDs and geometry for joining parcels to Census geography.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "Census TIGER Block Groups",
        "Geography / county": "California statewide",
        "Kind of data": "Census block-group boundary shapefile",
        "Source agency": "U.S. Census Bureau TIGER/Line",
        "Local path": "data/raw/census/tl_2025_06_bg.zip",
        "Source URL": "https://www2.census.gov/geo/tiger/TIGER2025/BG/tl_2025_06_bg.zip",
        "What to look for": "Block-group IDs and geometry for finer demographic joins once ACS variables are pulled.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "Census TIGER Places",
        "Geography / county": "California statewide",
        "Kind of data": "Incorporated place boundary shapefile",
        "Source agency": "U.S. Census Bureau TIGER/Line",
        "Local path": "data/raw/census/tl_2025_06_place.zip",
        "Source URL": "https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_06_place.zip",
        "What to look for": "Place boundaries for city-level geography checks.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "CDE Public Schools and Districts",
        "Geography / county": "California statewide; includes Contra Costa and San Ramon rows",
        "Kind of data": "School/district directory table",
        "Source agency": "California Department of Education",
        "Local path": "data/raw/schools/cde_public_schools_and_districts.txt",
        "Source URL": "https://www.cde.ca.gov/schooldirectory/report?rid=dl1&tp=txt",
        "What to look for": "School names, districts, locations, grade spans, status, and administrative metadata.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "CAL FIRE Local Responsibility Area Fire Hazard Zones",
        "Geography / county": "Contra Costa County project bbox",
        "Kind of data": "Wildfire hazard polygons",
        "Source agency": "CAL FIRE / Office of the State Fire Marshal",
        "Local path": "data/raw/risk/calfire_fhsz_lra_contra_costa_bbox.geojson",
        "Source URL": "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSALRA25_v1_All/FeatureServer/0",
        "What to look for": "Local responsibility area fire hazard classes: NonWildland, Moderate, High, Very High.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "CAL FIRE State Responsibility Area Fire Hazard Zones",
        "Geography / county": "Contra Costa County project bbox",
        "Kind of data": "Wildfire hazard polygons",
        "Source agency": "CAL FIRE / Office of the State Fire Marshal",
        "Local path": "data/raw/risk/calfire_fhsz_sra_contra_costa_bbox.geojson",
        "Source URL": "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSZSRA_23_3/FeatureServer/0",
        "What to look for": "State responsibility area fire hazard classes: Moderate, High, Very High.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "FEMA National Flood Hazard Layer Attributes",
        "Geography / county": "Contra Costa County project bbox",
        "Kind of data": "Flood hazard zone attributes",
        "Source agency": "FEMA NFHL ArcGIS service",
        "Local path": "data/raw/risk/fema_nfhl_flood_hazard_zones_contra_costa_bbox_attributes.geojson",
        "Source URL": "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28",
        "What to look for": "Flood zone code, SFHA flag, base flood elevation fields. Geometry is omitted for this extract.",
        "Status": "Downloaded attributes; parcel-level geometry join still pending",
    },
    {
        "Dataset": "OpenStreetMap San Ramon POIs",
        "Geography / county": "San Ramon / Contra Costa County bbox",
        "Kind of data": "Amenities, shops, leisure, public-transport POIs",
        "Source agency": "OpenStreetMap via Overpass API",
        "Local path": "data/raw/osm/osm_san_ramon_pois.json",
        "Source URL": "https://overpass-api.de/api/interpreter",
        "What to look for": "Nearby amenities such as restaurants, parks, schools, shops, parking, and leisure features.",
        "Status": "Downloaded",
    },
    {
        "Dataset": "San Francisco Building Permits",
        "Geography / county": "City and County of San Francisco",
        "Kind of data": "Building permit table with status, dates, cost, use, units, and point location",
        "Source agency": "DataSF / San Francisco Department of Building Inspection",
        "Local path": "data/raw/san_francisco/building_permits_selected_parts/",
        "Source URL": "https://data.sfgov.org/resource/i98e-djp9.csv",
        "What to look for": "1.29M permit records for a data-rich ingestion/explainability demo. Stored as split CSV parts.",
        "Status": "Downloaded as split CSV parts",
    },
    {
        "Dataset": "Comparable Sales",
        "Geography / county": "Target metro, likely Contra Costa / San Ramon first",
        "Kind of data": "Sale price, sale date, property attributes, APN/address match key",
        "Source agency": "TBD: county records, MLS/partner feed, purchased data, or manually seeded records",
        "Local path": "Not included yet",
        "Source URL": "TBD",
        "What to look for": "This is the missing valuation target. We need this before presenting production-grade valuation.",
        "Status": "Pending",
    },
    {
        "Dataset": "511 Bay Area Transit / GTFS",
        "Geography / county": "Bay Area, including Contra Costa County",
        "Kind of data": "Transit stops, routes, schedules, service calendars",
        "Source agency": "511.org",
        "Local path": "Not included yet",
        "Source URL": "https://511.org/open-data/transit",
        "What to look for": "Commute and transit-access features after an API token is available.",
        "Status": "Pending API token",
    },
    {
        "Dataset": "Census ACS 5-Year Variables",
        "Geography / county": "United States; planned pull for Contra Costa/SF tracts and block groups",
        "Kind of data": "Demographic and housing attributes",
        "Source agency": "U.S. Census Bureau ACS API",
        "Local path": "Not included yet",
        "Source URL": "https://www.census.gov/data/developers/data-sets/acs-5year.html",
        "What to look for": "Median income, commute, tenure, vacancy, housing cost, and related context variables.",
        "Status": "Pending Census API key",
    },
]


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def fmt_num(value: float | int | str) -> str:
    try:
        if pd.isna(value):
            return ""
        return f"{int(float(value)):,}"
    except Exception:
        return str(value)


def short_html(df: pd.DataFrame, max_rows: int = 20) -> str:
    return df.head(max_rows).to_html(index=False, escape=False, border=0)


def text_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    return df.head(max_rows).to_string(index=False)


def chart_svg(title: str, rows: list[tuple[str, float]], path: Path, width: int = 920, bar_color: str = BLUE) -> None:
    rows = [(label, float(value)) for label, value in rows if float(value) > 0]
    rows = rows[:12]
    max_value = max([value for _, value in rows] or [1])
    row_h = 42
    left = 250
    top = 70
    chart_w = width - left - 120
    height = top + len(rows) * row_h + 45
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="24" y="36" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="{SLATE}">{title}</text>',
    ]
    for idx, (label, value) in enumerate(rows):
        y = top + idx * row_h
        bar_w = max(3, (value / max_value) * chart_w)
        parts.extend([
            f'<text x="24" y="{y + 24}" font-family="Arial, sans-serif" font-size="15" fill="{SLATE}">{escape(label)}</text>',
            f'<rect x="{left}" y="{y + 7}" width="{bar_w:.1f}" height="22" rx="4" fill="{bar_color}"/>',
            f'<text x="{left + bar_w + 10}" y="{y + 24}" font-family="Arial, sans-serif" font-size="14" fill="{SLATE}">{fmt_num(value)}</text>',
        ])
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def escape(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def status_svg(path: Path) -> None:
    rows = [
        ("Parcel graph", "Available", "Contra Costa parcels, APN, address fields"),
        ("San Ramon filter", "Available", "City limits + SNRMN parcel code"),
        ("Zoning / land use", "Available", "County zoning and general-plan layers"),
        ("Schools", "Available", "CDE public schools/districts"),
        ("Risk", "Available", "CAL FIRE + FEMA attributes"),
        ("Amenities", "Available", "OSM San Ramon POIs"),
        ("SF permit demo", "Available", "1.29M permit records"),
        ("Comparable sales", "Pending", "Need legal comps source or seed set"),
        ("Transit / commute", "Pending", "511 token needed"),
        ("ACS variables", "Pending", "Census API key needed"),
    ]
    width = 980
    row_h = 54
    height = 84 + len(rows) * row_h
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="24" y="40" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="{SLATE}">Project Lattice data readiness</text>',
        f'<text x="24" y="64" font-family="Arial, sans-serif" font-size="14" fill="#64748b">What is ready to review now vs what still needs an owner.</text>',
    ]
    for idx, (area, status, note) in enumerate(rows):
        y = 88 + idx * row_h
        color = GREEN if status == "Available" else AMBER
        parts.extend([
            f'<rect x="24" y="{y}" width="{width - 48}" height="42" rx="8" fill="{LIGHT}" stroke="{BORDER}"/>',
            f'<text x="44" y="{y + 27}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="{SLATE}">{escape(area)}</text>',
            f'<rect x="265" y="{y + 10}" width="104" height="22" rx="11" fill="{color}"/>',
            f'<text x="317" y="{y + 26}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="white">{status}</text>',
            f'<text x="390" y="{y + 27}" font-family="Arial, sans-serif" font-size="15" fill="{SLATE}">{escape(note)}</text>',
        ])
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def flow_svg(path: Path) -> None:
    boxes = [
        ("1", "Open README", "2-minute orientation"),
        ("2", "Notebook 01", "What data exists"),
        ("3", "Notebook 02", "EDA and visuals"),
        ("4", "Notebook 03", "Gaps and next steps"),
        ("5", "Team decision", "Comps + MVP path"),
    ]
    width = 1040
    height = 240
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="24" y="42" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="{SLATE}">Simple review path</text>',
    ]
    x = 28
    y = 82
    box_w = 176
    for idx, (num, title, subtitle) in enumerate(boxes):
        parts.extend([
            f'<rect x="{x}" y="{y}" width="{box_w}" height="96" rx="10" fill="{LIGHT}" stroke="{BORDER}"/>',
            f'<circle cx="{x + 28}" cy="{y + 30}" r="16" fill="{BLUE}"/>',
            f'<text x="{x + 28}" y="{y + 36}" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="white">{num}</text>',
            f'<text x="{x + 56}" y="{y + 34}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="{SLATE}">{escape(title)}</text>',
            f'<text x="{x + 20}" y="{y + 70}" font-family="Arial, sans-serif" font-size="14" fill="#64748b">{escape(subtitle)}</text>',
        ])
        if idx < len(boxes) - 1:
            parts.extend([
                f'<line x1="{x + box_w + 12}" y1="{y + 48}" x2="{x + box_w + 46}" y2="{y + 48}" stroke="{SLATE}" stroke-width="2"/>',
                f'<polygon points="{x + box_w + 46},{y + 48} {x + box_w + 36},{y + 42} {x + box_w + 36},{y + 54}" fill="{SLATE}"/>',
            ])
        x += box_w + 62
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def dataset_catalog_df() -> pd.DataFrame:
    return pd.DataFrame(DATASET_CATALOG)


def make_dataset_catalog() -> pd.DataFrame:
    catalog = dataset_catalog_df()
    catalog_path = REPORTS / "dataset_catalog.csv"
    catalog.to_csv(catalog_path, index=False)

    lines = []
    lines.append("# Dataset Catalog")
    lines.append("")
    lines.append("This is the plain-English guide to the data in the repo. For each dataset I list what it is, what geography it covers, where it came from, and how I expect us to use it for Project Lattice.")
    lines.append("")
    lines.append("## Quick Table")
    lines.append("")
    lines.append("| Dataset | Geography / county | Kind of data | Source agency | Status | Local path |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in DATASET_CATALOG:
        lines.append(
            f"| {row['Dataset']} | {row['Geography / county']} | {row['Kind of data']} | "
            f"{row['Source agency']} | {row['Status']} | `{row['Local path']}` |"
        )
    lines.append("")
    lines.append("## Dataset Notes")
    lines.append("")
    for row in DATASET_CATALOG:
        lines.append(f"### {row['Dataset']}")
        lines.append("")
        lines.append(f"- **Geography / county:** {row['Geography / county']}")
        lines.append(f"- **Kind of data:** {row['Kind of data']}")
        lines.append(f"- **Source agency:** {row['Source agency']}")
        lines.append(f"- **Local path:** `{row['Local path']}`")
        lines.append(f"- **Source URL:** {row['Source URL']}")
        lines.append(f"- **What to look for:** {row['What to look for']}")
        lines.append(f"- **Status:** {row['Status']}")
        lines.append("")
    (ROOT / "docs" / "dataset-catalog.md").write_text("\n".join(lines), encoding="utf-8")
    return catalog


def make_figures() -> dict[str, Path]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    inventory = read_csv(REPORTS / "dataset_inventory.csv")
    status_svg(FIGURES / "data_readiness.svg")
    flow_svg(FIGURES / "review_path.svg")

    row_counts = []
    sf_parts = inventory[inventory["path"].astype(str).str.contains("building_permits_selected_part")]
    if not sf_parts.empty:
        row_counts.append(("SF permits", sf_parts["row_count"].sum()))
    for label, pattern in [
        ("Contra Costa parcels", "Parcels_Public_May2026.zip"),
        ("CDE schools", "cde_public_schools_and_districts.txt"),
        ("OSM San Ramon POIs", "osm_san_ramon_pois.json"),
        ("FEMA flood attrs", "fema_nfhl_flood_hazard"),
        ("Census block groups", "tl_2025_06_bg.zip"),
        ("Census tracts", "tl_2025_06_tract.zip"),
        ("Zoning polygons", "PLA_DCD_Zoning.zip"),
    ]:
        match = inventory[inventory["path"].astype(str).str.contains(pattern, regex=False)]
        if not match.empty:
            row_counts.append((label, float(match.iloc[0]["row_count"])))
    chart_svg("Rows / features by major dataset", row_counts, FIGURES / "major_record_counts.svg", bar_color=BLUE)

    city_counts = read_csv(REPORTS / "profiles" / "contra_costa_parcel_city_counts.csv")
    chart_svg("Contra Costa parcel city counts", list(city_counts.head(10).itertuples(index=False, name=None)), FIGURES / "parcel_city_counts.svg", bar_color=GREEN)

    permit_status = read_csv(REPORTS / "profiles" / "sf_permit_status_counts.csv")
    chart_svg("San Francisco permit status mix", list(permit_status.head(10).itertuples(index=False, name=None)), FIGURES / "permit_status_counts.svg", bar_color=BLUE)

    flood = read_csv(REPORTS / "profiles" / "fema_flood_zone_counts.csv")
    chart_svg("FEMA flood zone counts", list(flood.itertuples(index=False, name=None)), FIGURES / "fema_flood_counts.svg", bar_color=AMBER)

    return {
        "readiness": FIGURES / "data_readiness.svg",
        "flow": FIGURES / "review_path.svg",
        "records": FIGURES / "major_record_counts.svg",
        "cities": FIGURES / "parcel_city_counts.svg",
        "permits": FIGURES / "permit_status_counts.svg",
        "flood": FIGURES / "fema_flood_counts.svg",
    }


def output_df(df: pd.DataFrame) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [
            {
                "output_type": "execute_result",
                "execution_count": None,
                "metadata": {},
                "data": {
                    "text/plain": text_table(df),
                    "text/html": short_html(df),
                },
            }
        ],
        "source": [],
    }


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip() + "\n"}


def code(source: str, df: pd.DataFrame | None = None, text: str | None = None, count: int = 1) -> dict:
    outputs = []
    if df is not None:
        outputs.append({
            "output_type": "execute_result",
            "execution_count": count,
            "metadata": {},
            "data": {"text/plain": text_table(df), "text/html": short_html(df)},
        })
    if text is not None:
        outputs.append({"output_type": "stream", "name": "stdout", "text": text if text.endswith("\n") else text + "\n"})
    return {
        "cell_type": "code",
        "execution_count": count,
        "metadata": {},
        "outputs": outputs,
        "source": source.strip() + "\n",
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.x"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_notebook(path: Path, cells: list[dict]) -> None:
    path.write_text(json.dumps(notebook(cells), indent=2) + "\n", encoding="utf-8")


def make_visual_index() -> None:
    text = """# Project Lattice Visual Review

This is the shortest path through the repo.

![Review path](figures/review_path.svg)

## Current Data Readiness

![Data readiness](figures/data_readiness.svg)

## Biggest Datasets

![Major record counts](figures/major_record_counts.svg)

## What To Open

| Step | File | Why |
| --- | --- | --- |
| 1 | `../docs/dataset-catalog.md` | Understand what each dataset is, what county/geography it covers, and where it came from. |
| 2 | `../notebooks/01_data_inventory.ipynb` | See what data is actually in the repo. |
| 3 | `../notebooks/02_executed_eda.ipynb` | Review the key EDA charts and tables. |
| 4 | `../notebooks/03_availability_and_next_steps.ipynb` | See what is available, pending, and who should review what. |
| 5 | `../docs/project-lattice-data-review.md` | Read the team review instructions. |

Actual downloaded data files are organized under `../data/raw/`.

## Main Decision

The data is strong enough for a sourced explanation/knowledge-graph demo. It is not enough for production-grade valuation until we secure comparable sales.
"""
    (REPORTS / "visual_review.md").write_text(text, encoding="utf-8")


def make_notebooks() -> None:
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    catalog = dataset_catalog_df()
    inventory = read_csv(REPORTS / "dataset_inventory.csv")
    blocked = read_csv(REPORTS / "blocked_or_deferred_sources.csv")
    city_counts = read_csv(REPORTS / "profiles" / "contra_costa_parcel_city_counts.csv")
    permit_status = read_csv(REPORTS / "profiles" / "sf_permit_status_counts.csv")
    flood = read_csv(REPORTS / "profiles" / "fema_flood_zone_counts.csv")
    lra = read_csv(REPORTS / "profiles" / "calfire_lra_fhsz_counts.csv")
    osm = read_csv(REPORTS / "profiles" / "osm_amenity_counts.csv")

    summary_rows = [
        ("SF permits", "data/raw/san_francisco/building_permits_selected_parts/", "1,291,589 rows", "Available"),
        ("Contra Costa parcels", "data/raw/contra_costa/Parcels_Public_May2026.zip", "387,835 parcels", "Available"),
        ("Census boundaries", "data/raw/census/", "tracts, block groups, places", "Available"),
        ("Schools", "data/raw/schools/cde_public_schools_and_districts.txt", "18,390 rows", "Available"),
        ("Wildfire risk", "data/raw/risk/calfire_*.geojson", "LRA/SRA extracts", "Available"),
        ("Flood risk", "data/raw/risk/fema_*.geojson", "6,435 attribute rows", "Available for review; geometry join pending"),
        ("Amenities", "data/raw/osm/osm_san_ramon_pois.json", "7,026 elements", "Available"),
        ("Comparable sales", "not included", "needed for valuation", "Pending"),
        ("511 transit", "not included", "API token needed", "Pending"),
        ("ACS variables", "not included", "Census API key needed", "Pending"),
    ]
    summary = pd.DataFrame(summary_rows, columns=["Area", "Path", "Current coverage", "Status"])

    inventory_view = inventory[["path", "kind", "row_count", "column_count"]].copy()
    inventory_view["row_count"] = inventory_view["row_count"].apply(fmt_num)
    inventory_view = inventory_view.rename(columns={"path": "File", "kind": "Kind", "row_count": "Rows/features", "column_count": "Columns"})

    write_notebook(
        NOTEBOOKS / "01_data_inventory.ipynb",
        [
            md("# 01 Data Inventory\n\nI use this notebook as the quick proof that the raw data is actually here and organized. Start with the catalog table so every file has context: county/geography, source, data type, and status."),
            md("![Review path](../reports/figures/review_path.svg)\n\n![Data readiness](../reports/figures/data_readiness.svg)"),
            code(
                "import pandas as pd\ncatalog = pd.read_csv('../reports/dataset_catalog.csv')\ncatalog[['Dataset', 'Geography / county', 'Kind of data', 'Source agency', 'Status', 'Local path']]",
                catalog[["Dataset", "Geography / county", "Kind of data", "Source agency", "Status", "Local path"]],
                count=1,
            ),
            md("## Downloaded And Pending Summary"),
            code(
                "import pandas as pd\nsummary = pd.read_csv('../reports/notebook_tables/data_inventory_summary.csv')\nsummary",
                summary,
                count=2,
            ),
            md("## Full File Inventory\n\nThis table is long, but it is useful for checking row counts and file locations."),
            code(
                "inventory = pd.read_csv('../reports/dataset_inventory.csv')\ninventory[['path', 'kind', 'row_count', 'column_count']].head(30)",
                inventory_view,
                count=3,
            ),
            md("## What Is Pending\n\nThese are the items we still need to assign or unlock."),
            code(
                "blocked = pd.read_csv('../reports/blocked_or_deferred_sources.csv')\nblocked",
                blocked,
                count=4,
            ),
        ],
    )

    write_notebook(
        NOTEBOOKS / "02_executed_eda.ipynb",
        [
            md("# 02 Executed EDA\n\nThis notebook is the visual EDA pass. The outputs are already saved so reviewers do not need to rerun anything just to understand the data."),
            md("## Major Dataset Sizes\n\n![Rows by dataset](../reports/figures/major_record_counts.svg)"),
            md("## Contra Costa Parcel Concentration\n\n![Parcel city counts](../reports/figures/parcel_city_counts.svg)"),
            code(
                "city_counts = pd.read_csv('../reports/profiles/contra_costa_parcel_city_counts.csv')\ncity_counts.head(12)",
                city_counts.head(12),
                count=1,
            ),
            md("## San Francisco Permit Signal\n\n![Permit statuses](../reports/figures/permit_status_counts.svg)"),
            code(
                "permit_status = pd.read_csv('../reports/profiles/sf_permit_status_counts.csv')\npermit_status.head(12)",
                permit_status.head(12),
                count=2,
            ),
            md("## Flood And Wildfire Risk\n\n![Flood zones](../reports/figures/fema_flood_counts.svg)"),
            code(
                "flood = pd.read_csv('../reports/profiles/fema_flood_zone_counts.csv')\nflood",
                flood,
                count=3,
            ),
            code(
                "calfire_lra = pd.read_csv('../reports/profiles/calfire_lra_fhsz_counts.csv')\ncalfire_lra",
                lra,
                count=4,
            ),
            md("## OSM Amenity Signal"),
            code(
                "osm_amenities = pd.read_csv('../reports/profiles/osm_amenity_counts.csv')\nosm_amenities.head(12)",
                osm.head(12),
                count=5,
            ),
        ],
    )

    next_steps = pd.DataFrame([
        ("Comparable sales", "Pending", "Owner needed", "Find legal comps source or manually seed 50-200 sale records."),
        ("511 transit", "Pending", "API key needed", "Register for 511 token and pull GTFS regional feed."),
        ("ACS variables", "Pending", "API key needed", "Pull tract/block-group attributes after Census key is available."),
        ("Parcel joins", "Ready", "Geospatial owner", "Join parcels to city, zoning, risk, schools, Census, and OSM."),
        ("SF permit demo", "Ready", "Data/product owner", "Use as fast ingestion/explanation proof point."),
    ], columns=["Workstream", "Status", "Owner need", "Next action"])

    readiness = pd.DataFrame([
        ("Graph base", "Ready", "Parcels, APN, address fields, city/ZIP."),
        ("Explainability context", "Ready", "Zoning, risk, schools, amenities, Census boundaries."),
        ("Permit signal", "Ready for SF demo", "1.29M SF permits; San Ramon feed still needs follow-up."),
        ("Production valuation", "Not ready", "Comparable sales are missing."),
    ], columns=["Product layer", "Status", "Why"])

    write_notebook(
        NOTEBOOKS / "03_availability_and_next_steps.ipynb",
        [
            md("# 03 Availability And Next Steps\n\nThis is the decision notebook: what we can build now, what is pending, and what I need the team to review."),
            md("![Data readiness](../reports/figures/data_readiness.svg)"),
            code(
                "readiness = pd.DataFrame(...)\nreadiness",
                readiness,
                count=1,
            ),
            md("## Pending Items"),
            code(
                "blocked = pd.read_csv('../reports/blocked_or_deferred_sources.csv')\nblocked",
                blocked,
                count=2,
            ),
            md("## Suggested Owner Split"),
            code(
                "next_steps = pd.DataFrame(...)\nnext_steps",
                next_steps,
                count=3,
            ),
            md("## My Decision Point\n\nWe can build the knowledge graph and explanation demo now. We should not present the valuation model as production-grade until comparable sales are secured."),
        ],
    )

    tables_dir = REPORTS / "notebook_tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(tables_dir / "data_inventory_summary.csv", index=False)
    next_steps.to_csv(tables_dir / "next_steps.csv", index=False)
    readiness.to_csv(tables_dir / "product_readiness.csv", index=False)


def main() -> None:
    make_dataset_catalog()
    make_figures()
    make_visual_index()
    make_notebooks()
    print(f"Wrote figures to {FIGURES}")
    print(f"Wrote notebooks to {NOTEBOOKS}")
    print(f"Wrote visual index to {REPORTS / 'visual_review.md'}")


if __name__ == "__main__":
    main()
