from flask import Flask, render_template, jsonify
import datetime

app = Flask(__name__)

# Store dispense times (hour:minute)
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
    time_label = now.strftime("%H:%M")

    if "06:00" <= time_label <= "21:00":  # Only log within time range
        if time_label in dispense_log:
            dispense_log[time_label] += 1  # Increase count if within the same minute
        else:
            dispense_log[time_label] = 1

    dispense_treat()
    return jsonify(success=True, log=dispense_log)

@app.route('/get_log')
def get_log():
    """Returns the dispense log for the activity graph."""
    return jsonify(dispense_log)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
