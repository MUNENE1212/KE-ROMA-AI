from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.multi_ai_service import MultiAIService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    preferred_provider: Optional[str] = "auto"

class ChatResponse(BaseModel):
    response: str
    provider_used: str
    generation_time: float
    fallback_used: bool = False

class ChatHistory(BaseModel):
    messages: List[dict]

# Initialize AI service
ai_service = MultiAIService()

@router.post("/send", response_model=ChatResponse)
async def send_chat_message(chat_message: ChatMessage):
    """
    Send a message to the AI chatbot and get a response
    """
    try:
        # Create a cooking/recipe-focused prompt
        system_prompt = """You are KE-ROUMA's AI Kitchen Assistant, an expert in African cuisine and cooking. 
        You help users with:
        - African recipe recommendations and cooking tips
        - Ingredient substitutions and cooking techniques
        - Nutritional advice for African dishes
        - Cultural context about African food traditions
        - Meal planning and ingredient shopping advice
        
        Keep responses helpful, friendly, and focused on African cuisine. 
        If asked about non-food topics, politely redirect to cooking and recipes."""
        
        # Combine system prompt with user message
        full_prompt = f"{system_prompt}\n\nUser: {chat_message.message}\n\nAssistant:"
        
        # Generate response using multi-AI service
        result = await ai_service.generate_chat_response(
            prompt=full_prompt,
            preferred_provider=chat_message.preferred_provider,
            user_id=chat_message.user_id
        )
        
        return ChatResponse(
            response=result["response"],
            provider_used=result["successful_provider"],
            generation_time=result["generation_time"],
            fallback_used=result.get("fallback_used", False)
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        # Fallback response
        return ChatResponse(
            response="I'm sorry, I'm having trouble responding right now. Please try asking about African recipes or cooking tips!",
            provider_used="fallback",
            generation_time=0.0,
            fallback_used=True
        )

@router.get("/suggestions")
async def get_chat_suggestions():
    """
    Get suggested questions/topics for the chatbot
    """
    suggestions = [
        "What's a good Nigerian breakfast recipe?",
        "How do I make authentic jollof rice?",
        "What are healthy African vegetarian dishes?",
        "Can you suggest a quick Kenyan dinner?",
        "What spices are essential for Ethiopian cooking?",
        "How do I prepare traditional South African bobotie?",
        "What's a good substitute for cassava flour?",
        "Tell me about Moroccan tagine cooking techniques"
    ]
    
    return {"suggestions": suggestions}

@router.post("/feedback")
async def submit_chat_feedback(feedback: dict):
    """
    Submit feedback about chat responses for improvement
    """
    try:
        # Log feedback for analysis
        logger.info(f"Chat feedback received: {feedback}")
        
        # In a production app, you'd store this in a database
        return {"status": "success", "message": "Thank you for your feedback!"}
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
