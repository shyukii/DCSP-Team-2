import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix encoding issues on Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Also set console encoding
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from config import Config
from set_bot_commands import COMMANDS
from constants import (
    AUTH_CHOICE,
    REGISTER_USERNAME,
    REGISTER_PASSWORD,
    LOGIN_USERNAME,
    LOGIN_PASSWORD,
    TANK_VOLUME,
    SOIL_VOLUME,
    MAIN_MENU,
    AMA,
    GREENS_INPUT,
    COMPOST_HELPER_INPUT,
    ML_CROP_SELECTION,
    ML_GREENS_INPUT,
    SCAN_TYPE_SELECTION,
    FEEDING_LOG_INPUT,
    PLANT_MOISTURE_INPUT,
    EC_FORECAST_SELECTION,
    EC_INPUT,
)
from handlers.auth import (
    start as start_conversation,
    direct_start_command,
    auth_choice,
    register_username,
    register_password,
    login_username,
    login_password,
    tank_volume,
    soil_volume,
    cancel,
    help_command,
)
from handlers.llama_handler import llama_response
from handlers.commands import (
    status_command,
    dashboards_command,
    input_command,
    scan_command,
    handle_photo,
    care_command,
    profile_command,
    handle_calculator_choice,
    handle_greens_input,
    handle_ml_crop_selection,
    handle_ml_greens_input,
    compost_helper_start,
    compost_helper_input,
    handle_scan_type_choice,
    handle_feeding_log_input,
    handle_plant_moisture_input,
    handle_ec_input,
    watering_command,
)
from services.emissions_calculator import co2_calculator_command
from handlers.menu import handle_main_menu, back_to_menu_command, back_to_menu_callback
from handlers.speech_handler import handle_voice
from handlers.ama_helpers import block_commands_during_ama


# Set command menu for Telegram
async def set_bot_commands(application):
    await application.bot.set_my_commands(COMMANDS)

async def setup_webhook(application):
    """Set up webhook for the bot"""
    await application.initialize()
    await application.start()
    
    # Set webhook URL
    webhook_url = f"{Config.WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    
    print(f"Webhook set to: {webhook_url}")
    print(f"Bot is ready to receive updates via webhook")

# Global application instance
application = None

def create_application():
    """Create and configure the application"""
    Config.validate_required_env_vars()
    return Application.builder().token(Config.TELEGRAM_TOKEN).post_init(set_bot_commands).build()

def setup_handlers():
    """Set up all conversation and command handlers"""
    global application
    if application is None:
        return
        
    # Conversation flow: auth → setup → main menu → AMA
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_conversation)],
        states={
            AUTH_CHOICE:       [CallbackQueryHandler(auth_choice)],
            REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_username)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
            LOGIN_USERNAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)],
            LOGIN_PASSWORD:    [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
            TANK_VOLUME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, tank_volume)],
            SOIL_VOLUME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, soil_volume)],
            MAIN_MENU:         [
                CallbackQueryHandler(handle_main_menu),
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"), 
                CallbackQueryHandler(handle_calculator_choice, pattern="^(use_ml_calculator|use_calculator)$"),
                CommandHandler("input", input_command),
                CommandHandler("status", status_command),
                CommandHandler("dashboards", dashboards_command),
                CommandHandler(["back", "menu"], back_to_menu_command),
                MessageHandler(filters.PHOTO, handle_photo)
            ],
            AMA:               [CommandHandler(["back","menu"], back_to_menu_command),
                                CallbackQueryHandler(handle_main_menu, pattern="^create_video$"),
                                MessageHandler(filters.TEXT & ~filters.COMMAND, llama_response),
                                MessageHandler(filters.VOICE, handle_voice),
                                MessageHandler(filters.COMMAND, block_commands_during_ama),],
            GREENS_INPUT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_greens_input)],
            ML_CROP_SELECTION: [CallbackQueryHandler(handle_ml_crop_selection)],
            ML_GREENS_INPUT:   [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ml_greens_input)],
            COMPOST_HELPER_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, compost_helper_input),
                CallbackQueryHandler(handle_main_menu, pattern="^back_to_menu$")
            ],
            SCAN_TYPE_SELECTION: [
                CallbackQueryHandler(handle_scan_type_choice),
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"),
                CommandHandler(["back", "menu"], back_to_menu_command)
            ],
            FEEDING_LOG_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feeding_log_input),
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$")
            ],
            PLANT_MOISTURE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plant_moisture_input),
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$")
            ],
            EC_FORECAST_SELECTION: [
                CallbackQueryHandler(handle_main_menu),
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"),
                CommandHandler("status", status_command)
            ],
            EC_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ec_input),
                CallbackQueryHandler(handle_main_menu, pattern="^ec_forecast$"),
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$")],
        name="nutribot_conversation",
    )
    # Add the conversation handler
    application.add_handler(conv_handler)

    # Non-conversation command handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("scan", scan_command))
    application.add_handler(CommandHandler("care", care_command))
    application.add_handler(CommandHandler("co2", co2_calculator_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("watering", watering_command))
    application.add_handler(CommandHandler("dashboards", dashboards_command))
    application.add_handler(CommandHandler(["back", "menu"], back_to_menu_command))
    
    # Note: CO2 callbacks (co2_personal, co2_global) are now handled by the main menu handler

    # Voice handler
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Fallback direct /start
    application.add_handler(CommandHandler("start", direct_start_command))

def main() -> None:
    # Configure logging
    logging.basicConfig(
        format=Config.LOGGING_FORMAT,
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    # Build the application
    global application
    application = create_application()
    
    # Set up all handlers
    setup_handlers()

    # Set up webhook if URL is provided
    if Config.WEBHOOK_URL:
        asyncio.run(setup_webhook(application))
    else:
        # Fallback to polling for local development
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
