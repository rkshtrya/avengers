#!/usr/bin/env python3
"""
Rebuild large source files that are stored as GitHub-friendly CSV parts.

The repository stores the San Francisco permits extract in multiple part files
so every committed file stays below GitHub's normal single-file limit.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SF_PARTS = ROOT / "data" / "raw" / "san_francisco" / "building_permits_selected_parts"
SF_OUTPUT = ROOT / "data" / "raw" / "san_francisco" / "building_permits_selected.csv"


def combine_csv_parts(parts_dir: Path, output_path: Path) -> None:
    parts = sorted(parts_dir.glob("*.csv"))
    if not parts:
        raise FileNotFoundError(f"No CSV parts found in {parts_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as out:
        for index, part in enumerate(parts):
            with part.open("rb") as src:
                header = src.readline()
                if index == 0:
                    out.write(header)
                for line in src:
                    out.write(line)


def main() -> None:
    combine_csv_parts(SF_PARTS, SF_OUTPUT)
    print(f"Wrote {SF_OUTPUT}")


if __name__ == "__main__":
    main()
