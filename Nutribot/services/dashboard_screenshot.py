"""
Dashboard Screenshot Service
Captures screenshots of the CO2E Dashboard filtered for specific users
"""

import os
import asyncio
import tempfile
import io
from typing import Optional

# Try to import playwright, but make it optional
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("Warning: Playwright not available, only placeholder images will be generated")
    PLAYWRIGHT_AVAILABLE = False

from config import Config


class DashboardScreenshot:
    """Service for capturing dashboard screenshots"""
    
    # Dashboard URL - update this to match your actual dashboard URL
    DASHBOARD_BASE_URL = "http://localhost:5173"  # Update with your actual dashboard URL
    
    @staticmethod
    async def capture_user_dashboard(username: str) -> Optional[str]:
        """
        Capture a screenshot of the dashboard filtered for a specific user
        
        Args:
            username: The username to filter the dashboard for
            
        Returns:
            Path to the screenshot file or None if failed
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("Playwright not available, falling back to placeholder")
            return DashboardScreenshot.create_placeholder_image(username)
            
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                # Navigate to dashboard
                dashboard_url = f"{DashboardScreenshot.DASHBOARD_BASE_URL}/savings"
                await page.goto(dashboard_url, wait_until='networkidle')
                
                # Wait for the page to load completely
                await page.wait_for_timeout(3000)
                
                # Select Personal view if not already selected
                try:
                    personal_button = page.locator('button:has-text("Personal View")')
                    if await personal_button.is_visible():
                        await personal_button.click()
                        await page.wait_for_timeout(1000)
                except:
                    pass  # Already in personal view or button not found
                
                # Select the user from dropdown
                try:
                    user_dropdown = page.locator('select')
                    if await user_dropdown.is_visible():
                        await user_dropdown.select_option(value=username)
                        
                        # Wait for data to load
                        await page.wait_for_timeout(3000)
                        
                        # Wait for loading to finish
                        loading_indicator = page.locator('text=Loading')
                        if await loading_indicator.is_visible():
                            await loading_indicator.wait_for(state='hidden', timeout=10000)
                    
                except Exception as e:
                    print(f"Error selecting user: {e}")
                    # Continue anyway - might already be selected or user might not exist
                
                # Create temporary file for screenshot
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=f'_{username}_dashboard.png', 
                    delete=False
                )
                temp_file.close()
                
                # Take screenshot
                await page.screenshot(
                    path=temp_file.name,
                    full_page=True
                )
                
                await browser.close()
                return temp_file.name
                
        except Exception as e:
            print(f"Error capturing dashboard screenshot: {e}")
            # Return placeholder image instead
            return DashboardScreenshot.create_placeholder_image(username)
    
    @staticmethod
    def create_placeholder_image(username: str) -> Optional[str]:
        """
        Create a placeholder image when dashboard is not available
        
        Args:
            username: The username to create placeholder for
            
        Returns:
            Path to placeholder image file or None if failed
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image with dashboard theme colors
            img = Image.new('RGB', (1200, 800), color='#2D4A3E')  # deepgreen
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts, fallback to default if not available
            try:
                font_title = ImageFont.truetype("arial.ttf", 48)
                font_large = ImageFont.truetype("arial.ttf", 32)
                font_medium = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 18)
            except:
                font_title = ImageFont.load_default()
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Colors from the dashboard theme
            sage_color = '#8FB896'
            cream_color = '#F7FFF2'
            deepgreen_color = '#2D4A3E'
            
            # Draw header
            draw.text((600, 100), "CO₂E Savings Dashboard", fill=sage_color, font=font_title, anchor='mm')
            draw.text((600, 160), f"Personal Impact: {username}", fill=cream_color, font=font_large, anchor='mm')
            
            # Create mock dashboard sections
            # Left side - metrics cards
            card_y = 220
            card_height = 120
            card_width = 250
            
            metrics = [
                ("🥬", "Food Waste", "Processing..."),
                ("🌍", "CO₂ Saved", "Calculating..."),
                ("🌳", "Trees Equiv.", "Loading..."),
                ("🚗", "Car Miles", "Updating...")
            ]
            
            for i, (icon, title, value) in enumerate(metrics):
                x = 150 + (i % 2) * 280
                y = card_y + (i // 2) * 140
                
                # Draw card background
                draw.rectangle([x, y, x + card_width, y + card_height], fill=sage_color)
                
                # Draw icon and text
                draw.text((x + 30, y + 25), icon, fill=cream_color, font=font_large)
                draw.text((x + 30, y + 65), title, fill=cream_color, font=font_medium)
                draw.text((x + 30, y + 90), value, fill=cream_color, font=font_small)
            
            # Right side - chart placeholder
            chart_x, chart_y = 700, 220
            chart_w, chart_h = 400, 300
            draw.rectangle([chart_x, chart_y, chart_x + chart_w, chart_y + chart_h], fill=sage_color)
            draw.text((chart_x + chart_w//2, chart_y + 30), "CO₂ Savings Trend", fill=cream_color, font=font_medium, anchor='mm')
            draw.text((chart_x + chart_w//2, chart_y + chart_h//2), "📈", fill=cream_color, font=font_title, anchor='mm')
            draw.text((chart_x + chart_w//2, chart_y + chart_h - 40), "Chart Loading...", fill=cream_color, font=font_small, anchor='mm')
            
            # Bottom section
            bottom_y = 560
            draw.text((600, bottom_y), "🌱 Dashboard Coming Soon! 🌱", fill=sage_color, font=font_large, anchor='mm')
            draw.text((600, bottom_y + 40), "Your composting impact will be visualized here", fill=cream_color, font=font_medium, anchor='mm')
            draw.text((600, bottom_y + 70), "once the dashboard is deployed and accessible", fill=cream_color, font=font_medium, anchor='mm')
            
            # Footer
            draw.text((600, 720), "🌍 Making a positive environmental impact through composting! 🌍", fill=sage_color, font=font_small, anchor='mm')
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=f'_{username}_placeholder.png',
                delete=False
            )
            img.save(temp_file.name, 'PNG')
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error creating placeholder image: {e}")
            return None
    
    @staticmethod
    async def capture_plant_moisture_dashboard(username: str) -> Optional[str]:
        """
        Capture a screenshot of the plant moisture dashboard for a specific user
        
        Args:
            username: The username to filter the dashboard for
            
        Returns:
            Path to the screenshot file or None if failed
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("Playwright not available, falling back to placeholder")
            return DashboardScreenshot.create_plant_moisture_placeholder(username)
            
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                # Navigate to plant moisture dashboard
                dashboard_url = f"{DashboardScreenshot.DASHBOARD_BASE_URL}/plant-moisture?user={username}"
                await page.goto(dashboard_url, wait_until='networkidle')
                
                # Wait for the page to load completely
                await page.wait_for_timeout(3000)
                
                # Select the user from dropdown
                try:
                    user_dropdown = page.locator('select')
                    if await user_dropdown.is_visible():
                        await user_dropdown.select_option(value=username)
                        
                        # Wait for data to load
                        await page.wait_for_timeout(3000)
                        
                        # Wait for loading to finish
                        loading_indicator = page.locator('text=Loading')
                        if await loading_indicator.is_visible():
                            await loading_indicator.wait_for(state='hidden', timeout=10000)
                    
                except Exception as e:
                    print(f"Error selecting user: {e}")
                    # Continue anyway - might already be selected or user might not exist
                
                # Create temporary file for screenshot
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=f'_{username}_plant_dashboard.png', 
                    delete=False
                )
                temp_file.close()
                
                # Take screenshot
                await page.screenshot(
                    path=temp_file.name,
                    full_page=True
                )
                
                await browser.close()
                return temp_file.name
                
        except Exception as e:
            print(f"Error capturing plant moisture dashboard screenshot: {e}")
            # Return placeholder image instead
            return DashboardScreenshot.create_plant_moisture_placeholder(username)

    @staticmethod
    def create_plant_moisture_placeholder(username: str) -> Optional[str]:
        """
        Create a placeholder image for plant moisture dashboard when not available
        
        Args:
            username: The username to create placeholder for
            
        Returns:
            Path to placeholder image file or None if failed
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image with dashboard theme colors
            img = Image.new('RGB', (1200, 800), color='#2D4A3E')  # deepgreen
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts, fallback to default if not available
            try:
                font_title = ImageFont.truetype("arial.ttf", 48)
                font_large = ImageFont.truetype("arial.ttf", 32)
                font_medium = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 18)
            except:
                font_title = ImageFont.load_default()
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Colors from the dashboard theme
            sage_color = '#8FB896'
            cream_color = '#F7FFF2'
            
            # Draw header
            draw.text((600, 100), "🌱 Plant Moisture Dashboard", fill=sage_color, font=font_title, anchor='mm')
            draw.text((600, 160), f"Moisture Tracking: {username}", fill=cream_color, font=font_large, anchor='mm')
            
            # Create mock dashboard sections
            # Left side - status cards
            card_y = 220
            card_height = 120
            card_width = 250
            
            status_cards = [
                ("💧", "Current Moisture", "65%", "Good"),
                ("🗓️", "Next Watering", "Aug 15", "3 Days"),
                ("🚨", "Alerts", "2 Upcoming", "Monitor"),
                ("📊", "30-Day Trend", "Stable", "Healthy")
            ]
            
            for i, (icon, title, value, status) in enumerate(status_cards):
                x = 100 + (i % 2) * 280
                y = card_y + (i // 2) * 140
                
                # Draw card background
                draw.rectangle([x, y, x + card_width, y + card_height], fill=sage_color)
                
                # Draw icon and text
                draw.text((x + 30, y + 25), icon, fill=cream_color, font=font_large)
                draw.text((x + 30, y + 65), title, fill=cream_color, font=font_medium)
                draw.text((x + 30, y + 85), value, fill=cream_color, font=font_small)
                draw.text((x + 30, y + 100), status, fill=cream_color, font=font_small)
            
            # Right side - chart placeholder
            chart_x, chart_y = 650, 220
            chart_w, chart_h = 450, 300
            draw.rectangle([chart_x, chart_y, chart_x + chart_w, chart_y + chart_h], fill=sage_color)
            draw.text((chart_x + chart_w//2, chart_y + 30), "30-Day Moisture Prediction", fill=cream_color, font=font_medium, anchor='mm')
            draw.text((chart_x + chart_w//2, chart_y + chart_h//2), "📈", fill=cream_color, font=font_title, anchor='mm')
            draw.text((chart_x + chart_w//2, chart_y + chart_h - 40), "ML-Powered Forecasting", fill=cream_color, font=font_small, anchor='mm')
            
            # Bottom section - watering schedule
            bottom_y = 560
            draw.text((600, bottom_y), "🚨 Watering Schedule", fill=sage_color, font=font_large, anchor='mm')
            draw.text((300, bottom_y + 40), "Aug 10: Water needed (39%)", fill=cream_color, font=font_medium)
            draw.text((300, bottom_y + 65), "Aug 17: Critical level (26%)", fill=cream_color, font=font_medium)
            draw.text((300, bottom_y + 90), "Aug 24: Monitor closely (15%)", fill=cream_color, font=font_medium)
            
            # Footer
            draw.text((600, 720), "🌱 AI-Powered Plant Care Monitoring 🌱", fill=sage_color, font=font_small, anchor='mm')
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=f'_{username}_plant_placeholder.png',
                delete=False
            )
            img.save(temp_file.name, 'PNG')
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error creating plant moisture placeholder image: {e}")
            return None

    @staticmethod
    def get_dashboard_url(username: str) -> str:
        """
        Generate a direct URL to the dashboard filtered for a specific user
        
        Args:
            username: The username to filter for
            
        Returns:
            URL string with user parameter
        """
        return f"{DashboardScreenshot.DASHBOARD_BASE_URL}/savings?user={username}&view=personal"
    
    @staticmethod
    def get_plant_moisture_dashboard_url(username: str) -> str:
        """
        Generate a direct URL to the plant moisture dashboard filtered for a specific user
        
        Args:
            username: The username to filter for
            
        Returns:
            URL string with user parameter
        """
        return f"{DashboardScreenshot.DASHBOARD_BASE_URL}/plant-moisture?user={username}"
    
    @staticmethod
    def cleanup_screenshot(file_path: str):
        """
        Clean up screenshot file
        
        Args:
            file_path: Path to the screenshot file to delete
        """
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up screenshot: {e}")
