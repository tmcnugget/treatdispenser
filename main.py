from gpiozero import RotaryEncoder, Button
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from PIL import ImageFont
import time
import threading

# GPIO Pins
CLK_PIN = 17
DT_PIN = 18
SW_PIN = 27

# Initialize OLED display
serial = i2c(port=1, address=0x3C)  # Adjust if needed
device = ssd1306(serial)

# Load font
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 20
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# Initialize rotary encoder and button
encoder = RotaryEncoder(CLK_PIN, DT_PIN, wrap=False, max_steps=100)
button = Button(SW_PIN, pull_up=True, bounce_time=0.05)  # 50ms debounce

# Global detent variable
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

def encoder_callback():
    """Handles encoder rotation events"""
    global detent
    with detent_lock:
        detent = encoder.steps
    print(f"Detent: {detent}")

def button_callback():
    """Handles button press event"""
    print("Button Pressed")

# Attach callbacks
encoder.when_rotated = encoder_callback
button.when_pressed = button_callback

# Start display update in a thread
display_thread = threading.Thread(target=update_display, daemon=True)
display_thread.start()

try:
    while True:
        time.sleep(1)  # Keep the script running
except KeyboardInterrupt:
    print("Exiting...")
