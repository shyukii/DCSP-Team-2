import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration management for Nutribot"""
    
    # API Tokens & Keys
    TELEGRAM_TOKEN: str = os.getenv("BOT_TOKEN")
    CLARIFAI_PAT: str = os.getenv("CLARIFAI_PAT")  # Legacy/fallback
    CLARIFAI_TANK_PAT: str = os.getenv("CLARIFAI_TANK_PAT")
    CLARIFAI_PLANT_PAT: str = os.getenv("CLARIFAI_PLANT_PAT")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")
    
    # AI Models & Endpoints
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini-2025-04-14")
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    
    # Replicate Models
    REPLICATE_SPEECH_MODEL: str = "openai/whisper:8099696689d249cf8b122d833c36ac3f75505c666a395ca40ef26f68e7d3d16e"
    
    # Clarifai Configuration
    CLARIFAI_COMPOST_MODEL_URL: str = "https://clarifai.com/shyueqi/Nuritbot/models/TANKER-SEGMENTER"
    CLARIFAI_PLANT_MODEL_URL: str = "https://clarifai.com/s10257235/NutriBot-Image-Classification/models/Image-Classification-Model"
    
    # File Paths (removed FFMPEG_PATH - now using pydub)
    
    # Webhook Configuration
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8000"))
    
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
    
    
    # Logging Configuration
    LOGGING_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate_required_env_vars(cls) -> None:
        """Validate that all required environment variables are set"""
        required_vars = {
            "BOT_TOKEN": cls.TELEGRAM_TOKEN,
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "REPLICATE_API_TOKEN": cls.REPLICATE_API_TOKEN,
            "SUPABASE_URL": cls.SUPABASE_URL,
            "SUPABASE_ANON_KEY": cls.SUPABASE_ANON_KEY
        }
        
        # Check Clarifai PATs - at least one should be available
        clarifai_pats = [cls.CLARIFAI_TANK_PAT, cls.CLARIFAI_PLANT_PAT, cls.CLARIFAI_PAT]
        if not any(clarifai_pats):
            required_vars["CLARIFAI_PAT or CLARIFAI_TANK_PAT or CLARIFAI_PLANT_PAT"] = None
        
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
OPENAI_API_KEY = Config.OPENAI_API_KEY
REPLICATE_API_TOKEN = Config.REPLICATE_API_TOKEN
# Legacy - use specific model URLs instead
CLARIFAI_MODEL_URL = Config.CLARIFAI_COMPOST_MODEL_URL