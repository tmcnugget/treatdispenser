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

# Font Setup
FONT_PATH = "font.ttf"  # Change if needed
FONT_SIZE = 16
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# Menu Items
menu_items = ["Option 1", "Option 2", "Option 3", "Option 4"]
current_index = 0  # Tracks menu position
selected_index = None  # Tracks selected item

detent_lock = threading.Lock()

# Function to render menu on OLED
def update_display():
    while True:
        with detent_lock:
            index = current_index
            selected = selected_index
        
        with canvas(device) as draw:
            for i, item in enumerate(menu_items):
                y_pos = i * 20  # Adjust spacing
                
                if selected == i:
                    # Selected item: White box with black text
                    draw.rectangle((0, y_pos, device.width, y_pos + 18), fill="white")
                    draw.text((5, y_pos), item, font=font, fill="black")
                elif index == i:
                    # Highlighted item: Add > item <
                    draw.text((5, y_pos), f"> {item} <", font=font, fill="white")
                else:
                    # Normal items
                    draw.text((5, y_pos), item, font=font, fill="white")
        
        time.sleep(0.1)  # Refresh rate

# Encoder rotation callback
def encoder_callback():
    global current_index
    with detent_lock:
        if selected_index is None:  # Only move when not selected
            new_index = current_index + (1 if encoder.steps > 0 else -1)
            if 0 <= new_index < len(menu_items):  # Prevent wrapping
                current_index = new_index
    print(f"Menu Position: {current_index}")

# Button press callback
def button_callback():
    global selected_index
    with detent_lock:
        if selected_index is None:
            selected_index = current_index  # Select item
        else:
            selected_index = None  # Deselect item
    print(f"Selected Item: {menu_items[current_index]}")

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
