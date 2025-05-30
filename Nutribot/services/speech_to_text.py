# services/speech_to_text.py

import os
import logging
from dotenv import load_dotenv
import replicate

logger = logging.getLogger(__name__)
load_dotenv()

# Make sure this is set in your .env
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_TOKEN:
    raise RuntimeError("⚠️  Please set REPLICATE_API_TOKEN in your .env")

# Pin to the only available version on Replicate
MODEL = (
    "cjwbw/seamless_communication:"
    "668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0"
)

def convert_to_wav(input_path: str, output_path: str) -> bool:
    from config import FFMPEG_PATH
    import subprocess

    try:
        subprocess.run(
            [
                FFMPEG_PATH,
                "-i", input_path,
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y",
                output_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(f"✅ Converted {input_path} → {output_path}")
        return True
    except Exception as e:
        logger.error(f"FFmpeg conversion error: {e}")
        return False


def transcribe_audio(wav_path: str) -> str:
    """
    Speech-to-Text TRANSLATION: auto-detect spoken language, always return English.
    """
    if not os.path.exists(wav_path):
        logger.error(f"Audio file not found: {wav_path}")
        return ""

    try:
        with open(wav_path, "rb") as audio_file:
            output = replicate.run(
                MODEL,
                input={
                    "input_audio": audio_file,
                    "task_name": "S2TT (Speech to Text translation)",
                    "target_language_text_only": "English",  # <-- force English output
                },
                api_token=REPLICATE_TOKEN,
            )

        text = output.get("text_output", "") or ""
        logger.info(f"🔤 Translated to English: {text!r}")
        return text.strip()

    except Exception as e:
        logger.error(f"⚠️ Replicate S2TT failed: {e}")
        return ""

