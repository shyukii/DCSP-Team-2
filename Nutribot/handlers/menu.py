from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from services.database import db
from utils.message_utils import get_cached_user_data, clear_user_cache
from constants import MAIN_MENU, CO2_FOOD_WASTE_INPUT, COMPOST_HELPER_INPUT, AMA, SCAN_TYPE_SELECTION
# from services.clarifai_segmentation import ClarifaiImageSegmentation  # Lazy loaded when needed
import os

# Remove global clarifai instantiation - use lazy loading instead

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str = None) -> int:
    context.user_data.pop("state", None)  # Clear AMA flag if returning
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    username = username or context.user_data.get("username", "there")  # fallback name

    # Clear AMA flag if returning from LLM mode
    context.user_data.pop("state", None)

    # If username wasn’t passed in, fall back to stored context
    username = username or context.user_data.get("username")

    telegram_id = update.effective_user.id
    user_data  = get_cached_user_data(telegram_id, context)

    kb = [
        [InlineKeyboardButton("📦 Compost Feeding", callback_data="compost_feed"),
         InlineKeyboardButton("💩 Compost Extraction", callback_data="compost_extract")],
        [InlineKeyboardButton("🪴 Ask Anything ",    callback_data="start_llama")],
        [InlineKeyboardButton("📈 CO2 Tracker", callback_data="co2_tracker")],
        [InlineKeyboardButton("📸 Image Scan",  callback_data="image_scan")],
        [InlineKeyboardButton("❓ Help",         callback_data="help_commands")]
    ]
    markup = InlineKeyboardMarkup(kb)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"Setup complete, {username}! Your compost setup is saved.\n\n"
            "What would you like to do?",
            reply_markup=markup
        )
    else:
        await update.message.reply_text(
            f"Welcome, {username}! Let's care for your compost.\n\n"
            "Choose an option:",
            reply_markup=markup
        )
    return MAIN_MENU

async def back_to_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Clear various state flags
    context.user_data.pop("state", None)
    context.user_data.pop("scan_mode", None)
    context.user_data.pop("scan_type", None)
    context.user_data.pop("expecting_image", None)
    # Call the existing menu (no username arg)
    return await show_main_menu(update, context)

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
        # Lazy load Clarifai only when needed
        from services.clarifai_segmentation import ClarifaiImageSegmentation
        clarifai = ClarifaiImageSegmentation()
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

    # Handle calculator choices (both basic and ML)
    if choice in ["use_calculator", "use_ml_calculator", "basic_guidelines", "back_to_input"]:
        from handlers.commands import handle_calculator_choice
        return await handle_calculator_choice(update, context)
    
    # Handle ML crop selection
    if choice.startswith("crop_"):
        from handlers.commands import handle_ml_crop_selection
        return await handle_ml_crop_selection(update, context)
    
    # Handle CO2 calculator callbacks
    if choice.startswith("co2_") and choice not in ["co2_tracker", "co2_impact", "co2_add"]:
        from services.emissions_calculator import handle_co2_callback
        return await handle_co2_callback(update, context)
    
    # Handle scan type selection callbacks
    if choice in ["scan_compost", "scan_plant"]:
        from handlers.commands import handle_scan_type_choice
        return await handle_scan_type_choice(update, context)

    if choice == "start_llama":
        await q.edit_message_text(
            "I'm Llama and I'm here to help you with your plants!!\n\n"
            "You can now type or speak your question."
        )

        # ★ Mark the user as “in Ask‐Anything mode”:
        from constants import AMA
        context.user_data["state"] = AMA

        return AMA

    # compost help submenu
    if choice == "compost_feed":
        keyboard = [
            [InlineKeyboardButton("🧠 ML Smart Recommendations", callback_data="use_ml_calculator")],
            [InlineKeyboardButton("🧮 Basic Calculator", callback_data="use_calculator")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await q.edit_message_text(
            "🥕 **Food & Water Input Guide**\n\n"
            "Choose your recommendation method:\n\n"
            "🧠 **ML Smart**: Crop-specific recommendations based on historical data\n"
            "🧮 **Basic**: Simple ratio-based calculations\n\n"
            "Which would you prefer?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return MAIN_MENU
         
    if choice == "compost_helper":
        from handlers.commands import compost_helper_start
        return await compost_helper_start(update, context)
    
    if choice == "compost_extract":
        # build a single “Back to Menu” button
        kb = [[ InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu") ]]
        reply_markup = InlineKeyboardMarkup(kb)

        # show the estimate-calculator “page”
        await q.edit_message_text(
            "🌱 *Compost Estimate Calculator*\n\n"
            "Please tell me the amount of *greens* (kg), *browns* (kg), and *water* (L) you intend to put.\n\n"
            "Enter three numbers separated by semicolons:\n"
            "`greens;browns;water`\n\n"
            "_Example_: `1.5;0.8;0.4`",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return COMPOST_HELPER_INPUT
        
    if choice == "co2_tracker":
        # Load user data for CO2 calculator
        telegram_id = update.effective_user.id
        user_data = get_cached_user_data(telegram_id, context)
        tank_vol = user_data.get("tank_volume", 0) if user_data else 0
        soil_vol = user_data.get("soil_volume", 0) if user_data else 0
        
        # Check if user has set up volumes
        if tank_vol == 0 or soil_vol == 0:
            await q.edit_message_text(
                "⚠️ **Volume Setup Required**\n\n"
                "Please set up your tank and soil volumes in /profile first!",
                parse_mode="Markdown"
            )
            return MAIN_MENU
        
        # Get stored food waste total if available
        total_food_waste = user_data.get("total_food_waste_kg", 0) if user_data else 0
        if total_food_waste is None:
            total_food_waste = 0
        
        # Create keyboard options
        keyboard = [
            [InlineKeyboardButton("🧮 Calculate New Savings", callback_data="co2_calculate")],
            [InlineKeyboardButton("📊 View Total Impact", callback_data="co2_view_total")],
            [InlineKeyboardButton("🔄 Reset Counter", callback_data="co2_reset")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Calculate current savings
        if total_food_waste > 0:
            from services.emissions_calculator import EmissionsCalculator
            result = EmissionsCalculator.calculate_co2_saved_from_food_waste(
                total_food_waste, tank_vol, soil_vol
            )
            impact = EmissionsCalculator.get_environmental_impact_summary(
                result['total_co2_saved_kg']
            )
            
            message = (
                f"🌍 **CO₂ Savings Calculator**\n\n"
                f"📈 **Your Impact So Far:**\n"
                f"• Food waste composted: {total_food_waste:.1f} kg\n"
                f"• CO₂ saved: {result['total_co2_saved_kg']:.1f} kg\n"
                f"• Equivalent to planting {impact['trees_equivalent']} trees 🌳\n"
                f"• Or saving {impact['petrol_litres_equivalent']} litres of petrol ⛽\n\n"
                f"What would you like to do?"
            )
        else:
            message = (
                "🌍 **CO₂ Savings Calculator**\n\n"
                "Start tracking your environmental impact!\n"
                "Calculate how much CO₂ you save by composting food waste.\n\n"
                "What would you like to do?"
            )
        
        await q.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        return MAIN_MENU

    if choice == "image_scan":
        # Create inline keyboard for scan type selection
        keyboard = [
            [InlineKeyboardButton("🪣 Analyze Compost Tank", callback_data="scan_compost")],
            [InlineKeyboardButton("🌱 Analyze Plant", callback_data="scan_plant")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await q.edit_message_text(
            "📸 **Image Analysis**\n\n"
            "What would you like to analyze?\n\n"
            "🪣 **Compost Tank**: Analyze compost composition and quality\n"
            "🌱 **Plant**: Analyze plant health and identify issues\n\n"
            "Choose your analysis type:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        context.user_data["scan_mode"] = "menu"  # Flag to indicate menu scan vs direct scan
        return SCAN_TYPE_SELECTION

    # profile updates

    if choice == "change_volume":
        kb = [[InlineKeyboardButton("Back to Profile", callback_data="back_to_profile")]]
        await q.edit_message_text(
            "Send a message with your new tank volume (litres) followed by soil volume (litres).",
            reply_markup=InlineKeyboardMarkup(kb)
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
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]])
        )
        return MAIN_MENU

    if choice == "back_to_menu":
        return await show_main_menu(update, context, user)

    # fallback for unimplemented
    await q.edit_message_text(
        f"You selected {choice}. This feature is coming soon!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]])
    )
    return MAIN_MENU