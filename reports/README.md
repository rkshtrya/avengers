# Reports Folder Guide

This folder contains the EDA outputs and visual review files.

Use this folder after reading `../README.md` and `../docs/dataset-catalog.md`.

## What To Open First

| File | What it shows |
| --- | --- |
| `visual_review.md` | Short visual walkthrough with charts. |
| `figures/contra_costa_location_snapshot.svg` | Map snapshot showing Contra Costa County in California and the Bay Area. |
| `domain_eda_findings.md` | Product-facing EDA: what the data can and cannot support. |
| `eda_summary.md` | File inventory, row counts, sample paths, and blocked sources. |
| `dataset_inventory.csv` | File-level inventory of data in the repo. |
| `dataset_catalog.csv` | Table version of the dataset catalog. |
| `download_manifest.csv` | Source URLs, local paths, statuses, and notes. |
| `blocked_or_deferred_sources.csv` | Data sources that still need credentials, licensing, or decisions. |

## Folder Map

```text
reports/
  figures/             SVG charts and the county location snapshot
  notebook_tables/     Small tables used by the notebooks
  profiles/            Count tables from EDA
```

## How To Read The EDA

Start with the pictures, then the tables:

1. `visual_review.md`
2. `figures/contra_costa_location_snapshot.svg`
3. `figures/data_readiness.svg`
4. `figures/major_record_counts.svg`
5. `domain_eda_findings.md`
6. `profiles/`

The important point is not just row count. The important point is whether a dataset can support a graph edge and a sourced explanation.
