import os
import subprocess
from dotenv import load_dotenv
import replicate
import requests

from config import FFMPEG_PATH

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("speech_to_text")

def convert_to_wav(ogg_path: str, wav_path: str) -> bool:
    """
    Use ffmpeg to convert .ogg to mono 16 kHz .wav.
    """
    cmd = [
        FFMPEG_PATH,
        "-i", ogg_path,
        "-ar", "16000",
        "-ac", "1",
        wav_path,
        "-y"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode == 0

import replicate

client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

def transcribe_audio(wav_path: str) -> str:
    # Upload directly via Replicate
    audio_url = client.upload_file(open(wav_path, "rb"))

    output = client.run(
        "facebook/seamless-m4t-v2-large:9277f86d4f5d8dc06a05bb8fc55fdfc6e43bb3171c8354edaa95161d6df0c96f",
        input={
            "audio": audio_url,
            "task": "transcribe",
            "target_language": "eng"
        }
    )
    return output.get("text", str(output))
