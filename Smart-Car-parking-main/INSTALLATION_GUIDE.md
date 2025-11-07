# Smart Parking QR Camera Automation - Complete Setup Guide

## 🎯 What This Does
This system automatically:
1. **Monitors your camera** for QR codes
2. **Detects when a QR code appears** in the camera view
3. **Automatically clicks** the "Open Camera" button on your website
4. **Lets your website handle** the QR scanning and user validation

## 📋 Prerequisites
- Raspberry Pi (Model 3B+ or newer recommended)
- USB Webcam or Raspberry Pi Camera Module
- Internet connection
- Your Replit website URL
- Monitor (for initial setup) or SSH access

## 🔧 Installation Steps

### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Required Packages

```bash
# Install Chromium and ChromeDriver
sudo apt-get install -y chromium-chromedriver chromium-browser

# Install Python and pip
sudo apt-get install -y python3 python3-pip

# Install OpenCV for camera/QR detection
sudo apt-get install -y python3-opencv

# Install required Python packages
pip3 install selenium pyzbar pillow

# Install ZBar for QR code decoding
sudo apt-get install -y libzbar0
```

### Step 3: Verify Camera

```bash
# Check if camera is detected
ls /dev/video*

# Should show something like: /dev/video0

# Test camera with simple capture
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera working!' if cap.isOpened() else 'Camera not working'); cap.release()"
```

### Step 4: Download the Scripts

Create a project directory:
```bash
mkdir ~/parking_automation
cd ~/parking_automation
```

Save these files to the directory:
- `qr_parking_automation_v2.py` - Main automation script
- `find_button_selector.py` - Helper to find button selector

### Step 5: Find Your Button Selector

Run the helper script to find the correct selector:
```bash
python3 find_button_selector.py
```

This will:
- Ask for your website URL
- Open the website
- Show all buttons found
- Suggest the correct selector format

Example output:
```
Button #1:
  Text: 'Open Camera'
  ID: 'openCamera'
  → Selector: button#openCamera
  Classes: btn, btn-primary
  → Selector: button.btn
```

### Step 6: Configure the Main Script

Edit `qr_parking_automation_v2.py`:
```bash
nano qr_parking_automation_v2.py
```

Update these configuration values near the top:
```python
WEBSITE_URL = "https://your-site.repl.co"  # Your actual Replit URL
CAMERA_BUTTON_SELECTOR = "button#openCamera"  # From helper script
CAMERA_INDEX = 0  # 0 for first camera, 1 for second, etc.
QR_COOLDOWN = 10  # Seconds between QR detections
```

**Important Selector Examples:**
- If button has ID: `button#openCamera` or `#openCamera`
- If button has class: `button.camera-btn` or `.btn-camera`
- By button text: `//button[contains(text(), 'Open Camera')]`
- By multiple classes: `button.btn.btn-primary`

### Step 7: Test the System

```bash
# Make script executable
chmod +x qr_parking_automation_v2.py

# Run the script
python3 qr_parking_automation_v2.py
```

**What should happen:**
1. Browser window opens with your website
2. Camera window appears showing live feed
3. System logs: "Scanning for QR codes..."
4. When you show a QR code to camera:
   - Green box appears around QR
   - System clicks "Open Camera" button
   - Website opens its camera for scanning
   - 10-second cooldown before next detection

**Testing checklist:**
- [ ] Camera window shows live feed
- [ ] Browser opens your website
- [ ] QR code is detected (green box appears)
- [ ] Button is clicked automatically
- [ ] Website camera opens for scanning

Press `q` in the camera window to exit.

## 🚀 Running at Startup

### Method 1: Using systemd (Recommended)

Create a service file:
```bash
sudo nano /etc/systemd/system/parking-automation.service
```

Add this content (adjust paths if needed):
```ini
[Unit]
Description=Smart Parking QR Camera Automation
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/parking_automation
ExecStart=/usr/bin/python3 /home/pi/parking_automation/qr_parking_automation_v2.py
Restart=always
RestartSec=10
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority

[Install]
WantedBy=graphical.target
```

Enable and start:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable parking-automation.service

# Start service now
sudo systemctl start parking-automation.service

# Check status
sudo systemctl status parking-automation.service

# View live logs
sudo journalctl -u parking-automation.service -f
```

**Service management commands:**
```bash
# Stop service
sudo systemctl stop parking-automation.service

# Restart service
sudo systemctl restart parking-automation.service

# Disable auto-start
sudo systemctl disable parking-automation.service

# View recent logs
sudo journalctl -u parking-automation.service -n 100
```

### Method 2: Using Autostart (Desktop)

If running on Raspberry Pi Desktop:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/parking-automation.desktop
```

Add:
```ini
[Desktop Entry]
Type=Application
Name=Parking Automation
Exec=python3 /home/pi/parking_automation/qr_parking_automation_v2.py
Terminal=false
```

## 🔍 Troubleshooting

### Issue: "Failed to open camera"
**Solutions:**
```bash
# Check camera connection
ls /dev/video*

# Check camera permissions
sudo usermod -a -G video $USER
# Then logout and login again

# Try different camera index
# In script, change: CAMERA_INDEX = 1  # or 2, 3, etc.

# Test camera manually
python3 -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print('Working!' if ret else 'Not working'); cap.release()"
```

### Issue: "Failed to click camera button"
**Solutions:**
1. **Run the helper script again:**
   ```bash
   python3 find_button_selector.py
   ```

2. **Try alternative selectors:**
   ```python
   # By class
   CAMERA_BUTTON_SELECTOR = ".camera-button"
   
   # By XPath (text-based)
   # Change By.CSS_SELECTOR to By.XPATH in the click function
   CAMERA_BUTTON_SELECTOR = "//button[contains(text(), 'Open')]"
   ```

3. **Increase wait time:**
   In the `click_camera_button` function, change:
   ```python
   camera_button = WebDriverWait(self.driver, 20).until(  # Changed from 10 to 20
   ```

4. **Check browser console:**
   Set `use_headless=False` to see browser and check for errors

### Issue: "ChromeDriver version mismatch"
```bash
# Check versions
chromium-browser --version
chromedriver --version

# Update both
sudo apt-get update
sudo apt-get install --reinstall chromium-browser chromium-chromedriver
```

### Issue: QR codes not detected
**Solutions:**
```bash
# Better lighting and QR code size needed

# Test QR detection:
python3 << 'EOF'
import cv2
from pyzbar import pyzbar

cap = cv2.VideoCapture(0)
print("Show QR code to camera...")

while True:
    ret, frame = cap.read()
    if ret:
        qr_codes = pyzbar.decode(frame)
        if qr_codes:
            print(f"QR Detected: {qr_codes[0].data.decode()}")
            break
    cv2.imshow('Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
EOF
```

### Issue: System stops responding
```bash
# Check system resources
htop  # or top

# Check logs
sudo journalctl -u parking-automation.service --since "1 hour ago"

# Restart service
sudo systemctl restart parking-automation.service
```

### Issue: Browser doesn't have camera permission
The script automatically grants permissions, but if issues persist:
```python
# In setup_browser(), add:
chrome_options.add_argument('--use-fake-device-for-media-stream')
chrome_options.add_argument('--allow-file-access-from-files')
```

## ⚙️ Advanced Configuration

### Multiple Camera Support
If you have multiple parking spots:

```bash
# Copy the script for each camera
cp qr_parking_automation_v2.py spot1_automation.py
cp qr_parking_automation_v2.py spot2_automation.py

# Edit each to use different cameras
# In spot1_automation.py: CAMERA_INDEX = 0
# In spot2_automation.py: CAMERA_INDEX = 1
```

### Adjust QR Detection Sensitivity

In `qr_parking_automation_v2.py`, modify the `detect_qr_code` function:
```python
def detect_qr_code(self, frame):
    # Convert to grayscale for better detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding for better QR detection
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # Detect QR codes
    qr_codes = pyzbar.decode(thresh)
    # ... rest of function
```

### Change Cooldown Period
```python
QR_COOLDOWN = 15  # Increase to 15 seconds between detections
```

### Headless Operation (No Display)
If you want to run without showing windows:
```python
# In setup_browser():
chrome_options.add_argument('--headless')

# Comment out these lines in camera_monitoring_thread():
# cv2.imshow('QR Code Detection - Smart Parking', frame)
# if cv2.waitKey(1) & 0xFF == ord('q'):
```

## 📊 Monitoring and Logs

### View Real-time Logs
```bash
# systemd service logs
sudo journalctl -u parking-automation.service -f

# Or with timestamps
sudo journalctl -u parking-automation.service -f --since "today"
```

### Log File (Alternative)
To save logs to a file, run:
```bash
python3 qr_parking_automation_v2.py >> ~/parking_automation.log 2>&1 &
```

View logs:
```bash
tail -f ~/parking_automation.log
```

## 🛠️ Maintenance

### Update the System
```bash
cd ~/parking_automation
git pull  # If using git
# Or download updated scripts manually

# Restart service
sudo systemctl restart parking-automation.service
```

### Check System Health
```bash
# Check if service is running
systemctl status parking-automation.service

# Check camera
v4l2-ctl --list-devices

# Check Chrome/ChromeDriver
chromium-browser --version
chromedriver --version

# Check Python packages
pip3 list | grep -E "selenium|opencv|pyzbar"
```

## 📝 Common Workflows

### Start/Stop System
```bash
# Start
sudo systemctl start parking-automation.service

# Stop
sudo systemctl stop parking-automation.service

# Restart
sudo systemctl restart parking-automation.service
```

### Testing Without Auto-start
```bash
# Run manually to test
cd ~/parking_automation
python3 qr_parking_automation_v2.py
```

### Debugging Mode
Run with verbose output:
```bash
python3 qr_parking_automation_v2.py 2>&1 | tee debug.log
```

## 🆘 Getting Help

If you're still having issues:

1. **Check all logs:**
   ```bash
   sudo journalctl -u parking-automation.service -n 200
   ```

2. **Test components individually:**
   - Camera: `python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`
   - QR detection: Use test script above
   - Browser: `chromium-browser https://your-site.repl.co`

3. **Common issues checklist:**
   - [ ] Camera is plugged in and detected
   - [ ] ChromeDriver version matches Chromium
   - [ ] Website URL is correct and accessible
   - [ ] Button selector is correct
   - [ ] Internet connection is stable
   - [ ] Camera permissions are granted

## 📦 Complete Dependency List

```bash
# System packages
chromium-browser
chromium-chromedriver
python3
python3-pip
python3-opencv
libzbar0

# Python packages
selenium
pyzbar
Pillow
opencv-python  # If not using system python3-opencv
```

## 🎓 How It Works

1. **Camera Monitor Thread**: Continuously captures frames from camera
2. **QR Detection**: Uses pyzbar library to detect QR codes in real-time
3. **Cooldown Management**: Prevents multiple triggers from same QR code
4. **Browser Automation**: Selenium clicks the button when QR is detected
5. **Website Integration**: Your website's built-in camera handles validation

**Flow:**
```
Camera Feed → QR Detection → Button Click → Website Camera → Validation
     ↓             ↓              ↓              ↓              ↓
  OpenCV      pyzbar       Selenium      Your Website    Your Backend
```

## ✅ Success Indicators

Your system is working correctly if you see:
1. Camera window displaying live feed
2. Browser opening your website automatically
3. Log message: "Scanning for QR codes..."
4. When QR shown: Green box around QR + "QR DETECTED" message
5. Log message: "Successfully clicked button"
6. Website camera opens for scanning
7. Cooldown counter appears (10 seconds)

Happy automating! 🚗🅿️