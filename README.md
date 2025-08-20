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
research-mcp --stdio
```

Or using Python module directly:
```bash
python -m research_mcp.server serve --stdio
```

The server will listen for MCP protocol messages and route requests to appropriate OpenRouter models based on the routing configuration in `routing.yaml`.

### CLI Options

```bash
research-mcp --help
```

Available options:
- `--env-file .env` - Environment file path (default: .env)
- `--routing routing.yaml` - Routing configuration file (default: routing.yaml)  
- `--stdio` - Use stdio transport for MCP (default: True)

## 🔗 Claude Code Integration

### Method 1: Quick Setup from Any Repository

Install and add the MCP server to Claude Code from any repository:

```bash
# Install the tool globally
pip install git+https://github.com/ethene/research-mcp-tool.git

# Add to Claude Code MCP configuration  
claude mcp add research-mcp-tool \
  --command research-mcp \
  --args "--stdio" \
  --env OPENROUTER_API_KEY=your-api-key-here
```

For environment variable setup:

```bash
# Option 1: Set environment in MCP config
claude mcp add research-mcp-tool \
  --command research-mcp \
  --args "--stdio" \
  --env OPENROUTER_API_KEY=$OPENROUTER_API_KEY

# Option 2: Use with local .env file
claude mcp add research-mcp-tool \
  --command research-mcp \  
  --args "--stdio --env-file /path/to/your/.env" \
  --cwd /path/to/research-mcp-tool
```

**Quick Setup for Development**:
```bash
# From any directory
git clone https://github.com/ethene/research-mcp-tool.git
cd research-mcp-tool
cp .env.example .env
# Edit .env with your API key
claude mcp add research-mcp-tool research-mcp --stdio
```

### Method 2: Manual Configuration

Add to your Claude Code MCP settings file:

```json
{
  "research-mcp-tool": {
    "command": "research-mcp",
    "args": ["--stdio"],
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
research-mcp --help

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

### Authentication Issues

**401 Unauthorized / Invalid API Key**
```bash
# Verify your API key format
grep OPENROUTER_API_KEY .env
# Should show: OPENROUTER_API_KEY=sk-or-v1-...

# Test API key validity
python -c "
import httpx, os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')
resp = httpx.get('https://openrouter.ai/api/v1/models', 
                headers={'Authorization': f'Bearer {api_key}'})
print(f'API Key Status: {resp.status_code}')
"
```

**Missing Environment Variables**
- Ensure `.env` file exists in working directory
- Claude Code MCP config must include `env` section with API key
- Check file permissions: `ls -la .env`

### Network & API Issues

**Network connection failures**
```bash
# Test OpenRouter connectivity
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models
```

**Rate limiting (429 errors)**
- OpenRouter enforces rate limits based on your plan
- Upgrade your OpenRouter plan for higher limits
- Implement request delays if needed

**Timeout errors**
- Large requests may timeout - reduce `max_tokens` parameter
- Check your network stability
- Perplexity models with web search take longer

### Configuration Issues

**YAML parse errors in routing.yaml**
```bash
# Validate YAML syntax
python -c "
import yaml
with open('routing.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('✅ YAML is valid')
    print(f'Tasks: {list(config[\"tasks\"].keys())}')
"
```

**Model fallback triggers**
```bash
# Check which models are available
python -c "
from research_mcp.routing import TaskRouter
router = TaskRouter('routing.yaml')
print('Available models:', router.get_available_models())
print('Fallback models:', router.get_fallback_models())
"
```

**Common YAML errors:**
- Indentation must use spaces, not tabs
- Colons must have space after them: `task: model`
- Model names are case-sensitive: `perplexity/sonar-deep-research`

### Server Issues

**"No module named 'mcp'"**
```bash
pip install modelcontextprotocol
```

**Server startup failures**
```bash
# Test server components
python test_mcp_connection.py

# Run server manually with verbose output
research-mcp --stdio --env-file .env
```

**Server not responding in Claude Code**
- Verify command path: `which research-mcp`
- Test manually: `research-mcp --stdio` 
- Check Claude Code MCP logs in settings
- Ensure working directory is correct in MCP config

### Model Access Issues

**"Model not found" errors**
```bash
# Check specific model availability
python -c "
from research_mcp.openrouter import OpenRouterClient
import asyncio, os
from dotenv import load_dotenv

load_dotenv()
async def check():
    client = OpenRouterClient(os.getenv('OPENROUTER_API_KEY'))
    async with client:
        models = await client.list_models()
        target = 'perplexity/sonar-deep-research'
        found = any(m['id'] == target for m in models['data'])
        print(f'{target}: {\"✅ Available\" if found else \"❌ Not found\"}')

asyncio.run(check())
"
```

**Model access restrictions**
- Some models require special access or higher billing tier
- Verify your OpenRouter account has credits
- Check model-specific requirements in OpenRouter dashboard

### Debug Mode

Enable detailed logging:

```bash
export PYTHONPATH=.
research-mcp --stdio --env-file .env
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
research-mcp --stdio
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