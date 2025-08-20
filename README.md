# Research MCP Tool

A Python MCP (Model Context Protocol) server that routes requests to different OpenRouter models based on task type.

## Purpose

This tool acts as an intelligent routing layer between Claude Code and OpenRouter's API, automatically selecting the best model for different types of research and content generation tasks:

- **Deep Research**: Uses Perplexity Sonar for comprehensive research
- **Fast Research**: Uses Perplexity Sonar for quick lookups  
- **Spec Structuring**: Uses Claude 3.7 Sonnet for technical specifications
- **UX Copy**: Uses GPT-4o Mini for user-facing content

## Setup

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

3. **Get OpenRouter API Key:**
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Generate an API key
   - Update the `OPENROUTER_API_KEY` in your `.env` file

## Running Locally

Start the MCP server:
```bash
research-mcp
```

The server will listen for MCP protocol messages and route requests to appropriate OpenRouter models based on the routing configuration in `routing.yaml`.

## Register with Claude Code

Add this MCP server to Claude Code:

```bash
claude mcp add research-mcp-tool
```

Then configure it in your Claude Code MCP settings:

```json
{
  "research-mcp-tool": {
    "command": "research-mcp",
    "env": {
      "OPENROUTER_API_KEY": "your-api-key-here"
    }
  }
}
```

## Example Usage

Once registered with Claude Code, you can use the research tools:

```
# Deep research task
Ask Claude: "Research the latest developments in quantum computing using deep research"

# Fast lookup
Ask Claude: "Quick research on Python async best practices"

# Technical specifications  
Ask Claude: "Structure this API specification document"

# UX copy
Ask Claude: "Write user-friendly error messages for this form"
```

The tool will automatically route these requests to the appropriate models based on the task type.

## Configuration

Edit `routing.yaml` to customize model routing:

```yaml
tasks:
  research_deep: perplexity/sonar-deep-research
  research_fast: perplexity/sonar-reasoning  
  spec_structuring: anthropic/claude-3.7-sonnet
  ux_copy: openai/gpt-4o-mini

fallbacks:
  - openai/gpt-4o-mini
  - meta-llama/llama-3.1-70b-instruct
```

## Development

Run tests:
```bash
pytest
```

Install development dependencies:
```bash
pip install -e ".[dev]"
```