from telegram import Update
from telegram.ext import ContextTypes
from constants import AMA

async def block_commands_during_ama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ You’re in Ask-Anything mode right now. Use /back or /menu to exit."
    )
    # Stay in AMA
    return AMA
