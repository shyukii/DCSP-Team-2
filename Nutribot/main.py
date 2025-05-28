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

from config import TELEGRAM_TOKEN
from constants import (
    AUTH_CHOICE,
    REGISTER_USERNAME,
    REGISTER_PASSWORD,
    LOGIN_USERNAME,
    LOGIN_PASSWORD,
    PLANT_SPECIES,
    COMPOST_VOLUME,
    MAIN_MENU,
    AMA,
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
    compost_volume,
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
    co2_command,
    profile_command,
)
from handlers.menu import handle_main_menu
from handlers.speech_handler import handle_voice  # <-- New import

def main() -> None:
    # Configure logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    # Build the application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

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
            COMPOST_VOLUME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, compost_volume)],
            MAIN_MENU:         [CallbackQueryHandler(handle_main_menu)],
            AMA:               [MessageHandler(filters.TEXT & ~filters.COMMAND, llama_response)],
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
    application.add_handler(CommandHandler("co2", co2_command))
    application.add_handler(CommandHandler("profile", profile_command))

    # Photo and voice handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))  # <-- Voice support

    # Add the conversation handler
    application.add_handler(conv_handler)

    # Fallback direct /start (when not in a conversation)
    application.add_handler(CommandHandler("start", direct_start_command))

    # Start polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
