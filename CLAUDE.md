# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a learning repository for exploring the Anthropic Claude API and the Model Context Protocol (MCP). It is organized into weekly modules:

- `week1-basics/` — MCP server implementations
- `week2-api/` — Direct Anthropic Python SDK usage

## Package Management

All dependencies are managed from the **root** of the repository using a single `pyproject.toml`. There is one shared `.venv` at the root.

```bash
# Clone and install everything in one command
git clone <repo>
cd claude_learn
uv sync
```

Python 3.12+ is required (enforced via `.python-version` at the repo root).

## Running Scripts

All scripts are run from the **repo root** using `uv run python <path>`:

### week2-api — Anthropic SDK scripts

```bash
uv run python week2-api/first_call.py                        # Basic API call
uv run python week2-api/first_call_with_env_stream.py        # Streaming call
uv run python week2-api/conversation_demo.py                 # Multi-turn demo
uv run python week2-api/chat.py                              # Interactive CLI chat
uv run python week2-api/chat_with_context_window_strategy.py # Chat with context management
```

The `ANTHROPIC_API_KEY` must be set — either via `week2-api/.env` (loaded with `python-dotenv`) or as an environment variable. The `.env` file is gitignored.

### week1-basics — MCP servers

MCP servers communicate over stdio and are typically launched by an MCP client (e.g., Claude Desktop). To run manually for testing:

```bash
uv run python week1-basics/weather-mcp-server/weather.py
uv run python week1-basics/code-index-mcp/code_index.py
```

## Architecture

### week2-api

Scripts progressively build on each other:
1. `first_call.py` — reads `ANTHROPIC_API_KEY` from `os.getenv`, single request
2. `first_call_with_env_stream.py` — adds `dotenv` + streaming via `client.messages.stream()`
3. `conversation_demo.py` — introduces the `conversation[]` list pattern for multi-turn context
4. `chat.py` — interactive loop with streaming and token usage reporting
5. `chat_with_context_window_strategy.py` — same pattern extracted into a reusable `chat_with_claude()` function

All scripts use `model="claude-sonnet-4-20250514"` and the `anthropic` Python SDK.

### week1-basics/weather-mcp-server

Uses **FastMCP** (high-level MCP API from `mcp.server.fastmcp`). Tools are declared with the `@mcp.tool()` decorator. The server calls the US National Weather Service API (no API key required) and exposes:
- `get_alerts(state)` — active weather alerts for a 2-letter US state code
- `get_forecast(latitude, longitude)` — 5-period weather forecast

Runs via `mcp.run(transport="stdio")`.

### week1-basics/code-index-mcp

Uses the **low-level MCP Server API** (`mcp.server.Server`), with explicit `@server.list_tools()` and `@server.call_tool()` handlers. Tools include filesystem operations: `search_files`, `search_content`, `read_file`, `list_directory`, and `get_file_changes` (which uses in-memory `file_timestamps` dict to track modifications across calls).

Runs via `stdio_server()` in an async context.
