from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.file_utils import load_user_credentials, save_user_credentials
from constants import MAIN_MENU
from services.clarifai_segmentation import ClarifaiImageSegmentation
import os

# Initialize clarifai service
clarifai = ClarifaiImageSegmentation()

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

async def handle_photo_from_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo processing when user sends image after selecting image_scan from menu"""
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return MAIN_MENU
    
    if not context.user_data.get("expecting_image"):
        await update.message.reply_text("Use the Image Scan option from the menu first.")
        return MAIN_MENU

    context.user_data["expecting_image"] = False
    processing = await update.message.reply_text("🔄 Analysing your image...")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    path = f"temp_{update.effective_user.id}.jpg"
    await file.download_to_drive(path)

    try:
        top = clarifai.get_top_concepts(path, top_n=5)
        text = "🔍 **Image Analysis Results**\n\n**Top elements:**\n"
        for i,c in enumerate(top,1):
            text += f"{i}. {c['name'].title()}: {round(c['value']*100,1)}%\n"
        text += "\n💡 Ask me questions about what you see!"
    except Exception:
        text = "⚠️ Could not analyse image. Try a clearer photo."

    try: 
        os.remove(path)
    except: 
        pass

    await processing.delete()
    
    # Create back to menu button
    kb = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(kb)
    
    await update.message.reply_text(
        text, 
        parse_mode="Markdown",
        reply_markup=reply_markup
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
    
    # Handle CO2 calculator callbacks
    if choice.startswith("co2_") and choice not in ["co2_tracker", "co2_impact", "co2_add"]:
        from services.extraction_timing import handle_co2_callback
        return await handle_co2_callback(update, context)

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
            "🌍 **CO₂ Tracker**\n\nTrack your compost's impact!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return MAIN_MENU

    if choice == "image_scan":
        # Create back button
        kb = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        
        # Send instruction message and set expecting_image flag
        await q.edit_message_text(
            "📸 **Image Analysis**\n\n"
            "Send a photo of your compost or plants!\n"
            "Ensure good lighting and focus.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        context.user_data["expecting_image"] = True
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
        await q.edit_message_text(
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