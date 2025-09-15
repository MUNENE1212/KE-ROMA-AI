from fastapi import APIRouter, HTTPException, Depends
from models.schemas import RecipeGenerationRequest, RecipeGenerationResponse, User, Recipe, RecipeCreate
from services.multi_ai_service import MultiAIService
from routes.auth import get_current_user
from services.recipe_service import RecipeService
from utils.security import SecurityUtils
from models.database import get_database
from models.user import UserService
from bson import ObjectId
from typing import List, Optional
import time

router = APIRouter()

@router.post("/generate", response_model=RecipeGenerationResponse)
async def generate_recipes(request: RecipeGenerationRequest):
    """Generate AI-powered recipe recommendations based on pantry ingredients"""
    start_time = time.time()
    
    # Debug: Log the incoming request
    print(f"DEBUG: Received request: {request}")
    print(f"DEBUG: Request ingredients: {request.ingredients}")
    print(f"DEBUG: Request user_id: {request.user_id}")
    
    try:
        # Check if user exists and premium status
        is_premium = False
        user_id = request.user_id
        if user_id:
            is_premium = await UserService.check_premium_status(user_id)
        
        # Generate recipes using multi-AI service
        recipes, generation_info = await MultiAIService.generate_recipes(
            pantry_ingredients=request.ingredients,
            health_goals=request.dietary_restrictions,
            is_premium=is_premium,
            preferred_provider=getattr(request, 'preferred_provider', 'gemini')
        )
        
        # Save generated recipes to database
        saved_recipes = []
        for recipe_data in recipes:
            recipe_create = RecipeCreate(
                **recipe_data,
                generated_for_user=user_id,
                pantry_ingredients=request.ingredients
            )
            saved_recipe = await RecipeService.create_recipe(recipe_create)
            saved_recipes.append(saved_recipe)
        
        generation_time = time.time() - start_time
        
        return RecipeGenerationResponse(
            recipes=saved_recipes,
            generation_time=generation_time,
            is_premium_user=is_premium
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers/status")
async def get_provider_status():
    """Get status of all AI providers"""
    try:
        return await MultiAIService.check_all_providers()
    except Exception as e:
        print(f"Error getting provider status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get provider status")

@router.get("/providers/available")
async def get_available_providers():
    """Get list of available AI providers"""
    try:
        return {"providers": MultiAIService.get_available_providers()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved/{user_id}", response_model=List[Recipe])
async def get_saved_recipes(user_id: str):
    """Get user's saved recipes"""
    try:
        db = await get_database()
        
        # Get user's saved recipe IDs
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        saved_recipe_ids = user.get("saved_recipes", [])
        
        # Get recipe details
        recipes = []
        for recipe_id in saved_recipe_ids:
            recipe = await db.recipes.find_one({"_id": ObjectId(recipe_id)})
            if recipe:
                recipe["id"] = str(recipe["_id"])
                recipes.append(Recipe(**recipe))
        
        return recipes
        
    except Exception as e:
        print(f"Error getting saved recipes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save/{recipe_id}")
async def save_recipe(recipe_id: str, user_id: str):
    """Save a recipe to user's collection"""
    try:
        success = await UserService.add_saved_recipe(user_id, recipe_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to save recipe")
        
        return {"success": True, "message": "Recipe saved successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/saved/{recipe_id}")
async def remove_saved_recipe(recipe_id: str, user_id: str):
    """Remove a recipe from user's saved collection"""
    try:
        success = await UserService.remove_saved_recipe(user_id, recipe_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to remove recipe")
        
        return {"success": True, "message": "Recipe removed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_recipes(
    ingredients: str = None,
    tags: str = None,
    user_id: str = None,
    limit: int = 20
):
    """Search recipes by ingredients or tags"""
    try:
        recipes = await RecipeService.search_recipes(
            ingredients=ingredients.split(",") if ingredients else None,
            tags=tags.split(",") if tags else None,
            user_id=user_id,
            limit=limit
        )
        return {"recipes": recipes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))