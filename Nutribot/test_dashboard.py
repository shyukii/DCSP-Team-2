"""
Test script for dashboard screenshot functionality
"""
import asyncio
import os
from services.dashboard_screenshot import DashboardScreenshot

async def test_dashboard_screenshot():
    """Test the dashboard screenshot functionality"""
    print("Testing dashboard screenshot service...")
    
    # Test username
    test_username = "testuser"
    
    try:
        # Try to capture dashboard (will likely fail since dashboard isn't running)
        print(f"\n1. Attempting to capture dashboard for user: {test_username}")
        screenshot_path = await DashboardScreenshot.capture_user_dashboard(test_username)
        
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"✅ Screenshot created successfully: {screenshot_path}")
            
            # Check file size
            file_size = os.path.getsize(screenshot_path)
            print(f"   File size: {file_size:,} bytes")
            
            # Clean up
            DashboardScreenshot.cleanup_screenshot(screenshot_path)
            print("✅ Cleanup completed")
            
        else:
            print("❌ Screenshot creation failed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    # Test URL generation
    print(f"\n2. Testing URL generation for user: {test_username}")
    dashboard_url = DashboardScreenshot.get_dashboard_url(test_username)
    print(f"✅ Generated URL: {dashboard_url}")

if __name__ == "__main__":
    asyncio.run(test_dashboard_screenshot())
