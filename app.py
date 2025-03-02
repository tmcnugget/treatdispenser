from flask import Flask, render_template, jsonify
import datetime

app = Flask(__name__)

# Store dispense times
dispense_log = {}

def dispense_treat():
    """Mock function to dispense a treat."""
    print("Treat Dispensed!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dispense', methods=['POST'])
def dispense():
    """Handles the dispense button press."""
    now = datetime.datetime.now()
    hour_minute = now.strftime("%H:%M")

    if 6 <= now.hour <= 21:  # Only log between 06:00 - 21:00
        dispense_log[hour_minute] = dispense_log.get(hour_minute, 0) + 1

    dispense_treat()
    return jsonify(success=True, log=dispense_log)

@app.route('/get_log')
def get_log():
    """Returns the dispense log for the activity graph."""
    return jsonify(dispense_log)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
