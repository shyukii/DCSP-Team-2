import os
import re

from telegram import Update
from telegram.ext import ContextTypes, filters

from services.speech_to_text import convert_to_wav, transcribe_audio
from constants import KEYWORD_TRIGGERS
from handlers.auth import help_command
from handlers.commands import (
    status_command,
    input_command,
    scan_command,
    care_command,
    co2_command,
    back_command
)

# Map intents to their handlers
INTENT_HANDLERS = {
    "help":   help_command,
    "status": status_command,
    "input":  input_command,
    "scan":   scan_command,
    "care":   care_command,
    "co2":    co2_command,
    "back":   back_command,
}

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file  = await context.bot.get_file(voice.file_id)

    # ensure temp folder exists
    os.makedirs("temp", exist_ok=True)
    ogg = os.path.join("temp", f"{voice.file_unique_id}.ogg")
    wav = ogg.replace(".ogg", ".wav")

    # download & convert
    await file.download_to_drive(ogg)
    if not convert_to_wav(ogg, wav):
        await update.message.reply_text("⚠️ Couldn’t convert audio.")
        os.remove(ogg)
        return

    # transcribe
    transcription = transcribe_audio(wav).lower()
    await update.message.reply_text(f"🗣️ You said: {transcription}")

    # cleanup
    for path in (ogg, wav):
        try: os.remove(path)
        except: pass

    # require prior login via text
    if not context.user_data.get("username"):
        await update.message.reply_text(
            "🔒 Voice commands work only after you’ve logged in via /start.\n"
            "Please register or login using text first."
        )
        return

    # dispatch by keyword
    for intent, keywords in KEYWORD_TRIGGERS.items():
        if any(kw in transcription for kw in keywords):
            return await INTENT_HANDLERS[intent](update, context)

    # fallback
    await update.message.reply_text(
        "🤔 I didn’t catch that. Try saying: ‘help’, ‘status’, ‘input’, ‘scan’, ‘care’, ‘co2’, or ‘back’."
    )
