from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time
from flask import Flask, render_template, jsonify
from datetime import datetime
from threading import Thread

app = Flask(__name__)
activity_log = {
    "dispense": {},
    "redact": {},
    "purge": {}
}
is_purging = False

# Initialize the Motor HAT
kit = MotorKit()

# Select stepper motor 1 (M1, M2, M3, M4)
motor = kit.stepper1

def purge_motor():
    """Function to move the motor in backward steps during purging"""
    while True:
        if not is_purging:  # Check if purging is still enabled
            break
        else:    
            motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            time.sleep(0.001)  # Small delay for motor stepping speed

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
    return jsonify(log=activity_log)
    for _ in range(1000):
        motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
        time.sleep(0.001)

@app.route("/redact", methods=["POST"])
def redact():
    log_event("redact")
    return jsonify(log=activity_log)
    for _ in range(1000):
        motor.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
        time.sleep(0.001)

@app.route("/purge_start", methods=["POST"])
def purge_start():
    global is_purging
    is_purging = True
    log_event("purge")
    purge_thread = Thread(target=purge_motor)
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
