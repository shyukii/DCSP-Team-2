# services/speech_to_text.py

import os
import logging
from dotenv import load_dotenv
import replicate
from config import Config

logger = logging.getLogger(__name__)
load_dotenv()


# Pin to the only available version on Replicate
MODEL = Config.REPLICATE_SPEECH_MODEL

def convert_to_wav(input_path: str, output_path: str) -> bool:
    from config import FFMPEG_PATH
    import subprocess

    try:
        subprocess.run(
            [
                FFMPEG_PATH,
                "-i", input_path,
                "-acodec", Config.AUDIO_CODEC,
                "-ar", str(Config.AUDIO_SAMPLE_RATE),
                "-ac", str(Config.AUDIO_CHANNELS),
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
                api_token=Config.REPLICATE_API_TOKEN,
            )

        text = output.get("text_output", "") or ""
        logger.info(f"🔤 Translated to English: {text!r}")
        return text.strip()

    except Exception as e:
        logger.error(f"⚠️ Replicate S2TT failed: {e}")
        return ""

