# src/ingestion

Turns destination PDFs into ChromaDB embeddings for RAG.

## Files

| File | Purpose |
| --- | --- |
| `load_pdf.py` | Extract page text with PyMuPDF |
| `chunk.py` | Split pages (~800 tokens, 100 overlap) and attach destination/source metadata |
| `tracker.py` | SHA-256 hashes and `ingestion_state/manifest.json` |
| `ingest.py` | Walk `data/raw/`, skip unchanged files, delete stale chunks, embed with `BAAI/bge-small-en-v1.5` |

## Flow

```
PDF → text extraction → chunking → embedding → vector_db (tourism)
```

Run ingestion from the project root after adding or updating PDFs under `data/raw/`.
