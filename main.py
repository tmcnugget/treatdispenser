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
menu_items = ["Auto", "Manual"]
current_index = 0  # Tracks menu position
selected_index = None  # Tracks selected item

# Auto Mode Variables
amount = 0
in_auto_mode = False
detent_lock = threading.Lock()

# Function to render the menu and pages
def update_display():
    global in_auto_mode
    while True:
        with detent_lock:
            index = current_index
            selected = selected_index
            mode = "Auto" if in_auto_mode else "Home"

        with canvas(device) as draw:
            # Top Banner: Treat Vendor (Just Text, No Fill)
            if selected_index is None:  # Home mode
                draw.text((device.width // 2 - 50, 2), "Treat Vendor", font=font, fill="white")

            if in_auto_mode:
                # Auto Mode Page
                # Back button in top left
                draw.text((0, 0), "Home", font=font, fill="white")
                # Amount in top center
                draw.text((device.width // 2 - 20, 18), f"{amount:02}g", font=font, fill="white")
                # Dispense banner at bottom
                draw.rectangle((0, device.height - 16, device.width, device.height), fill="white")
                draw.text((device.width // 2 - 30, device.height - 14), "Dispense", font=font, fill="black")
            else:
                # Home Screen
                for i, item in enumerate(menu_items):
                    y_pos = i * 20 + 16  # Adjust vertical spacing for menu items
                    if selected == i:
                        # Selected item: White box with black text
                        draw.rectangle((0, y_pos, device.width, y_pos + 18), fill="white")
                        draw.text((device.width // 2 - (len(item) * FONT_SIZE // 2), y_pos), item, font=font, fill="black")
                    elif index == i:
                        # Highlighted item: Add > item <
                        draw.text((device.width // 2 - (len(item) * FONT_SIZE // 2), y_pos), f"> {item} <", font=font, fill="white")
                    else:
                        # Normal items
                        draw.text((device.width // 2 - (len(item) * FONT_SIZE // 2), y_pos), item, font=font, fill="white")

        time.sleep(0.1)  # Refresh rate

# Encoder rotation callback for the menu
def encoder_callback():
    global current_index, amount, in_auto_mode
    with detent_lock:
        if selected_index is None:  # Move through menu only if no item is selected
            new_index = current_index + (1 if encoder.steps > 0 else -1)
            if 0 <= new_index < len(menu_items):  # Prevent wrapping
                current_index = new_index
        elif in_auto_mode:
            if selected_index == 1:  # Amount option is selected
                # Increase or decrease the amount
                new_amount = amount + (1 if encoder.steps > 0 else -1)
                if 0 <= new_amount <= 99:  # Prevent wrapping
                    amount = new_amount
                    print(f"Amount: {amount:02}")

# Button press callback for the menu and auto mode
def button_callback():
    global selected_index, in_auto_mode, amount, current_index
    with detent_lock:
        if selected_index is None:  # Select menu item
            selected_index = current_index
            if current_index == 0:  # Auto is selected
                in_auto_mode = True
            elif current_index == 1:  # Manual is selected (Not implemented yet)
                pass
        elif in_auto_mode:
            if selected_index == 0:  # "Auto" is selected, you enter the amount mode
                selected_index = 1  # Move to amount selection
            elif selected_index == 1:  # Amount is selected, save the value
                selected_index = None  # De-select and return to Home
            # Back action if 'back' was selected
        else:
            selected_index = None  # Deselect any selected item
            in_auto_mode = False  # Go back to Home

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
