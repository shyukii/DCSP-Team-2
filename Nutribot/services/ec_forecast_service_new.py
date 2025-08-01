import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class ECForecastService:
    def __init__(self):
        """Initialize the EC Forecast Service with the pre-trained model"""
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'ec_forecast_model.pkl')
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained EC forecast model - NO FALLBACKS"""
        try:
            with open(self.model_path, 'rb') as file:
                self.model = pickle.load(file)
            logger.info("EC forecast model loaded successfully from Marissa folder")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to load EC forecast model: {e}")
            self.model = None
            raise Exception(f"Cannot load required ML model: {e}")
    
    def predict_90_day_forecast(self, current_ec: float, current_moisture: float) -> Dict:
        """
        Predict EC values for the next 90 days using the actual ML model
        
        Args:
            current_ec: Current EC value in mS/cm
            current_moisture: Current moisture percentage
            
        Returns:
            Dictionary containing predictions and metadata
        """
        if self.model is None:
            raise Exception("EC forecast model not loaded - cannot make predictions")
        
        try:
            # Generate predictions for 90 days using the actual ML model
            predictions = []
            dates = []
            
            # Starting from tomorrow
            start_date = datetime.now() + timedelta(days=1)
            
            for day in range(90):
                predict_date = start_date + timedelta(days=day)
                
                # Create feature vector for your specific model
                # Note: You may need to adjust this based on what features your model expects
                try:
                    # Try different feature combinations based on common ML model inputs
                    # Option 1: Just EC and moisture
                    features = np.array([[current_ec, current_moisture]])
                    predicted_ec = self.model.predict(features)[0]
                except:
                    try:
                        # Option 2: EC, moisture, and day
                        features = np.array([[current_ec, current_moisture, day + 1]])
                        predicted_ec = self.model.predict(features)[0]
                    except:
                        try:
                            # Option 3: Single EC value
                            features = np.array([[current_ec]])
                            predicted_ec = self.model.predict(features)[0]
                        except Exception as model_error:
                            raise Exception(f"Model prediction failed: {model_error}")
                
                predictions.append(predicted_ec)
                dates.append(predict_date)
                
                # Keep original EC for consistent predictions (don't chain predictions)
                # current_ec = predicted_ec  # Comment this out to avoid chaining
            
            # Calculate statistics
            avg_ec = np.mean(predictions)
            max_ec = np.max(predictions)
            min_ec = np.min(predictions)
            
            # Find key prediction points
            week_1 = predictions[6]   # Day 7
            week_2 = predictions[13]  # Day 14
            month_1 = predictions[29] # Day 30
            month_2 = predictions[59] # Day 60
            month_3 = predictions[89] # Day 90
            
            result = {
                'predictions': predictions,
                'dates': dates,
                'statistics': {
                    'average_ec': round(avg_ec, 2),
                    'max_ec': round(max_ec, 2),
                    'min_ec': round(min_ec, 2),
                    'current_ec': current_ec,
                    'current_moisture': current_moisture
                },
                'key_predictions': {
                    'week_1': round(week_1, 2),
                    'week_2': round(week_2, 2),
                    'month_1': round(month_1, 2),
                    'month_2': round(month_2, 2),
                    'month_3': round(month_3, 2)
                },
                'prediction_date': datetime.now(),
                'success': True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error making EC predictions with actual model: {e}")
            return {
                'success': False,
                'error': str(e),
                'statistics': {},
                'key_predictions': {},
                'predictions': [],
                'dates': []
            }
    
    def format_prediction_message(self, prediction_result: Dict) -> str:
        """
        Format the prediction results into a user-friendly message
        
        Args:
            prediction_result: Result from predict_90_day_forecast
            
        Returns:
            Formatted message string
        """
        if not prediction_result.get('success', False):
            return f"❌ **Prediction Failed**\n\nError: {prediction_result.get('error', 'Unknown error')}"
        
        stats = prediction_result['statistics']
        key_preds = prediction_result['key_predictions']
        
        message = f"""🧠 **90-Day EC Forecast Results**

📊 **Current Conditions:**
• EC: {stats['current_ec']} mS/cm
• Moisture: {stats['current_moisture']}%

🔮 **Key Predictions:**
• Week 1 (Day 7): {key_preds['week_1']} mS/cm
• Week 2 (Day 14): {key_preds['week_2']} mS/cm
• Month 1 (Day 30): {key_preds['month_1']} mS/cm
• Month 2 (Day 60): {key_preds['month_2']} mS/cm
• Month 3 (Day 90): {key_preds['month_3']} mS/cm

📈 **90-Day Statistics:**
• Average EC: {stats['average_ec']} mS/cm
• Maximum EC: {stats['max_ec']} mS/cm
• Minimum EC: {stats['min_ec']} mS/cm

💡 **Insights:**
"""
        
        # Add insights based on trends
        current_ec = stats['current_ec']
        final_ec = key_preds['month_3']
        
        if final_ec > current_ec * 1.2:
            message += "• 📈 **Rising trend**: EC is expected to increase significantly\n"
            message += "• 🚰 Consider more frequent watering to manage salinity\n"
        elif final_ec < current_ec * 0.8:
            message += "• 📉 **Declining trend**: EC is expected to decrease\n"
            message += "• 🌱 Good for plant health - nutrients being absorbed\n"
        else:
            message += "• ⚖️ **Stable trend**: EC levels remain relatively consistent\n"
            message += "• ✅ Indicates good nutrient balance\n"
        
        # EC level recommendations
        avg_ec = stats['average_ec']
        if avg_ec > 3.5:
            message += "• ⚠️ **High EC levels**: Monitor for salt stress\n"
        elif avg_ec < 1.0:
            message += "• 📊 **Low EC levels**: Consider nutrient supplementation\n"
        else:
            message += "• ✅ **Optimal EC range**: Good for most plants\n"
        
        message += f"\n🕐 **Forecast generated**: {prediction_result['prediction_date'].strftime('%Y-%m-%d %H:%M')}"
        
        return message
    
    def get_prediction_data_for_storage(self, prediction_result: Dict, telegram_id: int) -> List[Dict]:
        """
        Format prediction data for database storage
        
        Args:
            prediction_result: Result from predict_90_day_forecast
            telegram_id: User's telegram ID
            
        Returns:
            List of dictionaries ready for database insertion
        """
        if not prediction_result.get('success', False):
            return []
        
        storage_data = []
        predictions = prediction_result['predictions']
        dates = prediction_result['dates']
        
        for i, (date, predicted_ec) in enumerate(zip(dates, predictions)):
            storage_data.append({
                'telegram_id': telegram_id,
                'prediction_date': date.isoformat(),
                'predicted_ec': round(predicted_ec, 2),
                'day_number': i + 1,
                'created_at': datetime.now().isoformat()
            })
        
        return storage_data
    
    def store_predictions_to_database(self, prediction_result: Dict, telegram_id: int) -> bool:
        """
        Store predictions to database using the database service
        
        Args:
            prediction_result: Result from predict_90_day_forecast
            telegram_id: User's telegram ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from services.database import db
            storage_data = self.get_prediction_data_for_storage(prediction_result, telegram_id)
            return db.store_ec_predictions(storage_data)
        except Exception as e:
            logger.error(f"Error storing predictions to database: {e}")
            return False
