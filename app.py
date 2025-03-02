from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time
from flask import Flask, render_template, jsonify
from datetime import datetime
from threading import Thread

app = Flask(__name__)

# File path for activity log
log_file_path = "activity_log.json"

is_purging = False

# Initialize the Motor HAT
kit = MotorKit()

# Select stepper motor 1 (M1, M2, M3, M4)
motor = kit.stepper1

def save_log_to_file():
    """Save activity log to the JSON file."""
    with open(log_file_path, "w") as f:
        json.dump(activity_log, f)

def load_log_from_file():
    """Load activity log from the JSON file."""
    try:
        with open(log_file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"dispense": {}, "redact": {}, "purge": {}}

# Load the activity log when the server starts
activity_log = load_log_from_file()

def purgeMotor():
    """Function to move the motor in backward steps during purging"""
    while True:
        if not is_purging:  # Check if purging is still enabled
            break
        else:
            motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            time.sleep(0.001)  # Small delay for motor stepping speed

def dispenseMotor():
    for _ in range(100):
        motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
        time.sleep(0.01)

def redactMotor():
    for _ in range(100):
        motor.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
        time.sleep(0.001)

def log_event(event_type):
    now = datetime.now().strftime("%H:%M")
    if now in activity_log[event_type]:
        activity_log[event_type][now] += 1
    else:
        activity_log[event_type][now] = 1

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dispense", methods=["POST"])
def dispense():
    log_event("dispense")
    dispense_thread = Thread(target=dispenseMotor)
    dispense_thread.start()
    return jsonify(log=activity_log)

@app.route("/redact", methods=["POST"])
def redact():
    log_event("redact")
    redact_thread = Thread(target=redactMotor)
    redact_thread.start()
    return jsonify(log=activity_log)

@app.route("/purge_start", methods=["POST"])
def purge_start():
    global is_purging
    is_purging = True
    log_event("purge")
    purge_thread = Thread(target=purgeMotor)
    purge_thread.start()
    return jsonify(log=activity_log)

@app.route("/purge_stop", methods=["POST"])
def purge_stop():
    global is_purging
    is_purging = False
    return jsonify(log=activity_log)

@app.route("/release", methods=["POST"])
def release():
    # Code to release motors to save battery
    print("Releasing motors...")
    motor.release()
    return jsonify(message="Motors Released")

@app.route("/get_log", methods=["GET"])
def get_log():
    return jsonify(activity_log)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
