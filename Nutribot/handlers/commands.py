import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
# from services.clarifai_segmentation import ClarifaiImageSegmentation  # Lazy loaded when needed
from services.emissions_calculator import EmissionsCalculator
from services.feeding_input import FeedCalculator
from services.ML_input import MLCompostRecommendation, get_available_crop_types
from services.extraction_timing import CompostProcessCalculator
from constants import GREENS_INPUT, MAIN_MENU, COMPOST_HELPER_INPUT, AMA, ML_CROP_SELECTION, ML_GREENS_INPUT, SCAN_TYPE_SELECTION
from services.database import db
from handlers.menu import show_main_menu
from utils.message_utils import get_cached_user_data

# Remove global clarifai instantiation - use lazy loading instead
logger = logging.getLogger(__name__)
feed_calculator = FeedCalculator()
ml_recommender = MLCompostRecommendation()


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return
        
    tank_vol = user_data.get("tank_volume", 0)
    soil_vol = user_data.get("soil_volume", 0)
    await update.message.reply_text(
        "🧪 **Compost Status Check**\n\n"
        "Based on your setup, your compost is approximately 65% ready.\n"
        "Estimated time to full maturity: 2-3 weeks.\n\n"
        "The moisture level appears normal and bacterial activity is good.",
        parse_mode="Markdown"
    )

async def input_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return
    
    # Create inline keyboard for calculator options
    keyboard = [
        [InlineKeyboardButton("🧠 ML Smart Recommendations", callback_data="use_ml_calculator")],
        [InlineKeyboardButton("🧮 Basic Calculator", callback_data="use_calculator")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🥕 **Food & Water Input Guide**\n\n"
        "Choose your recommendation method:\n\n"
        "🧠 **ML Smart**: Crop-specific recommendations based on historical data\n"
        "🧮 **Basic**: Simple ratio-based calculations\n\n"
        "Which would you prefer?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    # Return conversation state only if we're in a conversation context
    return MAIN_MENU

async def handle_calculator_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the calculator choice callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "use_ml_calculator":
        # Show crop selection for ML recommendations
        crops = get_available_crop_types()
        keyboard = []
        
        # Create buttons for each crop type (2 per row)
        for i in range(0, len(crops), 2):
            row = []
            row.append(InlineKeyboardButton(f"🌱 {crops[i]}", callback_data=f"crop_{crops[i].replace(' ', '_').lower()}"))
            if i + 1 < len(crops):
                row.append(InlineKeyboardButton(f"🌱 {crops[i+1]}", callback_data=f"crop_{crops[i+1].replace(' ', '_').lower()}"))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_input")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🧠 **ML Smart Recommendations**\n\n"
            "Select your target crop type for personalised recommendations:\n\n"
            "Each crop has different optimal C:N ratios and moisture requirements based on our sensor data analysis.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return ML_CROP_SELECTION
        
    elif query.data == "use_calculator":
        await query.edit_message_text(
            "🧮 **Basic Compost Calculator**\n\n"
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
    
    elif query.data == "back_to_input":
        # Return to input method selection
        return await input_command(update, context)

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

async def handle_ml_crop_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle crop selection for ML recommendations"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("crop_"):
        # Extract crop type from callback data
        crop_key = query.data.replace("crop_", "").replace("_", " ").title()
        
        # Convert back to proper crop names
        crop_mapping = {
            "Leafy Greens": "Leafy Greens",
            "Fruit Veggies": "Fruit Veggies", 
            "Root Vegetables": "Root Vegetables",
            "Herbs": "Herbs",
            "Flowering Plants": "Flowering Plants",
            "Woody Plants": "Woody Plants"
        }
        
        selected_crop = crop_mapping.get(crop_key)
        if not selected_crop:
            await query.edit_message_text("❌ Invalid crop selection. Please try again.")
            return ML_CROP_SELECTION
        
        # Store selected crop in context
        context.user_data["selected_crop"] = selected_crop
        
        await query.edit_message_text(
            f"🌱 **ML Recommendations for {selected_crop}**\n\n"
            f"Perfect choice! Now please enter the weight of your greens in kilograms.\n\n"
            f"This will provide recommendations specifically optimised for {selected_crop.lower()} "
            f"based on historical sensor data.\n\n"
            f"Examples:\n"
            f"• 0.03 (for 30g)\n"
            f"• 0.5 (for 500g)\n"
            f"• 1.2 (for 1.2kg)\n\n"
            f"💡 *Tip: Even small amounts work - the ML model will scale appropriately*",
            parse_mode="Markdown"
        )
        return ML_GREENS_INPUT
    
    elif query.data == "back_to_input":
        return await input_command(update, context)

async def handle_ml_greens_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle greens input for ML recommendations"""
    try:
        greens_weight_kg = float(update.message.text.strip())
        
        if greens_weight_kg <= 0:
            await update.message.reply_text(
                "❌ Please enter a positive number for the weight of greens.\n"
                "Try again with a number like 0.5 or 1.2"
            )
            return ML_GREENS_INPUT
            
        if greens_weight_kg > 50:  # Sanity check
            await update.message.reply_text(
                "❌ That seems like a very large amount! Please enter a reasonable weight (up to 50kg).\n"
                "Try again with a smaller number."
            )
            return ML_GREENS_INPUT
        
        # Get selected crop from context
        selected_crop = context.user_data.get("selected_crop")
        if not selected_crop:
            await update.message.reply_text("❌ Crop selection lost. Please start over.")
            return await input_command(update, context)
        
        # Convert kg to grams for ML model
        greens_weight_grams = greens_weight_kg * 1000
        
        # Get ML recommendation
        try:
            ml_recommendation = ml_recommender.get_formatted_recommendation(
                greens_weight_grams, selected_crop
            )
            
            # Create keyboard for actions
            keyboard = [
                [InlineKeyboardButton("🧠 Try Different Crop", callback_data="use_ml_calculator")],
                [InlineKeyboardButton("🧮 Try Basic Calculator", callback_data="use_calculator")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                ml_recommendation,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Clear the selected crop from context
            context.user_data.pop("selected_crop", None)
            
            # Stay in main menu conversation state
            return MAIN_MENU
            
        except Exception as ml_error:
            # Fallback to basic calculator if ML fails
            await update.message.reply_text(
                f"⚠️ ML recommendation temporarily unavailable. Using basic calculator instead.\n\n"
                f"Error: {str(ml_error)}"
            )
            
            basic_recommendation = feed_calculator.get_feeding_recommendations(greens_weight_kg)
            
            keyboard = [
                [InlineKeyboardButton("🔄 Try Again", callback_data="use_ml_calculator")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                basic_recommendation,
                parse_mode="Markdown", 
                reply_markup=reply_markup
            )
            
            return MAIN_MENU
        
    except ValueError:
        await update.message.reply_text(
            "❌ Please enter a valid number (e.g., 0.5, 1.2, 2.0).\n"
            f"How many kilograms of greens do you have for {context.user_data.get('selected_crop', 'your crop')}?"
        )
        return ML_GREENS_INPUT
    except Exception as e:
        await update.message.reply_text(
            "❌ Sorry, there was an error processing your input. Please try again."
        )
        return ML_GREENS_INPUT

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    
    # Create inline keyboard for scan type selection
    keyboard = [
        [InlineKeyboardButton("🪣 Analyze Compost Tank", callback_data="scan_compost")],
        [InlineKeyboardButton("🌱 Analyze Plant", callback_data="scan_plant")],
        [InlineKeyboardButton("🔙 Back", callback_data="scan_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📸 **Image Analysis**\n\n"
        "What would you like to analyze?\n\n"
        "🪣 **Compost Tank**: Analyze compost composition and quality\n"
        "🌱 **Plant**: Analyze plant health and identify issues\n\n"
        "Choose your analysis type:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    context.user_data["scan_mode"] = "direct"  # Flag to indicate direct scan vs menu scan
    return SCAN_TYPE_SELECTION

async def handle_scan_type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the scan type selection callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "scan_compost":
        # Set scan type to compost
        context.user_data["scan_type"] = "compost"
        await query.edit_message_text(
            "🪣 **Compost Tank Analysis**\n\n"
            "Send a photo of your compost tank!\n\n"
            "💡 **Tips for best results:**\n"
            "• Good lighting\n"
            "• Clear focus on compost contents\n"
            "• Avoid shadows\n\n"
            "📸 Ready to analyze your compost composition and quality.",
            parse_mode="Markdown"
        )
        context.user_data["expecting_image"] = True
        return MAIN_MENU
        
    elif query.data == "scan_plant":
        # Set scan type to plant
        context.user_data["scan_type"] = "plant"
        await query.edit_message_text(
            "🌱 **Plant Analysis**\n\n"
            "Send a photo of your plant!\n\n"
            "💡 **Tips for best results:**\n"
            "• Natural lighting preferred\n"
            "• Include leaves and stems\n"
            "• Close-up for detail\n\n"
            "📸 Ready to analyze plant health and identify issues.",
            parse_mode="Markdown"
        )
        context.user_data["expecting_image"] = True
        return MAIN_MENU
        
    elif query.data == "scan_back":
        # Return to previous state based on scan_mode
        if context.user_data.get("scan_mode") == "direct":
            # Clean up scan flags
            context.user_data.pop("scan_mode", None)
            context.user_data.pop("scan_type", None)
            # Return to main menu for direct scan
            username = context.user_data.get("username")
            return await show_main_menu(update, context, username)
        else:
            # Return to main menu
            username = context.user_data.get("username")
            return await show_main_menu(update, context, username)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = context.user_data.get("username")
    if not user:
        await update.message.reply_text("Please /start to login first.")
        return
    
    # Check if we're expecting an image
    if context.user_data.get("expecting_image"):
        # Handle both menu and direct scan modes with lazy loading
        context.user_data["expecting_image"] = False
        processing = await update.message.reply_text("🔄 Analysing your image...")
        
        # Get photo and download it
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        path = f"temp_{update.effective_user.id}.jpg"
        await file.download_to_drive(path)

        try:
            # Get scan type from context (default to compost for backward compatibility)
            scan_type = context.user_data.get("scan_type", "compost")
            
            # Use the new dual analysis system
            from handlers.image_handler import image_analyzer
            
            # Update processing message to indicate dual analysis
            await processing.edit_text("🔄 Performing technical analysis...")
            
            # Get dual analysis results
            analysis_result = await image_analyzer.analyze_image_with_ai_advice(path, scan_type)
            
            # Show Clarifai results first (if available)
            if analysis_result["clarifai_success"]:
                scan_emoji = "🪣" if scan_type == "compost" else "🌱"
                scan_name = "Compost Tank" if scan_type == "compost" else "Plant"
                
                clarifai_text = f"{scan_emoji} **{scan_name} Analysis Results**\n\n**Top elements detected:**\n"
                for i, c in enumerate(analysis_result["clarifai_results"], 1):
                    clarifai_text += f"{i}. {c['name'].title()}: {round(c['value']*100, 1)}%\n"
                clarifai_text += f"\n💡 Generating expert insights..."
                
                await processing.edit_text(clarifai_text, parse_mode="Markdown")
            else:
                # If Clarifai fails, update message
                await processing.edit_text("🔄 Analyzing image with AI vision...")
            
            # Send the comprehensive AI analysis as a new message
            if analysis_result["combined_message"]:
                await update.message.reply_text(
                    analysis_result["combined_message"], 
                    parse_mode="Markdown"
                )
            else:
                # Fallback message
                await update.message.reply_text(
                    "⚠️ Unable to analyze the image at this time. Please try again with a clearer photo."
                )
            
            # Add follow-up options after analysis
            scan_type = context.user_data.get("scan_type", "compost")
            scan_emoji = "🪣" if scan_type == "compost" else "🌱"
            scan_name = "Compost Tank" if scan_type == "compost" else "Plant"
            
            keyboard = [
                [InlineKeyboardButton(f"📸 Scan Another {scan_name}", callback_data=f"scan_{scan_type}")],
                [InlineKeyboardButton("📸 Switch Analysis Type", callback_data="image_scan")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"{scan_emoji} **Analysis Complete!**\n\n"
                "What would you like to do next?",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
                
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            await processing.edit_text(
                "⚠️ Could not analyse image. Try a clearer photo or check your connection.",
                parse_mode="Markdown"
            )
        
        try:
            import os
            os.remove(path)  # Clean up temp file
        except:
            pass
        
        # Clean up scan flags
        context.user_data.pop("scan_mode", None)
        context.user_data.pop("scan_type", None)
        
        # Return to main menu if this was from menu, otherwise stay in current state
        return MAIN_MENU
    
    # Otherwise, prompt user to use /scan first
    await update.message.reply_text("Use /scan first to analyze images.")
    return

async def care_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return

    tips = "🌡️ Keep soil moist and well-drained\n💧 Water regularly but avoid overwatering\n☀️ Provide adequate sunlight\n🌱 Monitor for pests and diseases"
    
    # Add inline button for Ask Anything (LLM)
    keyboard = [
        [InlineKeyboardButton("🪴 Ask Anything", callback_data="start_llama")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🪴 **{species.capitalize()} Care Guide**\n\n{tips}\n\n"
        "Remember to apply compost when nutrients deplete.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def co2_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return
        
    tank_vol = user_data.get("tank_volume", 0)
    soil_vol = user_data.get("soil_volume", 0)
    total_vol = tank_vol + soil_vol
    # using 0.5kg CO₂ saved per litre per year
    saved = round(total_vol * 0.5, 1)
    trees = round(saved / 25, 1)
    await update.message.reply_text(
        f"🌍 **CO₂ Savings Impact**\n\n"
        f"Your {total_vol}L setup saves ~{saved} kg CO₂/year\n"
        f"Equivalent to planting **{trees} trees**!",
        parse_mode="Markdown"
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return
        
    tank_vol = user_data.get("tank_volume", 0)
    soil_vol = user_data.get("soil_volume", 0)
    kb = [
        [InlineKeyboardButton("Change Volume", callback_data="change_volume")],
        [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
    ]
    await update.message.reply_text(
        f"👤 **Your Profile**\n\n"
        f"🪣 Tank Volume: {tank_vol} L\n"
        f"🌱 Soil Volume: {soil_vol} L\n\n"
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

async def compost_helper_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    prompt = (
        "🌱 *Compost Estimate Calculator*\n\n"
        "Please tell me the amount of *greens* (kg), *browns* (kg), and *water* (L) you intend to put.\n\n"
        "Enter three numbers separated by semicolons:\n"
        "`greens;browns;water`\n\n"
        "_Example_: `1.5;0.8;0.4`"
    )

    # 1) If this was triggered by an inline-button…
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text(
            prompt,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
            )
        )

    # 2) …or if it was triggered by a voice/text command
    else:
        await update.message.reply_text(
            prompt,
            parse_mode="Markdown"
        )

    return COMPOST_HELPER_INPUT

async def compost_helper_input(update, context):
    text = update.message.text.strip()
    try:
        greens_kg, browns_kg, water_kg = map(float, text.split(";"))
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid format. Send three numbers separated by semicolons, e.g.: `1.5;0.8;0.4`\n"
            "Please try again:"
        )
        return COMPOST_HELPER_INPUT

    results = CompostProcessCalculator.analyze_actual_mix(
        greens_kg, browns_kg, water_kg
    )

    await update.message.reply_text(
        "📊 *Compost Estimate Result*\n\n"
        f"• Start mass: **{results['total_start_mass_kg']} kg**\n"
        f"• Expected yield: **{results['expected_yield_kg']} kg of compost**\n"
        f"• Est. time to ready: **~{results['time_est_days']} days**\n"
        f"  _(range: {results['time_lower_days']}–{results['time_upper_days']} days)_",
        parse_mode="Markdown"
    )

    # return to main menu
    return await show_main_menu(update, context, context.user_data["username"])
