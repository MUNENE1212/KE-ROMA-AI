from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta

# Rate limiting storage
rate_limit_storage = defaultdict(list)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        
    async def dispatch(self, request: Request, call_next):
        # Rate limiting
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old entries
        rate_limit_storage[client_ip] = [
            timestamp for timestamp in rate_limit_storage[client_ip]
            if now - timestamp < timedelta(minutes=1)
        ]
        
        # Check rate limit
        if len(rate_limit_storage[client_ip]) >= self.calls_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Add current request
        rate_limit_storage[client_ip].append(now)
        
        # Security headers
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com"
        
        return response

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log suspicious requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                body_str = body.decode('utf-8').lower()
                
                # Check for common attack patterns
                suspicious_patterns = [
                    'union select', 'drop table', 'delete from',
                    '<script', 'javascript:', 'eval(',
                    '../', '..\\', 'etc/passwd'
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in body_str:
                        logging.warning(f"Suspicious request from {request.client.host}: {pattern}")
                        
            except Exception:
                pass  # Continue if body parsing fails
        
        response = await call_next(request)
        return response
