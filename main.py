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

# Updated Participants List with Name and Email
participants = [
    {"name": "David", "email": "david@example.com"},
    {"name": "Benjamin Mary", "email": "benjamin.mary@ica.csic.es"},
    {"name": "Andujar Dioni", "email": "d.andujar@csic.es"},
    {"name": "Bennani Zineb", "email": "zineb.bennani@unito.it"},
    {"name": "Borra Irene", "email": "irene.borra@ica.csic.es"},
    {"name": "Burchard Vicente", "email": "vburchard@ica.csic.es"},
    {"name": "Campos David", "email": "dcampos@ica.csic.es"},
    {"name": "de Castro Ana", "email": "ana.decastro@csic.es"},
    {"name": "Fernandez-Quintanilla Cesar", "email": "cfernandezquintanilla@gmail.com"},
    {"name": "Guerra Jose", "email": "jose.g.guerra@ica.csic.es"},
    {"name": "Martin Jose Manuel", "email": "jmanuel.martin@csic.es"},
    {"name": "Mena Juan Diego", "email": "jdmena@ica.csic.es"},
    {"name": "Mesias Gustavo", "email": "gmesias@ica.csic.es"},
    {"name": "Nieto Hector", "email": "hector.nieto@ica.csic.es"},
    {"name": "Olivares Guillermo", "email": "golivares@ica.csic.es"},
    {"name": "Peña Jose Manuel", "email": "jmpena@ica.csic.es"},
    {"name": "Rueda Christian", "email": "christian.rueda@inia.csic.es"},
    {"name": "Miguel Ángel Herrezuelo Bermúdez", "email": "miguel.herrezuelo@ica.csic.es"},
    {"name": "Jose Dorado", "email": "jose.dorado@csic.es"}
]

tasks = [
    "Clean Coffee Machine",
    "Clean Garbage Plastic",
    "Buy New Paper for Printer",
    "Get New Papel de Mano"
]

CSV_FILE = "test_tareas_responsability.csv"

# Read past responsibilities from CSV
# previous_responsibilities = {}

# if os.path.exists(CSV_FILE):
#     with open(CSV_FILE, newline="", encoding="utf-8") as file:
#         reader = csv.reader(file)
#         header = next(reader)  # Skip the header row
#         for row in reader:
#             task = row[1]  # The task is in the second column

#             # Extract the previous responsible (it's in the third column)
#             previous_responsible = row[2]

#             # Extract the assigned participants (name and email)
#             assigned_1_name = row[3]
#             assigned_1_email = row[4]
#             assigned_2_name = row[5]
#             assigned_2_email = row[6]

#             # Extract the supervisors (name and email)
#             supervisor_1_name = row[7]
#             supervisor_1_email = row[8]
#             supervisor_2_name = row[9]
#             supervisor_2_email = row[10]

#             # Store the data in previous_responsibilities (list format)
#             previous_responsibilities[task] = [
#                 previous_responsible,  # Previous Responsible
#                 [assigned_1_name, assigned_1_email],  # Assigned Responsible 1
#                 [assigned_2_name, assigned_2_email],  # Assigned Responsible 2
#                 [supervisor_1_name, supervisor_1_email],  # Supervisor 1
#                 [supervisor_2_name, supervisor_2_email],  # Supervisor 2
#                 row[0]  # Date is in the first column
#             ]

# Function to randomly select two supervisors
def select_assigned():
    available_assigned = [p for p in participants if p["name"]]
    return random.sample(available_assigned, 2)


# Function to randomly select two supervisors, ensuring they are not in the exclude list
def select_supervisors(exclude):
    available_supervisors = [p for p in participants if p["name"] not in [e["name"] for e in exclude]]

    # Ensure there are enough people to select supervisors
    if len(available_supervisors) < 2:
        raise ValueError("Not enough participants to select two supervisors.")

    return random.sample(available_supervisors, 2)


# Get the current 15-day period
start_date = datetime.date(2025, 3, 15)
days_since_start = (datetime.date.today() - start_date).days
current_period = days_since_start // 15

# Get the previous, current, and next task assignments
periods = ['Current', 'Next']
task_assignments = {}

for period in periods:
    # Adjust the period index for the correct task assignments
    period_offset = {'Previous': -1, 'Current': 0, 'Next': 1}[period]
    period_start = start_date + datetime.timedelta(days=(current_period + period_offset) * 15)

    # Assign tasks and supervisors
    task_assignments[period] = {}
    for i, task in enumerate(tasks):
        # Pick two assigned participants (ensure they are not the same)
        assigned_participants = [
            participants[((current_period + period_offset) * len(tasks) + i) % len(participants)],
            participants[((current_period + period_offset) * len(tasks) + i + 1) % len(participants)]
        ]

        # Exclude the assigned participants and the previous period's supervisors (if available)
        previous_supervisors = task_assignments.get("Previous", {}).get(task, {}).get("Supervisors", [])
        exclude_list = assigned_participants + previous_supervisors  # Ensure it's a list of dicts

        # Ensure you select two unique supervisors
        supervisors = select_supervisors(exclude_list)

        task_assignments[period][task] = {
            "Assigned": [{"name": p["name"], "email": p["email"]} for p in assigned_participants],
            "Supervisors": [{"name": supervisor["name"], "email": supervisor["email"]} for supervisor in supervisors],
            "Period Start": period_start.strftime("%B %d, %Y")
        }


# # Save responsibilities in CSV
# with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)

#     # Write header if file is empty
#     if file.tell() == 0:
#         writer.writerow([
#             "Date", "Task", "Previous Responsible",
#             "Assigned Responsible 1 Name", "Assigned Responsible 1 Email",
#             "Assigned Responsible 2 Name", "Assigned Responsible 2 Email",
#             "Supervisor 1 Name", "Supervisor 1 Email",
#             "Supervisor 2 Name", "Supervisor 2 Email"
#         ])

#     today = datetime.date.today()
#     for task, details in task_assignments["Current"].items():
#         # Get the previous responsible person (or N/A if not available)
#         previous_person = previous_responsibilities.get(task, "N/A")

#         # Get the names and emails of the assigned participants
#         assigned_participants = details["Assigned"]
#         assigned_names_emails = [(p["name"], p["email"]) for p in assigned_participants]

#         # Get the names and emails of the supervisors
#         supervisors = details["Supervisors"]
#         supervisor_names_emails = [(s["name"], s["email"]) for s in supervisors]

#         # Write the task details to the CSV
#         writer.writerow([
#             today, task, previous_person,
#             assigned_names_emails[0][0], assigned_names_emails[0][1],
#             assigned_names_emails[1][0], assigned_names_emails[1][1],
#             supervisor_names_emails[0][0], supervisor_names_emails[0][1],
#             supervisor_names_emails[1][0], supervisor_names_emails[1][1]
#         ])


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
