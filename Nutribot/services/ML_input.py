"""
ML-Based Compost Feed Recommendation System
Adapted from Dahlia DSCP Model Final.ipynb for production use in Telegram chatbot.
"""

import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MLCompostRecommendation:
    """
    ML-powered compost recommendation system based on historical sensor data.
    Provides crop-specific feeding recommendations with time predictions.
    """
    
    def __init__(self):
        """Initialise the ML recommendation system."""
        self.df = None
        self.crop_requirements = {
            "Leafy Greens": {
                "moisture": 57.75,
                "cn_min": 10,
                "cn_max": 15
            },
            "Fruit Veggies": {
                "moisture": 41.3, 
                "cn_min": 15,
                "cn_max": 20
            },
            "Root Vegetables": {
                "moisture": 40.76,
                "cn_min": 15,
                "cn_max": 25
            },
            "Herbs": {
                "moisture": 48.28,  
                "cn_min": 12,
                "cn_max": 20
            },
            "Flowering Plants": {
                "moisture": 40.76,  
                "cn_min": 15,
                "cn_max": 25
            },
            "Woody Plants": {
                "moisture": 39.67,  
                "cn_min": 20,
                "cn_max": 30
            }
        }
        self._load_data()
    
    def _load_data(self) -> None:
        """Load and preprocess the training dataset."""
        try:
            # Get the path to the CSV file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(current_dir, "data", "feeding_input_df.csv")
            
            if not os.path.exists(csv_path):
                logger.error(f"CSV file not found at {csv_path}")
                raise FileNotFoundError(f"Training data file not found: {csv_path}")
            
            # Load the dataset
            self.df = pd.read_csv(csv_path)
            
            # Preprocess the data
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['date_of_feed'] = pd.to_datetime(self.df['date_of_feed'])
            
            # Convert amounts from kg to grams for consistency
            self.df['browns_amount'] = self.df['browns_amount'] * 1000 
            self.df['greens_amount'] = self.df['greens_amount'] * 1000
            
            # Process NPK ratios
            self._process_npk_ratios()
            
            # Process C:N ratios
            self._process_cn_ratios()
            
            logger.info(f"Successfully loaded {len(self.df)} records from training data")
            
        except Exception as e:
            logger.error(f"Error loading ML training data: {str(e)}")
            raise
    
    def _process_npk_ratios(self) -> None:
        """Process NPK ratios and classify plant readiness."""
        # Clean and split NPK values
        self.df[['N', 'P', 'K']] = self.df['NPK Ratio'].str.split(':', expand=True).astype(float)
        
        # Apply NPK classification
        self.df['NPK - Plant Readiness'] = self.df.apply(
            lambda row: self._classify_adjusted_npk(row['N'], row['P'], row['K']), 
            axis=1
        )
    
    def _classify_adjusted_npk(self, n: float, p: float, k: float) -> str:
        """Classify NPK ratios for plant readiness with ±3 threshold flexibility."""
        if n == 0 or p == 0 or k == 0:
            return 'Unknown'
        
        # Simple ratio normalisation
        p_ratio = round(p / n, 1)
        k_ratio = round(k / n, 1)

        # Adjusted range thresholds (±3 flexibility)
        if 1.4 <= p_ratio <= 2.6 and 1.4 <= k_ratio <= 2.6:
            return 'Optimal (Long Bean)'
        elif 0.9 <= p_ratio <= 2.1 and 0.9 <= k_ratio <= 2.1:
            return 'Balanced (Lady Finger)'
        elif 0.4 <= p_ratio <= 1.6 and 0.4 <= k_ratio <= 1.6:
            return 'Balanced (General)'
        elif 0.1 <= p_ratio <= 1.1 and 0.1 <= k_ratio <= 1.1:
            return 'High Nitrogen (Spinach Leaning)'
        else:
            return 'Unbalanced'
    
    def _process_cn_ratios(self) -> None:
        """Process C:N ratios and classify for different plant types."""
        self.df['C_N_Status'] = self.df['C_N_Ratio'].apply(self._classify_cn_ratio)
    
    def _classify_cn_ratio(self, cn_ratio_str: str) -> str:
        """Classify C:N ratio based on ranges for different plant types."""
        try:
            cn_value = int(str(cn_ratio_str).split(':')[0])
        except:
            return 'Unknown'
        
        ranges = {
            'Leafy Greens': (10, 15),
            'Fruit Veggies': (15, 20),
            'Root Vegetables': (15, 25),
            'Herbs': (12, 20),
            'Flowering Plants': (15, 25),
            'Woody Plants': (20, 30)
        }
        
        status = []
        for plant_type, (min_val, max_val) in ranges.items():
            if min_val <= cn_value <= max_val:
                status.append(plant_type)
        
        if not status:
            return 'Unbalanced'
        elif len(status) == 1:
            return f'Optimal for {status[0]}'
        else:
            return f'Optimal for multiple: {", ".join(status)}'
    
    def _get_cn_value(self, cn_ratio_str: str) -> Optional[int]:
        """Extract the numeric value from C:N ratio string."""
        try:
            return int(str(cn_ratio_str).split(':')[0])
        except:
            return None
    
    def _is_optimal_for_crop(self, cn_ratio_str: str, target_crop: str) -> bool:
        """Check if C:N ratio is optimal for the target crop."""
        cn_value = self._get_cn_value(cn_ratio_str)
        if cn_value is None:
            return False
        requirements = self.crop_requirements.get(target_crop)
        if not requirements:
            return False
        return requirements['cn_min'] <= cn_value <= requirements['cn_max']
    
    def get_available_crops(self) -> List[str]:
        """Get list of available crop types."""
        return list(self.crop_requirements.keys())
    
    def validate_crop_type(self, crop_type: str) -> bool:
        """Validate if the provided crop type is supported."""
        return crop_type in self.crop_requirements
    
    def generate_ml_recommendation(self, greens_input_grams: float, target_crop: str) -> Dict:
        """
        Generate ML-based compost feed recommendation.
        
        Args:
            greens_input_grams (float): Amount of greens in grams
            target_crop (str): Target crop type
            
        Returns:
            Dict: Recommendation results
        """
        try:
            if not self.validate_crop_type(target_crop):
                return {
                    "success": False,
                    "message": f"Invalid crop type: {target_crop}. Choose from: {', '.join(self.get_available_crops())}"
                }
            
            if greens_input_grams <= 0:
                return {
                    "success": False,
                    "message": "Greens amount must be positive"
                }
            
            target_moisture_pct = self.crop_requirements[target_crop]['moisture']
            
            # Find feeds that resulted in optimal C:N for this crop
            optimal_feeds = []
            
            # Group by device and find sequences of feed -> optimal state
            for device, device_data in self.df.groupby('devicename'):
                # Sort by date
                device_data = device_data.sort_values('date')
                
                # Find all optimal events for this crop
                optimal_events = device_data[
                    device_data['C_N_Status'].notna() & 
                    device_data['C_N_Status'].str.contains("Optimal", case=False) &
                    device_data.apply(lambda row: self._is_optimal_for_crop(row['C_N_Ratio'], target_crop), axis=1)
                ].sort_values('date')
                
                for _, optimal_row in optimal_events.iterrows():
                    # Find the feed before this optimal event
                    feed_before = device_data[
                        (device_data['date_of_feed'].notna()) &
                        (device_data['date_of_feed'] <= optimal_row['date']) &
                        (device_data['greens_amount'].notna()) &
                        (device_data['browns_amount'].notna())
                    ].sort_values('date_of_feed', ascending=False)
                    
                    if not feed_before.empty:
                        feed_row = feed_before.iloc[0]
                        days_to_optimal = (optimal_row['date'] - feed_row['date_of_feed']).days
                        optimal_feeds.append({
                            'feed': feed_row,
                            'optimal': optimal_row,
                            'days_to_optimal': days_to_optimal,
                            'device': device
                        })
            
            if not optimal_feeds:
                return {
                    "success": False,
                    "message": f"No optimal compost recipes found for {target_crop}. Please try a different crop type."
                }

            # Select the feed that took the median time to reach optimal
            optimal_feeds.sort(key=lambda x: x['days_to_optimal'])
            selected = optimal_feeds[len(optimal_feeds) // 2]  # Median
            
            feed_row = selected['feed']
            optimal_row = selected['optimal']
            
            # Calculate browns amount based on historical ratio
            brown_per_green = feed_row['browns_amount'] / feed_row['greens_amount']
            browns_amount = greens_input_grams * brown_per_green
            
            # Calculate water needed to reach target moisture
            water_target = (target_moisture_pct / 100) * (greens_input_grams + browns_amount) / (1 - target_moisture_pct / 100)
            
            return {
                "success": True,
                "greens_g": round(greens_input_grams, 2),
                "browns_g": round(browns_amount, 2),
                "water_g": round(water_target, 2),
                "target_crop": target_crop,
                "resulting_cn_ratio": optimal_row['C_N_Ratio'],
                "days_to_optimal": selected['days_to_optimal'],
                "based_on_device": selected['device'],
                "feed_date": feed_row['date_of_feed'].strftime('%Y-%m-%d'),
                "optimal_date": optimal_row['date'].strftime('%Y-%m-%d'),
                "moisture_target_pct": target_moisture_pct,
                "confidence_note": f"Based on {len(optimal_feeds)} historical optimal outcomes"
            }
            
        except Exception as e:
            logger.error(f"Error generating ML recommendation: {str(e)}")
            return {
                "success": False,
                "message": f"Error calculating recommendation: {str(e)}"
            }
    
    def get_formatted_recommendation(self, greens_input_grams: float, target_crop: str) -> str:
        """
        Get human-readable ML recommendation for Telegram bot.
        
        Args:
            greens_input_grams (float): Amount of greens in grams
            target_crop (str): Target crop type
            
        Returns:
            str: Formatted recommendation text
        """
        result = self.generate_ml_recommendation(greens_input_grams, target_crop)
        
        if not result["success"]:
            return f"❌ {result['message']}"
        
        # Convert grams to more readable units
        greens_kg = result['greens_g'] / 1000
        browns_kg = result['browns_g'] / 1000
        water_l = result['water_g'] / 1000
        
        recommendation = f"""🧠 **ML-Powered Feed Recommendation**

**For {greens_kg:.1f}kg of greens → {result['target_crop']}:**

🥬 **Greens**: {greens_kg:.1f}kg (your input)
🍂 **Browns**: {browns_kg:.1f}kg 
💧 **Water**: {water_l:.1f}L
🎯 **Target Moisture**: {result['moisture_target_pct']:.1f}%

⏱️ **Expected Results**:
• C:N Ratio: {result['resulting_cn_ratio']}
• Days to optimal: ~{result['days_to_optimal']} days

📊 **ML Insights**:
• {result['confidence_note']}
• Based on device: {result['based_on_device']}
• Historical feed: {result['feed_date']}

💡 **Pro Tips**:
• Mix materials thoroughly
• Turn compost weekly for best aeration
• Monitor moisture - adjust if too dry/wet
• This recommendation is tailored for {result['target_crop'].lower()}"""

        return recommendation


# Convenience functions for backward compatibility
def get_ml_recommendation(greens_input_grams: float, target_crop: str) -> Dict:
    """
    Convenience function to get ML recommendation.
    
    Args:
        greens_input_grams (float): Amount of greens in grams
        target_crop (str): Target crop type
        
    Returns:
        Dict: Recommendation results
    """
    ml_system = MLCompostRecommendation()
    return ml_system.generate_ml_recommendation(greens_input_grams, target_crop)


def get_formatted_ml_recommendation(greens_input_grams: float, target_crop: str) -> str:
    """
    Convenience function to get formatted ML recommendation for chatbot.
    
    Args:
        greens_input_grams (float): Amount of greens in grams
        target_crop (str): Target crop type
        
    Returns:
        str: Formatted recommendation text
    """
    ml_system = MLCompostRecommendation()
    return ml_system.get_formatted_recommendation(greens_input_grams, target_crop)


def get_available_crop_types() -> List[str]:
    """Get list of available crop types."""
    ml_system = MLCompostRecommendation()
    return ml_system.get_available_crops()


# Main execution for testing
if __name__ == "__main__":
    # Test the ML recommendation system
    ml_system = MLCompostRecommendation()
    
    print("Available crop types:", ml_system.get_available_crops())
    
    # Test with herbs and 30g of greens (like in the original notebook)
    test_result = ml_system.get_formatted_recommendation(30.0, "Herbs")
    print("\nTest Recommendation:")
    print(test_result)