from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

router = APIRouter()

class CookingRequest(BaseModel):
    recipe_data: Dict[str, Any]
    user_id: Optional[str] = None

class NextStepRequest(BaseModel):
    session_id: str
    current_step: int

class TimerRequest(BaseModel):
    duration: int = 5
    label: str = "Cooking Timer"

class VoiceCommandRequest(BaseModel):
    command: str

@router.post("/start-cooking")
async def start_cooking(request: CookingRequest):
    """Start cooking mode with realtime guidance"""
    try:
        if not request.recipe_data:
            raise HTTPException(status_code=400, detail="Recipe data required")

        # Create cooking session
        cooking_session = {
            "session_id": f"cook_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "recipe": request.recipe_data,
            "started_at": datetime.now().isoformat(),
            "current_step": 0,
            "total_steps": len(request.recipe_data.get('instructions', [])),
            "timers": [],
            "status": "active"
        }

        # Generate step-by-step guidance with timing
        enhanced_steps = []
        for i, instruction in enumerate(request.recipe_data.get('instructions', [])):
            step = {
                "step_number": i + 1,
                "instruction": instruction,
                "estimated_time": estimate_step_time(instruction),
                "tips": generate_cooking_tips(instruction),
                "temperature": extract_temperature(instruction),
                "techniques": extract_techniques(instruction)
            }
            enhanced_steps.append(step)

        cooking_session["enhanced_steps"] = enhanced_steps

        return {
            "success": True,
            "session": cooking_session,
            "message": "Cooking session started! Follow the step-by-step guidance."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next-step")
async def next_step(request: NextStepRequest):
    """Get next cooking step with guidance"""
    try:
        # In a real app, you'd fetch from database
        # For now, we'll simulate step progression

        cooking_tips = [
            "🔥 Heat control is key - medium heat works best for most sautéing",
            "🧂 Taste as you go and adjust seasoning gradually",
            "⏰ Don't rush the process - good food takes time",
            "🥄 Stir gently to preserve ingredient texture",
            "🌡️ Use a thermometer for perfect doneness"
        ]

        next_step_data = {
            "step_number": request.current_step + 1,
            "guidance": f"Step {request.current_step + 1} guidance ready",
            "tip": cooking_tips[request.current_step % len(cooking_tips)],
            "estimated_time_remaining": max(0, (10 - request.current_step) * 3),  # Simulate time
            "voice_command": f"Alexa, set timer for {3 + request.current_step} minutes"
        }

        return {
            "success": True,
            "next_step": next_step_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-timer")
async def set_timer(request: TimerRequest):
    """Set cooking timer"""
    try:
        timer = {
            "id": f"timer_{datetime.now().strftime('%H%M%S')}",
            "label": request.label,
            "duration": request.duration,
            "started_at": datetime.now().isoformat(),
            "ends_at": (datetime.now() + timedelta(minutes=request.duration)).isoformat(),
            "status": "active"
        }

        return {
            "success": True,
            "timer": timer,
            "message": f"Timer set for {request.duration} minutes"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-command")
async def voice_command(request: VoiceCommandRequest):
    """Process voice commands"""
    try:
        command = request.command.lower()

        responses = {
            "next step": "Moving to the next cooking step. Check your screen for details.",
            "set timer": "What duration would you like for the timer?",
            "how long left": "You have approximately 15 minutes remaining.",
            "temperature": "The recommended temperature is 180°C or medium heat.",
            "help": "I can help with timers, next steps, temperatures, and cooking tips.",
            "ingredients": "Here are the ingredients you need for this step...",
            "tips": "Here's a pro tip: taste as you cook and adjust seasoning gradually."
        }

        # Simple command matching
        response = "I didn't understand that command. Try 'next step', 'set timer', or 'help'."
        for key, value in responses.items():
            if key in command:
                response = value
                break

        return {
            "success": True,
            "response": response,
            "command_recognized": any(key in command for key in responses.keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nutrition-info")
async def nutrition_info(recipe_data: Dict[str, Any]):
    """Get nutrition information for current recipe"""
    try:
        # Simulate nutrition calculation
        nutrition = {
            "calories_per_serving": 320,
            "protein": "18g",
            "carbohydrates": "45g",
            "fat": "12g",
            "fiber": "8g",
            "sodium": "680mg",
            "health_score": 8.5,
            "dietary_info": ["High in fiber", "Good source of protein", "Contains iron"]
        }

        return {
            "success": True,
            "nutrition": nutrition
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def estimate_step_time(instruction):
    """Estimate time for cooking step"""
    instruction_lower = instruction.lower()
    
    if "boil" in instruction_lower:
        return "10-15 minutes"
    elif "sauté" in instruction_lower or "fry" in instruction_lower:
        return "5-8 minutes"
    elif "chop" in instruction_lower or "dice" in instruction_lower:
        return "3-5 minutes"
    elif "simmer" in instruction_lower:
        return "15-20 minutes"
    elif "bake" in instruction_lower:
        return "25-30 minutes"
    else:
        return "5 minutes"

def generate_cooking_tips(instruction):
    """Generate cooking tips for instruction"""
    tips = [
        "Keep ingredients at room temperature for even cooking",
        "Use a sharp knife for clean cuts",
        "Don't overcrowd the pan",
        "Season in layers for better flavor",
        "Let meat rest after cooking"
    ]
    return tips[len(instruction) % len(tips)]

def extract_temperature(instruction):
    """Extract temperature from instruction"""
    if "medium" in instruction.lower():
        return "Medium heat (180°C)"
    elif "high" in instruction.lower():
        return "High heat (220°C)"
    elif "low" in instruction.lower():
        return "Low heat (120°C)"
    else:
        return "Medium heat (180°C)"

def extract_techniques(instruction):
    """Extract cooking techniques"""
    techniques = []
    instruction_lower = instruction.lower()
    
    if "sauté" in instruction_lower:
        techniques.append("sautéing")
    if "boil" in instruction_lower:
        techniques.append("boiling")
    if "simmer" in instruction_lower:
        techniques.append("simmering")
    if "chop" in instruction_lower:
        techniques.append("knife skills")
    
    return techniques if techniques else ["basic cooking"]
