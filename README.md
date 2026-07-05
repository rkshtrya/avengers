# Project Lattice Data Workspace

This repository is a data and EDA handoff for Project Lattice, an explainable property intelligence and valuation product.

The goal of this workspace is to help the team review source coverage, inspect the available data, understand the remaining gaps, and build the next feature-engineering layer.

## Review Order

Start here:

1. `docs/project-lattice-data-handoff.md`  
   Team-facing overview, review workflow, source gaps, and next steps.

2. `reports/domain_eda_findings.md`  
   Product-oriented EDA: sufficiency matrix, parcel coverage, permit signal, schools, risks, OSM POIs, and recommended decisions.

3. `reports/eda_summary.md`  
   Dataset inventory with row counts, file sizes, samples, and blocked/deferred sources.

4. `reports/download_manifest.csv`  
   Download status, source URLs, file paths, and notes.

5. `data/processed/samples/`  
   Small samples for quick review without opening full raw files.

## Repository Layout

```text
data/
  raw/                  Downloaded source datasets
  processed/samples/    Small review samples generated from raw files
  metadata/             Source/service metadata
  source_registry.csv   Source registry and MVP relevance notes
docs/                   Project handoff and collaboration notes
reports/                EDA summaries and profile outputs
reports/profiles/       Count tables from domain EDA
scripts/                Download, EDA, and reconstruction scripts
project_brief/          Project deck export
notebooks/              Notebook workspace notes
```

## Included Dataset Areas

- Contra Costa parcels, city limits, zoning, general-plan land use, urban limit line, and LAFCO sphere of influence.
- California Census TIGER boundaries for tracts, block groups, and places.
- CDE public schools and districts.
- CAL FIRE wildfire hazard severity zone extracts.
- FEMA flood hazard zone attributes for the project bbox.
- OpenStreetMap San Ramon POIs.
- San Francisco building permit selected-column extract, stored as split CSV parts.

## Important Data Note

The San Francisco permits extract is 519 MB as one CSV, so it is stored in split parts under:

`data/raw/san_francisco/building_permits_selected_parts/`

To rebuild the single source file locally:

```bash
python3 scripts/reconstruct_large_files.py
```

The rebuilt file is ignored by Git to avoid accidentally committing a file larger than GitHub's normal limit.

## Reproduce The EDA

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run:

```bash
python3 scripts/eda_project_lattice_data.py
python3 scripts/profile_project_lattice_data.py
```

To refresh source downloads:

```bash
python3 scripts/download_project_lattice_data.py
```

Some sources need credentials or manual decisions. See:

`reports/blocked_or_deferred_sources.csv`

## Current Project Verdict

The public/contextual data is strong enough for source review, knowledge-graph design, early joins, and explainability work.

The critical blocker is comparable sales. Before claiming production-grade valuation, the team needs a permitted comps source with sale price, sale date, property identity, and property characteristics.
