"""
Helper utilities for the Healthcare Assistant Frontend
"""
from datetime import datetime
from typing import Dict, Any


def format_timestamp(timestamp: datetime = None) -> str:
    """
    Format a timestamp for display

    Args:
        timestamp: Datetime object (defaults to now)

    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%I:%M %p")


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_message(message: str, max_length: int = 2000) -> tuple[bool, str]:
    """
    Validate a chat message

    Args:
        message: Message text to validate
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Message cannot be empty"

    if len(message) > max_length:
        return False, f"Message too long (max {max_length} characters)"

    return True, ""


def get_agent_avatar() -> str:
    """Get avatar emoji for the assistant"""
    return "🤖"


def get_user_avatar() -> str:
    """Get avatar emoji for the user"""
    return "👤"


def format_error_message(error: Exception) -> str:
    """
    Format an error message for display

    Args:
        error: Exception object

    Returns:
        User-friendly error message
    """
    error_str = str(error)

    if "connection" in error_str.lower():
        return "❌ Unable to connect to the healthcare assistant. Please check your connection."

    if "timeout" in error_str.lower():
        return "⏱️ Request timed out. The assistant may be processing a complex query. Please try again."

    if "404" in error_str:
        return "❌ Service not found. Please contact support."

    if "500" in error_str or "503" in error_str:
        return "❌ The healthcare assistant is temporarily unavailable. Please try again later."

    return f"❌ An error occurred: {error_str}"
