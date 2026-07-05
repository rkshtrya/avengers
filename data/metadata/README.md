# Metadata Guide

This folder stores supporting metadata about downloads and source services.

Metadata helps answer:

- where a file came from
- when it was retrieved
- whether a public service responded
- what layers or service details were available

## Files

| File | What it is |
| --- | --- |
| `download_manifest.json` | Download status, local file paths, source URLs, and notes. |
| `fema_nfhl_mapserver_metadata.json` | FEMA NFHL ArcGIS service metadata used to inspect flood layers. |
| `calfire_fhsz_catalog_metadata.json` | CAL FIRE catalog/service metadata. |
| `calfire_fhsz_webmap.json` | CAL FIRE web map metadata. |

Use these when checking provenance or when rebuilding the download process.
