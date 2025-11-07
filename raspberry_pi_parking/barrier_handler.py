"""
Dual Servo Barrier Handler for Raspberry Pi Smart Parking System
Controls entry and exit barriers with auto-close functionality
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

        @staticmethod
        def setmode(mode):
            pass

        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            pass

        @staticmethod
        def output(pin, value):
            pass

        @staticmethod
        def PWM(pin, freq):
            return MockPWM()

        @staticmethod
        def cleanup():
            pass

    class MockPWM:
        def start(self, duty):
            pass

        def ChangeDutyCycle(self, duty):
            pass

        def stop(self):
            pass

    GPIO = MockGPIO()

logger = logging.getLogger(__name__)


class BarrierHandler:
    def __init__(self):
        """Initialize Barrier Handler"""
        self.entry_pwm = None
        self.exit_pwm = None
        self.running = Event()

        # Barrier states
        self.entry_open = False
        self.exit_open = False

        # Auto-close timers
        self.entry_timer = 0
        self.exit_timer = 0

        # Lock for thread safety
        self.lock = Lock()

        # Auto-close thread
        self.timer_thread = None

    def setup(self):
        """Initialize GPIO and servos"""
        try:
            if not config.ENABLE_BARRIERS:
                logger.warning("Barriers disabled in config")
                return True

            # Setup GPIO mode
            GPIO.setmode(GPIO.BCM)

            # Setup entry servo
            logger.info(f"Initializing entry barrier on GPIO {config.SERVO_ENTRY_PIN}...")
            GPIO.setup(config.SERVO_ENTRY_PIN, GPIO.OUT)
            self.entry_pwm = GPIO.PWM(config.SERVO_ENTRY_PIN, 50)  # 50Hz for servo
            self.entry_pwm.start(0)
            self._set_servo_angle(self.entry_pwm, config.BARRIER_CLOSED_ANGLE)
            logger.info("Entry barrier initialized (closed position)")

            # Setup exit servo
            logger.info(f"Initializing exit barrier on GPIO {config.SERVO_EXIT_PIN}...")
            GPIO.setup(config.SERVO_EXIT_PIN, GPIO.OUT)
            self.exit_pwm = GPIO.PWM(config.SERVO_EXIT_PIN, 50)  # 50Hz for servo
            self.exit_pwm.start(0)
            self._set_servo_angle(self.exit_pwm, config.BARRIER_CLOSED_ANGLE)
            logger.info("Exit barrier initialized (closed position)")

            return True

        except Exception as e:
            logger.error(f"Failed to setup barriers: {e}")
            return False

    def start(self):
        """Start auto-close timer thread"""
        if not config.ENABLE_BARRIERS:
            return

        self.running.set()
        self.timer_thread = Thread(target=self._auto_close_handler, daemon=True)
        self.timer_thread.start()
        logger.info("Barrier auto-close handler started")

    def _set_servo_angle(self, pwm, angle):
        """
        Set servo to specific angle

        Args:
            pwm: PWM object
            angle: Angle in degrees (0-180)
        """
        # Convert angle to duty cycle
        # For most servos: 0° = 2.5% duty, 180° = 12.5% duty
        duty_cycle = 2.5 + (angle / 180.0) * 10.0
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.3)  # Give servo time to move
        pwm.ChangeDutyCycle(0)  # Stop sending signal to prevent jitter

    def open_barrier(self, barrier_type, user_id=None):
        """
        Open specified barrier

        Args:
            barrier_type: "entry" or "exit"
            user_id: Optional user ID for logging
        """
        try:
            with self.lock:
                if barrier_type == "entry":
                    logger.info(f"Opening ENTRY barrier (User: {user_id})")
                    self._set_servo_angle(self.entry_pwm, config.BARRIER_OPEN_ANGLE)
                    self.entry_open = True
                    self.entry_timer = time.time()

                elif barrier_type == "exit":
                    logger.info(f"Opening EXIT barrier (User: {user_id})")
                    self._set_servo_angle(self.exit_pwm, config.BARRIER_OPEN_ANGLE)
                    self.exit_open = True
                    self.exit_timer = time.time()

                else:
                    logger.warning(f"Unknown barrier type: {barrier_type}")

        except Exception as e:
            logger.error(f"Error opening {barrier_type} barrier: {e}")

    def close_barrier(self, barrier_type):
        """
        Close specified barrier

        Args:
            barrier_type: "entry" or "exit"
        """
        try:
            with self.lock:
                if barrier_type == "entry":
                    if self.entry_open:
                        logger.info("Closing ENTRY barrier")
                        self._set_servo_angle(self.entry_pwm, config.BARRIER_CLOSED_ANGLE)
                        self.entry_open = False
                        self.entry_timer = 0

                elif barrier_type == "exit":
                    if self.exit_open:
                        logger.info("Closing EXIT barrier")
                        self._set_servo_angle(self.exit_pwm, config.BARRIER_CLOSED_ANGLE)
                        self.exit_open = False
                        self.exit_timer = 0

        except Exception as e:
            logger.error(f"Error closing {barrier_type} barrier: {e}")

    def _auto_close_handler(self):
        """Thread that handles auto-closing of barriers"""
        logger.info("Auto-close handler thread started")

        while self.running.is_set():
            try:
                current_time = time.time()

                # Check entry barrier
                if self.entry_open:
                    if current_time - self.entry_timer > config.BARRIER_OPEN_DURATION:
                        logger.info("Entry barrier auto-close timer expired")
                        self.close_barrier("entry")

                # Check exit barrier
                if self.exit_open:
                    if current_time - self.exit_timer > config.BARRIER_OPEN_DURATION:
                        logger.info("Exit barrier auto-close timer expired")
                        self.close_barrier("exit")

                time.sleep(0.1)  # Check every 100ms

            except Exception as e:
                logger.error(f"Error in auto-close handler: {e}")
                time.sleep(1)

        logger.info("Auto-close handler thread stopped")

    def get_status(self):
        """Get current status of both barriers"""
        with self.lock:
            return {
                "entry": "open" if self.entry_open else "closed",
                "exit": "open" if self.exit_open else "closed"
            }

    def cleanup(self):
        """Clean up GPIO resources"""
        logger.info("Cleaning up barriers...")
        self.running.clear()

        # Wait for timer thread
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=2)

        # Close both barriers
        if config.ENABLE_BARRIERS:
            self.close_barrier("entry")
            self.close_barrier("exit")

            # Stop PWM
            if self.entry_pwm:
                self.entry_pwm.stop()

            if self.exit_pwm:
                self.exit_pwm.stop()

            # Cleanup GPIO
            GPIO.cleanup()
            logger.info("GPIO cleaned up")
