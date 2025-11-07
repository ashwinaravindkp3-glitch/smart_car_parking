"""
IR Sensor Slot Monitoring Handler for Raspberry Pi Smart Parking System
Monitors 6 physical IR sensors and maps them to 20 virtual slots
"""

import time
import logging
from threading import Thread, Event, Lock
import config

# Import RPi.GPIO for Raspberry Pi
try:
    import RPi.GPIO as GPIO
except ImportError:
    # Fallback for testing on non-RPi systems
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("RPi.GPIO not available, using mock GPIO")

    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"
        PUD_UP = "PUD_UP"
        HIGH = 1
        LOW = 0

        @staticmethod
        def setmode(mode):
            pass

        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            pass

        @staticmethod
        def input(pin):
            return MockGPIO.HIGH

        @staticmethod
        def cleanup():
            pass

    GPIO = MockGPIO()

logger = logging.getLogger(__name__)


class SlotHandler:
    def __init__(self, on_state_change_callback=None):
        """
        Initialize Slot Handler

        Args:
            on_state_change_callback: Function to call when slot states change
                                     Should accept (slot_states) - list of 20 booleans
        """
        self.running = Event()
        self.on_state_change_callback = on_state_change_callback

        # Real sensor states (6 sensors)
        self.real_slot_states = [False] * config.NUM_REAL_SENSORS

        # Virtual slot states (20 slots)
        self.virtual_slot_states = [True] * config.TOTAL_SLOTS  # Default all occupied

        # Lock for thread safety
        self.lock = Lock()

        # Monitoring thread
        self.monitor_thread = None

    def setup(self):
        """Initialize GPIO pins for IR sensors"""
        try:
            if not config.ENABLE_IR_SENSORS:
                logger.warning("IR sensors disabled in config")
                return True

            # Setup GPIO mode
            GPIO.setmode(GPIO.BCM)

            # Setup IR sensor pins
            logger.info(f"Initializing {config.NUM_REAL_SENSORS} IR sensors...")
            for i, pin in enumerate(config.IR_SENSOR_PINS):
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                logger.debug(f"  Sensor {i+1} on GPIO {pin}")

            # Read initial states
            for i in range(config.NUM_REAL_SENSORS):
                pin = config.IR_SENSOR_PINS[i]
                pin_state = GPIO.input(pin)

                # Determine if occupied based on config
                if config.IR_ACTIVE_LOW:
                    self.real_slot_states[i] = (pin_state == GPIO.LOW)
                else:
                    self.real_slot_states[i] = (pin_state == GPIO.HIGH)

            logger.info("IR sensors initialized successfully")
            logger.info(f"Initial sensor states: {self.real_slot_states}")

            # Update virtual slots
            self._update_virtual_slots()

            return True

        except Exception as e:
            logger.error(f"Failed to setup IR sensors: {e}")
            return False

    def start(self):
        """Start slot monitoring thread"""
        if not config.ENABLE_IR_SENSORS:
            return

        self.running.set()
        self.monitor_thread = Thread(target=self._monitor_sensors, daemon=True)
        self.monitor_thread.start()
        logger.info("Slot monitoring thread started")

    def _monitor_sensors(self):
        """Thread that continuously monitors IR sensors"""
        logger.info("Slot monitoring loop started")

        while self.running.is_set():
            try:
                state_changed = False

                # Read all sensors
                with self.lock:
                    for i in range(config.NUM_REAL_SENSORS):
                        pin = config.IR_SENSOR_PINS[i]
                        pin_state = GPIO.input(pin)

                        # Determine if occupied
                        if config.IR_ACTIVE_LOW:
                            is_occupied = (pin_state == GPIO.LOW)
                        else:
                            is_occupied = (pin_state == GPIO.HIGH)

                        # Check if state changed
                        if is_occupied != self.real_slot_states[i]:
                            old_state = "Occupied" if self.real_slot_states[i] else "Available"
                            new_state = "Occupied" if is_occupied else "Available"

                            slot_number = config.REAL_SLOT_MAPPING[i]
                            logger.info(f"Slot {slot_number} changed: {old_state} → {new_state}")

                            self.real_slot_states[i] = is_occupied
                            state_changed = True

                # If any state changed, update virtual slots and notify
                if state_changed:
                    self._update_virtual_slots()

                    # Call callback
                    if self.on_state_change_callback:
                        self.on_state_change_callback(self.virtual_slot_states.copy())

                # Small delay
                time.sleep(0.1)  # Check every 100ms

            except Exception as e:
                logger.error(f"Error in slot monitoring: {e}")
                time.sleep(1)

        logger.info("Slot monitoring loop stopped")

    def _update_virtual_slots(self):
        """Map real sensor states to virtual 20-slot array"""
        with self.lock:
            # Reset all to occupied (default for unmapped slots)
            self.virtual_slot_states = [True] * config.TOTAL_SLOTS

            # Map real sensors to their designated slots
            for i in range(config.NUM_REAL_SENSORS):
                slot_number = config.REAL_SLOT_MAPPING[i]
                slot_index = slot_number - 1  # Convert to 0-indexed

                if 0 <= slot_index < config.TOTAL_SLOTS:
                    self.virtual_slot_states[slot_index] = self.real_slot_states[i]

    def get_slot_states(self):
        """Get current virtual slot states (20 slots)"""
        with self.lock:
            return self.virtual_slot_states.copy()

    def get_real_sensor_states(self):
        """Get current real sensor states (6 sensors)"""
        with self.lock:
            return self.real_slot_states.copy()

    def get_available_slots(self):
        """Get list of available slot numbers"""
        with self.lock:
            available = []
            for i in range(config.TOTAL_SLOTS):
                if not self.virtual_slot_states[i]:  # False = available
                    available.append(i + 1)
            return available

    def get_occupancy_summary(self):
        """Get occupancy statistics"""
        with self.lock:
            occupied_count = sum(self.virtual_slot_states)
            available_count = config.TOTAL_SLOTS - occupied_count

            return {
                "total": config.TOTAL_SLOTS,
                "occupied": occupied_count,
                "available": available_count,
                "occupancy_rate": (occupied_count / config.TOTAL_SLOTS) * 100
            }

    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up slot handler...")
        self.running.clear()

        # Wait for monitor thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)

        # Note: GPIO cleanup is handled by BarrierHandler to avoid conflicts
        logger.info("Slot handler cleanup complete")
