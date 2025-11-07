"""
MQTT Network Handler for Raspberry Pi Smart Parking System
Handles all MQTT communication with HiveMQ Cloud broker
"""

import ssl
import json
import logging
import time
from threading import Thread, Event
import paho.mqtt.client as mqtt
import config

logger = logging.getLogger(__name__)


class MQTTHandler:
    def __init__(self, on_door_command_callback=None):
        """
        Initialize MQTT Handler

        Args:
            on_door_command_callback: Function to call when door open command received
                                     Should accept (barrier_type, user_id, slot_number, timestamp)
        """
        self.client = None
        self.connected = Event()
        self.running = Event()
        self.on_door_command_callback = on_door_command_callback

        # Statistics
        self.messages_published = 0
        self.messages_received = 0
        self.last_publish_time = 0

    def setup(self):
        """Initialize MQTT client and connect to broker"""
        try:
            # Create MQTT client
            client_id = f"RaspberryPi-Parking-{int(time.time())}"
            self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

            # Set credentials
            self.client.username_pw_set(config.MQTT_USER, config.MQTT_PASSWORD)

            # Configure TLS/SSL if enabled
            if config.MQTT_USE_TLS:
                self.client.tls_set(cert_reqs=ssl.CERT_NONE)
                self.client.tls_insecure_set(True)

            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            # Connect to broker
            logger.info(f"Connecting to MQTT broker: {config.MQTT_BROKER}:{config.MQTT_PORT}")
            self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)

            # Start network loop in background thread
            self.running.set()
            self.client.loop_start()

            # Wait for connection (with timeout)
            if self.connected.wait(timeout=10):
                logger.info("MQTT connection established successfully")
                return True
            else:
                logger.error("MQTT connection timeout")
                return False

        except Exception as e:
            logger.error(f"Failed to setup MQTT: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.connected.set()

            # Subscribe to door open topic
            self.client.subscribe(config.MQTT_TOPIC_DOOR_OPEN)
            logger.info(f"Subscribed to topic: {config.MQTT_TOPIC_DOOR_OPEN}")
        else:
            logger.error(f"MQTT connection failed with code: {rc}")
            self.connected.clear()

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        logger.warning(f"Disconnected from MQTT broker (code: {rc})")
        self.connected.clear()

        if rc != 0 and self.running.is_set():
            logger.info("Unexpected disconnect, will attempt to reconnect...")

    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')

            logger.info(f"Message received on topic '{topic}': {payload}")
            self.messages_received += 1

            # Handle door open commands
            if topic == config.MQTT_TOPIC_DOOR_OPEN:
                self._handle_door_command(payload)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _handle_door_command(self, payload):
        """
        Handle door open command
        Expected format:
        {
          "action": "open",
          "barrier": "exit",  // or "entry"
          "userId": "USER123",
          "slotNumber": 5,
          "timestamp": "2025-11-07T..."
        }
        """
        try:
            data = json.loads(payload)

            action = data.get('action', '').lower()
            barrier = data.get('barrier', '').lower()
            user_id = data.get('userId', 'Unknown')
            slot_number = data.get('slotNumber', 0)
            timestamp = data.get('timestamp', '')

            if action == 'open':
                logger.info(f"Door open command: barrier={barrier}, user={user_id}, slot={slot_number}")

                # Call the callback if registered
                if self.on_door_command_callback:
                    self.on_door_command_callback(barrier, user_id, slot_number, timestamp)
            else:
                logger.warning(f"Unknown action received: {action}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in door command: {payload}")
        except Exception as e:
            logger.error(f"Error handling door command: {e}")

    def publish_slot_status(self, slot_states):
        """
        Publish parking slot status

        Args:
            slot_states: List of 20 slot statuses (True=occupied, False=available)
        """
        try:
            if not self.connected.is_set():
                logger.warning("Cannot publish: MQTT not connected")
                return False

            # Build JSON payload
            slots_array = []
            for i in range(config.TOTAL_SLOTS):
                slot_number = i + 1
                status = "occupied" if slot_states[i] else "available"
                slots_array.append({
                    "slotNumber": slot_number,
                    "status": status
                })

            payload = {
                "slots": slots_array,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }

            json_payload = json.dumps(payload)

            # Publish
            result = self.client.publish(config.MQTT_TOPIC_SLOT_STATUS, json_payload, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.messages_published += 1
                self.last_publish_time = time.time()
                logger.debug(f"Published slot status: {json_payload[:100]}...")
                return True
            else:
                logger.error(f"Failed to publish slot status: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"Error publishing slot status: {e}")
            return False

    def publish_qr_detected(self, qr_data, camera_type, barrier_type):
        """
        Publish QR code detection event

        Args:
            qr_data: QR code data string
            camera_type: "entry" or "exit"
            barrier_type: "entry" or "exit"
        """
        try:
            if not self.connected.is_set():
                logger.warning("Cannot publish: MQTT not connected")
                return False

            payload = {
                "qrData": qr_data,
                "camera": camera_type,
                "barrier": barrier_type,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }

            json_payload = json.dumps(payload)

            result = self.client.publish(config.MQTT_TOPIC_QR_DETECTED, json_payload, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.messages_published += 1
                logger.info(f"Published QR detection: {qr_data} on {camera_type} camera")
                return True
            else:
                logger.error(f"Failed to publish QR detection: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"Error publishing QR detection: {e}")
            return False

    def is_connected(self):
        """Check if MQTT is connected"""
        return self.connected.is_set()

    def cleanup(self):
        """Clean up MQTT connection"""
        logger.info("Cleaning up MQTT handler...")
        self.running.clear()

        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

        logger.info(f"MQTT Stats - Published: {self.messages_published}, Received: {self.messages_received}")
