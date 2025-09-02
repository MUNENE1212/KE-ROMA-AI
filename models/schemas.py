from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, _source_type, _handler):
        return {"type": "string"}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, validation_info=None):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid objectid")

# User Models
class UserBase(BaseModel):
    username: Optional[str] = None
    phone_number: str
    health_goals: List[str] = []
    pantry: List[str] = []
    is_premium: bool = False
    premium_expires_at: Optional[datetime] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    health_goals: Optional[List[str]] = None
    pantry: Optional[List[str]] = None

class User(UserBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password: str
    saved_recipes: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Recipe Models
class RecipeBase(BaseModel):
    name: str
    ingredients: List[str]
    instructions: List[str]
    health_benefits: Optional[str] = None
    cooking_time: Optional[str] = None
    nutrition_info: Optional[dict] = None
    tags: List[str] = []
    origin: Optional[str] = None
    cultural_context: Optional[str] = None

class RecipeCreate(RecipeBase):
    generated_for_user: Optional[str] = None
    pantry_ingredients: List[str] = []

class Recipe(RecipeBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    generated_for_user: Optional[str] = None
    pantry_ingredients: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Payment Models
class PaymentBase(BaseModel):
    phone_number: str
    amount: float
    currency: str = "KES"

class PaymentCreate(PaymentBase):
    user_id: str

class Payment(PaymentBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    intasend_checkout_id: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class RecipeGenerationRequest(BaseModel):
    pantry_ingredients: List[str]
    health_goals: Optional[List[str]] = []
    user_id: Optional[str] = None
    preferred_provider: Optional[str] = None

class RecipeGenerationResponse(BaseModel):
    recipes: List[Recipe]
    generation_time: float
    is_premium_user: bool
    generation_info: Optional[Dict[str, Any]] = None

class PaymentInitiateRequest(BaseModel):
    phone_number: str
    amount: Optional[float] = 100

class PaymentStatusResponse(BaseModel):
    status: str
    expires_at: Optional[datetime] = None
