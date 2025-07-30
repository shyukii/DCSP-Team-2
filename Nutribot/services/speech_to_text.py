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
    Speech-to-Text using OpenAI Whisper via Replicate
    """
    if not os.path.exists(wav_path):
        logger.error(f"Audio file not found: {wav_path}")
        return ""

    # Check file size (Replicate has limits)
    file_size = os.path.getsize(wav_path)
    if file_size > 25 * 1024 * 1024:  # 25MB limit
        logger.error(f"Audio file too large: {file_size} bytes")
        return ""

    try:
        # Upload file to Replicate first
        logger.info(f"📤 Uploading audio file to Replicate ({file_size} bytes)...")
        with open(wav_path, "rb") as audio_file:
            file_upload = replicate.files.create(audio_file)

        logger.info(f"✅ File uploaded: {file_upload}")

        # Now use the uploaded file URL
        output = replicate.run(
            MODEL,
            input={
                "audio": file_upload.urls["get"],  # Use the URL from the File object
                "model": "base",           
                "language": "auto",        
                "translate": False,         
                "temperature": 0,          
                "suppress_tokens": "-1",   
                "initial_prompt": "",      
            }
        )

        # Extract transcription from output
        if isinstance(output, dict):
            text = output.get("transcription", "") or output.get("text", "")
        elif isinstance(output, str):
            text = output
        else:
            text = str(output)
        
        if not text:
            logger.warning("Empty transcription result")
            return ""
            
        logger.info(f"🔤 Transcribed: {text!r}")
        return text.strip()

    except Exception as e:
        logger.error(f"⚠️ Replicate Whisper failed: {e}")
        return ""

