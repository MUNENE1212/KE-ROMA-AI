from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId
import re

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
    username: str
    phone_number: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.strip()
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if not re.match(r'^254[0-9]{9}$', v):
            raise ValueError('Phone number must be in format 254XXXXXXXXX')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

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

class ChatMessage(BaseModel):
    message: str
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 1000:
            raise ValueError('Message too long (max 1000 characters)')
        # Basic XSS prevention
        dangerous_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError('Message contains potentially unsafe content')
        return v.strip()

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
    ingredients: List[str]
    mood: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = []
    cuisine_type: Optional[str] = "African"
    serving_size: Optional[int] = 4
    
    @validator('ingredients')
    def validate_ingredients(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one ingredient is required')
        if len(v) > 20:
            raise ValueError('Maximum 20 ingredients allowed')
        # Sanitize ingredient names
        sanitized = []
        for ingredient in v:
            clean = re.sub(r'[^a-zA-Z0-9\s-]', '', ingredient.strip())
            if len(clean) > 0 and len(clean) <= 50:
                sanitized.append(clean)
        return sanitized
    
    @validator('serving_size')
    def validate_serving_size(cls, v):
        if v is not None and (v < 1 or v > 20):
            raise ValueError('Serving size must be between 1 and 20')
        return v

class RecipeGenerationResponse(BaseModel):
    recipes: List[Recipe]
    generation_time: float
    is_premium_user: bool

class PaymentInitiateRequest(BaseModel):
    phone_number: str
    amount: Optional[float] = 100

class PaymentStatusResponse(BaseModel):
    status: str
    expires_at: Optional[datetime] = None
