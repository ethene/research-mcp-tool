"""MCP server entry point."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from dotenv import load_dotenv
from pydantic import BaseModel
from rich.console import Console
from rich.logging import RichHandler
import logging

from mcp import Tool, McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .openrouter import OpenRouterClient
from .routing import TaskRouter

# Set up rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()

# Cost estimation table (rough estimates in USD per 1K tokens)
COST_ESTIMATES = {
    # OpenAI models
    "openai/gpt-4o": {"input": 0.005, "output": 0.015},
    "openai/gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "openai/gpt-4": {"input": 0.03, "output": 0.06},
    
    # Anthropic models
    "anthropic/claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "anthropic/claude-3.7-sonnet": {"input": 0.003, "output": 0.015},
    "anthropic/claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    
    # Meta models
    "meta-llama/llama-3.1-70b-instruct": {"input": 0.0004, "output": 0.0004},
    "meta-llama/llama-3.1-8b-instruct": {"input": 0.0001, "output": 0.0001},
    
    # Perplexity models (with search costs)
    "perplexity/sonar-deep-research": {"input": 0.005, "output": 0.005, "search": 5.0},
    "perplexity/sonar-reasoning": {"input": 0.001, "output": 0.001, "search": 0.005},
    
    # Default fallback
    "default": {"input": 0.001, "output": 0.002}
}

class MCPServer:
    """MCP Server implementation with OpenRouter integration."""
    
    def __init__(self, api_key: str, base_url: str, routing_config: str):
        """Initialize MCP server."""
        self.client = OpenRouterClient(api_key, base_url)
        self.router = TaskRouter(routing_config)
        self.server = Server("research-mcp-tool")
        self._setup_handlers()
        logger.info("MCP Server initialized")
    
    def _setup_handlers(self):
        """Set up MCP tool handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools():
            """List available tools."""
            return [
                Tool(
                    name="list_models",
                    description="List available models from OpenRouter, optionally filtered by name/provider",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "Optional filter to match model names or providers"
                            }
                        }
                    }
                ),
                Tool(
                    name="validate_model",
                    description="Validate if a model exists and return its details",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Model name to validate"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="route_chat", 
                    description="Route a chat request to appropriate model based on task type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Task type (research_deep, research_fast, spec_structuring, ux_copy)"
                            },
                            "messages": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "role": {"type": "string"},
                                        "content": {"type": "string"}
                                    },
                                    "required": ["role", "content"]
                                },
                                "description": "Chat messages in OpenAI format"
                            },
                            "options": {
                                "type": "object",
                                "properties": {
                                    "temperature": {"type": "number"},
                                    "max_tokens": {"type": "integer"},
                                    "top_p": {"type": "number"},
                                    "reasoning": {"type": "boolean"},
                                    "search_limit": {"type": "integer"}
                                },
                                "description": "Optional generation parameters"
                            }
                        },
                        "required": ["task", "messages"]
                    }
                ),
                Tool(
                    name="cost_estimate",
                    description="Estimate cost for using a specific model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Model name"
                            },
                            "tokens_in": {
                                "type": "integer", 
                                "description": "Input tokens"
                            },
                            "tokens_out": {
                                "type": "integer",
                                "description": "Output tokens"
                            },
                            "searches": {
                                "type": "integer",
                                "description": "Number of searches (for Perplexity models)",
                                "default": 0
                            }
                        },
                        "required": ["model", "tokens_in", "tokens_out"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            """Handle tool calls."""
            try:
                if name == "list_models":
                    return await self._list_models(arguments)
                elif name == "validate_model":
                    return await self._validate_model(arguments)
                elif name == "route_chat":
                    return await self._route_chat(arguments)
                elif name == "cost_estimate":
                    return await self._cost_estimate(arguments)
                else:
                    raise McpError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
                raise McpError(f"Tool error: {str(e)}")
    
    async def _list_models(self, args: Dict[str, Any]):
        """List available models."""
        models_data = await self.client.list_models()
        models = models_data.get("data", [])
        
        # Apply filter if provided
        filter_str = args.get("filter", "").lower()
        if filter_str:
            models = [
                m for m in models 
                if filter_str in m.get("id", "").lower() or 
                   filter_str in m.get("owned_by", "").lower()
            ]
        
        # Format response
        formatted_models = []
        for model in models:
            formatted_models.append({
                "name": model.get("id", ""),
                "context": model.get("context_length", 0),
                "pricing": model.get("pricing"),
                "provider": model.get("owned_by", "")
            })
        
        result = {
            "count": len(formatted_models),
            "models": formatted_models
        }
        
        return [{"type": "text", "text": str(result)}]
    
    async def _validate_model(self, args: Dict[str, Any]):
        """Validate model existence."""
        model_name = args.get("name")
        if not model_name:
            raise McpError("Model name is required")
        
        models_data = await self.client.list_models()
        models = models_data.get("data", [])
        
        # Find matching model
        for model in models:
            if model.get("id", "").lower() == model_name.lower():
                result = {
                    "name": model.get("id", ""),
                    "context": model.get("context_length", 0),
                    "pricing": model.get("pricing"),
                    "provider": model.get("owned_by", ""),
                    "exists": True
                }
                return [{"type": "text", "text": str(result)}]
        
        # Model not found
        result = {"exists": False, "error": f"Model '{model_name}' not found"}
        return [{"type": "text", "text": str(result)}]
    
    async def _route_chat(self, args: Dict[str, Any]):
        """Route chat request to appropriate model."""
        task = args.get("task")
        messages = args.get("messages")
        options = args.get("options", {})
        
        if not task:
            raise McpError("Task is required")
        if not messages:
            raise McpError("Messages are required")
        
        # Get available models
        models_data = await self.client.list_models()
        available_models = [m.get("id", "") for m in models_data.get("data", [])]
        
        # Route to appropriate model
        try:
            selected_model = self.router.route_task(task, available_models)
        except ValueError as e:
            raise McpError(str(e))
        
        # Prepare request options
        chat_options = {}
        if "temperature" in options:
            chat_options["temperature"] = options["temperature"]
        if "max_tokens" in options:
            chat_options["max_tokens"] = options["max_tokens"]
        if "top_p" in options:
            chat_options["top_p"] = options["top_p"]
        
        # Handle special options
        if options.get("reasoning"):
            chat_options["reasoning"] = True
        
        if options.get("search_limit") and "perplexity" in selected_model.lower():
            logger.info(f"Search limit {options['search_limit']} noted for {selected_model}")
        
        # Make the chat request
        response = await self.client.chat_completion(
            model=selected_model,
            messages=messages,
            **chat_options
        )
        
        # Extract response data
        choice = response.get("choices", [{}])[0]
        usage = response.get("usage", {})
        
        result = {
            "model_used": selected_model,
            "tokens": {
                "in": usage.get("prompt_tokens", 0),
                "out": usage.get("completion_tokens", 0)
            },
            "content": choice.get("message", {}).get("content", ""),
        }
        
        # Add citations if available (Perplexity models)
        if "citations" in choice:
            result["citations"] = choice["citations"]
        
        return [{"type": "text", "text": str(result)}]
    
    async def _cost_estimate(self, args: Dict[str, Any]):
        """Estimate cost for model usage."""
        model = args.get("model")
        tokens_in = args.get("tokens_in", 0)
        tokens_out = args.get("tokens_out", 0)
        searches = args.get("searches", 0)
        
        if not model:
            raise McpError("Model name is required")
        
        # Get cost data
        cost_data = COST_ESTIMATES.get(model, COST_ESTIMATES["default"])
        
        # Calculate costs
        input_cost = (tokens_in / 1000) * cost_data["input"]
        output_cost = (tokens_out / 1000) * cost_data["output"]
        search_cost = 0
        
        if searches > 0 and "search" in cost_data:
            search_cost = (searches / 1000) * cost_data["search"]
        
        total_cost = input_cost + output_cost + search_cost
        
        breakdown = {
            "input_tokens": f"${input_cost:.6f}",
            "output_tokens": f"${output_cost:.6f}"
        }
        
        if search_cost > 0:
            breakdown["searches"] = f"${search_cost:.6f}"
        
        result = {
            "estimate_usd": f"${total_cost:.6f}",
            "breakdown": breakdown
        }
        
        return [{"type": "text", "text": str(result)}]
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Research MCP Tool server...")
        logger.info(f"Available tasks: {', '.join(self.router.get_available_tasks())}")
        
        async with self.client:
            await stdio_server(self.server.request_ctx)

# CLI setup
app = typer.Typer(help="Research MCP Tool - OpenRouter integration for Claude Code")

@app.command()
def serve(
    env_file: str = typer.Option(".env", help="Environment file path"),
    routing: str = typer.Option("routing.yaml", help="Routing configuration file"),
    stdio: bool = typer.Option(True, help="Use stdio transport (default)"),
):
    """Start the MCP server."""
    # Load environment
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    
    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        console.print("❌ [red]Error: OPENROUTER_API_KEY not found in environment[/red]")
        console.print(f"Please add your API key to {env_file}")
        raise typer.Exit(1)
    
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Check routing file
    if not os.path.exists(routing):
        console.print(f"❌ [red]Error: Routing config not found: {routing}[/red]")
        raise typer.Exit(1)
    
    # Start server
    server = MCPServer(api_key, base_url, routing)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise typer.Exit(1)

def main():
    """Main entry point."""
    app()

if __name__ == "__main__":
    main()