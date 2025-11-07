#!/usr/bin/env python3
"""
QR Code Detection + Website Camera Button Automation for Smart Parking System
This script runs on Raspberry Pi to:
1. Continuously monitor camera feed for QR codes
2. When QR code is detected, automatically click "Open Camera" button on website
3. Let the website handle the QR scanning and validation
"""

import time
import cv2
from pyzbar import pyzbar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
from threading import Thread, Event

# Configuration
WEBSITE_URL = "YOUR_REPLIT_URL_HERE"  # Replace with your actual Replit URL
CAMERA_BUTTON_SELECTOR = "button#openCamera"  # Update with actual CSS selector
CAMERA_INDEX = 0  # 0 for USB camera, can be changed for multiple cameras
QR_COOLDOWN = 10  # Seconds to wait after clicking button before detecting next QR

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartParkingAutomation:
    def __init__(self, website_url, button_selector, camera_index=0):
        self.website_url = website_url
        self.button_selector = button_selector
        self.camera_index = camera_index
        self.driver = None
        self.camera = None
        self.last_qr_time = 0
        self.qr_cooldown = QR_COOLDOWN
        self.running = Event()
        self.qr_detected = Event()
        
    def setup_browser(self):
        """Initialize Chrome browser for Raspberry Pi"""
        try:
            chrome_options = Options()
            
            # Don't use headless - website needs to access camera
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Allow camera access automatically
            chrome_options.add_argument('--use-fake-ui-for-media-stream')
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.media_stream_camera": 1,
                "profile.default_content_setting_values.media_stream_mic": 1,
                "profile.default_content_setting_values.notifications": 2
            })
            
            # For Raspberry Pi
            service = Service('/usr/bin/chromedriver')
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Browser initialized successfully")
            
            # Navigate to website
            logger.info(f"Navigating to {self.website_url}")
            self.driver.get(self.website_url)
            time.sleep(3)  # Wait for page to load
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    def setup_camera(self):
        """Initialize camera for QR code detection"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return False
            
            logger.info(f"Camera {self.camera_index} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def detect_qr_code(self, frame):
        """Detect QR codes in the camera frame"""
        qr_codes = pyzbar.decode(frame)
        
        if qr_codes:
            for qr_code in qr_codes:
                qr_data = qr_code.data.decode('utf-8')
                
                # Draw rectangle around QR code for visual feedback
                points = qr_code.polygon
                if len(points) == 4:
                    pts = [(point.x, point.y) for point in points]
                    for i in range(4):
                        cv2.line(frame, pts[i], pts[(i + 1) % 4], (0, 255, 0), 3)
                
                # Add text showing QR data
                cv2.putText(frame, f"QR: {qr_data[:20]}", 
                           (qr_code.rect.left, qr_code.rect.top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                return qr_data, frame
        
        return None, frame
    
    def camera_monitoring_thread(self):
        """Thread to continuously monitor camera for QR codes"""
        logger.info("Camera monitoring thread started")
        
        while self.running.is_set():
            ret, frame = self.camera.read()
            
            if not ret:
                logger.warning("Failed to read frame from camera")
                time.sleep(0.1)
                continue
            
            # Check cooldown period
            current_time = time.time()
            if current_time - self.last_qr_time < self.qr_cooldown:
                # Show cooldown status
                remaining = int(self.qr_cooldown - (current_time - self.last_qr_time))
                cv2.putText(frame, f"Cooldown: {remaining}s", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                # Detect QR codes
                qr_data, frame = self.detect_qr_code(frame)
                
                if qr_data:
                    logger.info(f"QR Code detected: {qr_data}")
                    self.qr_detected.set()  # Signal that QR was detected
                    self.last_qr_time = current_time
                    
                    # Show detection status
                    cv2.putText(frame, "QR DETECTED! Clicking button...", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display status
            cv2.putText(frame, "Scanning for QR codes...", (10, 450),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show the frame
            cv2.imshow('QR Code Detection - Smart Parking', frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Exit key pressed")
                self.running.clear()
                break
            
            time.sleep(0.03)  # ~30 FPS
    
    def click_camera_button(self):
        """Click the 'Open Camera' button on the website"""
        try:
            logger.info("Looking for camera button...")
            
            # Wait for button to be clickable
            camera_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.button_selector))
            )
            
            logger.info("Clicking 'Open Camera' button")
            camera_button.click()
            
            logger.info("Successfully clicked button - website should now scan QR code")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click camera button: {e}")
            logger.info(f"Make sure selector is correct: {self.button_selector}")
            return False
    
    def run(self):
        """Main function to run the automation system"""
        logger.info("=" * 60)
        logger.info("Smart Parking QR Automation System Starting")
        logger.info("=" * 60)
        
        # Setup browser
        if not self.setup_browser():
            logger.error("Failed to setup browser. Exiting.")
            return
        
        # Setup camera
        if not self.setup_camera():
            logger.error("Failed to setup camera. Exiting.")
            self.cleanup()
            return
        
        # Start the system
        self.running.set()
        
        # Start camera monitoring in separate thread
        camera_thread = Thread(target=self.camera_monitoring_thread, daemon=True)
        camera_thread.start()
        
        logger.info("System is running. Monitoring for QR codes...")
        logger.info("Press 'q' in the camera window to exit")
        
        try:
            # Main loop - wait for QR detections
            while self.running.is_set():
                if self.qr_detected.is_set():
                    # QR code was detected, click the button
                    self.click_camera_button()
                    self.qr_detected.clear()
                    
                    logger.info(f"Waiting {self.qr_cooldown} seconds before next detection...")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.running.clear()
            camera_thread.join(timeout=2)
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        if self.camera:
            self.camera.release()
        
        if self.driver:
            self.driver.quit()
        
        cv2.destroyAllWindows()
        logger.info("Cleanup complete")


def main():
    """
    Setup Instructions:
    1. Update WEBSITE_URL with your Replit URL
    2. Update CAMERA_BUTTON_SELECTOR with correct button selector
    3. Adjust QR_COOLDOWN if needed (time between QR detections)
    4. Run: python3 qr_parking_automation.py
    
    The system will:
    - Monitor camera for QR codes
    - When QR detected, automatically click "Open Camera" on website
    - Wait for cooldown period before detecting next QR
    - Website handles actual QR scanning and validation
    """
    
    automation = SmartParkingAutomation(
        website_url=WEBSITE_URL,
        button_selector=CAMERA_BUTTON_SELECTOR,
        camera_index=CAMERA_INDEX
    )
    
    automation.run()


if __name__ == "__main__":
    main()
