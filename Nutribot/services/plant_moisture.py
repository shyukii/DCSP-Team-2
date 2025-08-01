import random
import numpy as np
import pandas as pd
import pickle
import os
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from services.database import db
import logging

logger = logging.getLogger(__name__)

class PlantMoistureProjection:
    """Service to handle plant moisture projection and watering recommendations"""
    
    def __init__(self):
        self.xgb_model = None
        self.feature_names = None
        self.load_lagged_model()
    
    def load_lagged_model(self):
        """Load the lagged XGBoost model and feature names"""
        try:
            # Load the complete model package from pickle file
            model_path = os.path.join(os.path.dirname(__file__), 'data', 'moisture_prediction_model.pkl')
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Extract model and features from the loaded data
            if isinstance(model_data, dict):
                # If it's a dictionary, extract model and features
                self.xgb_model = model_data.get('model')
                self.feature_names = model_data.get('features') or model_data.get('feature_names')
            elif hasattr(model_data, 'feature_names_in_'):
                # If it's a model object with embedded features
                self.xgb_model = model_data
                self.feature_names = list(model_data.feature_names_in_)
            else:
                # If it's just the model
                self.xgb_model = model_data
                # Try to extract features from the model
                if hasattr(self.xgb_model, 'feature_names_in_'):
                    self.feature_names = list(self.xgb_model.feature_names_in_)
                elif hasattr(self.xgb_model, 'get_booster'):
                    try:
                        booster = self.xgb_model.get_booster()
                        if hasattr(booster, 'feature_names'):
                            self.feature_names = booster.feature_names
                    except:
                        self.feature_names = None
                else:
                    self.feature_names = None
            
            if self.xgb_model is None:
                raise ValueError("Could not extract model from pickle file")
            
            logger.info(f"Loaded lagged XGBoost model with features: {self.feature_names}")
            
        except Exception as e:
            logger.error(f"Error loading lagged model: {e}")
            self.xgb_model = None
            self.feature_names = None
    
    
    def validate_moisture_percentage(self, moisture_input: str) -> tuple[bool, float]:
        """
        Validate moisture percentage input
        Returns: (is_valid, moisture_value)
        """
        try:
            moisture = float(moisture_input.strip().replace('%', ''))
            if 0 <= moisture <= 100:
                return True, moisture
            else:
                return False, 0.0
        except ValueError:
            return False, 0.0
    
    def generate_moisture_projection(self, current_moisture: float, telegram_id: int) -> Dict:
        """
        Generate moisture projection for the next 30 days using lagged XGBoost model
        """
        # Log the current moisture reading
        try:
            db.create_plant_moisture_log(telegram_id, current_moisture)
        except Exception as e:
            logger.error(f"Failed to log moisture data: {e}")
        
        projections = []
        current_date = datetime.now()
        
        # Try to use lagged XGBoost model first
        if self.xgb_model is not None and self.feature_names is not None:
            logger.info("Using lagged XGBoost model for predictions")
            raw_predictions = self.predict_next_30_days(telegram_id, current_moisture)
            
            # Add today's reading as day 0
            projections.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": current_date.strftime("%A"),
                "moisture_percentage": round(current_moisture, 1),
                "recommendation": self._get_status_and_recommendation(current_moisture)[1],
                "status": self._get_status_and_recommendation(current_moisture)[0]
            })
            
            # Transform XGBoost predictions to existing format
            for pred in raw_predictions:
                pred_date = datetime.strptime(pred['date'], '%Y-%m-%d')
                status, recommendation = self._get_status_and_recommendation(pred['moisture'])
                
                projections.append({
                    "date": pred['date'],
                    "day_name": pred_date.strftime("%A"),
                    "moisture_percentage": pred['moisture'],
                    "recommendation": recommendation,
                    "status": status
                })
        
        else:
            # XGBoost model failed to load - return error
            logger.error("XGBoost model not available - cannot generate predictions")
            raise ValueError("Moisture prediction model not available")
        
        return {
            "current_moisture": current_moisture,
            "projections": projections,
            "overall_recommendation": self._get_overall_recommendation(projections),
            "next_watering_day": self._get_next_watering_day(projections),
            "watering_alerts": self._get_watering_alerts(projections)
        }
    
    
    def _get_watering_alerts(self, projections: List[Dict]) -> List[Dict]:
        """Generate specific watering alerts when moisture drops below 40%"""
        alerts = []
        
        for projection in projections:
            if projection["moisture_percentage"] < 40 and projection["status"] in ["critical", "low"]:
                alerts.append({
                    "date": projection["date"],
                    "day_name": projection["day_name"],
                    "moisture_level": projection["moisture_percentage"],
                    "urgency": projection["status"],
                    "message": f"🚨 Water needed on {projection['day_name']} - Moisture will be {projection['moisture_percentage']}%"
                })
        
        return alerts[:5]  # Return first 5 alerts to avoid spam
    
    def _get_overall_recommendation(self, projections: List[Dict]) -> str:
        """Generate overall watering recommendation based on projections"""
        critical_days = sum(1 for p in projections if p["status"] == "critical")
        low_days = sum(1 for p in projections if p["status"] == "low")
        
        if critical_days > 0:
            return "🚨 **Immediate Action Required**: Your plant will need water within the next few days."
        elif low_days > 2:
            return "⚠️ **Plan Ahead**: Schedule watering sessions to maintain healthy moisture levels."
        else:
            return "✅ **All Good**: Your plant's moisture levels look healthy for the week ahead."
    
    def _get_next_watering_day(self, projections: List[Dict]) -> str:
        """Determine the recommended next watering day"""
        for projection in projections:
            if projection["status"] in ["critical", "low"]:
                return f"Next watering recommended: **{projection['day_name']}** ({projection['date']})"
        
        return "No immediate watering needed this week"
    
    def get_moisture_tips(self, current_moisture: float) -> str:
        """Get tips based on current moisture level"""
        if current_moisture < 20:
            return (
                "🚨 **Critical Moisture Level**\n"
                "• Water immediately with room temperature water\n"
                "• Check drainage - soil should be moist but not waterlogged\n"
                "• Monitor daily until moisture improves"
            )
        elif current_moisture < 40:
            return (
                "⚠️ **Low Moisture Level**\n"
                "• Plan to water within 1-2 days\n"
                "• Check soil with finger test - top inch should be slightly moist\n"
                "• Consider humidity levels in your environment"
            )
        elif current_moisture < 60:
            return (
                "📊 **Moderate Moisture Level**\n"
                "• Monitor every 2-3 days\n"
                "• Water when top layer of soil feels dry\n"
                "• Maintain consistent watering schedule"
            )
        else:
            return (
                "✅ **Good Moisture Level**\n"
                "• Your plant is well-hydrated\n"
                "• Continue current watering routine\n"
                "• Avoid overwatering - check soil before next water"
            )
    
    def create_features(self, moisture_data: pd.DataFrame, lag_days: int = 3) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create lagged features from historical moisture data
        
        Args:
            moisture_data: DataFrame with columns ['date', 'moisture', 'days_since_water']
            lag_days: Number of lag days to create
        
        Returns:
            tuple: (X_features, y_target) ready for model prediction
        """
        if len(moisture_data) < lag_days + 1:
            raise ValueError(f"Need at least {lag_days + 1} days of data for {lag_days} lags")
        
        # Sort by date to ensure proper ordering
        moisture_data = moisture_data.sort_values('date').reset_index(drop=True)
        
        features_list = []
        targets = []
        
        for i in range(lag_days, len(moisture_data)):
            # Create lagged features (lag_1, lag_2, lag_3)
            lags = [moisture_data.iloc[i-j]['moisture'] for j in range(1, lag_days + 1)]
            
            # Add other features (days_since_water, etc.)
            other_features = [moisture_data.iloc[i]['days_since_water']]
            
            # Combine all features
            row_features = lags + other_features
            features_list.append(row_features)
            targets.append(moisture_data.iloc[i]['moisture'])
        
        # Use feature names if available, otherwise create generic names
        if self.feature_names:
            columns = self.feature_names
        else:
            columns = [f'lag_{i+1}' for i in range(lag_days)] + ['days_since_water']
        
        X = pd.DataFrame(features_list, columns=columns)
        y = pd.Series(targets)
        
        return X, y
    
    def _get_historical_moisture_data(self, telegram_id: int, days: int = 4) -> pd.DataFrame:
        """
        Retrieve historical moisture readings from database
        
        Returns DataFrame with columns: ['date', 'moisture', 'days_since_water']
        """
        try:
            # Get moisture logs from database
            logs = db.get_user_plant_moisture_logs(telegram_id, limit=days)
            
            if not logs:
                return pd.DataFrame()
            
            # Convert to DataFrame with required structure
            data = []
            for log in logs:
                data.append({
                    'date': log['created_at'] if isinstance(log['created_at'], datetime) else datetime.fromisoformat(log['created_at']),
                    'moisture': log['plant_moisture'],
                    'days_since_water': self._calculate_days_since_water_for_date(telegram_id, log['created_at'])
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error retrieving historical data: {e}")
            return pd.DataFrame()
    
    def _calculate_days_since_water(self, telegram_id: int) -> int:
        """Calculate days since last watering event"""
        try:
            # For now, use a simple estimation based on moisture logs
            # In a full implementation, you'd track actual watering events
            logs = db.get_user_plant_moisture_logs(telegram_id, limit=5)
            if logs and len(logs) > 1:
                # Calculate based on time since last moisture reading
                last_log = logs[0]
                last_date = last_log['created_at'] if isinstance(last_log['created_at'], datetime) else datetime.fromisoformat(last_log['created_at'])
                days_diff = (datetime.now() - last_date).days
                return max(1, days_diff)  # At least 1 day
            return 1  # Default assumption
        except Exception as e:
            logger.error(f"Error calculating days since water: {e}")
            return 1
    
    def _calculate_days_since_water_for_date(self, telegram_id: int, target_date) -> int:
        """Calculate days since water for a specific historical date"""
        # For historical data, make reasonable assumptions
        # This would be more accurate with actual watering event tracking
        # Using telegram_id and target_date for future implementation
        _ = telegram_id, target_date  # Acknowledge parameters for future use
        return random.randint(1, 5)  # Random reasonable value for now
    
    def predict_next_30_days(self, telegram_id: int, current_moisture: float) -> List[Dict]:
        """
        Generate 30-day moisture predictions using lagged XGBoost model
        """
        try:
            # Get historical data (last 4 days minimum)
            historical_data = self._get_historical_moisture_data(telegram_id, days=4)
            
            if len(historical_data) < 4:
                logger.warning(f"Insufficient historical data ({len(historical_data)} days), using fallback")
                return self._fallback_predictions(current_moisture)
            
            # Add current reading to historical data
            today_data = {
                'date': datetime.now(),
                'moisture': current_moisture,
                'days_since_water': self._calculate_days_since_water(telegram_id)
            }
            
            # Combine historical + current data
            full_data = pd.concat([historical_data, pd.DataFrame([today_data])], ignore_index=True)
            
            # Create features for prediction
            X_features, _ = self.create_features(full_data, lag_days=3)
            current_features = X_features.iloc[-1].values.copy()
            
            # Generate 30-day rolling predictions
            predictions = []
            
            for day in range(30):
                # Make prediction for this day
                pred = self.xgb_model.predict(current_features.reshape(1, -1))[0]
                pred = max(0, min(100, pred))  # Clamp to valid range
                
                predictions.append({
                    'day': day + 1,
                    'moisture': round(pred, 1),
                    'date': (datetime.now() + timedelta(days=day + 1)).strftime('%Y-%m-%d')
                })
                
                # Update features for next prediction
                # Shift moisture lags: lag_3 = lag_2, lag_2 = lag_1, lag_1 = current_pred
                if len(current_features) >= 3:
                    current_features[2] = current_features[1]  # lag_3 = lag_2  
                    current_features[1] = current_features[0]  # lag_2 = lag_1
                    current_features[0] = pred                 # lag_1 = current prediction
                
                # Increment days since water (assuming no watering)
                current_features[-1] += 1
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in lagged prediction: {e}")
            return self._fallback_predictions(current_moisture)
    
    def _fallback_predictions(self, current_moisture: float) -> List[Dict]:
        """Generate fallback predictions using simple decay model"""
        predictions = []
        moisture = current_moisture
        
        for day in range(30):
            # Simple decay model
            daily_loss = random.uniform(2.5, 4.5)
            moisture = max(0, moisture - daily_loss)
            
            predictions.append({
                'day': day + 1,
                'moisture': round(moisture, 1),
                'date': (datetime.now() + timedelta(days=day + 1)).strftime('%Y-%m-%d')
            })
        
        return predictions
    
    def _get_status_and_recommendation(self, moisture: float) -> Tuple[str, str]:
        """Get status and recommendation for a moisture level"""
        if moisture < 20:
            return "critical", "🚨 Critical - Water immediately"
        elif moisture < 40:
            return "low", "⚠️ Low - Water soon"
        elif moisture < 60:
            return "moderate", "📊 Moderate - Monitor"
        else:
            return "good", "✅ Good - No action needed"