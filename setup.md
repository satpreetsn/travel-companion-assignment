# Setup

Install and run Travel Companion on a local machine. No cloud APIs are required.

## Prerequisites

| Requirement | Notes |
| --- | --- |
| Python 3.13 | Matches `.python-version` and `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | Package and environment manager |
| [Ollama](https://ollama.com/) | Local LLM runtime |
| Git | To clone the repository |
| Disk / RAM | Embedding model plus `gemma3:4b` (several GB). A GPU is optional |

### Install uv (if needed)

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Confirm:

```bash
uv --version
python --version
```

If `python` is not 3.13, install it with `uv python install 3.13`.

### Install Ollama (if needed)

1. Download and install from [https://ollama.com/download](https://ollama.com/download).
2. Start the Ollama app so the local server is running.
3. Pull the model used by this project:

```bash
ollama pull gemma3:4b
```

Confirm:

```bash
ollama list
```

You should see `gemma3:4b`.

---

## 1. Clone the repository

```bash
git clone <repository-url>
cd travel-companion-assignment
```

---

## 2. Install Python dependencies

From the project root:

```bash
uv sync
```

This creates `.venv` and installs packages from `pyproject.toml` (ChromaDB, sentence-transformers, PyMuPDF, MCP SDK, langchain-ollama, and so on).

`requirements.txt` is a shorter list for reference. Prefer `uv sync` so versions match the project.

---

## 3. Build the RAG knowledge base

PDFs live under `data/raw/<Destination>/` (Singapore is included). Ingestion writes embeddings to `vector_db/` using `BAAI/bge-small-en-v1.5`.

Run from the project root:

```bash
uv run python src/ingestion/ingest.py
```

The first run downloads the embedding model from Hugging Face (needs network). Later ingest runs skip unchanged PDFs using `ingestion_state/manifest.json`.

Query-time retrieval loads that model with `local_files_only=True`, so ingestion must succeed at least once before you chat.

Expected console output includes `[SKIP]`, `[NEW]`, or `[UPDATE]` per PDF, then `Ingestion complete.`

---

## 4. Start the assistant

Keep Ollama running, then:

```bash
uv run python run.py
```

You should see the terminal welcome screen:

```
======================================================================
                    TRAVEL COMPANION
======================================================================

Your local AI travel assistant

Commands:
  clear         Start a new conversation
  exit          Exit the application
```

Try:

```
You: I am planning a 4 day trip to Singapore
```

| Command | Effect |
| --- | --- |
| `clear` | Reset conversation and travel context |
| `exit` or `quit` | End the session |

Backend diagnostics go to `logs/backend_<timestamp>.log`. The log path is printed when the session ends.

Architecture and component details are in [README.md](README.md).

---

## Quick checklist

1. Python 3.13 and uv installed
2. Ollama running with `gemma3:4b`
3. `uv sync`
4. `uv run python src/ingestion/ingest.py`
5. `uv run python run.py`

---

## Troubleshooting

**`ollama` / connection errors when answering**  
Ollama is not running, or `gemma3:4b` was not pulled. Start Ollama and run `ollama pull gemma3:4b`.

**Retrieval fails or collection missing**  
`vector_db/` is empty or incomplete. Run ingestion from the project root again.

**Embedding model not found (`local_files_only`)**  
The Hugging Face cache does not have `BAAI/bge-small-en-v1.5`. Re-run ingest while online so the model can download.

**Import errors for `src.*`**  
Run commands from the repository root, not from inside `src/`.

**MCP tools fail to start**  
The client launches `src/travel_mcp/server.py` with the same Python as `uv run`. Use `uv run python run.py` so the environment includes the MCP SDK.

**Slow first answer**  
The first LLM call after Ollama starts can take longer while the model loads into memory.
