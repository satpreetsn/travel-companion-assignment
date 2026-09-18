# logs

Per-session backend logs written when the app starts via `run.py`.

Each run creates a file named `backend_<YYYYMMDD_HHMMSS_microseconds>.log`. The terminal UI shows only user-facing messages; diagnostics stay in these files.

## Typical log contents

- Context extraction and current `TravelContext`
- Standalone (contextualized) query
- Request routing (`rag` / `mcp` / `both`)
- MCP tool discovery, selection, and results
- RAG retrieval debug information
- Exceptions

This directory is gitignored. `run.py` creates it if it does not exist.
