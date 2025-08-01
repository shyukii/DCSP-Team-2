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
            user.get('tank_volume') is not None,
            user.get('soil_volume') is not None
        ])
    
    def create_feeding_log(self, telegram_id: int, greens: float, browns: float, moisture_percentage: float) -> Optional[Dict[str, Any]]:
        """
        Create a new feeding log entry
        
        Args:
            telegram_id: User's telegram ID
            greens: Amount of greens added (in grams)
            browns: Amount of browns added (in grams)  
            moisture_percentage: Moisture percentage achieved after feeding
            
        Returns:
            Created feeding log entry or None if failed
        """
        try:
            # Get the user to retrieve the username
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User not found for telegram_id {telegram_id}")
                return None
            
            response = self.supabase.table('feeding_logs').insert({
                'telegram_id': telegram_id,
                'username': user['username'],  # Add username to the feeding log
                'greens': greens,
                'browns': browns,
                'moisture_percentage': moisture_percentage
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating feeding log for telegram_id {telegram_id}: {e}")
            return None
    
    def get_user_feeding_logs(self, telegram_id: int, limit: int = 10) -> list:
        """
        Get recent feeding logs for a user
        
        Args:
            telegram_id: User's telegram ID
            limit: Number of recent logs to retrieve
            
        Returns:
            List of feeding log entries
        """
        try:
            response = self.supabase.table('feeding_logs').select("*").eq('telegram_id', telegram_id).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting feeding logs for telegram_id {telegram_id}: {e}")
            return []
    
    def get_user_total_food_waste(self, telegram_id: int) -> float:
        """
        Calculate total food waste (greens + browns) for a specific user from feeding logs
        
        Args:
            telegram_id: User's telegram ID
            
        Returns:
            Total food waste in kg
        """
        try:
            response = self.supabase.table('feeding_logs').select("greens, browns").eq('telegram_id', telegram_id).execute()
            if not response.data:
                return 0.0
            
            total_grams = sum(log.get('greens', 0) + log.get('browns', 0) for log in response.data)
            return round(total_grams / 1000, 2)  # Convert grams to kg
        except Exception as e:
            logger.error(f"Error calculating total food waste for telegram_id {telegram_id}: {e}")
            return 0.0
    
    def get_all_users_total_food_waste(self) -> float:
        """
        Calculate total food waste (greens + browns) for all NutriBot users from feeding logs
        
        Returns:
            Total food waste across all users in kg
        """
        try:
            response = self.supabase.table('feeding_logs').select("greens, browns").execute()
            if not response.data:
                return 0.0
            
            total_grams = sum(log.get('greens', 0) + log.get('browns', 0) for log in response.data)
            return round(total_grams / 1000, 2)  # Convert grams to kg
        except Exception as e:
            logger.error(f"Error calculating total food waste for all users: {e}")
            return 0.0
    
    def create_plant_moisture_log(self, telegram_id: int, plant_moisture: float) -> Optional[Dict[str, Any]]:
        """
        Create a new plant moisture log entry
        
        Args:
            telegram_id: User's telegram ID
            plant_moisture: Current plant moisture percentage
            
        Returns:
            Created plant moisture log entry or None if failed
        """
        try:
            # Get the user to retrieve the username
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User not found for telegram_id {telegram_id}")
                return None
            
            response = self.supabase.table('plant').insert({
                'telegram_id': telegram_id,
                'username': user['username'],
                'plant_moisture': plant_moisture
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating plant moisture log for telegram_id {telegram_id}: {e}")
            return None
    
    def get_user_plant_moisture_logs(self, telegram_id: int, limit: int = 10) -> list:
        """
        Get recent plant moisture logs for a user
        
        Args:
            telegram_id: User's telegram ID
            limit: Number of recent logs to retrieve
            
        Returns:
            List of plant moisture log entries
        """
        try:
            response = self.supabase.table('plant').select("*").eq('telegram_id', telegram_id).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting plant moisture logs for telegram_id {telegram_id}: {e}")
            return []

db = DatabaseService()