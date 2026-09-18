# vector_db

Local ChromaDB persistence directory for the `tourism` collection.

Ingestion writes embeddings here (`BAAI/bge-small-en-v1.5`). The retriever opens the same path to search chunks, optionally filtering by destination.

## Notes

- Created and updated by `src/ingestion/ingest.py`
- Read at query time by `src/retrieval/retriever.py`
- Gitignored; regenerate by re-running ingestion after placing PDFs in `data/raw/`

Do not edit Chroma internal files by hand. Rebuild the index through the ingestion pipeline instead.
