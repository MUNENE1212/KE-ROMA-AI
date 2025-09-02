import re
import html
from typing import List, Dict, Any
import logging

class SecurityUtils:
    """Security utilities for input validation and sanitization"""
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not text:
            return ""
        
        # Truncate if too long
        text = text[:max_length]
        
        # HTML escape
        text = html.escape(text)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate Kenyan phone number format"""
        if not phone:
            return False
        
        # Remove any spaces or special characters
        phone = re.sub(r'[^\d]', '', phone)
        
        # Check format: 254XXXXXXXXX (Kenyan format)
        return bool(re.match(r'^254[0-9]{9}$', phone))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username or len(username) < 3 or len(username) > 30:
            return False
        
        # Only alphanumeric and underscores
        return bool(re.match(r'^[a-zA-Z0-9_]+$', username))
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """Check password strength and return feedback"""
        issues = []
        score = 0
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters")
        else:
            score += 1
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password should contain uppercase letters")
        else:
            score += 1
            
        if not re.search(r'[a-z]', password):
            issues.append("Password should contain lowercase letters")
        else:
            score += 1
            
        if not re.search(r'\d', password):
            issues.append("Password should contain numbers")
        else:
            score += 1
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password should contain special characters")
        else:
            score += 1
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        strength = strength_levels[min(score, 4)]
        
        return {
            "is_valid": len(issues) == 0 or score >= 3,
            "strength": strength,
            "score": score,
            "issues": issues
        }
    
    @staticmethod
    def sanitize_recipe_data(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize recipe data to prevent injection attacks"""
        sanitized = {}
        
        for key, value in recipe_data.items():
            if isinstance(value, str):
                sanitized[key] = SecurityUtils.sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    SecurityUtils.sanitize_input(str(item)) if isinstance(item, str) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                sanitized[key] = SecurityUtils.sanitize_recipe_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def log_security_event(event_type: str, details: str, ip_address: str = None):
        """Log security events for monitoring"""
        logging.warning(f"SECURITY_EVENT: {event_type} - {details} - IP: {ip_address}")
