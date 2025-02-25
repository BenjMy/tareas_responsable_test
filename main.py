import csv
import os
import datetime
import random
from flask import Flask, render_template, request, jsonify
from flask_frozen import Freezer

app = Flask(__name__)
app.config['FREEZER_DESTINATION'] = 'docs'
# Initialize Flask-Frozen
freezer = Freezer(app)

# Participants and Tasks
participants = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"},
    {"name": "David", "email": "david@example.com"},
]

tasks = [
    "Clean Coffee Machine",
    "Clean Garbage Plastic",
    "Buy New Paper for Printer",
    "Get New Papel de Mano"
]

CSV_FILE = "test_tareas_responsability.csv"

# Read past responsibilities from CSV
previous_responsibilities = {}

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            previous_responsibilities[row["Task"]] = row["Current Responsible"]

# Function to randomly select two supervisors
def select_supervisors():
    return random.sample(participants, 2)

# Get the current 15-day period
start_date = datetime.date(2024, 1, 1)
days_since_start = (datetime.date.today() - start_date).days
current_period = days_since_start // 15

# Get the previous, current, and next task assignments
periods = ['Previous', 'Current', 'Next']
task_assignments = {}

for period in periods:
    # Adjust the period index for the correct task assignments
    period_offset = {'Previous': -1, 'Current': 0, 'Next': 1}[period]
    period_start = start_date + datetime.timedelta(days=(current_period + period_offset) * 15)

    # Assign tasks and supervisors
    task_assignments[period] = {}
    for i, task in enumerate(tasks):
        assigned_participant = participants[((current_period + period_offset) * len(tasks) + i) % len(participants)]
        supervisors = select_supervisors()
        task_assignments[period][task] = {
            "Assigned": assigned_participant,
            "Supervisors": [{"name": supervisor["name"], "email": supervisor["email"]} for supervisor in supervisors],
            "Period Start": period_start.strftime("%B %d, %Y")
        }

# Save responsibilities in CSV
with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # Write header if file is empty
    if file.tell() == 0:
        writer.writerow(["Date", "Task", "Previous Responsible", "Current Responsible"])

    today = datetime.date.today()
    for task, details in task_assignments["Current"].items():
        previous_person = previous_responsibilities.get(task, "N/A")
        writer.writerow([today, task, previous_person, details["Assigned"]["name"]])

@app.route("/")
def index():
    current_date = datetime.date.today().strftime("%B %d, %Y")  # Format the current date
    return render_template("index.html", task_assignments=task_assignments, current_date=current_date)

@app.route("/alert", methods=["POST"])
def alert():
    task = request.json["task"]
    person = task_assignments["Current"][task]["Assigned"]
    return jsonify({"message": f"Alert sent to {person['name']} ({person['email']}) about '{task}'!"})

@app.route("/about.html")
def about():
    return render_template("about.html")



if __name__ == "__main__":
    freezer.freeze()  # This will freeze the app into static files
