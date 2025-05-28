import os
import re
from types import SimpleNamespace

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from services.speech_to_text import convert_to_wav, transcribe_audio
from constants import KEYWORD_TRIGGERS
from handlers.auth import help_command  # still comes from auth
from handlers.commands import (
    status_command,
    input_command,
    scan_command,
    care_command,
    co2_command,
    back_command
)
from handlers.auth import (
    register_username,
    register_password,
    login_username,
    login_password,
    REGISTER_USERNAME,
    REGISTER_PASSWORD,
    LOGIN_USERNAME,
    LOGIN_PASSWORD
)

INTENT_HANDLERS = {
    "help":   help_command,
    "status": status_command,
    "input":  input_command,
    "scan":   scan_command,
    "care":   care_command,
    "co2":    co2_command,
    "back":   back_command,
}

def extract_username(text: str) -> str:
    m = re.search(r'\b\w+\b', text)
    return m.group(0).capitalize() if m else ""

def words_to_digits(text: str) -> str:
    mapping = {
        "zero":"0","one":"1","two":"2","three":"3","four":"4",
        "five":"5","six":"6","seven":"7","eight":"8","nine":"9"
    }
    words = re.findall(r'\b(?:' + '|'.join(mapping) + r')\b', text.lower())
    return "".join(mapping[w] for w in words)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file  = await context.bot.get_file(voice.file_id)

    # ensure temp folder exists
    os.makedirs("temp", exist_ok=True)

    ogg = os.path.join("temp", f"{voice.file_unique_id}.ogg")
    wav = ogg.replace(".ogg", ".wav")

    await file.download_to_drive(ogg)
    if not convert_to_wav(ogg, wav):
        await update.message.reply_text("Sorry, I couldn’t convert your audio.")
        os.remove(ogg)
        return

    transcription = transcribe_audio(wav).lower()
    await update.message.reply_text(f"🗣️ You said: {transcription}")

    # Clean up
    try:
        os.remove(ogg)
        os.remove(wav)
    except OSError:
        pass

    # 1) Registration/login flow
    state = context.user_data.get("current_state")
    if state == REGISTER_USERNAME:
        context.user_data["current_state"] = None
        username = extract_username(transcription)
        fake_msg = SimpleNamespace(
            text=username, chat=update.message.chat,
            from_user=update.message.from_user,
            reply_text=update.message.reply_text
        )
        fake_upd = SimpleNamespace(message=fake_msg, effective_user=update.effective_user)
        return await register_username(fake_upd, context)

    if state == REGISTER_PASSWORD:
        context.user_data["current_state"] = None
        password = words_to_digits(transcription)
        fake_msg = SimpleNamespace(
            text=password, chat=update.message.chat,
            from_user=update.message.from_user,
            reply_text=update.message.reply_text
        )
        fake_upd = SimpleNamespace(message=fake_msg, effective_user=update.effective_user)
        return await register_password(fake_upd, context)

    if state == LOGIN_USERNAME:
        context.user_data["current_state"] = None
        username = extract_username(transcription)
        fake_msg = SimpleNamespace(
            text=username, chat=update.message.chat,
            from_user=update.message.from_user,
            reply_text=update.message.reply_text
        )
        fake_upd = SimpleNamespace(message=fake_msg, effective_user=update.effective_user)
        return await login_username(fake_upd, context)

    if state == LOGIN_PASSWORD:
        context.user_data["current_state"] = None
        password = words_to_digits(transcription)
        fake_msg = SimpleNamespace(
            text=password, chat=update.message.chat,
            from_user=update.message.from_user,
            reply_text=update.message.reply_text
        )
        fake_upd = SimpleNamespace(message=fake_msg, effective_user=update.effective_user)
        return await login_password(fake_upd, context)

    # 2) Voice-based auth triggers
    if any(kw in transcription for kw in ["register", "sign up", "create account"]):
        context.user_data["current_state"] = REGISTER_USERNAME
        await update.message.reply_text("Registration via voice—say your username.")
        return REGISTER_USERNAME

    if any(kw in transcription for kw in ["login", "sign in"]):
        context.user_data["current_state"] = LOGIN_USERNAME
        await update.message.reply_text("Login via voice—say your username.")
        return LOGIN_USERNAME

    # 3) Require login for other commands
    if not context.user_data.get("username"):
        await update.message.reply_text("🔒 Please /start and login first.")
        return

    # 4) Keyword dispatch
    for intent, kws in KEYWORD_TRIGGERS.items():
        if any(kw in transcription for kw in kws):
            return await INTENT_HANDLERS[intent](update, context)

    # 5) Fallback
    await update.message.reply_text(
        "Sorry, I didn’t catch that. Try 'check status', 'show me the commands', or 'analyze image'."
    )
