from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from models.database import init_db
from config.config import get_settings
from middleware.security import SecurityMiddleware, InputSanitizationMiddleware
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (if needed)

# Create FastAPI app
app = FastAPI(
    title="KE-ROUMA API",
    description="African Heritage Recipe Recommendation API",
    version="2.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(SecurityMiddleware, calls_per_minute=100)
app.add_middleware(InputSanitizationMiddleware)

# CORS middleware - Security hardened
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
from routes.main import router as main_router
from routes.recipes import router as recipes_router
from routes.chat import router as chat_router
from routes.payments import router as payments_router
from routes.auth import router as auth_router
from routes.users import router as users_router

# Serve static files for development
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers - main router first to handle root route
app.include_router(main_router, tags=["main"])
app.include_router(recipes_router, prefix="/api/recipes", tags=["recipes"])
app.include_router(payments_router, prefix="/api/payments", tags=["payments"])
app.include_router(auth_router, tags=["auth"])
app.include_router(users_router, tags=["users"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "KE-ROUMA"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)