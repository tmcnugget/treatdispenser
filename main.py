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

# Global variables
page = "home"
value = 0
pressed = False
button_handled = False
editing_number = False  # Track if we're editing a number
number_value = 10  # Default number input
old_number_value = 10  # Store the old number before editing

# Load font
FONT_PATH = "font.ttf"

def wrap(index, lock):
    """Wraps the index to loop within a given lock range."""
    return (index % lock) + 1

def draw_text(draw, text, size, x, y, color="white"):
    """Displays text on the OLED screen."""
    font = ImageFont.truetype(FONT_PATH, size)
    draw.text((x, y), text, font=font, fill=color)

def draw_button(draw, text_value, size, x, y, index, lock, id, box1, box2, target_page):
    """Draws a selectable button on the screen."""
    global page, pressed
    selection = wrap(index, lock)
    selected = (selection == id)
    
    if selected:
        draw.rectangle([(0, box1), (140, box2)], outline="white", fill="white", width=1)
        draw_text(draw, text_value, size, x, y, "black")
        if pressed:
            page = target_page
    else:
        draw_text(draw, text_value, size, x, y, "white")

def draw_number(draw, minimum, maximum, size, x, y, index, lock, id, box1, box2):
    """Displays and allows adjustment of a number value."""
    global number_value, old_number_value, editing_number, pressed

    selection = wrap(index, lock)
    selected = (selection == id)

    if selected:
        if editing_number:
            draw.rectangle([(0, box1), (140, box2)], outline="white", fill="white", width=1)
            draw_text(draw, f"[{number_value}]", size, x, y, "black")  # Highlight in edit mode
        else:
            draw_text(draw, str(number_value), size, x, y, "white")
            draw.rectangle([(0, box1), (140, box2)], outline="white", fill="white", width=1)

        if pressed:
            if editing_number:
                editing_number = False  # Exit edit mode
            else:
                editing_number = True  # Enter edit mode
                old_number_value = number_value  # Store the old value

# Page rendering functions
def render_home(draw):
    """Renders the home page."""
    draw_button(draw, "Auto", 20, 25, 0, value, 2, 1, 0, 20, "auto")
    draw_button(draw, "Manual", 20, 25, 25, value, 2, 2, 25, 45, "manual")

def render_auto(draw):
    """Renders the auto settings page."""
    draw_button(draw, "<- Back", 10, 0, 0, value, 3, 1, 0, 10, "home")
    draw_number(draw, 0, 30, 20, 25, 25, value, 3, 2, 55, 85)

# Main display update loop
def update_display():
    """Continuously updates the OLED display based on the active page."""
    while True:
        with canvas(device) as draw:
            if page == "home":
                render_home(draw)
            elif page == "auto":
                render_auto(draw)
        time.sleep(0.05)

# Encoder rotation callback
def encoder_callback():
    """Handles rotary encoder rotation."""
    global value, number_value, editing_number

    if editing_number:
        number_value += 1 if encoder.steps > 0 else -1
        number_value = max(0, min(number_value, 30))  # Clamp between 0-30
    else:
        value += 1 if encoder.steps > 0 else -1

# Button press handling
def button_callback():
    """Handles button press to prevent rapid switching."""
    global pressed, button_handled
    if not button_handled:
        pressed = True
        button_handled = True

def reset_pressed():
    """Resets button press state when released."""
    global pressed, button_handled
    pressed = False
    button_handled = False

# Setup rotary encoder and button
encoder = RotaryEncoder(CLK_PIN, DT_PIN, wrap=False)
button = Button(SW_PIN, pull_up=True, bounce_time=0.05)

encoder.when_rotated = encoder_callback
button.when_pressed = button_callback
button.when_released = reset_pressed

# Start display update thread
display_thread = threading.Thread(target=update_display, daemon=True)
display_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
