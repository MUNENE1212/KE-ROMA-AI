from models.database import get_database
from models.schemas import Recipe, RecipeCreate
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

class RecipeService:
    @staticmethod
    async def create_recipe(recipe_data: RecipeCreate) -> Recipe:
        """Create a new recipe in the database"""
        db = await get_database()
        
        recipe_dict = recipe_data.dict()
        recipe_dict["created_at"] = datetime.utcnow()
        
        result = await db.recipes.insert_one(recipe_dict)
        
        # Fetch the created recipe
        created_recipe = await db.recipes.find_one({"_id": result.inserted_id})
        return Recipe(**created_recipe)
    
    @staticmethod
    async def get_recipe_by_id(recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by its ID"""
        db = await get_database()
        recipe_data = await db.recipes.find_one({"_id": ObjectId(recipe_id)})
        
        if recipe_data:
            return Recipe(**recipe_data)
        return None
    
    @staticmethod
    async def get_recipes_by_ids(recipe_ids: List[str]) -> List[Recipe]:
        """Get multiple recipes by their IDs"""
        db = await get_database()
        
        object_ids = [ObjectId(rid) for rid in recipe_ids if ObjectId.is_valid(rid)]
        
        cursor = db.recipes.find({"_id": {"$in": object_ids}})
        recipes = []
        
        async for recipe_data in cursor:
            recipes.append(Recipe(**recipe_data))
        
        return recipes
    
    @staticmethod
    async def search_recipes(
        ingredients: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Recipe]:
        """Search recipes based on various criteria"""
        db = await get_database()
        
        # Build search query
        query = {}
        
        if ingredients:
            # Search in ingredients array or pantry_ingredients
            ingredient_regex = "|".join(ingredients)
            query["$or"] = [
                {"ingredients": {"$regex": ingredient_regex, "$options": "i"}},
                {"pantry_ingredients": {"$in": ingredients}}
            ]
        
        if tags:
            query["tags"] = {"$in": tags}
        
        if user_id:
            query["generated_for_user"] = user_id
        
        cursor = db.recipes.find(query).sort("created_at", -1).limit(limit)
        recipes = []
        
        async for recipe_data in cursor:
            recipes.append(Recipe(**recipe_data))
        
        return recipes
    
    @staticmethod
    async def get_user_recipes(user_id: str, limit: int = 50) -> List[Recipe]:
        """Get all recipes generated for a specific user"""
        db = await get_database()
        
        cursor = db.recipes.find(
            {"generated_for_user": user_id}
        ).sort("created_at", -1).limit(limit)
        
        recipes = []
        async for recipe_data in cursor:
            recipes.append(Recipe(**recipe_data))
        
        return recipes
    
    @staticmethod
    async def delete_recipe(recipe_id: str) -> bool:
        """Delete a recipe by ID"""
        db = await get_database()
        
        result = await db.recipes.delete_one({"_id": ObjectId(recipe_id)})
        return result.deleted_count > 0
    
    @staticmethod
    async def get_popular_recipes(limit: int = 10) -> List[Recipe]:
        """Get popular recipes (most recently created for now)"""
        db = await get_database()
        
        cursor = db.recipes.find({}).sort("created_at", -1).limit(limit)
        recipes = []
        
        async for recipe_data in cursor:
            recipes.append(Recipe(**recipe_data))
        
        return recipes
