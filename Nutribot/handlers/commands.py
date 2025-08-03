import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
# from services.clarifai_segmentation import ClarifaiImageSegmentation  # Lazy loaded when needed
# Removed unused imports: EmissionsCalculator, FeedCalculator
from services.ML_input import MLCompostRecommendation
from services.extraction_timing import CompostProcessCalculator
from constants import GREENS_INPUT, MAIN_MENU, COMPOST_HELPER_INPUT, AMA, ML_CROP_SELECTION, ML_GREENS_INPUT, SCAN_TYPE_SELECTION, FEEDING_LOG_INPUT, PLANT_MOISTURE_INPUT, EC_INPUT
from services.database import db
from handlers.menu import show_main_menu
from utils.message_utils import get_cached_user_data

# Remove global clarifai instantiation - use lazy loading instead
logger = logging.getLogger(__name__)
# Removed unused feed_calculator instance
ml_recommender = MLCompostRecommendation()


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from handlers.menu import handle_main_menu
    
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return
    
    # Create a fake callback query to trigger the ec_forecast menu
    class FakeCallbackQuery:
        def __init__(self):
            self.data = "ec_forecast"
            
        async def answer(self):
            pass
            
        async def edit_message_text(self, text, parse_mode=None, reply_markup=None):
            await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    
    # Create fake update to trigger ec_forecast handler
    fake_update = type('obj', (object,), {
        'callback_query': FakeCallbackQuery(),
        'effective_user': update.effective_user
    })()
    
    # Call the existing menu handler with ec_forecast and return the state
    return await handle_main_menu(fake_update, context)

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
        "🧠 **ML Smart**: Crop-specific recommendations with soil volume-based water calculations\n"
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
        crops = ml_recommender.get_available_crop_types()
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
            "Each crop has different optimal C:N ratios based on ML analysis.",
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
        
        # Calculate basic ratios (simple 3:1 brown:green ratio)
        greens_grams = greens_weight * 1000
        browns_grams = greens_grams * 3  # Basic 3:1 ratio
        water_ml = (greens_grams + browns_grams) * 0.6  # 60% moisture
        
        recommendations = f"""🧮 **Basic Calculator Results**

🔢 **For {greens_weight}kg of greens:**

🌿 **Greens:** {greens_weight}kg (your input)
🍂 **Browns:** {browns_grams/1000:.1f}kg
💧 **Water:** {water_ml/1000:.1f}L

📊 **Basic Guidelines:**
• 3:1 brown to green ratio
• ~60% moisture content
• Turn weekly for best results

💡 *For crop-specific recommendations, try ML Smart mode!*"""
        
        # Create keyboard for actions
        keyboard = [
            [InlineKeyboardButton("📝 Log Actual Feeding", callback_data="log_feeding")],
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
        
        # Validate crop using ML model
        available_crops = ml_recommender.get_available_crop_types()
        if crop_key not in available_crops:
            await query.edit_message_text("❌ Invalid crop selection. Please try again.")
            return ML_CROP_SELECTION
        
        selected_crop = crop_key
        
        # Store selected crop in context
        context.user_data["selected_crop"] = selected_crop
        
        await query.edit_message_text(
            f"🧠 **ML Recommendations for {selected_crop}**\n\n"
            f"Perfect choice! Now please enter the weight of your greens in kilograms.\n\n"
            f"This will provide recommendations specifically optimised for {selected_crop.lower()} "
            f"using your registered soil volume for water calculations.\n\n"
            f"Examples:\n"
            f"• 0.03 (for 30g)\n"
            f"• 0.5 (for 500g)\n"
            f"• 1.2 (for 1.2kg)\n\n"
            f"💡 *Tip: Water amount will be calculated as 50% of your soil volume*",
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
        
        # Get user soil volume for water calculation
        telegram_id = update.effective_user.id
        user_data = get_cached_user_data(telegram_id, context)
        soil_volume = user_data.get("soil_volume", 0) if user_data else 0
        
        # Get ML recommendation
        try:
            ml_recommendation = ml_recommender.get_formatted_recommendation(
                greens_weight_grams, selected_crop, soil_volume
            )
            
            # Create keyboard for actions
            keyboard = [
                [InlineKeyboardButton("📝 Log Actual Feeding", callback_data="log_feeding")],
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
            
            # Basic calculator fallback
            greens_grams = greens_weight_kg * 1000
            browns_grams = greens_grams * 3  # Basic 3:1 ratio
            water_ml = (greens_grams + browns_grams) * 0.6  # 60% moisture
            
            basic_recommendation = f"""🧮 **Basic Calculator (Fallback)**

🔢 **For {greens_weight_kg}kg of greens:**

🌿 **Greens:** {greens_weight_kg}kg
🍂 **Browns:** {browns_grams/1000:.1f}kg
💧 **Water:** {water_ml/1000:.1f}L

📊 **Basic Guidelines:**
• 3:1 brown to green ratio
• ~60% moisture content

💡 *Try again later for ML recommendations!*"""
            
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
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
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
    
    # Handle back_to_menu first
    if query.data == "back_to_menu":
        from handlers.menu import show_main_menu
        username = context.user_data.get("username") or context.user_data.get("login_username")
        # Clear scan states
        context.user_data.pop("scan_mode", None)
        context.user_data.pop("scan_type", None)
        context.user_data.pop("expecting_image", None)
        return await show_main_menu(update, context, username)
    
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
        f"🪴 **Plant Care Guide**\n\n{tips}\n\n"
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
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    await update.message.reply_text(
        f"👤 **Your Profile**\n\n"
        f"🪣 Tank Volume: {tank_vol} L\n"
        f"🌱 Soil Volume: {soil_vol} L\n\n"
        "What to update?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def handle_log_feeding_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the 'Log Actual Feeding' button click"""
    query = update.callback_query
    await query.answer()
    
    # Send a new message instead of editing the recommendation
    await update.effective_message.reply_text(
        "📝 **Log Your Actual Feeding**\n\n"
        "Please enter the actual amounts you added to your compost in this format:\n"
        "`greens;browns;moisture_percentage`\n\n"
        "**Example:** `30;54;45`\n"
        "• Greens: 30g\n"
        "• Browns: 54g  \n"
        "• Moisture achieved: 45%\n\n"
        "💡 *Use your moisture meter to measure the final moisture percentage after adding water*",
        parse_mode="Markdown"
    )
    
    return FEEDING_LOG_INPUT

async def handle_feeding_log_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the actual feeding amounts input"""
    try:
        # Parse the input
        input_text = update.message.text.strip()
        parts = input_text.split(';')
        
        if len(parts) != 3:
            await update.message.reply_text(
                "❌ Please enter three values separated by semicolons.\n"
                "Format: `greens;browns;moisture_percentage`\n"
                "Example: `30;54;45`"
            )
            return FEEDING_LOG_INPUT
        
        try:
            greens = float(parts[0])
            browns = float(parts[1])
            moisture_percentage = float(parts[2])
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter valid numbers.\n"
                "Format: `greens;browns;moisture_percentage`\n" 
                "Example: `30;54;45`"
            )
            return FEEDING_LOG_INPUT
        
        # Validate values are positive and moisture is within range
        if greens < 0 or browns < 0 or moisture_percentage < 0:
            await update.message.reply_text(
                "❌ Please enter positive values only.\n"
                "All amounts should be greater than or equal to 0."
            )
            return FEEDING_LOG_INPUT
        
        if moisture_percentage > 100:
            await update.message.reply_text(
                "❌ Moisture percentage cannot exceed 100%.\n"
                "Please enter a value between 0 and 100."
            )
            return FEEDING_LOG_INPUT
        
        # Save to database
        telegram_id = update.effective_user.id
        feeding_log = db.create_feeding_log(telegram_id, greens, browns, moisture_percentage)
        
        if feeding_log:
            # Check if moisture is close to target
            moisture_feedback = ""
            if moisture_percentage < 40:
                moisture_feedback = "\n⚠️ Moisture is quite low - consider adding more water next time."
            elif moisture_percentage > 60:
                moisture_feedback = "\n⚠️ Moisture is quite high - reduce water next time for better aeration."
            elif 45 <= moisture_percentage <= 55:
                moisture_feedback = "\n🎯 Perfect! You hit the ideal moisture range!"
            
            await update.message.reply_text(
                f"✅ **Feeding Logged Successfully!**\n\n"
                f"📊 **Your Entry:**\n"
                f"🌿 Greens: {greens}g\n"  
                f"🍂 Browns: {browns}g\n"
                f"💧 Moisture achieved: {moisture_percentage}%{moisture_feedback}\n\n"
                f"📅 Logged at: {feeding_log.get('created_at', 'just now')}\n\n"
                f"Great job tracking your composting! 🌱",
                parse_mode="Markdown"
            )
            
            # Return to main menu
            username = context.user_data.get("username") or context.user_data.get("login_username")
            return await show_main_menu(update, context, username)
        else:
            await update.message.reply_text(
                "❌ Failed to save feeding log. Please try again later."
            )
            # Return to main menu even on failure
            username = context.user_data.get("username") or context.user_data.get("login_username")
            return await show_main_menu(update, context, username)
        
    except Exception as e:
        logger.error(f"Error processing feeding log input: {e}")
        await update.message.reply_text(
            "❌ An error occurred while saving your feeding log. Please try again."
        )
        # Return to main menu on error
        username = context.user_data.get("username") or context.user_data.get("login_username")
        return await show_main_menu(update, context, username)

async def handle_view_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle viewing recent feeding logs"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    logs = db.get_user_feeding_logs(telegram_id, limit=5)
    
    if not logs:
        # Send new message instead of editing the recommendation
        await update.effective_message.reply_text(
            "📋 **No Feeding Logs Found**\n\n"
            "You haven't logged any feedings yet.\n"
            "Start tracking your compost inputs using the 📝 Log Feeding feature!",
            parse_mode="Markdown"
        )
        # Return to main menu
        username = context.user_data.get("username") or context.user_data.get("login_username")
        return await show_main_menu(query, context, username)
    
    # Format the logs
    log_text = "📋 **Your Recent Feeding Logs**\n\n"
    for i, log in enumerate(logs, 1):
        created_date = log.get('created_at', '')[:10] if log.get('created_at') else 'Unknown'
        log_text += f"**{i}. {created_date}**\n"
        log_text += f"🌿 Greens: {log.get('greens', 0)}g\n"
        log_text += f"🍂 Browns: {log.get('browns', 0)}g\n" 
        moisture = log.get('moisture_percentage', log.get('water', 0))  # Fallback for old logs
        if log.get('moisture_percentage') is not None:
            log_text += f"💧 Moisture: {moisture}%\n\n"
        else:
            log_text += f"💧 Water: {moisture}ml (old format)\n\n"
    
    # Send new message instead of editing the recommendation
    await update.effective_message.reply_text(
        log_text,
        parse_mode="Markdown"
    )
    
    # Return to main menu
    username = context.user_data.get("username") or context.user_data.get("login_username")
    return await show_main_menu(query, context, username)

async def watering_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /watering command - direct access to plant moisture projection"""
    telegram_id = update.effective_user.id
    user_data = get_cached_user_data(telegram_id, context)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return
    
    # Create keyboard with dashboard option
    keyboard = [
        [InlineKeyboardButton("📊 View Plant Dashboard", callback_data="view_plant_dashboard")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💧 **Plant Moisture Projection**\n\n"
        "📏 Using your soil moisture meter, please measure your plant's current moisture percentage.\n\n"
        "Enter the moisture percentage (0-100):\n"
        "_Example_: `45` for 45% moisture\n\n"
        "📊 Or view your visual dashboard below:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    return PLANT_MOISTURE_INPUT

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

async def handle_plant_moisture_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plant moisture percentage input and generate projections"""
    try:
        moisture_input = update.message.text.strip()
        
        # Import the plant moisture service
        from services.plant_moisture import PlantMoistureProjection
        moisture_service = PlantMoistureProjection()
        
        # Validate input
        is_valid, moisture_value = moisture_service.validate_moisture_percentage(moisture_input)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Please enter a valid moisture percentage between 0 and 100.\n"
                "Examples: `45`, `67%`, `32.5`\n\n"
                "Please try again:"
            )
            return PLANT_MOISTURE_INPUT
        
        # Generate moisture projection with telegram_id for logging
        telegram_id = update.effective_user.id
        projection_data = moisture_service.generate_moisture_projection(moisture_value, telegram_id)
        
        # Create comprehensive dashboard message
        dashboard_text = f"💧 **Plant Moisture Dashboard**\n\n"
        dashboard_text += f"📊 **Current Status:**\n"
        dashboard_text += f"• Current moisture: {moisture_value}%\n"
        dashboard_text += f"• {projection_data['next_watering_day']}\n\n"
        
        # Show watering alerts if any
        if projection_data['watering_alerts']:
            dashboard_text += f"🚨 **Watering Alerts (Next 30 Days):**\n"
            for alert in projection_data['watering_alerts'][:3]:  # Show first 3 alerts
                dashboard_text += f"• {alert['message']}\n"
            dashboard_text += "\n"
        
        dashboard_text += f"📅 **Next 7 Days Projection:**\n"
        for proj in projection_data['projections'][:7]:  # Show first 7 days
            status_emoji = {"critical": "🚨", "low": "⚠️", "moderate": "📊", "good": "✅"}
            emoji = status_emoji.get(proj['status'], "📊")
            dashboard_text += f"{emoji} {proj['day_name']}: {proj['moisture_percentage']}%\n"
        
        dashboard_text += f"\n🎯 **30-Day Recommendation:**\n"
        dashboard_text += f"{projection_data['overall_recommendation']}\n\n"
        
        # Add care tips
        tips = moisture_service.get_moisture_tips(moisture_value)
        dashboard_text += f"💡 **Care Tips:**\n{tips}"
        
        # Create back to menu button
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            dashboard_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Return to main menu state
        return MAIN_MENU
        
    except Exception as e:
        logger.error(f"Error processing plant moisture input: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your moisture data. Please try again."
        )
        # Return to main menu on error
        username = context.user_data.get("username") or context.user_data.get("login_username")
        return await show_main_menu(update, context, username)

async def handle_ec_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle EC and moisture input for ML prediction"""
    try:
        # Parse the input
        input_text = update.message.text.strip()
        parts = input_text.split(';')
        
        if len(parts) != 2:
            await update.message.reply_text(
                "❌ Please enter two values separated by semicolon.\n"
                "Format: `ec_value;moisture_percentage`\n"
                "Example: `2.5;65`"
            )
            return EC_INPUT
        
        try:
            ec_value = float(parts[0])
            moisture_percentage = float(parts[1])
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter valid numbers.\n"
                "Format: `ec_value;moisture_percentage`\n" 
                "Example: `2.5;65`"
            )
            return EC_INPUT
        
        # Validate values
        if ec_value < 0 or moisture_percentage < 0:
            await update.message.reply_text(
                "❌ Please enter positive values only.\n"
                "EC and moisture should be greater than 0."
            )
            return EC_INPUT
        
        if moisture_percentage > 100:
            await update.message.reply_text(
                "❌ Moisture percentage cannot exceed 100%.\n"
                "Please enter a value between 0 and 100."
            )
            return EC_INPUT
        
        if ec_value > 10:  # Reasonable upper limit for EC
            await update.message.reply_text(
                "❌ EC value seems too high (>10 mS/cm).\n"
                "Please check your reading and try again."
            )
            return EC_INPUT
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🔄 **Processing your data...**\n\n"
            f"📊 EC: {ec_value} mS/cm\n"
            f"💧 Moisture: {moisture_percentage}%\n\n"
            "🧠 Running ML prediction..."
        )
        
        # Generate ML prediction first
        try:
            from services.ec_forecast_service import ECForecastService
            ec_service = ECForecastService()
            
            # Update processing message
            await processing_msg.edit_text(
                "🔄 **Generating 90-day forecast...**\n\n"
                f"📊 EC: {ec_value} mS/cm\n"
                f"💧 Moisture: {moisture_percentage}%\n\n"
                "🧠 ML model working..."
            )
            
            # Get prediction
            prediction_result = ec_service.predict_90_day_forecast(ec_value, moisture_percentage)
            
        except Exception as ml_error:
            logger.error(f"ML prediction error: {ml_error}")
            prediction_result = {'success': False, 'error': str(ml_error)}
        
        # Save to database with predictions
        telegram_id = update.effective_user.id
        compost_status = db.create_compost_status_with_predictions(telegram_id, ec_value, moisture_percentage, prediction_result)
        
        if not compost_status:
            await processing_msg.edit_text(
                "❌ Failed to save your data. Please try again."
            )
            return EC_INPUT
        
        # Handle the prediction results
        if prediction_result.get('success', False):
            # Format and send the prediction message
            prediction_message = ec_service.format_prediction_message(prediction_result)
            
            # Create action buttons
            keyboard = [
                [InlineKeyboardButton("📊 Enter New Reading", callback_data="ml_ec_prediction")],
                [InlineKeyboardButton(" Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update processing message with results
            await processing_msg.edit_text(
                "✅ **Data Saved Successfully!**\n\n"
                f"📊 Your reading and predictions have been saved to the database."
            )
            
            # Send prediction results as new message
            await update.message.reply_text(
                prediction_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        else:
            # ML prediction failed, but data was saved
            error_msg = prediction_result.get('error', 'Unknown error')
            await processing_msg.edit_text(
                f"✅ **Data Saved Successfully!**\n\n"
                f"📊 EC: {ec_value} mS/cm\n"
                f"💧 Moisture: {moisture_percentage}%\n\n"
                f"⚠️ **ML Prediction Failed**: {error_msg}\n\n"
                "Your data has been saved for future analysis."
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 Try Again", callback_data="ml_ec_prediction")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "What would you like to do next?",
                reply_markup=reply_markup
            )
        
        # Return to main menu state
        return MAIN_MENU
        
    except Exception as e:
        logger.error(f"Error processing EC input: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your input. Please try again."
        )
        return EC_INPUT
