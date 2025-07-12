# Nutribot - Smart Composting Assistant

Nutribot is a Telegram chatbot that helps you manage your composting system.

## Project Structure

```
DCSP-Team-2/
├── Nutribot/                   # Main application directory
│   ├── main.py                # Main entry point (START HERE)
│   ├── config.py              # Configuration settings
│   ├── .env                   # Environment variables (create this)
│   ├── handlers/              # Command and message handlers
│   ├── services/             # Core business logic
│   └── utils/                # Utility functions
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Quick Setup

### Prerequisites
- Python 3.8+, Telegram account, FFmpeg

### Installation

1. Clone: `git clone https://github.com/shyukii/DCSP-Team-2 && cd DCSP-Team-2`

2. Virtual environment:
   - Windows: `python -m venv venv && venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv && source venv/bin/activate`

3. Install: `pip install -r requirements.txt`

4. Create `.env` file in `Nutribot/` directory with by copying `.env.example`

5. Run: `cd Nutribot && python main.py`

## Features

- **User Authentication:** Secure registration and login system
- **Plant Management:** Track your composting setup with plant species and container volumes
- **Image Analysis:** Upload photos of your compost for AI-powered analysis
- **Voice Commands:** Send voice messages for hands-free interaction
- **CO2 Calculator:** Calculate carbon emissions from your food waste
- **Feed Recommendations:** Get personalised advice on composting materials
- **Compost Helper:** Step-by-step guidance for optimal composting

## Available Commands

- `/start` - Begin using the bot and set up your profile
- `/help` - Get help and information about commands
- `/status` - Check the current status of your composting system
- `/scan` - Analyse photos of your compost
- `/care` - Get care instructions for your plants
- `/co2` - Calculate carbon emissions from food waste
- `/profile` - View and manage your profile
- `/cancel` - Cancel current operation

## How to Use

1. **First Time Setup:**
   - Start a conversation with your bot on Telegram
   - Use `/start` to begin registration
   - Choose to register a new account or log in
   - Set up your plant species and container volumes

2. **Daily Use:**
   - Send photos of your compost for analysis
   - Ask questions using the AI assistant
   - Use voice messages for convenience
   - Calculate emissions from your food waste
   - Get feeding recommendations for optimal composting

## Troubleshooting

- **Bot not responding:** Check your BOT_TOKEN in the .env file
- **Voice messages not working:** Ensure FFmpeg is properly installed
- **Image analysis failing:** Verify your CLARIFAI_PAT token is valid
- **AI responses not working:** Check your OpenAI API key and Replicate API tokens

To deactivate the virtual environment: `deactivate`
