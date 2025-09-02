import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

# Force load environment variables from .env file
load_dotenv(override=True)

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields like flask_env
    )
    
    # App Configuration
    app_name: str = "KE-ROUMA"
    debug: bool = False
    
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "kerouma"
    
    # AI Configuration
    openai_api_key: str = ""
    gemini_api_key: str = ""
    huggingface_api_key: str = ""
    cohere_api_key: str = ""
    
    # Payment Configuration
    intasend_publishable_key: str = ""
    intasend_secret_key: str = ""
    intasend_base_url: str = "https://sandbox.intasend.com/api/v1"
    premium_price: int = 100
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"

@lru_cache()
def get_settings():
    # Clear cache to ensure fresh environment loading
    import os
    print(f"Loading settings from: {os.getcwd()}")
    print(f"INTASEND_PUBLISHABLE_KEY from env: {os.getenv('INTASEND_PUBLISHABLE_KEY', 'NOT SET')}")
    return Settings()