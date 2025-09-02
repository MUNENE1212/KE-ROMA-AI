#!/usr/bin/env python3
"""
Test script for KE-ROUMA AI and Payment integrations
"""
import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from services.multi_ai_service import MultiAIService
from services.intasend_service import IntaSendService
from config.config import get_settings

def test_configuration():
    """Test configuration loading"""
    settings = get_settings()
    # Basic configuration should be loaded
    assert settings is not None

@pytest.mark.asyncio
async def test_multi_ai_service():
    """Test Multi AI service integration"""
    # Test provider status
    providers = MultiAIService.get_provider_status()
    assert isinstance(providers, dict)
    assert len(providers) > 0
    
    # Test available providers
    available = MultiAIService.get_available_providers()
    assert isinstance(available, list)

@pytest.mark.asyncio
async def test_recipe_generation_fallback():
    """Test recipe generation with fallback"""
    ingredients = ["tomatoes", "onions", "rice"]
    
    # This should work with mock fallback even without API keys
    recipes, metadata = await MultiAIService.generate_recipes(
        pantry_ingredients=ingredients,
        preferred_provider="mock"
    )
    
    assert len(recipes) > 0
    assert "name" in recipes[0]
    assert "ingredients" in recipes[0]
    assert metadata["provider_used"] == "mock"

@pytest.mark.asyncio
async def test_chat_response():
    """Test chat response generation"""
    response = await MultiAIService.generate_chat_response(
        prompt="What's a good recipe for dinner?",
        preferred_provider="mock"
    )
    
    assert "response" in response
    assert "provider_used" in response

@pytest.mark.skip(reason="Requires IntaSend API keys")
@pytest.mark.asyncio
async def test_payment_service():
    """Test payment service integration"""
    payment_service = IntaSendService()
    
    # Test payment initiation (mock)
    result = await payment_service.initiate_payment(
        amount=100,
        phone_number="254700000000",
        email="test@example.com"
    )
    
    assert "invoice_id" in result

def test_environment_variables():
    """Test that required environment variables are documented"""
    env_example_path = ".env.example"
    assert os.path.exists(env_example_path)
    
    with open(env_example_path, 'r') as f:
        content = f.read()
        
    # Check for required variables
    required_vars = [
        "MONGODB_URL",
        "JWT_SECRET_KEY",
        "OPENAI_API_KEY",
        "INTASEND_PUBLISHABLE_KEY"
    ]
    
    for var in required_vars:
        assert var in content, f"Missing {var} in .env.example"

async def test_api_endpoints():
    """Test API endpoints with curl commands"""
    print("\n🌐 Testing API Endpoints...")
    
    import subprocess
    
    endpoints = [
        ("Health Check", "http://localhost:8000/health"),
        ("App Info", "http://localhost:8000/info"),
        ("Home Page", "http://localhost:8000/"),
    ]
    
    for name, url in endpoints:
        try:
            result = subprocess.run(
                ["curl", "-s", "-w", "%{http_code}", url],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                status_code = result.stdout[-3:]  # Last 3 chars are status code
                if status_code.startswith("2"):  # 2xx success
                    print(f"   ✅ {name}: HTTP {status_code}")
                else:
                    print(f"   ❌ {name}: HTTP {status_code}")
            else:
                print(f"   ❌ {name}: Connection failed")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  {name}: Timeout")
        except Exception as e:
            print(f"   ❌ {name}: {str(e)}")

def create_sample_env():
    """Create a sample .env file if it doesn't exist"""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print("\n📝 Creating sample .env file...")
        
        sample_env = """# KE-ROUMA Environment Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=kerouma

# Get your OpenAI API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Get IntaSend keys from: https://developers.intasend.com/
INTASEND_PUBLISHABLE_KEY=your_intasend_publishable_key_here
INTASEND_SECRET_KEY=your_intasend_secret_key_here
INTASEND_BASE_URL=https://sandbox.intasend.com/api/v1

SECRET_KEY=kerouma-secret-key-change-in-production
DEBUG=true
PREMIUM_PRICE=100
"""
        
        with open(env_path, 'w') as f:
            f.write(sample_env)
        
        print("   ✅ Created .env file")
        print("   💡 Please add your actual API keys to enable full functionality")

async def main():
    """Run all integration tests"""
    print("🍽️  KE-ROUMA Integration Tests\n")
    print("=" * 50)
    
    # Create sample .env if needed
    create_sample_env()
    
    # Test configuration
    config_ok = test_configuration()
    
    # Test API endpoints
    await test_api_endpoints()
    
    # Test AI service
    ai_ok = await test_ai_service()
    
    # Test payment service
    payment_ok = await test_payment_service()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Configuration: {'✅' if config_ok else '⚠️'}")
    print(f"   AI Service: {'✅' if ai_ok else '⚠️'}")
    print(f"   Payment Service: {'✅' if payment_ok else '⚠️'}")
    
    if not (ai_ok and payment_ok):
        print("\n💡 Next Steps:")
        print("   1. Copy .env.local to .env")
        print("   2. Add your OpenAI API key")
        print("   3. Add your IntaSend API keys")
        print("   4. Run this test again")
    else:
        print("\n🎉 All integrations working correctly!")

if __name__ == "__main__":
    asyncio.run(main())
