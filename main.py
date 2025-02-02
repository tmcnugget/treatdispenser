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

# OLED Setup
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

button = 0
page = "home"

def wrap(index, lock):
    return (index % lock) - 1

def text(device, text, size, x, y colour):
    """Function to display text on the OLED display"""
    with canvas(device) as draw:
        font = ImageFont.truetype("font.ttf", size)
        draw.text((x, y), text, font=font, fill=colour)

def button(device, text, size, x, y, inverted, index, lock, id):
    selected = 0
    selection = wrap(index, lock)
    if inverted = "false":
        if selected:
            text(device, text, size, x, y, "black")
            with canvas(device) as draw:
                font = ImageFont.truetype("font.ttf", size)
                text_width, text_height = draw.textsize(text, font=font)
                draw.rectangle([(x - 2, y - 2), (x + text_width + 2, y + text_height + 2)], outline="white", width=1)
        else:
            text(device, text, size, x, y, "white")
    elif inverted = "true":
        if selected:
            text(device, text, size, x, y, "white")
        else:
            text(device, text, size, x, y, "black")
            with canvas(device) as draw:
                font = ImageFont.truetype("font.ttf", size)
                text_width, text_height = draw.textsize(text, font=font)
                draw.rectangle([(x - 2, y - 2), (x + text_width + 2, y + text_height + 2)], outline="white", width=1)
            
    if selection == id:
        selected = 1   
        
# Function to render the menu and pages
def update_display(device):
    if page == "home":
        button(device, "Auto", 20, 25, 0, "false", value, 2, 1)
        button(device, "Manual", 20, 25, 25, "false", value, 2, 2)
    if page == "auto":

    if page == "manual":

# Encoder rotation callback for the menu
def encoder_callback():
    global value
    value = value + (1 if encoder.steps > 0 else -1)

# Button press callback for the menu and auto mode
def button_callback():
    button = 1
    time.sleep(0.05)
    button = 0

# Setup rotary encoder and button
encoder = RotaryEncoder(CLK_PIN, DT_PIN, wrap=False, max_steps=len(menu_items) - 1)
button = Button(SW_PIN, pull_up=True, bounce_time=0.05)

encoder.when_rotated = encoder_callback
button.when_pressed = button_callback

# Start display update thread
display_thread = threading.Thread(target=update_display, daemon=True)
display_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
