# Nutribot Process Flow Detailed Explanation

## 1. Bot Initialization Process

When you run `python main.py`, the following happens:

1. **Environment Setup**
   - Fixes encoding issues for Windows
   - Sets UTF-8 encoding for console output

2. **Configuration Loading**
   - `config.py` loads environment variables from `.env`
   - Retrieves bot token, API keys, and model settings

3. **Application Building**
   - Creates Telegram Application instance with bot token
   - Sets up conversation handler with entry points and states
   - Registers all command handlers
   - Starts polling for messages

## 2. User Interaction Flows

### A. New User Registration Flow
```
User sends /start
↓
auth.py: start_conversation()
↓
Shows "Login" or "Register" buttons
↓
User clicks "Register"
↓
auth.py: auth_choice() → Sets state to REGISTER_USERNAME
↓
Bot asks for username
↓
auth.py: register_username() → Validates & stores username
↓
Bot asks for password
↓
auth.py: register_password() → Stores credentials in loginIDs.json
↓
Bot asks for plant species (Tomato/Basil/Lettuce)
↓
auth.py: plant_species() → Stores preference
↓
Bot asks for compost volume
↓
auth.py: compost_volume() → Stores volume
↓
menu.py: show_main_menu() → Displays main menu
```

### B. AI Conversation Flow (Ask Me Anything)
```
User selects "Ask Me Anything" from menu
↓
menu.py: handle_main_menu() → Sets state to AMA
↓
User types question: "How do I care for tomatoes?"
↓
llama_handler.py: llama_response() receives message
↓
Shows typing indicator
↓
Calls llama_interface.py: generate_response()
↓
LlamaInterface formats prompt:
  "<|system|>You are NutriBot...</s>
   <|user|>How do I care for tomatoes?</s>
   <|assistant|>"
↓
Sends to Hugging Face API (zephyr-7b-beta model)
↓
Receives AI response
↓
Cleans response (removes formatting artifacts)
↓
Sends cleaned response to user
```

### C. Photo Analysis Flow
```
User sends photo of plant
↓
commands.py: handle_photo() receives image
↓
Downloads photo from Telegram servers
↓
clarifai_segmentation.py processes image
↓
Sends to Clarifai API for plant recognition
↓
Receives plant identification & health analysis
↓
Formats results and sends to user
```

### D. Voice Message Flow
```
User sends voice message
↓
speech_handler.py: handle_voice() receives audio
↓
Downloads voice file
↓
speech_to_text.py converts audio to text
↓
Passes text to llama_handler.py
↓
Same flow as text message from here
```

## 3. Data Storage Structure

### loginIDs.json Format
```json
{
  "username1": {
    "password": "user_password",
    "plant_species": "Tomato",
    "compost_volume": "50",
    "messages_sent": 10,
    "compost_inputs": 5,
    "co2_reduced": 25.5
  }
}
```

## 4. API Integration Details

### Hugging Face API
- **Endpoint**: `https://api-inference.huggingface.co/models/{model_name}`
- **Authentication**: Bearer token in headers
- **Payload Format**:
  ```json
  {
    "inputs": "formatted_prompt",
    "parameters": {
      "max_new_tokens": 500,
      "temperature": 0.8,
      "top_p": 0.9,
      "do_sample": true,
      "return_full_text": false
    }
  }
  ```

### Telegram Bot API
- Uses python-telegram-bot library
- Webhook disabled, uses polling
- Handles updates for messages, callbacks, photos, voice

### Clarifai API
- Used for image recognition
- Identifies plant species
- Analyzes plant health

## 5. Error Handling Mechanisms

1. **API Failures**
   - LlamaInterface has fallback models
   - If primary model fails, switches to backup
   - User-friendly error messages

2. **Network Issues**
   - Timeout handling (30 seconds)
   - Retry logic for transient failures
   - Graceful degradation

3. **Invalid Input**
   - Validation at each step
   - Clear error messages
   - Option to retry or cancel

## 6. State Management

The bot uses a finite state machine approach:
- Each user interaction moves through defined states
- States are defined in `constants.py`
- ConversationHandler manages state transitions
- Users can cancel at any time with `/cancel`

## 7. Security Considerations

Current Implementation:
- API keys in .env file (not in version control)
- User passwords stored in plain text (security risk)
- No rate limiting
- No input sanitization

Recommended Improvements:
- Hash passwords using bcrypt
- Implement rate limiting
- Add input validation
- Use database instead of JSON file
- Add user session management