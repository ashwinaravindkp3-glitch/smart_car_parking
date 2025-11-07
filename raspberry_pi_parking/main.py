#!/usr/bin/env python3
"""
Raspberry Pi Smart Parking System - Main Controller
Integrates cameras, barriers, IR sensors, and MQTT communication
"""

import sys
import time
import signal
import logging
from logging.handlers import RotatingFileHandler

import config
from mqtt_handler import MQTTHandler
from camera_handler import CameraHandler
from barrier_handler import BarrierHandler
from slot_handler import SlotHandler
from display_handler import DisplayHandler


class SmartParkingSystem:
    def __init__(self):
        """Initialize Smart Parking System"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Handlers
        self.mqtt = None
        self.cameras = None
        self.barriers = None
        self.slots = None
        self.display = None

        # System state
        self.running = False

    def setup_logging(self):
        """Configure logging system"""
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.LOG_LEVEL))
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    def on_qr_detected(self, qr_data, camera_type):
        """
        Callback when QR code is detected

        Args:
            qr_data: QR code data string
            camera_type: "entry" or "exit"
        """
        self.logger.info(f"QR Code detected on {camera_type} camera: {qr_data}")

        # Determine barrier type (same as camera type)
        barrier_type = camera_type

        # Open appropriate barrier
        if self.barriers:
            self.barriers.open_barrier(barrier_type, user_id=qr_data)

        # Publish QR detection event
        if self.mqtt:
            self.mqtt.publish_qr_detected(qr_data, camera_type, barrier_type)

    def on_door_command(self, barrier_type, user_id, slot_number, timestamp):
        """
        Callback when door open command received via MQTT

        Args:
            barrier_type: "entry" or "exit"
            user_id: User ID
            slot_number: Assigned slot number
            timestamp: Command timestamp
        """
        self.logger.info(f"Door command received: {barrier_type} for user {user_id}, slot {slot_number}")

        # Open the barrier
        if self.barriers:
            self.barriers.open_barrier(barrier_type, user_id=user_id)

        # Display appropriate message
        if self.display:
            if barrier_type == "entry":
                # Show welcome message with slot number
                self.display.show_welcome(slot_number, user_id)
            elif barrier_type == "exit":
                # Show thank you message
                self.display.show_thank_you()

    def on_slot_state_change(self, slot_states):
        """
        Callback when IR sensor states change

        Args:
            slot_states: List of 20 boolean values (True=occupied, False=available)
        """
        self.logger.info("Slot states changed, publishing to MQTT")

        # Publish to MQTT
        if self.mqtt:
            self.mqtt.publish_slot_status(slot_states)

        # Log occupancy summary
        if self.slots:
            summary = self.slots.get_occupancy_summary()
            self.logger.info(
                f"Occupancy: {summary['occupied']}/{summary['total']} "
                f"({summary['occupancy_rate']:.1f}%)"
            )

    def setup(self):
        """Initialize all system components"""
        self.logger.info("=" * 70)
        self.logger.info("Raspberry Pi Smart Parking System")
        self.logger.info("=" * 70)
        self.logger.info(f"Admin Website: {config.ADMIN_WEBSITE_URL}")
        self.logger.info("=" * 70)

        # Initialize MQTT Handler
        self.logger.info("Setting up MQTT handler...")
        self.mqtt = MQTTHandler(on_door_command_callback=self.on_door_command)
        if not self.mqtt.setup():
            self.logger.error("Failed to setup MQTT handler")
            return False

        # Initialize Display Handler
        self.logger.info("Setting up display handler...")
        self.display = DisplayHandler()
        if not self.display.setup():
            self.logger.error("Failed to setup display handler")
            return False

        # Initialize Barrier Handler
        self.logger.info("Setting up barrier handler...")
        self.barriers = BarrierHandler()
        if not self.barriers.setup():
            self.logger.error("Failed to setup barrier handler")
            return False

        # Initialize Slot Handler
        self.logger.info("Setting up slot handler...")
        self.slots = SlotHandler(on_state_change_callback=self.on_slot_state_change)
        if not self.slots.setup():
            self.logger.error("Failed to setup slot handler")
            return False

        # Initialize Camera Handler
        self.logger.info("Setting up camera handler...")
        self.cameras = CameraHandler(on_qr_detected_callback=self.on_qr_detected)
        if not self.cameras.setup():
            self.logger.error("Failed to setup camera handler")
            return False

        self.logger.info("All components initialized successfully")
        return True

    def start(self):
        """Start all system components"""
        self.logger.info("Starting all system components...")

        # Start barriers (auto-close timer)
        if self.barriers:
            self.barriers.start()

        # Start slot monitoring
        if self.slots:
            self.slots.start()

            # Publish initial slot status
            initial_states = self.slots.get_slot_states()
            if self.mqtt:
                self.mqtt.publish_slot_status(initial_states)

        # Start camera monitoring
        if self.cameras:
            self.cameras.start()

        self.running = True
        self.logger.info("=" * 70)
        self.logger.info("System is RUNNING")
        self.logger.info("=" * 70)
        self.logger.info("Press Ctrl+C to stop")

    def run(self):
        """Main system loop"""
        try:
            while self.running:
                # Main loop - just keep alive
                # All work is done in handler threads
                time.sleep(config.LOOP_DELAY)

                # Periodic status check (every 60 seconds)
                if int(time.time()) % 60 == 0:
                    self.log_system_status()
                    time.sleep(1)  # Prevent multiple logs in same second

        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        finally:
            self.stop()

    def log_system_status(self):
        """Log periodic system status"""
        self.logger.info("--- System Status ---")

        # MQTT status
        if self.mqtt:
            status = "Connected" if self.mqtt.is_connected() else "Disconnected"
            self.logger.info(f"MQTT: {status}")

        # Barrier status
        if self.barriers:
            barrier_status = self.barriers.get_status()
            self.logger.info(f"Entry Barrier: {barrier_status['entry']}")
            self.logger.info(f"Exit Barrier: {barrier_status['exit']}")

        # Slot occupancy
        if self.slots:
            summary = self.slots.get_occupancy_summary()
            available_slots = self.slots.get_available_slots()
            self.logger.info(
                f"Slots: {summary['available']} available, "
                f"{summary['occupied']} occupied "
                f"({summary['occupancy_rate']:.1f}%)"
            )
            if available_slots:
                self.logger.info(f"Available: {available_slots}")

        self.logger.info("--- End Status ---")

    def stop(self):
        """Stop all system components"""
        self.logger.info("Stopping Smart Parking System...")
        self.running = False

        # Cleanup in reverse order
        if self.cameras:
            self.cameras.cleanup()

        if self.slots:
            self.slots.cleanup()

        if self.barriers:
            self.barriers.cleanup()

        if self.display:
            self.display.cleanup()

        if self.mqtt:
            self.mqtt.cleanup()

        self.logger.info("System stopped successfully")


def signal_handler(signum, frame):
    """Handle system signals"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and run system
    system = SmartParkingSystem()

    if not system.setup():
        logging.error("Failed to setup system. Exiting.")
        sys.exit(1)

    system.start()
    system.run()


if __name__ == "__main__":
    main()
