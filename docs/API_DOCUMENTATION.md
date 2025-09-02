# KE-ROUMA API Documentation

## Overview

The KE-ROUMA API is built with FastAPI and provides endpoints for recipe generation, user management, authentication, payments, and AI chat functionality. The API follows RESTful principles and includes comprehensive error handling and validation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow a consistent format:

```json
{
    "success": true,
    "data": { /* response data */ },
    "message": "Success message",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

Error responses:
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": { /* additional error details */ }
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
}
```

### Authentication Endpoints

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
    "phone_number": "+254712345678",
    "password": "securepassword123",
    "full_name": "John Doe",
    "email": "john@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "user_id",
            "phone_number": "+254712345678",
            "full_name": "John Doe",
            "email": "john@example.com",
            "is_premium": false,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "token": "jwt_token_here"
    },
    "message": "User registered successfully"
}
```

#### POST /api/auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
    "phone_number": "+254712345678",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "user_id",
            "phone_number": "+254712345678",
            "full_name": "John Doe",
            "is_premium": false
        },
        "token": "jwt_token_here"
    },
    "message": "Login successful"
}
```

### Recipe Endpoints

#### POST /api/recipes/generate
Generate AI-powered recipes based on ingredients and preferences.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "ingredients": ["tomatoes", "onions", "rice", "chicken"],
    "mood": "comfort",
    "dietary_restrictions": ["gluten-free"],
    "servings": 4,
    "cooking_time": "30-45 minutes",
    "user_id": "user_id_here"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "recipe": {
            "id": "recipe_id",
            "name": "African Chicken Rice Stew",
            "description": "A warm, comforting meal that brings the taste of home to your table.",
            "ingredients": [
                "2 cups rice",
                "500g chicken pieces",
                "3 large tomatoes",
                "2 medium onions",
                "2 tbsp vegetable oil",
                "1 tsp salt",
                "1 tsp black pepper",
                "2 cups chicken stock"
            ],
            "instructions": [
                "Heat oil in a large pot over medium heat",
                "Add chopped onions and cook until soft and translucent",
                "Add chicken pieces and brown on all sides",
                "Add chopped tomatoes and cook until soft",
                "Add rice and stir to combine",
                "Pour in chicken stock and bring to a boil",
                "Reduce heat, cover and simmer for 20-25 minutes",
                "Season with salt and pepper to taste"
            ],
            "cooking_time": "35 minutes",
            "servings": 4,
            "difficulty": "Medium",
            "nutrition": {
                "calories": 425,
                "protein": "28g",
                "carbs": "45g",
                "fat": "12g"
            },
            "cultural_context": "This dish is inspired by traditional West African jollof rice...",
            "created_at": "2024-01-01T00:00:00Z"
        }
    },
    "message": "Recipe generated successfully"
}
```

#### GET /api/recipes/saved/{user_id}
Get user's saved recipes.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "recipes": [
            {
                "id": "recipe_id",
                "name": "African Chicken Rice Stew",
                "ingredients": ["rice", "chicken", "tomatoes"],
                "cooking_time": "35 minutes",
                "saved_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1
    },
    "message": "Saved recipes retrieved successfully"
}
```

#### POST /api/recipes/save
Save a recipe to user's collection.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "recipe": {
        "name": "African Chicken Rice Stew",
        "ingredients": ["rice", "chicken", "tomatoes"],
        "instructions": ["step 1", "step 2"],
        "cooking_time": "35 minutes"
    },
    "user_id": "user_id_here"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "recipe_id": "saved_recipe_id"
    },
    "message": "Recipe saved successfully"
}
```

#### DELETE /api/recipes/saved/{recipe_id}
Remove a saved recipe.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Recipe removed successfully"
}
```

### User Management Endpoints

#### GET /api/users/{user_id}
Get user profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "user_id",
            "phone_number": "+254712345678",
            "full_name": "John Doe",
            "email": "john@example.com",
            "is_premium": false,
            "premium_expires_at": null,
            "created_at": "2024-01-01T00:00:00Z",
            "preferences": {
                "dietary_restrictions": ["gluten-free"],
                "favorite_cuisines": ["african", "mediterranean"],
                "cooking_skill": "intermediate"
            }
        }
    },
    "message": "User profile retrieved successfully"
}
```

#### PUT /api/users/{user_id}
Update user profile.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "full_name": "John Updated Doe",
    "email": "john.updated@example.com",
    "preferences": {
        "dietary_restrictions": ["gluten-free", "dairy-free"],
        "favorite_cuisines": ["african"],
        "cooking_skill": "advanced"
    }
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "user_id",
            "full_name": "John Updated Doe",
            "email": "john.updated@example.com"
        }
    },
    "message": "User profile updated successfully"
}
```

#### GET /api/users/{user_id}/premium-status
Check user's premium subscription status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "is_premium": true,
        "premium_expires_at": "2024-12-31T23:59:59Z",
        "features": [
            "unlimited_recipes",
            "nutrition_analysis",
            "meal_planning",
            "priority_support"
        ]
    },
    "message": "Premium status retrieved successfully"
}
```

### Payment Endpoints

#### POST /api/payments/initiate
Initiate M-Pesa payment for premium subscription.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "phone_number": "+254712345678",
    "amount": 100,
    "user_id": "user_id_here",
    "subscription_type": "monthly"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "checkout_id": "checkout_id_here",
        "payment_url": "https://payment.intasend.com/checkout/...",
        "status": "pending",
        "amount": 100,
        "currency": "KES"
    },
    "message": "Payment initiated successfully"
}
```

#### GET /api/payments/status/{checkout_id}
Check payment status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "checkout_id": "checkout_id_here",
        "status": "completed",
        "amount": 100,
        "currency": "KES",
        "transaction_id": "mpesa_transaction_id",
        "completed_at": "2024-01-01T00:00:00Z"
    },
    "message": "Payment status retrieved successfully"
}
```

#### GET /api/payments/history/{user_id}
Get user's payment history.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "payments": [
            {
                "id": "payment_id",
                "amount": 100,
                "currency": "KES",
                "status": "completed",
                "subscription_type": "monthly",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1
    },
    "message": "Payment history retrieved successfully"
}
```

### Chat Endpoints

#### POST /api/chat/message
Send message to AI chat assistant.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "message": "Can you suggest a recipe with chicken and rice?",
    "user_id": "user_id_here",
    "context": {
        "current_ingredients": ["chicken", "rice"],
        "mood": "quick"
    }
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "response": "I'd be happy to suggest a quick chicken and rice recipe! Based on your ingredients...",
        "suggestions": [
            {
                "type": "recipe",
                "title": "Quick Chicken Fried Rice",
                "action": "generate_recipe"
            }
        ],
        "conversation_id": "conversation_id"
    },
    "message": "Chat response generated successfully"
}
```

#### GET /api/chat/history/{user_id}
Get user's chat history.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "conversations": [
            {
                "id": "conversation_id",
                "messages": [
                    {
                        "role": "user",
                        "content": "Can you suggest a recipe?",
                        "timestamp": "2024-01-01T00:00:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "I'd be happy to help!",
                        "timestamp": "2024-01-01T00:00:01Z"
                    }
                ],
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    },
    "message": "Chat history retrieved successfully"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_ERROR` | Invalid or missing authentication |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `USER_NOT_FOUND` | User does not exist |
| `RECIPE_NOT_FOUND` | Recipe does not exist |
| `PAYMENT_FAILED` | Payment processing failed |
| `AI_SERVICE_ERROR` | AI service unavailable |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_SERVER_ERROR` | Server error |

## Rate Limiting

- **Free Users**: 10 recipe generations per day
- **Premium Users**: Unlimited recipe generations
- **API Calls**: 100 requests per minute per user
- **Chat Messages**: 50 messages per hour for free users

## Webhooks

### Payment Webhooks

The API supports webhooks for payment status updates:

**Endpoint**: `POST /api/webhooks/payment`

**Payload:**
```json
{
    "event": "payment.completed",
    "data": {
        "checkout_id": "checkout_id_here",
        "status": "completed",
        "user_id": "user_id_here",
        "amount": 100,
        "currency": "KES"
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## SDK Examples

### JavaScript/Node.js

```javascript
class KERomaAPI {
    constructor(baseURL, token) {
        this.baseURL = baseURL;
        this.token = token;
    }

    async generateRecipe(ingredients, mood = 'balanced') {
        const response = await fetch(`${this.baseURL}/api/recipes/generate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ingredients,
                mood,
                user_id: this.userId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async saveRecipe(recipe) {
        const response = await fetch(`${this.baseURL}/api/recipes/save`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipe,
                user_id: this.userId
            })
        });

        return await response.json();
    }
}

// Usage
const api = new KERomaAPI('http://localhost:8000', 'your-jwt-token');
const recipe = await api.generateRecipe(['chicken', 'rice'], 'comfort');
```

### Python

```python
import requests
import json

class KERomaAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def generate_recipe(self, ingredients, mood='balanced'):
        url = f'{self.base_url}/api/recipes/generate'
        data = {
            'ingredients': ingredients,
            'mood': mood,
            'user_id': self.user_id
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def save_recipe(self, recipe):
        url = f'{self.base_url}/api/recipes/save'
        data = {
            'recipe': recipe,
            'user_id': self.user_id
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

# Usage
api = KERomaAPI('http://localhost:8000', 'your-jwt-token')
recipe = api.generate_recipe(['chicken', 'rice'], 'comfort')
```

## Testing

### Health Check Test
```bash
curl -X GET http://localhost:8000/health
```

### Recipe Generation Test
```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "rice", "tomatoes"],
    "mood": "comfort",
    "user_id": "test_user_id"
  }'
```

### Authentication Test
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+254712345678",
    "password": "testpassword"
  }'
```

## Changelog

### v1.0.0 (Current)
- Initial API release
- Recipe generation endpoints
- User management
- M-Pesa payment integration
- AI chat functionality
- Authentication and authorization

### Planned Features
- Recipe collections and categories
- Social features (sharing, comments, likes)
- Advanced search and filtering
- Meal planning endpoints
- Nutrition analysis improvements
- Multi-language support
