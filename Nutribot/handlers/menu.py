from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.file_utils import load_user_credentials, save_user_credentials
from constants import MAIN_MENU
from services.clarifai_segmentation import ClarifaiImageSegmentation

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str) -> int:
    creds = load_user_credentials()
    species = creds[username].get("plant_species","plants")

    kb = [
        [InlineKeyboardButton("📦 Compost Feeding", callback_data="compost_feed"),
         InlineKeyboardButton("Compost Extraction", callback_data="compost_extract")],
        [InlineKeyboardButton("🪴 Ask Anything ",    callback_data="start_llama")],
        [InlineKeyboardButton("📈 CO2 Tracker", callback_data="co2_tracker")],
        [InlineKeyboardButton("📸 Image Scan",  callback_data="image_scan")],
        [InlineKeyboardButton("❓ Help",         callback_data="help_commands")]
    ]
    markup = InlineKeyboardMarkup(kb)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"Setup complete, {username}! Your {species} data is saved.\n\n"
            "What would you like to do?",
            reply_markup=markup
        )
    else:
        await update.message.reply_text(
            f"Welcome, {username}! Let's care for your {species}.\n\n"
            "Choose an option:",
            reply_markup=markup
        )
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    choice = q.data
    user   = context.user_data.get("username")

    # Handle calculator choices
    if choice in ["use_calculator", "basic_guidelines", "back_to_menu"]:
        from handlers.commands import handle_calculator_choice
        return await handle_calculator_choice(update, context)

    if choice == "start_llama":
        await q.edit_message_text("I'm Llama and I'm here to help you with your plants!!")
        from constants import AMA
        return AMA

    # compost help submenu
    if choice == "compost_feed":
        keyboard = [
            [InlineKeyboardButton("🧮 Feed Calculator", callback_data="use_calculator")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await q.edit_message_text(
            "🥕 **Food & Water Input Guide**\n\n"
            "Choose how you'd like to get feeding recommendations:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return MAIN_MENU
    if choice == "compost_extract":
        # Get user credentials to check tank volume
        creds = load_user_credentials()
        tank_vol = creds[user].get("tank_volume", 0)
        soil_vol = creds[user].get("soil_volume", 0)
        
        # Create back button
        kb = [[InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(kb)
        
        # Send status message (same as status_command)
        await q.edit_message_text(
            "🧪 **Compost Status Check**\n\n"
            "Based on your setup, your compost is approximately 65% ready.\n"
            "Estimated time to full maturity: 2-3 weeks.\n\n"
            "The moisture level appears normal and bacterial activity is good.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return MAIN_MENU
    if choice == "co2_tracker":
        kb = [
            [InlineKeyboardButton("View Impact", callback_data="co2_impact"),
             InlineKeyboardButton("Add Compost", callback_data="co2_add")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
        ]
        await q.edit_message_text(
            "🌍 **CO₂ Tracker**\n\nTrack your compost’s impact!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return MAIN_MENU

    if choice == "image_scan":
        kb = [[InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]]
        await q.edit_message_text(
            "📸 **Image Scan**\nSend me a photo to analyse.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return MAIN_MENU

    # profile updates
    if choice == "change_plant":
        kb = [
            [InlineKeyboardButton("Lady's Finger", callback_data="update_plant_ladysfinger"),
             InlineKeyboardButton("Spinach",       callback_data="update_plant_spinach"),
             InlineKeyboardButton("Long Bean",     callback_data="update_plant_longbean")],
            [InlineKeyboardButton("Back to Profile", callback_data="back_to_profile")]
        ]
        await q.edit_message_text("Select your new plant type:", reply_markup=InlineKeyboardMarkup(kb))
        return MAIN_MENU

    if choice == "change_volume":
        kb = [[InlineKeyboardButton("Back to Profile", callback_data="back_to_profile")]]
        await q.edit_message.reply_text(
            "Send a message with your new tank volume (litres) followed by soil volume (litres).",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return MAIN_MENU

    if choice.startswith("update_plant_"):
        new = choice.split("update_plant_")[-1]
        creds = load_user_credentials()
        creds[user]["plant_species"] = new
        save_user_credentials(creds)
        await q.edit_message_text(
            f"Your plant type has been updated to {new}!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Profile", callback_data="back_to_profile")]])
        )
        return MAIN_MENU

    if choice == "back_to_profile":
        from handlers.commands import profile_command
        await profile_command(update, context)
        return MAIN_MENU

    if choice == "help_commands":
        from constants import HELP_MESSAGE
        await q.edit_message_text(
            HELP_MESSAGE,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]])
        )
        return MAIN_MENU

    if choice == "back_to_menu":
        return await show_main_menu(update, context, user)

    # fallback for unimplemented
    await q.edit_message_text(
        f"You selected {choice}. This feature is coming soon!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]])
    )
    return MAIN_MENU
