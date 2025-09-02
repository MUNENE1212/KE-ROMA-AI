import openai
from config.config import get_settings
import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from datetime import datetime
import google.generativeai as genai
from huggingface_hub import AsyncInferenceClient
import cohere
from enum import Enum

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

class AIService:
    # Provider status tracking
    _provider_status = {}
    _fallback_order = [AIProvider.GEMINI, AIProvider.OPENAI, AIProvider.HUGGINGFACE, AIProvider.COHERE, AIProvider.MOCK]
    
    @staticmethod
    async def generate_recipes(
        pantry_ingredients: List[str], 
        health_goals: List[str] = None, 
        is_premium: bool = False,
        preferred_provider: str = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Generate AI-powered recipe recommendations with multi-provider support"""
        
        if not pantry_ingredients:
            raise ValueError("At least one pantry ingredient is required")
        
        # Determine provider order
        provider_order = AIService._get_provider_order(preferred_provider)
        
        generation_info = {
            "providers_tried": [],
            "successful_provider": None,
            "fallback_used": False,
            "provider_statuses": {}
        }
        
        # Try each provider in order
        for provider in provider_order:
            try:
                print(f"Attempting recipe generation with {provider.value}...")
                generation_info["providers_tried"].append(provider.value)
                
                recipes = await AIService._generate_with_provider(
                    provider, pantry_ingredients, health_goals, is_premium
                )
                
                if recipes:
                    generation_info["successful_provider"] = provider.value
                    generation_info["fallback_used"] = provider != provider_order[0]
                    AIService._update_provider_status(provider, True)
                    return recipes, generation_info
                    
            except Exception as e:
                error_msg = str(e)
                print(f"{provider.value} failed: {error_msg}")
                AIService._update_provider_status(provider, False, error_msg)
                generation_info["provider_statuses"][provider.value] = {
                    "error": error_msg,
                    "quota_exceeded": "429" in error_msg or "quota" in error_msg.lower()
                }
                continue
        
        # If all providers fail, this shouldn't happen as MOCK should always work
        raise Exception("All AI providers failed to generate recipes")
    
    @staticmethod
    async def _generate_with_openai(client, pantry_ingredients: List[str], health_goals: List[str], is_premium: bool):
        """Generate recipes using OpenAI API"""
        # Build prompt based on user type and African cuisine focus
        ingredient_list = ", ".join(pantry_ingredients)
        health_context = f" with focus on {', '.join(health_goals)}" if health_goals else ""
        
        if is_premium:
            prompt = f"""You are a culinary expert specializing in authentic African cuisine. Generate 3 detailed, traditional African recipes using these available ingredients: {ingredient_list}{health_context}.

Focus on:
- Traditional African cooking methods and flavors
- Nutritional benefits of indigenous ingredients
- Cultural significance of the dishes
- Seasonal and locally available ingredients

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
            prompt = f"""Generate 3 simple, authentic African recipes using these ingredients: {ingredient_list}{health_context}.

Focus on traditional African dishes that are:
- Easy to prepare
- Use common African ingredients and cooking methods
- Nutritious and satisfying

For each recipe, provide:
Recipe Name: [African dish name]
Ingredients: [List with basic quantities]
Instructions: [Simple cooking steps]
Health Benefits: [Key nutritional benefits]

Separate each recipe with "---"."""
        
        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4" if is_premium else "gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert in African cuisine, specializing in traditional recipes from across the continent. Focus on authentic, culturally significant dishes."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000 if is_premium else 1200,
                temperature=0.7
            )
            
            # Parse the response
            recipes_text = response.choices[0].message.content
            recipes = AIService._parse_recipes(recipes_text, pantry_ingredients)
            
            return recipes
            
        except Exception as e:
            raise Exception(f"AI recipe generation failed: {str(e)}")
    
    @staticmethod
    def _parse_recipes(response_text: str, pantry_ingredients: List[str]) -> List[Dict[str, Any]]:
        """Parse OpenAI response into structured recipe data"""
        recipe_blocks = [block.strip() for block in response_text.split('---') if block.strip()]
        recipes = []
        
        for i, block in enumerate(recipe_blocks):
            recipe = {
                "name": f"African Recipe {i + 1}",
                "origin": "",
                "ingredients": [],
                "instructions": [],
                "health_benefits": "",
                "cultural_context": "",
                "cooking_time": "",
                "nutrition_info": {},
                "tags": ["african", "traditional"] + pantry_ingredients
            }
            
            lines = block.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if line.lower().startswith('recipe name:'):
                    recipe["name"] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('origin:'):
                    recipe["origin"] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('ingredients:'):
                    current_section = "ingredients"
                    content = line.split(':', 1)[1].strip()
                    if content:
                        current_content = [content]
                    else:
                        current_content = []
                elif line.lower().startswith('instructions:'):
                    if current_section == "ingredients" and current_content:
                        recipe["ingredients"] = AIService._parse_ingredients(current_content)
                    current_section = "instructions"
                    content = line.split(':', 1)[1].strip()
                    if content:
                        current_content = [content]
                    else:
                        current_content = []
                elif line.lower().startswith('health benefits:'):
                    if current_section == "instructions" and current_content:
                        recipe["instructions"] = current_content
                    current_section = "health_benefits"
                    recipe["health_benefits"] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('cultural context:'):
                    recipe["cultural_context"] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('cooking time:'):
                    recipe["cooking_time"] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('nutrition info:'):
                    nutrition_text = line.split(':', 1)[1].strip()
                    recipe["nutrition_info"] = AIService._parse_nutrition(nutrition_text)
                else:
                    # Continue current section
                    if current_section and line:
                        current_content.append(line)
            
            # Handle last section
            if current_section == "ingredients" and current_content:
                recipe["ingredients"] = AIService._parse_ingredients(current_content)
            elif current_section == "instructions" and current_content:
                recipe["instructions"] = current_content
            
            recipes.append(recipe)
        
        return recipes
    
    @staticmethod
    def _parse_ingredients(ingredient_lines: List[str]) -> List[str]:
        """Parse ingredient lines into a clean list"""
        ingredients = []
        for line in ingredient_lines:
            # Split by common delimiters and clean up
            items = re.split(r'[,\n•\-\*]', line)
            for item in items:
                item = item.strip()
                if item and not item.startswith(('Recipe', 'Ingredients:')):
                    ingredients.append(item)
        return ingredients
    
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
    def _generate_mock_recipes(pantry_ingredients: List[str], health_goals: List[str], is_premium: bool) -> List[Dict[str, Any]]:
        """Generate mock African recipes when OpenAI quota is exceeded"""
        
        ingredient_list = ", ".join(pantry_ingredients)
        
        mock_recipes = [
            {
                "name": f"Jollof Rice with {pantry_ingredients[0] if pantry_ingredients else 'Vegetables'}",
                "origin": "West Africa",
                "ingredients": [
                    "2 cups jasmine rice",
                    "1 can diced tomatoes",
                    "1 large onion, diced",
                    "3 cloves garlic, minced"
                ] + [f"1 cup {ing}" for ing in pantry_ingredients[:3]],
                "instructions": [
                    "Heat oil in a large pot over medium heat",
                    "Sauté onions until golden brown",
                    "Add garlic and cook for 1 minute",
                    "Add tomatoes and selected ingredients",
                    "Add rice and stock, bring to boil",
                    "Reduce heat, cover and simmer for 20-25 minutes",
                    "Let stand 5 minutes before serving"
                ],
                "cooking_time": "45 minutes",
                "health_benefits": "Rich in complex carbohydrates, provides sustained energy, contains antioxidants from tomatoes",
                "cultural_context": "Jollof rice is a beloved West African dish, often served at celebrations and family gatherings",
                "nutrition_info": {
                    "calories": 420,
                    "protein": "12g",
                    "fiber": "8g",
                    "vitamin_c": "25mg"
                } if is_premium else None
            },
            {
                "name": f"Ethiopian Spiced Lentils with {pantry_ingredients[1] if len(pantry_ingredients) > 1 else 'Herbs'}",
                "origin": "Ethiopia",
                "ingredients": [
                    "1 cup red lentils",
                    "2 tbsp berbere spice blend",
                    "1 large onion, chopped",
                    "3 cloves garlic, minced"
                ] + [f"1/2 cup {ing}" for ing in pantry_ingredients[:2]],
                "instructions": [
                    "Rinse lentils and set aside",
                    "Sauté onions until soft and golden",
                    "Add garlic and berbere spice, cook 1 minute",
                    "Add selected ingredients and lentils",
                    "Add 3 cups water, bring to boil",
                    "Simmer 20-25 minutes until lentils are tender",
                    "Season with salt and serve hot"
                ],
                "cooking_time": "35 minutes",
                "health_benefits": "High in plant protein and fiber, supports digestive health, rich in iron and folate",
                "cultural_context": "Misir wot is a staple Ethiopian dish, traditionally served with injera bread",
                "nutrition_info": {
                    "calories": 280,
                    "protein": "18g",
                    "fiber": "12g",
                    "iron": "6mg"
                } if is_premium else None
            },
            {
                "name": f"Kenyan Sukuma Wiki with {pantry_ingredients[0] if pantry_ingredients else 'Onions'}",
                "origin": "Kenya",
                "ingredients": [
                    "1 bunch collard greens (sukuma wiki)",
                    "2 medium tomatoes, chopped",
                    "1 large onion, sliced",
                    "2 cloves garlic, minced"
                ] + [f"1/2 cup {ing}" for ing in pantry_ingredients[:2]],
                "instructions": [
                    "Wash and chop collard greens into strips",
                    "Heat oil in a large pan",
                    "Sauté onions until translucent",
                    "Add garlic and selected ingredients",
                    "Add tomatoes, cook until soft",
                    "Add collard greens, stir well",
                    "Cover and cook 10-15 minutes until tender"
                ],
                "cooking_time": "25 minutes",
                "health_benefits": "Excellent source of vitamins A, C, and K, supports immune system and bone health",
                "cultural_context": "Sukuma wiki means 'push the week' in Swahili, a nutritious and affordable daily meal",
                "nutrition_info": {
                    "calories": 150,
                    "protein": "8g",
                    "fiber": "6g",
                    "vitamin_a": "200% DV"
                } if is_premium else None
            }
        ]
        
        return mock_recipes
