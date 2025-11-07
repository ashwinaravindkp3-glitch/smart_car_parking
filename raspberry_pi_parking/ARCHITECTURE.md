# System Architecture

## Overview

The Raspberry Pi Smart Parking System is a modular, event-driven IoT solution that integrates multiple hardware components with cloud-based MQTT communication.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 4                            │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Main Controller (main.py)                  │ │
│  │         Orchestrates all system components              │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │             │
│    ┌────▼────┐       ┌─────▼─────┐     ┌─────▼──────┐     │
│    │ Camera  │       │ Barrier   │     │   Slot     │     │
│    │ Handler │       │ Handler   │     │  Handler   │     │
│    └────┬────┘       └─────┬─────┘     └─────┬──────┘     │
│         │                  │                  │             │
│    ┌────▼────┐       ┌─────▼─────┐     ┌─────▼──────┐     │
│    │USB Cam 0│       │Servo GPIO │     │IR Sensors  │     │
│    │USB Cam 1│       │  18 & 13  │     │GPIO 17-25  │     │
│    └─────────┘       └───────────┘     └────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           MQTT Handler (mqtt_handler.py)                │ │
│  │      Manages cloud communication with HiveMQ            │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Internet   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────────────────────────┐
                    │   HiveMQ Cloud MQTT Broker       │
                    │  (TLS/SSL Encrypted)             │
                    └──────┬───────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
        ┌───────▼────────┐    ┌──────▼──────────┐
        │  Admin Website │    │  Mobile App     │
        │   (Replit)     │    │  (Future)       │
        └────────────────┘    └─────────────────┘
```

## Data Flow

### 1. QR Code Detection Flow

```
Camera Captures Frame
    ↓
pyzbar Detects QR Code
    ↓
camera_handler.py triggers callback
    ↓
main.py receives QR data
    ↓
┌───────────────┴────────────────┐
│                                │
▼                                ▼
Publish to MQTT                Open Barrier
(parking/rpi/qr)              (entry/exit)
    ↓                              ↓
Admin Website                Auto-close after 5s
receives event
```

### 2. Slot Status Update Flow

```
IR Sensor State Changes
    ↓
slot_handler.py detects change
    ↓
Update virtual slot states (6→20 mapping)
    ↓
Trigger callback to main.py
    ↓
Publish to MQTT (parking/rpi/status)
    ↓
Admin Website updates dashboard
```

### 3. Remote Barrier Control Flow

```
User clicks "Open" on Admin Website
    ↓
Website publishes to MQTT (door_open)
    ↓
HiveMQ Cloud Broker routes message
    ↓
Raspberry Pi MQTT client receives
    ↓
mqtt_handler.py parses JSON
    ↓
Triggers door_command callback
    ↓
main.py calls barrier_handler
    ↓
Servo opens appropriate barrier
    ↓
Auto-close after 5 seconds
```

## Module Responsibilities

### main.py
- System initialization and coordination
- Event routing between modules
- Periodic status logging
- Signal handling (Ctrl+C, shutdown)

### config.py
- Centralized configuration
- Hardware pin mappings
- MQTT credentials
- Timing parameters

### mqtt_handler.py
**Responsibilities:**
- MQTT connection management
- TLS/SSL encryption
- Message publishing (slot status, QR events)
- Message subscription (door commands)
- Auto-reconnect logic

**Topics:**
- Subscribe: `door_open`
- Publish: `parking/rpi/status`, `parking/rpi/qr`

### camera_handler.py
**Responsibilities:**
- Manage 2 USB cameras (entry/exit)
- Continuous QR code detection
- Cooldown management (prevent duplicates)
- Thread-safe camera access

**Threading:**
- 2 threads (one per camera)
- Non-blocking operation
- ~30 FPS frame processing

### barrier_handler.py
**Responsibilities:**
- Control 2 servo motors (entry/exit)
- PWM signal generation
- Auto-close timer management
- Thread-safe barrier control

**Threading:**
- 1 auto-close timer thread
- Checks both barriers every 100ms

### slot_handler.py
**Responsibilities:**
- Monitor 6 IR sensors
- Map to 20 virtual slots
- Detect state changes
- Publish updates via callback

**Threading:**
- 1 monitoring thread
- Polls sensors every 100ms
- Only publishes on state change

## Hardware Interfaces

### GPIO Pins (BCM Numbering)

| Component | GPIO | Physical Pin | Type |
|-----------|------|--------------|------|
| Entry Servo | 18 | 12 | PWM Output |
| Exit Servo | 13 | 33 | PWM Output |
| IR Sensor 1 | 17 | 11 | Digital Input |
| IR Sensor 2 | 27 | 13 | Digital Input |
| IR Sensor 3 | 22 | 15 | Digital Input |
| IR Sensor 4 | 23 | 16 | Digital Input |
| IR Sensor 5 | 24 | 18 | Digital Input |
| IR Sensor 6 | 25 | 22 | Digital Input |

### Virtual Slot Mapping

**Physical Sensors → Virtual Slots:**

```python
REAL_SLOT_MAPPING = [2, 5, 8, 12, 15, 18]

Sensor Index → Slot Number
     0       →      2
     1       →      5
     2       →      8
     3       →     12
     4       →     15
     5       →     18
```

**Unmapped Slots:** 1, 3, 4, 6, 7, 9, 10, 11, 13, 14, 16, 17, 19, 20
- These always report as "occupied" (for demo purposes)

**Why 6→20 mapping?**
- Demo requires 20 slots for presentation
- Only 6 physical sensors available
- Unmapped slots create realistic "partially monitored" scenario

## Threading Model

The system uses a **multi-threaded event-driven architecture**:

```
Main Thread
 ├─ System initialization
 ├─ Event handling
 └─ Status logging

Camera Thread 1 (Entry)
 └─ QR detection → Callback

Camera Thread 2 (Exit)
 └─ QR detection → Callback

Barrier Timer Thread
 └─ Auto-close monitoring

Slot Monitor Thread
 └─ IR sensor polling → Callback

MQTT Network Thread (paho-mqtt internal)
 └─ Message handling → Callback
```

**Thread Safety:**
- All handlers use `threading.Lock` for shared state
- Callbacks are thread-safe
- No blocking operations in main thread

## MQTT Message Formats

### Incoming: Door Open Command

**Topic:** `door_open`

```json
{
  "action": "open",
  "barrier": "entry",
  "userId": "USER123",
  "slotNumber": 5,
  "timestamp": "2025-11-07T10:30:00.000Z"
}
```

### Outgoing: Slot Status

**Topic:** `parking/rpi/status`

```json
{
  "slots": [
    {"slotNumber": 1, "status": "occupied"},
    {"slotNumber": 2, "status": "available"},
    ...
    {"slotNumber": 20, "status": "occupied"}
  ],
  "timestamp": "2025-11-07T10:30:00.000Z"
}
```

### Outgoing: QR Detection

**Topic:** `parking/rpi/qr`

```json
{
  "qrData": "USER123",
  "camera": "entry",
  "barrier": "entry",
  "timestamp": "2025-11-07T10:30:00.000Z"
}
```

## Error Handling

### Connection Resilience
- MQTT: Auto-reconnect every 5 seconds
- Cameras: Graceful frame skip on read failure
- GPIO: Mock implementation for non-RPi testing

### Logging
- **File:** `parking_system.log` (10MB rotating, 5 backups)
- **Console:** Real-time output
- **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

### Graceful Shutdown
1. Catch SIGINT/SIGTERM
2. Stop all threads
3. Release cameras
4. Close barriers
5. Cleanup GPIO
6. Disconnect MQTT

## Performance Characteristics

- **Camera FPS:** ~30 FPS per camera
- **QR Detection Latency:** <100ms
- **Barrier Response Time:** <500ms (from MQTT to open)
- **Slot Update Latency:** <200ms (sensor change to MQTT publish)
- **CPU Usage:** ~15-25% (Raspberry Pi 4)
- **Memory Usage:** ~150-200MB
- **Network:** <1 KB/s (status updates only on change)

## Security Considerations

### Current Implementation
- MQTT over TLS (port 8883)
- Certificate validation disabled (insecure mode)
- Credentials in config file

### Production Recommendations
1. Enable proper TLS certificate validation
2. Move credentials to environment variables
3. Implement MQTT ACLs on broker
4. Add authentication for QR codes
5. Encrypt QR data payloads
6. Rate limiting on MQTT publishes
7. Firewall rules for Raspberry Pi

## Future Enhancements

1. **License Plate Recognition** - Add ALPR capability
2. **Payment Integration** - Connect to payment gateways
3. **Mobile App** - Native iOS/Android control
4. **Multiple Lanes** - Support for larger parking lots
5. **Analytics Dashboard** - Usage patterns, peak times
6. **Backup Power** - UPS integration for power failures
7. **Edge AI** - On-device vehicle classification
8. **Database Integration** - Local SQLite for offline operation

## Testing Strategy

### Unit Tests
- Mock GPIO for non-RPi environments
- Test each handler independently
- Verify MQTT message formats

### Integration Tests
- End-to-end QR→Barrier→MQTT flow
- Concurrent camera operation
- Slot state propagation

### Hardware Tests
- Servo angle accuracy
- IR sensor reliability
- Camera resolution/FPS
- WiFi stability under load

## Deployment Options

### Development
```bash
python3 main.py
```

### Production (systemd)
```bash
sudo systemctl start parking.service
```

### Docker (Future)
```dockerfile
FROM balenalib/raspberry-pi-python:3.9
# ... containerized deployment
```

---

**Version:** 1.0.0
**Last Updated:** 2025-11-07
**Platform:** Raspberry Pi 4 Model B / Raspberry Pi OS
