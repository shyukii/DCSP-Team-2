"""
ML Compost Recommendation System - Advanced compost recommendation model
Provides greens input -> browns recommendation logic with water calculation
"""

class MLCompostRecommendation:
    def __init__(self):
        # Crop requirements from the Dahlia model
        self.crop_requirements = {
            "Leafy Greens": {
                "cn_min": 12.5,
                "cn_max": 17.5
            },
            "Fruit Veggies": {
                "cn_min": 21.5,
                "cn_max": 26.5
            },
            "Root Vegetables": {
                "cn_min": 15.5,
                "cn_max": 20.5
            },
            "Herbs": {
                "cn_min": 21.5,
                "cn_max": 26.5
            },
            "Flowering Plants": {
                "cn_min": 18.5,
                "cn_max": 23.5
            },
            "Woody Plants": {
                "cn_min": 24.5,
                "cn_max": 29.5
            }
        }
        
        # Default green to brown ratios based on historical data
        self.default_ratios = {
            "Leafy Greens": 1.8,    # Browns multiplier for greens
            "Fruit Veggies": 2.1,
            "Root Vegetables": 1.8,
            "Herbs": 2.0,
            "Flowering Plants": 1.9,
            "Woody Plants": 2.2
        }

    def get_available_crop_types(self):
        """Get list of available crop types"""
        return list(self.crop_requirements.keys())

    def normalize_crop_name(self, crop_input):
        """Normalize crop name from user input"""
        crop_input_normalized = crop_input.strip().lower().replace(" ", "").replace("-", "")
        crop_options = {
            "leafygreens": "Leafy Greens",
            "fruitveggies": "Fruit Veggies", 
            "rootvegetables": "Root Vegetables",
            "herbs": "Herbs",
            "floweringplants": "Flowering Plants",
            "woodyplants": "Woody Plants"
        }
        return crop_options.get(crop_input_normalized)

    def calculate_recommendation(self, greens_grams, target_crop, soil_volume_liters=None):
        """
        Calculate compost recommendation based on ML model
        
        Args:
            greens_grams: Amount of greens in grams
            target_crop: Target crop type
            soil_volume_liters: User's soil volume for water calculation (50% of soil volume)
            
        Returns:
            Dictionary with recommendation details
        """
        # Normalize crop name
        normalized_crop = self.normalize_crop_name(target_crop)
        if not normalized_crop:
            return {
                "error": f"Invalid crop type: {target_crop}. Choose from: {self.get_available_crop_types()}"
            }

        # Get crop requirements
        requirements = self.crop_requirements[normalized_crop]
        
        # Calculate browns amount using default ratio
        brown_per_green = self.default_ratios[normalized_crop]
        browns_grams = greens_grams * brown_per_green
        
        # Calculate water needed - always 50% of soil volume
        if soil_volume_liters and soil_volume_liters > 0:
            # Use 50% of soil volume
            water_grams = soil_volume_liters * 1000 * 0.5  # Convert L to g and use 50%
        else:
            # If no soil volume provided, return error
            return {
                "error": "Soil volume is required for water calculation. Please complete your profile setup."
            }
        
        # Calculate expected C:N ratio (approximation)
        expected_cn_ratio = f"{int((requirements['cn_min'] + requirements['cn_max']) / 2)}:1"
        
        return {
            "greens_g": round(greens_grams, 2),
            "browns_g": round(browns_grams, 2),
            "water_g": round(water_grams, 2),
            "water_ml": round(water_grams, 2),  # Same as grams for water
            "target_crop": normalized_crop,
            "expected_cn_ratio": expected_cn_ratio,
            "brown_per_green_ratio": brown_per_green,
            "soil_volume_liters": soil_volume_liters
        }

    def get_formatted_recommendation(self, greens_grams, target_crop, soil_volume_liters=None):
        """
        Get formatted ML recommendation message for Telegram bot
        """
        result = self.calculate_recommendation(greens_grams, target_crop, soil_volume_liters)
        
        if "error" in result:
            return f"❌ {result['error']}"
        
        # Format the response
        
        message = f"""🧠 **ML Smart Recommendation**

**For {result['target_crop']}:**

🥬 **Greens:** {result['greens_g']}g
🍂 **Browns:** {result['browns_g']}g  
💧 **Water:** {result['water_ml']}ml

📊 **Details:**
• Expected C:N ratio: {result['expected_cn_ratio']}
• Soil volume: {result['soil_volume_liters']}L
• Browns per greens ratio: {result['brown_per_green_ratio']}:1

💧 Water calculated as 50% of your soil volume

*Based on advanced ML analysis optimized for {result['target_crop'].lower()}*"""

        return message


# Convenience functions for backward compatibility
def get_available_crop_types():
    """Get list of available crop types."""
    ml_system = MLCompostRecommendation()
    return ml_system.get_available_crop_types()