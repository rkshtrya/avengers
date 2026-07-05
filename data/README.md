# Data Folder Guide

This folder contains the data files used for the Project Lattice review.

Start here if you want to know where the actual files are.

## Simple Map

```text
data/
  source_registry.csv        Main checklist of sources, priority, status, and open questions
  raw/                       Actual downloaded source files
  processed/samples/         Small sample CSVs created from the raw files
  metadata/                  JSON metadata from source services and downloads
```

## What To Open First

| Step | Open | What it tells you |
| --- | --- | --- |
| 1 | `../DATA_FILES.md` | Exact raw files uploaded to GitHub. |
| 2 | `source_registry.csv` | Source list, status, priority, and remaining questions. |
| 3 | `raw/README.md` | What each raw-data folder contains. |
| 4 | `processed/samples/README.md` | How to use the small sample files. |
| 5 | `metadata/README.md` | What the metadata files are for. |

## Raw vs Processed

| Folder | Meaning |
| --- | --- |
| `raw/` | Files downloaded from source agencies or public data services. These should stay close to the original source. |
| `processed/samples/` | Small sample files created so the team can inspect columns and values quickly. These are easier to open in GitHub. |
| `metadata/` | Download manifests and service metadata. These help prove where files came from and what was available. |

## How To Review A Dataset

For any dataset, ask:

1. What place does it cover?
2. What source agency published it?
3. What kind of data is it?
4. What key lets it join to parcels: APN, address, coordinates, geometry, tract ID, school ID, or permit ID?
5. Does it support a user-facing claim?
6. What is missing before we can use it confidently?

## Important Current Answer

The data here supports a knowledge-graph and explanation demo.

The missing piece for production valuation is comparable sales: sale price, sale date, property characteristics, and a legal right to use the data.
