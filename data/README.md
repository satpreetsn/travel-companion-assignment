# data

Source documents used to build the local RAG knowledge base.

PDFs are organized by destination under `raw/`. Ingestion reads this tree, extracts text, chunks it, and stores embeddings in `vector_db/`.

## Layout

```
data/
└── raw/
    └── Singapore/
```

Add a new destination by creating `data/raw/<DestinationName>/` and placing PDF guides in that folder. The folder name is stored as the `destination` metadata on each chunk.
