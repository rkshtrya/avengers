# Project Lattice Data Workspace

I put this repo together so we can review Project Lattice from the data up: what we already have, what is strong enough to build on, and what still needs a decision before we claim a real valuation product.

Project Lattice is an explainable property intelligence and valuation product. The point is not just to output a number; the point is to show why a property looks fairly priced, overpriced, undervalued, risky, or promising, with every claim tied back to source data.

## How I Want The Team To Review This

Start here:

1. `docs/project-lattice-data-handoff.md`  
   My summary of what is in the repo, what is missing, and how I want us to review it.

2. `reports/domain_eda_findings.md`  
   The most useful EDA readout. This connects the datasets back to the actual product: parcels, permits, schools, risks, amenities, and valuation readiness.

3. `reports/eda_summary.md`  
   A compact inventory of the downloaded files, row counts, fields, samples, and blocked sources.

4. `reports/download_manifest.csv`  
   The source URL and status behind each downloaded file.

5. `data/processed/samples/`  
   Small samples we can inspect quickly before opening the full raw files.

## Repo Layout

```text
data/
  raw/                  Downloaded source datasets
  processed/samples/    Small samples for quick review
  metadata/             Source/service metadata
  source_registry.csv   Source list, priority, and open EDA questions
docs/                   Project notes and team review plan
reports/                EDA summaries and profile outputs
reports/profiles/       Count tables from the domain EDA
scripts/                Download, EDA, and file reconstruction scripts
project_brief/          Project deck export
notebooks/              Notebook workspace notes
```

## Data I Included

- Contra Costa parcels, city limits, zoning, general-plan land use, urban limit line, and LAFCO sphere of influence.
- California Census TIGER boundaries for tracts, block groups, and places.
- CDE public schools and districts.
- CAL FIRE wildfire hazard severity zone extracts.
- FEMA flood hazard zone attributes for the project area.
- OpenStreetMap San Ramon POIs.
- San Francisco building permit extract, stored as split CSV parts because the single CSV is too large for a normal GitHub file.

## Large SF Permit File

The San Francisco permits extract is 519 MB as one CSV, so I split it into parts here:

`data/raw/san_francisco/building_permits_selected_parts/`

To rebuild the original single CSV locally:

```bash
python3 scripts/reconstruct_large_files.py
```

The rebuilt file is ignored by Git so we do not accidentally recommit a file over GitHub's normal limit.

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

Some sources still need credentials, manual download, or a business decision. See:

`reports/blocked_or_deferred_sources.csv`

## My Current Read

We have enough public/contextual data to build the graph, run spatial joins, produce source-backed explanations, and make a credible demo.

The blocker is still comparable sales. Before we claim production-grade valuation, we need a permitted comps source with sale price, sale date, property identity, and basic property characteristics.
