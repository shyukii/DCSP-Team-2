"""
CO2 Calculator Module for Composting System
Handles emissions calculations and /co2 command functionality
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.database import db
from constants import MAIN_MENU, CO2_FOOD_WASTE_INPUT


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


# CO2 Calculator Command Functions
async def co2_calculator_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Enhanced CO2 command with calculator functionality
    """
    telegram_id = update.effective_user.id
    user_data = await db.get_user_by_telegram_id(telegram_id)
    
    if not user_data:
        await update.message.reply_text("Please /start to login first.")
        return
    
    tank_vol = user_data.get("tank_volume", 0)
    soil_vol = user_data.get("soil_volume", 0)
    
    # Check if user has set up volumes
    if tank_vol == 0 or soil_vol == 0:
        await update.message.reply_text(
            "⚠️ **Volume Setup Required**\n\n"
            "Please set up your tank and soil volumes in /profile first!",
            parse_mode="Markdown"
        )
        return
    
    # Get stored food waste total if available
    total_food_waste = user_data.get("total_food_waste_kg", 0)
    
    # Create keyboard options
    keyboard = [
        [InlineKeyboardButton("🧮 Calculate New Savings", callback_data="co2_calculate")],
        [InlineKeyboardButton("📊 View Total Impact", callback_data="co2_view_total")],
        [InlineKeyboardButton("🔄 Reset Counter", callback_data="co2_reset")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Calculate current savings
    if total_food_waste > 0:
        result = EmissionsCalculator.calculate_co2_saved_from_food_waste(
            total_food_waste, tank_vol, soil_vol
        )
        impact = EmissionsCalculator.get_environmental_impact_summary(
            result['total_co2_saved_kg']
        )
        
        message = (
            f"🌍 **CO₂ Savings Calculator**\n\n"
            f"📈 **Your Impact So Far:**\n"
            f"• Food waste composted: {total_food_waste:.1f} kg\n"
            f"• CO₂ saved: {result['total_co2_saved_kg']:.1f} kg\n"
            f"• Equivalent to planting {impact['trees_equivalent']} trees 🌳\n"
            f"• Or saving {impact['petrol_litres_equivalent']} litres of petrol ⛽\n\n"
            f"What would you like to do?"
        )
    else:
        message = (
            "🌍 **CO₂ Savings Calculator**\n\n"
            "Start tracking your environmental impact!\n"
            "Calculate how much CO₂ you save by composting food waste.\n\n"
            "What would you like to do?"
        )
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    return MAIN_MENU


async def handle_co2_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callbacks for CO2 calculator options"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    user_data = await db.get_user_by_telegram_id(telegram_id)
    
    if query.data == "co2_calculate":
        await query.edit_message_text(
            "🧮 **CO₂ Savings Calculator**\n\n"
            "Enter the weight of food waste you've added to your compost (in kg).\n\n"
            "Examples:\n"
            "• 0.5 (for 500g)\n"
            "• 1.5 (for 1.5kg)\n"
            "• 2.3 (for 2.3kg)\n\n"
            "💡 *Tip: An average household produces about 1-2kg of food waste per week*",
            parse_mode="Markdown"
        )
        return CO2_FOOD_WASTE_INPUT
        
    elif query.data == "co2_view_total":
        total_food_waste = user_data.get("total_food_waste_kg", 0)
        tank_vol = user_data.get("tank_volume", 0)
        soil_vol = user_data.get("soil_volume", 0)
        
        if total_food_waste > 0:
            result = EmissionsCalculator.calculate_co2_saved_from_food_waste(
                total_food_waste, tank_vol, soil_vol
            )
            impact = EmissionsCalculator.get_environmental_impact_summary(
                result['total_co2_saved_kg']
            )
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="co2_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📊 **Total Environmental Impact**\n\n"
                f"🗑️ Total food waste composted: {total_food_waste:.2f} kg\n"
                f"💨 Total CO₂ saved: {result['total_co2_saved_kg']:.2f} kg\n\n"
                f"**Breakdown:**\n"
                f"• Baseline emissions saved: {result['baseline_emissions_grams']:.2f} g\n"
                f"• Landfill diversion savings: {result['co2_saved_from_landfill_kg']:.2f} kg\n\n"
                f"**Environmental Equivalents:**\n"
                f"🌳 Trees planted: {impact['trees_equivalent']}\n"
                f"⛽ Petrol saved: {impact['petrol_litres_equivalent']} litres\n"
                f"🚗 Car miles offset: {impact['car_miles_equivalent']} miles\n\n"
                f"Keep up the great work! 🌱",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                "📊 No composting data recorded yet.\n"
                "Start by calculating your first food waste input!",
                parse_mode="Markdown"
            )
            
        return MAIN_MENU
        
    elif query.data == "co2_reset":
        # Confirm reset
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Reset", callback_data="co2_confirm_reset")],
            [InlineKeyboardButton("❌ Cancel", callback_data="co2_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚠️ **Reset Confirmation**\n\n"
            "Are you sure you want to reset your total food waste counter to 0?\n"
            "This action cannot be undone.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return MAIN_MENU
        
    elif query.data == "co2_confirm_reset":
        # Reset the counter
        await db.update_user_profile(telegram_id, total_food_waste_kg=0)
        
        await query.edit_message_text(
            "✅ **Counter Reset**\n\n"
            "Your food waste counter has been reset to 0 kg.\n"
            "Ready to start tracking again!",
            parse_mode="Markdown"
        )
        return MAIN_MENU
        
    elif query.data == "co2_menu":
        # Return to CO2 menu
        return await co2_calculator_command(update, context)


async def handle_food_waste_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user input for food waste weight"""
    try:
        food_waste_kg = float(update.message.text.strip())
        
        if food_waste_kg <= 0:
            await update.message.reply_text(
                "❌ Please enter a positive number for food waste weight.\n"
                "Try again with a number like 1.5 or 2.0"
            )
            return CO2_FOOD_WASTE_INPUT
            
        if food_waste_kg > 100:  # Sanity check
            await update.message.reply_text(
                "❌ That seems like a very large amount! Please enter a reasonable weight (up to 100kg).\n"
                "Try again with a smaller number."
            )
            return CO2_FOOD_WASTE_INPUT
        
        # Load user data
        telegram_id = update.effective_user.id
        user_data = await db.get_user_by_telegram_id(telegram_id)
        tank_vol = user_data.get("tank_volume", 0)
        soil_vol = user_data.get("soil_volume", 0)
        
        # Update total food waste
        current_total = user_data.get("total_food_waste_kg", 0)
        new_total = current_total + food_waste_kg
        await db.update_user_profile(telegram_id, total_food_waste_kg=new_total)
        
        # Calculate savings for this input
        result = EmissionsCalculator.calculate_co2_saved_from_food_waste(
            food_waste_kg, tank_vol, soil_vol
        )
        
        # Calculate total savings
        total_result = EmissionsCalculator.calculate_co2_saved_from_food_waste(
            new_total, tank_vol, soil_vol
        )
        impact = EmissionsCalculator.get_environmental_impact_summary(
            result['total_co2_saved_kg']
        )
        
        # Create keyboard
        keyboard = [
            [InlineKeyboardButton("➕ Add More", callback_data="co2_calculate")],
            [InlineKeyboardButton("📊 View Total", callback_data="co2_view_total")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ **Calculation Complete!**\n\n"
            f"**This Input:**\n"
            f"• Food waste: {food_waste_kg:.2f} kg\n"
            f"• CO₂ saved: {result['total_co2_saved_kg']:.2f} kg\n"
            f"• Trees equivalent: {impact['trees_equivalent']} 🌳\n\n"
            f"**Running Total:**\n"
            f"• Total composted: {new_total:.2f} kg\n"
            f"• Total CO₂ saved: {total_result['total_co2_saved_kg']:.2f} kg\n\n"
            f"Great work reducing emissions! 🌍",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        return MAIN_MENU
        
    except ValueError:
        await update.message.reply_text(
            "❌ Please enter a valid number (e.g., 1.5, 2, 0.8).\n"
            "How many kilograms of food waste have you composted?"
        )
        return CO2_FOOD_WASTE_INPUT
    except Exception as e:
        await update.message.reply_text(
            "❌ Sorry, there was an error processing your input. Please try again."
        )
        return CO2_FOOD_WASTE_INPUT
