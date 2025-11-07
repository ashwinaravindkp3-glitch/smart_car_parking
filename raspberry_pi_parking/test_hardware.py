#!/usr/bin/env python3
"""
Hardware Test Script for Raspberry Pi Smart Parking System
Tests cameras, servos, and IR sensors individually
"""

import sys
import time
import cv2

print("=" * 60)
print("Raspberry Pi Smart Parking - Hardware Test")
print("=" * 60)

# Test 1: Camera Test
print("\n1. Testing Cameras...")
print("-" * 60)

try:
    # Test Entry Camera
    print("Testing Entry Camera (index 0)...")
    cap0 = cv2.VideoCapture(0)
    if cap0.isOpened():
        ret, frame = cap0.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"  ✓ Entry camera OK - Resolution: {w}x{h}")
        else:
            print("  ✗ Entry camera failed to capture frame")
        cap0.release()
    else:
        print("  ✗ Entry camera failed to open")

    # Test Exit Camera
    print("Testing Exit Camera (index 1)...")
    cap1 = cv2.VideoCapture(1)
    if cap1.isOpened():
        ret, frame = cap1.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"  ✓ Exit camera OK - Resolution: {w}x{h}")
        else:
            print("  ✗ Exit camera failed to capture frame")
        cap1.release()
    else:
        print("  ✗ Exit camera failed to open")

except Exception as e:
    print(f"  ✗ Camera test error: {e}")

# Test 2: GPIO Test
print("\n2. Testing GPIO...")
print("-" * 60)

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    print("  ✓ RPi.GPIO imported and initialized")

    # Test Servo Pins
    servo_pins = [18, 13]
    print(f"  Testing servo pins: {servo_pins}")
    for pin in servo_pins:
        GPIO.setup(pin, GPIO.OUT)
        print(f"    ✓ GPIO {pin} configured as output")

    # Test IR Sensor Pins
    ir_pins = [17, 27, 22, 23, 24, 25]
    print(f"  Testing IR sensor pins: {ir_pins}")
    for pin in ir_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        state = GPIO.input(pin)
        print(f"    ✓ GPIO {pin} configured as input - Current state: {state}")

    GPIO.cleanup()
    print("  ✓ GPIO cleanup complete")

except ImportError:
    print("  ⚠ RPi.GPIO not available (not on Raspberry Pi?)")
except Exception as e:
    print(f"  ✗ GPIO test error: {e}")

# Test 3: Servo Test
print("\n3. Testing Servos (Optional)...")
print("-" * 60)

response = input("Do you want to test servos? This will move them! (y/n): ")
if response.lower() == 'y':
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)

        entry_pin = 18
        exit_pin = 13

        GPIO.setup(entry_pin, GPIO.OUT)
        GPIO.setup(exit_pin, GPIO.OUT)

        entry_pwm = GPIO.PWM(entry_pin, 50)
        exit_pwm = GPIO.PWM(exit_pin, 50)

        print("  Moving servos to 0° (closed)...")
        entry_pwm.start(2.5)
        exit_pwm.start(2.5)
        time.sleep(1)

        print("  Moving servos to 90° (open)...")
        entry_pwm.ChangeDutyCycle(7.5)
        exit_pwm.ChangeDutyCycle(7.5)
        time.sleep(1)

        print("  Moving servos back to 0° (closed)...")
        entry_pwm.ChangeDutyCycle(2.5)
        exit_pwm.ChangeDutyCycle(2.5)
        time.sleep(1)

        entry_pwm.stop()
        exit_pwm.stop()
        GPIO.cleanup()

        print("  ✓ Servo test complete")

    except Exception as e:
        print(f"  ✗ Servo test error: {e}")
else:
    print("  Skipped servo test")

# Test 4: QR Detection
print("\n4. Testing QR Detection...")
print("-" * 60)

try:
    from pyzbar import pyzbar
    print("  ✓ pyzbar imported successfully")

    response = input("Do you want to test live QR detection? (y/n): ")
    if response.lower() == 'y':
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("  Camera opened. Show a QR code... (press 'q' to quit)")
            qr_found = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                qr_codes = pyzbar.decode(frame)
                if qr_codes:
                    for qr in qr_codes:
                        data = qr.data.decode('utf-8')
                        print(f"  ✓ QR Code detected: {data}")
                        qr_found = True

                cv2.imshow('QR Test (press q to quit)', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

            if qr_found:
                print("  ✓ QR detection working!")
            else:
                print("  ⚠ No QR code detected during test")
        else:
            print("  ✗ Failed to open camera for QR test")
    else:
        print("  Skipped live QR test")

except ImportError:
    print("  ✗ pyzbar not installed")
    print("    Install: sudo apt-get install libzbar0 && pip3 install pyzbar")
except Exception as e:
    print(f"  ✗ QR test error: {e}")

# Test 5: MQTT
print("\n5. Testing MQTT...")
print("-" * 60)

try:
    import paho.mqtt.client as mqtt
    import ssl

    print("  ✓ paho-mqtt imported successfully")

    response = input("Do you want to test MQTT connection? (y/n): ")
    if response.lower() == 'y':
        broker = "344221df652946139079042b380d50c9.s1.eu.hivemq.cloud"
        port = 8883
        user = "thegooddoctor62"
        password = "Ashwin@25"

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("  ✓ MQTT connected successfully!")
                client.disconnect()
            else:
                print(f"  ✗ MQTT connection failed with code: {rc}")

        client = mqtt.Client("TestClient")
        client.username_pw_set(user, password)
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)
        client.on_connect = on_connect

        print(f"  Connecting to {broker}:{port}...")
        client.connect(broker, port, 60)
        client.loop_start()
        time.sleep(3)
        client.loop_stop()
    else:
        print("  Skipped MQTT test")

except ImportError:
    print("  ✗ paho-mqtt not installed")
    print("    Install: pip3 install paho-mqtt")
except Exception as e:
    print(f"  ✗ MQTT test error: {e}")

print("\n" + "=" * 60)
print("Hardware test complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Fix any failed tests above")
print("2. Update config.py with your settings")
print("3. Run: sudo python3 main.py")
print("")
