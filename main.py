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
font_large = ImageFont.truetype(FONT_PATH, 24)

# Menu States
STATE_HOME = "home"
STATE_AUTO = "auto"
STATE_MANUAL = "manual"
STATE_ADJUST_AMOUNT = "adjust_amount"

menu_state = STATE_HOME
selected_index = 0  # Tracks selection in home & auto menus
amount = 0  # Default amount
detent_lock = threading.Lock()

# Track encoder position manually
encoder_position = 0

# Function to render menu on OLED
def update_display():
    with detent_lock:
        state = menu_state
        index = selected_index
        num = amount
    
    with canvas(device) as draw:
        if state == STATE_HOME:
            draw.text((20, 0), "Treat Vendor", font=font, fill="white")  # Banner
            
            draw.text((20, 20), "[Auto]" if index == 0 else " Auto ", font=font, fill="white")
            draw.text((90, 20), "[Manual]" if index == 1 else " Manual ", font=font, fill="white")

        elif state == STATE_AUTO:
            draw.text((5, 0), "< Back", font=font, fill="white")
            draw.text((45, 20), "[Amount]" if index == 0 else " Amount ", font=font, fill="white")
            draw.text((55, 45), f"{num:02d}", font=font_large, fill="white")
            draw.text((25, 60), "Dispense", font=font, fill="white")  # Bottom banner

# Encoder Callback
def encoder_callback():
    global selected_index, amount, menu_state, encoder_position

    with detent_lock:
        if encoder.is_active:
            movement = encoder.value - encoder_position
            encoder_position = encoder.value  # Update stored position

            if menu_state == STATE_HOME:
                selected_index = (selected_index + movement) % 2  # Toggle between 0 (Auto) & 1 (Manual)
            elif menu_state == STATE_AUTO:
                if selected_index == 0:  # Adjusting amount
                    amount = max(0, min(99, amount + movement))

    update_display()

# Button Callback
def button_callback():
    global menu_state, selected_index

    with detent_lock:
        if menu_state == STATE_HOME:
            if selected_index == 0:
                menu_state = STATE_AUTO
                selected_index = 0  # Default selection in Auto mode
            elif selected_index == 1:
                menu_state = STATE_MANUAL  # Placeholder for manual mode

        elif menu_state == STATE_AUTO:
            if selected_index == 0:
                menu_state = STATE_ADJUST_AMOUNT
            else:
                menu_state = STATE_HOME  # Back button pressed

        elif menu_state == STATE_ADJUST_AMOUNT:
            menu_state = STATE_AUTO  # Exit amount adjustment

    update_display()

# Initialize Encoder & Button
encoder = RotaryEncoder(CLK_PIN, DT_PIN)
button = Button(SW_PIN)

encoder.when_rotated = encoder_callback
button.when_pressed = button_callback

# Start Display
update_display()

# Keep running
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
