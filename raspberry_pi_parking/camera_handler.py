"""
Dual Camera QR Code Detection Handler for Raspberry Pi Smart Parking System
Monitors entry and exit cameras for QR codes
"""

import cv2
import time
import logging
from threading import Thread, Event, Lock
from pyzbar import pyzbar
import config

logger = logging.getLogger(__name__)


class CameraHandler:
    def __init__(self, on_qr_detected_callback=None):
        """
        Initialize Camera Handler

        Args:
            on_qr_detected_callback: Function to call when QR detected
                                    Should accept (qr_data, camera_type)
        """
        self.entry_camera = None
        self.exit_camera = None
        self.running = Event()
        self.on_qr_detected_callback = on_qr_detected_callback

        # Cooldown tracking
        self.last_qr_times = {
            'entry': 0,
            'exit': 0
        }
        self.cooldown_lock = Lock()

        # Threading
        self.entry_thread = None
        self.exit_thread = None

    def setup(self):
        """Initialize both cameras"""
        try:
            if not config.ENABLE_CAMERAS:
                logger.warning("Cameras disabled in config")
                return True

            # Initialize entry camera
            logger.info(f"Initializing entry camera (index {config.CAMERA_ENTRY_INDEX})...")
            self.entry_camera = cv2.VideoCapture(config.CAMERA_ENTRY_INDEX)

            if not self.entry_camera.isOpened():
                logger.error("Failed to open entry camera")
                return False

            self.entry_camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.entry_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            self.entry_camera.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)

            logger.info("Entry camera initialized successfully")

            # Initialize exit camera
            logger.info(f"Initializing exit camera (index {config.CAMERA_EXIT_INDEX})...")
            self.exit_camera = cv2.VideoCapture(config.CAMERA_EXIT_INDEX)

            if not self.exit_camera.isOpened():
                logger.error("Failed to open exit camera")
                self.entry_camera.release()
                return False

            self.exit_camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.exit_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            self.exit_camera.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)

            logger.info("Exit camera initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup cameras: {e}")
            return False

    def start(self):
        """Start camera monitoring threads"""
        if not config.ENABLE_CAMERAS:
            logger.info("Camera monitoring disabled")
            return

        self.running.set()

        # Start entry camera thread
        self.entry_thread = Thread(target=self._monitor_camera, args=('entry', self.entry_camera), daemon=True)
        self.entry_thread.start()
        logger.info("Entry camera monitoring thread started")

        # Start exit camera thread
        self.exit_thread = Thread(target=self._monitor_camera, args=('exit', self.exit_camera), daemon=True)
        self.exit_thread.start()
        logger.info("Exit camera monitoring thread started")

    def _monitor_camera(self, camera_type, camera):
        """
        Monitor a camera for QR codes

        Args:
            camera_type: "entry" or "exit"
            camera: OpenCV VideoCapture object
        """
        logger.info(f"Starting {camera_type} camera monitoring loop")

        while self.running.is_set():
            try:
                # Read frame
                ret, frame = camera.read()

                if not ret:
                    logger.warning(f"{camera_type} camera: Failed to read frame")
                    time.sleep(0.1)
                    continue

                # Check cooldown
                current_time = time.time()
                with self.cooldown_lock:
                    if current_time - self.last_qr_times[camera_type] < config.QR_COOLDOWN_SECONDS:
                        # Still in cooldown, skip detection
                        time.sleep(0.03)  # ~30 FPS
                        continue

                # Detect QR codes
                qr_codes = pyzbar.decode(frame)

                if qr_codes:
                    for qr_code in qr_codes:
                        qr_data = qr_code.data.decode('utf-8')

                        # Update cooldown time
                        with self.cooldown_lock:
                            self.last_qr_times[camera_type] = current_time

                        logger.info(f"{camera_type.upper()} camera: QR Code detected: {qr_data}")

                        # Call callback
                        if self.on_qr_detected_callback:
                            self.on_qr_detected_callback(qr_data, camera_type)

                        # Break after first QR (prevent multiple triggers)
                        break

                # Small delay to control frame rate
                time.sleep(0.03)  # ~30 FPS

            except Exception as e:
                logger.error(f"Error in {camera_type} camera monitoring: {e}")
                time.sleep(1)

        logger.info(f"{camera_type} camera monitoring stopped")

    def get_frame(self, camera_type):
        """
        Get a single frame from specified camera (for display/debugging)

        Args:
            camera_type: "entry" or "exit"

        Returns:
            Frame or None
        """
        try:
            camera = self.entry_camera if camera_type == 'entry' else self.exit_camera

            if camera and camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    return frame

            return None

        except Exception as e:
            logger.error(f"Error getting frame from {camera_type} camera: {e}")
            return None

    def cleanup(self):
        """Clean up camera resources"""
        logger.info("Cleaning up cameras...")
        self.running.clear()

        # Wait for threads to finish
        if self.entry_thread and self.entry_thread.is_alive():
            self.entry_thread.join(timeout=2)

        if self.exit_thread and self.exit_thread.is_alive():
            self.exit_thread.join(timeout=2)

        # Release cameras
        if self.entry_camera:
            self.entry_camera.release()
            logger.info("Entry camera released")

        if self.exit_camera:
            self.exit_camera.release()
            logger.info("Exit camera released")

        cv2.destroyAllWindows()
