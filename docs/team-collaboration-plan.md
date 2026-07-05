# Project Lattice Team Collaboration Plan

## How I Want Us To Work

I want GitHub to be the source of truth for the data review. Slides or docs are fine for presentation polish, but the actual source registry, EDA results, scripts, and decisions should live here so we can audit what changed.

The goal for this phase is not to make the model look good. The goal is to decide whether the data can support the product we want to build.

## Folder Structure

```text
docs/
  README.md                         # How to read the docs folder
  dataset-catalog.md                # Plain-English guide to every dataset
  knowledge-graph-plan.md           # How the data becomes graph nodes and edges
  project-lattice-data-sources.md   # Product understanding and source strategy
  project-lattice-data-review.md    # What I downloaded and how to review it
  team-collaboration-plan.md        # This workflow
data/
  README.md                         # How to read the data folder
  source_registry.csv               # Source list, priority, and EDA questions
  raw/                              # Downloaded source files already organized by folder
  processed/samples/                # Small review samples
  metadata/                         # Source/service metadata
reports/
  README.md                         # How to read the EDA outputs
  domain_eda_findings.md            # Main product-oriented EDA summary
  eda_summary.md                    # File inventory, row counts, and samples
  profiles/                         # Count tables from EDA
scripts/
  README.md
  download_project_lattice_data.py
  eda_project_lattice_data.py
  profile_project_lattice_data.py
notebooks/
  README.md
```

## Team Workflow

1. Start with `docs/project-lattice-data-review.md`.
2. Use `data/source_registry.csv` as the operating checklist.
3. Assign one owner per `P0` source or unresolved source gap.
4. Each owner should answer the EDA questions already listed in the registry.
5. Put evidence in notebooks or scripts, but put decisions back into `docs/` or `reports/`.
6. Do not add more large raw files casually. If a new file is large, decide first whether it belongs in Git, a GitHub Release asset, Drive, S3, or another shared bucket.

## Suggested Ownership

| Workstream | Owner | Deliverable |
| --- | --- | --- |
| Parcels and zoning | TBD | Can we build the base property graph for the chosen metro? |
| Comparable sales | TBD | Can we get enough sale records for credible valuation/backtest? |
| Transit and commute | TBD | Can we compute nearest stop and commute to a target office? |
| Risk layers | TBD | Can we label flood/wildfire risk with source-backed edges? |
| Schools and demographics | TBD | Can we derive explainable school/neighborhood features? |
| Product narrative | TBD | Can we turn the EDA into the final team presentation? |

## EDA Goals

The first pass should answer whether the data can support the promised final output:

- `Valuation result`: Do we have enough comparable sales?
- `Why this number`: Can we compute traceable value-driver features?
- `Hidden upside`: Can we identify permits, transit projects, zoning, or redevelopment signals?
- `Hidden risk`: Can we identify flood, wildfire, insurance-relevant, or oversupply signals?
- `For you`: Can we personalize with commute and school preferences?
- `Every claim links to a public record`: Can each graph edge store source metadata?

## The Key Milestone

Before we invest heavily in UI or multi-agent orchestration, we need to validate comparable sales.

Minimum acceptable evidence:

- At least 50-200 sale records in the chosen metro.
- Sale price and sale date.
- Matchable property identifier: APN, normalized address, or coordinates.
- Basic property attributes: beds, baths, square footage, lot size, property type.
- Clear permission to use the data for the capstone/demo.

If we cannot secure this, we should keep Lattice as an explainability/decision-support demo and label valuation as illustrative.

## Presentation Structure For The Team

1. What Lattice needs from data.
2. Which sources are verified and sufficient.
3. Which sources are promising but need owner follow-up.
4. The critical blocker: comparable sales.
5. MVP recommendation: story-first San Ramon vs data-first San Francisco.
6. EDA assignments and one-week validation plan.
