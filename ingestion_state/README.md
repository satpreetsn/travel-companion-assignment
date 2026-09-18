# ingestion_state

Persistent tracking for PDF ingestion so unchanged files are not re-embedded.

## Files

| File | Purpose |
| --- | --- |
| `manifest.json` | Maps each ingested PDF to its SHA-256 hash and destination |

`src/ingestion/tracker.py` reads and writes this folder. When a PDF hash changes, old chunks for that source are deleted from ChromaDB and replaced.

This directory is gitignored. It is created automatically on the first successful ingest.
