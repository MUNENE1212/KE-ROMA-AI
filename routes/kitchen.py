from flask import Blueprint, jsonify, request
from services.ai_service import AIService
import json
from datetime import datetime, timedelta

kitchen_bp = Blueprint('kitchen', __name__)

@kitchen_bp.route('/api/kitchen/start-cooking', methods=['POST'])
def start_cooking():
    """Start cooking mode with realtime guidance"""
    try:
        data = request.get_json()
        recipe_id = data.get('recipe_id')
        recipe_data = data.get('recipe_data')
        
        if not recipe_data:
            return jsonify({"error": "Recipe data required"}), 400
        
        # Create cooking session
        cooking_session = {
            "session_id": f"cook_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "recipe": recipe_data,
            "started_at": datetime.now().isoformat(),
            "current_step": 0,
            "total_steps": len(recipe_data.get('instructions', [])),
            "timers": [],
            "status": "active"
        }
        
        # Generate step-by-step guidance with timing
        enhanced_steps = []
        for i, instruction in enumerate(recipe_data.get('instructions', [])):
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
        
        return jsonify({
            "success": True,
            "session": cooking_session,
            "message": "Cooking session started! Follow the step-by-step guidance."
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@kitchen_bp.route('/api/kitchen/next-step', methods=['POST'])
def next_step():
    """Get next cooking step with guidance"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        current_step = data.get('current_step', 0)
        
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
            "step_number": current_step + 1,
            "guidance": f"Step {current_step + 1} guidance ready",
            "tip": cooking_tips[current_step % len(cooking_tips)],
            "estimated_time_remaining": max(0, (10 - current_step) * 3),  # Simulate time
            "voice_command": f"Alexa, set timer for {3 + current_step} minutes"
        }
        
        return jsonify({
            "success": True,
            "next_step": next_step_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@kitchen_bp.route('/api/kitchen/set-timer', methods=['POST'])
def set_timer():
    """Set cooking timer"""
    try:
        data = request.get_json()
        duration = data.get('duration', 5)  # minutes
        label = data.get('label', 'Cooking Timer')
        
        timer = {
            "id": f"timer_{datetime.now().strftime('%H%M%S')}",
            "label": label,
            "duration": duration,
            "started_at": datetime.now().isoformat(),
            "ends_at": (datetime.now() + timedelta(minutes=duration)).isoformat(),
            "status": "active"
        }
        
        return jsonify({
            "success": True,
            "timer": timer,
            "message": f"Timer set for {duration} minutes"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@kitchen_bp.route('/api/kitchen/voice-command', methods=['POST'])
def voice_command():
    """Process voice commands"""
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
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
        
        return jsonify({
            "success": True,
            "response": response,
            "command_recognized": any(key in command for key in responses.keys())
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@kitchen_bp.route('/api/kitchen/nutrition-info', methods=['POST'])
def nutrition_info():
    """Get nutrition information for current recipe"""
    try:
        data = request.get_json()
        recipe_data = data.get('recipe_data')
        
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
        
        return jsonify({
            "success": True,
            "nutrition": nutrition
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
