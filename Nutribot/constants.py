# Conversation states
AMA, AUTH_CHOICE, REGISTER_USERNAME, REGISTER_PASSWORD, LOGIN_USERNAME, LOGIN_PASSWORD, PLANT_SPECIES, COMPOST_VOLUME, MAIN_MENU = range(9)

# Bot messages
WELCOME_MESSAGE = """👋 Hi there! I'm NutriBot, your friendly composting and plant care assistant 🌱♻️

You don't need to be a gardening expert — just ask me anything!"""

HELP_MESSAGE = """Here's what I can do for you:

/status — Check compost readiness  
/input  — Get food & water guidance  
/scan   — Upload compost or plant image for analysis  
/care   — Get compost or plant care advice  
/co2    — View your CO₂ emissions impact  
/profile— Update your compost setup  
/help   — Show this commands list

Type a command or tap a button to get started!
"""
KEYWORD_TRIGGERS = {
    "help":   ["help", "command"],
    "status": ["status", "ready", "mature"],
    "input":  ["input", "food", "water"],
    "scan":   ["scan", "image", "photo", "picture"],
    "care":   ["care", "plant", "watering", "growth"],
    "co2":    ["co2", "carbon", "emission", "savings"],
    "back":   ["back", "previous", "return"],
}