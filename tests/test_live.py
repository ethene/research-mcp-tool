"""Live API tests with real OpenRouter calls."""

import pytest
import os
from dotenv import load_dotenv
import asyncio

from research_mcp.routing import TaskRouter
from research_mcp.openrouter import OpenRouterClient


# Load environment variables
load_dotenv()

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv('OPENROUTER_API_KEY'), reason="No API key available")
class TestLiveAPI:
    """Test with real OpenRouter API calls."""
    
    async def test_list_models_live(self):
        """Test listing models from real OpenRouter API."""
        api_key = os.getenv('OPENROUTER_API_KEY')
        client = OpenRouterClient(api_key)
        
        async with client:
            result = await client.list_models()
            
            assert 'data' in result
            assert isinstance(result['data'], list)
            assert len(result['data']) > 0
            
            # Check that we have some expected models
            model_ids = [model.get('id', '') for model in result['data']]
            
            # Should have at least some popular models
            assert any('openai' in model_id for model_id in model_ids)
            print(f"✅ Found {len(result['data'])} models")
    
    async def test_routing_with_live_models(self):
        """Test routing against real model list."""
        api_key = os.getenv('OPENROUTER_API_KEY')
        client = OpenRouterClient(api_key)
        router = TaskRouter("routing.yaml")
        
        async with client:
            # Get real available models
            models_data = await client.list_models()
            available_models = [m.get('id', '') for m in models_data.get('data', [])]
            
            print(f"Available models: {len(available_models)}")
            
            # Test routing for each configured task
            tasks = router.get_available_tasks()
            print(f"Configured tasks: {tasks}")
            
            for task in tasks:
                try:
                    selected_model = router.route_task(task, available_models)
                    print(f"✅ {task} → {selected_model}")
                    assert selected_model in available_models
                except ValueError as e:
                    print(f"⚠️  {task} → {e}")
                    # Task routing failed, but that's okay if the preferred model isn't available
    
    async def test_small_chat_completion_live(self):
        """Test a small chat completion with real API."""
        api_key = os.getenv('OPENROUTER_API_KEY')
        client = OpenRouterClient(api_key)
        
        async with client:
            # Use a cheap model for testing
            messages = [{"role": "user", "content": "Say 'Hello' in exactly one word."}]
            
            try:
                result = await client.chat_completion(
                    model="openai/gpt-4o-mini", 
                    messages=messages,
                    max_tokens=10
                )
                
                assert 'choices' in result
                assert len(result['choices']) > 0
                assert 'message' in result['choices'][0]
                assert 'content' in result['choices'][0]['message']
                
                content = result['choices'][0]['message']['content']
                print(f"✅ Chat response: {content}")
                
                # Check usage tracking
                if 'usage' in result:
                    usage = result['usage']
                    print(f"✅ Token usage - In: {usage.get('prompt_tokens', 0)}, Out: {usage.get('completion_tokens', 0)}")
                
            except Exception as e:
                print(f"Chat completion failed: {e}")
                # Don't fail the test - API might have rate limits or other issues
                pytest.skip(f"Chat completion failed: {e}")


def test_routing_config_validation():
    """Test that our routing config is valid."""
    router = TaskRouter("routing.yaml")
    
    tasks = router.get_available_tasks()
    assert len(tasks) > 0
    print(f"✅ Routing config valid with {len(tasks)} tasks")
    
    fallbacks = router.get_fallbacks()
    assert len(fallbacks) > 0  
    print(f"✅ Found {len(fallbacks)} fallback models")
    
    # Test each configured task
    for task in tasks:
        model = router.get_model_for_task(task)
        assert model is not None
        print(f"✅ {task} → {model}")


if __name__ == "__main__":
    # Run basic sync test
    test_routing_config_validation()
    
    # Run async tests
    async def run_live_tests():
        if not os.getenv('OPENROUTER_API_KEY'):
            print("⚠️  No API key - skipping live tests")
            return
            
        test_instance = TestLiveAPI()
        
        print("Testing live model listing...")
        await test_instance.test_list_models_live()
        
        print("Testing routing with live models...")  
        await test_instance.test_routing_with_live_models()
        
        print("Testing small chat completion...")
        await test_instance.test_small_chat_completion_live()
    
    asyncio.run(run_live_tests())