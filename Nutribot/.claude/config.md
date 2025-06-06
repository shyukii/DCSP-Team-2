# Nutribot Configuration and Common Commands

## Supabase Configuration
```
SUPABASE_URL: https://nimflhaujdwzwirodude.supabase.co
SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbWZsaGF1amR3endpcm9kdWRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNjAzMjMsImV4cCI6MjA2NDczNjMyM30.hMjh7o7vAbxR6oqaL0oxu4Jyc8lAXs4ziS46LFQ4WhI
PROJECT_ID: nimflhaujdwzwirodude
```

## Database Schema
- **users** table:
  - id (uuid, primary key)
  - telegram_id (bigint, unique, not null) - Links to Telegram user ID for auto-auth
  - username (varchar, unique, not null)
  - password_hash (varchar, not null) - Bcrypt hashed password
  - plant_species (varchar) - User's selected plant type
  - compost_volume (numeric) - Currently unused, reserved for future use
  - tank_volume (numeric) - Compost tank volume in litres
  - soil_volume (numeric) - Soil volume in litres
  - total_food_waste_kg (numeric) - Running total of composted waste for CO2 tracking
  - created_at (timestamptz)
  - updated_at (timestamptz)

## Common Commands

### Python/Bot Commands
```bash
# Run the bot
cd Nutribot && python main.py

# Install dependencies
pip install -r requirements.txt

# Install Supabase client
pip install supabase

# Check Python syntax
python -m py_compile Nutribot/*.py

# Run tests (if any)
python -m pytest
```

### Git Commands
```bash
# Check status
git status

# Stage changes
git add .

# Commit with message
git commit -m "Integrate Supabase authentication with Telegram ID"

# Push to remote
git push origin main
```

### Supabase SQL Queries
```sql
-- Get user by Telegram ID
SELECT * FROM users WHERE telegram_id = $1;

-- Create new user
INSERT INTO users (telegram_id, username, password_hash) 
VALUES ($1, $2, $3) 
RETURNING *;

-- Update user profile
UPDATE users 
SET plant_species = $2, tank_volume = $3, soil_volume = $4, updated_at = NOW() 
WHERE telegram_id = $1;
```

### Environment Setup
```bash
# Create .env file
echo "SUPABASE_URL=https://nimflhaujdwzwirodude.supabase.co" > .env
echo "SUPABASE_ANON_KEY=<key>" >> .env

# Source environment
source .env
```

## Implementation Notes
1. Replace plaintext passwords with bcrypt hashing
2. Use Telegram ID as primary identifier for auto-authentication
3. Remove loginIDs.json dependency
4. Add proper error handling for database operations
5. Implement session management with Supabase