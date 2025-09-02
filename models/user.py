from models.database import get_database
from models.schemas import User, UserCreate, UserUpdate
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional, List

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        """Create a new user"""
        db = await get_database()
        
        user_dict = user_data.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["saved_recipes"] = []
        
        result = await db.users.insert_one(user_dict)
        
        # Fetch the created user
        created_user = await db.users.find_one({"_id": result.inserted_id})
        return User(**created_user)
    
    @staticmethod
    async def get_user_by_phone(phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        db = await get_database()
        user_data = await db.users.find_one({"phone_number": phone_number})
        
        if user_data:
            # Ensure password field exists for backward compatibility
            if 'password' not in user_data:
                user_data['password'] = ''
            return User(**user_data)
        return None
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = await get_database()
        user_data = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if user_data:
            # Ensure password field exists for backward compatibility
            if 'password' not in user_data:
                user_data['password'] = ''
            return User(**user_data)
        return None
    
    @staticmethod
    async def update_user(user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        db = await get_database()
        
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        
        if update_data:
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        
        return await UserService.get_user_by_id(user_id)
    
    @staticmethod
    async def activate_premium(phone_number: str) -> bool:
        """Activate premium subscription for user"""
        db = await get_database()
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        result = await db.users.update_one(
            {"phone_number": phone_number},
            {
                "$set": {
                    "is_premium": True,
                    "premium_expires_at": expires_at
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def check_premium_status(user_id: str) -> bool:
        """Check if user has active premium subscription"""
        user = await UserService.get_user_by_id(user_id)
        
        if not user or not user.is_premium:
            return False
        
        if user.premium_expires_at and user.premium_expires_at < datetime.utcnow():
            # Premium expired, update user
            await UserService.update_user(user_id, UserUpdate(is_premium=False))
            return False
        
        return True
    
    @staticmethod
    async def add_saved_recipe(user_id: str, recipe_id: str) -> bool:
        """Add recipe to user's saved recipes"""
        db = await get_database()
        
        # First ensure the saved_recipes field exists
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$setOnInsert": {"saved_recipes": []}},
            upsert=False
        )
        
        # Check if recipe is already saved
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user and recipe_id in user.get("saved_recipes", []):
            return True  # Already saved, consider it successful
        
        # Add the recipe to saved list
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"saved_recipes": recipe_id}}
        )
        
        return result.matched_count > 0  # Return true if user was found, regardless of modification
    
    @staticmethod
    async def remove_saved_recipe(user_id: str, recipe_id: str) -> bool:
        """Remove recipe from user's saved recipes"""
        db = await get_database()
        
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"saved_recipes": recipe_id}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def update_user_password(user_id: str, hashed_password: str) -> bool:
        """Update user password"""
        db = await get_database()
        
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_password}}
        )
        
        return result.modified_count > 0