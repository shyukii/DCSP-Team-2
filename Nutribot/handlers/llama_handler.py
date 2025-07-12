import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.llama_interface import LlamaInterface
from handlers.menu import show_main_menu
from constants import AMA

logger = logging.getLogger(__name__)
llama = LlamaInterface()

async def llama_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # 1) If this message has no text (voice path), pull from last_llama_input
    raw = update.message.text
    if raw is None:
        raw = context.user_data.pop("last_llama_input", "")

    # 2) If still empty, prompt the user to retry
    if not raw:
        await update.message.reply_text("⚠️ I didn’t catch any text. Please type or speak again.")
        return AMA

    text = raw

    # 3a) Allow only /menu and /back to exit AMA mode
    if text.lower() in ['/menu', '/back']:
        context.user_data.pop("state", None)
        llama.clear_memory()
        return await show_main_menu(update, context)

    # 3b) Block all other /commands
    if text.startswith("/") and text.lower() not in ['/menu', '/back']:
        await update.message.reply_text("❌ That command isn't available right now. Use /back to return to the menu.")
        return AMA

    # 4) Send the prompt to Llama
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
