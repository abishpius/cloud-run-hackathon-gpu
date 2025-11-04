"""
Configuration settings for Healthcare Assistant Frontend
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings and configuration"""

    # Backend API Configuration
    BACKEND_API_URL: str = os.getenv(
        "BACKEND_API_URL",
        "http://localhost:8080"  # Default for local development
    )

    # Application Configuration
    APP_NAME: str = "Healthcare Assistant"
    APP_SUBTITLE: str = "Your AI-Powered Primary Care Companion"

    # Page Configuration
    PAGE_TITLE: str = "Dr. Cloud - Healthcare Assistant"
    PAGE_ICON: str = "🏥"
    LAYOUT: str = "wide"

    # Authentication Configuration
    COOKIE_NAME: str = "healthcare_assistant_auth"
    COOKIE_KEY: str = os.getenv("COOKIE_KEY", "healthcare_secret_key_change_in_production")
    COOKIE_EXPIRY_DAYS: int = 30

    # Chat Configuration
    MAX_MESSAGE_LENGTH: int = 2000
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "false").lower() == "true"

    # API Timeouts
    API_TIMEOUT: int = 300  # 5 minutes for long-running agent responses

    # UI Configuration
    SHOW_DISCLAIMER: bool = True
    DISCLAIMER_TEXT: str = (
        "⚠️ **Medical Disclaimer**: This system is for informational purposes only "
        "and is NOT a substitute for professional medical advice, diagnosis, or treatment. "
        "Always seek the advice of qualified health providers."
    )

    # User Database (for simple auth - use external auth in production)
    USERS_FILE: str = os.getenv("USERS_FILE", "config/users.yaml")

    @classmethod
    def get_backend_url(cls, endpoint: str = "") -> str:
        """Get full backend API URL for an endpoint"""
        base_url = cls.BACKEND_API_URL.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base_url}/{endpoint}" if endpoint else base_url


# Singleton instance
settings = Settings()
