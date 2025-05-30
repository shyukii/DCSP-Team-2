# Conversation states
AMA, AUTH_CHOICE, REGISTER_USERNAME, REGISTER_PASSWORD, LOGIN_USERNAME, LOGIN_PASSWORD, PLANT_SPECIES, TANK_VOLUME, SOIL_VOLUME, MAIN_MENU, GREENS_INPUT, CO2_FOOD_WASTE_INPUT = range(12)

# Bot messages
WELCOME_MESSAGE = """👋 *Hi there! I'm NutriBot, your friendly composting and plant care assistant *🌱♻️

You don't need to be a gardening expert — just ask me anything!"""

REGISTRATION_MESSAGE = """ 👋 Welcome to NutriBot made by NutriCycle AI! 

Let us get your composting journey started the right way.

To begin, please follow these simple setup steps:

Choose your compost tank 
🪣 This can be a bin, bucket, or container with airflow. Make sure it is placed in a ventilated spot, either indoors or outdoors.

Add a base layer of soil
🌱 Soil helps with microbial activity and provides a healthy environment for decomposition.

Introduce your composting worms
🪱 Worms help break down food faster and improve compost quality. Red wigglers are the most common composting worms."""

GLOSSARY_MESSAGE = """Quick Composting Glossary: Key Terms Explained

Greens 🥬: Moist, nitrogen-rich food waste like fruit peels, veggie scraps, and coffee grounds.

Browns 🍂: Dry, carbon-rich items like dried leaves, cardboard, and shredded newspaper.

Moisture💧: Compost needs to feel like a wrung-out sponge — not too dry or too soggy.

Aeration 🌬: Turning or mixing your compost adds oxygen and helps speed up decomposition.

To learn more about composting, use our AI assistant using feature /care to get personalized advice and tips after you set up your compost tank!"""

HELP_MESSAGE = """Here is what I can do for you:

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
    "help":           ["help", "command", "commands", "show help"],
    "status":         ["status", "mature", "check status"],
    "input":          ["input", "compost feed", "feeding", "food", "water", "greens", "browns"],
    "scan":           ["scan", "image", "photo", "picture", "scan image"],
    "care":           ["care", "plant", "watering", "growth", "gardening","guidance"],
    "co2":            ["co2", "carbon", "emission", "savings", "co2 tracker"],
    "back":           ["back", "previous", "return", "go back"],
    "profile":        ["profile", "my profile", "show profile"],
    "compost_feed":   ["compost feed", "feeding recommendations","feeding"],
    "compost_extract":["compost extraction", "estimate compost", "compost helper","compost readiness","ready"],
    "image_scan":     ["image scan", "analyse image", "scan compost"],
    "help_commands":  ["help commands", "list commands", "what can i do"],
}

CHECK_READINESS, GET_CURRENT_VOL = range(9, 11)
BATCH_PLAN = 30
COMPOST_HELPER_INPUT = 31