# src/tests

Manual / script-style checks for core pipeline pieces.

These modules are not a full pytest suite with fixtures; they exercise components with sample Singapore context.

## Files

| File | Purpose |
| --- | --- |
| `test_context.py` | Travel context extraction and updates |
| `test_contextualization.py` | Standalone query rewriting |
| `test_tool_selector.py` | MCP tool selection |
| `test_answer.py` | Answer generation from sample RAG (and related) inputs |

Run from an environment where `src` packages are importable and Ollama is available for LLM-backed tests.
