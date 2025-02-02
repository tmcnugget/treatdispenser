import RPi.GPIO as GPIO
import time
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from PIL import ImageFont

# Pin configuration
CLK = 17  # Clock pin
DT = 18   # Data pin
SW = 27   # Switch pin

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize OLED display
serial = i2c(port=1, address=0x3C)  # Ensure address matches your OLED (0x3C is common)
device = ssd1306(serial)

def text(device, text, size, x, y):
    """Function to display text on the OLED display"""
    with canvas(device) as draw:
        font = ImageFont.truetype("font.ttf", size)
        draw.text((x, y), text, font=font, fill="white")

# Initialize the display
device.clear()
text(device, "Counter: 0", 50, 0, 0)
device.show()

counter = 0
clkLastState = GPIO.input(CLK)

try:
    while True:
        # Read rotation
        clkState = GPIO.input(CLK)
        dtState = GPIO.input(DT)
        if clkState != clkLastState:
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
            print(f"Counter: {counter}")

            # Update OLED display
            device.clear()
            text(device, f"Counter: {counter}", 50, 0, 0)
            device.show()

        clkLastState = clkState

        # Check for button press
        if GPIO.input(SW) == GPIO.LOW:
            print("Button Pressed")
            time.sleep(0.5)  # Debounce delay

        time.sleep(0.01)  # Avoid excessive CPU usage
finally:
    GPIO.cleanup()
