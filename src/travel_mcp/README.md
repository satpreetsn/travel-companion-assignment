# src/travel_mcp

Local Model Context Protocol (MCP) layer for dynamic travel information.

Tools currently return mock data for learning; they do not call live travel APIs.

## Files

| File | Purpose |
| --- | --- |
| `server.py` | MCP server exposing `get_flight_info`, `get_currency_exchange_rate`, and weather |
| `client.py` | Client that talks to the local server over MCP |
| `tool_selector.py` | LLM chooses whether an MCP tool is needed and with which arguments |
| `request_router.py` | LLM chooses `rag`, `mcp`, or `both` for the user request |

## When MCP is used

- Weather
- Currency conversion
- Flights

Static destination knowledge still comes from RAG, not these tools.
