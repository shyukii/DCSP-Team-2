"""
Compost Calculator for Optimal Feed Input

This module provides functionality to calculate optimal browns and water ratios
based on the user's greens input for composting.

The optimal C:N ratio for composting is typically 30:1 (carbon to nitrogen).
- Greens (nitrogen-rich): 12-25:1 C:N ratio
- Browns (carbon-rich): 150-500:1 C:N ratio

Water content should be 50-60% of the total compost volume.
"""

import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class FeedCalculator:
    """
    A calculator for optimal compost ratios based on greens input.
    """
    
    # Average C:N ratios for different materials
    GREENS_CN_RATIO = 20  # Average C:N ratio for greens (nitrogen-rich materials)
    BROWNS_CN_RATIO = 300  # Average C:N ratio for browns (carbon-rich materials)
    TARGET_CN_RATIO = 30  # Optimal C:N ratio for composting
    
    # Water content parameters
    TARGET_MOISTURE = 0.55  # 55% moisture content (optimal range 50-60%)
    GREENS_WATER_CONTENT = 0.8  # Greens typically contain 80% water
    BROWNS_WATER_CONTENT = 0.15  # Browns typically contain 15% water
    
    def __init__(self):
        """Initialise the FeedCalculator."""
        pass
    
    def calculate_optimal_ratios(self, greens_weight_kg: float) -> Dict[str, float]:
        """
        Calculate optimal browns and water ratios based on greens input.
        
        Args:
            greens_weight_kg (float): Weight of greens in kilograms
            
        Returns:
            Dict[str, float]: Dictionary containing optimal ratios
                - browns_kg: Weight of browns needed in kg
                - water_litres: Additional water needed in litres
                - total_volume_litres: Estimated total compost volume
                - cn_ratio: Calculated C:N ratio
        """
        if greens_weight_kg <= 0:
            raise ValueError("Greens weight must be positive")
        
        # Calculate browns needed for optimal C:N ratio
        numerator = (self.TARGET_CN_RATIO - self.GREENS_CN_RATIO) * greens_weight_kg
        denominator = self.BROWNS_CN_RATIO - self.TARGET_CN_RATIO
        browns_weight_kg = numerator / denominator
        
        if browns_weight_kg < 0:
            browns_weight_kg = 0
            logger.warning(f"Calculated negative browns weight, setting to 0")
        
        # Calculate total dry weight
        total_dry_weight = greens_weight_kg + browns_weight_kg
        
        # Calculate water content in materials
        water_from_greens = greens_weight_kg * self.GREENS_WATER_CONTENT
        water_from_browns = browns_weight_kg * self.BROWNS_WATER_CONTENT
        existing_water = water_from_greens + water_from_browns
        
        # Calculate total weight needed for target moisture
        # target_moisture = existing_water + additional_water / total_weight
        # Solving for total_weight: total_weight = (existing_water + additional_water) / target_moisture
        # And total_weight = total_dry_weight + existing_water + additional_water
        # Therefore: additional_water = (target_moisture * total_dry_weight) / (1 - target_moisture) - existing_water
        
        target_total_water = (self.TARGET_MOISTURE * total_dry_weight) / (1 - self.TARGET_MOISTURE)
        additional_water_litres = max(0, target_total_water - existing_water)
        
        # Estimate total volume (assuming density of ~0.4 kg/L for compost mix)
        total_weight = total_dry_weight + existing_water + additional_water_litres
        total_volume_litres = total_weight / 0.4
        
        # Calculate actual C:N ratio
        carbon_from_greens = greens_weight_kg * self.GREENS_CN_RATIO
        carbon_from_browns = browns_weight_kg * self.BROWNS_CN_RATIO
        nitrogen_from_greens = greens_weight_kg  # greens are our nitrogen source
        nitrogen_from_browns = browns_weight_kg / self.BROWNS_CN_RATIO
        
        total_carbon = carbon_from_greens + carbon_from_browns
        total_nitrogen = nitrogen_from_greens + nitrogen_from_browns
        actual_cn_ratio = total_carbon / total_nitrogen if total_nitrogen > 0 else 0
        
        return {
            'browns_kg': round(browns_weight_kg, 2),
            'water_litres': round(additional_water_litres, 2),
            'total_volume_litres': round(total_volume_litres, 1),
            'cn_ratio': round(actual_cn_ratio, 1),
            'moisture_percentage': round(self.TARGET_MOISTURE * 100, 1)
        }
    
    def get_feeding_recommendations(self, greens_weight_kg: float) -> str:
        """
        Get human-readable feeding recommendations.
        
        Args:
            greens_weight_kg (float): Weight of greens in kilograms
            
        Returns:
            str: Formatted recommendations text
        """
        try:
            ratios = self.calculate_optimal_ratios(greens_weight_kg)
            
            recommendations = f"""🥬 **Feed Calculator Results**

For {greens_weight_kg}kg of greens, you need:

🍂 **Browns**: {ratios['browns_kg']}kg
• Dry leaves, paper, cardboard
• Helps achieve optimal C:N ratio of ~{ratios['cn_ratio']}:1

💧 **Additional Water**: {ratios['water_litres']} litres
• Target moisture: {ratios['moisture_percentage']}%

📦 **Estimated Volume**: ~{ratios['total_volume_litres']} litres

💡 **Tips**:
• Mix materials thoroughly
• Turn compost weekly for best results
• Adjust water if mixture feels too dry or soggy"""
            
            return recommendations
            
        except ValueError as e:
            return f"❌ Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error in get_feeding_recommendations: {str(e)}")
            return "❌ Sorry, there was an error calculating the recommendations. Please try again."