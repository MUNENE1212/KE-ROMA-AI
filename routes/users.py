from fastapi import APIRouter, HTTPException, Depends
from models.schemas import User, UserCreate, UserUpdate
from models.user import UserService
from models.database import get_database
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["users"])

class RecipeSaveRequest(BaseModel):
    recipe: dict
    user_id: str

class StapleRequest(BaseModel):
    staple: str

@router.post("/", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = await UserService.get_user_by_phone(user_data.phone_number)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this phone number already exists")
        
        user = await UserService.create_user(user_data)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phone/{phone_number}", response_model=User)
async def get_user_by_phone(phone_number: str):
    """Get user by phone number"""
    try:
        user = await UserService.get_user_by_phone(phone_number)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user information"""
    try:
        user = await UserService.update_user(user_id, user_update)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/premium-status")
async def check_premium_status(user_id: str):
    """Check if user has active premium subscription"""
    try:
        is_premium = await UserService.check_premium_status(user_id)
        user = await UserService.get_user_by_id(user_id)
        
        return {
            "is_premium": is_premium,
            "expires_at": user.premium_expires_at if user else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/recipes")
async def get_user_recipes(user_id: str, current_user: User = Depends(get_current_user)):
    """Get all saved recipes for a user"""
    try:
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_database()
        recipes = await db.saved_recipes.find({"user_id": user_id}).to_list(None)
        
        return recipes
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recipes/save")
async def save_recipe(request: RecipeSaveRequest, current_user: User = Depends(get_current_user)):
    """Save a recipe for the current user"""
    try:
        if str(current_user.id) != request.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_database()
        
        # Check if recipe already saved
        existing = await db.saved_recipes.find_one({
            "user_id": request.user_id,
            "recipe.name": request.recipe.get("name")
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Recipe already saved")
        
        # Save recipe
        recipe_doc = {
            "user_id": request.user_id,
            "recipe": request.recipe,
            "saved_at": datetime.utcnow()
        }
        
        result = await db.saved_recipes.insert_one(recipe_doc)
        recipe_doc["_id"] = str(result.inserted_id)
        
        return {"success": True, "recipe_id": str(result.inserted_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/recipes/{recipe_id}")
async def delete_saved_recipe(recipe_id: str, current_user: User = Depends(get_current_user)):
    """Delete a saved recipe"""
    try:
        db = await get_database()
        
        # Check if recipe belongs to user
        recipe = await db.saved_recipes.find_one({"_id": recipe_id})
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        if recipe["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete recipe
        await db.saved_recipes.delete_one({"_id": recipe_id})
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/staples")
async def get_user_staples(user_id: str, current_user: User = Depends(get_current_user)):
    """Get user's pantry staples"""
    try:
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_database()
        user_doc = await db.users.find_one({"_id": user_id})
        
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_doc.get("staples", [])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/staples")
async def add_user_staple(user_id: str, request: StapleRequest, current_user: User = Depends(get_current_user)):
    """Add a staple to user's pantry"""
    try:
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_database()
        
        # Add staple to user's staples array
        await db.users.update_one(
            {"_id": user_id},
            {"$addToSet": {"staples": request.staple}}
        )
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/staples/{staple}")
async def remove_user_staple(user_id: str, staple: str, current_user: User = Depends(get_current_user)):
    """Remove a staple from user's pantry"""
    try:
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_database()
        
        # Remove staple from user's staples array
        await db.users.update_one(
            {"_id": user_id},
            {"$pull": {"staples": staple}}
        )
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
