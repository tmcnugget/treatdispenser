let isPurging = false;

function sendAction(action) {
    fetch(`/${action}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => updateGraph(data.log))
        .catch(error => console.error("Error during fetch:", error));
}

function togglePurge() {
    isPurging = !isPurging;
    const purgeButton = document.getElementById("purge-btn");
    purgeButton.textContent = isPurging ? "Stop Purge" : "Purge";
    sendAction(isPurging ? "purge_start" : "purge_stop");
}

function releaseMotors() {
    sendAction("release");
}

document.getElementById("dispense-btn").addEventListener("click", () => sendAction("dispense"));
document.getElementById("redact-btn").addEventListener("click", () => sendAction("redact"));
document.getElementById("purge-btn").addEventListener("click", togglePurge);

function updateGraph(log) {
    let labels = [];
    let dispenseData = [];
    let redactData = [];
    let purgeData = [];
    let maxY = 1;

    // Loop through hours from 6 AM to 9 PM
    for (let hour = 6; hour <= 21; hour++) {
        let label = `${hour}:00`;
        labels.push(label);
        let dispenseCount = 0, redactCount = 0, purgeCount = 0;

        // Loop through each minute of the hour
        for (let minute = 0; minute < 60; minute++) {
            let timeLabel = `${hour}:${minute < 10 ? "0" : ""}${minute}`;

            // Safely access the count for each action (dispense, redact, purge)
            dispenseCount += (log["dispense"][timeLabel] || []).length;
            redactCount += (log["redact"][timeLabel] || []).length;
            purgeCount += (log["purge"][timeLabel] || []).length;
        }

        dispenseData.push(dispenseCount);
        redactData.push(redactCount);
        purgeData.push(purgeCount);
        maxY = Math.max(maxY, dispenseCount, redactCount, purgeCount);
    }

    // Update the chart with the new data
    activityChart.data.labels = labels;
    activityChart.data.datasets[0].data = dispenseData;
    activityChart.data.datasets[1].data = redactData;
    activityChart.data.datasets[2].data = purgeData;
    activityChart.options.scales.y.max = maxY + 1;
    activityChart.update();
}

let ctx = document.getElementById('activityChart').getContext('2d');
let activityChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Dispense',
                data: [],
                backgroundColor: 'rgba(0, 255, 0, 0.8)',
                barPercentage: 1.0,
                categoryPercentage: 0.8
            },
            {
                label: 'Redact',
                data: [],
                backgroundColor: 'rgba(255, 165, 0, 0.8)',
                barPercentage: 1.0,
                categoryPercentage: 0.8
            },
            {
                label: 'Purge',
                data: [],
                backgroundColor: 'rgba(255, 0, 0, 0.8)',
                barPercentage: 1.0,
                categoryPercentage: 0.8
            }
        ]
    },
    options: {
        scales: {
            x: { title: { display: true, text: 'Time (06:00 - 21:00)' }},
            y: { beginAtZero: true, ticks: { stepSize: 1 }}
        }
    }
});

fetch('/get_log')
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then(data => updateGraph(data.activity_log)) // Adjusted based on the actual log structure
    .catch(error => console.error("Error fetching log:", error));

document.getElementById("activityChart").addEventListener("contextmenu", function (e) {
    e.preventDefault();
    let time = prompt("Enter the time (HH:MM):");

    // Validate the time format (simple check for HH:MM)
    if (!/^\d{2}:\d{2}$/.test(time)) {
        alert("Invalid time format. Please enter time as HH:MM.");
        return;
    }

    fetch('/get_log')
        .then(response => response.json())
        .then(data => {
            let log = data["dispense"][time] || [];
            if (log.length > 0) {
                alert(`Entries at ${time}:\n${log.map(entry => `${entry.name} (${entry.ip})`).join("\n")}`);
            } else {
                alert("No entries at this time.");
            }
        })
        .catch(error => console.error("Error fetching log data:", error));
});
