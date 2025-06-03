import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.llama_interface import LlamaInterface
from handlers.menu import show_main_menu
from constants import AMA

logger = logging.getLogger(__name__)
llama = LlamaInterface()

#async def llama_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#    text = update.message.text
#    if text.lower() in ['/menu','/back','/exit']:
#        user = context.user_data.get("username")
#        # ← before showing the main menu again, clear the AMA flag:
#        context.user_data.pop("state", None)
#        return await show_main_menu(update, context, user)

#    try:
#        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
#        resp = await llama.generate_response(text)
#        await update.message.reply_text(resp)
#    except Exception as e:
#        logger.error(f"Llama error: {e}")
#        await update.message.reply_text(
#            "Sorry, I'm having trouble processing your request. Please try again."
#        )
#    return AMA

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

    # 3) Check for exit commands
    if text.lower() in ['/menu','/back','/exit']:
        user = context.user_data.get("username")
        context.user_data.pop("state", None)
        return await show_main_menu(update, context, user)

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
