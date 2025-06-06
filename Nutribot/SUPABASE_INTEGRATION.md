# Supabase Integration for Nutribot

## Overview
Nutribot now uses Supabase as its database backend instead of local JSON files. This provides:
- Secure authentication with bcrypt password hashing
- Auto-authentication using Telegram ID
- Persistent data storage
- Multi-device access
- Scalable infrastructure

## Auto-Authentication Flow

### For New Users:
1. User sends `/start` command
2. Bot checks if Telegram ID exists in database
3. If not found, shows Register/Login options
4. User registers with username/password
5. Bot stores Telegram ID with user account

### For Existing Users:
1. User sends `/start` command
2. Bot checks Telegram ID in database
3. If found, auto-authenticates user
4. Shows main menu or profile completion if needed
5. No password required!

## Database Schema

The `users` table contains:
- `telegram_id`: Links to Telegram user for auto-auth
- `username`: Unique username
- `password_hash`: Bcrypt hashed password
- `plant_species`: Selected plant type
- `tank_volume`: Compost tank volume (litres)
- `soil_volume`: Soil volume (litres)
- `total_food_waste_kg`: Running total for CO2 tracking

## Migration from JSON

If you have existing users in `loginIDs.json`:

```bash
cd Nutribot
python migrate_to_supabase.py
```

This will:
1. Read existing users from JSON
2. Create accounts in Supabase
3. Preserve all user data
4. Users must `/start` once to link their Telegram ID

## Environment Setup

1. Create `.env` file in Nutribot folder:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
```

2. Install dependencies:
```bash
pip install supabase bcrypt python-dotenv
```

## Security Features

- Passwords are hashed with bcrypt
- No plaintext passwords stored
- Telegram ID provides secure auto-auth
- Database access via secure API keys
- Row-level security can be enabled

## Benefits

1. **User Experience**
   - One-time login per device
   - Auto-authentication on return
   - Secure password storage

2. **Data Persistence**
   - Cloud-based storage
   - No local file corruption
   - Automatic backups

3. **Scalability**
   - Supports unlimited users
   - Fast queries
   - Real-time updates possible

## Troubleshooting

- If auto-auth fails, users can still login with username/password
- Check `.env` file has correct credentials
- Ensure Supabase project is active
- Check internet connectivity