# services/speech_to_text.py

import logging
import io
from dotenv import load_dotenv
import openai
from config import Config

logger = logging.getLogger(__name__)
load_dotenv()

# Set up OpenAI client
openai.api_key = Config.OPENAI_API_KEY

async def transcribe_audio_memory(audio_buffer: io.BytesIO) -> str:
    """
    Speech-to-Text using OpenAI Whisper API directly from memory buffer
    """
    try:
        # Reset buffer position
        audio_buffer.seek(0)
        
        # Check buffer size (OpenAI has 25MB limit)
        buffer_size = len(audio_buffer.getvalue())
        if buffer_size > 25 * 1024 * 1024:  # 25MB limit
            logger.error(f"Audio buffer too large: {buffer_size} bytes")
            return ""

        logger.info(f"🎯 Transcribing audio with OpenAI Whisper ({buffer_size} bytes)...")
        
        # Reset position before reading
        audio_buffer.seek(0)
        
        # Set a filename for the buffer (OpenAI needs this for format detection)
        audio_buffer.name = "voice_message.ogg"
        
        # Create OpenAI client and transcribe
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_buffer,
            response_format="text"
        )
        
        # Response is just the text string
        text = response.strip() if isinstance(response, str) else str(response).strip()
        
        if not text:
            logger.warning("Empty transcription result from OpenAI")
            return ""
            
        logger.info(f"✅ Transcribed: {text!r}")
        return text

    except Exception as e:
        logger.error(f"⚠️ OpenAI Whisper transcription failed: {e}")
        return ""


# Legacy functions (keeping for backward compatibility but not used)
def convert_to_wav_memory(input_buffer: io.BytesIO) -> io.BytesIO:
    """
    No longer needed - OpenAI Whisper accepts OGG directly
    """
    logger.warning("convert_to_wav_memory called but no longer needed with OpenAI API")
    return input_buffer


def transcribe_audio(audio_path: str) -> str:
    """
    Legacy file-based transcription (not used in memory implementation)
    """
    logger.warning("Legacy transcribe_audio called - consider using transcribe_audio_memory")
    try:
        with open(audio_path, "rb") as audio_file:
            client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            return response.strip() if isinstance(response, str) else str(response).strip()
    except Exception as e:
        logger.error(f"⚠️ OpenAI transcription failed: {e}")
        return ""

