from flask import Flask, render_template, jsonify
import datetime

app = Flask(__name__)

# Store dispense times
dispense_log = {f"{hour:02d}:00": 0 for hour in range(6, 22)}  # Initialize 06:00 - 21:00

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
    time_label = now.strftime("%H:00")

    if "06:00" <= time_label <= "21:00":  # Only update log within time range
        dispense_log[time_label] = 1  # Mark as dispensed at that hour

    dispense_treat()
    return jsonify(success=True, log=dispense_log)

@app.route('/get_log')
def get_log():
    """Returns the dispense log for the activity graph."""
    return jsonify(dispense_log)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
