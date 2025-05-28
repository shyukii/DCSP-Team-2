from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CommandHandler
import asyncio
import logging

from constants import (
    AMA, AUTH_CHOICE, REGISTER_USERNAME, REGISTER_PASSWORD,
    LOGIN_USERNAME, LOGIN_PASSWORD, PLANT_SPECIES, COMPOST_VOLUME, MAIN_MENU,
    WELCOME_MESSAGE
)
from utils.file_utils import load_user_credentials, save_user_credentials
from services.clarifai_segmentation import ClarifaiImageSegmentation
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
    logger.info(f"Start command received from user {update.effective_user.id}")
    loading = await update.message.reply_text("🔄 Loading NutriBot...")
    await asyncio.sleep(0.5)
    await loading.delete()
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
    user = context.user_data["username"]
    creds = load_user_credentials()
    if user in creds:
        await update.message.reply_text("Username exists—try a different one.")
        return REGISTER_USERNAME
    creds[user] = {"password": pwd}
    save_user_credentials(creds)

    kb = [
        [InlineKeyboardButton("Lady's Finger", callback_data="ladysfinger"),
         InlineKeyboardButton("Spinach",        callback_data="spinach"),
         InlineKeyboardButton("Long Bean",      callback_data="longbean")]
    ]
    await update.message.reply_text(
        f"Registration successful, {user}! Select your plant species:",
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
    user = context.user_data.get("login_username")
    creds = load_user_credentials()

    if user in creds and creds[user]["password"] == pwd:
        context.user_data["username"] = user
        user_data = creds[user]
        if "plant_species" in user_data and "compost_volume" in user_data:
            return await show_main_menu(update, context, user)
        # else, complete setup
        kb = [
            [InlineKeyboardButton("Lady's Finger", callback_data="ladysfinger"),
             InlineKeyboardButton("Spinach",        callback_data="spinach"),
             InlineKeyboardButton("Long Bean",      callback_data="longbean")]
        ]
        await update.message.reply_text(
            f"Welcome back, {user}! Complete setup—select plant species:",
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

    user = context.user_data.get("username") or context.user_data.get("login_username")
    creds = load_user_credentials()
    creds[user]["plant_species"] = species
    save_user_credentials(creds)

    await q.edit_message_text(f"You selected {species}. Enter your compost volume (litres):")
    return COMPOST_VOLUME

async def compost_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        vol = float(update.message.text)
        if vol <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("Enter a valid positive number.")
        return COMPOST_VOLUME

    user = context.user_data.get("username") or context.user_data.get("login_username")
    creds = load_user_credentials()
    creds[user]["compost_volume"] = vol
    save_user_credentials(creds)

    return await show_main_menu(update, context, user)

# -- cancel / end --

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled. Type /start to begin again.")
    context.user_data.clear()
    return ConversationHandler.END
