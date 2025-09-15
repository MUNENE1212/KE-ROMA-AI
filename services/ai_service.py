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
        """Generate mock African recipes when all AI providers fail - using dynamic generation"""
        try:
            # Try to generate recipes dynamically using the multi-AI service
            from services.multi_ai_service import MultiAIService
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
                    "nutrition_info": None
                }
            ]
