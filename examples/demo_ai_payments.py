#!/usr/bin/env python3
"""
KE-ROUMA AI & Payment Demo
Demonstrates AI recipe generation and M-Pesa payment integration
"""
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

class MockAIService:
    """Mock AI service that generates African recipes without requiring OpenAI API"""
    
    AFRICAN_RECIPES = [
        {
            "name": "Jollof Rice with Beans",
            "cuisine": "West African",
            "prep_time": "45 minutes",
            "difficulty": "Medium",
            "servings": 4,
            "ingredients": [
                "2 cups jasmine rice", "1 cup black-eyed beans", "3 large tomatoes",
                "1 large onion", "3 cloves garlic", "1 inch ginger", 
                "2 tbsp palm oil", "1 tsp curry powder", "Salt to taste"
            ],
            "instructions": [
                "Soak beans overnight, then boil until tender",
                "Blend tomatoes, onion, garlic, and ginger into a smooth paste",
                "Heat palm oil in a large pot, fry the paste until thick",
                "Add curry powder, salt, and cooked beans",
                "Add rice and 3 cups water, bring to boil",
                "Reduce heat, cover and simmer for 25 minutes",
                "Let stand 5 minutes before serving"
            ],
            "nutrition": {
                "calories": 420,
                "protein": "12g",
                "carbs": "68g",
                "fiber": "8g",
                "iron": "15% DV"
            },
            "health_benefits": [
                "High in plant protein from beans",
                "Rich in iron for blood health",
                "Complex carbohydrates for sustained energy",
                "Anti-inflammatory ginger and garlic"
            ]
        },
        {
            "name": "Ugali with Sukuma Wiki",
            "cuisine": "East African",
            "prep_time": "30 minutes",
            "difficulty": "Easy",
            "servings": 4,
            "ingredients": [
                "2 cups white cornmeal", "4 cups water", "1 bunch collard greens",
                "2 tomatoes", "1 onion", "2 cloves garlic", 
                "2 tbsp vegetable oil", "Salt to taste"
            ],
            "instructions": [
                "Boil water in a heavy-bottomed pot",
                "Gradually add cornmeal while stirring to prevent lumps",
                "Cook for 15 minutes, stirring constantly until thick",
                "For sukuma wiki: sauté onions until golden",
                "Add garlic, tomatoes, cook until soft",
                "Add chopped collard greens, cook until wilted",
                "Season with salt and serve with ugali"
            ],
            "nutrition": {
                "calories": 320,
                "protein": "8g",
                "carbs": "58g",
                "fiber": "6g",
                "vitamin_k": "200% DV"
            },
            "health_benefits": [
                "High in vitamin K for bone health",
                "Rich in folate from greens",
                "Gluten-free whole grain energy",
                "Low in saturated fat"
            ]
        },
        {
            "name": "Injera with Lentil Stew",
            "cuisine": "Ethiopian",
            "prep_time": "60 minutes",
            "difficulty": "Hard",
            "servings": 6,
            "ingredients": [
                "2 cups teff flour", "3 cups water", "1 cup red lentils",
                "2 onions", "3 cloves garlic", "1 inch ginger",
                "2 tbsp berbere spice", "2 tbsp olive oil", "Salt to taste"
            ],
            "instructions": [
                "Mix teff flour with water, let ferment 2-3 days",
                "Cook injera batter on non-stick pan like crepes",
                "For stew: sauté onions until caramelized",
                "Add garlic, ginger, berbere spice",
                "Add lentils and 2 cups water, simmer 30 minutes",
                "Season with salt, serve on injera bread"
            ],
            "nutrition": {
                "calories": 380,
                "protein": "16g",
                "carbs": "62g",
                "fiber": "12g",
                "iron": "25% DV"
            },
            "health_benefits": [
                "Complete protein from lentils",
                "High fiber for digestive health",
                "Rich in iron and B vitamins",
                "Probiotic benefits from fermented injera"
            ]
        }
    ]
    
    @staticmethod
    async def generate_recipes(pantry_ingredients: List[str], health_goals: List[str] = None, is_premium: bool = False) -> List[Dict[str, Any]]:
        """Generate African recipes based on available ingredients"""
        
        # Simulate AI processing time
        await asyncio.sleep(1)
        
        # Filter recipes based on available ingredients
        available_recipes = []
        
        for recipe in MockAIService.AFRICAN_RECIPES:
            # Check if user has key ingredients for this recipe
            recipe_ingredients = [ing.lower() for ing in recipe["ingredients"]]
            user_ingredients = [ing.lower() for ing in pantry_ingredients]
            
            # Count matching ingredients
            matches = sum(1 for user_ing in user_ingredients 
                         if any(user_ing in recipe_ing for recipe_ing in recipe_ingredients))
            
            if matches >= 2:  # Need at least 2 matching ingredients
                recipe_copy = recipe.copy()
                recipe_copy["ingredient_matches"] = matches
                recipe_copy["available_ingredients"] = [
                    ing for ing in recipe["ingredients"] 
                    if any(user_ing.lower() in ing.lower() for user_ing in user_ingredients)
                ]
                available_recipes.append(recipe_copy)
        
        # Sort by ingredient matches
        available_recipes.sort(key=lambda x: x["ingredient_matches"], reverse=True)
        
        # Return based on premium status
        if is_premium:
            return available_recipes[:3]  # Premium users get up to 3 recipes
        else:
            return available_recipes[:1]  # Free users get 1 recipe

class MockPaymentService:
    """Mock payment service that simulates M-Pesa integration"""
    
    @staticmethod
    async def initiate_payment(phone_number: str, amount: float, currency: str = "KES") -> Dict[str, Any]:
        """Simulate M-Pesa payment initiation"""
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        # Generate mock checkout response
        checkout_id = f"CHK_{int(datetime.now().timestamp())}"
        
        return {
            "id": checkout_id,
            "state": "PENDING",
            "provider": "MPESA",
            "charges": amount,
            "net_amount": amount,
            "currency": currency,
            "value": amount,
            "phone_number": phone_number,
            "created_at": datetime.now().isoformat(),
            "api_ref": f"kerouma_premium_{checkout_id}",
            "checkout_url": f"https://checkout.intasend.com/{checkout_id}",
            "qr_code": f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        }
    
    @staticmethod
    async def check_payment_status(checkout_id: str) -> Dict[str, Any]:
        """Simulate payment status check"""
        
        await asyncio.sleep(0.3)
        
        # Simulate successful payment after some time
        return {
            "id": checkout_id,
            "state": "COMPLETE",
            "provider": "MPESA",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "failed_reason": None,
            "failed_code": None
        }

async def demo_ai_recipes():
    """Demonstrate AI recipe generation"""
    print("🤖 AI Recipe Generation Demo")
    print("=" * 40)
    
    # Test with typical African pantry ingredients
    pantry_ingredients = ["rice", "beans", "tomatoes", "onions", "garlic", "ginger", "oil"]
    health_goals = ["heart health", "weight management", "high protein"]
    
    print(f"📦 Available Ingredients: {', '.join(pantry_ingredients)}")
    print(f"🎯 Health Goals: {', '.join(health_goals)}")
    print()
    
    # Test free user (1 recipe)
    print("👤 Free User Experience:")
    free_recipes = await MockAIService.generate_recipes(
        pantry_ingredients=pantry_ingredients,
        health_goals=health_goals,
        is_premium=False
    )
    
    for i, recipe in enumerate(free_recipes, 1):
        print(f"   Recipe {i}: {recipe['name']} ({recipe['cuisine']})")
        print(f"   ⏱️  {recipe['prep_time']} | 🍽️  {recipe['servings']} servings | 📊 {recipe['difficulty']}")
        print(f"   🥗 Available ingredients: {', '.join(recipe['available_ingredients'][:3])}...")
        print(f"   💪 Health benefits: {recipe['health_benefits'][0]}")
    
    print()
    
    # Test premium user (3 recipes)
    print("⭐ Premium User Experience:")
    premium_recipes = await MockAIService.generate_recipes(
        pantry_ingredients=pantry_ingredients,
        health_goals=health_goals,
        is_premium=True
    )
    
    for i, recipe in enumerate(premium_recipes, 1):
        print(f"   Recipe {i}: {recipe['name']} ({recipe['cuisine']})")
        print(f"   ⏱️  {recipe['prep_time']} | 🍽️  {recipe['servings']} servings | 📊 {recipe['difficulty']}")
        print(f"   🔥 {recipe['nutrition']['calories']} calories | 🥩 {recipe['nutrition']['protein']} protein")
        print(f"   💪 {len(recipe['health_benefits'])} health benefits")
        print()

async def demo_payment_system():
    """Demonstrate M-Pesa payment integration"""
    print("💳 M-Pesa Payment Demo")
    print("=" * 40)
    
    # Test payment flow
    phone_number = "+254712345678"
    amount = 100.0
    
    print(f"📱 Phone: {phone_number}")
    print(f"💰 Amount: KES {amount}")
    print()
    
    # Step 1: Initiate payment
    print("Step 1: Initiating M-Pesa payment...")
    checkout_response = await MockPaymentService.initiate_payment(
        phone_number=phone_number,
        amount=amount,
        currency="KES"
    )
    
    print(f"   ✅ Payment initiated successfully!")
    print(f"   🆔 Checkout ID: {checkout_response['id']}")
    print(f"   📊 Status: {checkout_response['state']}")
    print(f"   🔗 Checkout URL: {checkout_response['checkout_url']}")
    print()
    
    # Step 2: Check payment status
    print("Step 2: Checking payment status...")
    await asyncio.sleep(1)  # Simulate user completing payment
    
    status_response = await MockPaymentService.check_payment_status(
        checkout_response['id']
    )
    
    print(f"   ✅ Payment completed successfully!")
    print(f"   📊 Final Status: {status_response['state']}")
    print(f"   ⏰ Updated: {status_response['updated_at']}")
    print()

async def demo_complete_user_journey():
    """Demonstrate complete user journey from recipe generation to premium upgrade"""
    print("🍽️  Complete User Journey Demo")
    print("=" * 50)
    
    # User starts as free user
    print("Scenario: User wants recipes for dinner")
    print()
    
    pantry = ["rice", "chicken", "tomatoes", "onions", "spices"]
    
    # Free user gets limited recipes
    print("1️⃣  Free user generates recipe:")
    free_recipes = await MockAIService.generate_recipes(pantry, is_premium=False)
    print(f"   Got {len(free_recipes)} recipe: {free_recipes[0]['name']}")
    print("   💡 'Upgrade to Premium for more recipes!'")
    print()
    
    # User decides to upgrade
    print("2️⃣  User decides to upgrade to Premium:")
    payment_result = await MockPaymentService.initiate_payment("+254712345678", 100)
    print(f"   Payment initiated: {payment_result['id']}")
    
    # Simulate payment completion
    await asyncio.sleep(1)
    status = await MockPaymentService.check_payment_status(payment_result['id'])
    print(f"   Payment status: {status['state']}")
    print()
    
    # Premium user gets more recipes
    print("3️⃣  Premium user generates recipes:")
    premium_recipes = await MockAIService.generate_recipes(pantry, is_premium=True)
    print(f"   Got {len(premium_recipes)} recipes:")
    for recipe in premium_recipes:
        print(f"   • {recipe['name']} ({recipe['cuisine']})")
    print()
    
    print("✨ User journey completed successfully!")

async def main():
    """Run all demos"""
    print("🇰🇪 KE-ROUMA AI & Payment Integration Demo")
    print("🍽️  Promoting African Heritage Through Technology")
    print()
    
    # Run individual demos
    await demo_ai_recipes()
    print("\n" + "="*60 + "\n")
    
    await demo_payment_system()
    print("\n" + "="*60 + "\n")
    
    await demo_complete_user_journey()
    
    print("\n🎉 All demos completed successfully!")
    print("\n💡 Key Features Demonstrated:")
    print("   ✅ AI-powered African recipe generation")
    print("   ✅ Ingredient-based recipe matching")
    print("   ✅ Health-conscious recipe suggestions")
    print("   ✅ M-Pesa payment integration")
    print("   ✅ Premium subscription flow")
    print("   ✅ Complete user experience")

if __name__ == "__main__":
    asyncio.run(main())
