class EmissionsCalculator:
    """Simplified calculator for CO₂ emissions in composting systems."""

    # Constants for STP
    STP_AIR_CONCENTRATION_PERCENT = 21.0
    STP_CO2_PPM = 415.0

    @staticmethod
    def calculate_co2_saved_from_food_waste(food_waste_kg: float,
                                            tank_volume: float,
                                            soil_volume: float) -> dict:
        """
        Calculate CO₂ emissions saved from composting food waste.
        """
        co2_ppm = EmissionsCalculator.STP_CO2_PPM
        air_conc = EmissionsCalculator.STP_AIR_CONCENTRATION_PERCENT / 100

        effective_volume = tank_volume - (soil_volume * air_conc)
        baseline_co2_grams = (co2_ppm / 1_000_000) * effective_volume * 1.8

        # 1kg food waste → ~2.5kg CO₂, composting reduces 80%
        co2_saved_landfill_kg = food_waste_kg * 2.5 * 0.8
        co2_saved_landfill_g = co2_saved_landfill_kg * 1000

        total_saved_g = baseline_co2_grams + co2_saved_landfill_g
        total_saved_kg = total_saved_g / 1000

        return {
            'food_waste_kg': food_waste_kg,
            'tank_volume': tank_volume,
            'soil_volume': soil_volume,
            'effective_volume': round(effective_volume, 4),
            'baseline_emissions_grams': round(baseline_co2_grams, 6),
            'co2_saved_from_landfill_kg': round(co2_saved_landfill_kg, 2),
            'total_co2_saved_kg': round(total_saved_kg, 2),
            'total_co2_saved_grams': round(total_saved_g, 2)
        }

    @staticmethod
    def get_environmental_impact_summary(co2_saved_kg: float) -> dict:
        """
        Convert CO₂ savings into relatable metrics.
        """
        return {
            'trees_equivalent': round(co2_saved_kg / 25, 2),
            'petrol_litres_equivalent': round(co2_saved_kg / 2.3, 1),
            'car_miles_equivalent': round(co2_saved_kg / 0.4, 1)
        }
