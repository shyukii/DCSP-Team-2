"""
Utility functions for common message patterns and keyboard creation
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import List, Dict, Optional
from config import Config

# Common error messages
ERROR_MESSAGES = {
    "not_logged_in": "Please /start to login first.",
    "invalid_number": "❌ Please enter a valid positive number.",
    "setup_required": "⚠️ **Volume Setup Required**\n\nPlease set up your tank and soil volumes in /profile first!",
    "generic_error": "❌ Sorry, there was an error. Please try again.",
}

def get_error_message(error_type: str) -> str:
    """Get a standardized error message."""
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["generic_error"])

def create_back_menu_keyboard() -> InlineKeyboardMarkup:
    """Create a standard back to menu keyboard."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
    ]])


def create_keyboard_from_options(options: List[Dict[str, str]], columns: int = 1) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard from a list of options.
    
    Args:
        options: List of dicts with 'text' and 'callback_data' keys
        columns: Number of buttons per row
        
    Returns:
        InlineKeyboardMarkup object
    """
    keyboard = []
    row = []
    
    for i, option in enumerate(options):
        button = InlineKeyboardButton(
            text=option.get('text', ''),
            callback_data=option.get('callback_data', '')
        )
        row.append(button)
        
        if (i + 1) % columns == 0:
            keyboard.append(row)
            row = []
    
    # Add remaining buttons if any
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

def format_user_profile(user_data: Dict) -> str:
    """Format user profile data for display."""
    tank_vol = user_data.get("tank_volume", 0)
    soil_vol = user_data.get("soil_volume", 0)
    
    return (
        f"👤 **Your Profile**\n\n"
        f"🪣 Tank Volume: {tank_vol} L\n"
        f"🌱 Soil Volume: {soil_vol} L"
    )

def validate_positive_number(text: str, max_value: Optional[float] = None) -> tuple[bool, float]:
    """
    Validate that text is a positive number.
    
    Returns:
        Tuple of (is_valid, parsed_value)
    """
    try:
        value = float(text.strip())
        if value <= 0:
            return False, 0.0
        if max_value and value > max_value:
            return False, 0.0
        return True, value
    except ValueError:
        return False, 0.0

def get_cached_user_data(telegram_id: int, context: ContextTypes.DEFAULT_TYPE) -> Optional[Dict]:
    """
    Get user data from cache or database. 
    Caches result in context.user_data to avoid repeated DB calls.
    
    Args:
        telegram_id: Telegram user ID
        context: Bot context containing user_data cache
        
    Returns:
        User data dict or None if user not found
    """
    # Check cache first
    cached_data = context.user_data.get("profile_data")
    if cached_data:
        return cached_data
    
    # Fetch from database and cache
    from services.database import db
    user_data = db.get_user_by_telegram_id(telegram_id)
    if user_data:
        context.user_data["profile_data"] = user_data
    
    return user_data

def clear_user_cache(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear cached user data. Call after profile updates."""
    context.user_data.pop("profile_data", None)