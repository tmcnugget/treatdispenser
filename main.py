from pyky040 import pyky040
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from PIL import ImageFont
import time
import threading

# Initialize OLED display
serial = i2c(port=1, address=0x3C)  # Adjust if needed
device = ssd1306(serial)

# Load font
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 20
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

def update_display(text):
    """Function to display text on the OLED"""
    with canvas(device) as draw:
        draw.text((0, 0), text, font=font, fill="white")

# Initialize encoder
detent = 0

def encoder_callback(position):
    global detent
    detent = position
    print(f"Detent: {detent}")
    update_display(f"Detent: {detent}")

def button_callback():
    print("Button Pressed")

encoder = pyky040.Encoder(CLK=17, DT=18, SW=27)
encoder.setup(scale_min=0, scale_max=100, step=1, chg_callback=encoder_callback, sw_callback=button_callback)

# Run encoder in a separate thread
encoder_thread = threading.Thread(target=encoder.watch, daemon=True)
encoder_thread.start()

# Initialize display
update_display("Detent: 0")

try:
    while True:
        time.sleep(1)  # Keep the script running
except KeyboardInterrupt:
    print("Exiting...")
