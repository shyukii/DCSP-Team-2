from telegram import BotCommand

COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("status", "Check compost readiness status"),
    BotCommand("input", "Input greens for feed calculator"),
    BotCommand("scan", "Scan compost image"),
    BotCommand("care", "Get plant care tips"),
    BotCommand("co2", "Estimate CO2 impact"),
    BotCommand("profile", "View or edit profile"),
    BotCommand("back", "Return to main menu"),
    BotCommand("compost_helper", "Get compost yield estimate"),
]