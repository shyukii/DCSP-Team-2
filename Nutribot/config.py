import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CLARIFAI_PAT    = os.getenv("CLARIFAI_PAT")
LLAMA_MODEL     = os.getenv("LLAMA_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
LOGIN_FILE      = os.getenv("LOGIN_FILE", "loginIDs.json")

# Path to ffmpeg binary, loaded from .env (fallback to a default if you like)
FFMPEG_PATH     = os.getenv(
    "FFMPEG_PATH",
    r"C:/ffmpeg/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"
)