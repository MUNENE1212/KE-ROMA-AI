from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web application"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KE-ROUMA API"}

@router.get("/info")
async def app_info():
    """Get application information"""
    return {
        "name": "KE-ROUMA",
        "description": "African Heritage Recipe Recommendation System",
        "version": "2.0.0",
        "features": [
            "AI-powered recipe generation",
            "User management",
            "Premium subscriptions",
            "M-Pesa payments",
            "Recipe saving and sharing"
        ]
    }
