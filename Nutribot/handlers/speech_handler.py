import logging
import io

from telegram import Update
from telegram.ext import ContextTypes

from services.speech_to_text import transcribe_audio_memory
from constants import KEYWORD_TRIGGERS, AMA
from handlers.llama_handler import llama_response
from config import Config
from handlers.auth import help_command
from handlers.commands import (
    status_command,
    input_command,
    scan_command,
    care_command,
    co2_command,
    back_command,
    profile_command,     
    compost_helper_start,  
)

logger = logging.getLogger(__name__)

INTENT_HANDLERS = {
    "help":   help_command,
    "status": status_command,
    "input":  input_command,
    "scan":   scan_command,
    "care":   care_command,
    "co2":    co2_command,
    "back":   back_command,
    "profile":        profile_command,
    "compost_feed":   input_command,
    "compost_extract":compost_helper_start,
    "image_scan":     scan_command,
    "help_commands":  help_command,
}

MAX_AUDIO_DURATION = Config.MAX_AUDIO_DURATION  # seconds

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    user_id = update.effective_user.id
    logger.info(f"Processing voice from user {user_id}")

    if voice.duration > MAX_AUDIO_DURATION:
        await update.message.reply_text(
            f"⏰ Please keep voice messages under {MAX_AUDIO_DURATION}s."
        )
        return

    file = await context.bot.get_file(voice.file_id)

    try:
        await update.message.reply_text("🎤 Processing your voice…")
        
        # Download audio data directly to memory
        ogg_buffer = io.BytesIO()
        await file.download_to_memory(ogg_buffer)
        ogg_buffer.seek(0)

        # Transcribe audio directly from OGG buffer using OpenAI Whisper
        transcription = await transcribe_audio_memory(ogg_buffer)
        if not transcription:
            await update.message.reply_text(
                "❌ I didn't catch that—please try again."
            )
            return

        await update.message.reply_text(f"🗣️ You said: \"{transcription}\"")

        if not context.user_data.get("username"):
            await update.message.reply_text(
                "🔐 Voice commands only work after login. Use /start first."
            )
            return

        await process_voice_command(update, context, transcription.lower())

    except Exception as e:
        logger.error(f"Error in handle_voice: {e}")
        await update.message.reply_text(
            "❌ Something went wrong. Please try again."
        )

async def process_voice_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    transcription: str
):
    # 1) If user is already in AMA (Ask Anything) state, short‐circuit to llama_response:
    if context.user_data.get("state") == AMA:
        # 1) Store the transcription so llama_response can read it:
        context.user_data["last_llama_input"] = transcription

        await update.message.reply_text("💬 Passing your voice message to NutriBot…")
        return await llama_response(update, context)

    # 2) Otherwise, try to match one of the keyword intents first:
    matched = None
    for intent, keywords in KEYWORD_TRIGGERS.items():
        if any(kw.lower() in transcription for kw in keywords):
            matched = intent
            break

    if matched and matched in INTENT_HANDLERS:
        try:
            await INTENT_HANDLERS[matched](update, context)
        except Exception as e:
            logger.error(f"Error executing '{matched}': {e}")
            await update.message.reply_text(
                f"❌ Couldn’t run '{matched}'. Please try again."
            )
    else:
        # 3) If nothing matched, prompt user to either use text or say “Ask Anything” first:
        await update.message.reply_text(
            "🤔 I didn’t catch a valid command. If you want to ask NutriBot, please first tap “Ask Anything” or type it, then speak."
        )