# Smart Parking QR Camera Automation System

Automatically detect QR codes and trigger your website's camera for smart parking validation.

## 📖 Quick Start

### 1. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y chromium-chromedriver chromium-browser python3-opencv libzbar0
pip3 install selenium pyzbar pillow
```

### 2. Test Your System
```bash
python3 test_system.py
```
This will verify all components are working correctly.

### 3. Find Your Button Selector
```bash
python3 find_button_selector.py
```
Enter your website URL and get the correct selector for your "Open Camera" button.

### 4. Configure Main Script
Edit `qr_parking_automation_v2.py`:
```python
WEBSITE_URL = "https://your-replit-site.repl.co"  # Your website
CAMERA_BUTTON_SELECTOR = "button#openCamera"      # From step 3
```

### 5. Run the System
```bash
python3 qr_parking_automation_v2.py
```

## 📁 Files Included

| File | Purpose |
|------|---------|
| `qr_parking_automation_v2.py` | Main automation script |
| `find_button_selector.py` | Helper to find button CSS selector |
| `test_system.py` | Diagnostic tests for all components |
| `INSTALLATION_GUIDE.md` | Detailed setup and troubleshooting |

## 🎯 How It Works

```
┌─────────────┐
│   Camera    │  Monitors for QR codes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ QR Detected │  pyzbar detects QR in frame
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Click Button│  Selenium clicks "Open Camera" on website
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Website   │  Website scans QR and validates user
└─────────────┘
```

## ⚙️ Configuration Options

In `qr_parking_automation_v2.py`:

```python
# Website configuration
WEBSITE_URL = "https://your-site.repl.co"
CAMERA_BUTTON_SELECTOR = "button#openCamera"

# Camera settings
CAMERA_INDEX = 0  # 0 = first camera, 1 = second, etc.

# Detection settings
QR_COOLDOWN = 10  # Seconds between QR detections
```

## 🔧 Common Selectors

Based on your HTML button:

| HTML | Selector |
|------|----------|
| `<button id="openCamera">` | `button#openCamera` |
| `<button class="camera-btn">` | `button.camera-btn` |
| `<button name="camera">` | `button[name="camera"]` |
| Text "Open Camera" | `//button[contains(text(), 'Open Camera')]` |

## 🚀 Auto-Start on Boot

```bash
sudo systemctl enable parking-automation.service
sudo systemctl start parking-automation.service
```

See `INSTALLATION_GUIDE.md` for detailed setup.

## 📊 Monitoring

View real-time logs:
```bash
sudo journalctl -u parking-automation.service -f
```

## 🐛 Troubleshooting

### Camera not detected
```bash
ls /dev/video*  # Check if camera is connected
```

### Button not clicking
```bash
python3 find_button_selector.py  # Verify selector
```

### See detailed logs
```bash
python3 qr_parking_automation_v2.py  # Run manually to see output
```

For more troubleshooting, see `INSTALLATION_GUIDE.md`.

## 💡 Tips

1. **Better QR Detection**: Ensure good lighting and QR code is 5-10cm from camera
2. **Multiple Cameras**: Run multiple instances with different `CAMERA_INDEX`
3. **Adjust Cooldown**: Increase `QR_COOLDOWN` if processing same QR multiple times
4. **Test First**: Always run `test_system.py` before deploying

## 📋 Requirements

- Raspberry Pi 3B+ or newer
- USB Camera or Pi Camera Module
- Chromium browser & ChromeDriver
- Python 3.7+
- Internet connection

## 🆘 Support

1. Run diagnostic test: `python3 test_system.py`
2. Check detailed guide: `INSTALLATION_GUIDE.md`
3. View logs: `sudo journalctl -u parking-automation.service -n 100`

## 📝 Workflow

### Development/Testing
```bash
python3 qr_parking_automation_v2.py  # Run manually
```

### Production
```bash
sudo systemctl start parking-automation.service  # Run as service
```

---

**Note**: You don't need YOLO for QR detection. The `pyzbar` library is specifically designed for barcode/QR code detection and is more accurate and efficient for this use case than YOLO would be.

Happy automating! 🚗🅿️
