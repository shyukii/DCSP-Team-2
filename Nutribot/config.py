import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration management for Nutribot"""
    
    # API Tokens & Keys
    TELEGRAM_TOKEN: str = os.getenv("BOT_TOKEN")
    CLARIFAI_PAT: str = os.getenv("CLARIFAI_PAT")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")
    
    # AI Models & Endpoints
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini-2025-04-14")
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    
    # Replicate Models
    REPLICATE_SPEECH_MODEL: str = "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0"
    
    # Clarifai Configuration
    CLARIFAI_USER_ID: str = "clarifai"
    CLARIFAI_APP_ID: str = "main"
    CLARIFAI_MODEL_ID: str = "image-subject-segmentation"
    CLARIFAI_MODEL_VERSION: str = "55b2051b75f14577b6fdd5a4fa3fd5a7"
    
    # File Paths
    LOGIN_FILE: str = os.getenv("LOGIN_FILE", "loginIDs.json")
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", r"C:/ffmpeg/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe")
    TEMP_AUDIO_DIR: str = "temp/"
    
    # API Timeouts & Limits
    HTTP_TIMEOUT: int = 30
    MAX_AUDIO_DURATION: int = 120
    MAX_FOOD_WASTE_INPUT: int = 100
    
    # AI Model Parameters
    AI_MAX_NEW_TOKENS: int = 500
    AI_TEMPERATURE: float = 0.8
    AI_TOP_P: float = 0.9
    
    # Audio Processing Settings
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    AUDIO_CODEC: str = "pcm_s16le"
    
    # Scientific Constants
    class CompostCalculations:
        GREENS_CN_RATIO: int = 20
        BROWNS_CN_RATIO: int = 300
        TARGET_CN_RATIO: int = 30
        TARGET_MOISTURE: float = 0.55
        GREENS_WATER_CONTENT: float = 0.8
        BROWNS_WATER_CONTENT: float = 0.15
        COMPOST_DENSITY: float = 0.4  # kg/L
        
        # For extraction timing
        CN_GREENS: int = 17
        CN_BROWNS: int = 70
        MASS_LOSS_ESTIMATE: float = 0.5
        TIME_PER_KG_GREENS: int = 6  # days
        TIMING_VARIABILITY: float = 0.2  # ±20%
    
    class EmissionsCalculations:
        STP_AIR_CONCENTRATION_PERCENT: float = 21.0
        STP_CO2_PPM: float = 415.0
        FOOD_WASTE_CO2_FACTOR: float = 2.5  # kg CO2 per kg food waste
        COMPOST_REDUCTION_FACTOR: float = 0.8  # 80% reduction
        TREE_CO2_ABSORPTION: float = 25.0  # kg CO2 per tree per year
        PETROL_CO2_FACTOR: float = 2.3  # kg CO2 per litre
        CAR_CO2_FACTOR: float = 0.4  # kg CO2 per mile
    
    # Database Configuration
    DATABASE_TABLE: str = "users"
    
    # Plant Species Options
    PLANT_SPECIES: List[str] = ["Lady's Finger", "Spinach", "Long Bean"]
    
    # Logging Configuration
    LOGGING_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate_required_env_vars(cls) -> None:
        """Validate that all required environment variables are set"""
        required_vars = {
            "BOT_TOKEN": cls.TELEGRAM_TOKEN,
            "CLARIFAI_PAT": cls.CLARIFAI_PAT,
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "REPLICATE_API_TOKEN": cls.REPLICATE_API_TOKEN,
            "SUPABASE_URL": cls.SUPABASE_URL,
            "SUPABASE_ANON_KEY": cls.SUPABASE_ANON_KEY
        }
        
        missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @classmethod
    def get_keyword_triggers(cls) -> Dict[str, List[str]]:
        """Return keyword triggers for voice commands"""
        return {
            "feeding": ["feed", "feeding", "calculator", "browns", "greens", "compost ratio"],
            "emissions": ["emissions", "co2", "carbon", "environment", "tracking"],
            "extraction": ["extract", "extraction", "harvest", "timing", "ready"],
            "image": ["image", "photo", "picture", "analyze", "analysis"],
            "chat": ["chat", "talk", "ask", "question", "help", "advice"]
        }

# Backwards compatibility - maintain old variable names for now
TELEGRAM_TOKEN = Config.TELEGRAM_TOKEN
CLARIFAI_PAT = Config.CLARIFAI_PAT
OPENAI_MODEL = Config.OPENAI_MODEL
LOGIN_FILE = Config.LOGIN_FILE
OPENAI_API_KEY = Config.OPENAI_API_KEY
REPLICATE_API_TOKEN = Config.REPLICATE_API_TOKEN
FFMPEG_PATH = Config.FFMPEG_PATH