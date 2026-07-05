#!/usr/bin/env python3
"""
Build a presentation-style location snapshot for Contra Costa County.

This script uses only the Python standard library. It reads Census shapefiles
directly from the zipped source files and writes an SVG that GitHub can render.
"""

from __future__ import annotations

import html
import math
import struct
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
COUNTY_ZIP = ROOT / "data" / "raw" / "census" / "cb_2025_us_county_500k.zip"
PLACE_ZIP = ROOT / "data" / "raw" / "census" / "tl_2025_06_place.zip"
OUTPUT = ROOT / "reports" / "figures" / "contra_costa_location_snapshot.svg"


OCEAN = "#d9eef7"
LAND = "#eef6ef"
BAY_LAND = "#dff1e7"
BAY_HIGHLIGHT = "#dbeafe"
COUNTY = "#f97316"
COUNTY_DARK = "#9a3412"
SAN_RAMON = "#2563eb"
INK = "#1f2937"
MUTED = "#64748b"
CARD = "#ffffff"
BORDER = "#cbd5e1"
GREEN = "#059669"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def zip_read(zip_path: Path, suffix: str) -> bytes:
    with ZipFile(zip_path) as zf:
        name = next(name for name in zf.namelist() if name.lower().endswith(suffix))
        return zf.read(name)


def dbf_records(zip_path: Path) -> list[dict[str, str]]:
    data = zip_read(zip_path, ".dbf")
    record_count = int.from_bytes(data[4:8], "little")
    header_len = struct.unpack("<H", data[8:10])[0]
    record_len = struct.unpack("<H", data[10:12])[0]

    fields = []
    pos = 32
    while pos + 32 <= header_len and data[pos] != 0x0D:
        raw_name = data[pos:pos + 11].split(b"\x00", 1)[0]
        fields.append({
            "name": raw_name.decode("latin1", errors="ignore").strip(),
            "length": data[pos + 16],
        })
        pos += 32

    rows: list[dict[str, str]] = []
    offset = header_len
    for _ in range(record_count):
        rec = data[offset:offset + record_len]
        offset += record_len
        if not rec or rec[:1] == b"*":
            continue
        cursor = 1
        row: dict[str, str] = {}
        for field in fields:
            raw = rec[cursor:cursor + field["length"]]
            cursor += field["length"]
            row[field["name"]] = raw.decode("latin1", errors="ignore").strip()
        rows.append(row)
    return rows


def shp_shapes(zip_path: Path) -> list[list[list[tuple[float, float]]]]:
    data = zip_read(zip_path, ".shp")
    shapes: list[list[list[tuple[float, float]]]] = []
    pos = 100
    while pos + 8 <= len(data):
        _record_number, content_words = struct.unpack(">ii", data[pos:pos + 8])
        pos += 8
        content = data[pos:pos + content_words * 2]
        pos += content_words * 2
        if len(content) < 4:
            shapes.append([])
            continue
        shape_type = struct.unpack("<i", content[:4])[0]
        if shape_type == 0:
            shapes.append([])
            continue
        if shape_type not in {5, 15, 25, 31}:
            raise ValueError(f"Unsupported shape type {shape_type} in {zip_path}")

        part_count, point_count = struct.unpack("<ii", content[36:44])
        parts_start = 44
        points_start = parts_start + part_count * 4
        part_indexes = list(struct.unpack(f"<{part_count}i", content[parts_start:points_start]))
        points = [
            struct.unpack("<dd", content[points_start + idx * 16:points_start + (idx + 1) * 16])
            for idx in range(point_count)
        ]

        rings: list[list[tuple[float, float]]] = []
        for idx, start in enumerate(part_indexes):
            end = part_indexes[idx + 1] if idx + 1 < len(part_indexes) else point_count
            ring = points[start:end]
            if len(ring) >= 3:
                rings.append(ring)
        shapes.append(rings)
    return shapes


def load_features(zip_path: Path) -> list[dict]:
    rows = dbf_records(zip_path)
    shapes = shp_shapes(zip_path)
    if len(rows) != len(shapes):
        raise ValueError(f"DBF/SHP record mismatch for {zip_path}: {len(rows)} vs {len(shapes)}")
    return [{"properties": row, "rings": rings} for row, rings in zip(rows, shapes)]


def feature_bbox(feature: dict) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for ring in feature["rings"]:
        for x, y in ring:
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def bounds(features: list[dict]) -> tuple[float, float, float, float]:
    boxes = [feature_bbox(feature) for feature in features if feature["rings"]]
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def pad_bounds(box: tuple[float, float, float, float], pad_ratio: float) -> tuple[float, float, float, float]:
    min_x, min_y, max_x, max_y = box
    dx = max_x - min_x
    dy = max_y - min_y
    return (
        min_x - dx * pad_ratio,
        min_y - dy * pad_ratio,
        max_x + dx * pad_ratio,
        max_y + dy * pad_ratio,
    )


def mercator(lon: float, lat: float) -> tuple[float, float]:
    lat = max(min(lat, 89.0), -89.0)
    rad = math.radians(lat)
    return math.radians(lon), math.log(math.tan(math.pi / 4 + rad / 2))


def mapper(
    lonlat_bounds: tuple[float, float, float, float],
    x: float,
    y: float,
    width: float,
    height: float,
):
    min_lon, min_lat, max_lon, max_lat = lonlat_bounds
    px1, py1 = mercator(min_lon, min_lat)
    px2, py2 = mercator(max_lon, max_lat)
    min_px, max_px = min(px1, px2), max(px1, px2)
    min_py, max_py = min(py1, py2), max(py1, py2)
    scale = min(width / (max_px - min_px), height / (max_py - min_py))
    draw_w = (max_px - min_px) * scale
    draw_h = (max_py - min_py) * scale
    x_pad = x + (width - draw_w) / 2
    y_pad = y + (height - draw_h) / 2

    def project(lon: float, lat: float) -> tuple[float, float]:
        px, py = mercator(lon, lat)
        sx = x_pad + (px - min_px) * scale
        sy = y_pad + draw_h - (py - min_py) * scale
        return sx, sy

    return project


def simplify(points: list[tuple[float, float]], min_dist: float) -> list[tuple[float, float]]:
    if len(points) <= 3:
        return points
    kept = [points[0]]
    last_x, last_y = points[0]
    for x, y in points[1:-1]:
        if abs(x - last_x) + abs(y - last_y) >= min_dist:
            kept.append((x, y))
            last_x, last_y = x, y
    kept.append(points[-1])
    return kept if len(kept) >= 3 else points


def path_data(feature: dict, project, tolerance: float = 0.7) -> str:
    parts: list[str] = []
    for ring in feature["rings"]:
        projected = [project(lon, lat) for lon, lat in ring]
        projected = simplify(projected, tolerance)
        if len(projected) < 3:
            continue
        first = projected[0]
        cmds = [f"M {first[0]:.1f} {first[1]:.1f}"]
        cmds.extend(f"L {x:.1f} {y:.1f}" for x, y in projected[1:])
        cmds.append("Z")
        parts.append(" ".join(cmds))
    return " ".join(parts)


def feature_center(feature: dict) -> tuple[float, float]:
    min_x, min_y, max_x, max_y = feature_bbox(feature)
    return (min_x + max_x) / 2, (min_y + max_y) / 2


def county_style(name: str, bay_names: set[str]) -> tuple[str, str, str]:
    if name == "Contra Costa":
        return COUNTY, COUNTY_DARK, "2.2"
    if name in bay_names:
        return BAY_HIGHLIGHT, "#8bb5d9", "1.2"
    return LAND, "#ffffff", "0.8"


def rect(x: int, y: int, w: int, h: int, rx: int = 22, fill: str = CARD) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{BORDER}" stroke-width="1"/>'
    )


def pill(x: int, y: int, label: str, value: str, fill: str) -> str:
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="292" height="56" rx="18" fill="{fill}" stroke="{BORDER}" stroke-width="1"/>',
        f'<text x="{x + 20}" y="{y + 22}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="{MUTED}">{esc(label)}</text>',
        f'<text x="{x + 20}" y="{y + 43}" font-family="Arial, sans-serif" font-size="18" font-weight="800" fill="{INK}">{esc(value)}</text>',
    ])


def build_svg() -> str:
    county_features = load_features(COUNTY_ZIP)
    place_features = load_features(PLACE_ZIP)
    ca = [f for f in county_features if f["properties"].get("STATEFP") == "06"]
    contra = next(f for f in ca if f["properties"].get("COUNTYFP") == "013")
    san_ramon = next(f for f in place_features if f["properties"].get("NAME") == "San Ramon")

    bay_names = {
        "Alameda",
        "Contra Costa",
        "Marin",
        "Napa",
        "San Francisco",
        "San Mateo",
        "Santa Clara",
        "Solano",
        "Sonoma",
    }
    bay = [f for f in ca if f["properties"].get("NAME") in bay_names]

    ca_project = mapper(pad_bounds(bounds(ca), 0.02), 105, 250, 400, 465)
    bay_project = mapper(pad_bounds(bounds(bay), 0.08), 725, 215, 575, 405)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900">',
        "<defs>",
        '<linearGradient id="page" x1="0" x2="1" y1="0" y2="1">',
        '<stop offset="0%" stop-color="#f8fbf7"/>',
        '<stop offset="55%" stop-color="#f2f8fb"/>',
        '<stop offset="100%" stop-color="#fff7ed"/>',
        "</linearGradient>",
        '<filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">',
        '<feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#0f172a" flood-opacity="0.14"/>',
        "</filter>",
        "</defs>",
        '<rect width="1400" height="900" fill="url(#page)"/>',
        '<text x="58" y="70" font-family="Arial, sans-serif" font-size="38" font-weight="900" fill="#111827">Contra Costa County Location Snapshot</text>',
        '<text x="60" y="103" font-family="Arial, sans-serif" font-size="17" fill="#475569">California -> Northern California -> San Francisco Bay Area -> East Bay</text>',
        '<text x="60" y="128" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#334155">Contra Costa County contains San Ramon, our city focus</text>',
        f'<g filter="url(#softShadow)">{rect(48, 132, 590, 685)}</g>',
        '<rect x="72" y="160" width="542" height="615" rx="22" fill="#e8f6fb"/>',
        '<text x="92" y="190" font-family="Arial, sans-serif" font-size="22" font-weight="900" fill="#111827">State view: California</text>',
        '<text x="92" y="216" font-family="Arial, sans-serif" font-size="14" fill="#475569">Contra Costa is the countywide data layer; San Ramon is one city inside it.</text>',
    ]

    for feature in ca:
        name = feature["properties"].get("NAME", "")
        fill, stroke, stroke_width = county_style(name, bay_names)
        parts.append(
            f'<path d="{path_data(feature, ca_project, 0.8)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" vector-effect="non-scaling-stroke"/>'
        )

    cx, cy = ca_project(*feature_center(contra))
    parts.extend([
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="#fff7ed" stroke="{COUNTY_DARK}" stroke-width="3"/>',
        f'<line x1="{cx + 12:.1f}" y1="{cy - 3:.1f}" x2="486" y2="330" stroke="{COUNTY_DARK}" stroke-width="2"/>',
        '<rect x="382" y="278" width="178" height="74" rx="16" fill="#fff7ed" stroke="#fed7aa"/>',
        f'<text x="400" y="306" font-family="Arial, sans-serif" font-size="16" font-weight="900" fill="{COUNTY_DARK}">Contra Costa</text>',
        '<text x="400" y="329" font-family="Arial, sans-serif" font-size="13" fill="#7c2d12">East Bay county</text>',
        '<text x="92" y="750" font-family="Arial, sans-serif" font-size="12" fill="#475569">Orange = Contra Costa County. Light blue = neighboring Bay Area counties.</text>',
        f'<g filter="url(#softShadow)">{rect(684, 132, 668, 510)}</g>',
        '<rect x="708" y="160" width="620" height="445" rx="22" fill="#e8f6fb"/>',
        '<text x="728" y="190" font-family="Arial, sans-serif" font-size="22" font-weight="900" fill="#111827">Bay Area zoom: East Bay focus</text>',
        '<text x="728" y="216" font-family="Arial, sans-serif" font-size="14" fill="#475569">Contra Costa is east of San Francisco and north of Alameda County.</text>',
        '<text x="728" y="237" font-family="Arial, sans-serif" font-size="14" fill="#475569">San Ramon is in the southern part of Contra Costa County.</text>',
    ])

    for feature in bay:
        name = feature["properties"].get("NAME", "")
        fill = COUNTY if name == "Contra Costa" else BAY_LAND
        stroke = COUNTY_DARK if name == "Contra Costa" else "#94a3b8"
        width = "2.2" if name == "Contra Costa" else "1.1"
        parts.append(
            f'<path d="{path_data(feature, bay_project, 0.45)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}" vector-effect="non-scaling-stroke"/>'
        )

    sr_path = path_data(san_ramon, bay_project, 0.25)
    sr_x, sr_y = bay_project(*feature_center(san_ramon))
    parts.extend([
        f'<path d="{sr_path}" fill="{SAN_RAMON}" fill-opacity="0.92" stroke="#1e3a8a" stroke-width="1.6" vector-effect="non-scaling-stroke"/>',
        f'<circle cx="{sr_x:.1f}" cy="{sr_y:.1f}" r="7" fill="#ffffff" stroke="{SAN_RAMON}" stroke-width="4"/>',
        f'<line x1="{sr_x + 8:.1f}" y1="{sr_y - 8:.1f}" x2="1168" y2="535" stroke="{SAN_RAMON}" stroke-width="2"/>',
        '<rect x="1070" y="493" width="210" height="66" rx="18" fill="#eff6ff" stroke="#bfdbfe"/>',
        f'<text x="1090" y="520" font-family="Arial, sans-serif" font-size="16" font-weight="900" fill="{SAN_RAMON}">San Ramon</text>',
        '<text x="1090" y="542" font-family="Arial, sans-serif" font-size="13" fill="#1e40af">Project city focus</text>',
    ])

    label_positions = {
        "Contra Costa": (-10, -10),
        "Alameda": (10, 28),
        "San Francisco": (-52, 12),
        "Solano": (8, -18),
        "Marin": (-36, -18),
        "San Mateo": (-44, 28),
    }
    for feature in bay:
        name = feature["properties"].get("NAME", "")
        if name not in label_positions:
            continue
        lx, ly = bay_project(*feature_center(feature))
        dx, dy = label_positions[name]
        color = "#7c2d12" if name == "Contra Costa" else "#334155"
        parts.append(
            f'<text x="{lx + dx:.1f}" y="{ly + dy:.1f}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="12" font-weight="800" '
            f'fill="{color}">{esc(name)}</text>'
        )

    parts.extend([
        f'<g filter="url(#softShadow)">{rect(684, 672, 668, 145)}</g>',
        '<text x="720" y="715" font-family="Arial, sans-serif" font-size="22" font-weight="900" fill="#111827">How to describe the location</text>',
        pill(720, 737, "State", "California", "#f8fafc"),
        pill(1020, 737, "Part of state", "Northern California", "#f8fafc"),
        pill(720, 802, "Metro region", "San Francisco Bay Area", "#f8fafc"),
        pill(1020, 802, "City inside county", "Contra Costa -> San Ramon", "#fff7ed"),
        '<rect x="72" y="792" width="542" height="46" rx="16" fill="#ffffff" fill-opacity="0.86" stroke="#dbe4ea"/>',
        f'<circle cx="97" cy="815" r="7" fill="{COUNTY}"/>',
        '<text x="116" y="820" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#334155">Source: U.S. Census Bureau 2025 county and place boundaries.</text>',
        "</svg>",
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    if not COUNTY_ZIP.exists():
        raise FileNotFoundError(f"Missing {COUNTY_ZIP}")
    if not PLACE_ZIP.exists():
        raise FileNotFoundError(f"Missing {PLACE_ZIP}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
