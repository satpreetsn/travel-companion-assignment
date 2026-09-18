# src/ui

Terminal chat interface for Travel Companion.

## Files

| File | Purpose |
| --- | --- |
| `terminal.py` | Welcome screen, input loop, answer display, `clear` / `exit` / `quit` |
| `__init__.py` | Package marker |

The UI constructs `TravelCompanionPipeline` and prints only the final assistant reply. Backend traces go to `logs/`.

Started from the project root: `uv run python run.py`.
