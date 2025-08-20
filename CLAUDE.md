# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python MCP (Model Context Protocol) server that acts as an intelligent routing layer between Claude Code and OpenRouter's API. It automatically selects the best model for different types of tasks based on a configurable routing system.

### Core Architecture

The system has three main components that work together:

1. **OpenRouterClient** (`src/research_mcp/openrouter.py`): HTTP client for OpenRouter API with authentication
2. **TaskRouter** (`src/research_mcp/routing.py`): Maps task types to specific models using `routing.yaml` config, with fallback handling
3. **MCPServer** (`src/research_mcp/server.py`): MCP protocol implementation with 4 tools (list_models, validate_model, route_chat, cost_estimate)

### Task Routing System

The routing logic maps high-level task types to specific models:
- `research_deep` → `perplexity/sonar-deep-research` (comprehensive research)
- `research_fast` → `perplexity/sonar-reasoning` (quick lookups)
- `spec_structuring` → `anthropic/claude-3.7-sonnet` (technical specs)
- `ux_copy` → `openai/gpt-4o-mini` (user-facing content)

If a preferred model is unavailable, the system automatically falls back to backup models defined in `routing.yaml`.

## Development Commands

### Setup and Installation
```bash
pip install -e .                    # Install package in development mode
cp .env.example .env                # Set up environment (add OpenRouter API key)
```

### Running Tests
```bash
pytest                              # Run all tests
pytest tests/test_basic.py          # Run basic unit tests (mocked)
python tests/test_live.py           # Run live API tests (requires API key)
python tests/test_end_to_end.py     # Run comprehensive end-to-end tests
pytest -k "test_routing"            # Run specific test pattern
```

### Running the MCP Server
```bash
research-mcp serve --stdio          # Start MCP server (default for Claude Code)
python -m research_mcp.server serve --stdio  # Alternative method
research-mcp serve --help           # Show CLI options
```

### Configuration
- **Environment**: Modify `.env` for API keys and base URLs
- **Model Routing**: Edit `routing.yaml` to change task-to-model mappings
- **Cost Estimates**: Update `COST_ESTIMATES` dict in `server.py` for pricing

## Key Implementation Details

### MCP Tools Provided
1. `list_models(filter?)` - Retrieve available OpenRouter models with optional filtering
2. `validate_model(name)` - Check if specific model exists and get details
3. `route_chat(task, messages, options?)` - Route chat to appropriate model based on task type
4. `cost_estimate(model, tokens_in, tokens_out, searches?)` - Calculate usage costs including search pricing for Perplexity models

### Error Handling
- TaskRouter validates YAML structure on load and provides clear error messages for unknown tasks
- OpenRouterClient handles HTTP errors and authentication failures gracefully
- MCP server wraps all tool calls in try/catch to return proper MCP error responses

### Testing Strategy
- `test_basic.py`: Unit tests with mocked HTTP calls for routing and client logic
- `test_live.py`: Integration tests using real OpenRouter API (requires API key)
- `test_end_to_end.py`: Complete workflow tests simulating actual MCP tool usage

The live tests verify that all 314 models can be fetched, routing works for all configured tasks, and real chat completions succeed with proper token tracking and cost calculation.