# 🧠 Research MCP Tool

<div align="center">

**Intelligent AI Model Router for Claude Code**

*A Python MCP (Model Context Protocol) server that automatically routes requests to optimal OpenRouter models based on task type*

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Integrated-orange.svg)](https://openrouter.ai/)

</div>

## ✨ Features

This tool acts as an intelligent routing layer between Claude Code and OpenRouter's API, automatically selecting the best model for different types of research and content generation tasks:

| Task Type | Model | Use Case |
|-----------|-------|----------|
| 🔍 **Deep Research** | `perplexity/sonar-deep-research` | Comprehensive research with citations |
| ⚡ **Fast Research** | `perplexity/sonar-reasoning` | Quick lookups and fact-checking |
| 📋 **Spec Structuring** | `anthropic/claude-3.7-sonnet` | Technical specifications and documentation |
| ✏️ **UX Copy** | `openai/gpt-4o-mini` | User-facing content and messaging |

### 🎯 Key Benefits

- **🤖 Automatic Model Selection**: No need to manually choose models
- **💰 Cost Optimization**: Routes to cost-effective models for each task
- **🔄 Fallback Support**: Automatically switches to backup models if primary unavailable  
- **📊 Usage Tracking**: Built-in token counting and cost estimation
- **⚙️ Configurable**: Easy YAML-based routing configuration

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [OpenRouter API key](https://openrouter.ai/) (free tier available)
- [Claude Code](https://claude.ai/code) for MCP integration

### Installation

1. **Clone and install:**
   ```bash
   git clone https://github.com/ethene/research-mcp-tool.git
   cd research-mcp-tool
   pip install -e .
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

3. **Get your OpenRouter API key:**
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Go to [API Keys](https://openrouter.ai/keys)
   - Create a new key
   - Add it to your `.env` file:
   ```bash
   OPENROUTER_API_KEY=sk-or-your-key-here
   ```

### Test Installation

```bash
# Test the installation
python tests/test_end_to_end.py

# You should see:
# 🧪 Running End-to-End Tests with Live API
# ✅ Found 314+ models
# ✅ All routing works
# ✅ Live chat completion successful
# 🎉 All end-to-end tests passed!
```

## Running Locally

Start the MCP server:
```bash
research-mcp serve --stdio
```

Or using Python module directly:
```bash
python -m research_mcp.server serve --stdio
```

The server will listen for MCP protocol messages and route requests to appropriate OpenRouter models based on the routing configuration in `routing.yaml`.

### CLI Options

```bash
research-mcp serve --help
```

Available options:
- `--env-file .env` - Environment file path (default: .env)
- `--routing routing.yaml` - Routing configuration file (default: routing.yaml)  
- `--stdio` - Use stdio transport for MCP (default: True)

## 🔗 Claude Code Integration

### Method 1: Automatic Registration (Recommended)

Add this MCP server to Claude Code:

```bash
claude mcp add research-mcp-tool
```

### Method 2: Manual Configuration

Add to your Claude Code MCP settings file:

```json
{
  "research-mcp-tool": {
    "command": "research-mcp",
    "args": ["serve", "--stdio"],
    "env": {
      "OPENROUTER_API_KEY": "sk-or-your-key-here"
    }
  }
}
```

### Method 3: Direct Path (if installed locally)

```json
{
  "research-mcp-tool": {
    "command": "/path/to/research-mcp-tool/venv/bin/python",
    "args": ["-m", "research_mcp.server", "serve", "--stdio"],
    "cwd": "/path/to/research-mcp-tool",
    "env": {
      "OPENROUTER_API_KEY": "sk-or-your-key-here"
    }
  }
}
```

## 💡 Usage Examples

Once registered with Claude Code, the MCP tools are automatically available. You can use them in natural language:

### 🔍 Research Tasks

```
👤 "Research the latest developments in quantum computing using deep research"
🤖 Uses perplexity/sonar-deep-research for comprehensive analysis with citations

👤 "Quick lookup: What's the current Python version?"  
🤖 Uses perplexity/sonar-reasoning for fast fact-checking
```

### 📋 Content Generation

```
👤 "Structure this API specification document"
🤖 Uses anthropic/claude-3.7-sonnet for technical documentation

👤 "Write user-friendly error messages for this form"
🤖 Uses openai/gpt-4o-mini for UX copy
```

### 🛠️ Direct Tool Usage

You can also call tools directly:

```
👤 "Use the list_models tool to show me available Anthropic models"
👤 "Use route_chat with task='research_deep' to analyze this data"
👤 "Use cost_estimate to calculate pricing for 1000 tokens with gpt-4o"
```

### 🎯 Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_models` | List available OpenRouter models | `filter` (optional) |
| `validate_model` | Check if model exists | `name` (required) |
| `route_chat` | Route chat to optimal model | `task`, `messages`, `options` |
| `cost_estimate` | Calculate usage costs | `model`, `tokens_in`, `tokens_out`, `searches` |

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

## 🔧 Advanced Configuration

### Custom Model Routing

Edit `routing.yaml` to add new task types or change models:

```yaml
tasks:
  research_deep: perplexity/sonar-deep-research
  research_fast: perplexity/sonar-reasoning
  spec_structuring: anthropic/claude-3.7-sonnet
  ux_copy: openai/gpt-4o-mini
  # Add your custom tasks:
  code_review: anthropic/claude-3.7-sonnet
  translation: openai/gpt-4o
  creative_writing: anthropic/claude-3.5-sonnet

fallbacks:
  - openai/gpt-4o-mini    # Cheap and fast
  - meta-llama/llama-3.1-70b-instruct  # Open source backup
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | _(required)_ | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | API base URL |

### CLI Options

```bash
research-mcp serve --help

Options:
  --env-file TEXT     Environment file path [default: .env]  
  --routing TEXT      Routing config file [default: routing.yaml]
  --stdio BOOLEAN     Use stdio transport [default: true]
```

## 🧪 Development & Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/test_basic.py          # Unit tests (fast, mocked)
python tests/test_live.py           # Live API tests (requires key)
python tests/test_end_to_end.py     # Full integration test

# Run with coverage
pytest --cov=research_mcp tests/

# Run single test
pytest -k "test_routing" -v
```

### Development Setup

```bash
# Install with dev dependencies  
pip install -e ".[dev]"

# Run linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Type checking (if you add type hints)
mypy src/research_mcp/
```

### Adding New Task Types

1. **Add to routing.yaml:**
   ```yaml
   tasks:
     your_new_task: preferred/model
   ```

2. **Update cost estimates** in `src/research_mcp/server.py`:
   ```python
   COST_ESTIMATES = {
       "your/model": {"input": 0.001, "output": 0.002}
   }
   ```

3. **Test your changes:**
   ```bash
   python tests/test_end_to_end.py
   ```

## 🔍 Troubleshooting

### Common Issues

**"No module named 'mcp'"**
```bash
pip install modelcontextprotocol
```

**"OpenRouter API key not found"**
- Check `.env` file exists and contains `OPENROUTER_API_KEY=sk-or-...`
- Ensure Claude Code MCP config includes the `env` section

**"Model not found" errors**
- Check if model exists: `python tests/test_live.py`
- Verify your OpenRouter account has access to the model
- Check routing.yaml for typos in model names

**Server not responding in Claude Code**
- Test server manually: `research-mcp serve --stdio`
- Check Claude Code MCP logs
- Verify the command path in MCP configuration

### Debug Mode

Enable detailed logging:

```bash
export PYTHONPATH=.
research-mcp serve --stdio --env-file .env
```

## 📊 Performance & Costs

### Token Usage

The tool automatically tracks token usage for all requests:

```python
# Example response
{
    "model_used": "perplexity/sonar-deep-research",
    "tokens": {"in": 150, "out": 800},
    "content": "Research results...",
    "citations": ["https://source1.com", "..."]
}
```

### Cost Optimization

- **UX Copy**: Uses `gpt-4o-mini` (~$0.0006/1K tokens)
- **Fast Research**: Uses `perplexity/sonar-reasoning` (~$0.001/1K tokens)
- **Deep Research**: Uses `perplexity/sonar-deep-research` (~$0.005/1K + search costs)
- **Technical Specs**: Uses `claude-3.7-sonnet` (~$0.015/1K tokens output)

The routing system automatically selects cost-effective models while maintaining quality for each task type.

## 🧪 Verification & Testing

### Quick Connection Test

Run the built-in connection tester:

```bash
python test_mcp_connection.py
```

This will verify:
- ✅ CLI command availability
- ✅ Environment setup (.env with API key)
- ✅ Routing configuration (routing.yaml)  
- ✅ Server startup without errors

### Manual MCP Server Test

Start the server manually to test:

```bash
research-mcp serve --stdio
```

You should see:
```
INFO     Starting Research MCP Tool server...
INFO     Available tasks: research_deep, research_fast, spec_structuring, ux_copy
```

The server will wait for MCP protocol messages via stdin/stdout.

### Test with Real API Calls

Verify everything works with your OpenRouter API key:

```bash
python tests/test_end_to_end.py
```

Expected output:
```
🧪 Running End-to-End Tests with Live API
✅ Found 314+ models
✅ Task routing works for all 4 tasks
✅ Live chat completion: "API test successful."
✅ Cost estimation accurate
🎉 All end-to-end tests passed!
```

## 🤝 Contributing & Support

### Found an Issue?

1. **Check the troubleshooting section** above
2. **Run the connection tester**: `python test_mcp_connection.py`
3. **Test with live API**: `python tests/test_end_to_end.py`
4. **Open an issue** with the output of these tests

### Want to Contribute?

1. Fork the repository
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`  
4. Make your changes
5. Add tests for new functionality
6. Submit a pull request

---

<div align="center">

**🧠 Research MCP Tool** - *Intelligent AI routing for Claude Code*

Made with ❤️ for the Claude Code community

</div>