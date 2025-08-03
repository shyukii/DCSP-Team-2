from telegram import BotCommand

COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("status", "Check compost readiness status"),
    BotCommand("input", "Input greens for feed calculator"),
    BotCommand("scan", "Scan compost image"),
    BotCommand("care", "Get compost and plant care tips"),
    BotCommand("co2", "Estimate CO2 impact"),
    BotCommand("profile", "View or edit profile"),
    BotCommand("dashboards", "Access comprehensive analytics dashboards"),
    BotCommand("back", "Return to main menu"),
    BotCommand("watering", "Plant moisture projection")
]