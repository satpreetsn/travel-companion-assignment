# src

Application source for the local Travel Companion pipeline.

`pipeline.py` is the orchestrator: it extracts travel context, routes the request to RAG and/or MCP, and generates the final answer with the local LLM.

## Packages

| Package | Role |
| --- | --- |
| `context/` | Conversation travel state and query contextualization |
| `ingestion/` | PDF load, chunk, embed, and persist to ChromaDB |
| `retrieval/` | Semantic search over the tourism collection |
| `travel_mcp/` | Local MCP server, client, tool selection, and routing |
| `generation/` | Ollama LLM client and answer assembly |
| `ui/` | Terminal chat interface |
| `tests/` | Component-level checks |
| `travel_companion_assignment/` | Package entry placeholder from `pyproject.toml` |

Start the product from the project root with `uv run python run.py`, which loads `src.ui.terminal`.
