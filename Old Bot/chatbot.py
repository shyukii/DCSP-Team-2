import logging
import json
import asyncio
import os
import subprocess
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram._message import Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from llama import LlamaInterface  
from emissions_calculator import EmissionsCalculator
from computer_vision import ClarifaiImageSegmentation

# Enable logging  
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
AMA, AUTH_CHOICE, REGISTER_USERNAME, REGISTER_PASSWORD, LOGIN_USERNAME, LOGIN_PASSWORD, PLANT_SPECIES, COMPOST_VOLUME, MAIN_MENU = range(9)

llama = LlamaInterface()

# async def start_llama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text("I'm Llama and I'm here to help you with caring your plants!")
#     return AMA

async def llama_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text
    if user_message.lower() in ['/menu', '/back', '/exit']:
        username = context.user_data.get("username")
        return await show_main_menu(update, context, username)
    
    try:
        # Send typing action to show bot is processing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = await llama.generate_response(user_message)
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error getting response from Llama: {e}")
        await update.message.reply_text(
            "Sorry, I'm having trouble processing your request. Please try again."
        )
    return AMA

############################################################################
# (/start)
############################################################################

# Direct bot response message (non-conversation)
async def direct_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command when outside of the conversation handler."""
    # This function will be called when /start is used but not matched by ConversationHandler
    await update.message.reply_text(
        "🚀 **NutriBot is now active!**\n\n"
        "I'm connecting to the system...\n"
        "Type /start again to begin the login process."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation with welcome message and login/register options."""
    logger.info(f"Start command received from user {update.effective_user.id}")
    
    # Display a quick loading message first
    loading_message = await update.message.reply_text("🔄 Loading NutriBot...")
    
    # Simulate a brief delay for effect (only 0.5 seconds to keep it responsive)
    await asyncio.sleep(0.5)
    
    # Delete the loading message
    await loading_message.delete()
    
    # Display welcome message
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")
    
    # Show login/register options
    keyboard = [
        [
            InlineKeyboardButton("Register", callback_data="register"),
            InlineKeyboardButton("Login", callback_data="login"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select an option to get started:",
        reply_markup=reply_markup
    )
    return AUTH_CHOICE

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(HELP_MESSAGE)


############################################################################
# Login Handler
############################################################################

# Path to JSON file for storing user credentials
LOGIN_FILE = "loginIDs.json"

# Ensure login file exists
def ensure_login_file_exists():
    if not os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, 'w') as f:
            json.dump({}, f)

# Load user credentials from JSON file
def load_user_credentials():
    ensure_login_file_exists()
    try:
        with open(LOGIN_FILE, 'r') as f:
            data = f.read().strip()
            if data:
                return json.loads(data)
            return {}
    except json.JSONDecodeError:
        return {}

# Save user credentials to JSON file
def save_user_credentials(credentials):
    with open(LOGIN_FILE, 'w') as f:
        json.dump(credentials, f, indent=4)

# Welcome message
WELCOME_MESSAGE = """👋 Hi there! I'm NutriBot, your friendly composting and plant care assistant 🌱♻️

You don't need to be a gardening expert — just ask me anything!"""

############################################################################
# Register Handler
############################################################################

async def register_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the username for registration and asks for password."""
    username = update.message.text
    context.user_data["username"] = username
    await update.message.reply_text("Now please create a password:")
    return REGISTER_PASSWORD

async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the password and completes registration."""
    password = update.message.text
    username = context.user_data.get("username", "")
    
    # Load existing credentials
    credentials = load_user_credentials()
    
    # Check if username already exists
    if username in credentials:
        await update.message.reply_text("Username already exists. Please try a different one.")
        return REGISTER_USERNAME
    
    # Add new user
    credentials[username] = {"password": password}
    save_user_credentials(credentials)
    
    # Move to plant species selection
    keyboard = [
        [
            InlineKeyboardButton("Lady's Finger", callback_data="ladysfinger"),
            InlineKeyboardButton("Spinach", callback_data="spinach"),
            InlineKeyboardButton("Long Bean", callback_data="longbean"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Registration successful, {username}! Now, please select your plant species:",
        reply_markup=reply_markup
    )
    return PLANT_SPECIES

async def login_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the username for login and asks for password."""
    username = update.message.text
    context.user_data["login_username"] = username
    await update.message.reply_text("Now please enter your password:")
    return LOGIN_PASSWORD

async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verifies login credentials."""
    password = update.message.text
    username = context.user_data.get("login_username", "")
    
    # Load credentials
    credentials = load_user_credentials()
    
    # Check credentials
    if username in credentials and credentials[username]["password"] == password:
        # Store username in context
        context.user_data["username"] = username
        
        # Check if user has plant species and compost volume
        user_data = credentials[username]
        
        if "plant_species" in user_data and "compost_volume" in user_data:
            # User already has plant and compost data, go to main menu
            return await show_main_menu(update, context, username)
        else:
            # User needs to complete setup with plant species
            keyboard = [
                [
                    InlineKeyboardButton("Lady's Finger", callback_data="ladysfinger"),
                    InlineKeyboardButton("Spinach", callback_data="spinach"),
                    InlineKeyboardButton("Long Bean", callback_data="longbean"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Welcome back, {username}! We need to complete your setup. Please select your plant species:",
                reply_markup=reply_markup
            )
            return PLANT_SPECIES
    else:
        await update.message.reply_text("Invalid username or password. Please try again.")
        return LOGIN_USERNAME

async def plant_species(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plant species selection."""
    query = update.callback_query
    await query.answer()
    
    species = query.data
    context.user_data["plant_species"] = species
    
    # Store the plant species in user data
    username = context.user_data.get("username") or context.user_data.get("login_username")
    credentials = load_user_credentials()
    if username in credentials:
        credentials[username]["plant_species"] = species
        save_user_credentials(credentials)
    
    await query.edit_message_text(f"You selected {species}. Now, please enter your compost volume (in litres):")
    return COMPOST_VOLUME

async def compost_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store compost volume and complete setup."""
    try:
        volume = float(update.message.text)
        if volume <= 0:
            await update.message.reply_text("Please enter a positive number for compost volume.")
            return COMPOST_VOLUME
    except ValueError:
        await update.message.reply_text("Please enter a valid number for compost volume.")
        return COMPOST_VOLUME
    
    # Store the compost volume in user data
    username = context.user_data.get("username") or context.user_data.get("login_username")
    credentials = load_user_credentials()
    if username in credentials:
        credentials[username]["compost_volume"] = volume
        save_user_credentials(credentials)
    
    # Show main menu
    return await show_main_menu(update, context, username)

############################################################################
# Checking compost readiness (/status)
############################################################################

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command to check compost readiness."""
    username = context.user_data.get("username")
    
    # If not logged in, prompt login
    if not username:
        await update.message.reply_text("Please use /start to login first.")
        return
    
    # Get user data
    credentials = load_user_credentials()
    if username in credentials:
        # Placeholder for actual compost status check
        await update.message.reply_text(
            "🧪 **Compost Status Check**\n\n"
            "Based on your setup, your compost is approximately 65% ready.\n"
            "Estimated time to full maturity: 2-3 weeks.\n\n"
            "The moisture level appears normal and bacterial activity is good.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Please use /start to login first.")

############################################################################
# Getting food/water input guidance (/input)
############################################################################

async def input_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /input command to get food/water input guide."""
    username = context.user_data.get("username")
    
    # If not logged in, prompt login
    if not username:
        await update.message.reply_text("Please use /start to login first.")
        return
    
    # Get user data
    credentials = load_user_credentials()
    if username in credentials:
        plant_species = credentials[username].get("plant_species", "plants")
        compost_volume = credentials[username].get("compost_volume", 0)
        
        # Calculate recommended inputs based on compost volume
        food_weekly = round(compost_volume * 0.2, 1)  # 20% of volume
        water_weekly = round(compost_volume * 0.1, 1)  # 10% of volume
        
        await update.message.reply_text(
            f"🥕 **Food & Water Input Guide**\n\n"
            f"For your {compost_volume} litre compost bin:\n\n"
            f"🍎 **Food Scraps**: Add {food_weekly} litres per week\n"
            f"💧 **Water**: Add {water_weekly} litres per week\n\n"
            f"*Tip for {plant_species}*: Ensure you add vegetable scraps rich in nitrogen for optimal growth.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Please use /start to login first.")

############################################################################
# Upload compost or plant image (/scan)
############################################################################

# Initialize Clarifai image segmentation
clarifai_segmenter = ClarifaiImageSegmentation(pat='88daa3cc427546dfaf4f37e1c1ddb3d3')

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /scan command to upload and analyze images."""
    await update.message.reply_text(
        "📸 **Image Analysis**\n\n"
        "Please send me a photo of your compost or plants, and I'll analyze it for you!\n\n"
        "For best results, ensure good lighting and focus on the area of concern.",
        parse_mode="Markdown"
    )
    # Set a flag to indicate we're expecting an image
    context.user_data["expecting_image"] = True

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages for image analysis."""
    # Check if user is logged in
    username = context.user_data.get("username")
    if not username:
        await update.message.reply_text("Please use /start to login first before uploading images.")
        return
    
    # Check if we're expecting an image (user used /scan command)
    if not context.user_data.get("expecting_image", False):
        await update.message.reply_text(
            "I received your image! Use /scan command first if you want me to analyse it."
        )
        return
    
    # Reset the flag
    context.user_data["expecting_image"] = False
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("🔄 Analysing your image, please wait...")
        
        # Get the largest photo size
        photo = update.message.photo[-1]
        
        # Download the photo
        photo_file = await context.bot.get_file(photo.file_id)
        photo_path = f"temp_image_{update.effective_user.id}.jpg"
        await photo_file.download_to_drive(photo_path)
        
        # Analyse the image using Clarifai
        try:
            results = clarifai_segmenter.analyse_image(photo_path)
            top_concepts = clarifai_segmenter.get_top_concepts(photo_path, top_n=5)
            
            # Format the results
            if top_concepts:
                analysis_text = "🔍 **Image Analysis Results**\n\n"
                analysis_text += "**Top detected elements:**\n"
                
                for i, concept in enumerate(top_concepts, 1):
                    confidence_percent = round(concept['value'] * 100, 1)
                    analysis_text += f"{i}. {concept['name'].title()}: {confidence_percent}%\n"
                
                # Add plant-specific advice based on detected elements
                plant_keywords = ['plant', 'leaf', 'flower', 'stem', 'garden', 'vegetation']
                compost_keywords = ['soil', 'dirt', 'compost', 'organic', 'waste']
                
                detected_elements = [concept['name'].lower() for concept in top_concepts]
                
                if any(keyword in ' '.join(detected_elements) for keyword in plant_keywords):
                    analysis_text += "\n🌱 **Plant Care Advice:**\n"
                    # Get user's plant type for specific advice
                    credentials = load_user_credentials()
                    if username in credentials:
                        plant_species = credentials[username].get("plant_species", "plants")
                        if plant_species == "spinach":
                            analysis_text += "• Monitor for leaf discoloration or pest damage\n"
                            analysis_text += "• Ensure consistent moisture levels\n"
                        elif plant_species == "ladysfinger":
                            analysis_text += "• Check for proper flowering and pod development\n"
                            analysis_text += "• Ensure adequate support for growing stems\n"
                        elif plant_species == "longbean":
                            analysis_text += "• Provide climbing support if needed\n"
                            analysis_text += "• Monitor bean pod development\n"
                        else:
                            analysis_text += "• Monitor plant health and growth patterns\n"
                            analysis_text += "• Check for signs of nutrient deficiency\n"
                
                elif any(keyword in ' '.join(detected_elements) for keyword in compost_keywords):
                    analysis_text += "\n♻️ **Compost Analysis:**\n"
                    analysis_text += "• Compost appears to be developing well\n"
                    analysis_text += "• Ensure proper moisture and aeration\n"
                    analysis_text += "• Consider adding more organic matter if needed\n"
                
                analysis_text += f"\n💡 **Tip:** For more specific advice, you can ask me questions about what you see!"
                
            else:
                analysis_text = "❌ I couldn't detect specific elements in your image. Please try uploading a clearer photo with better lighting."
            
        except Exception as cv_error:
            logger.error(f"Computer vision error: {cv_error}")
            analysis_text = (
                "⚠️ I encountered an issue analysing your image. This could be due to:\n\n"
                "• Image quality or lighting\n"
                "• Network connectivity\n"
                "• Service availability\n\n"
                "Please try again with a clearer photo."
            )
        
        # Clean up the temporary file
        try:
            os.remove(photo_path)
        except:
            pass  # Ignore cleanup errors
        
        # Delete processing message and send results
        await processing_msg.delete()
        await update.message.reply_text(analysis_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't process your image. Please try again."
        )
        # Clean up the temporary file in case of error
        try:
            os.remove(photo_path)
        except:
            pass

############################################################################
# Learn more about composting or get plant care suggestions (/care)
############################################################################

async def care_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /care command to get plant care suggestions."""
    username = context.user_data.get("username")
    
    # If not logged in, prompt login
    if not username:
        await update.message.reply_text("Please use /start to login first.")
        return
    
    # Get user data
    credentials = load_user_credentials()
    if username in credentials:
        plant_species = credentials[username].get("plant_species", "plants")
        
        # Plant-specific care tips
        care_tips = {
            "ladysfinger": "🌡️ Keep soil temperature between 22-35C\n💧 Water regularly, keeping soil moist\n☀️ Requires 6+ hours of direct sunlight",
            "spinach": "🌡️ Prefers cooler temperatures (15-20C)\n💧 Keep soil consistently moist\n🌱 Harvest outer leaves first for continuous growth",
            "longbean": "🌿 Provide support for climbing\n💧 Water deeply once a week\n☀️ Plant in full sun exposure"
        }
        
        tips = care_tips.get(plant_species, "Keep soil moist and provide adequate sunlight.")
        
        await update.message.reply_text(
            f"🪴 **{plant_species.capitalize()} Care Guide**\n\n"
            f"{tips}\n\n"
            f"Remember to apply compost when soil appears depleted of nutrients.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Please use /start to login first.")

############################################################################
# View c02 emissions saved (/c02)
############################################################################

from emissions_calculator import EmissionsCalculator

async def co2_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /co2 command to view CO₂ savings."""
    username = context.user_data.get("username")
    
    # If not logged in, prompt login
    if not username:
        await update.message.reply_text("Please use /start to login first.")
        return
    
    # Get user data
    credentials = load_user_credentials()
    if username in credentials:
        compost_volume = credentials[username].get("compost_volume", 0)
        
        # Calculate CO2 savings (simplified estimation)
        # Assume 1L of compost saves about 0.5kg of CO2 over 3 months
        co2_saved = round(compost_volume * 0.5, 1)
        trees_equivalent = round(co2_saved / 25, 1)  # 25kg CO2 per tree per year (simplified)
        
        await update.message.reply_text(
            f"🌍 **CO₂ Savings Impact**\n\n"
            f"Your {compost_volume}L compost system helps avoid approximately:\n\n"
            f"🌱 **{co2_saved} kg** of CO2 emissions per year\n"
            f"🌳 Equivalent to planting **{trees_equivalent} trees**!\n\n"
            f"By composting, you're reducing methane emissions from landfills and helping fight climate change.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Please use /start to login first.")

############################################################################
# Updating users composting set up (/profile)
############################################################################

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profile command to update compost setup."""
    username = context.user_data.get("username")
    
    # If not logged in, prompt login
    if not username:
        await update.message.reply_text("Please use /start to login first.")
        return
    
    # Get user data
    credentials = load_user_credentials()
    if username in credentials:
        plant_species = credentials[username].get("plant_species", "unknown")
        compost_volume = credentials[username].get("compost_volume", 0)
        
        # Create keyboard for updating profile
        keyboard = [
            [InlineKeyboardButton("Change Plant Type", callback_data="change_plant")],
            [InlineKeyboardButton("Change Compost Volume", callback_data="change_volume")],
            [InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👤 **Your Profile**\n\n"
            f"🪴 Plant type: {plant_species}\n"
            f"📦 Compost volume: {compost_volume} litres\n\n"
            f"What would you like to update?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("Please use /start to login first.")

async def auth_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the auth choice callback."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    if choice == "register":
        await query.edit_message_text("You selected registration. Please enter a username:")
        return REGISTER_USERNAME
    else:
        await query.edit_message_text("You selected login. Please enter your username:")
        return LOGIN_USERNAME

############################################################################
# Main Menu
############################################################################

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, username) -> int:
    """Show the main menu with options."""
    # Get user data for personalized greeting
    credentials = load_user_credentials()
    plant_species = credentials[username].get("plant_species", "plants")
    
    # Create main menu keyboard
    keyboard = [
        [
            InlineKeyboardButton("📦 Compost Help", callback_data="compost_help"),
            InlineKeyboardButton("🪴 Plant Care", callback_data="start_llama")
        ],
        [
            InlineKeyboardButton("📈 CO2 Tracker", callback_data="co2_tracker"),
            InlineKeyboardButton("📸 Image Scan", callback_data="image_scan")
        ],
        [
            InlineKeyboardButton("❓ Help & Commands", callback_data="help_commands")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send personalized greeting with the main menu
    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"Setup complete, {username}! Your {plant_species} and compost information is saved.\n\n"
            f"What would you like to do today?",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"Welcome, {username}! I'm here to help with your {plant_species}.\n\n"
            f"What would you like to do today?",
            reply_markup=reply_markup
        )
    
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu selection."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    username = context.user_data.get("username") or context.user_data.get("login_username")
    if choice =="start_llama":
        await query.edit_message_text("I'm Llama and I'm here to help you with your plants!!")
        return AMA
    if choice == "help_commands":
        # Show help and commands menu
        await query.edit_message_text(
            HELP_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
            ])
        )
    elif choice == "back_to_menu":
        # Return to main menu
        return await show_main_menu(update, context, username)
    elif choice == "compost_help":
        await query.edit_message_text(
            "🧑‍🌾 **Compost Help**\n\n"
            "I can help you manage your compost. What would you like to know?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("What to Add", callback_data="compost_add"),
                 InlineKeyboardButton("When Ready", callback_data="compost_ready")],
                [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
            ])
        )
    elif choice == "co2_tracker":
        await query.edit_message_text(
            "🌍 **CO₂ Tracker**\n\n"
            "By composting, you're helping the environment! I'll help you track your impact.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View Impact", callback_data="co2_impact"),
                 InlineKeyboardButton("Add Compost", callback_data="co2_add")],
                [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
            ])
        )
    elif choice == "image_scan":
        await query.edit_message_text(
            "📸 **Image Scan**\n\n"
            "Send me a photo of your plants or compost, and I'll analyze it for you!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
            ])
        )
    elif choice == "change_plant":
        # Handle plant change request
        keyboard = [
            [
                InlineKeyboardButton("Lady's Finger", callback_data="update_plant_ladysfinger"),
                InlineKeyboardButton("Spinach", callback_data="update_plant_spinach"),
                InlineKeyboardButton("Long Bean", callback_data="update_plant_longbean"),
            ],
            [
                InlineKeyboardButton("Back to Profile", callback_data="back_to_profile")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Please select your new plant type:",
            reply_markup=reply_markup
        )
    elif choice == "change_volume":
        await query.edit_message_text(
            "Please send a message with your new compost volume in litres.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back to Profile", callback_data="back_to_profile")]
            ])
        )
    elif choice == "back_to_profile":
        await profile_command(update, context)
    elif choice.startswith("update_plant_"):
        new_plant = choice.replace("update_plant_", "")
        credentials = load_user_credentials()
        if username in credentials:
            credentials[username]["plant_species"] = new_plant
            save_user_credentials(credentials)
            
            await query.edit_message_text(
                f"Your plant type has been updated to {new_plant}!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Back to Profile", callback_data="back_to_profile")]
                ])
            )
    else:
        # Placeholder for other menu options
        await query.edit_message_text(
            f"You selected {choice}. This feature is coming soon!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
            ])
        )
    
    return MAIN_MENU

############################################################################
# Help message and commands (/help)
############################################################################

# Help message
HELP_MESSAGE = """Here's what I can do for you:

/status — Check compost readiness
/input — Get food and water input guidance
/scan — Upload compost or plant image for analysis
/care — Get compost or plant care advice
/co2 — View your CO2 emissions impact
/profile — Update your compost setup
/help — Show this commands list

Type any of these commands or use the menu buttons to get started!"""

############################################################################
# Stop conversation (/cancel)
############################################################################

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Operation cancelled. Type /start to begin again.")
    context.user_data.clear()
    return ConversationHandler.END


############################################################################
# Main 
############################################################################

def main() -> None:
    """Run the bot."""
    try:
        # Telegram token
        token = "7787023282:AAFGs3KVK9iIQEoeSfjj3XpZ2R1MgOhZWP8"
        
        # Create the Application
        application = Application.builder().token(token).build()

        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                AUTH_CHOICE: [CallbackQueryHandler(auth_choice)],
                REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_username)],
                REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
                LOGIN_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)],
                LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
                PLANT_SPECIES: [CallbackQueryHandler(plant_species)],
                COMPOST_VOLUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, compost_volume)],
                MAIN_MENU: [CallbackQueryHandler(handle_main_menu)],
                AMA:[MessageHandler(filters.TEXT & ~filters.COMMAND, llama_response)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            name="auth_conversation"
        )

        # Add separate command handlers BEFORE the conversation handler
        # This ensures they're checked first
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("input", input_command))
        application.add_handler(CommandHandler("scan", scan_command))
        application.add_handler(CommandHandler("care", care_command))
        application.add_handler(CommandHandler("co2", co2_command))
        application.add_handler(CommandHandler("profile", profile_command))
        
        # Add photo handler for image analysis
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # Add photo handler for image analysis
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # Add the conversation handler
        application.add_handler(conv_handler)
        
        # Add a direct /start command handler AFTER the conversation handler
        # This will only be triggered if the conversation handler doesn't match
        application.add_handler(CommandHandler("start", direct_start_command))

        # Start the Bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()