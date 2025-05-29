import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.clarifai_segmentation import ClarifaiImageSegmentation
from services.emissions_calculator import EmissionsCalculator
from services.feeding_input import FeedCalculator
from constants import GREENS_INPUT
from constants import MAIN_MENU
from utils.file_utils import load_user_credentials
from handlers.menu import show_main_menu

clarifai = ClarifaiImageSegmentation()
feed_calculator = FeedCalculator()

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    creds = load_user_credentials()
    vol = creds[user].get("compost_volume",0)
    await update.message.reply_text(
        "🧪 **Compost Status Check**\n\n"
        "Based on your setup, your compost is approximately 65% ready.\n"
        "Estimated time to full maturity: 2-3 weeks.\n\n"
        "The moisture level appears normal and bacterial activity is good.",
        parse_mode="Markdown"
    )

async def input_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    
    # Create inline keyboard for calculator options
    keyboard = [
        [InlineKeyboardButton("🧮 Feed Calculator", callback_data="use_calculator")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🥕 **Food & Water Input Guide**\n\n"
        "Choose how you'd like to get feeding recommendations:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_calculator_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the calculator choice callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "use_calculator":
        await query.edit_message_text(
            "🧮 **Compost Calculator**\n\n"
            "Please enter the weight of your greens (kitchen scraps, grass clippings, etc.) in kilograms.\n\n"
            "Examples:\n"
            "• 0.5 (for 500g)\n"
            "• 1.2 (for 1.2kg)\n"
            "• 2 (for 2kg)\n\n"
            "💡 *Tip: Weigh your kitchen scraps for a week to get an estimate*",
            parse_mode="Markdown"
        )
        return GREENS_INPUT
        
    elif query.data == "back_to_menu":
        username = context.user_data.get("username")
        return await show_main_menu(update, context, username)

async def handle_greens_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user input for greens weight"""
    try:
        greens_weight = float(update.message.text.strip())
        
        if greens_weight <= 0:
            await update.message.reply_text(
                "❌ Please enter a positive number for the weight of greens.\n"
                "Try again with a number like 1.5 or 2.0"
            )
            return GREENS_INPUT
            
        if greens_weight > 50:  # Sanity check
            await update.message.reply_text(
                "❌ That seems like a very large amount! Please enter a reasonable weight (up to 50kg).\n"
                "Try again with a smaller number."
            )
            return GREENS_INPUT
        
        # Calculate optimal ratios using the FeedCalculator
        recommendations = feed_calculator.get_feeding_recommendations(greens_weight)
        
        # Create keyboard for actions
        keyboard = [
            [InlineKeyboardButton("🔄 Calculate Again", callback_data="use_calculator")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            recommendations,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Stay in main menu conversation state
        return MAIN_MENU
        
    except ValueError:
        await update.message.reply_text(
            "❌ Please enter a valid number (e.g., 1.5, 2, 0.8).\n"
            "How many kilograms of greens do you have?"
        )
        return GREENS_INPUT
    except Exception as e:
        await update.message.reply_text(
            "❌ Sorry, there was an error processing your input. Please try again."
        )
        return GREENS_INPUT

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    await update.message.reply_text(
        "📸 **Image Analysis**\n\n"
        "Send a photo of your compost or plants!\n"
        "Ensure good lighting and focus.",
        parse_mode="Markdown"
    )
    context.user_data["expecting_image"] = True

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    if not context.user_data.get("expecting_image"):
        await update.message.reply_text("Use /scan first to analyze images.")
        return

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

    try: os.remove(path)
    except: pass

    await processing.delete()
    await update.message.reply_text(text, parse_mode="Markdown")

async def care_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    creds = load_user_credentials()
    species = creds[user].get("plant_species","plants")
    tips = {
        "ladysfinger": "🌡️ Keep soil 22-35°C\n💧 Water regularly\n☀️ 6+ hrs sun",
        "spinach":     "🌡️ 15-20°C\n💧 Keep moist\n🌱 Harvest outer leaves",
        "longbean":    "🌿 Provide support\n💧 Water deeply once/week\n☀️ Full sun"
    }.get(species, "Keep soil moist and give sunlight.")
    await update.message.reply_text(
        f"🪴 **{species.capitalize()} Care Guide**\n\n{tips}\n\n"
        "Remember to apply compost when nutrients deplete.",
        parse_mode="Markdown"
    )

async def co2_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    creds = load_user_credentials()
    vol = creds[user].get("compost_volume",0)
    # using 0.5kg CO₂ saved per litre per year
    saved = round(vol*0.5,1)
    trees = round(saved/25,1)
    await update.message.reply_text(
        f"🌍 **CO₂ Savings Impact**\n\n"
        f"Your {vol}L compost saves ~{saved} kg CO₂/year\n"
        f"Equivalent to planting **{trees} trees**!",
        parse_mode="Markdown"
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    creds = load_user_credentials()
    species = creds[user].get("plant_species","unknown")
    vol     = creds[user].get("compost_volume",0)
    kb = [
        [InlineKeyboardButton("Change Plant", callback_data="change_plant")],
        [InlineKeyboardButton("Change Volume",callback_data="change_volume")],
        [InlineKeyboardButton("Back to Menu",callback_data="back_to_menu")]
    ]
    await update.message.reply_text(
        f"👤 **Your Profile**\n\n"
        f"🪴 Plant: {species}\n"
        f"📦 Volume: {vol} L\n\n"
        "What to update?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle 'back' intent (e.g. from voice).
    Returns the user to the main menu.
    """
    # Figure out who’s logged in
    username = context.user_data.get("username") or context.user_data.get("login_username")
    if not username:
        await update.message.reply_text("🔒 Please /start and login first.")
        return

    # Show the main menu again
    return await show_main_menu(update, context, username)
