import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.llama_interface import LlamaInterface
from handlers.menu import show_main_menu
from constants import AMA

logger = logging.getLogger(__name__)
llama = LlamaInterface()

async def llama_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text.lower() in ['/menu','/back','/exit']:
        user = context.user_data.get("username")
        return await show_main_menu(update, context, user)

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        resp = await llama.generate_response(text)
        await update.message.reply_text(resp)
    except Exception as e:
        logger.error(f"Llama error: {e}")
        await update.message.reply_text(
            "Sorry, I'm having trouble processing your request. Please try again."
        )
    return AMA
