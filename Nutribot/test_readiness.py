#!/usr/bin/env python3
"""
Test script for EC forecast service with compost readiness estimation
"""

import sys
import traceback
from services.ec_forecast_service import ECForecastService

def test_ec_forecast_with_readiness():
    """Test the enhanced EC forecast service with compost readiness estimation"""
    try:
        print("🧪 Testing Enhanced EC Forecast Service with Readiness Estimation")
        print("=" * 60)
        
        # Initialize the service
        print("1. Loading EC Forecast Service...")
        ec_service = ECForecastService()
        print("✅ ECForecastService loaded successfully")
        
        # Test different scenarios
        test_cases = [
            {"ec": 2.5, "moisture": 65, "description": "Normal compost conditions"},
            {"ec": 1.8, "moisture": 50, "description": "Good maturation range"},
            {"ec": 4.2, "moisture": 70, "description": "High EC - needs stabilization"},
            {"ec": 0.8, "moisture": 45, "description": "Low EC - building nutrients"}
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {case['description']}")
            print(f"   Input: EC={case['ec']} mS/cm, Moisture={case['moisture']}%")
            
            # Generate prediction
            result = ec_service.predict_90_day_forecast(case['ec'], case['moisture'])
            
            if result['success']:
                print("✅ Prediction generated successfully")
                
                # Test the formatting with readiness info
                formatted_msg = ec_service.format_prediction_message(result)
                
                # Check if readiness estimation is included
                if '🎯 **Compost Readiness Estimate:**' in formatted_msg:
                    print("✅ Readiness estimation included in message")
                    
                    # Extract and show readiness section
                    lines = formatted_msg.split('\n')
                    readiness_start = -1
                    for j, line in enumerate(lines):
                        if '🎯 **Compost Readiness Estimate:**' in line:
                            readiness_start = j
                            break
                    
                    if readiness_start >= 0:
                        print("📋 Readiness section preview:")
                        for j in range(readiness_start, min(readiness_start + 10, len(lines))):
                            if lines[j].strip():  # Only show non-empty lines
                                print(f"   {lines[j]}")
                else:
                    print("❌ Readiness estimation not found in message")
                    
            else:
                print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
                
        print("\n" + "=" * 60)
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_ec_forecast_with_readiness()
    sys.exit(0 if success else 1)
