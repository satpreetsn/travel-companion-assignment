# Release Notes

## Travel Companion v0.1.0

**Release date:** 18 September 2026

First local release of Travel Companion: a context-aware travel assistant that combines conversational context, document RAG, MCP tools, and a local LLM. No cloud services are required.

### Highlights

- Terminal chat with `clear` / `exit` / `quit`
- Conversation-level travel context and standalone query rewrite
- PDF ingestion into ChromaDB (`BAAI/bge-small-en-v1.5`) with destination metadata
- Request routing: RAG, MCP, or both
- Local MCP tools (mock): flights, currency, weather
- Answers via Ollama `gemma3:4b`
- Per-session backend logs under `logs/`

### Documentation

- Root `README.md` rewritten so architecture, structure, and flows render correctly
- Folder `README.md` files for `data`, `src` packages, `logs`, `vector_db`, and `ingestion_state`
- New `setup.md` with install steps: Python 3.13, uv, Ollama, ingest, and run
- `.gitignore` still ignores runtime data, but keeps those folder READMEs

### Requirements

- Python 3.13
- uv
- Ollama with `gemma3:4b`
- At least one ingest of `data/raw/` before chatting

### How to run

See [setup.md](setup.md). Short path:

```bash
uv sync
uv run python src/ingestion/ingest.py
uv run python run.py
```

### Notes

- MCP tools use mock data (learning project, not live APIs)
- `vector_db/`, `ingestion_state/`, and `logs/` are local-only and not committed
- Retrieval expects the embedding model to already be in the Hugging Face cache after the first ingest
