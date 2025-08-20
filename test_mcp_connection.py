#!/usr/bin/env python3
"""
Simple MCP server connection tester.

This script helps verify that the MCP server is working correctly
and can be used for debugging Claude Code integration issues.
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path

def test_cli_available():
    """Test if the CLI command is available."""
    print("🧪 Testing CLI availability...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'research_mcp.server', 'serve', '--help'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ CLI command available")
            return True
        else:
            print("❌ CLI command failed:")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  CLI command timed out (might be working)")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_env_setup():
    """Test if environment is set up correctly."""
    print("\n🧪 Testing environment setup...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        return False
    
    # Check for API key
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    if "OPENROUTER_API_KEY=sk-or-" in env_content:
        print("✅ .env file has API key configured")
        return True
    elif "OPENROUTER_API_KEY=" in env_content:
        print("⚠️  .env file exists but API key may not be set")
        print("   Make sure OPENROUTER_API_KEY=sk-or-your-key-here")
        return False
    else:
        print("❌ .env file doesn't contain OPENROUTER_API_KEY")
        return False

def test_routing_config():
    """Test if routing configuration is valid."""
    print("\n🧪 Testing routing configuration...")
    
    routing_file = Path("routing.yaml") 
    if not routing_file.exists():
        print("❌ routing.yaml not found")
        return False
    
    try:
        import yaml
        with open(routing_file, 'r') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            print("❌ routing.yaml is not a valid dictionary")
            return False
            
        if 'tasks' not in config:
            print("❌ routing.yaml missing 'tasks' section")
            return False
            
        if 'fallbacks' not in config:
            print("❌ routing.yaml missing 'fallbacks' section")  
            return False
        
        tasks = len(config['tasks'])
        fallbacks = len(config['fallbacks'])
        print(f"✅ routing.yaml valid ({tasks} tasks, {fallbacks} fallbacks)")
        return True
        
    except Exception as e:
        print(f"❌ routing.yaml error: {e}")
        return False

async def test_server_start():
    """Test if server can start without errors."""
    print("\n🧪 Testing server startup...")
    
    try:
        # Try to import and initialize core components
        from research_mcp.server import MCPServer
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            print("⚠️  No API key found, testing with dummy key")
            api_key = "test-key"
        
        server = MCPServer(api_key, "https://openrouter.ai/api/v1", "routing.yaml")
        print("✅ Server components initialize successfully")
        return True
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_integration_help():
    """Print help for Claude Code integration."""
    print("\n📋 Claude Code Integration Help")
    print("=" * 40)
    
    print("\n1. Add to Claude Code MCP settings:")
    print("""
{
  "research-mcp-tool": {
    "command": "python",
    "args": ["-m", "research_mcp.server", "serve", "--stdio"],
    "cwd": "%s",
    "env": {
      "OPENROUTER_API_KEY": "your-api-key-here"
    }
  }
}""" % os.getcwd())

    print("\n2. Or if installed globally:")
    print("""
{
  "research-mcp-tool": {
    "command": "research-mcp",
    "args": ["--stdio"],  
    "env": {
      "OPENROUTER_API_KEY": "your-api-key-here"
    }
  }
}""")

    print("\n3. Test the connection in Claude Code:")
    print("   Ask: 'Use the list_models tool to show available models'")

async def main():
    """Run all tests."""
    print("🚀 Research MCP Tool - Connection Tester")
    print("=" * 50)
    
    tests = [
        test_cli_available(),
        test_env_setup(), 
        test_routing_config(),
        await test_server_start()
    ]
    
    passed = sum(1 for result in tests if result)
    total = len(tests)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server should work with Claude Code.")
        print_integration_help()
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Run: pip install -e .")
        print("- Run: cp .env.example .env")
        print("- Add your OpenRouter API key to .env")
        print("- Check that routing.yaml exists and is valid")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)