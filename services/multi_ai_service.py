import os
import logging
import time
import re
import asyncio
from typing import List, Dict, Any, Tuple
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv

import google.generativeai as genai
from openai import AsyncOpenAI
from huggingface_hub import AsyncInferenceClient
import cohere

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    MOCK = "mock"

class AIProviderStatus:
    def __init__(self, provider: AIProvider, available: bool, quota_remaining: bool = True, error: str = None):
        self.provider = provider
        self.available = available
        self.quota_remaining = quota_remaining
        self.error = error
        self.last_checked = datetime.utcnow()

class MultiAIService:
    # Provider status tracking
    _provider_status = {}
    _fallback_order = [AIProvider.GEMINI, AIProvider.OPENAI, AIProvider.HUGGINGFACE, AIProvider.COHERE, AIProvider.MOCK]
    _provider_pricing = {
        AIProvider.OPENAI: {"cost_per_request": 0.05, "premium_only": False},
        AIProvider.GEMINI: {"cost_per_request": 0.02, "premium_only": False},
        AIProvider.HUGGINGFACE: {"cost_per_request": 0.01, "premium_only": False},
        AIProvider.COHERE: {"cost_per_request": 0.03, "premium_only": True},
        AIProvider.MOCK: {"cost_per_request": 0.00, "premium_only": False}
    }
    
    @staticmethod
    async def generate_recipes(
        pantry_ingredients: List[str],
        health_goals: List[str] = None,
        is_premium: bool = False,
        preferred_provider: str = None,
        user_data: Any = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Generate AI-powered recipe recommendations with multi-provider support"""
        
        if not pantry_ingredients:
            raise ValueError("At least one pantry ingredient is required")
        
        # Determine provider order
        provider_order = MultiAIService._get_provider_order(preferred_provider)
        
        generation_info = {
            "providers_tried": [],
            "successful_provider": None,
            "fallback_used": False,
            "provider_statuses": {},
            "generation_time": 0,
            "quota_info": {}
        }
        
        start_time = datetime.utcnow()
        
        # Try each provider in order
        for provider in provider_order:
            try:
                print(f"Attempting recipe generation with {provider.value}...")
                generation_info["providers_tried"].append(provider.value)
                
                recipes = await MultiAIService._generate_with_provider(
                    provider, pantry_ingredients, health_goals, is_premium, user_data
                )
                
                if recipes:
                    generation_info["successful_provider"] = provider.value
                    generation_info["fallback_used"] = provider != provider_order[0]
                    generation_info["generation_time"] = (datetime.utcnow() - start_time).total_seconds()
                    MultiAIService._update_provider_status(provider, True)
                    return recipes, generation_info
                    
            except Exception as e:
                error_msg = str(e)
                print(f"{provider.value} failed: {error_msg}")
                MultiAIService._update_provider_status(provider, False, error_msg)
                generation_info["provider_statuses"][provider.value] = {
                    "error": error_msg,
                    "quota_exceeded": "429" in error_msg or "quota" in error_msg.lower()
                }
                continue
        
        # If all providers fail, this shouldn't happen as MOCK should always work
        raise Exception("All AI providers failed to generate recipes")
    
    @staticmethod
    def _get_provider_order(preferred_provider: str = None) -> List[AIProvider]:
        """Get the order of providers to try based on preference and availability"""
        default_provider = os.getenv("DEFAULT_AI_PROVIDER", "gemini")
        
        if preferred_provider:
            try:
                preferred = AIProvider(preferred_provider.lower())
                # Put preferred provider first, then follow default order
                order = [preferred] + [p for p in MultiAIService._fallback_order if p != preferred]
                return order
            except ValueError:
                pass
        
        # Use default provider first
        try:
            default = AIProvider(default_provider.lower())
            order = [default] + [p for p in MultiAIService._fallback_order if p != default]
            return order
        except ValueError:
            return MultiAIService._fallback_order
    
    @staticmethod
    async def _generate_with_provider(
        provider: AIProvider,
        pantry_ingredients: List[str],
        health_goals: List[str],
        is_premium: bool,
        user_data: Any = None
    ) -> List[Dict[str, Any]]:
        """Generate recipes using the specified provider"""
        
        if provider == AIProvider.OPENAI:
            return await MultiAIService._generate_with_openai(pantry_ingredients, health_goals, is_premium, user_data)
        elif provider == AIProvider.GEMINI:
            return await MultiAIService._generate_with_gemini(pantry_ingredients, health_goals, is_premium, user_data)
        elif provider == AIProvider.HUGGINGFACE:
            return await MultiAIService._generate_with_huggingface(pantry_ingredients, health_goals, is_premium, user_data)
        elif provider == AIProvider.COHERE:
            return await MultiAIService._generate_with_cohere(pantry_ingredients, health_goals, is_premium, user_data)
        elif provider == AIProvider.MOCK:
            return MultiAIService._generate_mock_recipes(pantry_ingredients, health_goals, is_premium, user_data)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @staticmethod
    async def generate_chat_response(prompt: str, preferred_provider: str = "auto", user_id: str = None) -> Dict[str, Any]:
        """Generate a chat response using the multi-AI service"""
        start_time = time.time()
        providers_tried = []
        
        # Get provider order
        provider_order = MultiAIService._get_provider_order(preferred_provider)
        
        for provider in provider_order:
            try:
                providers_tried.append(provider.value)
                logger.info(f"Attempting chat response with {provider.value}")
                
                if provider == AIProvider.OPENAI:
                    response = await MultiAIService._generate_openai_chat(prompt)
                elif provider == AIProvider.GEMINI:
                    response = await MultiAIService._generate_gemini_chat(prompt)
                elif provider == AIProvider.HUGGINGFACE:
                    response = await MultiAIService._generate_huggingface_chat(prompt)
                elif provider == AIProvider.COHERE:
                    response = await MultiAIService._generate_cohere_chat(prompt)
                elif provider == AIProvider.MOCK:
                    response = MultiAIService._generate_mock_chat(prompt)
                else:
                    continue
                
                generation_time = time.time() - start_time
                
                return {
                    "response": response,
                    "successful_provider": provider.value,
                    "generation_time": generation_time,
                    "providers_tried": providers_tried,
                    "fallback_used": len(providers_tried) > 1
                }
                
            except Exception as e:
                logger.warning(f"Chat failed with {provider.value}: {str(e)}")
                continue
        
        # All providers failed, return mock response
        generation_time = time.time() - start_time
        mock_response = MultiAIService._generate_mock_chat(prompt)
        
        return {
            "response": mock_response,
            "successful_provider": "mock",
            "generation_time": generation_time,
            "providers_tried": providers_tried,
            "fallback_used": True
        }

    @staticmethod
    async def _generate_openai_chat(prompt: str) -> str:
        """Generate chat response using OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not configured")
        
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()

    @staticmethod
    async def _generate_gemini_chat(prompt: str) -> str:
        """Generate chat response using Google Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("Gemini API key not configured")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        response = await model.generate_content_async(prompt)
        return response.text.strip()

    @staticmethod
    async def _generate_huggingface_chat(prompt: str) -> str:
        """Generate chat response using Hugging Face API"""
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise Exception("Hugging Face API key not configured")
        
        from huggingface_hub import AsyncInferenceClient
        client = AsyncInferenceClient(token=api_key)
        
        response = await client.text_generation(
            prompt=prompt,
            model="microsoft/DialoGPT-medium",
            max_new_tokens=300,
            temperature=0.7
        )
        
        return response.strip()

    @staticmethod
    async def _generate_cohere_chat(prompt: str) -> str:
        """Generate chat response using Cohere API"""
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise Exception("Cohere API key not configured")
        
        import cohere
        co = cohere.AsyncClient(api_key)
        
        response = await co.generate(
            model='command',
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        return response.generations[0].text.strip()

    @staticmethod
    def _generate_mock_chat(prompt: str) -> str:
        """Generate mock chat response for fallback"""
        responses = [
            "That's a great question about African cuisine! I'd recommend trying jollof rice - it's a beloved West African dish that's both flavorful and nutritious.",
            "For authentic African cooking, I suggest exploring traditional spices like berbere from Ethiopia or harissa from North Africa. They add incredible depth to dishes!",
            "Have you tried making ugali? It's a staple food in East Africa that pairs wonderfully with stews and vegetables.",
            "African cuisine offers so many healthy options! Consider dishes with leafy greens like sukuma wiki or moringa leaves - they're packed with nutrients.",
            "For a quick African-inspired meal, try making a simple groundnut stew with peanut butter, vegetables, and your choice of protein.",
            "Traditional African fermented foods like injera bread or fermented porridge are great for gut health and have unique flavors!"
        ]
        
        import random
        return random.choice(responses)

    @staticmethod
    async def _generate_with_openai(pantry_ingredients: List[str], health_goals: List[str], is_premium: bool, user_data: Any = None):
        """Generate recipes using OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not configured")

        client = AsyncOpenAI(api_key=api_key)
        prompt = MultiAIService._build_african_recipe_prompt(pantry_ingredients, health_goals, is_premium, user_data=user_data)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )

        return MultiAIService._parse_recipe_response(response.choices[0].message.content, is_premium)
    
    @staticmethod
    async def _generate_with_gemini(pantry_ingredients: List[str], health_goals: List[str], is_premium: bool, user_data: Any = None):
        """Generate recipes using Google Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("Gemini API key not configured")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = MultiAIService._build_african_recipe_prompt(pantry_ingredients, health_goals, is_premium, user_data=user_data)

        response = await asyncio.to_thread(model.generate_content, prompt)
        return MultiAIService._parse_recipe_response(response.text, is_premium)
    
    @staticmethod
    async def _generate_with_huggingface(pantry_ingredients: List[str], health_goals: List[str], is_premium: bool, user_data: Any = None):
        """Generate recipes using Hugging Face API"""
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise Exception("Hugging Face API key not configured")

        client = AsyncInferenceClient(token=api_key)
        prompt = MultiAIService._build_african_recipe_prompt(pantry_ingredients, health_goals, is_premium, max_length=800, user_data=user_data)

        response = await client.text_generation(
            prompt=prompt,
            model="microsoft/DialoGPT-large",
            max_new_tokens=1500,
            temperature=0.7
        )

        return MultiAIService._parse_recipe_response(response, is_premium)
    
    @staticmethod
    async def _generate_with_cohere(pantry_ingredients: List[str], health_goals: List[str], is_premium: bool, user_data: Any = None):
        """Generate recipes using Cohere API"""
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise Exception("Cohere API key not configured")

        co = cohere.AsyncClient(api_key)
        prompt = MultiAIService._build_african_recipe_prompt(pantry_ingredients, health_goals, is_premium, user_data=user_data)

        response = await co.generate(
            model='command',
            prompt=prompt,
            max_tokens=1500,
            temperature=0.7
        )

        return MultiAIService._parse_recipe_response(response.generations[0].text, is_premium)
    
    @staticmethod
    def _build_african_recipe_prompt(pantry_ingredients: List[str], health_goals: List[str], is_premium: bool, max_length: int = None, user_data: Any = None):
        """Build a comprehensive prompt for African recipe generation with user personalization"""
        ingredient_list = ", ".join(pantry_ingredients)
        health_context = f" with focus on {', '.join(health_goals)}" if health_goals else ""

        # Build user personalization context
        user_context = ""
        if user_data:
            user_context_parts = []

            # Add user's saved recipes for personalization
            if hasattr(user_data, 'saved_recipes') and user_data.saved_recipes:
                user_context_parts.append(f"User has previously saved {len(user_data.saved_recipes)} recipes, suggesting they enjoy diverse African cuisine")

            # Add user's health goals
            if hasattr(user_data, 'health_goals') and user_data.health_goals:
                user_health_goals = ", ".join(user_data.health_goals)
                user_context_parts.append(f"User's health goals include: {user_health_goals}")

            # Add user's pantry preferences
            if hasattr(user_data, 'pantry') and user_data.pantry:
                user_pantry = ", ".join(user_data.pantry)
                user_context_parts.append(f"User typically has these ingredients available: {user_pantry}")

            if user_context_parts:
                user_context = "\n\nUser Preferences:\n" + "\n".join(f"- {part}" for part in user_context_parts)

        if is_premium:
            prompt = f"""You are a culinary expert specializing in authentic African cuisine. Generate 3 detailed, traditional African recipes using these available ingredients: {ingredient_list}{health_context}.{user_context}

Focus on:
- Traditional African cooking methods and flavors
- Nutritional benefits of indigenous ingredients
- Cultural significance of the dishes
- Seasonal and locally available ingredients
- Personalization based on user's preferences and history

For each recipe, provide:
Recipe Name: [Traditional African dish name]
Origin: [Country/region of origin]
Ingredients: [Complete list with quantities, emphasizing African staples]
Instructions: [Detailed step-by-step cooking method]
Health Benefits: [Specific nutritional advantages and medicinal properties]
Cultural Context: [Brief history or cultural significance]
Cooking Time: [Prep and total cooking time]
Nutrition Info: [Estimated calories, protein, fiber, key vitamins]

Format each recipe clearly and separate with "---"."""

        else:
            prompt = f"""Generate 3 simple, authentic African recipes using these ingredients: {ingredient_list}{health_context}.{user_context}

Focus on traditional African dishes that are:
- Easy to prepare
- Use common African ingredients and cooking methods
- Nutritious and satisfying
- Personalized to user's preferences when possible

For each recipe, provide:
Recipe Name: [African dish name]
Origin: [Country/region]
Ingredients: [List with basic quantities]
Instructions: [Simple cooking steps]
Health Benefits: [Key nutritional benefits]
Cultural Context: [Brief cultural note]
Cooking Time: [Total time]

Separate each recipe with "---"."""

        if max_length and len(prompt) > max_length:
            # Simplified prompt for providers with token limits
            simplified_user_context = ""
            if user_data and hasattr(user_data, 'health_goals') and user_data.health_goals:
                simplified_user_context = f" User prefers: {', '.join(user_data.health_goals[:2])}"

            prompt = f"Create 3 African recipes using {ingredient_list}.{simplified_user_context} Include name, origin, ingredients, instructions, and cooking time for each. Separate with ---."

        return prompt
    
    @staticmethod
    def _parse_recipe_response(response_text: str, is_premium: bool) -> List[Dict[str, Any]]:
        """Parse AI response into structured recipe data"""
        recipes = []
        recipe_sections = response_text.split("---")
        
        for section in recipe_sections[:3]:  # Limit to 3 recipes
            if not section.strip():
                continue
                
            recipe = MultiAIService._extract_recipe_data(section.strip(), is_premium)
            if recipe:
                recipes.append(recipe)
        
        # If parsing fails, return mock recipes
        if not recipes:
            return MultiAIService._generate_mock_recipes(["rice", "tomatoes"], [], is_premium)
        
        return recipes
    
    @staticmethod
    def _extract_recipe_data(recipe_text: str, is_premium: bool) -> Dict[str, Any]:
        """Extract structured data from recipe text"""
        recipe = {
            "name": "African Recipe",
            "origin": "Africa",
            "ingredients": [],
            "instructions": [],
            "health_benefits": "Nutritious and delicious",
            "cultural_context": "Traditional African cuisine",
            "cooking_time": "30 minutes",
            "nutrition_info": None,
            "tags": []
        }
        
        # Extract recipe name
        name_match = re.search(r'(?:Recipe Name|Name):\s*(.+)', recipe_text, re.IGNORECASE)
        if name_match:
            recipe["name"] = name_match.group(1).strip()
        
        # Extract origin
        origin_match = re.search(r'Origin:\s*(.+)', recipe_text, re.IGNORECASE)
        if origin_match:
            recipe["origin"] = origin_match.group(1).strip()
        
        # Extract ingredients
        ingredients_match = re.search(r'Ingredients?:\s*(.*?)(?=Instructions?:|Health Benefits:|$)', recipe_text, re.IGNORECASE | re.DOTALL)
        if ingredients_match:
            ingredients_text = ingredients_match.group(1).strip()
            recipe["ingredients"] = [ing.strip() for ing in re.split(r'[-•\n]', ingredients_text) if ing.strip()]
        
        # Extract instructions
        instructions_match = re.search(r'Instructions?:\s*(.*?)(?=Health Benefits:|Cultural Context:|Cooking Time:|$)', recipe_text, re.IGNORECASE | re.DOTALL)
        if instructions_match:
            instructions_text = instructions_match.group(1).strip()
            recipe["instructions"] = [inst.strip() for inst in re.split(r'[-•\n]|\d+\.', instructions_text) if inst.strip()]
        
        # Extract health benefits
        health_match = re.search(r'Health Benefits?:\s*(.*?)(?=Cultural Context:|Cooking Time:|Nutrition Info:|$)', recipe_text, re.IGNORECASE | re.DOTALL)
        if health_match:
            recipe["health_benefits"] = health_match.group(1).strip()
        
        # Extract cultural context
        culture_match = re.search(r'Cultural Context:\s*(.*?)(?=Cooking Time:|Nutrition Info:|$)', recipe_text, re.IGNORECASE | re.DOTALL)
        if culture_match:
            recipe["cultural_context"] = culture_match.group(1).strip()
        
        # Extract cooking time
        time_match = re.search(r'Cooking Time:\s*(.*?)(?=Nutrition Info:|$)', recipe_text, re.IGNORECASE)
        if time_match:
            recipe["cooking_time"] = time_match.group(1).strip()
        
        # Extract nutrition info for premium users
        if is_premium:
            nutrition_match = re.search(r'Nutrition Info:\s*(.*?)$', recipe_text, re.IGNORECASE | re.DOTALL)
            if nutrition_match:
                recipe["nutrition_info"] = MultiAIService._parse_nutrition(nutrition_match.group(1).strip())
        
        return recipe
    
    @staticmethod
    def _parse_nutrition(nutrition_text: str) -> Dict[str, Any]:
        """Parse nutrition information into structured data"""
        nutrition = {}
        
        # Extract calories
        calories_match = re.search(r'(\d+)\s*calories?', nutrition_text, re.IGNORECASE)
        if calories_match:
            nutrition["calories"] = int(calories_match.group(1))
        
        # Extract protein
        protein_match = re.search(r'(\d+)g?\s*protein', nutrition_text, re.IGNORECASE)
        if protein_match:
            nutrition["protein"] = f"{protein_match.group(1)}g"
        
        # Extract fiber
        fiber_match = re.search(r'(\d+)g?\s*fiber', nutrition_text, re.IGNORECASE)
        if fiber_match:
            nutrition["fiber"] = f"{fiber_match.group(1)}g"
        
        return nutrition
    
    @staticmethod
    def _generate_mock_recipes(pantry_ingredients: List[str], health_goals: List[str], is_premium: bool, user_data: Any = None) -> List[Dict[str, Any]]:
        """Generate mock African recipes when all AI providers fail - using dynamic generation"""
        try:
            # Try to generate recipes dynamically using the multi-AI service
            recipes, _ = asyncio.run(MultiAIService.generate_recipes(
                pantry_ingredients=pantry_ingredients,
                health_goals=health_goals,
                is_premium=is_premium
            ))
            return recipes
        except Exception as e:
            print(f"Dynamic mock recipe generation failed: {e}")
            # Fallback to very basic generic recipes
            return [
                {
                    "name": f"Simple {pantry_ingredients[0] if pantry_ingredients else 'Ingredient'} Dish",
                    "origin": "African",
                    "ingredients": pantry_ingredients[:5] if pantry_ingredients else ["Basic ingredients"],
                    "instructions": ["Prepare ingredients", "Cook according to traditional methods", "Serve hot"],
                    "cooking_time": "30 minutes",
                    "health_benefits": "Provides essential nutrients",
                    "cultural_context": "Traditional African cooking",
                    "nutrition_info": None,
                    "tags": ["african", "traditional"]
                }
            ]
    
    @staticmethod
    def _update_provider_status(provider: AIProvider, success: bool, error: str = None):
        """Update the status of a provider"""
        MultiAIService._provider_status[provider] = AIProviderStatus(
            provider=provider,
            available=success,
            quota_remaining="quota" not in (error or "").lower(),
            error=error
        )
    
    @staticmethod
    def get_provider_statuses() -> Dict[str, Dict[str, Any]]:
        """Get current status of all providers"""
        statuses = {}
        for provider in AIProvider:
            status = MultiAIService._provider_status.get(provider)
            pricing = MultiAIService._provider_pricing.get(provider, {})
            
            if status:
                statuses[provider.value] = {
                    "available": status.available,
                    "quota_remaining": status.quota_remaining,
                    "error": status.error,
                    "last_checked": status.last_checked.isoformat(),
                    "cost_per_request": pricing.get("cost_per_request", 0),
                    "premium_only": pricing.get("premium_only", False),
                    "display_name": provider.value.title()
                }
            else:
                statuses[provider.value] = {
                    "available": False,
                    "quota_remaining": False,
                    "error": "Not initialized",
                    "last_checked": None,
                    "cost_per_request": pricing.get("cost_per_request", 0),
                    "premium_only": pricing.get("premium_only", False),
                    "display_name": provider.value.title()
                }
        return statuses
    
    @staticmethod
    async def check_all_providers() -> Dict[str, Dict[str, Any]]:
        """Check status of all AI providers"""
        for provider in AIProvider:
            try:
                await MultiAIService._check_provider_status(provider)
            except Exception as e:
                logger.error(f"Error checking {provider.value} status: {e}")
                MultiAIService._provider_status[provider] = AIProviderStatus(
                    provider, False, False, str(e)
                )
        
        return MultiAIService.get_provider_statuses()
    
    @staticmethod
    async def _check_provider_status(provider: AIProvider):
        """Check individual provider status"""
        try:
            if provider == AIProvider.OPENAI:
                client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                await client.models.list()
                MultiAIService._provider_status[provider] = AIProviderStatus(provider, True, True)
            
            elif provider == AIProvider.GEMINI:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                model = genai.GenerativeModel('gemini-pro')
                MultiAIService._provider_status[provider] = AIProviderStatus(provider, True, True)
            
            elif provider == AIProvider.HUGGINGFACE:
                client = AsyncInferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
                MultiAIService._provider_status[provider] = AIProviderStatus(provider, True, True)
            
            elif provider == AIProvider.COHERE:
                client = cohere.AsyncClient(api_key=os.getenv("COHERE_API_KEY"))
                MultiAIService._provider_status[provider] = AIProviderStatus(provider, True, True)
            
            elif provider == AIProvider.MOCK:
                MultiAIService._provider_status[provider] = AIProviderStatus(provider, True, True)
                
        except Exception as e:
            MultiAIService._provider_status[provider] = AIProviderStatus(
                provider, False, False, str(e)
            )
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of providers with valid API keys"""
        available = []
        
        if os.getenv("OPENAI_API_KEY"):
            available.append("openai")
        if os.getenv("GEMINI_API_KEY"):
            available.append("gemini")
        if os.getenv("HUGGINGFACE_API_KEY"):
            available.append("huggingface")
        if os.getenv("COHERE_API_KEY"):
            available.append("cohere")
        
        available.append("mock")  # Always available
        return available
