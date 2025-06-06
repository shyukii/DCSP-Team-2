from config import Config

class CompostProcessCalculator:
    """
    Calculates the compost recipe (greens, browns, water) 
    for a given feed input and provides stubs for yield and time estimates,
    including a ±20% timing range.
    """

    # Typical C:N ratios
    CN_GREENS    = Config.CompostCalculations.CN_GREENS
    CN_BROWNS    = Config.CompostCalculations.CN_BROWNS
    TARGET_CN    = Config.CompostCalculations.TARGET_CN_RATIO

    # Moisture targets
    TARGET_MOISTURE = Config.CompostCalculations.TARGET_MOISTURE

    @staticmethod
    def calculate_recipe(feed_weight_kg: float) -> dict:
        """
        Given the weight of fresh feed (greens) in kg,
        returns the required browns (kg), water (L), and total starting mass.
        """
        greens = feed_weight_kg
        browns = greens * (CompostProcessCalculator.TARGET_CN - CompostProcessCalculator.CN_GREENS) \
                         / (CompostProcessCalculator.CN_BROWNS - CompostProcessCalculator.TARGET_CN)
        total_mass = greens + browns

        water = CompostProcessCalculator.TARGET_MOISTURE * total_mass \
                - (greens * 0.8 + browns * 0.1)

        return {
            "greens_kg": round(greens, 2),
            "browns_kg": round(browns, 2),
            "water_kg": round(max(water, 0), 2),
            "total_start_mass_kg": round(total_mass, 2)
        }

    @staticmethod
    def estimate_yield(feed_weight_kg: float) -> float:
        """
        Estimate the finished-compost yield (kg) based on typical 50% mass loss.
        """
        return round(feed_weight_kg * 0.5, 2)

    @staticmethod
    def estimate_time_to_ready(feed_weight_kg: float) -> float:
        """
        Base estimator for days until compost is ready.
        Uses 6 days per kg of greens as a rule-of-thumb.
        """
        return round(feed_weight_kg * Config.CompostCalculations.TIME_PER_KG_GREENS, 1)

    @staticmethod
    def estimate_time_range(
        feed_weight_kg: float,
        variability: float = Config.CompostCalculations.TIMING_VARIABILITY
    ) -> tuple[float, float, float]:
        """
        Returns (lower_bound, estimate, upper_bound) in days,
        where estimate = 6 days/kg * feed, and bounds ±variability.
        """
        base  = CompostProcessCalculator.estimate_time_to_ready(feed_weight_kg)
        lower = round(base * (1 - variability), 1)
        upper = round(base * (1 + variability), 1)
        return lower, base, upper

    @staticmethod
    def analyze_actual_mix(
        greens_kg: float, 
        browns_kg: float, 
        water_kg: float
    ) -> dict:
        """
        Given the *actual* mix the user enters, return:
          - total_start_mass_kg
          - expected_yield_kg       (50% of greens)
          - time_lower_days,        (base ± variability)
          - time_est_days,
          - time_upper_days
        """
        total_start_mass = round(greens_kg + browns_kg + water_kg, 2)
        expected_yield   = CompostProcessCalculator.estimate_yield(greens_kg)
        lo, est, hi      = CompostProcessCalculator.estimate_time_range(greens_kg)

        return {
            "total_start_mass_kg": total_start_mass,
            "expected_yield_kg":   expected_yield,
            "time_lower_days":     lo,
            "time_est_days":       est,
            "time_upper_days":     hi,
        }


# Example usage
if __name__ == "__main__":
    greens, browns, water = 1.5, 0.8, 0.4
    results = CompostProcessCalculator.analyze_actual_mix(greens, browns, water)
    print("For an actual mix of "
          f"{greens} kg greens, {browns} kg browns, {water} L water:")
    print(" → Total start mass:", results["total_start_mass_kg"], "kg")
    print(" → Expected yield:",    results["expected_yield_kg"],    "kg")
    print(" → Est. time to ready:", results["time_est_days"],       "days")
    print(" → Time range:",        f"{results['time_lower_days']}–{results['time_upper_days']} days")
