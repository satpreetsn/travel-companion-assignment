# src/retrieval

Semantic search over the local `tourism` ChromaDB collection.

## Files

| File | Purpose |
| --- | --- |
| `retriever.py` | `Retriever` class: embed the standalone query, search, optional destination filter, return top-k chunks |
| `debug_retrival.py` | Ad-hoc retrieval debugging helper |

The embedding model matches ingestion: `BAAI/bge-small-en-v1.5` (loaded with `local_files_only=True` at query time).

Used when the request router chooses `rag` or `both`.
