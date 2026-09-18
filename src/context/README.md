# src/context

Conversation-level travel state used across RAG, MCP, and answer generation.

## Files

| File | Purpose |
| --- | --- |
| `manager.py` | `TravelContext` dataclass, LLM-based extraction, destination change handling, and standalone query rewriting |

## Responsibilities

- Extract destination, dates, travelers, budget, and interests from the latest user message
- Detect new destinations vs destination changes vs the same destination
- Resolve references such as “there”, “here”, and “that city”
- Rewrite the user message into a standalone retrieval query

`TravelCompanionPipeline` owns one `TravelContext` instance for the session. `clear` in the terminal UI resets it.
