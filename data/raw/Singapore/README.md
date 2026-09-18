# data/raw/Singapore

PDF source documents for Singapore travel knowledge.

These files are ingested into the `tourism` ChromaDB collection with `destination` metadata set to `Singapore`. Retrieval can then filter chunks to this destination when the conversation context is Singapore.

## Documents

- `Singapore.pdf`
- `Singapore Tourism Guide.pdf`
- `Singapore Travel & Events Guide.pdf`
- `Singapore Travel Orientation & Entry Guide.pdf`
- `Singapore Visitor Background and Logistics Guide.pdf`
- `singapore_rag_knowledge_base.pdf`

Replace or add PDFs here when updating Singapore coverage. Incremental ingestion uses file hashes in `ingestion_state/manifest.json` so unchanged files are skipped.
