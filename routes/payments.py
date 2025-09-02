from fastapi import APIRouter, HTTPException, Depends
from models.schemas import PaymentInitiateRequest, PaymentStatusResponse, PaymentCreate, Payment
from models.database import get_database
from models.user import UserService
from services.intasend_service import IntaSendService
from routes.auth import get_current_user
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

router = APIRouter()

# Payment Plans Configuration
SUBSCRIPTION_PLANS = {
    "basic": {"name": "Basic Plan", "price": 500, "credits": 50, "duration_days": 30},
    "premium": {"name": "Premium Plan", "price": 1000, "credits": 150, "duration_days": 30},
    "pro": {"name": "Pro Plan", "price": 2000, "credits": 400, "duration_days": 30}
}

CREDIT_PACKAGES = {
    "small": {"name": "Small Pack", "price": 200, "credits": 20},
    "medium": {"name": "Medium Pack", "price": 500, "credits": 60},
    "large": {"name": "Large Pack", "price": 1000, "credits": 150}
}

class CreditPurchaseRequest(BaseModel):
    package: str
    phone_number: str

class SubscriptionRequest(BaseModel):
    plan: str
    phone_number: str

class UsageTrackingRequest(BaseModel):
    user_id: str
    action: str
    provider: str
    cost: float

@router.post("/initiate")
async def initiate_payment(request: PaymentInitiateRequest):
    """Initiate M-Pesa payment for premium subscription"""
    try:
        # Get or create user
        user = await UserService.get_user_by_phone(request.phone_number)
        if not user:
            # Create user if doesn't exist
            from models.schemas import UserCreate
            import uuid
            user_create = UserCreate(
                phone_number=request.phone_number,
                username=f"user_{uuid.uuid4().hex[:8]}"  # Generate unique username
            )
            user = await UserService.create_user(user_create)
        
        # Try IntaSend payment, fallback to demo mode if keys are invalid
        try:
            checkout_response = await IntaSendService.create_checkout(
                phone_number=request.phone_number,
                amount=request.amount
            )
            checkout_id = checkout_response["id"]
            print(f"IntaSend payment initiated: {checkout_id}")
            is_demo = False
            
        except Exception as intasend_error:
            print(f"IntaSend failed: {intasend_error}")
            # Use demo payment if IntaSend keys are expired/invalid
            import uuid
            checkout_id = f"demo_{uuid.uuid4().hex[:8]}"
            print(f"Using demo payment mode: {checkout_id}")
            is_demo = True
        
        # Save payment record
        payment_create = PaymentCreate(
            user_id=str(user.id),
            phone_number=request.phone_number,
            amount=request.amount
        )
        
        db = await get_database()
        payment_dict = payment_create.dict()
        payment_dict["intasend_checkout_id"] = checkout_id
        payment_dict["status"] = "pending"
        payment_dict["created_at"] = datetime.utcnow()
        
        payment_id = await db.payments.insert_one(payment_dict).inserted_id
        
        return {"payment_id": str(payment_id), "checkout_id": checkout_id, "status": "pending", "is_demo": is_demo}
        
    except Exception as e:
        print(f"Payment initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/credits/purchase")
async def purchase_credits(request: CreditPurchaseRequest, current_user = Depends(get_current_user)):
    """Purchase credit package"""
    try:
        if request.package not in CREDIT_PACKAGES:
            raise HTTPException(status_code=400, detail="Invalid credit package")
        
        package = CREDIT_PACKAGES[request.package]
        
        # Initiate payment
        try:
            checkout_response = await IntaSendService.create_checkout(
                phone_number=request.phone_number,
                amount=package["price"]
            )
            checkout_id = checkout_response["id"]
            is_demo = False
        except Exception:
            import uuid
            checkout_id = f"demo_credits_{uuid.uuid4().hex[:8]}"
            is_demo = True
        
        # Save payment record
        db = await get_database()
        payment_result = await db.payments.insert_one({
            "user_id": str(current_user.id),
            "phone_number": request.phone_number,
            "amount": package["price"],
            "type": "credits",
            "package": request.package,
            "credits": package["credits"],
            "checkout_id": checkout_id,
            "status": "pending",
            "is_demo": is_demo,
            "created_at": datetime.utcnow()
        })
        payment_id = payment_result.inserted_id
        
        return {
            "payment_id": str(payment_id),
            "checkout_id": checkout_id,
            "package": package,
            "status": "pending",
            "is_demo": is_demo
        }
        
    except Exception as e:
        print(f"Credit purchase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscription/purchase")
async def purchase_subscription(request: SubscriptionRequest, current_user = Depends(get_current_user)):
    """Purchase subscription plan"""
    try:
        if request.plan not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Invalid subscription plan")
        
        plan = SUBSCRIPTION_PLANS[request.plan]
        
        # Initiate payment
        try:
            checkout_response = await IntaSendService.create_checkout(
                phone_number=request.phone_number,
                amount=plan["price"]
            )
            checkout_id = checkout_response["id"]
            is_demo = False
        except Exception:
            import uuid
            checkout_id = f"demo_sub_{uuid.uuid4().hex[:8]}"
            is_demo = True
        
        # Save payment record
        db = await get_database()
        payment_result = await db.payments.insert_one({
            "user_id": str(current_user.id),
            "phone_number": request.phone_number,
            "amount": plan["price"],
            "type": "subscription",
            "plan": request.plan,
            "credits": plan["credits"],
            "duration_days": plan["duration_days"],
            "intasend_checkout_id": checkout_id,
            "status": "pending",
            "is_demo": is_demo,
            "created_at": datetime.utcnow()
        })
        payment_id = payment_result.inserted_id
        
        return {
            "payment_id": str(payment_id),
            "checkout_id": checkout_id,
            "plan": plan,
            "status": "pending",
            "is_demo": is_demo
        }
        
    except Exception as e:
        print(f"Subscription purchase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{checkout_id}")
async def check_payment_status(checkout_id: str):
    """Check the status of a payment"""
    try:
        db = await get_database()
        
        # Get payment from database
        payment = await db.payments.find_one({"intasend_checkout_id": checkout_id})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Check payment status with IntaSend
        payment_status = await IntaSendService.check_payment_status(checkout_id)
        
        # Update payment status in database
        await db.payments.update_one(
            {"intasend_checkout_id": checkout_id},
            {"$set": {"status": payment_status["state"].lower()}}
        )
        
        if payment_status["state"].lower() == "complete":
            # Activate premium for user
            await UserService.activate_premium(payment["phone_number"])
            
            return {
                "status": "completed",
                "payment_id": str(payment["_id"]),
                "amount": payment["amount"],
                "expires_at": datetime.utcnow() + timedelta(days=30)
            }
        
        return {
            "status": payment_status["state"].lower(),
            "payment_id": str(payment["_id"]),
            "amount": payment["amount"]
        }
        
    except Exception as e:
        print(f"Payment status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/usage/track")
async def track_usage(request: UsageTrackingRequest):
    """Track API usage for billing"""
    try:
        db = await get_database()
        
        # Record usage
        await db.usage_tracking.insert_one({
            "user_id": request.user_id,
            "action": request.action,
            "provider": request.provider,
            "cost": request.cost,
            "timestamp": datetime.utcnow()
        })
        
        # Deduct credits from user
        user = await UserService.get_user_by_id(request.user_id)
        if user and hasattr(user, 'credits'):
            new_credits = max(0, user.credits - request.cost)
            await db.users.update_one(
                {"_id": ObjectId(request.user_id)},
                {"$set": {"credits": new_credits}}
            )
        
        return {"status": "tracked", "remaining_credits": new_credits if user else 0}
        
    except Exception as e:
        print(f"Usage tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans")
async def get_payment_plans():
    """Get available subscription plans and credit packages"""
    return {
        "subscription_plans": SUBSCRIPTION_PLANS,
        "credit_packages": CREDIT_PACKAGES
    }

@router.get("/history/{user_id}")
async def get_payment_history(user_id: str, current_user = Depends(get_current_user)):
    """Get user's payment history"""
    try:
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_database()
        payments = await db.payments.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(50).to_list(length=50)
        cursor = db.payments.find(
            {"user_id": user_id}
        ).sort("created_at", -1)
        
        payments = []
        async for payment_data in cursor:
            payment_data["_id"] = str(payment_data["_id"])
            payments.append(payment_data)
        
        return {"payments": payments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
