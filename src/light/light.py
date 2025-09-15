import time
import board
import neopixel_spi as neopixel

from utils.decorators import singleton



@singleton
class LightController:
    PIXEL_ORDER = neopixel.GRB
    NUM_PIXELS = 8

    def __init__(self):
        """
        Initialize the LightController with SPI and NeoPixel configuration.
        Sets default brightness and turns the light off initially.
        Shows a startup light effect to indicate readiness.
        """
        self.spi = board.SPI()
        self.pixels = neopixel.NeoPixel_SPI(self.spi, self.NUM_PIXELS, pixel_order=self.PIXEL_ORDER, auto_write=False)

        self.brightness = 1.0
        self.on = False

        # Show that light is working and the system is ready
        self.show_off()

    def set_brightness(self, brightness):
        """
        Set the brightness of the light.
        :param brightness: Brightness level (0.0 to 1.0)
        """
        self.brightness = brightness
        self.pixels.brightness = brightness
        self.pixels.show()

    def toggle(self):
        """
        Toggle the light on or off.
        """
        self.on = not self.on
        if self.on:
            self.pixels.fill((255, 255, 255))
        else:
            self.pixels.fill((0, 0, 0))
            
        self.pixels.brightness = self.brightness
        self.pixels.show()

    def turn(self, on_off):
        """
        Turn the light on or off.
        :param on_off: True to turn on, False to turn off
        """
        self.on = on_off
        if self.on:
            self.pixels.fill((255, 255, 255))
        else:
            self.pixels.fill((0, 0, 0))
            
        self.pixels.brightness = self.brightness
        self.pixels.show()

    def show_off(self):
        """
        Display a startup light effect: fade in each pixel, then a quick flash, then turn off.
        Used to indicate the system is ready.
        """
        steps = 500 # smoothness of the fade effect
        for i in range(self.NUM_PIXELS):
            for j in range(steps):
                brightness = int(255 * j / (steps - 1))
                self.pixels[i] = (brightness, brightness, brightness)
                self.pixels.show()
        
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        time.sleep(0.1)
        # Flashbang
        self.pixels.fill((255, 255, 255))
        self.pixels.show()   
        time.sleep(0.1)
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
