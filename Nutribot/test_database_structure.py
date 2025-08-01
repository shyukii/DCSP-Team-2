#!/usr/bin/env python3
"""
Test script for comprehensive database prediction storage
"""

def test_database_structure():
    """Test that all database methods work correctly"""
    print("🧪 Testing Comprehensive Database Prediction Storage")
    print("=" * 60)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from services.database import db
        print("✅ Database service imported successfully")
        
        # Test method existence
        print("\n2. Testing method availability...")
        methods_to_check = [
            'create_compost_status_with_predictions',
            'get_dashboard_data',
            '_analyze_ec_trend',
            '_calculate_readiness_metrics',
            '_assess_compost_conditions',
            '_generate_recommendations',
            '_calculate_dashboard_metrics'
        ]
        
        for method in methods_to_check:
            if hasattr(db, method):
                print(f"✅ {method} - Available")
            else:
                print(f"❌ {method} - Missing")
        
        print("\n3. Testing prediction data structure...")
        # Create sample prediction data
        sample_predictions = {
            'success': True,
            'predictions': [2.5, 2.4, 2.3, 2.2] * 22 + [2.1, 2.0],  # 90 values
            'dates': ['2025-08-01', '2025-08-02'] * 45,  # 90 dates
            'key_predictions': {
                'week_1': 2.4,
                'week_2': 2.3,
                'month_1': 2.2,
                'month_2': 2.1,
                'month_3': 2.0
            },
            'statistics': {
                'current_ec': 2.5,
                'average_ec': 2.25,
                'max_ec': 2.5,
                'min_ec': 2.0
            }
        }
        
        print("✅ Sample prediction data created")
        
        # Test helper methods
        print("\n4. Testing analysis methods...")
        
        try:
            trend_result = db._analyze_ec_trend(sample_predictions)
            print(f"✅ Trend analysis: {trend_result.get('ec_trend', 'unknown')}")
        except Exception as e:
            print(f"❌ Trend analysis failed: {e}")
        
        try:
            readiness_result = db._calculate_readiness_metrics(2.5, 65, sample_predictions)
            print(f"✅ Readiness metrics: {readiness_result.get('readiness_status', 'unknown')}")
        except Exception as e:
            print(f"❌ Readiness calculation failed: {e}")
        
        try:
            condition_result = db._assess_compost_conditions(2.5, 65, sample_predictions['statistics'])
            print(f"✅ Condition assessment: Score {condition_result.get('overall_health_score', 0)}")
        except Exception as e:
            print(f"❌ Condition assessment failed: {e}")
        
        try:
            recommendation_result = db._generate_recommendations(2.5, 65, sample_predictions)
            print(f"✅ Recommendations generated: {len(recommendation_result)} items")
        except Exception as e:
            print(f"❌ Recommendation generation failed: {e}")
        
        try:
            dashboard_result = db._calculate_dashboard_metrics(2.5, 65, sample_predictions)
            print(f"✅ Dashboard metrics: {dashboard_result.get('completion_percentage', 0)}% complete")
        except Exception as e:
            print(f"❌ Dashboard calculation failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Database structure test completed!")
        print("\n📋 Next Steps:")
        print("1. Run the SQL script: add_comprehensive_prediction_columns.sql")
        print("2. Test with actual user data")
        print("3. Implement dashboard frontend")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_structure()
