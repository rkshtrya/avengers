# Notebook Notes

Use notebooks for evidence, not as the only place where decisions live. If a notebook changes our direction, summarize the decision back in `docs/` or `reports/`.

## Suggested Notebook Order

- `01_source_inventory.ipynb`
- `02_spatial_join_quality.ipynb`
- `03_comps_feasibility.ipynb`
- `04_feature_eda.ipynb`
- `05_demo_property_report.ipynb`

## Rules I Want Us To Follow

- Read source metadata from `../data/source_registry.csv`.
- Keep credentials in local environment variables, never in notebooks.
- Do not add more large raw files without deciding where they should live.
- Write small reproducible outputs to `../data/processed/` only when licensing allows it.
- At the top of every notebook, list:
  - owner
  - source IDs used
  - run date
  - open questions
  - final verdict

## Minimum EDA Outputs

For every source, answer:

- Does it load?
- How many records are available?
- What geography does it cover?
- What keys can join it to parcels?
- What fields are missing?
- How fresh is the data?
- Can it support a user-facing claim with provenance?
