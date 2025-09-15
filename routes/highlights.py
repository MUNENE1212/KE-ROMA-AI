from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from models.database import get_database
from services.ai_service import AIService
import json
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI()

class HighlightsService:
    """Service for managing highlight recipes with MongoDB"""
    
    @staticmethod
    async def generate_highlights() -> Dict[str, Any]:
        """Generate and save highlight recipes"""
        try:
            ai_service = AIService()
            
            # Generate 6 diverse highlight recipes
            highlight_categories = [
                {"mood": "comfort", "cuisine": "Kenyan", "type": "main"},
                {"mood": "healthy", "cuisine": "Ethiopian", "type": "salad"},
                {"mood": "adventurous", "cuisine": "Nigerian", "type": "soup"},
                {"mood": "quick", "cuisine": "Ugandan", "type": "snack"},
                {"mood": "energetic", "cuisine": "Tanzanian", "type": "breakfast"},
                {"mood": "comfort", "cuisine": "Kenyan", "type": "dessert"}
            ]
            
            generated_recipes = []
            
            for category in highlight_categories:
                # Generate recipe using AI
                recipe_data = {
                    "ingredients": ["tomatoes", "onions", "garlic", "local spices"],
                    "dietary_restrictions": [category["mood"]],
                    "cuisine_type": category["cuisine"],
                    "meal_type": category["type"],
                    "serving_size": 4
                }
                
                recipe = ai_service.generate_recipe(recipe_data)
                if recipe:
                    # Add highlight-specific metadata
                    recipe['is_highlight'] = True
                    recipe['category'] = category
                    recipe['created_at'] = datetime.now().isoformat()
                    recipe['rating'] = round(4.2 + (len(recipe.get('name', '')) % 8) * 0.1, 1)
                    
                    generated_recipes.append(recipe)
            
            # Save to MongoDB
            db = await get_database()
            
            # Clear existing highlights
            await db.highlight_recipes.delete_many({})
            
            # Insert new highlights
            if generated_recipes:
                await db.highlight_recipes.insert_many(generated_recipes)
            
            return {
                "success": True,
                "message": f"Generated {len(generated_recipes)} highlight recipes",
                "recipes": generated_recipes
            }
            
        except Exception as e:
            print(f"Error generating highlights: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_highlights() -> Dict[str, Any]:
        """Get saved highlight recipes from MongoDB"""
        try:
            db = await get_database()
            
            # Fetch highlights from MongoDB
            cursor = db.highlight_recipes.find({}).sort("created_at", -1)
            recipes = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for recipe in recipes:
                if '_id' in recipe:
                    recipe['_id'] = str(recipe['_id'])
            
            return {
                "success": True,
                "recipes": recipes
            }
            
        except Exception as e:
            print(f"Error fetching highlights: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def refresh_highlights() -> Dict[str, Any]:
        """Refresh highlight recipes with new AI-generated content"""
        return await HighlightsService.generate_highlights()

@app.post("/api/highlights/generate")
async def generate_highlights():
    return await HighlightsService.generate_highlights()

@app.get("/api/highlights")
async def get_highlights():
    return await HighlightsService.get_highlights()

@app.post("/api/highlights/refresh")
async def refresh_highlights():
    return await HighlightsService.refresh_highlights()
