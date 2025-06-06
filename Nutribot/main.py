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
from constants import (
    AUTH_CHOICE,
    REGISTER_USERNAME,
    REGISTER_PASSWORD,
    LOGIN_USERNAME,
    LOGIN_PASSWORD,
    PLANT_SPECIES,
    TANK_VOLUME,
    SOIL_VOLUME,
    MAIN_MENU,
    AMA,
    GREENS_INPUT,
    CO2_FOOD_WASTE_INPUT,
    COMPOST_HELPER_INPUT,
)
from handlers.auth import (
    start as start_conversation,
    direct_start_command,
    auth_choice,
    register_username,
    register_password,
    login_username,
    login_password,
    plant_species,
    tank_volume,
    soil_volume,
    cancel,
    help_command,
)
from handlers.llama_handler import llama_response
from handlers.commands import (
    status_command,
    input_command,
    scan_command,
    handle_photo,
    care_command,
    profile_command,
    handle_calculator_choice,
    handle_greens_input,
    compost_helper_start,
    compost_helper_input,
)
from services.emissions_calculator import (
    co2_calculator_command,
    handle_co2_callback,
    handle_food_waste_input,
)
from handlers.menu import handle_main_menu
from handlers.speech_handler import handle_voice  # <-- New import

def main() -> None:
    # Configure logging
    logging.basicConfig(
        format=Config.LOGGING_FORMAT,
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    # Build the application
    Config.validate_required_env_vars()
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # Conversation flow: auth → setup → main menu → AMA
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_conversation)],
        states={
            AUTH_CHOICE:       [CallbackQueryHandler(auth_choice)],
            REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_username)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
            LOGIN_USERNAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)],
            LOGIN_PASSWORD:    [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
            PLANT_SPECIES:     [CallbackQueryHandler(plant_species)],
            TANK_VOLUME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, tank_volume)],
            SOIL_VOLUME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, soil_volume)],
            MAIN_MENU:         [
                CallbackQueryHandler(handle_main_menu),
                MessageHandler(filters.PHOTO, handle_photo)  # Add photo handling to MAIN_MENU state
            ],
            AMA:               [MessageHandler(filters.TEXT & ~filters.COMMAND, llama_response),
                                MessageHandler(filters.VOICE, handle_voice),],
            GREENS_INPUT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_greens_input)],
            CO2_FOOD_WASTE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_food_waste_input)],
            COMPOST_HELPER_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, compost_helper_input),
                CallbackQueryHandler(handle_main_menu, pattern="^back_to_menu$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="nutribot_conversation",
    )

    # Non-conversation command handlers (checked before conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("input", input_command))
    application.add_handler(CommandHandler("scan", scan_command))
    application.add_handler(CommandHandler("care", care_command))
    application.add_handler(CommandHandler("co2", co2_calculator_command))
    application.add_handler(CommandHandler("profile", profile_command))

    # Voice handler (keep this outside conversation as it doesn't need state)
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Add the conversation handler
    application.add_handler(conv_handler)

    # Fallback direct /start (when not in a conversation)
    application.add_handler(CommandHandler("start", direct_start_command))

    # Start polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
