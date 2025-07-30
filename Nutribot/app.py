from flask import Flask, request
from telegram import Update, Bot
import asyncio
import logging
import nest_asyncio

# Allow nested event loops
nest_asyncio.apply()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Import the configured application from main
import main
from config import Config

# Initialize bot and application
bot = Bot(token=Config.TELEGRAM_TOKEN)
main.application = main.create_application()
from main import setup_handlers
setup_handlers()
application = main.application

async def setup_webhook():
    """Set up webhook with Telegram"""
    # Initialize the application properly
    await application.initialize()
    await application.start()
    
    webhook_url = f"{Config.WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    print(f"Webhook registered: {webhook_url}")
    print("Bot ready to receive updates")

# Register webhook on startup
asyncio.run(setup_webhook())

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    
    # Process the update with nest_asyncio allowing nested event loops
    asyncio.run(application.process_update(update))
    
    return '', 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)