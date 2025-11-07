# Raspberry Pi Smart Parking System

Complete IoT-based smart parking solution using Raspberry Pi with dual cameras, dual barriers, IR sensors, and MQTT cloud communication.

## 🚀 Features

- **Dual Camera QR Detection**: Entry and exit cameras for automated vehicle identification
- **Dual Servo Barriers**: Independent control of entry and exit gates with auto-close
- **6 IR Sensors**: Real-time parking slot occupancy monitoring (mapped to 20 virtual slots)
- **MQTT Integration**: Cloud-based communication via HiveMQ
- **Real-time Updates**: Instant slot status publishing
- **Remote Control**: Open barriers via MQTT commands
- **Modular Architecture**: Clean, maintainable Python code

## 📦 Hardware Requirements

### Raspberry Pi
- Raspberry Pi 4 Model B (recommended) or Raspberry Pi 3B+
- 16GB+ microSD card
- 5V 3A power supply

### Cameras
- 2x USB Cameras or 2x Raspberry Pi Camera Modules
  - Camera 0: Entry monitoring
  - Camera 1: Exit monitoring

### Servos
- 2x SG90 or MG90S Servo Motors (9g)
  - Servo 1: Entry barrier (GPIO 18)
  - Servo 2: Exit barrier (GPIO 13)

### IR Sensors
- 6x IR Proximity Sensors (obstacle detection)
  - Recommended: HC-SR04 or similar
  - Connected to GPIO pins: 17, 27, 22, 23, 24, 25

### Additional Components
- Breadboard or PCB for connections
- Jumper wires
- External 5V power supply for servos (recommended)

## 🔌 Hardware Wiring

### GPIO Pin Mapping (BCM Numbering)

```
Component           | GPIO Pin | Physical Pin
--------------------|----------|-------------
Entry Barrier Servo | GPIO 18  | Pin 12
Exit Barrier Servo  | GPIO 13  | Pin 33
IR Sensor 1         | GPIO 17  | Pin 11
IR Sensor 2         | GPIO 27  | Pin 13
IR Sensor 3         | GPIO 22  | Pin 15
IR Sensor 4         | GPIO 23  | Pin 16
IR Sensor 5         | GPIO 24  | Pin 18
IR Sensor 6         | GPIO 25  | Pin 22
```

### Servo Wiring

```
Servo (Entry/Exit)
├── Brown/Black  → GND
├── Red          → 5V (external power recommended)
└── Orange/Yellow→ GPIO 18/13
```

### IR Sensor Wiring

```
IR Sensor
├── VCC → 5V
├── GND → GND
└── OUT → GPIO Pin (see table above)
```

## 📥 Installation

### 1. Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install System Dependencies

```bash
# Python and pip
sudo apt-get install -y python3-pip python3-dev

# OpenCV dependencies
sudo apt-get install -y libopencv-dev python3-opencv

# ZBar for QR detection
sudo apt-get install -y libzbar0 libzbar-dev

# GPIO support
sudo apt-get install -y python3-rpi.gpio

# Camera support
sudo apt-get install -y v4l-utils
```

### 3. Clone Repository

```bash
cd ~
git clone <your-repository-url>
cd raspberry_pi_parking
```

### 4. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 5. Configure System

Edit `config.py` and update:

```python
# MQTT Credentials (already configured for HiveMQ)
MQTT_BROKER = "344221df652946139079042b380d50c9.s1.eu.hivemq.cloud"
MQTT_USER = "thegooddoctor62"
MQTT_PASSWORD = "Ashwin@25"

# Verify camera indices
CAMERA_ENTRY_INDEX = 0
CAMERA_EXIT_INDEX = 1

# Verify GPIO pins match your wiring
SERVO_ENTRY_PIN = 18
SERVO_EXIT_PIN = 13
IR_SENSOR_PINS = [17, 27, 22, 23, 24, 25]

# Virtual slot mapping (which real sensors map to which slot numbers)
REAL_SLOT_MAPPING = [2, 5, 8, 12, 15, 18]
```

### 6. Test Cameras

```bash
# List connected cameras
ls /dev/video*

# Test entry camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Entry camera OK' if cap.isOpened() else 'Failed')"

# Test exit camera
python3 -c "import cv2; cap = cv2.VideoCapture(1); print('Exit camera OK' if cap.isOpened() else 'Failed')"
```

## 🎮 Usage

### Run Manually

```bash
sudo python3 main.py
```

### Run as System Service

Create systemd service file:

```bash
sudo nano /etc/systemd/system/parking.service
```

Add this content:

```ini
[Unit]
Description=Raspberry Pi Smart Parking System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/raspberry_pi_parking
ExecStart=/usr/bin/python3 /home/pi/raspberry_pi_parking/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable parking.service
sudo systemctl start parking.service
```

### Monitor Service

```bash
# Check status
sudo systemctl status parking.service

# View logs
sudo journalctl -u parking.service -f

# Restart service
sudo systemctl restart parking.service
```

## 📡 MQTT Topics

### Subscribe (Receive Commands)

**Topic:** `door_open`

**Payload Format:**
```json
{
  "action": "open",
  "barrier": "entry",
  "userId": "USER123",
  "slotNumber": 5,
  "timestamp": "2025-11-07T10:30:00"
}
```

**Barrier values:** `"entry"` or `"exit"`

### Publish (Send Data)

**Topic:** `parking/rpi/status`

**Payload Format:**
```json
{
  "slots": [
    {"slotNumber": 1, "status": "occupied"},
    {"slotNumber": 2, "status": "available"},
    ...
    {"slotNumber": 20, "status": "occupied"}
  ],
  "timestamp": "2025-11-07T10:30:00"
}
```

**Topic:** `parking/rpi/qr`

**Payload Format:**
```json
{
  "qrData": "USER123",
  "camera": "entry",
  "barrier": "entry",
  "timestamp": "2025-11-07T10:30:00"
}
```

## 🌐 Integration with Admin Website

Admin Dashboard: https://park-sensei-1-cbenp2ebs2500.replit.app/

The website can:
- Send barrier open commands via MQTT
- Receive real-time slot status updates
- Display parking availability
- Track QR code scans

## 🗂️ Project Structure

```
raspberry_pi_parking/
├── main.py              # Main controller
├── config.py            # Configuration file
├── mqtt_handler.py      # MQTT communication
├── camera_handler.py    # Dual camera QR detection
├── barrier_handler.py   # Dual servo control
├── slot_handler.py      # IR sensor monitoring
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── parking_system.log  # Log file (auto-generated)
```

## 🔧 Configuration Options

### Slot Mapping

The system uses **6 physical sensors** mapped to **20 virtual slots**:

```python
REAL_SLOT_MAPPING = [2, 5, 8, 12, 15, 18]
```

This means:
- Sensor 0 (GPIO 17) → Slot 2
- Sensor 1 (GPIO 27) → Slot 5
- Sensor 2 (GPIO 22) → Slot 8
- Sensor 3 (GPIO 23) → Slot 12
- Sensor 4 (GPIO 24) → Slot 15
- Sensor 5 (GPIO 25) → Slot 18

Unmapped slots (1, 3, 4, 6, 7, 9, 10, 11, 13, 14, 16, 17, 19, 20) default to "occupied".

### Barrier Timing

```python
BARRIER_OPEN_DURATION = 5  # Seconds
```

Barriers automatically close after 5 seconds.

### QR Cooldown

```python
QR_COOLDOWN_SECONDS = 5  # Seconds
```

Prevents duplicate QR triggers within 5 seconds.

## 📊 Monitoring

### View Real-time Logs

```bash
# Systemd service logs
sudo journalctl -u parking.service -f

# Application log file
tail -f parking_system.log
```

### Log Levels

Change in `config.py`:

```python
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🐛 Troubleshooting

### Cameras Not Detected

```bash
# Check camera devices
ls -l /dev/video*

# Check permissions
sudo usermod -a -G video pi

# Enable camera interface (for Pi Camera)
sudo raspi-config
# → Interface Options → Camera → Enable
```

### GPIO Permission Denied

```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Or run with sudo
sudo python3 main.py
```

### MQTT Connection Failed

- Verify internet connection
- Check MQTT credentials in `config.py`
- Test broker connectivity:

```bash
pip3 install paho-mqtt
python3 -c "import paho.mqtt.client as mqtt; print('MQTT library OK')"
```

### IR Sensors Always Occupied/Available

- Check sensor wiring (VCC, GND, OUT)
- Verify `IR_ACTIVE_LOW` setting in config
- Test sensor manually:

```bash
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN); print(GPIO.input(17))"
```

### Servos Not Moving

- Check servo power supply (servos need 5V, may need external power)
- Verify GPIO pins (18 and 13)
- Test servo manually:

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(7.5)  # Center position
time.sleep(2)
pwm.stop()
GPIO.cleanup()
```

## 🔒 Security Notes

- Change default MQTT credentials in production
- Use strong WiFi password
- Keep system updated: `sudo apt-get update && sudo apt-get upgrade`
- Consider firewall rules for network security

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues and questions:
- Check logs: `parking_system.log`
- Review troubleshooting section
- Open GitHub issue

---

**Built with ❤️ for smart parking automation**
