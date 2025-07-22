#!/usr/bin/env python3
"""
HTML Business Card to PNG Converter
Converts your HTML business card to a high-quality PNG suitable for printing
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time

def html_to_png(html_file_path, output_path="business_card.png"):
    """
    Convert HTML file to PNG image
    
    Args:
        html_file_path (str): Path to your HTML file
        output_path (str): Output PNG file path
    """
    
    print("🚀 Starting HTML to PNG conversion...")
    
    # Check if HTML file exists
    if not os.path.exists(html_file_path):
        print(f"❌ Error: HTML file '{html_file_path}' not found!")
        return False
    
    try:
        # Business card dimensions at 300 DPI: 3.5" x 2" = 1050 x 600 pixels
        width = 1050
        height = 600
        
        # Setup Chrome options for headless operation
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--force-device-scale-factor=3")  # High DPI for crisp images
        
        print("📋 Setting up Chrome driver...")
        
        # Initialize Chrome driver with auto-download
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set viewport size to match business card aspect ratio
        # Add extra height to account for browser UI that might interfere
        driver.set_window_size(width, height + 100)
        
        # Convert file path to file:// URL
        file_url = f"file://{os.path.abspath(html_file_path)}"
        print(f"🌐 Loading HTML file: {file_url}")
        
        # Load the HTML file
        driver.get(file_url)
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Wait for fonts to load
        driver.execute_script("""
            return document.fonts.ready.then(function() {
                return true;
            });
        """)
        
        # Additional wait for any animations or late-loading content
        time.sleep(1)
        
        print("📸 Taking screenshot...")
        
        # Find the business card element and get its location/size
        card_element = driver.find_element("css selector", ".business-card")
        
        # Get element dimensions and location
        location = card_element.location
        size = card_element.size
        
        print(f"📏 Card element found - Location: {location}, Size: {size}")
        
        # Take full page screenshot first
        screenshot_path = "temp_full_screenshot.png"
        driver.save_screenshot(screenshot_path)
        
        # Close browser
        driver.quit()
        
        print("🎨 Processing and cropping image...")
        
        # Open the full screenshot
        with Image.open(screenshot_path) as full_img:
            # Calculate crop coordinates (account for device scale factor)
            scale_factor = 3  # Same as force-device-scale-factor
            left = location['x'] * scale_factor
            top = location['y'] * scale_factor
            right = left + (size['width'] * scale_factor)
            bottom = top + (size['height'] * scale_factor)
            
            print(f"🔍 Cropping coordinates: ({left}, {top}, {right}, {bottom})")
            
            # Crop to just the business card
            cropped_img = full_img.crop((left, top, right, bottom))
            
            # Resize to exact print dimensions (1050x600 at 300 DPI)
            final_img = cropped_img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed (removes alpha channel)
            if final_img.mode in ('RGBA', 'LA'):
                rgb_img = Image.new('RGB', final_img.size, (255, 255, 255))
                rgb_img.paste(final_img, mask=final_img.split()[-1] if final_img.mode == 'RGBA' else None)
                final_img = rgb_img
            
            # Save final image with print-quality settings
            final_img.save(output_path, "PNG", dpi=(300, 300), optimize=True)
        
        # Clean up temp file
        os.remove(screenshot_path)
        
        print(f"✅ Success! Business card saved as: {output_path}")
        print(f"📏 Final size: {width}x{height} pixels (3.5\" x 2\" at 300 DPI)")
        print("🖨️  Ready for VistaPrint upload!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure Chrome browser is installed")
        print("2. Check that your HTML file path is correct")
        print("3. Try running: pip install selenium webdriver-manager pillow")
        print("4. Make sure your HTML has a .business-card class on the main container")
        return False

def main():
    """Main function to run the converter"""
    
    print("🃏 HTML Business Card to PNG Converter")
    print("=" * 40)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Script directory: {script_dir}")
    
    # Look for HTML files in the script directory
    html_files = [f for f in os.listdir(script_dir) if f.endswith('.html')]
    
    if html_files:
        print(f"\n📄 Found HTML files in script directory:")
        for i, file in enumerate(html_files, 1):
            print(f"  {i}. {file}")
        
        if len(html_files) == 1:
            html_file = os.path.join(script_dir, html_files[0])
            print(f"\n🎯 Using: {html_files[0]}")
        else:
            try:
                choice = int(input(f"\nSelect HTML file (1-{len(html_files)}): ")) - 1
                html_file = os.path.join(script_dir, html_files[choice])
            except (ValueError, IndexError):
                print("❌ Invalid selection!")
                return
    else:
        print("❌ No HTML files found in script directory!")
        html_file = input("Enter full path to your HTML file: ").strip()
        if not os.path.exists(html_file):
            print("❌ File not found!")
            return
    
    # Set output file in script directory
    output_file = os.path.join(script_dir, "business_card.png")
    
    # Ask if user wants different output name
    custom_name = input(f"\nOutput filename (default: business_card.png): ").strip()
    if custom_name:
        if not custom_name.lower().endswith('.png'):
            custom_name += '.png'
        output_file = os.path.join(script_dir, custom_name)
    
    print(f"💾 Output will be saved to: {output_file}")
    
    # Convert the file
    success = html_to_png(html_file, output_file)
    
    if success:
        print(f"\n🎉 Your business card is ready!")
        print(f"📁 File saved: {os.path.basename(output_file)}")
        print(f"📍 Location: {os.path.dirname(output_file)}")
    else:
        print("\n😞 Conversion failed. Please check the error messages above.")

if __name__ == "__main__":
    main()