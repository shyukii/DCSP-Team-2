# Nutribot Architecture and File Structure

## Overview
Nutribot is a Telegram bot that helps users with gardening, composting, and environmental topics. It uses AI (via Hugging Face models) to answer questions and provides various features for plant care and composting management.

## Core Files and Their Functions

### 1. Entry Point
**`Nutribot/main.py`**
- The main entry point of the application
- Sets up the Telegram bot using python-telegram-bot library
- Configures all command handlers and conversation flows
- Key responsibilities:
  - Initialize the Telegram Application with bot token
  - Set up conversation handler for authentication flow
  - Register command handlers (/help, /status, /scan, etc.)
  - Handle photo and voice message inputs
  - Start the bot polling loop

### 2. Configuration
**`Nutribot/config.py`**
- Loads environment variables from .env file
- Defines configuration constants:
  - `TELEGRAM_TOKEN`: Bot authentication token
  - `CLARIFAI_PAT`: API key for image recognition
  - `LLAMA_MODEL`: AI model to use (currently HuggingFaceH4/zephyr-7b-beta)
  - `HUGGINGFACE_API_TOKEN`: Authentication for Hugging Face API
  - `FFMPEG_PATH`: Path to ffmpeg for audio processing

**`Nutribot/.env`**
- Stores sensitive configuration values
- Should not be committed to version control
- Contains API keys and tokens

### 3. Constants
**`Nutribot/constants.py`**
- Defines conversation states for the bot's state machine
- States include:
  - Authentication states (AUTH_CHOICE, LOGIN_USERNAME, etc.)
  - Setup states (PLANT_SPECIES, COMPOST_VOLUME)
  - Interaction states (MAIN_MENU, AMA, GREENS_INPUT)

## Handler Files

### 4. Authentication Handler
**`Nutribot/handlers/auth.py`**
- Manages user registration and login
- Stores user credentials in loginIDs.json
- Handles the initial setup flow:
  1. User chooses login or register
  2. Collects username/password
  3. Asks for plant species preference
  4. Gets compost bin volume
- Transitions to main menu after successful auth

### 5. LLaMA Handler
**`Nutribot/handlers/llama_handler.py`**
- Manages AI-powered conversations
- Key function: `llama_response()`
  - Receives user messages
  - Sends typing indicator
  - Calls LlamaInterface to generate response
  - Handles errors gracefully
- Allows users to return to menu with /menu, /back, or /exit

### 6. Command Handlers
**`Nutribot/handlers/commands.py`**
- Implements various bot commands:
  - `/status`: Shows plant and compost status
  - `/input`: Records composting inputs
  - `/scan`: Initiates plant scanning via photo
  - `/care`: Provides plant care tips
  - `/co2`: Calculates CO2 reduction
  - `/profile`: Shows user profile
- `handle_photo()`: Processes uploaded images
- `handle_greens_input()`: Processes composting data

### 7. Menu Handler
**`Nutribot/handlers/menu.py`**
- Manages the main menu interface
- Creates inline keyboard buttons for navigation
- Routes user selections to appropriate handlers
- Options include:
  - Ask Me Anything (AI chat)
  - Compost Status
  - Plant Care Tips
  - CO2 Calculator
  - Profile

### 8. Speech Handler
**`Nutribot/handlers/speech_handler.py`**
- Processes voice messages
- Converts speech to text
- Passes text to LLaMA for response

## Service Files

### 9. LLaMA Interface
**`Nutribot/services/llama_interface.py`**
- Core AI integration service
- Class: `LlamaInterface`
- Key features:
  - Connects to Hugging Face Inference API
  - Formats prompts for the AI model
  - Handles API errors with fallback models
  - Cleans up AI responses
- Current implementation:
  - Uses zephyr-7b-beta model
  - Formats prompts with system/user/assistant tags
  - Removes formatting artifacts from responses

### 10. Image Segmentation
**`Nutribot/services/clarifai_segmentation.py`**
- Integrates with Clarifai API for plant recognition
- Analyzes uploaded photos
- Identifies plant species and health

### 11. Emissions Calculator
**`Nutribot/services/emissions_calculator.py`**
- Calculates CO2 reduction from composting
- Provides environmental impact metrics

### 12. Other Services
- **`extraction_timing.py`**: Manages compost readiness timing
- **`feeding_input.py`**: Processes composting input data
- **`speech_to_text.py`**: Converts audio to text

## Data Storage
**`Nutribot/loginIDs.json`**
- Stores user credentials and preferences
- Format: JSON with username as key
- Contains:
  - Password (should be hashed in production)
  - Plant species preference
  - Compost volume
  - User statistics

## Process Flow

### 1. Bot Startup
```
main.py → Load config.py → Initialize handlers → Start polling
```

### 2. New User Flow
```
/start → auth.py (register) → Get username/password → 
Get preferences → Save to loginIDs.json → Show main menu
```

### 3. AI Conversation Flow
```
User message → llama_handler.py → llama_interface.py → 
Hugging Face API → Clean response → Send to user
```

### 4. Photo Processing Flow
```
User sends photo → commands.py (handle_photo) → 
clarifai_segmentation.py → Analyze image → 
Return plant info → Send response
```

### 5. Voice Message Flow
```
Voice message → speech_handler.py → speech_to_text.py → 
Convert to text → llama_handler.py → AI response
```

## Error Handling
- API failures trigger fallback models
- Network errors show user-friendly messages
- Invalid inputs prompt for corrections
- All errors are logged for debugging

## Security Considerations
- API tokens stored in .env file
- User passwords should be hashed (currently plain text)
- Input validation needed for user data
- Rate limiting should be implemented

## Future Improvements
1. Implement proper password hashing
2. Add database instead of JSON file
3. Implement conversation context/memory
4. Add more plant species support
5. Enhance composting calculations
6. Add multilingual support