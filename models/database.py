from motor.motor_asyncio import AsyncIOMotorClient
from config.config import get_settings
import asyncio

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def init_db():
    """Initialize MongoDB connection"""
    settings = get_settings()
    
    # Create MongoDB client
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.database = db.client[settings.database_name]
    
    # Create saved_recipes collection
    await db.database.saved_recipes.create_index("user_id")
    await db.database.saved_recipes.create_index("saved_at")
    
    # Create highlight_recipes collection
    await db.database.highlight_recipes.create_index("name")
    await db.database.highlight_recipes.create_index("cuisine")
    await db.database.highlight_recipes.create_index("mood")
    await db.database.highlight_recipes.create_index("rating")
    await db.database.highlight_recipes.create_index("created_at")
    
    # Create cooking_sessions collection
    await db.database.cooking_sessions.create_index("session_id", unique=True)
    await db.database.cooking_sessions.create_index("user_id")
    await db.database.cooking_sessions.create_index("started_at")
    await db.database.cooking_sessions.create_index("completed_at")
    
    # Create indexes for better performance
    await create_indexes()
    
    print(f"Connected to MongoDB: {settings.database_name}")

async def create_indexes():
    """Create database indexes for optimal performance"""
    # Users collection indexes
    await db.database.users.create_index("phone_number", unique=True)
    await db.database.users.create_index("username", unique=True, sparse=True)
    
    # Recipes collection indexes
    await db.database.recipes.create_index("generated_for_user")
    await db.database.recipes.create_index("tags")
    await db.database.recipes.create_index("created_at")
    
    # Payments collection indexes
    await db.database.payments.create_index("user_id")
    await db.database.payments.create_index("intasend_checkout_id", unique=True)
    await db.database.payments.create_index("phone_number")

async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()
