"""
Configuration file for Raspberry Pi Smart Parking System
Update these values according to your hardware setup and network credentials
"""

# ==================== NETWORK CONFIGURATION ====================
WIFI_SSID = "thegooddoctor62"
WIFI_PASSWORD = "qzju6234"

# ==================== MQTT CONFIGURATION ====================
MQTT_BROKER = "344221df652946139079042b380d50c9.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "thegooddoctor62"
MQTT_PASSWORD = "Ashwin@25"
MQTT_USE_TLS = True

# MQTT Topics
MQTT_TOPIC_DOOR_OPEN = "door_open"          # Subscribe: Receive gate commands
MQTT_TOPIC_SLOT_STATUS = "parking/rpi/status"  # Publish: Send slot status
MQTT_TOPIC_QR_DETECTED = "parking/rpi/qr"      # Publish: QR code detections

# ==================== CAMERA CONFIGURATION ====================
# Camera indices (0, 1 for first and second USB cameras)
CAMERA_ENTRY_INDEX = 0      # Camera monitoring entry
CAMERA_EXIT_INDEX = 1       # Camera monitoring exit

# Camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# QR detection cooldown (seconds) - prevent multiple triggers
QR_COOLDOWN_SECONDS = 5

# ==================== SERVO/BARRIER CONFIGURATION ====================
# GPIO pins for servos (BCM numbering)
SERVO_ENTRY_PIN = 18       # GPIO 18 (PWM0) for entry barrier
SERVO_EXIT_PIN = 13        # GPIO 13 (PWM1) for exit barrier

# Servo angles
BARRIER_CLOSED_ANGLE = 0
BARRIER_OPEN_ANGLE = 90

# Barrier open duration (seconds)
BARRIER_OPEN_DURATION = 5

# ==================== IR SENSOR CONFIGURATION ====================
# Number of physical IR sensors
NUM_REAL_SENSORS = 6

# GPIO pins for IR sensors (BCM numbering)
IR_SENSOR_PINS = [17, 27, 22, 23, 24, 25]  # 6 sensors

# Virtual slot mapping (6 real sensors mapped to 20 virtual slots)
# Maps sensor index to slot number
REAL_SLOT_MAPPING = [2, 5, 8, 12, 15, 18]

# Total virtual slots in the system
TOTAL_SLOTS = 20

# IR sensor logic (True if LOW = occupied, False if HIGH = occupied)
IR_ACTIVE_LOW = True

# ==================== I2C LCD DISPLAY CONFIGURATION ====================
# I2C LCD Display settings
ENABLE_DISPLAY = True

# I2C address (common addresses: 0x27, 0x3F)
# Use 'i2cdetect -y 1' command to find your display address
LCD_I2C_ADDRESS = 0x27

# I2C port (1 for Raspberry Pi 2/3/4, 0 for older models)
LCD_I2C_PORT = 1

# LCD expander type ('PCF8574' is most common)
LCD_I2C_EXPANDER = 'PCF8574'

# LCD dimensions
LCD_COLS = 16  # Number of columns (16 or 20)
LCD_ROWS = 2   # Number of rows (2 or 4)

# Message display duration (seconds)
LCD_MESSAGE_DURATION = 5

# ==================== ADMIN WEBSITE ====================
ADMIN_WEBSITE_URL = "https://park-sensei-1-cbenp2ebs2500.replit.app/"

# ==================== LOGGING CONFIGURATION ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "parking_system.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# ==================== SYSTEM SETTINGS ====================
# Main loop delay (seconds)
LOOP_DELAY = 0.01

# Enable/disable features for testing
ENABLE_CAMERAS = True
ENABLE_BARRIERS = True
ENABLE_IR_SENSORS = True
ENABLE_MQTT = True
ENABLE_DISPLAY = True
