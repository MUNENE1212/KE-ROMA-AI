import requests
from base64 import b64encode
from config.config import get_settings
from datetime import datetime
from typing import Dict, Any

class IntaSendService:
    @staticmethod
    async def initiate_payment(phone_number: str, amount: float, currency: str = "KES") -> Dict[str, Any]:
        """Initiate M-Pesa payment via IntaSend"""
        return await IntaSendService.create_checkout(phone_number, amount)
    
    @staticmethod
    async def create_checkout(phone_number: str, amount: float) -> Dict[str, Any]:
        """Create IntaSend checkout for M-Pesa payment"""
        settings = get_settings()
        
        if not settings.intasend_secret_key or settings.intasend_secret_key == "your_intasend_secret_key_here":
            raise Exception("IntaSend API keys not configured properly")
        
        print(f"Creating checkout for {phone_number}, amount: {amount}")
        print(f"Using IntaSend URL: {settings.intasend_base_url}")
        print(f"Publishable key: {settings.intasend_publishable_key[:20]}...")
        print(f"Secret key: {settings.intasend_secret_key[:20]}...")
        
        checkout_data = {
            "public_key": settings.intasend_publishable_key,
            "amount": amount,
            "currency": "KES",
            "phone_number": phone_number,
            "api_ref": f"kerouma_premium_{int(datetime.now().timestamp())}",
            "comment": "KE-ROUMA Premium Subscription"
        }
        
        # Use Basic authentication instead of Bearer
        credentials = b64encode(f":{settings.intasend_secret_key}".encode()).decode()
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"Checkout data: {checkout_data}")
        
        response = requests.post(
            f'{settings.intasend_base_url}/checkout/',
            headers=headers,
            json=checkout_data,
            timeout=30
        )
        
        print(f"IntaSend response status: {response.status_code}")
        print(f"IntaSend response: {response.text}")
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"IntaSend API Error ({response.status_code}): {response.text}")
    
    @staticmethod
    async def check_payment_status(checkout_id: str) -> Dict[str, Any]:
        """Check payment status with IntaSend"""
        settings = get_settings()
        
        print(f"Checking payment status for checkout ID: {checkout_id}")
        print(f"Using URL: {settings.intasend_base_url}/checkout/{checkout_id}/")
        
        # Use Basic authentication instead of Bearer
        credentials = b64encode(f":{settings.intasend_secret_key}".encode()).decode()
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f'{settings.intasend_base_url}/checkout/{checkout_id}/',
            headers=headers,
            timeout=30
        )
        
        print(f"Status check response code: {response.status_code}")
        print(f"Status check response: {response.text[:200]}...")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to check payment status ({response.status_code}): {response.text[:200]}")