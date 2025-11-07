#!/usr/bin/env python3
"""
Button Selector Finder
This helper script opens your website and lists all buttons,
helping you find the correct selector for the "Open Camera" button.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# UPDATE THIS WITH YOUR WEBSITE URL
WEBSITE_URL = "YOUR_REPLIT_URL_HERE"

def find_buttons():
    """Find all buttons on the website and display their selectors"""
    
    print("=" * 70)
    print("Button Selector Finder for Smart Parking System")
    print("=" * 70)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Initialize browser
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"\n✓ Browser opened")
        print(f"✓ Navigating to: {WEBSITE_URL}")
        
        driver.get(WEBSITE_URL)
        time.sleep(3)  # Wait for page to load
        
        print("✓ Page loaded\n")
        print("=" * 70)
        print("FOUND BUTTONS:")
        print("=" * 70)
        
        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        if not buttons:
            print("❌ No buttons found on the page!")
            print("\nTrying to find input elements with type='button'...")
            buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='button']")
        
        if not buttons:
            print("❌ Still no buttons found!")
            print("\nMake sure:")
            print("1. Your website URL is correct")
            print("2. The page has fully loaded")
            print("3. The button is not inside an iframe")
        else:
            for i, button in enumerate(buttons, 1):
                print(f"\n--- Button #{i} ---")
                
                # Get button text
                text = button.text or button.get_attribute('value') or '(no text)'
                print(f"Text: {text}")
                
                # Get ID
                button_id = button.get_attribute('id')
                if button_id:
                    print(f"ID Selector: button#{button_id}")
                    print(f"  or just: #{button_id}")
                
                # Get classes
                classes = button.get_attribute('class')
                if classes:
                    class_list = classes.split()
                    if len(class_list) == 1:
                        print(f"Class Selector: button.{class_list[0]}")
                        print(f"  or just: .{class_list[0]}")
                    else:
                        print(f"Class Selector: button.{'.'.join(class_list)}")
                
                # Get name
                name = button.get_attribute('name')
                if name:
                    print(f"Name Selector: button[name='{name}']")
                
                # Get onclick
                onclick = button.get_attribute('onclick')
                if onclick:
                    print(f"OnClick: {onclick[:50]}...")
                
                # Get full outer HTML (first 100 chars)
                html = button.get_attribute('outerHTML')
                if html:
                    print(f"HTML: {html[:100]}...")
        
        print("\n" + "=" * 70)
        print("SUGGESTED SELECTORS TO TRY:")
        print("=" * 70)
        
        # Try to find camera-related buttons
        for button in buttons:
            text = (button.text or '').lower()
            button_id = (button.get_attribute('id') or '').lower()
            classes = (button.get_attribute('class') or '').lower()
            
            if any(keyword in text + button_id + classes 
                   for keyword in ['camera', 'cam', 'open', 'scan', 'qr']):
                
                print(f"\n🎯 Likely candidate: {button.text or '(no text)'}")
                
                if button.get_attribute('id'):
                    print(f"   Try: CAMERA_BUTTON_SELECTOR = \"#{button.get_attribute('id')}\"")
                elif button.get_attribute('class'):
                    first_class = button.get_attribute('class').split()[0]
                    print(f"   Try: CAMERA_BUTTON_SELECTOR = \".{first_class}\"")
                else:
                    print(f"   Try: CAMERA_BUTTON_SELECTOR = \"//button[contains(text(), '{button.text}')]\"")
                    print(f"        (Note: This uses XPath, change By.CSS_SELECTOR to By.XPATH in code)")
        
        print("\n" + "=" * 70)
        print("\nPress Enter to close browser...")
        input()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure WEBSITE_URL is set correctly at the top of this script")
        print("2. Check that chromium-chromedriver is installed:")
        print("   sudo apt-get install chromium-chromedriver")
        print("3. Verify your website is accessible:")
        print(f"   curl -I {WEBSITE_URL}")
    
    finally:
        try:
            driver.quit()
            print("✓ Browser closed")
        except:
            pass


if __name__ == "__main__":
    if WEBSITE_URL == "YOUR_REPLIT_URL_HERE":
        print("⚠️  Please update WEBSITE_URL at the top of this script first!")
        print("   Edit this file and replace YOUR_REPLIT_URL_HERE with your actual URL")
    else:
        find_buttons()
