# data/raw

Destination folders containing the original travel PDFs for RAG.

Each subdirectory name is treated as a destination label during ingestion. Only `.pdf` files in these folders are processed.

## Current destinations

| Folder | Purpose |
| --- | --- |
| `Singapore/` | Singapore travel guides used by the local knowledge base |

Place new PDFs in the matching destination folder, then run ingestion so ChromaDB stays in sync.
