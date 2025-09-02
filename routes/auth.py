from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import uuid
import os

from models.database import get_database
from models.user import UserService, UserCreate
from models.schemas import User

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class LoginRequest(BaseModel):
    phone_number: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    phone_number: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    phone_number: str

class PasswordResetConfirm(BaseModel):
    phone_number: str
    reset_code: str
    new_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_reset_code():
    import random
    return str(random.randint(100000, 999999))

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await UserService.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=Token)
async def register(request: RegisterRequest):
    try:
        # Check if user already exists
        existing_user = await UserService.get_user_by_phone(request.phone_number)
        if existing_user:
            raise HTTPException(status_code=400, detail="Phone number already registered")
        
        # Hash password
        hashed_password = get_password_hash(request.password)
        
        # Create user
        user_create = UserCreate(
            username=request.username,
            phone_number=request.phone_number,
            password=hashed_password
        )
        
        user = await UserService.create_user(user_create)
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "phone_number": user.phone_number,
                "is_premium": user.is_premium,
                "token": access_token
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    try:
        # Get user by phone
        user = await UserService.get_user_by_phone(request.phone_number)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid phone number or password")
        
        # Verify password
        if not verify_password(request.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid phone number or password")
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "phone_number": user.phone_number,
                "is_premium": user.is_premium,
                "token": access_token
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user = await UserService.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "phone_number": user.phone_number,
                "is_premium": user.is_premium,
                "token": access_token
            }
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        print(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.post("/password-reset")
async def request_password_reset(request: PasswordResetRequest):
    try:
        user = await UserService.get_user_by_phone(request.phone_number)
        if not user:
            # Don't reveal if phone number exists for security
            return {"message": "If the phone number exists, a reset code has been sent"}
        
        # Generate reset code
        reset_code = generate_reset_code()
        
        # Store reset code in database with expiration
        db = await get_database()
        await db.password_resets.insert_one({
            "phone_number": request.phone_number,
            "reset_code": reset_code,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=15),
            "used": False
        })
        
        # TODO: Send SMS with reset code via SMS service
        print(f"Password reset code for {request.phone_number}: {reset_code}")
        
        return {"message": "If the phone number exists, a reset code has been sent"}
    except Exception as e:
        print(f"Password reset request error: {e}")
        raise HTTPException(status_code=500, detail="Password reset request failed")

@router.post("/password-reset/confirm")
async def confirm_password_reset(request: PasswordResetConfirm):
    try:
        db = await get_database()
        
        # Find valid reset code
        reset_record = await db.password_resets.find_one({
            "phone_number": request.phone_number,
            "reset_code": request.reset_code,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not reset_record:
            raise HTTPException(status_code=400, detail="Invalid or expired reset code")
        
        # Update user password
        user = await UserService.get_user_by_phone(request.phone_number)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        hashed_password = get_password_hash(request.new_password)
        await UserService.update_user_password(str(user.id), hashed_password)
        
        # Mark reset code as used
        await db.password_resets.update_one(
            {"_id": reset_record["_id"]},
            {"$set": {"used": True}}
        )
        
        return {"message": "Password reset successful"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Password reset confirm error: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "phone_number": current_user.phone_number,
        "is_premium": current_user.is_premium
    }
