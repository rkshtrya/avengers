# Processed Data Guide

This folder is for outputs created from the raw data.

Right now it mainly contains small samples for review.

## Folder Map

```text
processed/
  samples/        Small CSV previews from raw files
```

The full raw files live in `../raw/`.

## Rule

Processed files should be reproducible.

If a new processed file is added, it should be clear:

- which raw source created it
- which script created it
- what filters or joins were applied
- whether it is safe to commit to GitHub
