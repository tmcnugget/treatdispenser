from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO
from time import sleep

app = Flask(__name__)

# GPIO setup
SERVO_PIN = 12  # Use GPIO 12 for hardware PWM
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz for servos
pwm.start(0)

# Define duty cycles for rotation
STOP_DUTY = 6.7    # Neutral duty cycle to stop
CCW_DUTY = 5.0     # Counterclockwise rotation
CW_DUTY = 10.0     # Clockwise rotation

# State variable to track if the servo is rotating
is_rotating = False

def rotate_servo(duty_cycle):
    pwm.ChangeDutyCycle(duty_cycle)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/servo_control', methods=['POST'])
def servo_control():
    global is_rotating
    if is_rotating:
        # Stop the servo and perform the "wipe" action
        rotate_servo(STOP_DUTY)
        is_rotating = False
        # Call the wipe function to rotate clockwise for 2 seconds
        wipe()
    else:
        # Start rotating counterclockwise
        rotate_servo(CCW_DUTY)
        is_rotating = True
    return jsonify(success=True)

@app.route('/wipe', methods=['POST'])
def wipe():
    # Rotate clockwise for 2 seconds, then stop
    rotate_servo(CW_DUTY)
    sleep(2)
    rotate_servo(STOP_DUTY)
    return jsonify(success=True)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        rotate_servo(STOP_DUTY)  # Ensure servo is stopped on exit
        pwm.stop()
        GPIO.cleanup()
