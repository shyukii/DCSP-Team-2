import random
from typing import Dict, List
from datetime import datetime, timedelta

class PlantMoistureProjection:
    """Service to handle plant moisture projection and watering recommendations"""
    
    def __init__(self):
        # Placeholder for future ML model integration
        self.ml_model = None
    
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
    
    def generate_moisture_projection(self, current_moisture: float) -> Dict:
        """
        Generate moisture projection for the next 7 days
        This is a placeholder - will be replaced with ML model later
        """
        projections = []
        current_date = datetime.now()
        
        # Simulate moisture decline over time (placeholder logic)
        for day in range(7):
            projection_date = current_date + timedelta(days=day)
            
            # Simulate moisture loss (3-8% per day depending on conditions)
            daily_loss = random.uniform(3, 8)
            if day == 0:
                projected_moisture = current_moisture
            else:
                projected_moisture = max(0, projected_moisture - daily_loss)
            
            # Determine watering recommendation
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
            "next_watering_day": self._get_next_watering_day(projections)
        }
    
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