import os
import logging
from supabase import create_client, Client
from typing import Optional, Dict, Any
import bcrypt
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_ANON_KEY
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(url, key)
    
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase.table(Config.DATABASE_TABLE).select("*").eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by telegram ID {telegram_id}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase.table(Config.DATABASE_TABLE).select("*").eq('username', username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def create_user(self, telegram_id: int, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            hashed_password = self.hash_password(password)
            response = self.supabase.table(Config.DATABASE_TABLE).insert({
                'telegram_id': telegram_id,
                'username': username,
                'password_hash': hashed_password
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None
    
    def update_user_profile(self, telegram_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table(Config.DATABASE_TABLE).update(update_data).eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user profile for telegram_id {telegram_id}: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            user = self.get_user_by_username(username)
            if user and self.verify_password(password, user['password_hash']):
                return user
            return None
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None
    
    def is_profile_complete(self, telegram_id: int) -> bool:
        user = self.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
        return all([
            user.get('plant_species'),
            user.get('tank_volume') is not None,
            user.get('soil_volume') is not None
        ])

db = DatabaseService()