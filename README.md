# Travel Companion Assignment

A local, context-aware AI travel assistant that combines:

- Conversational travel context
- Document-based RAG
- MCP tools
- LLM-based answer generation

This is a learning project. It runs entirely on the local machine and does not require cloud services.

---

## Architecture

```
User
  ↓
Conversation History
  ↓
Context Extraction
  ↓
TravelContext
  ↓
Query Contextualization
  ↓
Request Router
  ↓
RAG / MCP / BOTH
  ↓
Answer Generation
  ↓
Gemma 3 4B
  ↓
Final Answer
```

Everything shown above runs locally: terminal UI, pipeline, ChromaDB, MCP server (mock tools), and Ollama.

---



## Project Structure

```
travel-companion-assignment/
├── data/
│   └── raw/
│       └── Singapore/          # Destination PDFs for RAG
├── ingestion_state/
│   └── manifest.json           # Ingest file hashes (gitignored)
├── logs/
│   └── backend_<timestamp>.log # Per-session backend logs (gitignored)
├── src/
│   ├── context/                # TravelContext and query rewrite
│   ├── generation/             # Ollama client and answer prompts
│   ├── ingestion/              # PDF → chunks → ChromaDB
│   ├── retrieval/              # Semantic search
│   ├── tests/                  # Component checks
│   ├── travel_companion_assignment/
│   ├── travel_mcp/             # MCP server, client, routing
│   ├── ui/                     # Terminal chat
│   └── pipeline.py             # Request orchestrator
├── vector_db/                  # ChromaDB persistence (gitignored)
├── run.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

Each source and data folder has its own `README.md` with file-level detail.

---



## Main Components



### Context management

**Location:** `src/context/`

Responsible for:

- Extracting travel information from user messages
- Maintaining conversation-level travel context
- Detecting new destinations and destination changes
- Resolving references such as *there*, *here*, *that city*, and *the destination*
- Creating standalone queries for retrieval

```
User Message
     ↓
Context Extraction
     ↓
TravelContext.update()
     ↓
Current Travel Context
```



### Document ingestion

**Location:** `src/ingestion/`

Builds the local RAG knowledge base from PDFs under `data/raw/`.

```
PDF
 ↓
Text Extraction
 ↓
Chunking
 ↓
Embedding Generation
 ↓
ChromaDB
```

Each destination is a subdirectory of `data/raw/` (for example `data/raw/Singapore/`). The folder name is stored as `destination` metadata on every chunk.

### Retrieval

**Location:** `src/retrieval/`

The retrieval layer:

1. Receives a standalone query
2. Generates an embedding
3. Searches the local ChromaDB `tourism` collection
4. Optionally filters results by destination
5. Returns the most relevant document chunks

**Embedding model:** `BAAI/bge-small-en-v1.5`

```
Standalone Query
       ↓
Embedding Model
       ↓
Query Embedding
       ↓
ChromaDB
       ↓
Relevant Documents
```



### MCP

**Location:** `src/travel_mcp/`

The project uses the MCP protocol with a local MCP server. Tools currently return mock data for learning.

**Tools**

- Flight information
- Currency exchange rate
- Weather

```
server.py          → MCP tools
client.py          → MCP protocol communication
tool_selector.py   → selects required MCP tool
request_router.py  → chooses RAG / MCP / BOTH
```



### Request routing

The request router decides which information source is required.


| Route    | Use when                                                                            |
| -------- | ----------------------------------------------------------------------------------- |
| **RAG**  | Static travel knowledge: attractions, transport, culture, destinations, itineraries |
| **MCP**  | Dynamic information the tools support: weather, currency, flights                   |
| **BOTH** | The question needs static knowledge and live-style facts together                   |


Example of **BOTH**: *What should I do in Singapore tomorrow and what's the weather like?*

```
RAG → activities from the knowledge base
MCP → weather from the local tool
```



### Answer generation

**Location:** `src/generation/`

The final answer is generated from:

- User question
- Travel context
- Retrieved documents
- MCP results
- Local LLM (`gemma3:4b` via Ollama)

```
User Question
      +
Travel Context
      +
RAG Results
      +
MCP Results
      ↓
Answer Generation
      ↓
Gemma 3 4B
      ↓
Final Answer
```



### Terminal UI

**Location:** `src/ui/`

The terminal interface:

- Displays the welcome screen
- Accepts user messages
- Displays assistant responses
- Handles `clear`, `exit`, and `quit`
- Shows user-facing errors only

Backend diagnostics are written to log files, not the chat.

---



## Running the Application

First-time install (Python, uv, Ollama, ingest) is documented in [setup.md](setup.md).

From the project root:

```bash
uv run python run.py
```

That starts the terminal Travel Companion interface.

```
======================================================================
                    TRAVEL COMPANION
======================================================================

Your local AI travel assistant

Commands:
  clear         Start a new conversation
  exit          Exit the application

You: I am planning a 4 day trip to Singapore
```



### Conversation commands


| Command          | Effect                                              |
| ---------------- | --------------------------------------------------- |
| `clear`          | Starts a new conversation and resets travel context |
| `exit` or `quit` | Ends the session                                    |


Example:

```
You: clear

Conversation cleared.
Travel context has been reset.
```



### Ingesting documents

After adding or updating PDFs under `data/raw/<Destination>/`:

```bash
uv run python src/ingestion/ingest.py
```

Unchanged files are skipped using hashes in `ingestion_state/manifest.json`.

---



## Session Logging

Every run of `run.py` creates a separate backend log file:

```
logs/
└── backend_20260918_011111_641496.log
```

The filename includes the session start timestamp.

Logs include context extraction, current travel context, standalone query, MCP discovery/selection/execution, request routing, RAG retrieval, debug information, and exceptions.

```
run.py
  ↓
Create new timestamp
  ↓
Create new backend log
  ↓
Configure logging
  ↓
Start Travel Companion
```

When the session ends, the application prints the path of that log file.

---



## Complete Request Flow

```
                         User
                           │
                           ▼
                  User Message
                           │
                           ▼
                 Context Extraction
                           │
                           ▼
                    TravelContext
                           │
                           ▼
                Query Contextualization
                           │
                           ▼
                    Standalone Query
                           │
                           ▼
                   Request Router
                           │
                ┌──────────┼──────────┐
                │          │          │
                ▼          ▼          ▼
               RAG        MCP        BOTH
                │          │          │
                ▼          ▼          ▼
            ChromaDB    MCP Client   ChromaDB
                           │          │
                           ▼          ▼
                       MCP Server     MCP
                           │          │
                           └────┬─────┘
                                │
                                ▼
                       Answer Generation
                                │
                                ▼
                           Gemma 3 4B
                                │
                                ▼
                        Assistant Response
```



### RAG flow

Knowledge-base question:

```
User → Context Extraction → TravelContext → Standalone Query
  → Request Router → RAG → Embedding Model → ChromaDB
  → Relevant Documents → Answer Generation → Gemma 3 4B → Answer
```



### MCP flow

Dynamic-information question:

```
User → Context Extraction → TravelContext → Request Router → MCP
  → Tool Selector → Selected Tool → MCP Client → MCP Server
  → Tool Result → Answer Generation → Gemma 3 4B → Answer
```



### RAG + MCP flow

```
User → Context Extraction → TravelContext → Request Router → BOTH
        /    \
      RAG    MCP
       │      │
   ChromaDB  MCP Server
        \    /
         Answer Generation → Gemma 3 4B → Answer
```

---



## Local Technology Stack


| Component       | Technology               |
| --------------- | ------------------------ |
| Language        | Python 3.13              |
| Package manager | uv                       |
| LLM runtime     | Ollama                   |
| LLM             | Gemma 3 4B               |
| Vector database | ChromaDB                 |
| Embeddings      | BAAI/bge-small-en-v1.5   |
| PDF processing  | PyMuPDF                  |
| Text splitting  | LangChain Text Splitters |
| MCP             | MCP Python SDK           |
| Interface       | Terminal                 |


```
┌─────────────────────────────────────────┐
│            Local Machine                │
│                                         │
│  Terminal UI                            │
│       │                                 │
│       ▼                                 │
│  Travel Companion Pipeline              │
│       │                                 │
│   ┌───┴──────────────┐                  │
│   │                  │                  │
│   ▼                  ▼                  │
│ ChromaDB          MCP Server            │
│   │                  │                  │
│   │              Local Mock Tools       │
│   │                  │                  │
│   └────────┬─────────┘                  │
│            ▼                            │
│       Gemma 3 4B                        │
│            │                            │
│            ▼                            │
│       Final Answer                      │
│                                         │
└─────────────────────────────────────────┘
```

No cloud infrastructure is required.

Components are split so context, retrieval, MCP, generation, and UI can be developed and tested independently.

---



## Future Extensions

- Additional destinations
- More MCP tools
- Real-time travel APIs
- Improved retrieval ranking
- Conversation history persistence
- Better destination-specific context handling
- Hybrid RAG + MCP responses
- Web-based UI
- Evaluation and testing framework
- Improved document metadata and filtering

