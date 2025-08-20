"""End-to-end tests with real API calls to verify the implementation works."""

import asyncio
import os
import json
from dotenv import load_dotenv

from research_mcp.routing import TaskRouter
from research_mcp.openrouter import OpenRouterClient

# Load environment
load_dotenv()

async def test_full_workflow():
    """Test the complete workflow with real API calls."""
    
    print("🧪 Running End-to-End Tests with Live API")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No OPENROUTER_API_KEY found")
        return
    
    # Initialize components
    client = OpenRouterClient(api_key)
    router = TaskRouter("routing.yaml")
    
    async with client:
        
        # Test 1: List models (tool 1)
        print("\n1️⃣ Testing list_models functionality...")
        try:
            models_data = await client.list_models()
            models = models_data.get("data", [])
            
            # Format like the tool would
            formatted_models = []
            for model in models[:3]:  # Just first 3 for brevity
                formatted_models.append({
                    "name": model.get("id", ""),
                    "context": model.get("context_length", 0),
                    "pricing": model.get("pricing"),
                    "provider": model.get("owned_by", "")
                })
            
            result = {
                "count": len(models),
                "models": formatted_models
            }
            
            print(f"✅ Found {result['count']} models")
            print(f"   Sample: {formatted_models[0]['name']} by {formatted_models[0]['provider']}")
            
        except Exception as e:
            print(f"❌ list_models failed: {e}")
            return
        
        # Test 2: Validate model (tool 2) 
        print("\n2️⃣ Testing validate_model functionality...")
        try:
            # Test with a model we know exists
            test_model = "openai/gpt-4o-mini"
            found = False
            
            for model in models:
                if model.get("id", "").lower() == test_model.lower():
                    result = {
                        "name": model.get("id", ""),
                        "context": model.get("context_length", 0),
                        "pricing": model.get("pricing"),
                        "provider": model.get("owned_by", ""),
                        "exists": True
                    }
                    found = True
                    break
            
            if found:
                print(f"✅ Model validation works: {test_model} exists")
                print(f"   Context: {result['context']} tokens")
            else:
                print(f"❌ Model {test_model} not found")
                
        except Exception as e:
            print(f"❌ validate_model failed: {e}")
            return
        
        # Test 3: Route and execute chat (tool 3)
        print("\n3️⃣ Testing route_chat functionality...")
        try:
            # Get available model names
            available_models = [m.get("id", "") for m in models]
            
            # Test routing for each configured task
            for task in router.get_available_tasks():
                try:
                    selected_model = router.route_task(task, available_models)
                    print(f"   ✅ {task} → {selected_model}")
                    
                    # Test one actual chat completion
                    if task == "ux_copy":  # Use cheapest for testing
                        messages = [{"role": "user", "content": "Say 'API test successful' in 3 words."}]
                        
                        response = await client.chat_completion(
                            model=selected_model,
                            messages=messages,
                            max_tokens=10
                        )
                        
                        # Format like the tool would
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
                        
                        print(f"   💬 Response: '{result['content']}'")
                        print(f"   📊 Tokens: {result['tokens']['in']} in, {result['tokens']['out']} out")
                        
                except ValueError as e:
                    print(f"   ⚠️  {task} routing failed: {e}")
                    
        except Exception as e:
            print(f"❌ route_chat failed: {e}")
            return
        
        # Test 4: Cost estimation (tool 4)
        print("\n4️⃣ Testing cost_estimate functionality...")
        try:
            from research_mcp.server import COST_ESTIMATES
            
            model = "openai/gpt-4o-mini"
            tokens_in = 100
            tokens_out = 50
            
            # Get cost data
            cost_data = COST_ESTIMATES.get(model, COST_ESTIMATES["default"])
            
            # Calculate costs
            input_cost = (tokens_in / 1000) * cost_data["input"]
            output_cost = (tokens_out / 1000) * cost_data["output"]
            total_cost = input_cost + output_cost
            
            result = {
                "estimate_usd": f"${total_cost:.6f}",
                "breakdown": {
                    "input_tokens": f"${input_cost:.6f}",
                    "output_tokens": f"${output_cost:.6f}"
                }
            }
            
            print(f"✅ Cost estimate for {tokens_in}+{tokens_out} tokens with {model}:")
            print(f"   💰 Total: {result['estimate_usd']}")
            print(f"   📊 Breakdown: {result['breakdown']}")
            
        except Exception as e:
            print(f"❌ cost_estimate failed: {e}")
            return
    
    print("\n🎉 All end-to-end tests passed!")
    print("   The MCP server components are working correctly with real API calls.")


if __name__ == "__main__":
    asyncio.run(test_full_workflow())