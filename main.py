import RPi.GPIO as GPIO
import time
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c

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

# Initialize the display
device.clear()
device.text("Counter: 0", 0, 0, fill="white")
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
            device.text(f"Counter: {counter}", 0, 0, fill="white")
            device.show()

        clkLastState = clkState

        # Check for button press
        if GPIO.input(SW) == GPIO.LOW:
            print("Button Pressed")
            time.sleep(0.5)  # Debounce delay

        time.sleep(0.01)  # Avoid excessive CPU usage
finally:
    GPIO.cleanup()
