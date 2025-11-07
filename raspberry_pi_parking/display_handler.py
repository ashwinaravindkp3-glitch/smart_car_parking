"""
I2C LCD Display Handler for Raspberry Pi Smart Parking System
Displays welcome messages with slot numbers and thank you messages
"""

import time
import logging
from threading import Lock
import config

logger = logging.getLogger(__name__)

# Import I2C LCD library
try:
    from RPLCD.i2c import CharLCD
    I2C_AVAILABLE = True
except ImportError:
    logger.warning("RPLCD library not available, using mock display")
    I2C_AVAILABLE = False

    # Mock CharLCD for testing
    class CharLCD:
        def __init__(self, *args, **kwargs):
            pass

        def clear(self):
            pass

        def write_string(self, text):
            logger.info(f"[MOCK LCD] {text}")

        def cursor_pos(self, row, col):
            pass

        def close(self, clear=False):
            pass


class DisplayHandler:
    def __init__(self):
        """Initialize Display Handler"""
        self.lcd = None
        self.lock = Lock()
        self.display_available = False

    def setup(self):
        """Initialize I2C LCD display"""
        try:
            if not config.ENABLE_DISPLAY:
                logger.warning("Display disabled in config")
                return True

            logger.info(f"Initializing I2C LCD at address {hex(config.LCD_I2C_ADDRESS)}")

            # Initialize LCD
            # For 16x2 display: cols=16, rows=2
            # For 20x4 display: cols=20, rows=4
            self.lcd = CharLCD(
                i2c_expander=config.LCD_I2C_EXPANDER,
                address=config.LCD_I2C_ADDRESS,
                port=config.LCD_I2C_PORT,
                cols=config.LCD_COLS,
                rows=config.LCD_ROWS,
                dotsize=8,
                charmap='A02',
                auto_linebreaks=True
            )

            self.display_available = True

            # Show startup message
            self.show_startup()

            logger.info(f"I2C LCD initialized successfully ({config.LCD_COLS}x{config.LCD_ROWS})")
            return True

        except Exception as e:
            logger.error(f"Failed to setup I2C LCD: {e}")
            logger.info("Display will be disabled, but system will continue")
            self.display_available = False
            return True  # Don't fail the entire system if display fails

    def show_startup(self):
        """Show system startup message"""
        try:
            with self.lock:
                if not self.display_available:
                    return

                self.lcd.clear()
                if config.LCD_ROWS >= 2:
                    self.lcd.write_string("Smart Parking")
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string("System Ready")
                else:
                    self.lcd.write_string("Parking Ready")

                time.sleep(2)
                self.clear()

        except Exception as e:
            logger.error(f"Error showing startup message: {e}")

    def show_welcome(self, slot_number, user_id=None):
        """
        Show welcome message with assigned slot number

        Args:
            slot_number: Assigned parking slot number
            user_id: Optional user ID
        """
        try:
            with self.lock:
                if not self.display_available:
                    logger.info(f"[DISPLAY] Welcome! Slot: {slot_number}")
                    return

                self.lcd.clear()

                if config.LCD_ROWS == 2:
                    # 16x2 or 20x2 display
                    self.lcd.write_string("Welcome!")
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string(f"Proceed to Slot {slot_number}")

                elif config.LCD_ROWS >= 4:
                    # 20x4 display
                    self.lcd.write_string("Welcome!")
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string("")  # Blank line
                    self.lcd.cursor_pos(2, 0)
                    self.lcd.write_string(f"Please proceed to")
                    self.lcd.cursor_pos(3, 0)
                    self.lcd.write_string(f"SLOT {slot_number}")

                else:
                    # Single line display
                    self.lcd.write_string(f"Slot {slot_number}")

                logger.info(f"Display: Welcome message for Slot {slot_number}")

        except Exception as e:
            logger.error(f"Error showing welcome message: {e}")

    def show_thank_you(self):
        """Show thank you message when exiting"""
        try:
            with self.lock:
                if not self.display_available:
                    logger.info("[DISPLAY] Thank you!")
                    return

                self.lcd.clear()

                if config.LCD_ROWS == 2:
                    # 16x2 or 20x2 display
                    self.lcd.write_string("Thank You!")
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string("Drive Safely")

                elif config.LCD_ROWS >= 4:
                    # 20x4 display
                    self.lcd.write_string("Thank You")
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string("")  # Blank line
                    self.lcd.cursor_pos(2, 0)
                    self.lcd.write_string("for parking")
                    self.lcd.cursor_pos(3, 0)
                    self.lcd.write_string("Drive Safely!")

                else:
                    # Single line display
                    self.lcd.write_string("Thank You!")

                logger.info("Display: Thank you message")

        except Exception as e:
            logger.error(f"Error showing thank you message: {e}")

    def show_error(self, message="Error"):
        """Show error message"""
        try:
            with self.lock:
                if not self.display_available:
                    logger.info(f"[DISPLAY] Error: {message}")
                    return

                self.lcd.clear()
                self.lcd.write_string("Error")
                if config.LCD_ROWS >= 2:
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string(message[:config.LCD_COLS])

                logger.warning(f"Display: Error message - {message}")

        except Exception as e:
            logger.error(f"Error showing error message: {e}")

    def show_scanning(self, barrier_type="entry"):
        """Show scanning message"""
        try:
            with self.lock:
                if not self.display_available:
                    return

                self.lcd.clear()
                if config.LCD_ROWS >= 2:
                    self.lcd.write_string("Please scan")
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string("your QR code")
                else:
                    self.lcd.write_string("Scan QR Code")

        except Exception as e:
            logger.error(f"Error showing scanning message: {e}")

    def show_full(self):
        """Show parking full message"""
        try:
            with self.lock:
                if not self.display_available:
                    logger.info("[DISPLAY] Parking Full")
                    return

                self.lcd.clear()
                if config.LCD_ROWS >= 2:
                    self.lcd.write_string("Sorry!")
                    self.lcd.cursor_pos(1, 0)
                    self.lcd.write_string("Parking Full")
                else:
                    self.lcd.write_string("Parking Full")

                logger.info("Display: Parking full message")

        except Exception as e:
            logger.error(f"Error showing full message: {e}")

    def clear(self):
        """Clear display"""
        try:
            with self.lock:
                if not self.display_available:
                    return

                self.lcd.clear()

        except Exception as e:
            logger.error(f"Error clearing display: {e}")

    def show_custom(self, lines):
        """
        Show custom message

        Args:
            lines: List of strings, one per line
        """
        try:
            with self.lock:
                if not self.display_available:
                    logger.info(f"[DISPLAY] {' | '.join(lines)}")
                    return

                self.lcd.clear()
                for i, line in enumerate(lines):
                    if i >= config.LCD_ROWS:
                        break
                    self.lcd.cursor_pos(i, 0)
                    self.lcd.write_string(line[:config.LCD_COLS])

        except Exception as e:
            logger.error(f"Error showing custom message: {e}")

    def cleanup(self):
        """Clean up display resources"""
        logger.info("Cleaning up display handler...")

        try:
            if self.display_available and self.lcd:
                with self.lock:
                    self.lcd.clear()
                    self.lcd.write_string("Goodbye!")
                    time.sleep(1)
                    self.lcd.close(clear=True)

            logger.info("Display cleanup complete")

        except Exception as e:
            logger.error(f"Error during display cleanup: {e}")
