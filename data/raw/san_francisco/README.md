# San Francisco Building Permits

The selected-column San Francisco building permits extract has 1,291,589 rows and is about 519 MB as a single CSV. To keep the repository usable and avoid GitHub's normal single-file limit, it is stored as CSV parts in:

`data/raw/san_francisco/building_permits_selected_parts/`

Each part repeats the same header row. Most EDA can read the parts directly.

To rebuild the original single CSV locally:

```bash
python3 scripts/reconstruct_large_files.py
```

That writes:

`data/raw/san_francisco/building_permits_selected.csv`

The 250-row review sample is also available at:

`data/processed/samples/building_permits_selected_sample.csv`
