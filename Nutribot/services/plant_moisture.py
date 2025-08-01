import random
import numpy as np
import pandas as pd
import joblib
import os
from typing import Dict, List
from datetime import datetime, timedelta
from services.database import db
import logging

logger = logging.getLogger(__name__)

class PlantMoistureProjection:
    """Service to handle plant moisture projection and watering recommendations"""
    
    def __init__(self):
        self.ml_data = None
        self.load_ml_data()
    
    def load_ml_data(self):
        """Load the ML moisture data for pattern analysis"""
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'Marissa', 'plant_moist_model.pkl')
            self.ml_data = joblib.load(model_path)
            logger.info(f"Loaded ML data with {len(self.ml_data)} records")
        except Exception as e:
            logger.error(f"Error loading ML data: {e}")
            self.ml_data = None
    
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
        Generate moisture projection for the next 30 days using ML data patterns
        """
        # Log the current moisture reading
        try:
            db.create_plant_moisture_log(telegram_id, current_moisture)
        except Exception as e:
            logger.error(f"Failed to log moisture data: {e}")
        
        projections = []
        current_date = datetime.now()
        
        # Generate 30-day projection
        for day in range(30):
            projection_date = current_date + timedelta(days=day)
            
            if day == 0:
                projected_moisture = current_moisture
            else:
                # Use ML data patterns to predict moisture decline
                projected_moisture = self._predict_moisture_for_day(current_moisture, day)
            
            # Determine watering recommendation based on 40% threshold
            if projected_moisture < 20:
                recommendation = "🚨 Critical - Water immediately"
                status = "critical"
            elif projected_moisture < 40:
                recommendation = "⚠️ Low - Water soon"
                status = "low"
            elif projected_moisture < 60:
                recommendation = "📊 Moderate - Monitor"
                status = "moderate"
            else:
                recommendation = "✅ Good - No action needed"
                status = "good"
            
            projections.append({
                "date": projection_date.strftime("%Y-%m-%d"),
                "day_name": projection_date.strftime("%A"),
                "moisture_percentage": round(projected_moisture, 1),
                "recommendation": recommendation,
                "status": status
            })
        
        return {
            "current_moisture": current_moisture,
            "projections": projections,
            "overall_recommendation": self._get_overall_recommendation(projections),
            "next_watering_day": self._get_next_watering_day(projections),
            "watering_alerts": self._get_watering_alerts(projections)
        }
    
    def _predict_moisture_for_day(self, initial_moisture: float, day: int) -> float:
        """
        Predict moisture level for a specific day using ML data patterns
        """
        if self.ml_data is None or len(self.ml_data) == 0:
            # Fallback to simple decay model
            daily_loss = random.uniform(2, 6)
            return max(0, initial_moisture - (daily_loss * day))
        
        try:
            # Analyze patterns from ML data
            moisture_data = self.ml_data['Soil Moisture'].dropna()
            predicted_data = self.ml_data['Predicted Soil Moisture'].dropna()
            
            if len(moisture_data) > 0 and len(predicted_data) > 0:
                # Calculate average daily decline rate from ML data
                avg_decline_rate = np.mean(np.diff(moisture_data.values)) if len(moisture_data) > 1 else -3.5
                
                # Apply slight randomness for realistic variation
                daily_variation = random.uniform(-1, 1)
                predicted_moisture = initial_moisture + (avg_decline_rate * day) + daily_variation
                
                return max(0, min(100, predicted_moisture))
            else:
                # Fallback if no valid data
                daily_loss = 3.5  # Average daily loss
                return max(0, initial_moisture - (daily_loss * day))
                
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            # Fallback to simple model
            daily_loss = 3.5
            return max(0, initial_moisture - (daily_loss * day))
    
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