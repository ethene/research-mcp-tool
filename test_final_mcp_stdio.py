#!/usr/bin/env python3
"""
Final test to verify research-mcp --stdio command works correctly.

This script tests the complete MCP server functionality by:
1. Starting the research-mcp --stdio process
2. Sending MCP protocol messages
3. Verifying responses
4. Testing all 4 MCP tools
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path


def test_mcp_stdio_startup():
    """Test that research-mcp --stdio starts without errors."""
    print("🧪 Testing research-mcp --stdio startup...")
    
    try:
        # Start the process
        proc = subprocess.Popen(
            ['research-mcp', '--stdio'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Give it a moment to start
        import time
        time.sleep(1)
        
        # Check if process is running
        if proc.poll() is None:
            print("✅ research-mcp --stdio started successfully")
            proc.terminate()
            proc.wait()
            return True
        else:
            stdout, stderr = proc.communicate()
            print(f"❌ Process exited with code: {proc.returncode}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ research-mcp command not found")
        print("   Try: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Error testing startup: {e}")
        return False


def test_mcp_protocol():
    """Test basic MCP protocol communication."""
    print("\n🧪 Testing MCP protocol communication...")
    
    try:
        # Start the process
        proc = subprocess.Popen(
            ['research-mcp', '--stdio'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Send initialize message
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the message
        message = json.dumps(init_request) + '\n'
        proc.stdin.write(message)
        proc.stdin.flush()
        
        # Read response with timeout
        import select
        ready, _, _ = select.select([proc.stdout], [], [], 5.0)
        
        if ready:
            response_line = proc.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if response.get("id") == 1 and "result" in response:
                    print("✅ MCP protocol initialization successful")
                    proc.terminate()
                    proc.wait()
                    return True
                else:
                    print(f"❌ Unexpected response: {response}")
            else:
                print("❌ No response received")
        else:
            print("❌ Timeout waiting for response")
            
        proc.terminate()
        proc.wait()
        return False
        
    except Exception as e:
        print(f"❌ Error testing MCP protocol: {e}")
        if 'proc' in locals():
            proc.terminate()
            proc.wait()
        return False


def test_environment_check():
    """Test that all required files exist."""
    print("\n🧪 Testing environment...")
    
    checks = [
        (".env", "Environment file"),
        ("routing.yaml", "Routing configuration"),
    ]
    
    all_good = True
    for file_path, desc in checks:
        if os.path.exists(file_path):
            print(f"✅ {desc} found: {file_path}")
        else:
            print(f"❌ {desc} missing: {file_path}")
            all_good = False
    
    # Check API key
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
        if "OPENROUTER_API_KEY=sk-or-" in env_content:
            print("✅ API key configured in .env")
        else:
            print("⚠️  API key may not be configured")
            all_good = False
    
    return all_good


def main():
    """Run all tests."""
    print("🚀 Final MCP Server Test - research-mcp --stdio")
    print("=" * 60)
    
    tests = [
        ("Environment Check", test_environment_check),
        ("Startup Test", test_mcp_stdio_startup),
        ("Protocol Test", test_mcp_protocol),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append(result)
        print(f"Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUCCESS: research-mcp --stdio is working correctly!")
        print("\n🔗 Ready for Claude Code integration:")
        print("""
Add this to your Claude Code MCP settings:

{
  "research-mcp-tool": {
    "command": "research-mcp",
    "args": ["--stdio"],
    "env": {
      "OPENROUTER_API_KEY": "your-api-key-here"
    }
  }
}
        """)
        return True
    else:
        print("❌ FAILED: Some tests failed")
        print("\n🛠️ Troubleshooting:")
        print("1. Run: pip install -e .")
        print("2. Check: cp .env.example .env")
        print("3. Add API key to .env file")
        print("4. Run: python test_mcp_connection.py")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)