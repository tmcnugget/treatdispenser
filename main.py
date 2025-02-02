from pyky040 import pyky040
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from PIL import ImageFont
import RPi.GPIO as GPIO
import time
import threading

# GPIO Pin Definitions
CLK_PIN = 17
DT_PIN = 18
SW_PIN = 27

# Initialize GPIO with pull-ups
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize OLED display
serial = i2c(port=1, address=0x3C)  # Adjust if needed
device = ssd1306(serial)

# Load font
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 20
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

detent = 0
detent_lock = threading.Lock()

def update_display():
    """Continuously update the OLED display"""
    while True:
        with detent_lock:
            display_text = f"Detent: {detent}"
        
        with canvas(device) as draw:
            draw.text((0, 0), display_text, font=font, fill="white")
        
        time.sleep(0.1)  # Update every 100ms

def encoder_callback(position):
    """Handles encoder rotation events"""
    global detent
    with detent_lock:
        detent = position
    print(f"Detent: {detent}")

def button_callback():
    """Handles button press event"""
    print("Button Pressed")

# Initialize and configure encoder
encoder = pyky040.Encoder(CLK=CLK_PIN, DT=DT_PIN, SW=SW_PIN, polling_interval=5)  # 5ms polling
encoder.setup(
    scale_min=0,
    scale_max=100,
    step=1,
    chg_callback=encoder_callback,
    sw_callback=button_callback,
    sw_debounce_time=50  # Debounce button press
)

# Start encoder monitoring in a thread
encoder_thread = threading.Thread(target=encoder.watch, daemon=True)
encoder_thread.start()

# Start display update in a thread
display_thread = threading.Thread(target=update_display, daemon=True)
display_thread.start()

try:
    while True:
        time.sleep(1)  # Keep the script running
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()  # Clean up GPIO on exit
