"""
Application Settings Loader.
Loads configuration values from environment variables or defaults.
"""

import os
from dotenv import load_dotenv

# Load .env file if available
load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "PCIF - Patient Context Intelligence Framework")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "pcif_database")


settings = Settings()
