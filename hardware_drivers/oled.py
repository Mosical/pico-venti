"""Abstract the ssd1306 driver"""
import time
from machine import I2C
import ssd1306


class OLED:
    """Class to perform a reset and self test of the oled and handle the only functionality from the
    ssd1306 driver used by this project"""

    def __init__(self, i2c: I2C, horizontal: int = 128, vertical: int = 32, address: int = 0x3C):
        """Start the display object using the SSD1306 oled i2c driver

        Example:
            ```
            from machine import I2C, Pin
            from oled import OLED
            i2c = I2C(0, scl=Pin(1), sda=Pin(0))
            oled = OLED(i2c)

            # start screen and write a single string that will remain there
            oled.start_screen()
            oled.write_text("hello world", 0, 0)
            oled.display_text()

            # Continue writing text, replacing previous text
            for x in range(10):
                oled.clear_framebuffer()
                oled.write_text(f"{x}", 0 ,0)
                oled.display_text()
                time.sleep(0.5)
            ```

        Args:
            i2c (I2C): i2c object used by the oled screen
            horizontal (int, optional): horizontal pixel count of screen. Defaults to 128.
            vertical (int, optional): Vertical pixel count of screen. Defaults to 32.
            address (int, optional): The i2c address of the display
        """
        self.display = ssd1306.SSD1306_I2C(horizontal, vertical, i2c, address)

    def start_screen(self) -> None:
        """Perform a startup/test sequence resetting the oled then filling and wiping the screen"""
        self.display.poweroff()
        time.sleep(1)
        self.display.poweron()
        self.display.fill(1)
        self.display.show()
        time.sleep(1)
        self.display.fill(0)

    def clear_framebuffer(self) -> None:
        """Empty the framebuffer. Should be used before writing new text to the same position"""
        self.display.fill(0)

    def write_text(self, string: str, x_pos: int, y_pos: int) -> None:
        """Define the text that will be written to the screen and the position to write it to

        Args:
            string (str): Text to display on the oled screen
            x_pos (int): starting x position for the string
            y_pos (int): starting y position for the string
        """
        self.display.text(string, x_pos, y_pos)

    def display_text(self) -> None:
        """Write whatever is in the framebuffer to the screen"""
        self.display.show()
