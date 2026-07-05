# Project Lattice Data Collaboration Plan

## Recommended collaboration setup

Use a GitHub repository as the source of truth, with Google Slides or Google Docs only for presentation polish.

The reason: the team needs both narrative alignment and reproducible EDA. A shared doc alone will get messy. A repo lets everyone inspect the same source registry, run notebooks, commit findings, and keep data decisions auditable.

## Folder structure

```text
docs/
  project-lattice-data-sources.md   # Deep source analysis and current verdict
  team-collaboration-plan.md        # This collaboration workflow
data/
  source_registry.csv               # Machine-readable source list and EDA ownership
  raw/                              # Local only; do not commit large raw data
  processed/                        # Small derived samples are okay if allowed
notebooks/
  README.md                         # Notebook conventions
  01_source_inventory.ipynb         # Pull/sample each source
  02_spatial_join_quality.ipynb     # Parcels + boundaries + risks + amenities
  03_comps_feasibility.ipynb        # Comparable sales blocker analysis
  04_feature_eda.ipynb              # Value-driver feature distributions
  05_demo_property_report.ipynb     # One property end-to-end
```

## Team workflow

1. Use `data/source_registry.csv` as the operating checklist.
2. Assign one owner per `P0` source.
3. Each owner answers the EDA questions in the registry.
4. Each owner adds a short finding to `docs/project-lattice-data-sources.md`.
5. Use notebooks for evidence, not prose. Put decisions and conclusions back in docs.
6. Keep large raw data out of Git. Store it in Google Drive, S3, or a shared data bucket, and commit only sample rows or metadata.

## Suggested ownership

| Workstream | Owner | Deliverable |
| --- | --- | --- |
| Parcels and zoning | TBD | Can we build the base property graph for the chosen metro? |
| Comparable sales | TBD | Can we get enough sale records for credible valuation/backtest? |
| Transit and commute | TBD | Can we compute nearest stop and commute to a target office? |
| Risk layers | TBD | Can we label flood/wildfire risk with source-backed edges? |
| Schools and demographics | TBD | Can we derive explainable school/neighborhood features? |
| Product narrative | TBD | Can we turn EDA findings into the final team presentation? |

## EDA goals

The first EDA pass should not try to prove the model works. It should answer whether the data can support the promised final output:

- `Valuation result`: Do we have enough comparable sales?
- `Why this number`: Can we compute traceable value-driver features?
- `Hidden upside`: Can we identify permits, transit projects, zoning, or redevelopment signals?
- `Hidden risk`: Can we identify flood, wildfire, insurance-relevant, or oversupply signals?
- `For you`: Can we personalize with commute and school preferences?
- `Every claim links to a public record`: Can each graph edge store source metadata?

## The key milestone

Before investing heavily in UI or multi-agent orchestration, validate comparable sales.

Minimum acceptable evidence:

- At least 50-200 sale records in the chosen metro.
- Sale price and sale date.
- Matchable property identifier: APN, normalized address, or coordinates.
- Basic property attributes: beds, baths, square footage, lot size, property type.
- Clear permission to use the data for the capstone/demo.

If this cannot be secured, keep Lattice as an explainability/decision-support demo and label valuation as illustrative.

## Presentation structure for the team

1. What Lattice needs from data.
2. Which sources are verified and sufficient.
3. Which sources are promising but need owner follow-up.
4. The critical blocker: comparable sales.
5. MVP recommendation: story-first San Ramon vs data-first San Francisco.
6. EDA assignments and one-week validation plan.

