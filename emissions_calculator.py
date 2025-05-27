############################################################################
# SIMPLIFIED CARBON EMISSIONS CALCULATOR FOR CHATBOT /C02 FUCNTION
############################################################################

"""
Simplified emissions calculator for early-stage chatbot implementation.
Uses stored tank/soil volumes, STP conditions, and manual food waste input.
"""

class EmissionsCalculator:
    """Simplified calculator for CO₂ emissions in composting systems."""
    
    # Constants for STP (Standard Temperature and Pressure)
    STP_AIR_CONCENTRATION_PERCENT = 21.0  # Oxygen concentration at STP
    STP_CO2_PPM = 415.0  # Approximate atmospheric CO₂ at STP
    
    @staticmethod
    def calculate_co2_saved_from_food_waste(food_waste_kg: float, 
                                          tank_volume: float, 
                                          soil_volume: float) -> dict:
        """
        Calculate CO₂ emissions saved from composting food waste.
        
        Parameters:
        -----------
        food_waste_kg : float
            Total food waste composted (in kg)
        tank_volume : float
            Total volume of the tank (cubic metres)
        soil_volume : float
            Volume of soil in the tank (cubic metres)
        
        Returns:
        --------
        dict
            Dictionary containing emission calculations and savings
        """
        
        # Use STP conditions
        co2_ppm = EmissionsCalculator.STP_CO2_PPM
        air_concentration_percent = EmissionsCalculator.STP_AIR_CONCENTRATION_PERCENT
        
        # Convert percentage to decimal
        air_concentration = air_concentration_percent / 100
        
        # Calculate effective air volume using the original formula
        effective_volume = tank_volume - (soil_volume * air_concentration)
        
        # Apply the original formula for baseline emissions
        baseline_co2_mass_grams = (co2_ppm / 1_000_000) * effective_volume * 1.8
        
        # Calculate CO₂ saved from food waste composting
        # Assumption: 1kg of food waste would generate ~2.5kg CO₂ in landfill
        # Composting reduces this by approximately 80%
        co2_saved_from_landfill_kg = food_waste_kg * 2.5 * 0.8
        
        # Convert to grams for consistency
        co2_saved_from_landfill_grams = co2_saved_from_landfill_kg * 1000
        
        # Calculate total environmental impact
        total_co2_saved_grams = baseline_co2_mass_grams + co2_saved_from_landfill_grams
        total_co2_saved_kg = total_co2_saved_grams / 1000
        
        return {
            'food_waste_kg': food_waste_kg,
            'tank_volume': tank_volume,
            'soil_volume': soil_volume,
            'effective_volume': round(effective_volume, 4),
            'baseline_emissions_grams': round(baseline_co2_mass_grams, 6),
            'co2_saved_from_landfill_kg': round(co2_saved_from_landfill_kg, 2),
            'total_co2_saved_kg': round(total_co2_saved_kg, 2),
            'total_co2_saved_grams': round(total_co2_saved_grams, 2)
        }
    
    @staticmethod
    def get_environmental_impact_summary(co2_saved_kg: float) -> dict:
        """
        Calculate environmental impact metrics from CO₂ savings.
        
        Parameters:
        -----------
        co2_saved_kg : float
            Total CO₂ saved in kg
        
        Returns:
        --------
        dict
            Dictionary containing environmental impact metrics
        """
        # Trees equivalent (25kg CO₂ per tree per year - simplified)
        trees_equivalent = co2_saved_kg / 25
        
        # Petrol equivalent (2.3kg CO₂ per litre of petrol)
        petrol_litres_equivalent = co2_saved_kg / 2.3
        
        # Car miles equivalent (0.4kg CO₂ per mile average)
        car_miles_equivalent = co2_saved_kg / 0.4
        
        return {
            'trees_equivalent': round(trees_equivalent, 2),
            'petrol_litres_equivalent': round(petrol_litres_equivalent, 1),
            'car_miles_equivalent': round(car_miles_equivalent, 1)
        }


def main():
    """Simple command-line interface for testing."""
    print("Simplified CO₂ Emissions Calculator")
    print("-----------------------------------")
    
    try:
        food_waste = float(input("Enter total food waste composted (kg): "))
        tank_volume = float(input("Enter tank volume (cubic metres): "))
        soil_volume = float(input("Enter soil volume (cubic metres): "))
        
        calculator = EmissionsCalculator()
        result = calculator.calculate_co2_saved_from_food_waste(food_waste, tank_volume, soil_volume)
        impact = calculator.get_environmental_impact_summary(result['total_co2_saved_kg'])
        
        print(f"\n=== RESULTS ===")
        print(f"Food waste composted: {result['food_waste_kg']} kg")
        print(f"Effective air volume: {result['effective_volume']} m³")
        print(f"CO₂ saved from landfill diversion: {result['co2_saved_from_landfill_kg']} kg")
        print(f"Total CO₂ emissions saved: {result['total_co2_saved_kg']} kg")
        print(f"\n=== ENVIRONMENTAL IMPACT ===")
        print(f"Equivalent to planting {impact['trees_equivalent']} trees")
        print(f"Equivalent to saving {impact['petrol_litres_equivalent']} litres of petrol")
        print(f"Equivalent to avoiding {impact['car_miles_equivalent']} miles of car travel")
        
    except ValueError:
        print("Please enter valid numbers.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()