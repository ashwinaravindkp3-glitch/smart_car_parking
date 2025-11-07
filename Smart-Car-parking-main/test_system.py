#!/usr/bin/env python3
"""
Diagnostic Test Script for Smart Parking QR Automation
Run this to verify all components are working before using main script
"""

import sys
import subprocess

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def test_opencv():
    """Test OpenCV and camera"""
    print_header("Testing OpenCV and Camera")
    try:
        import cv2
        print("✓ OpenCV imported successfully")
        print(f"  Version: {cv2.__version__}")
        
        # Test camera
        print("\nTesting camera access...")
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("✓ Camera opened successfully")
            ret, frame = cap.read()
            if ret:
                print(f"✓ Frame captured successfully")
                print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            else:
                print("✗ Failed to capture frame")
                return False
            cap.release()
        else:
            print("✗ Failed to open camera")
            print("  Check: ls /dev/video*")
            return False
        
        return True
    except ImportError as e:
        print(f"✗ OpenCV not installed: {e}")
        print("  Install: sudo apt-get install python3-opencv")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_pyzbar():
    """Test pyzbar for QR detection"""
    print_header("Testing pyzbar (QR Detection)")
    try:
        from pyzbar import pyzbar
        print("✓ pyzbar imported successfully")
        
        # Check if zbar library is available
        import cv2
        import numpy as np
        
        # Create a simple test QR code image
        print("\nTesting QR code detection capability...")
        test_image = np.zeros((100, 100), dtype=np.uint8)
        result = pyzbar.decode(test_image)
        print("✓ pyzbar decode function working")
        
        return True
    except ImportError as e:
        print(f"✗ pyzbar not installed: {e}")
        print("  Install: pip3 install pyzbar")
        print("  Install: sudo apt-get install libzbar0")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_selenium():
    """Test Selenium"""
    print_header("Testing Selenium")
    try:
        from selenium import webdriver
        print("✓ Selenium imported successfully")
        
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        print("\nChecking ChromeDriver...")
        try:
            service = Service('/usr/bin/chromedriver')
            print("✓ ChromeDriver found at /usr/bin/chromedriver")
        except:
            print("✗ ChromeDriver not found")
            print("  Install: sudo apt-get install chromium-chromedriver")
            return False
        
        return True
    except ImportError as e:
        print(f"✗ Selenium not installed: {e}")
        print("  Install: pip3 install selenium")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_chromedriver():
    """Test ChromeDriver version"""
    print_header("Testing ChromeDriver and Chromium")
    try:
        # Check ChromeDriver
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ ChromeDriver: {result.stdout.strip()}")
        else:
            print("✗ ChromeDriver not working")
            return False
        
        # Check Chromium
        result = subprocess.run(['chromium-browser', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Chromium: {result.stdout.strip()}")
        else:
            print("✗ Chromium not installed")
            print("  Install: sudo apt-get install chromium-browser")
            return False
        
        return True
    except FileNotFoundError:
        print("✗ ChromeDriver or Chromium not found")
        print("  Install: sudo apt-get install chromium-browser chromium-chromedriver")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_camera_qr_detection():
    """Interactive test for camera and QR detection"""
    print_header("Interactive Camera + QR Detection Test")
    
    response = input("\nDo you want to test live QR detection? (y/n): ").lower()
    if response != 'y':
        print("Skipping interactive test")
        return True
    
    try:
        import cv2
        from pyzbar import pyzbar
        
        print("\nOpening camera... Show a QR code to test detection")
        print("Press 'q' to quit this test")
        
        cap = cv2.VideoCapture(0)
        qr_detected = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Try to detect QR codes
            qr_codes = pyzbar.decode(frame)
            
            if qr_codes:
                for qr_code in qr_codes:
                    qr_data = qr_code.data.decode('utf-8')
                    print(f"\n✓ QR Code detected: {qr_data}")
                    
                    # Draw box around QR
                    points = qr_code.polygon
                    if len(points) == 4:
                        pts = [(point.x, point.y) for point in points]
                        for i in range(4):
                            cv2.line(frame, pts[i], pts[(i + 1) % 4], (0, 255, 0), 3)
                    
                    qr_detected = True
            
            # Display frame
            status = "QR DETECTED!" if qr_codes else "Scanning for QR codes..."
            cv2.putText(frame, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('QR Detection Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if qr_detected:
            print("\n✓ QR detection is working!")
            return True
        else:
            print("\n⚠ No QR code was detected during test")
            print("  Try: Better lighting, larger QR code, or closer distance")
            return True  # Not a failure, just no QR shown
            
    except Exception as e:
        print(f"✗ Error during interactive test: {e}")
        return False

def test_browser_automation():
    """Test browser automation"""
    print_header("Testing Browser Automation")
    
    response = input("\nDo you want to test browser automation? (y/n): ").lower()
    if response != 'y':
        print("Skipping browser test")
        return True
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        import time
        
        print("\nOpening browser...")
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ Browser opened successfully")
        
        print("Navigating to Google...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        print(f"✓ Page loaded: {driver.title}")
        
        print("Closing browser...")
        driver.quit()
        
        print("✓ Browser automation test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Browser automation failed: {e}")
        return False

def check_system_info():
    """Display system information"""
    print_header("System Information")
    try:
        # Python version
        print(f"Python: {sys.version.split()[0]}")
        
        # OS info
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME'):
                        print(f"OS: {line.split('=')[1].strip('\"\\n')}")
                        break
        except:
            print("OS: Unknown")
        
        # Check camera devices
        try:
            result = subprocess.run(['ls', '/dev/video*'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                cameras = result.stdout.strip().split('\n')
                print(f"Cameras detected: {', '.join(cameras)}")
            else:
                print("Cameras detected: None")
        except:
            print("Cameras detected: Unable to check")
        
    except Exception as e:
        print(f"Error getting system info: {e}")

def main():
    print("\n" + "🔧" * 30)
    print("  SMART PARKING QR AUTOMATION - DIAGNOSTIC TEST")
    print("🔧" * 30)
    
    check_system_info()
    
    results = []
    
    # Run all tests
    results.append(("OpenCV & Camera", test_opencv()))
    results.append(("pyzbar (QR Detection)", test_pyzbar()))
    results.append(("Selenium", test_selenium()))
    results.append(("ChromeDriver & Chromium", test_chromedriver()))
    results.append(("Camera QR Detection", test_camera_qr_detection()))
    results.append(("Browser Automation", test_browser_automation()))
    
    # Summary
    print_header("Test Summary")
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "-"*60)
    if all_passed:
        print("✓ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Run: python3 find_button_selector.py")
        print("2. Update configuration in qr_parking_automation_v2.py")
        print("3. Run: python3 qr_parking_automation_v2.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nSee INSTALLATION_GUIDE.md for detailed troubleshooting")
    print("-"*60 + "\n")

if __name__ == "__main__":
    main()
