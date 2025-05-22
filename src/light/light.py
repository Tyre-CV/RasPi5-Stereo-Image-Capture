import board
import neopixel_spi as neopixel

from utils.decorators import singleton



@singleton
class LightController:
    PIXEL_ORDER = neopixel.GRB
    NUM_PIXELS = 8

    def __init__(self):
        self.spi = board.SPI()
        self.pixels = neopixel.NeoPixel_SPI(self.spi, self.NUM_PIXELS, pixel_order=self.PIXEL_ORDER, auto_write=False)

        self.brightness = 1.0
        self.on = False

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

    




# N = 100000
# duration = 10  # seconds for one full cycle (up and down)
# steps = 1000   # number of steps for smoothness
# delay = 0.5

# def pick_random_color():
#     return (
#         random.randint(0, 255),
#         random.randint(0, 255),
#         random.randint(0, 255)
#     )

# for _ in range(N):
#     for i in range(NUM_PIXELS):
#         color = pick_random_color()
#         r, g, b = color
#         pixels[i] = (
#             int(r),
#             int(g),
#             int(b)
#         )

#         pixels.show()
#         time.sleep(delay)

#         # Turn off the pixel to move to the next
#         pixels[i] = (0, 0, 0)
#         pixels.show()


# """
# for _ in range(N):
#     # Fade in
#     for i in range(steps):
#         brightness = int(255 * i / (steps - 1))
#         pixels.fill((brightness, brightness, brightness))
#         pixels.show()
#         time.sleep(duration / (2 * steps))
#     # Fade out
#     for i in range(steps - 1, -1, -1):
#         brightness = int(255 * i / (steps - 1))
#         pixels.fill((brightness, brightness, brightness))
#         pixels.show()
#         time.sleep(duration / (2 * steps))

# """
# # Turn off all pixels at the end
# pixels.fill((0, 0, 0))
# pixels.show()
