import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import bcrypt
from datetime import datetime

class DatabaseService:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL", "https://nimflhaujdwzwirodude.supabase.co")
        key = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbWZsaGF1amR3endpcm9kdWRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNjAzMjMsImV4cCI6MjA2NDczNjMyM30.hMjh7o7vAbxR6oqaL0oxu4Jyc8lAXs4ziS46LFQ4WhI")
        self.supabase: Client = create_client(url, key)
    
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase.table('users').select("*").eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by telegram ID: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase.table('users').select("*").eq('username', username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    async def create_user(self, telegram_id: int, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            hashed_password = self.hash_password(password)
            response = self.supabase.table('users').insert({
                'telegram_id': telegram_id,
                'username': username,
                'password_hash': hashed_password
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    async def update_user_profile(self, telegram_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('users').update(update_data).eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            user = await self.get_user_by_username(username)
            if user and self.verify_password(password, user['password_hash']):
                return user
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    async def is_profile_complete(self, telegram_id: int) -> bool:
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
        return all([
            user.get('plant_species'),
            user.get('tank_volume') is not None,
            user.get('soil_volume') is not None
        ])

db = DatabaseService()