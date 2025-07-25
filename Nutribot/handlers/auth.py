from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CommandHandler
import asyncio
import logging

from constants import (
    AMA, AUTH_CHOICE, REGISTER_USERNAME, REGISTER_PASSWORD,
    LOGIN_USERNAME, LOGIN_PASSWORD, PLANT_SPECIES, TANK_VOLUME, SOIL_VOLUME, MAIN_MENU,
    WELCOME_MESSAGE, REGISTRATION_MESSAGE, GLOSSARY_MESSAGE
)
from services.database import db
# from services.clarifai_segmentation import ClarifaiImageSegmentation  # Unused import - removed to fix Windows compatibility
from handlers.menu import show_main_menu

logger = logging.getLogger(__name__)

# -- start & help --

async def direct_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **NutriBot is now active!**\n\n"
        "I'm connecting to the system...\n"
        "Type /start again to begin the login process."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telegram_id = update.effective_user.id
    logger.info(f"Start command received from user {telegram_id}")
    
    loading = await update.message.reply_text("🔄 Loading NutriBot...")
    await asyncio.sleep(0.5)
    
    # Check if user exists in database
    existing_user = db.get_user_by_telegram_id(telegram_id)
    
    await loading.delete()
    
    if existing_user:
        # Auto-authenticate user
        context.user_data["username"] = existing_user["username"]
        context.user_data["telegram_id"] = telegram_id
        context.user_data["user_db"] = existing_user
        
        # Check if profile is complete
        if db.is_profile_complete(telegram_id):
            await update.message.reply_text(
                f"Welcome back, {existing_user['username']}! 🌱\n"
                f"You've been automatically authenticated."
            )
            return await show_main_menu(update, context, existing_user['username'])
        else:
            # Complete profile setup
            kb = [
                [InlineKeyboardButton("Lady's Finger", callback_data="ladysfinger"),
                 InlineKeyboardButton("Spinach",        callback_data="spinach"),
                 InlineKeyboardButton("Long Bean",      callback_data="longbean")]
            ]
            await update.message.reply_text(
                f"Welcome back, {existing_user['username']}! Let's complete your profile.\n"
                f"Please select your plant species:",
                reply_markup=InlineKeyboardMarkup(kb)
            )
            return PLANT_SPECIES
    
    # New user - show registration/login options
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")
    kb = [
        [InlineKeyboardButton("Register", callback_data="register"),
         InlineKeyboardButton("Login",    callback_data="login")]
    ]
    await update.message.reply_text(
        "Please select an option to get started:",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return AUTH_CHOICE

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from constants import HELP_MESSAGE
    await update.message.reply_text(HELP_MESSAGE)

# -- auth choice callback --

async def auth_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    if q.data == "register":
        await q.edit_message_text("You selected registration. Please enter a username:")
        return REGISTER_USERNAME
    else:
        await q.edit_message_text("You selected login. Please enter your username:")
        return LOGIN_USERNAME

# -- registration flow --

async def register_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["username"] = update.message.text
    await update.message.reply_text("Now please create a password:")
    return REGISTER_PASSWORD

async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pwd = update.message.text
    username = context.user_data["username"]
    telegram_id = update.effective_user.id
    
    # Check if username already exists
    existing_user = db.get_user_by_username(username)
    if existing_user:
        await update.message.reply_text("Username already exists. Please try a different one:")
        return REGISTER_USERNAME
    
    # Create user in database
    new_user = db.create_user(telegram_id, username, pwd)
    if not new_user:
        await update.message.reply_text("Registration failed. Please try again later.")
        return ConversationHandler.END
    
    context.user_data["telegram_id"] = telegram_id
    context.user_data["user_db"] = new_user

    await update.message.reply_text(REGISTRATION_MESSAGE)
    await update.message.reply_text(GLOSSARY_MESSAGE)

    kb = [
        [InlineKeyboardButton("Lady's Finger", callback_data="ladysfinger"),
         InlineKeyboardButton("Spinach",        callback_data="spinach"),
         InlineKeyboardButton("Long Bean",      callback_data="longbean")]
    ]
    await update.message.reply_text(
        f"Registration successful, {username}! Select your plant species:",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return PLANT_SPECIES

# -- login flow --

async def login_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["login_username"] = update.message.text
    await update.message.reply_text("Now please enter your password:")
    return LOGIN_PASSWORD

async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pwd = update.message.text
    username = context.user_data.get("login_username")
    telegram_id = update.effective_user.id
    
    # Authenticate user
    user = db.authenticate_user(username, pwd)
    
    if user:
        # Update telegram_id if not set or different
        if user['telegram_id'] != telegram_id:
            user = db.update_user_profile(telegram_id, telegram_id=telegram_id)
        
        context.user_data["username"] = username
        context.user_data["telegram_id"] = telegram_id
        context.user_data["user_db"] = user
        
        # Check if profile is complete
        if db.is_profile_complete(telegram_id):
            return await show_main_menu(update, context, username)
        
        # Complete setup
        kb = [
            [InlineKeyboardButton("Lady's Finger", callback_data="ladysfinger"),
             InlineKeyboardButton("Spinach",        callback_data="spinach"),
             InlineKeyboardButton("Long Bean",      callback_data="longbean")]
        ]
        await update.message.reply_text(
            f"Welcome back, {username}! Complete setup—select plant species:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return PLANT_SPECIES
    
    await update.message.reply_text("Invalid credentials, try again.")
    return LOGIN_USERNAME

# -- setup callbacks --

async def plant_species(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    species = q.data
    context.user_data["plant_species"] = species
    
    telegram_id = context.user_data.get("telegram_id", update.effective_user.id)
    
    # Update in database
    db.update_user_profile(telegram_id, plant_species=species)

    await q.edit_message_text(f"You selected {species}. Enter your compost tank volume (litres):")
    return TANK_VOLUME

async def tank_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        vol = float(update.message.text)
        if vol <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("Enter a valid positive number.")
        return TANK_VOLUME

    telegram_id = context.user_data.get("telegram_id", update.effective_user.id)
    
    # Update in database
    db.update_user_profile(telegram_id, tank_volume=vol)

    await update.message.reply_text("Now enter your soil volume (litres):")
    return SOIL_VOLUME

async def soil_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        vol = float(update.message.text)
        if vol <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("Enter a valid positive number.")
        return SOIL_VOLUME

    telegram_id = context.user_data.get("telegram_id", update.effective_user.id)
    username = context.user_data.get("username") or context.user_data.get("login_username")
    
    # Update in database
    db.update_user_profile(telegram_id, soil_volume=vol)

    return await show_main_menu(update, context, username)

# -- cancel / end --

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled. Type /start to begin again.")
    context.user_data.clear()
    return ConversationHandler.END
