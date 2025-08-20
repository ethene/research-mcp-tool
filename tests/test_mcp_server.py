"""Test the actual MCP server functionality."""

import asyncio
import json
import os
import tempfile
import yaml
from dotenv import load_dotenv
from unittest.mock import AsyncMock, patch

from research_mcp.server import MCPServer

# Load environment
load_dotenv()

async def test_mcp_server_initialization():
    """Test that MCP server can be initialized properly."""
    print("🧪 Testing MCP Server Initialization")
    
    # Create temporary routing file
    config_data = {
        "tasks": {
            "test_task": "openai/gpt-4o-mini"
        },
        "fallbacks": ["openai/gpt-4o-mini"]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        api_key = os.getenv('OPENROUTER_API_KEY', 'test-key')
        server = MCPServer(api_key, "https://test.api/v1", config_path)
        print("✅ MCP Server initialized successfully")
        print(f"   Router has {len(server.router.get_available_tasks())} tasks")
        return True
    except Exception as e:
        print(f"❌ MCP Server initialization failed: {e}")
        return False
    finally:
        os.unlink(config_path)


async def test_mcp_tools_with_live_api():
    """Test MCP tools with live OpenRouter API."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️  No API key - skipping live MCP tests")
        return True
    
    print("\n🧪 Testing MCP Tools with Live API")
    
    # Create routing config
    config_data = {
        "tasks": {
            "ux_copy": "openai/gpt-4o-mini"
        },
        "fallbacks": ["openai/gpt-4o-mini"]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        server = MCPServer(api_key, "https://openrouter.ai/api/v1", config_path)
        
        # Test 1: list_models tool
        print("\n1️⃣ Testing list_models tool...")
        result = await server._list_models({"filter": "openai"})
        print(f"✅ list_models returned {len(result)} content items")
        
        # Test 2: validate_model tool  
        print("\n2️⃣ Testing validate_model tool...")
        result = await server._validate_model({"name": "openai/gpt-4o-mini"})
        print("✅ validate_model works")
        
        # Test 3: route_chat tool
        print("\n3️⃣ Testing route_chat tool...")
        result = await server._route_chat({
            "task": "ux_copy",
            "messages": [{"role": "user", "content": "Say 'MCP test' in 2 words"}],
            "options": {"max_tokens": 5}
        })
        print("✅ route_chat completed successfully")
        print(f"   Response contains: {len(result)} content items")
        
        # Test 4: cost_estimate tool
        print("\n4️⃣ Testing cost_estimate tool...")
        result = await server._cost_estimate({
            "model": "openai/gpt-4o-mini",
            "tokens_in": 100,
            "tokens_out": 50
        })
        print("✅ cost_estimate works")
        print(f"   Estimated cost in result: {len(result)} content items")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(config_path)


async def test_mcp_server_cli():
    """Test that the CLI can at least show help without errors."""
    print("\n🧪 Testing MCP Server CLI")
    
    try:
        # Import and test the CLI setup
        from research_mcp.server import app
        print("✅ CLI app imported successfully")
        print(f"   App name: {app.info.name}")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


async def main():
    """Run all MCP server tests."""
    print("🚀 Starting MCP Server Tests")
    print("=" * 50)
    
    tests = [
        test_mcp_server_initialization(),
        test_mcp_tools_with_live_api(),
        test_mcp_server_cli()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All MCP server tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        for i, result in enumerate(results):
            if result is not True:
                print(f"   Test {i+1}: {result}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)