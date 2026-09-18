# src/generation

Local LLM access and final answer construction.

## Files

| File | Purpose |
| --- | --- |
| `llm.py` | Shared `ChatOllama` client (`gemma3:4b`) |
| `answer.py` | Builds the prompt from the user question, `TravelContext`, RAG chunks, and MCP results |

Other packages call `get_llm()` for routing, tool selection, and context extraction. Only `answer.py` produces the user-visible response.

Requires a local Ollama runtime with the Gemma 3 4B model available.
