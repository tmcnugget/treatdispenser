from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)
activity_log = {
    "dispense": {},
    "redact": {},
    "purge": {}
}
is_purging = False

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

@app.route("/redact", methods=["POST"])
def redact():
    log_event("redact")
    return jsonify(log=activity_log)

@app.route("/purge_start", methods=["POST"])
def purge_start():
    global is_purging
    is_purging = True
    log_event("purge")
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
    return jsonify(message="Motors Released")

@app.route("/get_log", methods=["GET"])
def get_log():
    return jsonify(activity_log)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
