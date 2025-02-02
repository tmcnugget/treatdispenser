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

page = "home"
value = 0
pressed = 0

def wrap(index, lock):
    return index % lock

def text(draw, text, size, x, y, colour):
    """Function to display text on the OLED display"""
    font = ImageFont.truetype("font.ttf", size)
    draw.text((x, y), text, font=font, fill=colour)
    
def gui_button(draw, text_value, size, x, y, index, lock, id):
    selection = wrap(index, lock)
    selected = (selection == id)
    font = ImageFont.truetype("font.ttf", size)

    if selected:
        text(draw, text_value, size, x, y, "black")
        text_width, text_height = font.getbbox(text_value)
        draw.rectangle([(x - 2, y - 2), (x + text_width + 2, y + text_height + 2)], outline="white", width=1)
    else:
        text(draw, text_value, size, x, y, "white")
        
# Function to render the menu and pages
def update_display():
    with canvas(device) as draw:
        if page == "home":
            gui_button(draw, "Auto", 20, 25, 0, value, 2, 1)
            gui_button(draw, "Manual", 20, 25, 25, value, 2, 2)

# Encoder rotation callback for the menu
def encoder_callback():
    global value
    value = value + (1 if encoder.steps > 0 else -1)

# Button press callback for the menu and auto mode
def button_callback():
    global pressed
    pressed = 1
    time.sleep(0.05)
    pressed = 0

# Setup rotary encoder and button
encoder = RotaryEncoder(CLK_PIN, DT_PIN, wrap=False)
button = Button(SW_PIN, pull_up=True, bounce_time=0.05)

encoder.when_rotated = encoder_callback
button.when_pressed = button_callback

while True:
    update_display()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
